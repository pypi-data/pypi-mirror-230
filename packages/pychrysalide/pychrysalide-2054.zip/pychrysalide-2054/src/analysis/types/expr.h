
/* Chrysalide - Outil d'analyse de fichiers binaires
 * expr.h - prototypes pour la manipulation de types sous forme d'expressions
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


#ifndef _ANALYSIS_TYPES_EXPR_H
#define _ANALYSIS_TYPES_EXPR_H


#include <glib-object.h>


#include "../type.h"



#define G_TYPE_EXPR_TYPE            g_expr_type_get_type()
#define G_EXPR_TYPE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_EXPR_TYPE, GExprType))
#define G_IS_EXPR_TYPE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_EXPR_TYPE))
#define G_EXPR_TYPE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_EXPR_TYPE, GExprTypeClass))
#define G_IS_EXPR_TYPE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_EXPR_TYPE))
#define G_EXPR_TYPE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_EXPR_TYPE, GExprTypeClass))


/* Description de type sous forme d'expressions (instance) */
typedef struct _GExprType GExprType;

/* Description de type sous forme d'expressions (classe) */
typedef struct _GExprTypeClass GExprTypeClass;


/* Indique le type défini pour un type sous forme d'expressions. */
GType g_expr_type_get_type(void);

/* Crée une représentation de type sous forme d'expressions. */
GDataType *g_expr_type_new(const char *);

/* Fournit la valeur d'un type fourni sous forme de caractères. */
const char *g_expr_type_get_value(const GExprType *);



#endif  /* _ANALYSIS_TYPES_EXPR_H */
