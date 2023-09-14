
/* Chrysalide - Outil d'analyse de fichiers binaires
 * make.h - prototypes pour une construction de volume de secondes à partir d'une date
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


#ifndef _ANALYSIS_SCAN_ITEMS_TIME_MAKE_H
#define _ANALYSIS_SCAN_ITEMS_TIME_MAKE_H


#include <glib-object.h>


#include "../../item.h"



#define G_TYPE_SCAN_TIME_MAKE_FUNCTION            g_scan_time_make_function_get_type()
#define G_SCAN_TIME_MAKE_FUNCTION(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_TIME_MAKE_FUNCTION, GScanTimeMakeFunction))
#define G_IS_SCAN_TIME_MAKE_FUNCTION(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_TIME_MAKE_FUNCTION))
#define G_SCAN_TIME_MAKE_FUNCTION_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_TIME_MAKE_FUNCTION, GScanTimeMakeFunctionClass))
#define G_IS_SCAN_TIME_MAKE_FUNCTION_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_TIME_MAKE_FUNCTION))
#define G_SCAN_TIME_MAKE_FUNCTION_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_TIME_MAKE_FUNCTION, GScanTimeMakeFunctionClass))


/* Convertisseur de date en nombre de secondes depuis le 01/01/1970 (instance) */
typedef GRegisteredItem GScanTimeMakeFunction;

/* Convertisseur de date en nombre de secondes depuis le 01/01/1970 (classe) */
typedef GRegisteredItemClass GScanTimeMakeFunctionClass;


/* Indique le type défini pour une conversion de date en nombre de secondes. */
GType g_scan_time_make_function_get_type(void);

/* Constitue une fonction de décompte du temps écoulé. */
GRegisteredItem *g_scan_time_make_function_new(void);



#endif  /* _ANALYSIS_SCAN_ITEMS_TIME_MAKE_H */
