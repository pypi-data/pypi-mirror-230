
/* Chrysalide - Outil d'analyse de fichiers binaires
 * group.h - prototypes pour la conservation d'un groupe de correspondance avec du binaire
 *
 * Copyright (C) 2023 Cyrille Bagard
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


#ifndef _PLUGINS_KAITAI_RECORDS_GROUP_H
#define _PLUGINS_KAITAI_RECORDS_GROUP_H


#include <glib-object.h>


#include <analysis/content.h>


#include "../record.h"
#include "../parsers/struct.h"



#define G_TYPE_RECORD_GROUP            g_record_group_get_type()
#define G_RECORD_GROUP(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_RECORD_GROUP, GRecordGroup))
#define G_IS_RECORD_GROUP(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_RECORD_GROUP))
#define G_RECORD_GROUP_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_RECORD_GROUP, GRecordGroupClass))
#define G_IS_RECORD_GROUP_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_RECORD_GROUP))
#define G_RECORD_GROUP_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_RECORD_GROUP, GRecordGroupClass))


/* Groupe de correspondances établies entre attributs et binaire (instance) */
typedef struct _GRecordGroup GRecordGroup;

/* Groupe de correspondances établies entre attributs et binaire (classe) */
typedef struct _GRecordGroupClass GRecordGroupClass;


/* Indique le type défini pour une série de correspondances entre attributes et binaire. */
GType g_record_group_get_type(void);

/* Crée une nouvelle série de correspondances attribut/binaire. */
GRecordGroup *g_record_group_new(GKaitaiStruct *, GBinContent *);

/* Ajoute une correspondance supplémentaire à une série. */
void g_record_group_add_record(GRecordGroup *, GMatchRecord *);



#endif  /* _PLUGINS_KAITAI_RECORDS_GROUP_H */
