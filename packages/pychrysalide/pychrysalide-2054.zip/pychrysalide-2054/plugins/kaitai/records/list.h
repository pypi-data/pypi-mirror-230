
/* Chrysalide - Outil d'analyse de fichiers binaires
 * list.h - prototypes pour la conservation d'une liste de correspondance avec du binaire
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


#ifndef _PLUGINS_KAITAI_RECORDS_LIST_H
#define _PLUGINS_KAITAI_RECORDS_LIST_H


#include <glib-object.h>


#include <analysis/content.h>


#include "../record.h"
#include "../parsers/attribute.h"



#define G_TYPE_RECORD_LIST            g_record_list_get_type()
#define G_RECORD_LIST(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_RECORD_LIST, GRecordList))
#define G_IS_RECORD_LIST(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_RECORD_LIST))
#define G_RECORD_LIST_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_RECORD_LIST, GRecordListClass))
#define G_IS_RECORD_LIST_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_RECORD_LIST))
#define G_RECORD_LIST_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_RECORD_LIST, GRecordListClass))


/* Liste de correspondances établies entre attributs et binaire (instance) */
typedef struct _GRecordList GRecordList;

/* Liste de correspondances établies entre attributs et binaire (classe) */
typedef struct _GRecordListClass GRecordListClass;


/* Indique le type défini pour une série de correspondances entre attributes et binaire. */
GType g_record_list_get_type(void);

/* Crée une nouvelle série de correspondances attribut/binaire. */
GRecordList *g_record_list_new(GKaitaiAttribute *, GBinContent *, const vmpa2t *);

/* Dénombre le nombre de correspondances enregistrées. */
size_t g_record_list_count_records(const GRecordList *);

/* Ajoute une correspondance supplémentaire à une série. */
void g_record_list_add_record(GRecordList *, GMatchRecord *);

/* Fournit un élément ciblé dans la liste de correspondances. */
GMatchRecord *g_record_list_get_record(const GRecordList *, size_t);



#endif  /* _PLUGINS_KAITAI_RECORDS_LIST_H */
