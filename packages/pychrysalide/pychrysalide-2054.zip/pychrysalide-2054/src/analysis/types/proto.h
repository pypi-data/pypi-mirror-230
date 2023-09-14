
/* Chrysalide - Outil d'analyse de fichiers binaires
 * proto.h - prototypes pour la manipulation des prototypes
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#ifndef _ANALYSIS_TYPES_PROTO_H
#define _ANALYSIS_TYPES_PROTO_H


#include <glib-object.h>


#include "../type.h"



#define G_TYPE_PROTO_TYPE            g_proto_type_get_type()
#define G_PROTO_TYPE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_PROTO_TYPE, GProtoType))
#define G_IS_PROTO_TYPE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_PROTO_TYPE))
#define G_PROTO_TYPE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_PROTO_TYPE, GProtoTypeClass))
#define G_IS_PROTO_TYPE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_PROTO_TYPE))
#define G_PROTO_TYPE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_PROTO_TYPE, GProtoTypeClass))


/* Description de prototype (instance) */
typedef struct _GProtoType GProtoType;

/* Description de prototype (classe) */
typedef struct _GProtoTypeClass GProtoTypeClass;


/* Indique le type défini pour un prototype. */
GType g_proto_type_get_type(void);

/* Crée une représentation de prototype. */
GDataType *g_proto_type_new(void);

/* Définit le type de retour d'un prototype. */
void g_proto_type_set_return_type(GProtoType *, GDataType *);

/* Fournit le type de retour d'un prototype. */
GDataType *g_proto_type_get_return_type(const GProtoType *);

/* Ajoute un argument à un prototype. */
void g_proto_type_add_arg(GProtoType *, GDataType *);

/* Indique le nombre d'arguments associés au prototype. */
size_t g_proto_type_count_args(const GProtoType *);

/* Fournit un argument donné du prototype. */
GDataType *g_proto_type_get_arg(const GProtoType *, size_t);



#endif  /* _ANALYSIS_TYPES_PROTO_H */
