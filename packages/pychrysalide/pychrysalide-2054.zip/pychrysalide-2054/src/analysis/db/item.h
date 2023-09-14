
/* Chrysalide - Outil d'analyse de fichiers binaires
 * item.h - prototypes pour la gestion d'éléments destinés à une collection générique
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


#ifndef _ANALYSIS_DB_ITEM_H
#define _ANALYSIS_DB_ITEM_H


#include <glib-object.h>
#include <stdbool.h>


#include "protocol.h"
#include "misc/timestamp.h"
#include "../../common/packed.h"
#include "../../common/sqlite.h"



/* Depuis ../binary.h : description de fichier binaire (instance) */
typedef struct _GLoadedBinary GLoadedBinary;


/* Propriétés particulières pour un élément */
typedef enum _DbItemFlags
{
    DIF_NONE     = (0 << 0),                /* Propriétés par défaut       */
    DIF_ERASER   = (1 << 0),                /* Suppression de l'effet      */
    DIF_UPDATED  = (1 << 1),                /* Mise à jour de l'élément    */
    DIF_VOLATILE = (1 << 2),                /* Abscence de sauvegarde      */
    DIF_BROKEN   = (1 << 3),                /* Application impossible      */
    DIF_DISABLED = (1 << 4),                /* Désactivation forcée        */

} DbItemFlags;


#define G_TYPE_DB_ITEM            g_db_item_get_type()
#define G_DB_ITEM(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_DB_ITEM, GDbItem))
#define G_IS_DB_ITEM(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_DB_ITEM))
#define G_DB_ITEM_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DB_ITEM, GDbItemClass))
#define G_IS_DB_ITEM_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DB_ITEM))
#define G_DB_ITEM_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DB_ITEM, GDbItemClass))


/* Base d'un élément pour collection générique (instance) */
typedef struct _GDbItem GDbItem;

/* Base d'un élément pour collection générique (classe) */
typedef struct _GDbItemClass GDbItemClass;


/* Indique le type défini pour une base d'élément de collection générique. */
GType g_db_item_get_type(void);

/* Indique la fonctionnalité représentée par l'élément. */
DBFeatures g_db_item_get_feature(const GDbItem *);

/* Indique à l'élément qu'il se trouve du côté serveur. */
void g_db_item_set_server_side(GDbItem *);

/* Calcule le condensat associé à l'élément vu comme clef. */
guint g_db_item_hash_key(const GDbItem *);

/* Compare deux éléments en tant que clefs. */
gboolean g_db_item_cmp_key(const GDbItem *, const GDbItem *);

/* Effectue la comparaison entre deux éléments de collection. */
int g_db_item_cmp_timestamp(const GDbItem **, const GDbItem **);

/* Effectue la comparaison entre un élément et un horodatage. */
int g_db_item_cmp_with_timestamp(const timestamp_t *, const GDbItem **);

/* Effectue la comparaison entre deux éléments de collection. */
gint g_db_item_cmp(const GDbItem *, const GDbItem *);

/* Importe la définition d'une base d'éléments pour collection. */
bool g_db_item_unpack(GDbItem *, packed_buffer_t *);

/* Exporte la définition d'une base d'éléments pour collection. */
bool g_db_item_pack(const GDbItem *, packed_buffer_t *);

/* Applique un élément de collection sur un binaire. */
bool g_db_item_apply(GDbItem *, GLoadedBinary *);

/* Annule une bascule d'affichage d'opérande sur un binaire. */
bool g_db_item_cancel(GDbItem *, GLoadedBinary *);

/* Décrit l'élément de collection en place. */
char *g_db_item_get_label(const GDbItem *);

/* Fournit l'horodatage associé à l'élément de collection. */
timestamp_t g_db_item_get_timestamp(const GDbItem *);

/* Applique un ensemble de propriétés à un élément. */
void g_db_item_set_flags(GDbItem *, DbItemFlags);

/* Ajoute une propriété à un élément de base de données. */
void g_db_item_add_flag(GDbItem *, DbItemFlags);

/* Retire une propriété à un élément de base de données. */
void g_db_item_remove_flag(GDbItem *, DbItemFlags);

/* Indique les propriétés particulières appliquées à l'élément. */
DbItemFlags g_db_item_get_flags(const GDbItem *);

#define g_db_item_has_flag(i, f) \
    (g_db_item_get_flags(i) & f)



/* --------------------- MANIPULATIONS AVEC UNE BASE DE DONNEES --------------------- */


/* Décrit les colonnes utiles à un chargement de données. */
bool g_db_item_setup_load(const GDbItem *, bound_value **, size_t *);

/* Charge les valeurs utiles pour un élément de collection. */
bool g_db_item_load(GDbItem *, const bound_value *, size_t);

/* Constitue les champs destinés à une insertion / modification. */
bool g_db_item_store(const GDbItem *, bound_value **, size_t *);



#endif  /* _ANALYSIS_DB_ITEM_H */
