
/* Chrysalide - Outil d'analyse de fichiers binaires
 * item.h - prototypes pour la conservation d'une correspondance entre attribut et binaire
 *
 * Copyright (C) 2019 Cyrille Bagard
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


#ifndef _PLUGINS_KAITAI_RECORDS_ITEM_H
#define _PLUGINS_KAITAI_RECORDS_ITEM_H


#include <glib-object.h>


#include "../record.h"
#include "../parsers/attribute.h"



#define G_TYPE_RECORD_ITEM            g_record_item_get_type()
#define G_RECORD_ITEM(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_RECORD_ITEM, GRecordItem))
#define G_IS_RECORD_ITEM(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_RECORD_ITEM))
#define G_RECORD_ITEM_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_RECORD_ITEM, GRecordItemClass))
#define G_IS_RECORD_ITEM_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_RECORD_ITEM))
#define G_RECORD_ITEM_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_RECORD_ITEM, GRecordItemClass))


/* Correspondance établie entre un attribut et du binaire (instance) */
typedef struct _GRecordItem GRecordItem;

/* Correspondance établie entre un attribut et du binaire (classe) */
typedef struct _GRecordItemClass GRecordItemClass;


/* Indique le type défini pour une correspondance entre un attribut et du binaire. */
GType g_record_item_get_type(void);

/* Crée une nouvelle correspondance entre attribut et binaire. */
GRecordItem *g_record_item_new(GKaitaiAttribute *, GBinContent *, const mrange_t *, SourceEndian);

/* Lit la série d'octets d'un élément Kaitai entier représenté. */
bool g_record_item_get_truncated_bytes(const GRecordItem *, bin_t **, size_t *);

/* Lit la valeur d'un élément Kaitai entier représenté. */
bool g_record_item_get_value(const GRecordItem *, resolved_value_t *);



#endif  /* _PLUGINS_KAITAI_RECORDS_ITEM_H */
