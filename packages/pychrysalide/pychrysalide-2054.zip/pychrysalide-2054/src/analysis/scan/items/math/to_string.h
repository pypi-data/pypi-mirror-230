
/* Chrysalide - Outil d'analyse de fichiers binaires
 * to_string.h - prototypes pour la conversion d'une valeur entière en chaîne
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _ANALYSIS_SCAN_ITEMS_MATH_TO_STRING_H
#define _ANALYSIS_SCAN_ITEMS_MATH_TO_STRING_H


#include <glib-object.h>


#include "../../item.h"



#define G_TYPE_SCAN_MATH_TO_STRING_FUNCTION            g_scan_math_to_string_function_get_type()
#define G_SCAN_MATH_TO_STRING_FUNCTION(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_MATH_TO_STRING_FUNCTION, GScanMathToStringFunction))
#define G_IS_SCAN_MATH_TO_STRING_FUNCTION(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_MATH_TO_STRING_FUNCTION))
#define G_SCAN_MATH_TO_STRING_FUNCTION_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_MATH_TO_STRING_FUNCTION, GScanMathToStringFunctionClass))
#define G_IS_SCAN_MATH_TO_STRING_FUNCTION_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_MATH_TO_STRING_FUNCTION))
#define G_SCAN_MATH_TO_STRING_FUNCTION_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_MATH_TO_STRING_FUNCTION, GScanMathToStringFunctionClass))


/* Conversion d'une valeur entière en valeur textuelle (instance) */
typedef GRegisteredItem GScanMathToStringFunction;

/* Conversion d'une valeur entière en valeur textuelle (classe) */
typedef GRegisteredItemClass GScanMathToStringFunctionClass;


/* Indique le type défini pour une conversion d'entier en texte. */
GType g_scan_math_to_string_function_get_type(void);

/* Crée une fonction de conversion de valeur entière en texte. */
GRegisteredItem *g_scan_math_to_string_function_new(void);



#endif  /* _ANALYSIS_SCAN_ITEMS_MATH_TO_STRING_H */
