
/* Chrysalide - Outil d'analyse de fichiers binaires
 * file.c - chargement de données binaires à partir d'un fichier
 *
 * Copyright (C) 2015-2019 Cyrille Bagard
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
 *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.
 */


#include "file.h"


#include <fcntl.h>
#include <malloc.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/stat.h>


#include "memory-int.h"
#include "../content-int.h"
#include "../db/misc/rlestr.h"
#include "../storage/serialize-int.h"
#include "../../core/logs.h"



/* -------------------------- ENSEMBLE DE DONNEES BINAIRES -------------------------- */


/* Contenu de données binaires issues d'un fichier (instance) */
struct _GFileContent
{
    GMemoryContent parent;                  /* A laisser en premier        */

    char *filename;                         /* Fichier chargé en mémoire   */
    int fd;                                 /* Flux ouvert en lectureu     */

};

/* Contenu de données binaires issues d'un fichier (classe) */
struct _GFileContentClass
{
    GMemoryContentClass parent;             /* A laisser en premier        */

};


/* Initialise la classe des contenus de données binaires. */
static void g_file_content_class_init(GFileContentClass *);

/* Initialise une instance de contenu de données binaires. */
static void g_file_content_init(GFileContent *);

/* Procède à l'initialisation de l'interface de sérialisation. */
static void g_file_content_serializable_init(GSerializableObjectInterface *);

/* Supprime toutes les références externes. */
static void g_file_content_dispose(GFileContent *);

/* Procède à la libération totale de la mémoire. */
static void g_file_content_finalize(GFileContent *);


/* -------------------- CONSERVATION ET RECHARGEMENT DES DONNEES -------------------- */


/* Charge un contenu depuis une mémoire tampon. */
static bool g_file_content_load(GFileContent *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
static bool g_file_content_store(const GFileContent *, GObjectStorage *, packed_buffer_t *);



/* ---------------------------------------------------------------------------------- */
/*                            ENSEMBLE DE DONNEES BINAIRES                            */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini par la GLib pour les contenus de données. */
G_DEFINE_TYPE_WITH_CODE(GFileContent, g_file_content, G_TYPE_MEMORY_CONTENT,
                        G_IMPLEMENT_INTERFACE(G_TYPE_SERIALIZABLE_OBJECT, g_file_content_serializable_init));


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des contenus de données binaires.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_file_content_class_init(GFileContentClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_file_content_dispose;
    object->finalize = (GObjectFinalizeFunc)g_file_content_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance de contenu de données binaires.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_file_content_init(GFileContent *content)
{
    content->filename = NULL;
    content->fd = -1;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de sérialisation.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_file_content_serializable_init(GSerializableObjectInterface *iface)
{
    iface->load = (load_serializable_object_cb)g_file_content_load;
    iface->store = (store_serializable_object_cb)g_file_content_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_file_content_dispose(GFileContent *content)
{
    G_OBJECT_CLASS(g_file_content_parent_class)->dispose(G_OBJECT(content));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_file_content_finalize(GFileContent *content)
{
    GMemoryContent *base;                   /* Structure parente           */

    free(content->filename);

    if (content->fd != -1)
    {
        base = G_MEMORY_CONTENT(content);
        munmap(base->data, base->length);

        close(content->fd);

    }

    G_OBJECT_CLASS(g_file_content_parent_class)->finalize(G_OBJECT(content));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : filename = chemin d'accès au fichier à charger.              *
*                                                                             *
*  Description : Charge en mémoire le contenu d'un fichier donné.             *
*                                                                             *
*  Retour      : Représentation de contenu à manipuler ou NULL en cas d'échec.*
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinContent *g_file_content_new(const char *filename)
{
    GFileContent *result;                   /* Structure à retourner       */
    int fd;                                 /* Descripteur du fichier      */
    struct stat info;                       /* Informations sur le fichier */
    int ret;                                /* Bilan d'un appel            */
    void *content;                          /* Contenu brut du fichier     */
    GMemoryContent *base;                   /* Structure parente           */

    /* Récupération des données */

    fd = open(filename, O_RDONLY);
    if (fd == -1)
    {
        LOG_ERROR_N("open");
        goto file_error;
    }

    ret = fstat(fd, &info);
    if (ret == -1)
    {
        close(fd);
        LOG_ERROR_N("fstat");
        goto file_error;
    }

    content = mmap(NULL, info.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
    if (content == MAP_FAILED)
    {
        close(fd);
        LOG_ERROR_N("mmap");
        goto file_error;
    }

    /* Constitution du contenu officiel */

    result = g_object_new(G_TYPE_FILE_CONTENT, NULL);

    result->filename = strdup(filename);

    base = G_MEMORY_CONTENT(result);

    base->data = content;
    base->length = info.st_size;

    return G_BIN_CONTENT(result);

 file_error:

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à venir consulter.                 *
*                                                                             *
*  Description : Fournit le nom de fichier associé au contenu binaire.        *
*                                                                             *
*  Retour      : Chemin d'accès au contenu binaire.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_file_content_get_filename(const GFileContent *content)
{
    char *result;                           /* Chemin d'accès à retourner  */

    result = content->filename;

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                      CONSERVATION ET RECHARGEMENT DES DONNEES                      */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : content = élément GLib à constuire.                          *
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à lire.                                *
*                                                                             *
*  Description : Charge un contenu depuis une mémoire tampon.                 *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_file_content_load(GFileContent *content, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GSerializableObjectIface *parent_iface; /* Interface du niveau parent  */
    rle_string str;                         /* Chaîne à charger            */

    parent_iface = g_type_interface_peek(g_file_content_parent_class, G_TYPE_SERIALIZABLE_OBJECT);

    result = parent_iface->load(G_SERIALIZABLE_OBJECT(content), storage, pbuf);

    setup_empty_rle_string(&str);

    if (result)
        result = unpack_rle_string(&str, pbuf);

    if (result)
    {
        result = (get_rle_string(&str) != NULL);

        if (result)
            content->filename = strdup(get_rle_string(&str));

        exit_rle_string(&str);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = élément GLib à consulter.                          *
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à remplir.                             *
*                                                                             *
*  Description : Sauvegarde un contenu dans une mémoire tampon.               *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_file_content_store(const GFileContent *content, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GSerializableObjectIface *parent_iface; /* Interface du niveau parent  */
    rle_string str;                         /* Chaîne à conserver          */

    parent_iface = g_type_interface_peek(g_file_content_parent_class, G_TYPE_SERIALIZABLE_OBJECT);

    result = parent_iface->store(G_SERIALIZABLE_OBJECT(content), storage, pbuf);

    if (result)
    {
        init_static_rle_string(&str, content->filename);

        result = pack_rle_string(&str, pbuf);

        exit_rle_string(&str);

    }

    return result;

}
