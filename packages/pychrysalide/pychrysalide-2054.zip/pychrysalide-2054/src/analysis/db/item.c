
/* Chrysalide - Outil d'analyse de fichiers binaires
 * item.c - gestion d'éléments destinés à une collection générique
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


#include "item.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>
#include <sqlite3.h>


#include "item-int.h"
#include "../../common/sort.h"
#include "../../core/params.h"



/* Initialise la classe des bases d'éléments pour collection. */
static void g_db_item_class_init(GDbItemClass *);

/* Initialise une base d'élément pour collection générique. */
static void g_db_item_init(GDbItem *);

/* Supprime toutes les références externes. */
static void g_db_item_dispose(GDbItem *);

/* Procède à la libération totale de la mémoire. */
static void g_db_item_finalize(GDbItem *);

/* Importe la définition d'une base d'éléments pour collection. */
static bool _g_db_item_unpack(GDbItem *, packed_buffer_t *);

/* Exporte la définition d'une base d'éléments pour collection. */
static bool _g_db_item_pack(const GDbItem *, packed_buffer_t *);



/* --------------------- MANIPULATIONS AVEC UNE BASE DE DONNEES --------------------- */


/* Charge les valeurs utiles pour un élément de collection. */
static bool _g_db_item_load(GDbItem *, const bound_value *, size_t);

/* Constitue les champs destinés à une insertion / modification. */
static bool _g_db_item_store(const GDbItem *, bound_value **, size_t *);



/* Indique le type défini pour une base d'élément de collection générique. */
G_DEFINE_TYPE(GDbItem, g_db_item, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des bases d'éléments pour collection.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_item_class_init(GDbItemClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_db_item_dispose;
    object->finalize = (GObjectFinalizeFunc)g_db_item_finalize;

    klass->cmp = (cmp_db_item_fc)g_db_item_cmp;

    klass->unpack = (unpack_db_item_fc)_g_db_item_unpack;
    klass->pack = (pack_db_item_fc)_g_db_item_pack;

    klass->load = (load_db_item_fc)_g_db_item_load;
    klass->store = (store_db_item_fc)_g_db_item_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une base d'élément pour collection générique.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_item_init(GDbItem *item)
{
    item->index = 0;

    set_static_rle_string(&item->author, "");

    g_atomic_int_set(&item->atomic_flags, DIF_NONE);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_item_dispose(GDbItem *item)
{
    G_OBJECT_CLASS(g_db_item_parent_class)->dispose(G_OBJECT(item));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_item_finalize(GDbItem *item)
{
    exit_rle_string(&item->author);

    G_OBJECT_CLASS(g_db_item_parent_class)->finalize(G_OBJECT(item));

}



/******************************************************************************
*                                                                             *
*  Paramètres  : item = élément de collection à consulter.                    *
*                                                                             *
*  Description : Indique la fonctionnalité représentée par l'élément.         *
*                                                                             *
*  Retour      : Identifiant valide pour le protocole.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

DBFeatures g_db_item_get_feature(const GDbItem *item)
{
    return G_DB_ITEM_GET_CLASS(item)->feature;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = élément de collection à traiter.                      *
*                                                                             *
*  Description : Indique à l'élément qu'il se trouve du côté serveur.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_db_item_set_server_side(GDbItem *item)
{
#ifndef NDEBUG
    bool status;                            /* Bilan d'une initialisation  */
#endif

#ifndef NDEBUG
    status = init_timestamp(&item->created);
    assert(status);
#else
    init_timestamp(&item->created);
#endif

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = élément de collection à consulter.                    *
*                                                                             *
*  Description : Calcule le condensat associé à l'élément vu comme clef.      *
*                                                                             *
*  Retour      : Condensat associé à l'élément.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

guint g_db_item_hash_key(const GDbItem *item)
{
    guint result;                           /* Valeur "unique" à renvoyer  */
    GDbItemClass *class;                    /* Classe liée à l'instance    */

    class = G_DB_ITEM_GET_CLASS(item);

    result = class->hash_key(item);

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

gboolean g_db_item_cmp_key(const GDbItem *a, const GDbItem *b)
{
    gboolean result;                        /* Bilan à retourner           */
    GDbItemClass *class;                    /* Classe liée à l'instance    */

    class = G_DB_ITEM_GET_CLASS(a);

    result = class->cmp_key(a, b);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = premier élément à analyser.                              *
*                b = second élément à analyser.                               *
*                                                                             *
*  Description : Effectue la comparaison entre deux éléments de collection.   *
*                                                                             *
*  Retour      : Bilan de la comparaison : -1, 0 ou 1.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int g_db_item_cmp_timestamp(const GDbItem **a, const GDbItem **b)
{
    int result;                             /* Bilan à retourner           */

    result = cmp_timestamp(&(*a)->created, &(*b)->created);

    if (result == 0)
        result = sort_unsigned_long((*a)->index, (*b)->index);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ts = premier élément à analyser.                             *
*                b  = second élément à analyser.                              *
*                                                                             *
*  Description : Effectue la comparaison entre un élément et un horodatage.   *
*                                                                             *
*  Retour      : Bilan de la comparaison : -1, 0 ou 1.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int g_db_item_cmp_with_timestamp(const timestamp_t *ts, const GDbItem **b)
{
    int result;                             /* Bilan à retourner           */

    result = cmp_timestamp(ts, &(*b)->created);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = premier élément à analyser.                              *
*                b = second élément à analyser.                               *
*                                                                             *
*  Description : Effectue la comparaison entre deux éléments de collection.   *
*                                                                             *
*  Retour      : Bilan de la comparaison : -1, 0 ou 1.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

gint g_db_item_cmp(const GDbItem *a, const GDbItem *b)
{
    gint result;                            /* Bilan à retourner           */
    GDbItemClass *class;                    /* Classe liée à l'instance    */
    char *label_a;                          /* Etiquette de l'élément A    */
    char *label_b;                          /* Etiquette de l'élément B    */

    result = g_db_item_cmp_timestamp(&a, &b);

    if (result == 0)
    {
        class = G_DB_ITEM_GET_CLASS(a);
        result = class->cmp(a, b);
    }

    if (result == 0)
    {
        label_a = g_db_item_get_label(a);
        label_b = g_db_item_get_label(b);

        result = strcmp(label_a, label_b);

        free(label_a);
        free(label_b);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = base d'éléments à charger. [OUT]                      *
*                pbuf = paquet de données où venir puiser les infos.          *
*                                                                             *
*  Description : Importe la définition d'une base d'éléments pour collection. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool _g_db_item_unpack(GDbItem *item, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    uint32_t flags;                         /* Propriétés de l'élément     */

    result = unpack_timestamp(&item->created, pbuf);

    if (result)
        result = unpack_rle_string(&item->author, pbuf);

    if (result)
    {
        result = extract_packed_buffer(pbuf, &flags, sizeof(uint32_t), true);
        g_db_item_set_flags(item, flags);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = base d'éléments à charger. [OUT]                      *
*                pbuf = paquet de données où venir puiser les infos.          *
*                                                                             *
*  Description : Importe la définition d'une base d'éléments pour collection. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_db_item_unpack(GDbItem *item, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    result = G_DB_ITEM_GET_CLASS(item)->unpack(item, pbuf);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = informations à sauvegarder.                           *
*                pbuf = paquet de données où venir inscrire les infos.        *
*                                                                             *
*  Description : Exporte la définition d'une base d'éléments pour collection. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool _g_db_item_pack(const GDbItem *item, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    DbItemFlags flags;                      /* Propriétés de l'élément     */

    result = pack_timestamp(&item->created, pbuf);

    if (result)
        result = pack_rle_string(&item->author, pbuf);

    if (result)
    {
        flags = g_db_item_get_flags(item);
        result = extend_packed_buffer(pbuf, (uint32_t []) { flags }, sizeof(uint32_t), true);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = informations à sauvegarder.                           *
*                pbuf = paquet de données où venir inscrire les infos.        *
*                                                                             *
*  Description : Exporte la définition d'une base d'éléments pour collection. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_db_item_pack(const GDbItem *item, packed_buffer_t *pbuf)
{
    return G_DB_ITEM_GET_CLASS(item)->pack(item, pbuf);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item   = élément de collection à manipuler.                  *
*                binary = binaire chargé en mémoire à modifier.               *
*                                                                             *
*  Description : Applique un élément de collection sur un binaire.            *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_db_item_apply(GDbItem *item, GLoadedBinary *binary)
{
    bool result;                            /* Bilan à faire remonter      */

    assert(!g_db_item_has_flag(item, DIF_DISABLED));

    result = G_DB_ITEM_GET_CLASS(item)->apply(item, binary);

    if (!result)
        g_db_item_add_flag(item, DIF_BROKEN);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item   = élément de collection à manipuler.                  *
*                binary = binaire chargé en mémoire à modifier.               *
*                                                                             *
*  Description : Annule une bascule d'affichage d'opérande sur un binaire.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_db_item_cancel(GDbItem *item, GLoadedBinary *binary)
{
    bool result;                            /* Bilan à faire remonter      */

    assert(g_db_item_has_flag(item, DIF_DISABLED));

    result = G_DB_ITEM_GET_CLASS(item)->cancel(item, binary);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = élément de collection à consulter.                    *
*                                                                             *
*  Description : Décrit l'élément de collection en place.                     *
*                                                                             *
*  Retour      : Description humaine mise en place à libérer après usage.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_db_item_get_label(const GDbItem *item)
{
    char *result;                           /* Description à retourner     */
    GDbItemClass *class;                    /* Classe de l'instance        */

    class = G_DB_ITEM_GET_CLASS(item);

    result = class->build_label(item);
    assert(result != NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = élément de collection à consulter.                    *
*                                                                             *
*  Description : Fournit l'horodatage associé à l'élément de collection.      *
*                                                                             *
*  Retour      : Date de création de l'élément.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

timestamp_t g_db_item_get_timestamp(const GDbItem *item)
{
    timestamp_t result;                     /* Horodatage à retourner      */

    result = item->created;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = base d'éléments à mettre à jour.                      *
*                flag = type de propriété à traiter.                          *
*                                                                             *
*  Description : Applique un ensemble de propriétés à un élément.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_db_item_set_flags(GDbItem *item, DbItemFlags flag)
{
    g_atomic_int_set(&item->atomic_flags, flag);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = base d'éléments à mettre à jour.                      *
*                flag = type de propriété à traiter.                          *
*                                                                             *
*  Description : Ajoute une propriété à un élément de base de données.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_db_item_add_flag(GDbItem *item, DbItemFlags flag)
{
    g_atomic_int_add(&item->atomic_flags, flag);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = base d'éléments à mettre à jour.                      *
*                flag = type de propriété à traiter.                          *
*                                                                             *
*  Description : Retire une propriété à un élément de base de données.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_db_item_remove_flag(GDbItem *item, DbItemFlags flag)
{
    gint mask;                              /* Masque à appliquer          */

    mask = flag;
    mask = ~mask;

    g_atomic_int_and(&item->atomic_flags, mask);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = base d'éléments à consulter.                          *
*                                                                             *
*  Description : Indique les propriétés particulières appliquées à l'élément. *
*                                                                             *
*  Retour      : Propriétés actives de l'élément.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

DbItemFlags g_db_item_get_flags(const GDbItem *item)
{
    DbItemFlags result;                     /* Fanions à retourner         */

    result = g_atomic_int_get(&item->atomic_flags);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       MANIPULATIONS AVEC UNE BASE DE DONNEES                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : item   = base d'éléments à consulter.                        *
*                values = tableau d'éléments à compléter. [OUT]               *
*                count  = nombre de descriptions renseignées. [OUT]           *
*                                                                             *
*  Description : Décrit les colonnes utiles à un chargement de données.       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_db_item_setup_load(const GDbItem *item, bound_value **values, size_t *count)
{
    *values = NULL;
    *count = 0;

    return G_DB_ITEM_GET_CLASS(item)->store(NULL, values, count);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item   = base d'éléments à charger depuis les réponses.      *
*                values = tableau d'éléments à consulter.                     *
*                count  = nombre de descriptions renseignées.                 *
*                                                                             *
*  Description : Charge les valeurs utiles pour un élément de collection.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool _g_db_item_load(GDbItem *item, const bound_value *values, size_t count)
{
    bool result;                            /* Bilan global à retourner    */
    const bound_value *value;               /* Valeur à intégrer           */

    result = load_timestamp(&item->created, "created", values, count);

    if (result)
        result = load_rle_string(&item->author, "author", values, count);

    if (result)
    {
        value = find_bound_value(values, count, "flags");

        result = (value != NULL && value->type == SQLITE_INTEGER);

        if (result)
            item->flags = value->integer;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item   = base d'éléments à charger depuis les réponses.      *
*                values = tableau d'éléments à consulter.                     *
*                count  = nombre de descriptions renseignées.                 *
*                                                                             *
*  Description : Charge les valeurs utiles pour un élément de collection.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_db_item_load(GDbItem *item, const bound_value *values, size_t count)
{
    bool result;                            /* Bilan à retourner           */

    result = G_DB_ITEM_GET_CLASS(item)->load(item, values, count);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item   = base d'éléments sur laquelle s'appuyer.             *
*                values = couples de champs et de valeurs à lier. [OUT]       *
*                count  = nombre de ces couples. [OUT]                        *
*                                                                             *
*  Description : Constitue les champs destinés à une insertion / modification.*
*                                                                             *
*  Retour      : Bilan de l'opération : succès ou non.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool _g_db_item_store(const GDbItem *item, bound_value **values, size_t *count)
{
    bool result;                            /* Bilan à retourner           */
    bound_value *value;                     /* Valeur à éditer / définir   */

    if (item == NULL)
        result = store_timestamp(NULL, "created", values, count);
    else
        result = store_timestamp(&item->created, "created", values, count);

    if (result)
    {
        if (item == NULL)
            result = store_rle_string(NULL, "author", values, count);
        else
            result = store_rle_string(&item->author, "author", values, count);
    }

    if (result)
    {
        *values = realloc(*values, ++(*count) * sizeof(bound_value));

        value = &(*values)[*count - 1];

        value->cname = "flags";
        value->built_name = false;
        value->type = SQLITE_INTEGER;

        value->has_value = (item != NULL);

        if (value->has_value)
            value->integer = g_db_item_get_flags(item);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item   = base d'éléments sur laquelle s'appuyer.             *
*                values = couples de champs et de valeurs à lier. [OUT]       *
*                count  = nombre de ces couples. [OUT]                        *
*                                                                             *
*  Description : Constitue les champs destinés à une insertion / modification.*
*                                                                             *
*  Retour      : Bilan de l'opération : succès ou non.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_db_item_store(const GDbItem *item, bound_value **values, size_t *count)
{
    *values = NULL;
    *count = 0;

    return G_DB_ITEM_GET_CLASS(item)->store(item, values, count);

}
