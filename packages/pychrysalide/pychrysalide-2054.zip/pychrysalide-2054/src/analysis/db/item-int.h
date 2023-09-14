
/* Chrysalide - Outil d'analyse de fichiers binaires
 * item-int.h - prototypes et définitions internes pour les bases d'éléments de collection
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


#ifndef _ANALYSIS_DB_ITEM_INT_H
#define _ANALYSIS_DB_ITEM_INT_H


#include "item.h"


#include <stdint.h>


#include "misc/rlestr.h"
#include "../binary.h"



/* Calcule le condensat associé à l'élément vu comme clef. */
typedef guint (* hash_db_item_key_fc) (const GDbItem *);

/* Compare deux éléments en tant que clefs. */
typedef gboolean (* cmp_db_item_key_fc) (const GDbItem *, const GDbItem *);

/* Effectue la comparaison entre deux éléments de collection. */
typedef gint (* cmp_db_item_fc) (const GDbItem *, const GDbItem *);

/* Importe la définition d'une base d'éléments pour collection. */
typedef bool (* unpack_db_item_fc) (GDbItem *, packed_buffer_t *);

/* Exporte la définition d'une base d'éléments pour collection. */
typedef bool (* pack_db_item_fc) (const GDbItem *, packed_buffer_t *);

/* Construit la description humaine d'un signet sur un tampon. */
typedef char * (* build_item_label_fc) (const GDbItem *);

/* Exécute un élément de collection sur un binaire. */
typedef bool (* run_item_fc) (GDbItem *, GLoadedBinary *);

/* Charge les valeurs utiles pour une localisation. */
typedef bool (* load_db_item_fc) (GDbItem *, const bound_value *, size_t);

/* Constitue les champs destinés à une insertion / modification. */
typedef bool (* store_db_item_fc) (const GDbItem *, bound_value **, size_t *);


/* Base d'un élément pour collection générique (instance) */
struct _GDbItem
{
    GObject parent;                         /* A laisser en premier        */

    timestamp_t created;                    /* Date de création            */
    unsigned long index;                    /* Indice au sein d'un groupe  */

    rle_string author;                      /* Utilisateur d'origine       */

    union
    {
        DbItemFlags flags;                  /* Propriétés de l'élément     */
        gint atomic_flags;                  /* Accès atomique              */

    };

};

/* Base d'un élément pour collection générique (classe) */
struct _GDbItemClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    DBFeatures feature;                     /* Fonctionnalité représentée  */

    hash_db_item_key_fc hash_key;           /* Condensat de l'élément      */
    cmp_db_item_key_fc cmp_key;             /* Comparaison en tant que clef*/
    cmp_db_item_fc cmp;                     /* Comparaison entre éléments  */

    unpack_db_item_fc unpack;               /* Réception depuis le réseau  */
    pack_db_item_fc pack;                   /* Emission depuis le réseau   */

    build_item_label_fc build_label;        /* Construction de description */
    run_item_fc apply;                      /* Application de l'élément    */
    run_item_fc cancel;                     /* Retrait de l'élément        */

    load_db_item_fc load;                   /* Chargement à partir d'une BD*/
    store_db_item_fc store;                 /* Préparation d'une requête   */

};


/* Définition du tronc commun pour les créations SQLite */
#define SQLITE_DB_ITEM_CREATE                   \
    SQLITE_TIMESTAMP_CREATE("created") ", "     \
    SQLITE_RLESTR_CREATE("author") ", "         \
    "flags INTEGER"



#endif  /* _ANALYSIS_DB_ITEM_INT_H */
