
/* Chrysalide - Outil d'analyse de fichiers binaires
 * collection.c - gestion d'éléments ajoutés par collection
 *
 * Copyright (C) 2014-2019 Cyrille Bagard
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


#include "collection.h"


#include <assert.h>
#include <malloc.h>
#include <stdio.h>
#include <string.h>


#include <i18n.h>


#include "collection-int.h"
#include "misc/rlestr.h"
#include "../../common/extstr.h"
#include "../../common/sort.h"
#include "../../glibext/chrysamarshal.h"







/* Initialise la classe des collections génériques d'éléments. */
static void g_db_collection_class_init(GDbCollectionClass *);

/* Initialise une collection générique d'éléments. */
static void g_db_collection_init(GDbCollection *);

/* Supprime toutes les références externes. */
static void g_db_collection_dispose(GDbCollection *);

/* Procède à la libération totale de la mémoire. */
static void g_db_collection_finalize(GDbCollection *);

/* Ajoute un élément dans la liste des éléments actifs. */
static void g_db_collection_set_last_item(GDbCollection *, GDbItem *, bool);

/* Retrouve l'élément correspondant à un horodatage. */
static size_t g_db_collection_find_by_timestamped(GDbCollection *, const GDbItem *);

/* Retire un élément de la liste des éléments courants. */
static void g_db_collection_unset_last_item(GDbCollection *, GDbItem *, size_t);

/* Retrouve le premier élément correspondant à un horodatage. */
static size_t g_db_collection_find_by_timestamp(GDbCollection *, timestamp_t);



/* --------------------- MANIPULATIONS AVEC UNE BASE DE DONNEES --------------------- */


/* Charge et intère un élément dans une collection. */
static bool g_db_collection_load_new_item(const bound_value *, size_t, GDbCollection *);

/* Enregistre un élément de collection dans une base de données. */
static bool g_db_collection_store_item(const GDbCollection *, const GDbItem *, sqlite3 *);

/* Met à jour un élément de collection dans une base de données. */
static bool g_db_collection_store_updated_item(const GDbCollection *, const GDbItem *, sqlite3 *);




/* Indique le type défini pour une collection générique d'éléments. */
G_DEFINE_TYPE(GDbCollection, g_db_collection, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des collections génériques d'éléments.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_collection_class_init(GDbCollectionClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_db_collection_dispose;
    object->finalize = (GObjectFinalizeFunc)g_db_collection_finalize;

    g_signal_new("content-extended",
                 G_TYPE_DB_COLLECTION,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GDbCollectionClass, content_extended),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__OBJECT,
                 G_TYPE_NONE, 1, G_TYPE_OBJECT);

    g_signal_new("state-changed",
                 G_TYPE_DB_COLLECTION,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GDbCollectionClass, state_changed),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__OBJECT,
                 G_TYPE_NONE, 1, G_TYPE_OBJECT);

    g_signal_new("active-changed",
                 G_TYPE_DB_COLLECTION,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GDbCollectionClass, active_changed),
                 NULL, NULL,
                 g_cclosure_user_marshal_VOID__ENUM_OBJECT,
                 G_TYPE_NONE, 2, G_TYPE_UINT, G_TYPE_OBJECT);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une collection générique d'éléments.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_collection_init(GDbCollection *collec)
{
    collec->binary = NULL;

    collec->items = NULL;
    collec->count = 0;

    collec->last_items = g_hash_table_new_full((GHashFunc)g_db_item_hash_key,
                                               (GEqualFunc)g_db_item_cmp_key,
                                               (GDestroyNotify)g_object_unref,
                                               (GDestroyNotify)g_object_unref);

    g_rw_lock_init(&collec->params_access);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_collection_dispose(GDbCollection *collec)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < collec->count; i++)
        g_clear_object(&collec->items[i]);

    G_OBJECT_CLASS(g_db_collection_parent_class)->dispose(G_OBJECT(collec));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_collection_finalize(GDbCollection *collec)
{
    if (collec->items != NULL)
        free(collec->items);

    g_rw_lock_clear(&collec->params_access);

    G_OBJECT_CLASS(g_db_collection_parent_class)->finalize(G_OBJECT(collec));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : id   = identifiant réseau des éléments à traiter.            *
*                type = type GLib des éléments à placer dans la collection.   *
*                name = indique le nom désignant la table associée.           *
*                                                                             *
*  Description : Prépare la mise en place d'une nouvelle collection.          *
*                                                                             *
*  Retour      : Adresse de l'instance ou NULL en cas d'échec.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDbCollection *g_db_collection_new(uint32_t id, GType type, const char *name)
{
    GDbCollection *result;                  /* Adresse à retourner         */

    result = g_object_new(G_TYPE_DB_COLLECTION, NULL);

    result->featuring = id;
    result->type = type;
    result->name = name;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = collection générique d'éléments à compléter.        *
*                binary = binaire sur lequel appliquer les éléments.          *
*                                                                             *
*  Description : Attache à une collection un binaire pour les éléments listés.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_db_collection_link_to_binary(GDbCollection *collec, GLoadedBinary *binary)
{
    collec->binary = binary;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = collection générique d'éléments à consulter.        *
*                                                                             *
*  Description : Décrit le type des éléments rassemblées dans une collection. *
*                                                                             *
*  Retour      : Identifiant interne des éléments collectionés.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

uint32_t g_db_collection_get_feature(const GDbCollection *collec)
{
    return collec->featuring;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = collection générique d'éléments à consulter.        *
*                                                                             *
*  Description : Décrit le type de collection manipulée.                      *
*                                                                             *
*  Retour      : Description humaine de la collection.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_db_collection_get_name(const GDbCollection *collec)
{
    return _(collec->name);

}









/******************************************************************************
*                                                                             *
*  Paramètres  : collec = ensemble d'éléments à considérer.                   *
*                pbuf   = paquet de données où venir puiser les infos.        *
*                action = commande de la requête. [OUT]                       *
*                dest   = élément de collection ou NULL pour un rejet. [OUT]  *
*                                                                             *
*  Description : Réceptionne un élément depuis une requête réseau.            *
*                                                                             *
*  Retour      : Bilan de l'exécution de l'opération.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool _g_db_collection_unpack(GDbCollection *collec, packed_buffer_t *pbuf, DBAction *action, GDbItem **dest)
{
    bool result;                            /* Bilan à faire remonter      */
    uint32_t tmp32;                         /* Valeur sur 32 bits          */
    GDbItem *item;                          /* Définition d'élément visé   */

    result = extract_packed_buffer(pbuf, &tmp32, sizeof(uint32_t), true);
    if (!result) goto qck_exit;

    *action = tmp32;

    result = (*action >= 0 && *action < DBA_COUNT);
    if (!result) goto qck_exit;

    item = g_object_new(collec->type, NULL);

    result = g_db_item_unpack(item, pbuf);
    if (!result) goto exit;

    if (dest != NULL)
    {
        g_object_ref(G_OBJECT(item));
        *dest = item;
    }

 exit:

    g_object_unref(G_OBJECT(item));

 qck_exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = ensemble d'éléments à considérer.                   *
*                pbuf   = paquet de données où venir puiser les infos.        *
*                db     = base de données à mettre à jour.                    *
*                                                                             *
*  Description : Réceptionne et traite une requête réseau pour collection.    *
*                                                                             *
*  Retour      : Bilan de l'exécution de l'opération.                         *
*                                                                             *
*  Remarques   : Cette fonction est uniquement destinée aux appels depuis     *
*                la fonction g_cdb_archive_process() ; une partie des         *
*                informations ont déjà été tirées des échanges protocolaires. *
*                                                                             *
******************************************************************************/

bool g_db_collection_unpack(GDbCollection *collec, packed_buffer_t *pbuf, sqlite3 *db)
{
    bool result;                            /* Bilan à faire remonter      */
    DBAction action;                        /* Commande de la requête      */
    GDbItem *item;                          /* Définition d'élément visé   */

    result = _g_db_collection_unpack(collec, pbuf, &action, &item);
    if (!result) return false;

    switch (action)
    {
        case DBA_ADD_ITEM:

            /* Ecrasement des horodatages par les valeurs communes du serveur */
            if (db != NULL)
                g_db_item_set_server_side(item);

            result = g_db_collection_add_item(collec, item);

            if (result)
            {
                if (collec->binary != NULL && !g_db_item_has_flag(item, DIF_DISABLED))
                    g_db_item_apply(item, collec->binary);

                if (db != NULL)
                    g_db_collection_store_item(collec, item, db);

            }

            break;

        case DBA_CHANGE_STATE:

            if (collec->binary != NULL)
            {
                result = g_db_collection_update_item_state(collec, item);

                if (result)
                {
                    if (g_db_item_has_flag(item, DIF_DISABLED))
                        g_db_item_cancel(item, collec->binary);
                    else
                        g_db_item_apply(item, collec->binary);
                }

            }

            else
            {
                assert(db != NULL);
                result = false;
            }

            g_object_unref(G_OBJECT(item));

            break;

        default:
            g_object_unref(G_OBJECT(item));
            result = false;
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = ensemble d'éléments à considérer.                   *
*                pbuf   = paquet de données où venir inscrire les infos.      *
*                action = avenir de l'élément fourni.                         *
*                item   = élément de collection à sérialiser.                 *
*                                                                             *
*  Description : Envoie pour traitement une requête réseau pour collection.   *
*                                                                             *
*  Retour      : Bilan de l'exécution de l'opération.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_db_collection_pack(GDbCollection *collec, packed_buffer_t *pbuf, DBAction action, const GDbItem *item)
{
    bool result;                            /* Bilan à retourner           */

    result = extend_packed_buffer(pbuf, (uint32_t []) { DBC_COLLECTION }, sizeof(uint32_t), true);

    if (result)
        result = extend_packed_buffer(pbuf, (uint32_t []) { collec->featuring }, sizeof(uint32_t), true);

    if (result)
        result = extend_packed_buffer(pbuf, (uint32_t []) { action }, sizeof(uint32_t), true);

    if (result)
        result = g_db_item_pack(item, pbuf);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = ensemble d'éléments à considérer.                   *
*                pbuf   = paquet de données où venir inscrire les infos.      *
*                                                                             *
*  Description : Envoie pour mise à jour tous les éléments courants.          *
*                                                                             *
*  Retour      : Bilan de l'exécution de l'opération.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_db_collection_pack_all_updates(GDbCollection *collec, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à renvoyer            */
    size_t i;                               /* Boucle de parcours          */

    result = true;

    /**
     * La gestion des accès s'effectue depuis le seul appelant : la fonction
     * g_cdb_archive_add_client().
    */

    for (i = 0; i < collec->count && result; i++)
        result = g_db_collection_pack(collec, pbuf, DBA_ADD_ITEM, G_DB_ITEM(collec->items[i]));

    return result;

}







/******************************************************************************
*                                                                             *
*  Paramètres  : collec = collection à mettre à jour.                         *
*                write  = précise le type d'accès prévu (lecture/écriture).   *
*                lock   = indique le sens du verrouillage à mener.            *
*                                                                             *
*  Description : Met à disposition un encadrement des accès aux éléments.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_db_collection_lock_unlock(GDbCollection *collec, bool write, bool lock)
{
    if (write)
    {
        if (lock) g_rw_lock_writer_lock(&collec->params_access);
        else g_rw_lock_writer_unlock(&collec->params_access);
    }
    else
    {
        if (lock) g_rw_lock_reader_lock(&collec->params_access);
        else g_rw_lock_reader_unlock(&collec->params_access);
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = ensemble d'éléments à consulter.                    *
*                count  = taille de la liste constituée. [OUT]                *
*                                                                             *
*  Description : Renvoie la liste des éléments rassemblés.                    *
*                                                                             *
*  Retour      : Liste d'éléments à parcourir.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDbItem **g_db_collection_get_items(const GDbCollection *collec, size_t *count)
{
    GDbItem **result;                       /* Liste à retourner           */
    size_t i;                               /* Boucle de parcours          */

    /**
     * Un verrou doit être posé !
     * Il n'y a pas d'assert() possible pour le vérifier...
     */

    *count = collec->count;

    if (*count == 0)
        result = NULL;

    else
    {
        result = malloc(*count * sizeof(GDbItem *));

        for (i = 0; i < *count; i++)
        {
            result[i] = collec->items[i];
            g_object_ref(G_OBJECT(result[i]));
        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = ensemble d'éléments à consulter.                    *
*                count  = taille de la liste constituée. [OUT]                *
*                                                                             *
*  Description : Renvoie la liste des éléments actifs.                        *
*                                                                             *
*  Retour      : Liste d'éléments à parcourir.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDbItem **g_db_collection_get_last_items(GDbCollection *collec, size_t *count)
{
    GDbItem **result;                       /* Liste à retourner           */
    GList *list;                            /* Liste brute des éléments    */
    GList *iter;                            /* Boucle de parcours #0       */
    size_t i;                               /* Boucle de parcours #1       */

    assert(!g_rw_lock_writer_trylock(&collec->params_access));

    list = g_hash_table_get_values(collec->last_items);

    *count = g_list_length(list);

    if (*count == 0)
        result = NULL;

    else
    {
        result = malloc(*count * sizeof(GDbItem *));

        for (iter = g_list_first(list), i = 0; iter != NULL; iter = g_list_next(iter), i++)
        {
            result[i] = iter->data;
            g_object_ref(G_OBJECT(result[i]));
        }

    }

    g_list_free(list);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = ensemble d'éléments à considérer.                   *
*                item   = élément de collection à manipuler.                  *
*                new    = précise la nature de l'élément à insérer.           *
*                                                                             *
*  Description : Ajoute un élément dans la liste des éléments actifs.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   :                                                              *
*                                                                             *
******************************************************************************/

static void g_db_collection_set_last_item(GDbCollection *collec, GDbItem *item, bool new)
{
    GDbItem *prev;                          /* Elément similaire précédent */
    timestamp_t its;                        /* Horodatage #0               */
    timestamp_t pts;                        /* Horodatage #1               */

    assert(!g_db_item_has_flag(item, DIF_DISABLED));

    prev = g_hash_table_lookup(collec->last_items, item);

    if (prev != NULL)
    {
        /**
         * Dans le cas où le changement intervient sans contexte particulier,
         * on s'assure de le pas remplacer un élément plus récent déjà en place
         * par un élément nouvellement actif mais dépassé.
         *
         * Le code de g_db_collection_disable_at(), aux conséquences portant
         * dans le serveur et le client, procède de manière à éviter cette
         * situation par un ordre de parcours choisi.
         *
         * On insère néanmoins une petite sécurité.
         */

        its = g_db_item_get_timestamp(item);
        pts = g_db_item_get_timestamp(prev);

        if (timestamp_is_younger(its, pts))
            goto already_up_to_date;

        g_object_ref(G_OBJECT(prev));

        if (g_db_item_get_flags(item) & DIF_ERASER)
        {
            g_signal_emit_by_name(collec, "active-changed", AIC_REMOVED, prev);
            g_hash_table_remove(collec->last_items, prev);
        }

        else
        {
            if (!new)
                g_db_item_add_flag(item, DIF_UPDATED);

            g_object_ref(G_OBJECT(item));
            g_object_ref(G_OBJECT(item));

            g_signal_emit_by_name(collec, "active-changed", AIC_UPDATED, item);
            g_hash_table_replace(collec->last_items, item, item);

        }

        g_object_unref(G_OBJECT(prev));

    }

    else
    {
        if ((g_db_item_get_flags(item) & DIF_ERASER) == 0)
        {
            g_object_ref(G_OBJECT(item));
            g_object_ref(G_OBJECT(item));

            g_signal_emit_by_name(collec, "active-changed", AIC_ADDED, item);
            g_hash_table_add(collec->last_items, item);

        }

    }

 already_up_to_date:

    ;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = ensemble d'éléments à considérer.                   *
*                item   = élément de collection à manipuler.                  *
*                                                                             *
*  Description : Procède à l'ajout d'un nouvel élément dans la collection.    *
*                                                                             *
*  Retour      : Bilan de l'exécution de l'opération.                         *
*                                                                             *
*  Remarques   : L'appelant perd la propriété de l'object transféré.          *
*                                                                             *
******************************************************************************/

bool g_db_collection_add_item(GDbCollection *collec, GDbItem *item)
{
    bool result;                            /* Bilan à faire remonter      */

    result = true;

    g_db_collection_wlock(collec);

    collec->items = realloc(collec->items, ++collec->count * sizeof(GDbItem *));
    collec->items[collec->count - 1] = item;

    g_db_collection_set_last_item(collec, item, true);

    g_signal_emit_by_name(collec, "content-extended", item);

    g_db_collection_wunlock(collec);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = ensemble d'éléments à considérer.                   *
*                pbuf   = paquet de données où venir inscrire les infos.      *
*                                                                             *
*  Description : Procède au retrait des éléments désactivés de la collection. *
*                                                                             *
*  Retour      : Bilan de l'exécution de l'opération.                         *
*                                                                             *
*  Remarques   :                                                              *
*                                                                             *
******************************************************************************/

bool g_db_collection_drop_disabled_items(GDbCollection *collec, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours          */
    GDbItem *item;                          /* Elément désactivé           */
#ifndef NDEBUG
    GDbItem *enabled;                       /* Eventuel similarité active  */
#endif

    /**
     * Voie de suppression d'un élément côté serveur.
     */

    result = true;

    g_db_collection_wlock(collec);

    for (i = collec->count; i > 0 && result; i--)
    {
        item = collec->items[i - 1];

        if (!g_db_item_has_flag(item, DIF_DISABLED))
            break;

#ifndef NDEBUG
        enabled = g_hash_table_lookup(collec->last_items, item);
        assert(enabled != item);
#endif

        collec->items = realloc(collec->items, --collec->count * sizeof(GDbItem *));

        result = g_db_collection_pack(collec, pbuf, DBA_REM_ITEM, item);

        g_object_unref(G_OBJECT(item));

    }

    g_db_collection_wunlock(collec);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = élément binaire à consulter.                        *
*                item   = définition de l'élément à retrouver.                *
*                                                                             *
*  Description : Retrouve l'élément correspondant à un horodatage.            *
*                                                                             *
*  Retour      : Indice valide pour un élément retrouvé, invalide sinon.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static size_t g_db_collection_find_by_timestamped(GDbCollection *collec, const GDbItem *item)
{
    size_t result;                          /* Indice à retourner          */
    GDbItem **found;                        /* Emplacement de la trouvaille*/

    found = bsearch(&item, collec->items, collec->count, sizeof(GDbItem *),
                    (__compar_fn_t)g_db_item_cmp_timestamp);

    if (found == NULL)
        result = collec->count;
    else
        result = found - collec->items;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = ensemble d'éléments à considérer.                   *
*                item   = élément de collection à manipuler.                  *
*                                                                             *
*  Description : Procède au retrait d'un élément dans la collection.          *
*                                                                             *
*  Retour      : Bilan de l'exécution de l'opération.                         *
*                                                                             *
*  Remarques   : L'appelant reste le propriétaire de l'object transféré.      *
*                                                                             *
******************************************************************************/

bool g_db_collection_remove_item(GDbCollection *collec, const GDbItem *item)
{
    bool result;                            /* Bilan à faire remonter      */
    size_t found;                           /* Indice de l'élément concerné*/
    GDbItem *disabled;                      /* Elément désactivé           */
#ifndef NDEBUG
    GDbItem *enabled;                       /* Eventuel similarité active  */
#endif

    /**
     * Voie de suppression d'un élément côté serveur.
     */

    g_db_collection_wlock(collec);

    found = g_db_collection_find_by_timestamped(collec, item);

    result = (found < collec->count);
    assert(result);

    if (result)
    {
        disabled = collec->items[found];

        assert(g_db_item_has_flag(disabled, DIF_DISABLED));

#ifndef NDEBUG
        enabled = g_hash_table_lookup(collec->last_items, disabled);
        assert(enabled != disabled);
#endif

        memmove(collec->items + found, collec->items + found + 1,
                (collec->count - found - 1) * sizeof(GDbItem *));

        collec->items = realloc(collec->items, --collec->count * sizeof(GDbItem *));

        g_object_unref(G_OBJECT(disabled));

    }

    g_db_collection_wunlock(collec);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = ensemble d'éléments à considérer.                   *
*                item   = élément de collection à manipuler.                  *
*                count  = décompte des éléments actifs.                       *
*                                                                             *
*  Description : Retire un élément de la liste des éléments courants.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   :                                                              *
*                                                                             *
******************************************************************************/

static void g_db_collection_unset_last_item(GDbCollection *collec, GDbItem *item, size_t count)
{
    GDbItem *prev;                          /* Elément similaire précédent */
    GDbItem *old;                           /* Ancien élément similaire    */
    size_t i;                               /* Boucle de parcours          */

    assert(g_db_item_has_flag(item, DIF_DISABLED));

    prev = g_hash_table_lookup(collec->last_items, item);

    if (prev == item)
    {
        old = NULL;

        for (i = count; i > 0; i++)
            if (g_db_item_cmp_key(collec->items[i - 1], item))
                break;
            else
                old = collec->items[i - 1];

        if (old == NULL || g_db_item_get_flags(old) & DIF_ERASER)
        {
            g_signal_emit_by_name(collec, "active-changed", AIC_REMOVED, item);
            g_hash_table_remove(collec->last_items, item);
        }

        else
        {
            g_object_ref(G_OBJECT(old));
            g_object_ref(G_OBJECT(old));

            g_signal_emit_by_name(collec, "active-changed", AIC_UPDATED, old);
            g_hash_table_replace(collec->last_items, old, old);

        }

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary    = élément binaire à consulter.                     *
*                timestamp = date du dernier élément à garder comme actif.    *
*                                                                             *
*  Description : Retrouve le premier élément correspondant à un horodatage.   *
*                                                                             *
*  Retour      : Indice valide pour un élément retrouvé, invalide sinon.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static size_t g_db_collection_find_by_timestamp(GDbCollection *collec, timestamp_t timestamp)
{
    size_t result;                          /* Indice à retourner          */
    timestamp_t prev_ts;                    /* Horodatage précédent        */

    bsearch_index(&timestamp, collec->items, collec->count, sizeof(GDbItem *),
                  (__compar_fn_t)g_db_item_cmp_with_timestamp, &result);

    while (result > 0)
    {
        prev_ts = g_db_item_get_timestamp(collec->items[result - 1]);

        if (cmp_timestamp(&prev_ts, &timestamp) != 0)
            break;

        result--;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary    = élément binaire à consulter.                     *
*                timestamp = date du dernier élément à garder comme actif.    *
*                db        = base de données à mettre à jour.                 *
*                pbuf      = paquet de données où venir inscrire les infos.   *
*                                                                             *
*  Description : Désactive les éléments en aval d'un horodatage donné.        *
*                                                                             *
*  Retour      : true si la commande a bien été envoyée, false sinon.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_db_collection_disable_at(GDbCollection *collec, timestamp_t timestamp, sqlite3 *db, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    size_t start;                           /* Début de la zone à changer  */
    size_t back;                            /* Début de restauration       */
    size_t i;                               /* Boucle de parcours          */
    GDbItem *item;                          /* Elément à traiter           */

    result = true;

    g_db_collection_wlock(collec);

    start = g_db_collection_find_by_timestamp(collec, timestamp);

    /* Réactivation d'éléments ? */

    if (start > 0)
    {
        back = start;

        for (i = start; i > 0; i--)
            if (!g_db_item_has_flag(collec->items[i - 1], DIF_DISABLED))
                break;
            else
                back--;

        for (i = back; i < start && result; i++)
        {
            item = collec->items[i];

            g_db_item_remove_flag(item, DIF_DISABLED);

            g_db_collection_store_updated_item(collec, item, db);

            g_db_collection_set_last_item(collec, item, false);

            result = g_db_collection_pack(collec, pbuf, DBA_CHANGE_STATE, item);

        }

    }

    /* Désactivation des éléments en queue */

    for (i = start; i < collec->count && result; i++)
    {
        item = collec->items[i];

        if (g_db_item_has_flag(item, DIF_DISABLED))
            break;

        g_db_item_add_flag(item, DIF_DISABLED);

        g_db_collection_store_updated_item(collec, item, db);

        g_db_collection_unset_last_item(collec, item, start);

        result = g_db_collection_pack(collec, pbuf, DBA_CHANGE_STATE, item);

    }

    g_db_collection_wunlock(collec);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = ensemble d'éléments à considérer.                   *
*                item   = élément de collection à manipuler.                  *
*                                                                             *
*  Description : Prend acte d'un changement d'état d'un élément de collection.*
*                                                                             *
*  Retour      : Bilan de l'exécution de l'opération.                         *
*                                                                             *
*  Remarques   : L'appelant reste le propriétaire de l'object transféré.      *
*                                                                             *
******************************************************************************/

bool g_db_collection_update_item_state(GDbCollection *collec, const GDbItem *item)
{
    bool result;                            /* Bilan à faire remonter      */
    size_t index;                           /* Indice de l'élément visé    */
    GDbItem *changed;                       /* Elément à basculer          */
    DbItemFlags new;                        /* Nouvelles propriétés        */

    result = false;

    g_db_collection_wlock(collec);

    index = g_db_collection_find_by_timestamped(collec, item);

    result = (index < collec->count);

    if (result)
    {
        changed = collec->items[index];

        new = g_db_item_get_flags(item);

        g_db_item_set_flags(changed, new);

        if (new & DIF_DISABLED)
            g_db_collection_unset_last_item(collec, changed, index);
        else
            g_db_collection_set_last_item(collec, changed, false);

        g_signal_emit_by_name(collec, "state-changed", changed);

    }

    g_db_collection_wunlock(collec);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       MANIPULATIONS AVEC UNE BASE DE DONNEES                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = ensemble d'éléments spectateur des opérations.      *
*                db     = accès à la base de données.                         *
*                                                                             *
*  Description : Crée la table d'élément dans une base de données.            *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_db_collection_create_db_table(const GDbCollection *collec, sqlite3 *db)
{
    return G_DB_COLLECTION_GET_CLASS(collec)->create_table(collec, db);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : values = couples de champs et de valeurs à lier.             *
*                count  = nombre de ces couples.                              *
*                collec = collection à manipuler.                             *
*                                                                             *
*  Description : Charge et intère un élément dans une collection.             *
*                                                                             *
*  Retour      : Bilan de l'opération : succès ou non.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_db_collection_load_new_item(const bound_value *values, size_t count, GDbCollection *collec)
{
    bool result;                            /* Bilan à retourner           */
    GDbItem *new;                           /* Nouvel élément à insérer    */

    new = g_object_new(G_DB_COLLECTION(collec)->type, NULL);

    result = g_db_item_load(new, values, count);

    if (result)
        result = g_db_collection_add_item(G_DB_COLLECTION(collec), new);
    else
        g_object_unref(G_OBJECT(new));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = ensemble d'éléments à peupler.                      *
*                db     = base de données repondant aux requêtes.             *
*                                                                             *
*  Description : Charge un ensemble d'éléments à partir d'une base de données.*
*                                                                             *
*  Retour      : Bilan de l'exécution de l'opération.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_db_collection_load_all_items(GDbCollection *collec, sqlite3 *db)
{
    bool result;                            /* Conclusion à faire remonter */
    GDbItem *dummy;                         /* Interface vide              */
    bound_value *values;                    /* Champs de table à inclure   */
    size_t count;                           /* Nombre de ces champs        */

    dummy = g_object_new(collec->type, NULL);

    result = g_db_item_setup_load(dummy, &values, &count);

    g_object_unref(G_OBJECT(dummy));

    if (result)
        result = load_db_values(db, collec->name, values, count, (db_load_cb)g_db_collection_load_new_item, collec);

    free_all_bound_values(values, count);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = ensemble d'éléments à considérer.                   *
*                item   = élément de collection à enregistrer.                *
*                db     = base de données à mettre à jour.                    *
*                                                                             *
*  Description : Enregistre un élément de collection dans une base de données.*
*                                                                             *
*  Retour      : Bilan de l'exécution de l'opération.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_db_collection_store_item(const GDbCollection *collec, const GDbItem *item, sqlite3 *db)
{
    bool result;                            /* Conclusion à faire remonter */
    bound_value *values;                    /* Champs de table à inclure   */
    size_t count;                           /* Nombre de ces champs        */

    result = g_db_item_store(item, &values, &count);

    if (result)
        result = store_db_values(db, collec->name, values, count);

    free_all_bound_values(values, count);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = ensemble d'éléments à considérer.                   *
*                item   = élément de collection à enregistrer.                *
*                db     = base de données à mettre à jour.                    *
*                                                                             *
*  Description : Met à jour un élément de collection dans une base de données.*
*                                                                             *
*  Retour      : Bilan de l'exécution de l'opération.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_db_collection_store_updated_item(const GDbCollection *collec, const GDbItem *item, sqlite3 *db)
{
    bool result;                            /* Conclusion à faire remonter */
    bound_value *values;                    /* Champs de table à inclure   */
    size_t count;                           /* Nombre de ces champs        */
    bound_value *updates;                   /* Champs à mettre à jour      */
    size_t ucount;                          /* Nombre de ces champs        */
    bound_value *conds;                     /* Champs de condition         */
    size_t ccount;                          /* Nombre de ces champs        */
    const bound_value *flags_ptr;           /* Emplacement des fanions     */
    size_t i;                               /* Boucle de parcours          */

    result = false;

    if (!g_db_item_store(item, &values, &count))
        goto building_values;

    updates = malloc(1 * sizeof(bound_value));
    ucount = 0;

    conds = malloc((count - 1) * sizeof(bound_value));
    ccount = 0;

    flags_ptr = find_bound_value(values, count, "flags");

    for (i = 0; i < count; i++)
    {
        if (&values[i] == flags_ptr)
        {
            assert(ucount < 1);
            memcpy(&updates[ucount++], &values[i], sizeof(bound_value));
        }
        else
        {
            assert(ccount < (count - 1));
            memcpy(&conds[ccount++], &values[i], sizeof(bound_value));
        }
    }

    result = update_db_values(db, collec->name, updates, ucount, conds, ccount);

 building_values:

    free_all_bound_values(values, count);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                     CREATION DE L'ABSTRACTION POUR COLLECTIONS                     */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : list   = ensemble de collectons à parcourir.                 *
*                binary = binaire sur lequel appliquer les éléments.          *
*                                                                             *
*  Description : Attache un binaire à une série de collections.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void attach_binary_to_collections(GList *list, GLoadedBinary *binary)
{
    GList *iter;                            /* Boucle de parcours          */
    GDbCollection *collec;                  /* Collection visée manipulée  */

    for (iter = g_list_first(list);
         iter != NULL;
         iter = g_list_next(iter))
    {
        collec = G_DB_COLLECTION(iter->data);

        g_db_collection_link_to_binary(collec, binary);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list = ensemble de collectons à parcourir.                   *
*                id   = identifiant interne du type d'éléments groupés.       *
*                                                                             *
*  Description : Recherche une collection correspondant à un type donné.      *
*                                                                             *
*  Retour      : Collection trouvée ou NULL en cas d'échec.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDbCollection *find_collection_in_list(GList *list, uint32_t id)
{
    GDbCollection *result;                  /* Collection trouvée renvoyée */
    GList *iter;                            /* Boucle de parcours          */

    result = NULL;

    for (iter = g_list_first(list);
         iter != NULL;
         iter = g_list_next(iter))
    {
        result = G_DB_COLLECTION(iter->data);

        if (g_db_collection_get_feature(result) == id)
            break;

    }

    return (iter != NULL ? result : NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list  = ensemble de collectons à parcourir.                  *
*                write = précise le type d'accès prévu (lecture/écriture).    *
*                lock  = indique le sens du verrouillage à mener.             *
*                                                                             *
*  Description : Met à disposition un encadrement des accès aux éléments.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void lock_unlock_collections(GList *list, bool write, bool lock)
{
    GList *iter;                            /* Boucle de parcours          */
    GDbCollection *collec;                  /* Collection visée manipulée  */

    for (iter = g_list_first(list);
         iter != NULL;
         iter = g_list_next(iter))
    {
        collec = G_DB_COLLECTION(iter->data);

        g_db_collection_lock_unlock(collec, write, lock);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list = ensemble de collectons à traiter.                     *
*                pbuf = paquet de données où venir inscrire des infos.        *
*                                                                             *
*  Description : Collecte les informations utiles pour un nouvel arrivant.    *
*                                                                             *
*  Retour      : Bilan du déroulement des opérations.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool pack_all_collection_updates(GList *list, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GList *iter;                            /* Boucle de parcours          */
    GDbCollection *collec;                  /* Collection visée manipulée  */

    result = true;

    /**
     * Cette procédure n'est appelée que depuis g_cdb_archive_process(),
     * qui bloque son exécution jusqu'à la fin des opérations.
     *
     * On a donc l'assurance d'un récupérer tous les éléments d'un coup,
     * sans activité parallèle.
     */

    for (iter = g_list_first(list);
         iter != NULL && result;
         iter = g_list_next(iter))
    {
        collec = G_DB_COLLECTION(iter->data);

        result = g_db_collection_pack_all_updates(collec, pbuf);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list   = ensemble de collectons à traiter.                   *
*                inbuf  = paquet de données où venir puiser les infos.        *
*                outbuf = paquet de données où inscrire les mises à jour.     *
*                db     = base de données à mettre à jour.                    *
*                                                                             *
*  Description : Met à jour les statuts d'activité des éléments.              *
*                                                                             *
*  Retour      : Bilan du déroulement des opérations.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool update_activity_in_collections(GList *list, packed_buffer_t *inbuf, packed_buffer_t *outbuf, sqlite3 *db)
{
    bool result;                            /* Résultat global à renvoyer  */
    bool status;                            /* Bilan de lecture initiale   */
    timestamp_t timestamp;                  /* Horodatage de limite        */
    GList *iter;                            /* Boucle de parcours          */
    GDbCollection *collec;                  /* Collection visée manipulée  */

    result = true;

    /**
     * Cette procédure n'est appelée que depuis g_cdb_archive_process(),
     * qui bloque son exécution jusqu'à la fin des opérations.
     *
     * On a donc l'assurance d'un traitement global homgène des horodatages.
     */

    status = unpack_timestamp(&timestamp, inbuf);
    if (!status) return false;

    for (iter = g_list_first(list);
         iter != NULL && result;
         iter = g_list_next(iter))
    {
        collec = G_DB_COLLECTION(iter->data);

        result = g_db_collection_disable_at(collec, timestamp, db, outbuf);

    }

    return result;

}
