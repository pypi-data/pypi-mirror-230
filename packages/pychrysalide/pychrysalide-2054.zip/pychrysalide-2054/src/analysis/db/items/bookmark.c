
/* Chrysalide - Outil d'analyse de fichiers binaires
 * bookmark.c - gestion des signets au sein d'un binaire
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


#include "bookmark.h"


#include <stdarg.h>
#include <stdio.h>
#include <sys/socket.h>


#include <i18n.h>


#include "../collection-int.h"
#include "../item-int.h"
#include "../../../glibext/gbinarycursor.h"



/* --------------------- ELABORATION D'UN ELEMENT DE COLLECTION --------------------- */


/* Signet à l'intérieur d'une zone de texte (instance) */
struct _GDbBookmark
{
    GDbItem parent;                         /* A laisser en premier        */

    vmpa2t addr;                            /* Adresse du signet           */
    rle_string comment;                     /* Eventuel commentaire associé*/

};

/* Signet à l'intérieur d'une zone de texte (classe) */
struct _GDbBookmarkClass
{
    GDbItemClass parent;                    /* A laisser en premier        */

};


/* Initialise la classe des signets dans une zone de texte. */
static void g_db_bookmark_class_init(GDbBookmarkClass *);

/* Initialise un signet dans une zone de texte. */
static void g_db_bookmark_init(GDbBookmark *);

/* Supprime toutes les références externes. */
static void g_db_bookmark_dispose(GDbBookmark *);

/* Procède à la libération totale de la mémoire. */
static void g_db_bookmark_finalize(GDbBookmark *);

/* Calcule le condensat associé à l'élément vu comme clef. */
static guint g_db_bookmark_hash_key(const GDbBookmark *);

/* Compare deux éléments en tant que clefs. */
static gboolean g_db_bookmark_cmp_key(const GDbBookmark *, const GDbBookmark *);

/* Effectue la comparaison entre deux signets de collection. */
static gint g_db_bookmark_cmp(const GDbBookmark *, const GDbBookmark *);

/* Importe la définition d'un signet dans un flux réseau. */
static bool g_db_bookmark_unpack(GDbBookmark *, packed_buffer_t *);

/* Exporte la définition d'un signet dans un flux réseau. */
static bool g_db_bookmark_pack(const GDbBookmark *, packed_buffer_t *);

/* Construit la description humaine d'un signet sur un tampon. */
static char *g_db_bookmark_build_label(const GDbBookmark *);

/* Exécute un signet sur un tampon de binaire chargé. */
static bool g_db_bookmark_run(GDbBookmark *, GLoadedBinary *, bool);

/* Applique un signet sur un tampon de binaire chargé. */
static bool g_db_bookmark_apply(GDbBookmark *, GLoadedBinary *);

/* Annule un signet sur un tampon de binaire chargé. */
static bool g_db_bookmark_cancel(GDbBookmark *, GLoadedBinary *);

/* Charge les valeurs utiles pour un signet. */
static bool g_db_bookmark_load(GDbBookmark *, const bound_value *, size_t);

/* Constitue les champs destinés à une insertion / modification. */
static bool g_db_bookmark_store(const GDbBookmark *, bound_value **, size_t *);



/* ---------------------- DEFINITION DE LA COLLECTION ASSOCIEE ---------------------- */


/* Collection dédiée aux signets (instance) */
struct _GBookmarkCollection
{
    GDbCollection parent;                   /* A laisser en premier        */

};

/* Collection dédiée aux signets (classe) */
struct _GBookmarkCollectionClass
{
    GDbCollectionClass parent;              /* A laisser en premier        */

};


/* Initialise la classe des signets dans une zone de texte. */
static void g_bookmark_collection_class_init(GBookmarkCollectionClass *);

/* Initialise un signet dans une zone de texte. */
static void g_bookmark_collection_init(GBookmarkCollection *);

/* Supprime toutes les références externes. */
static void g_bookmark_collection_dispose(GBookmarkCollection *);

/* Procède à la libération totale de la mémoire. */
static void g_bookmark_collection_finalize(GBookmarkCollection *);

/* Crée la table des signets dans une base de données. */
static bool g_bookmark_collection_create_db_table(const GBookmarkCollection *, sqlite3 *);



/* ---------------------------------------------------------------------------------- */
/*                       ELABORATION D'UN ELEMENT DE COLLECTION                       */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un signet à l'intérieur d'une zone de texte. */
G_DEFINE_TYPE(GDbBookmark, g_db_bookmark, G_TYPE_DB_ITEM);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des signets dans une zone de texte.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_bookmark_class_init(GDbBookmarkClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDbItemClass *item;                     /* Encore une autre vision...  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_db_bookmark_dispose;
    object->finalize = (GObjectFinalizeFunc)g_db_bookmark_finalize;

    item = G_DB_ITEM_CLASS(klass);

    item->feature = DBF_BOOKMARKS;

    item->hash_key = (hash_db_item_key_fc)g_db_bookmark_hash_key;
    item->cmp_key = (cmp_db_item_key_fc)g_db_bookmark_cmp_key;
    item->cmp = (cmp_db_item_fc)g_db_bookmark_cmp;

    item->unpack = (unpack_db_item_fc)g_db_bookmark_unpack;
    item->pack = (pack_db_item_fc)g_db_bookmark_pack;

    item->build_label = (build_item_label_fc)g_db_bookmark_build_label;
    item->apply = (run_item_fc)g_db_bookmark_apply;
    item->cancel = (run_item_fc)g_db_bookmark_cancel;

    item->load = (load_db_item_fc)g_db_bookmark_load;
    item->store = (store_db_item_fc)g_db_bookmark_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bookmark = instance à initialiser.                           *
*                                                                             *
*  Description : Initialise un signet dans une zone de texte.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_bookmark_init(GDbBookmark *bookmark)
{
    init_vmpa(&bookmark->addr, VMPA_NO_PHYSICAL, VMPA_NO_VIRTUAL);

    setup_empty_rle_string(&bookmark->comment);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bookmark = instance d'objet GLib à traiter.                  *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_bookmark_dispose(GDbBookmark *bookmark)
{
    G_OBJECT_CLASS(g_db_bookmark_parent_class)->dispose(G_OBJECT(bookmark));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bookmark = instance d'objet GLib à traiter.                  *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_bookmark_finalize(GDbBookmark *bookmark)
{
    exit_rle_string(&bookmark->comment);

    G_OBJECT_CLASS(g_db_bookmark_parent_class)->finalize(G_OBJECT(bookmark));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : addr    = adresse inamovible localisant une position donnée. *
*                comment = commentaire construit ou NULL.                     *
*                                                                             *
*  Description : Crée une définition d'un signet dans une zone de texte.      *
*                                                                             *
*  Retour      : Signet mis en place ou NULL en cas d'erreur.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDbBookmark *g_db_bookmark_new(const vmpa2t *addr, const char *comment)
{
    GDbBookmark *result;                    /* Instance à retourner        */
    bool status;                            /* Bilan de l'initialisation   */

    result = g_object_new(G_TYPE_DB_BOOKMARK, NULL);

    status = g_db_bookmark_fill(result, addr, comment);
    if (!status) goto error;

    return result;

 error:

    g_object_unref(G_OBJECT(result));

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bookmark = signet à initialiser.                             *
*                addr     = adresse inamovible localisant une position donnée.*
*                comment  = commentaire construit ou NULL.                    *
*                                                                             *
*  Description : Initialise la définition d'un signet dans une zone de texte. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_db_bookmark_fill(GDbBookmark *bookmark, const vmpa2t *addr, const char *comment)
{
    bool result;                            /* Bilan à retourner           */

    /**
     * Cette fonction est principalement destinée aux initialisations
     * depuis l'extension Python.
     */

    result = true;

    copy_vmpa(&bookmark->addr, addr);

    dup_into_rle_string(&bookmark->comment, comment);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bookmark = élément de collection à consulter.                *
*                                                                             *
*  Description : Calcule le condensat associé à l'élément vu comme clef.      *
*                                                                             *
*  Retour      : Condensat associé à l'élément.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static guint g_db_bookmark_hash_key(const GDbBookmark *bookmark)
{
    guint result;                           /* Valeur "unique" à renvoyer  */

    result = hash_vmpa(&bookmark->addr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = premier élément de collection à consulter.               *
*                b = second élément de collection à consulter.                *
*                                                                             *
*  Description : Compare deux éléments en tant que clefs.                     *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean g_db_bookmark_cmp_key(const GDbBookmark *a, const GDbBookmark *b)
{
    gboolean result;                        /* Bilan à retourner           */
    int ret;                                /* Bilan intermédiaire         */

    ret = cmp_vmpa(&a->addr, &b->addr);

    result = (ret == 0);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = premier élément à analyser.                              *
*                b = second élément à analyser.                               *
*                                                                             *
*  Description : Effectue la comparaison entre deux signets de collection.    *
*                                                                             *
*  Retour      : Bilan de la comparaison : -1, 0 ou 1.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gint g_db_bookmark_cmp(const GDbBookmark *a, const GDbBookmark *b)
{
    gint result;                            /* Bilan de la comparaison     */

    result = cmp_vmpa(&a->addr, &b->addr);

    if (result == 0)
        result = cmp_rle_string(&a->comment, &b->comment);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bookmark = signet dont les informations sont à charger. [OUT]*
*                pbuf     = paquet de données où venir inscrire les infos.    *
*                                                                             *
*  Description : Importe la définition d'un signet dans un flux réseau.       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_db_bookmark_unpack(GDbBookmark *bookmark, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    result = G_DB_ITEM_CLASS(g_db_bookmark_parent_class)->unpack(G_DB_ITEM(bookmark), pbuf);

    if (result)
        result = unpack_vmpa(&bookmark->addr, pbuf);

    if (result)
        result = unpack_rle_string(&bookmark->comment, pbuf);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bookmark = informations à sauvegarder.                       *
*                pbuf     = paquet de données où venir inscrire les infos.    *
*                                                                             *
*  Description : Exporte la définition d'un signet dans un flux réseau.       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_db_bookmark_pack(const GDbBookmark *bookmark, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    result = G_DB_ITEM_CLASS(g_db_bookmark_parent_class)->pack(G_DB_ITEM(bookmark), pbuf);

    if (result)
        result = pack_vmpa(&bookmark->addr, pbuf);

    if (result)
        result = pack_rle_string(&bookmark->comment, pbuf);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bookmark = signet à manipuler.                               *
*                                                                             *
*  Description : Construit la description humaine d'un signet sur un tampon.  *
*                                                                             *
*  Retour      : Chaîne de caractère correspondante.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_db_bookmark_build_label(const GDbBookmark *bookmark)
{
    char *result;                           /* Description à retourner     */
    DbItemFlags flags;                      /* Propriétés de l'élément     */
    const char *text;                       /* Commentaire associé         */
    const char *prefix;                     /* Préfixe à ajouter           */

    flags = g_db_item_get_flags(G_DB_ITEM(bookmark));

    if (flags & DIF_ERASER)
        asprintf(&result, _("Removed bookmark"));

    else if (flags & DIF_UPDATED)
    {
        text = get_rle_string(&bookmark->comment);

        if (text != NULL)
            asprintf(&result, _("Updated bookmark: \"%s\""), text);
        else
            asprintf(&result, _("Reset bookmark"));
    }

    else
    {
        prefix = _("Created");

        text = get_rle_string(&bookmark->comment);

        if (text != NULL)
            asprintf(&result, _("%s bookmark \"%s\""), prefix, text);
        else
            asprintf(&result, _("%s empty bookmark"), prefix);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bookmark = signet à manipuler.                               *
*                binary   = binaire chargé en mémoire à modifier.             *
*                set      = précision quant au nouvel état du drapeau.        *
*                                                                             *
*  Description : Exécute un signet sur un tampon de binaire chargé.           *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_db_bookmark_run(GDbBookmark *bookmark, GLoadedBinary *binary, bool set)
{
    bool result;                            /* Bilan à faire remonter      */
    GBufferCache *cache;                    /* Tampon d'impression colorée */
    GLineCursor *cursor;                    /* Emplacement dans un tampon  */
    size_t index;                           /* Indice de ligne à traiter   */

    result = false;

    cache = g_loaded_binary_get_disassembly_cache(binary);
    if (cache == NULL) goto exit;

    g_buffer_cache_wlock(cache);

    /* Recherche de la ligne concernée */

    cursor = g_binary_cursor_new();
    g_binary_cursor_update(G_BINARY_CURSOR(cursor), &bookmark->addr);

    index = g_buffer_cache_find_index_by_cursor(cache, cursor, true);

    g_object_unref(G_OBJECT(cursor));

    index = g_buffer_cache_look_for_flag(cache, index, BLF_HAS_CODE);

    /* Application du changement */

    result = (index < g_buffer_cache_count_lines(cache));

    if (result)
    {
        if (set)
            g_buffer_cache_add_line_flag(cache, index, BLF_BOOKMARK);
        else
            g_buffer_cache_remove_line_flag(cache, index, BLF_BOOKMARK);

    }

    /* Sortie */

    g_buffer_cache_wunlock(cache);

    g_object_unref(G_OBJECT(cache));

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bookmark = signet à manipuler.                               *
*                binary   = binaire chargé en mémoire à modifier.             *
*                                                                             *
*  Description : Applique un signet sur un tampon de binaire chargé.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_db_bookmark_apply(GDbBookmark *bookmark, GLoadedBinary *binary)
{
    bool result;                            /* Bilan à faire remonter      */
    DbItemFlags flags;                      /* Propriétés de l'élément     */

    flags = g_db_item_get_flags(G_DB_ITEM(bookmark));

    result = g_db_bookmark_run(bookmark, binary, (flags & DIF_ERASER) == 0);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bookmark = signet à manipuler.                               *
*                binary   = binaire chargé en mémoire à modifier.             *
*                                                                             *
*  Description : Annule un signet sur un tampon de binaire chargé.            *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_db_bookmark_cancel(GDbBookmark *bookmark, GLoadedBinary *binary)
{
    bool result;                            /* Bilan à faire remonter      */
    DbItemFlags flags;                      /* Propriétés de l'élément     */

    flags = g_db_item_get_flags(G_DB_ITEM(bookmark));

    result = g_db_bookmark_run(bookmark, binary, (flags & DIF_ERASER) != 0);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bookmark = bascule d'affichage à charger depuis les réponses.*
*                values   = tableau d'éléments à consulter.                   *
*                count    = nombre de descriptions renseignées.               *
*                                                                             *
*  Description : Charge les valeurs utiles pour un signet.                    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_db_bookmark_load(GDbBookmark *bookmark, const bound_value *values, size_t count)
{
    bool result;                            /* Bilan à faire remonter      */

    result = G_DB_ITEM_CLASS(g_db_bookmark_parent_class)->load(G_DB_ITEM(bookmark), values, count);

    if (result) result = load_vmpa(&bookmark->addr, NULL, values, count);

    if (result) result = load_rle_string(&bookmark->comment, "comment", values, count);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bookmark = base d'éléments sur laquelle s'appuyer.           *
*                values   = couples de champs et de valeurs à lier. [OUT]     *
*                count    = nombre de ces couples. [OUT]                      *
*                                                                             *
*  Description : Constitue les champs destinés à une insertion / modification.*
*                                                                             *
*  Retour      : Etat du besoin en sauvegarde.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_db_bookmark_store(const GDbBookmark *bookmark, bound_value **values, size_t *count)
{
    bool status;                            /* Bilan d'opération initiale  */

    if (bookmark == NULL)
        status = G_DB_ITEM_CLASS(g_db_bookmark_parent_class)->store(NULL, values, count);
    else
        status = G_DB_ITEM_CLASS(g_db_bookmark_parent_class)->store(G_DB_ITEM(bookmark), values, count);

    if (!status) return false;

    if (bookmark == NULL)
        status = store_vmpa(NULL, NULL, values, count);
    else
        status = store_vmpa(&bookmark->addr, NULL, values, count);

    if (!status) return false;

    if (bookmark == NULL)
        status &= store_rle_string(NULL, "comment", values, count);
    else
        status &= store_rle_string(&bookmark->comment, "comment", values, count);

    if (!status) return false;

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bookmark = informations à consulter.                         *
*                                                                             *
*  Description : Fournit l'adresse associée à un signet.                      *
*                                                                             *
*  Retour      : Adresse mémoire.                                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const vmpa2t *g_db_bookmark_get_address(const GDbBookmark *bookmark)
{
    const vmpa2t *result;                   /* Localisation à retourner    */

    result = &bookmark->addr;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bookmark = informations à consulter.                         *
*                                                                             *
*  Description : Fournit le commentaire associé à un signet.                  *
*                                                                             *
*  Retour      : Commentaire existant ou NULL.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_db_bookmark_get_comment(const GDbBookmark *bookmark)
{
    const char *result;                     /* Commentaire à renvoyer      */

    result = get_rle_string(&bookmark->comment);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                        DEFINITION DE LA COLLECTION ASSOCIEE                        */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une collection de signets. */
G_DEFINE_TYPE(GBookmarkCollection, g_bookmark_collection, G_TYPE_DB_COLLECTION);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des signets dans une zone de texte.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_bookmark_collection_class_init(GBookmarkCollectionClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDbCollectionClass *collec;             /* Encore une autre vision...  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_bookmark_collection_dispose;
    object->finalize = (GObjectFinalizeFunc)g_bookmark_collection_finalize;

    collec = G_DB_COLLECTION_CLASS(klass);

    collec->create_table = (collec_create_db_table_fc)g_bookmark_collection_create_db_table;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise un signet dans une zone de texte.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_bookmark_collection_init(GBookmarkCollection *collec)
{
    G_DB_COLLECTION(collec)->featuring = DBF_BOOKMARKS;
    G_DB_COLLECTION(collec)->type = G_TYPE_DB_BOOKMARK;
    G_DB_COLLECTION(collec)->name = "Bookmarks";

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

static void g_bookmark_collection_dispose(GBookmarkCollection *collec)
{
    G_OBJECT_CLASS(g_bookmark_collection_parent_class)->dispose(G_OBJECT(collec));

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

static void g_bookmark_collection_finalize(GBookmarkCollection *collec)
{
    G_OBJECT_CLASS(g_bookmark_collection_parent_class)->finalize(G_OBJECT(collec));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée une collection dédiée aux signets.                      *
*                                                                             *
*  Retour      : Collection mise en place.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBookmarkCollection *g_bookmark_collection_new(void)
{
    GBookmarkCollection *result;            /* Instance à retourner        */

    result = g_object_new(G_TYPE_BM_COLLECTION, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = ensemble d'éléments spectateur des opérations.      *
*                db     = accès à la base de données.                         *
*                                                                             *
*  Description : Crée la table des signets dans une base de données.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_bookmark_collection_create_db_table(const GBookmarkCollection *collec, sqlite3 *db)
{
    const char *sql;                        /* Patron de requête SQL       */
    char *addr_fields;                      /* Champs pour l'adresse       */
    char *request;                          /* Requête à exécuter          */
    char *msg;                              /* Message d'erreur            */
    int ret;                                /* Bilan de la création        */

    sql = "CREATE TABLE Bookmarks ("            \
             SQLITE_DB_ITEM_CREATE ", "         \
             "%s, "                             \
             SQLITE_RLESTR_CREATE("comment")    \
          ");";

    addr_fields = create_vmpa_db_table(NULL);

    asprintf(&request, sql, addr_fields);

    ret = sqlite3_exec(db, request, NULL, NULL, &msg);

    free(addr_fields);
    free(request);

    if (ret != SQLITE_OK)
    {
        fprintf(stderr, "sqlite3_exec(): %s\n", msg);
        sqlite3_free(msg);
    }

    return (ret == SQLITE_OK);

}
