
/* Chrysalide - Outil d'analyse de fichiers binaires
 * move.c - mémorisation des déplacements au sein de code
 *
 * Copyright (C) 2016-2019 Cyrille Bagard
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


#include "move.h"


#include <assert.h>
#include <malloc.h>
#include <stdio.h>
#include <sys/socket.h>


#include <i18n.h>


#include "../collection-int.h"
#include "../item-int.h"
#ifdef INCLUDE_GTK_SUPPORT
#   include "../../../gui/core/global.h"
#endif
#include "../../../glibext/gbinarycursor.h"
#ifdef INCLUDE_GTK_SUPPORT
#   include "../../../glibext/gloadedpanel.h"
#endif



/* --------------------- ELABORATION D'UN ELEMENT DE COLLECTION --------------------- */


/* Déplacement d'un emplacement à un autre dans du code (instance) */
struct _GDbMove
{
    GDbItem parent;                         /* A laisser en premier        */

    GLineCursor *src;                       /* Emplacement de départ       */
    GLineCursor *dest;                      /* Emplacement d'arrivée       */

};

/* Déplacement d'un emplacement à un autre dans du code (classe) */
struct _GDbMoveClass
{
    GDbItemClass parent;                    /* A laisser en premier        */

};


/* Initialise la classe des déplacements au sein de codes. */
static void g_db_move_class_init(GDbMoveClass *);

/* Initialise une bascule d'affichage pour opérande numérique. */
static void g_db_move_init(GDbMove *);

/* Supprime toutes les références externes. */
static void g_db_move_dispose(GDbMove *);

/* Procède à la libération totale de la mémoire. */
static void g_db_move_finalize(GDbMove *);

/* Effectue la comparaison entre deux changements de position. */
static gint g_db_move_cmp(const GDbMove *, const GDbMove *);

/* Importe la définition d'un déplacement depuis un flux réseau. */
static bool g_db_move_unpack(GDbMove *, packed_buffer_t *);

/* Exporte la définition d'un déplacement dans un flux réseau. */
static bool g_db_move_pack(const GDbMove *, packed_buffer_t *);

/* Construit la description humaine d'un déplacement. */
static char *g_db_move_build_label(GDbMove *);

/* Exécute un déplacement dans une zone de code. */
static bool g_db_move_run(const GDbMove *, GLineCursor *);

/* Applique un déplacement au sein d'une zone de code. */
static bool g_db_move_apply(GDbMove *, GLoadedBinary *);

/* Annule un déplacement au sein d'une zone de code. */
static bool g_db_move_cancel(GDbMove *, GLoadedBinary *);

/* Charge les valeurs utiles pour un déplacement dans du code. */
static bool g_db_move_load(GDbMove *, const bound_value *, size_t);

/* Constitue les champs destinés à une insertion / modification. */
static bool g_db_move_store(const GDbMove *, bound_value **, size_t *);



/* ---------------------- DEFINITION DE LA COLLECTION ASSOCIEE ---------------------- */


/* Collection dédiée aux basculements d'affichage (instance) */
struct _GMoveCollection
{
    GDbCollection parent;                   /* A laisser en premier        */

};

/* Collection dédiée aux basculements d'affichage (classe) */
struct _GMoveCollectionClass
{
    GDbCollectionClass parent;              /* A laisser en premier        */

};


/* Initialise la classe des collections de déplacements. */
static void g_move_collection_class_init(GMoveCollectionClass *);

/* Initialise une collection de déplacements. */
static void g_move_collection_init(GMoveCollection *);

/* Supprime toutes les références externes. */
static void g_move_collection_dispose(GMoveCollection *);

/* Procède à la libération totale de la mémoire. */
static void g_move_collection_finalize(GMoveCollection *);

/* Crée la table des basculements dans une base de données. */
static bool g_move_collection_create_db_table(const GMoveCollection *, sqlite3 *);



/* ---------------------------------------------------------------------------------- */
/*                       ELABORATION D'UN ELEMENT DE COLLECTION                       */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un déplacement au sein de code. */
G_DEFINE_TYPE(GDbMove, g_db_move, G_TYPE_DB_ITEM);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des déplacements au sein de codes.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_move_class_init(GDbMoveClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDbItemClass *item;                     /* Encore une autre vision...  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_db_move_dispose;
    object->finalize = (GObjectFinalizeFunc)g_db_move_finalize;

    item = G_DB_ITEM_CLASS(klass);

    item->feature = DBF_MOVES;

    item->cmp = (cmp_db_item_fc)g_db_move_cmp;

    item->unpack = (unpack_db_item_fc)g_db_move_unpack;
    item->pack = (pack_db_item_fc)g_db_move_pack;

    item->build_label = (build_item_label_fc)g_db_move_build_label;
    item->apply = (run_item_fc)g_db_move_apply;
    item->cancel = (run_item_fc)g_db_move_cancel;

    item->load = (load_db_item_fc)g_db_move_load;
    item->store = (store_db_item_fc)g_db_move_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : move = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise un déplacement au sein de code.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_move_init(GDbMove *move)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : move = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_move_dispose(GDbMove *move)
{
    g_object_unref(G_OBJECT(move->src));
    g_object_unref(G_OBJECT(move->dest));

    G_OBJECT_CLASS(g_db_move_parent_class)->dispose(G_OBJECT(move));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : move = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_move_finalize(GDbMove *move)
{
    G_OBJECT_CLASS(g_db_move_parent_class)->finalize(G_OBJECT(move));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : src  = emplacement de départ d'un mouvement.                 *
*                dest = emplacement d'arrivée du même mouvement.              *
*                                                                             *
*  Description : Organise un déplacement d'une position à une autre.          *
*                                                                             *
*  Retour      : Déplacement mis en place ou NULL en cas d'erreur.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDbMove *g_db_move_new(const GLineCursor *src, const GLineCursor *dest)
{
    GDbMove *result;                        /* Instance à retourner        */

    result = g_object_new(G_TYPE_DB_MOVE, NULL);

    result->src = g_line_cursor_duplicate(src);
    result->dest = g_line_cursor_duplicate(dest);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = premier élément à analyser.                              *
*                b = second élément à analyser.                               *
*                                                                             *
*  Description : Effectue la comparaison entre deux changements de position.  *
*                                                                             *
*  Retour      : Bilan de la comparaison : -1, 0 ou 1.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gint g_db_move_cmp(const GDbMove *a, const GDbMove *b)
{
    gint result;                            /* Bilan de la comparaison     */

    result = g_line_cursor_compare(a->src, b->src);

    if (result == 0)
        result = g_line_cursor_compare(a->dest, b->dest);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : move = bascule d'affichage aux infos à charger. [OUT]        *
*                pbuf = paquet de données où venir inscrire les infos.        *
*                                                                             *
*  Description : Importe la définition d'un déplacement depuis un flux réseau.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_db_move_unpack(GDbMove *move, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    result = G_DB_ITEM_CLASS(g_db_move_parent_class)->unpack(G_DB_ITEM(move), pbuf);

    move->src = g_binary_cursor_new();
    move->dest = g_binary_cursor_new();

    if (result)
        result = g_line_cursor_unserialize(move->src, pbuf);

    if (result)
        result = g_line_cursor_unserialize(move->dest, pbuf);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : move = bascule d'affichage aux infos à sauvegarder.          *
*                pbuf = paquet de données où venir inscrire les infos.        *
*                                                                             *
*  Description : Exporte la définition d'un déplacement dans un flux réseau.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_db_move_pack(const GDbMove *move, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    result = G_DB_ITEM_CLASS(g_db_move_parent_class)->pack(G_DB_ITEM(move), pbuf);

    if (result)
        result = g_line_cursor_serialize(move->src, pbuf);

    if (result)
        result = g_line_cursor_serialize(move->dest, pbuf);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : move = informations de déplacement à manipuler.              *
*                                                                             *
*  Description : Construit la description humaine d'un déplacement.           *
*                                                                             *
*  Retour      : Chaîne de caractère correspondante.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_db_move_build_label(GDbMove *move)
{
#if 0
    char *src_label;                        /* Indication de position #1   */
    char *dest_label;                       /* Indication de position #2   */

    src_label = g_line_cursor_build_label(move->src);
    dest_label = g_line_cursor_build_label(move->dest);

    asprintf(&G_DB_ITEM(move)->label, _("Move from %s to %s"), src_label, dest_label);

    free(src_label);
    free(dest_label);
#endif
    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : move   = informations de déplacement à consulter.            *
*                cursor = localisation à placer bien en évidence.             *
*                                                                             *
*  Description : Exécute un déplacement dans une zone de code.                *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_db_move_run(const GDbMove *move, GLineCursor *cursor)
{
#ifdef INCLUDE_GTK_SUPPORT

    GLoadedPanel *panel;                    /* Afficheur effectif de code  */

    typedef struct _move_params
    {
        GLoadedPanel *panel;                /* Afficheur effectif de code  */
        GLineCursor *cursor;                /* Emplacement à rejoindre     */

    } move_params;

    move_params *params;                    /* Paramètres à transmettre    */

    /* Procédure de nettoyage */

    void delete_move_params(move_params *p)
    {
        g_object_unref(G_OBJECT(p->panel));
        g_object_unref(G_OBJECT(p->cursor));

        free(p);

    }

    /* Procédure d'application différée */

    gboolean do_move_in_main_loop(move_params *p)
    {
        g_loaded_panel_scroll_to_cursor(p->panel, p->cursor, SPT_CENTER, true);

        return G_SOURCE_REMOVE;

    }

    /* Lancement de l'opération */

    panel = get_current_view();

    if (G_IS_LOADED_PANEL(panel))
    {
        params = calloc(1, sizeof(move_params));

        params->panel = panel;
        params->cursor = cursor;

        g_object_ref(G_OBJECT(params->panel));
        g_object_ref(G_OBJECT(params->cursor));

        g_idle_add_full(G_PRIORITY_DEFAULT_IDLE,
                        (GSourceFunc)do_move_in_main_loop,
                        params, (GDestroyNotify)delete_move_params);

    }

    if (panel != NULL)
        g_object_unref(G_OBJECT(panel));

#endif

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : move   = bascule d'affichage à manipuler.                    *
*                binary = binaire de rattachement chargé en mémoire.          *
*                                                                             *
*  Description : Applique un déplacement au sein d'une zone de code.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_db_move_apply(GDbMove *move, GLoadedBinary *binary)
{
    bool result;                            /* Bilan à faire remonter      */

    result = g_db_move_run(move, move->dest);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : move   = informations de déplacement à consulter.            *
*                binary = binaire chargé en mémoire à modifier.               *
*                                                                             *
*  Description : Annule un déplacement au sein d'une zone de code.            *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_db_move_cancel(GDbMove *move, GLoadedBinary *binary)
{
    bool result;                            /* Bilan à faire remonter      */

    result = g_db_move_run(move, move->src);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : move   = bascule d'affichage à charger depuis les réponses.  *
*                values = tableau d'éléments à consulter.                     *
*                count  = nombre de descriptions renseignées.                 *
*                                                                             *
*  Description : Charge les valeurs utiles pour un déplacement dans du code.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_db_move_load(GDbMove *move, const bound_value *values, size_t count)
{
    bool result;                            /* Bilan à faire remonter      */

    result = G_DB_ITEM_CLASS(g_db_move_parent_class)->load(G_DB_ITEM(move), values, count);

    if (result)
        result = g_line_cursor_load(move->src, "src", values, count);

    if (result)
        result = g_line_cursor_load(move->dest, "dest", values, count);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : move   = base d'éléments sur laquelle s'appuyer.             *
*                values = couples de champs et de valeurs à lier. [OUT]       *
*                count  = nombre de ces couples. [OUT]                        *
*                                                                             *
*  Description : Constitue les champs destinés à une insertion / modification.*
*                                                                             *
*  Retour      : Etat du besoin en sauvegarde.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_db_move_store(const GDbMove *move, bound_value **values, size_t *count)
{
    bool status;                            /* Bilan d'opération initiale  */

    if (move == NULL)
        status = G_DB_ITEM_CLASS(g_db_move_parent_class)->store(NULL, values, count);
    else
        status = G_DB_ITEM_CLASS(g_db_move_parent_class)->store(G_DB_ITEM(move), values, count);

    if (!status) return false;

    if (move == NULL)
        status = g_line_cursor_setup_load(move->src, "src", values, count);
    else
        status = g_line_cursor_store(move->src, "src", values, count);

    if (!status) return false;

    if (move == NULL)
        status = g_line_cursor_setup_load(move->dest, "dest", values, count);
    else
        status = g_line_cursor_store(move->dest, "dest", values, count);

    if (!status) return false;

    return true;

}



/* ---------------------------------------------------------------------------------- */
/*                        DEFINITION DE LA COLLECTION ASSOCIEE                        */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une collection de déplacements dans du code. */
G_DEFINE_TYPE(GMoveCollection, g_move_collection, G_TYPE_DB_COLLECTION);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des collections de déplacements.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_move_collection_class_init(GMoveCollectionClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDbCollectionClass *collec;             /* Encore une autre vision...  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_move_collection_dispose;
    object->finalize = (GObjectFinalizeFunc)g_move_collection_finalize;

    collec = G_DB_COLLECTION_CLASS(klass);

    collec->create_table = (collec_create_db_table_fc)g_move_collection_create_db_table;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une collection de déplacements.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_move_collection_init(GMoveCollection *collec)
{
    G_DB_COLLECTION(collec)->featuring = DBF_MOVES;
    G_DB_COLLECTION(collec)->type = G_TYPE_DB_MOVE;
    G_DB_COLLECTION(collec)->name = "Moves";

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

static void g_move_collection_dispose(GMoveCollection *collec)
{
    G_OBJECT_CLASS(g_move_collection_parent_class)->dispose(G_OBJECT(collec));

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

static void g_move_collection_finalize(GMoveCollection *collec)
{
    G_OBJECT_CLASS(g_move_collection_parent_class)->finalize(G_OBJECT(collec));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée une collection dédiée aux déplacements dans du code.    *
*                                                                             *
*  Retour      : Collection mise en place.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GMoveCollection *g_move_collection_new(void)
{
    GMoveCollection *result;            /* Instance à retourner        */

    result = g_object_new(G_TYPE_MOVE_COLLECTION, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = ensemble d'éléments spectateur des opérations.      *
*                db     = accès à la base de données.                         *
*                                                                             *
*  Description : Crée la table des basculements dans une base de données.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_move_collection_create_db_table(const GMoveCollection *collec, sqlite3 *db)
{
    const char *sql;                        /* Patron de requête SQL       */
    char *src_fields;                       /* Champs pour la source       */
    char *dest_fields;                      /* Champs pour la destination  */
    char *request;                          /* Requête à exécuter          */
    char *msg;                              /* Message d'erreur            */
    int ret;                                /* Bilan de la création        */

    sql = "CREATE TABLE Moves ("            \
             SQLITE_DB_ITEM_CREATE ", "     \
             "%s, "                         \
             "%s"                           \
          ");";

    src_fields = g_binary_cursor_create_db_table("src");
    dest_fields = g_binary_cursor_create_db_table("dest");

    asprintf(&request, sql, src_fields, dest_fields);

    ret = sqlite3_exec(db, request, NULL, NULL, &msg);

    free(src_fields);
    free(dest_fields);
    free(request);

    if (ret != SQLITE_OK)
    {
        fprintf(stderr, "sqlite3_exec(): %s\n", msg);
        sqlite3_free(msg);
    }

    return (ret == SQLITE_OK);

}
