
/* Chrysalide - Outil d'analyse de fichiers binaires
 * storage.c - conservation hors mémoire d'objets choisis
 *
 * Copyright (C) 2020 Cyrille Bagard
 *
 *  This file is part of Chrysalide.
 *
 *  Chrysalide is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  Chrysalide is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#include "storage.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>
#include <unistd.h>
#include <stdarg.h>


#include "storage-int.h"
#include "../db/misc/rlestr.h"
#include "../../common/io.h"
#include "../../common/leb128.h"
#include "../../core/logs.h"



#define STORAGE_MAGIC "CSTR"
#define STORAGE_NUMBER "\x00\x01"


/* Initialise la classe des conservations d'objets en place. */
static void g_object_storage_class_init(GObjectStorageClass *);

/* Initialise une instance de conservation d'objets en place. */
static void g_object_storage_init(GObjectStorage *);

/* Supprime toutes les références externes. */
static void g_object_storage_dispose(GObjectStorage *);

/* Procède à la libération totale de la mémoire. */
static void g_object_storage_finalize(GObjectStorage *);

/* Retrouve l'encadrement pour un nouveau groupe d'objets. */
static storage_backend_t *g_object_storage_find_backend(GObjectStorage *, const char *);

/* Ajoute le support d'un nouveau groupe d'objets construits. */
static bool g_object_storage_add_backend(GObjectStorage *, const char *, storage_backend_t **);

/* Extrait d'un tampon des enregistrements spécifiques. */
static bool g_object_storage_load_backend(GObjectStorage *, packed_buffer_t *);

/* Place dans un tampon les données liées à des enregistrements. */
static bool pack_storage_backend(const storage_backend_t *, packed_buffer_t *);



/* Indique le type défini pour une conservation d'objets construits. */
G_DEFINE_TYPE(GObjectStorage, g_object_storage, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des conservations d'objets en place.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_object_storage_class_init(GObjectStorageClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_object_storage_dispose;
    object->finalize = (GObjectFinalizeFunc)g_object_storage_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : storage = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance de conservation d'objets en place.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_object_storage_init(GObjectStorage *storage)
{
    storage->tpmem = g_type_memory_new();

    storage->hash = NULL;

    storage->backends = NULL;
    storage->count = 0;
    g_mutex_init(&storage->mutex);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : storage = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_object_storage_dispose(GObjectStorage *storage)
{
    g_clear_object(&storage->tpmem);

    G_OBJECT_CLASS(g_object_storage_parent_class)->dispose(G_OBJECT(storage));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : storage = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_object_storage_finalize(GObjectStorage *storage)
{
    size_t i;                               /* Boucle de parcours          */
    storage_backend_t *backend;             /* Gestionnaire à manipuler    */
    int ret;                                /* Bilan d'un appel            */

    g_mutex_lock(&storage->mutex);

    for (i = 0; i < storage->count; i++)
    {
        backend = &storage->backends[i];

        if (backend->fd != -1)
            close(backend->fd);
        else
            assert(false);

        ret = access(backend->filename, W_OK);
        if (ret == 0)
        {
            ret = unlink(backend->filename);
            if (ret != 0) LOG_ERROR_N("unlink");
        }

        free(backend->name);

        free(backend->filename);

    }

    if (storage->backends != NULL)
        free(storage->backends);

    g_mutex_unlock(&storage->mutex);

    g_mutex_clear(&storage->mutex);

    if (storage->hash != NULL)
        free(storage->hash);

    G_OBJECT_CLASS(g_object_storage_parent_class)->finalize(G_OBJECT(storage));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : loaded = contenu binaire à associer.                         *
*                                                                             *
*  Description : Crée le support d'une conservation d'objets en place.        *
*                                                                             *
*  Retour      : Mécanismes mis en place.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GObjectStorage *g_object_storage_new(const char *hash)
{
    GObjectStorage *result;                 /* Structure à retourner       */

    result = g_object_new(G_TYPE_OBJECT_STORAGE, NULL);

    result->hash = strdup(hash);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pbuf = zone tampon à lire.                                   *
*                                                                             *
*  Description : Charge le support d'une conservation d'objets en place.      *
*                                                                             *
*  Retour      : Gestionnaire de conservations construit ou NULL si erreur.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GObjectStorage *g_object_storage_load(packed_buffer_t *pbuf)
{
    GObjectStorage *result;                 /* Structure à retourner       */
    char header[6];                         /* Entête attendue des données */
    bool status;                            /* Bilan d'une extraction      */
    rle_string str;                         /* Chaîne à conserver          */
    uleb128_t count;                        /* Nombre de groupes à charger */
    uleb128_t i;                            /* Boucle de parcours          */

    result = NULL;

    status = extract_packed_buffer(pbuf, header, 6, false);
    if (!status) goto quick_exit;

    if (strncmp(header, STORAGE_MAGIC STORAGE_NUMBER, 6) != 0)
        goto quick_exit;

    setup_empty_rle_string(&str);

    status = unpack_rle_string(&str, pbuf);
    if (!status) goto quick_exit;

    if (get_rle_string(&str) == NULL)
    {
        exit_rle_string(&str);
        goto quick_exit;
    }

    result = g_object_new(G_TYPE_OBJECT_STORAGE, NULL);

    result->hash = strdup(get_rle_string(&str));

    exit_rle_string(&str);

    status = g_type_memory_load_types(result->tpmem, pbuf);
    if (!status) goto exit_while_loading;

    status = unpack_uleb128(&count, pbuf);

    for (i = 0; i < count && status; i++)
        status = g_object_storage_load_backend(result, pbuf);

 exit_while_loading:

    if (!status)
    {
        g_object_unref(G_OBJECT(result));
        result = NULL;
    }

 quick_exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : storage = gestionnaire de conservations à manipuler.         *
*                pbuf    = zone tampon à remplir. [OUT]                       *
*                                                                             *
*  Description : Sauvegarde le support d'une conservation d'objets en place.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_object_storage_store(GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    rle_string str;                         /* Chaîne à conserver          */
    size_t i;                               /* Boucle de parcours          */

    result = extend_packed_buffer(pbuf, STORAGE_MAGIC STORAGE_NUMBER, 6, false);

    if (result)
    {
        init_static_rle_string(&str, storage->hash);

        result = pack_rle_string(&str, pbuf);

        exit_rle_string(&str);

    }

    g_mutex_lock(&storage->mutex);

    if (result)
        result = g_type_memory_store_types(storage->tpmem, pbuf);

    if (result)
        result = pack_uleb128((uleb128_t []){ storage->count }, pbuf);

    for (i = 0; i < storage->count && result; i++)
        result = pack_storage_backend(&storage->backends[i], pbuf);

    g_mutex_unlock(&storage->mutex);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : storage = gestionnaire de conservations à compléter.         *
*                name    = désignation d'un nouveau groupe d'objets.          *
*                                                                             *
*  Description : Retrouve l'encadrement pour un nouveau groupe d'objets.      *
*                                                                             *
*  Retour      : Informations liées à un groupe ou NULL en cas d'échec.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static storage_backend_t *g_object_storage_find_backend(GObjectStorage *storage, const char *name)
{
    storage_backend_t *result;              /* Encadrement à retourner     */
    size_t i;                               /* Boucle de parcours          */

    assert(!g_mutex_trylock(&storage->mutex));

    for (i = 0; i < storage->count; i++)
        if (strcmp(storage->backends[i].name, name) == 0)
            break;

    if (i == storage->count)
        result = NULL;
    else
        result = &storage->backends[i];

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : storage = gestionnaire de conservations à compléter.         *
*                name    = désignation d'un nouveau groupe d'objets.          *
*                backend = support mis en place pour les enregistrements.     *
*                                                                             *
*  Description : Ajoute le support d'un nouveau groupe d'objets construits.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_object_storage_add_backend(GObjectStorage *storage, const char *name, storage_backend_t **backend)
{
    bool result;                            /* Bilan à retourner           */
    char *prefix;                           /* Début de nom de fichier     */
    char *filename;                         /* Chemin d'accès aux données  */
    int fd;                                 /* Descripteur de flux ouvert  */

    result = false;

    *backend = NULL;

    assert(!g_mutex_trylock(&storage->mutex));

    if (g_object_storage_find_backend(storage, name) != NULL)
        goto exit;

    /* Préparatifs */

    asprintf(&prefix, "%s-%s", storage->hash, name);

    fd = make_tmp_file(prefix, "cache", &filename);

    free(prefix);

    if (fd == -1)
        goto exit;

    /* Inscription en bonne et due forme */

    storage->backends = realloc(storage->backends, ++storage->count * sizeof(storage_backend_t));

    *backend = &storage->backends[storage->count - 1];

    (*backend)->name = strdup(name);

    (*backend)->filename = filename;
    (*backend)->fd = fd;

    result = true;

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : storage = gestionnaire de conservations à compléter.         *
*                pbuf    = zone tampon à lire.                                *
*                                                                             *
*  Description : Extrait d'un tampon des enregistrements spécifiques.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_object_storage_load_backend(GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    rle_string str;                         /* Chaîne à conserver          */
    bool status;                            /* Bilan de lecture de contenu */
    storage_backend_t *backend;             /* Informations à intégrer     */
    uleb128_t length;                       /* Taille des données à charger*/
    off_t moved;                            /* Nouvelle position établie   */

    result = false;

    g_mutex_lock(&storage->mutex);

    /* Récupération du nom et création du support */

    setup_empty_rle_string(&str);

    status = unpack_rle_string(&str, pbuf);
    if (!status) goto exit;

    if (get_rle_string(&str) == NULL)
    {
        exit_rle_string(&str);
        goto exit;
    }

    status = g_object_storage_add_backend(storage, get_rle_string(&str), &backend);

    exit_rle_string(&str);

    if (!status) goto exit;

    /* Récupération du contenu */

    status = unpack_uleb128(&length, pbuf);
    if (!status) goto exit;

    status = safe_write(backend->fd, pbuf->data + pbuf->pos, length);
    if (!status) goto exit;

    advance_packed_buffer(pbuf, length);

    moved = lseek(backend->fd, 0, SEEK_SET);
    if (moved == ((off_t)-1))
    {
        LOG_ERROR_N("lseek");
        goto exit;
    }

    result = true;

 exit:

    g_mutex_unlock(&storage->mutex);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = stockage des enregistrements spécifiques.          *
*                pbuf    = zone tampon à remplir. [OUT]                       *
*                                                                             *
*  Description : Place dans un tampon les données liées à des enregistrements.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool pack_storage_backend(const storage_backend_t *backend, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    rle_string str;                         /* Chaîne à conserver          */
    bool status;                            /* Bilan de lecture de contenu */
    off_t current;                          /* Position courante           */
    off_t moved;                            /* Nouvelle position établie   */
    void *data;                             /* Données à transférer        */

    result = false;

    /* Inscription du nom */

    init_static_rle_string(&str, backend->name);

    status = pack_rle_string(&str, pbuf);

    exit_rle_string(&str);

    if (!status) goto exit;

    /* Inscription du contenu */

    current = lseek(backend->fd, 0, SEEK_CUR);
    if (current == ((off_t)-1))
    {
        LOG_ERROR_N("lseek");
        goto exit;
    }

    moved = lseek(backend->fd, 0, SEEK_SET);
    if (moved == ((off_t)-1))
    {
        LOG_ERROR_N("lseek");
        goto exit;
    }

    data = malloc(current);
    if (data == NULL)
    {
        LOG_ERROR_N("malloc");
        goto restore;
    }

    status = safe_read(backend->fd, data, current);
    if (!status) goto free_mem;

    status = pack_uleb128((uleb128_t []){ current }, pbuf);
    if (!status) goto free_mem;

    status = extend_packed_buffer(pbuf, data, current, false);

 free_mem:

    free(data);

 restore:

    moved = lseek(backend->fd, current, SEEK_SET);
    if (moved == ((off_t)-1))
    {
        LOG_ERROR_N("lseek");
        goto exit;
    }

    result = status;

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : storage = gestionnaire à manipuler.                          *
*                name    = désignation d'un nouveau groupe d'objets.          *
*                pos     = tête de lecture avant écriture.                    *
*                                                                             *
*  Description : Charge un objet à partir de données rassemblées.             *
*                                                                             *
*  Retour      : Objet restauré en mémoire ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GSerializableObject *g_object_storage_load_object(GObjectStorage *storage, const char *name, off64_t pos)
{
    GSerializableObject *result;            /* Instance à retourner        */
    bool status;                            /* Bilan d'une opération       */
    storage_backend_t *backend;             /* Informations à consulter    */
    packed_buffer_t pbuf;                   /* Tampon des données à lire   */
    off64_t new;                            /* Nouvelle position de lecture*/

    result = NULL;

    /* Chargement */

    status = false;

    g_mutex_lock(&storage->mutex);

    backend = g_object_storage_find_backend(storage, name);

    if (backend != NULL)
    {
        new = lseek64(backend->fd, pos, SEEK_SET);

        if (new == pos)
        {
            init_packed_buffer(&pbuf);
            status = read_packed_buffer(&pbuf, backend->fd);
        }

    }

    g_mutex_unlock(&storage->mutex);

    if (!status)
        goto exit;

    /* Phase de conversion */

    result = G_SERIALIZABLE_OBJECT(g_type_memory_create_object(storage->tpmem, &pbuf));

    if (result)
    {
        status = g_serializable_object_load(result, storage, &pbuf);

        if (!status)
            g_clear_object(&result);

    }

    exit_packed_buffer(&pbuf);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : storage = gestionnaire à manipuler.                          *
*                name    = désignation d'un nouveau groupe d'objets.          *
*                pbuf    = zone tampon à parcourir.                           *
*                                                                             *
*  Description : Charge un objet interne à partir de données rassemblées.     *
*                                                                             *
*  Retour      : Objet restauré en mémoire ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GSerializableObject *g_object_storage_unpack_object(GObjectStorage *storage, const char *name, packed_buffer_t *pbuf)
{
    GSerializableObject *result;            /* Instance à retourner        */
    uint64_t pos;                           /* Localisation des données    */
    bool status;                            /* Bilan d'une opération       */

    result = NULL;

    status = extract_packed_buffer(pbuf, &pos, sizeof(uint64_t), true);

    if (status)
        result = g_object_storage_load_object(storage, name, pos);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : storage  = gestionnaire à manipuler.                         *
*                name     = désignation d'un nouveau groupe d'objets.         *
*                pbuf     = zone tampon à parcourir.                          *
*                expected = type d'objet attendu.                             *
*                ...      = élément restauré ou NULL en cas d'échec. [OUT]    *
*                                                                             *
*  Description : Charge un objet interne à partir de données rassemblées.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_object_storage_unpack_object_2(GObjectStorage *storage, const char *name, packed_buffer_t *pbuf, GType expected, ...)
{
    bool result;                            /* Bilan d'une opération       */
    uint64_t pos;                           /* Localisation des données    */
    GSerializableObject *instance;          /* Objet rechargé à valider    */
    va_list ap;                             /* Liste d'arguments variables */
    void **object;                          /* Lieu d'enregistrement final */

    result = extract_packed_buffer(pbuf, &pos, sizeof(uint64_t), true);

    if (result)
    {
        if (pos == 0)
            *object = NULL;

        else
        {
            instance = g_object_storage_load_object(storage, name, pos);

            result = G_TYPE_CHECK_INSTANCE_TYPE(instance, expected);

            if (result)
            {
                va_start(ap, expected);

                object = va_arg(ap, void **);

                *object = instance;

                va_end(ap);

            }

            else
                g_clear_object(&instance);

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : storage = gestionnaire à manipuler.                          *
*                name    = désignation d'un nouveau groupe d'objets.          *
*                object  = objet sérialisable à traiter.                      *
*                pos     = tête de lecture avant écriture. [OUT]              *
*                                                                             *
*  Description : Sauvegarde un object sous forme de données rassemblées.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_object_storage_store_object(GObjectStorage *storage, const char *name, const GSerializableObject *object, off64_t *pos)
{
    bool result;                            /* Bilan à retourner           */
    packed_buffer_t pbuf;                   /* Tampon des données à écrire */
    storage_backend_t *backend;             /* Informations à consulter    */
    off64_t tmp;                            /* Conservation éphémère       */

    /* Phase de conversion */

    init_packed_buffer(&pbuf);

    result = g_type_memory_store_object_gtype(storage->tpmem, G_OBJECT(object), &pbuf);
    if (!result) goto exit;

    result = g_serializable_object_store(object, storage, &pbuf);
    if (!result) goto exit;

    /* Enregistrement */

    result = false;

    g_mutex_lock(&storage->mutex);

    backend = g_object_storage_find_backend(storage, name);

    if (backend == NULL)
        g_object_storage_add_backend(storage, name, &backend);

    if (backend != NULL)
    {
        if (pos == NULL)
            pos = &tmp;

        *pos = lseek64(backend->fd, 0, SEEK_CUR);

        if (*pos != (off64_t)-1)
            result = write_packed_buffer(&pbuf, backend->fd);

    }

    g_mutex_unlock(&storage->mutex);

    /* Sortie propre */

 exit:

    exit_packed_buffer(&pbuf);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : storage = gestionnaire à manipuler.                          *
*                name    = désignation d'un nouveau groupe d'objets.          *
*                pbuf    = zone tampon à remplir.                             *
*                                                                             *
*  Description : Sauvegarde un object interne sous forme de données.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_object_storage_pack_object(GObjectStorage *storage, const char *name, const GSerializableObject *object, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    off64_t pos;                            /* Localisation des données    */

    if (object == NULL)
        result = extend_packed_buffer(pbuf, (uint64_t []){ 0 }, sizeof(uint64_t), true);

    else
    {
        result = g_object_storage_store_object(storage, name, object, &pos);

        if (result)
            result = extend_packed_buffer(pbuf, (uint64_t []){ pos }, sizeof(uint64_t), true);

    }

    return result;

}
