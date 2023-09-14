
/* Chrysalide - Outil d'analyse de fichiers binaires
 * to_int.h - prototypes pour la conversion d'une chaîne en valeur entière
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


#ifndef _ANALYSIS_SCAN_ITEMS_STRING_TO_INT_H
#define _ANALYSIS_SCAN_ITEMS_STRING_TO_INT_H


#include <glib-object.h>


#include "../../item.h"



#define G_TYPE_SCAN_STRING_TO_INT_FUNCTION            g_scan_string_to_int_function_get_type()
#define G_SCAN_STRING_TO_INT_FUNCTION(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_STRING_TO_INT_FUNCTION, GScanStringToIntFunction))
#define G_IS_SCAN_STRING_TO_INT_FUNCTION(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_STRING_TO_INT_FUNCTION))
#define G_SCAN_STRING_TO_INT_FUNCTION_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_STRING_TO_INT_FUNCTION, GScanStringToIntFunctionClass))
#define G_IS_SCAN_STRING_TO_INT_FUNCTION_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_STRING_TO_INT_FUNCTION))
#define G_SCAN_STRING_TO_INT_FUNCTION_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_STRING_TO_INT_FUNCTION, GScanStringToIntFunctionClass))


/* Conversion d'une valeur textuelle en valeur entière (instance) */
typedef GRegisteredItem GScanStringToIntFunction;

/* Conversion d'une valeur textuelle en valeur entière (classe) */
typedef GRegisteredItemClass GScanStringToIntFunctionClass;


/* Indique le type défini pour une conversion de texte en entier. */
GType g_scan_string_to_int_function_get_type(void);

/* Crée une fonction de conversion de texte en valeur entière. */
GRegisteredItem *g_scan_string_to_int_function_new(void);



#endif  /* _ANALYSIS_SCAN_ITEMS_STRING_TO_INT_H */
