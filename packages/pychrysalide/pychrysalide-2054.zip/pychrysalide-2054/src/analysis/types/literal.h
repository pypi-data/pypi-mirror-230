
/* Chrysalide - Outil d'analyse de fichiers binaires
 * literal.h - prototypes pour la manipulation des valeurs littérales de types instanciés
 *
 * Copyright (C) 2012-2018 Cyrille Bagard
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


#ifndef _ANALYSIS_TYPES_LITERAL_H
#define _ANALYSIS_TYPES_LITERAL_H


#include <glib-object.h>


#include "../type.h"



#define G_TYPE_LITERAL_TYPE            g_literal_type_get_type()
#define G_LITERAL_TYPE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_LITERAL_TYPE, GLiteralType))
#define G_IS_LITERAL_TYPE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_LITERAL_TYPE))
#define G_LITERAL_TYPE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_LITERAL_TYPE, GLiteralTypeClass))
#define G_IS_LITERAL_TYPE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_LITERAL_TYPE))
#define G_LITERAL_TYPE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_LITERAL_TYPE, GLiteralTypeClass))


/* Description de type instancié avec une valeur litérale (instance) */
typedef struct _GLiteralType GLiteralType;

/* Description de type instancié avec une valeur litérale (classe) */
typedef struct _GLiteralTypeClass GLiteralTypeClass;


/* Valeurs instanciées supportées */
typedef union _literal_value
{
    int int_val;                            /* Valeur entière              */
    float float_val;                        /* Valeur flottante            */

} literal_value;


/* Indique le type défini pour un type instancié avec une valeur litérale. */
GType g_literal_type_get_type(void);

/* Crée une représentation de type instancié avec une valeur. */
GDataType *g_literal_type_new(GDataType *, const literal_value *);



#endif  /* _ANALYSIS_TYPES_LITERAL_H */
