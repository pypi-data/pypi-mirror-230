
/* Chrysalide - Outil d'analyse de fichiers binaires
 * array.h - prototypes pour la manipulation des types de tableaux
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


#ifndef _ANALYSIS_TYPES_ARRAY_H
#define _ANALYSIS_TYPES_ARRAY_H


#include <glib-object.h>


#include "../type.h"



#define G_TYPE_ARRAY_TYPE            g_array_type_get_type()
#define G_ARRAY_TYPE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_ARRAY_TYPE, GArrayType))
#define G_IS_ARRAY_TYPE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_ARRAY_TYPE))
#define G_ARRAY_TYPE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ARRAY_TYPE, GArrayTypeClass))
#define G_IS_ARRAY_TYPE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ARRAY_TYPE))
#define G_ARRAY_TYPE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ARRAY_TYPE, GArrayTypeClass))


/* Description de tableau (instance) */
typedef struct _GArrayType GArrayType;

/* Description de tableau (classe) */
typedef struct _GArrayTypeClass GArrayTypeClass;


/* Indique le type défini pour un tableau. */
GType g_array_type_get_type(void);

/* Crée une représentation de tableau. */
GDataType *g_array_type_new(GDataType *);

/* Fournit le type des membres du tableau. */
GDataType *g_array_type_get_members_type(const GArrayType *);

/* Indique si la dimension du tableau est chiffrée. */
bool g_array_type_is_dimension_numbered(const GArrayType *);

/* Fournit la dimension associée au tableau. */
ssize_t g_array_type_get_dimension_number(const GArrayType *);

/* Définit la dimension associée au tableau. */
void g_array_type_set_dimension_number(GArrayType *, ssize_t);

/* Fournit la dimension associée au tableau. */
const char *g_array_type_get_dimension_expression(const GArrayType *);

/* Définit la dimension associée au tableau. */
void g_array_type_set_dimension_expression(GArrayType *, char *);

/* Définit une dimension vide pour le tableau. */
void g_array_type_set_empty_dimension(GArrayType *);



#endif  /* _ANALYSIS_TYPES_ARRAY_H */
