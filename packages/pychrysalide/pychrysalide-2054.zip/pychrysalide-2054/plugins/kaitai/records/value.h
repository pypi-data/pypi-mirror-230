
/* Chrysalide - Outil d'analyse de fichiers binaires
 * value.h - prototypes pour la conservation d'une correspondance entre attribut et binaire
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


#ifndef _PLUGINS_KAITAI_RECORDS_VALUE_H
#define _PLUGINS_KAITAI_RECORDS_VALUE_H


#include <glib-object.h>


#include "../record.h"
#include "../parsers/instance.h"



#define G_TYPE_RECORD_VALUE            g_record_value_get_type()
#define G_RECORD_VALUE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_RECORD_VALUE, GRecordValue))
#define G_IS_RECORD_VALUE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_RECORD_VALUE))
#define G_RECORD_VALUE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_RECORD_VALUE, GRecordValueClass))
#define G_IS_RECORD_VALUE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_RECORD_VALUE))
#define G_RECORD_VALUE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_RECORD_VALUE, GRecordValueClass))


/* Valeur calculée selon des correspondances parallèles (instance) */
typedef struct _GRecordValue GRecordValue;

/* Valeur calculée selon des correspondances parallèles (classe) */
typedef struct _GRecordValueClass GRecordValueClass;


/* Indique le type défini pour une valeur calculée selon des correspondances établies. */
GType g_record_value_get_type(void);

/* Crée une nouvelle valeur calculée à partir d'une instance. */
GRecordValue *g_record_value_new(GKaitaiInstance *, const kaitai_scope_t *);

/* Détermine la valeur d'un élément Kaitai entier calculé. */
bool g_record_value_compute_value(const GRecordValue *, resolved_value_t *);

/* Détermine et ajuste la valeur d'un élément Kaitai calculé. */
bool g_record_value_compute_and_aggregate_value(const GRecordValue *, resolved_value_t *);



#endif  /* _PLUGINS_KAITAI_RECORDS_VALUE_H */
