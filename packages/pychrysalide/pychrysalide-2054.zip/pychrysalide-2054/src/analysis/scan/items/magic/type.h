
/* Chrysalide - Outil d'analyse de fichiers binaires
 * type.h - prototypes pour la reconnaissance du type d'un contenu
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


#ifndef _ANALYSIS_SCAN_ITEMS_MAGIC_TYPE_H
#define _ANALYSIS_SCAN_ITEMS_MAGIC_TYPE_H


#include <glib-object.h>


#include "../../item.h"



#define G_TYPE_SCAN_MAGIC_TYPE_FUNCTION            g_scan_magic_type_function_get_type()
#define G_SCAN_MAGIC_TYPE_FUNCTION(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_MAGIC_TYPE_FUNCTION, GScanMagicTypeFunction))
#define G_IS_SCAN_MAGIC_TYPE_FUNCTION(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_MAGIC_TYPE_FUNCTION))
#define G_SCAN_MAGIC_TYPE_FUNCTION_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_MAGIC_TYPE_FUNCTION, GScanMagicTypeFunctionClass))
#define G_IS_SCAN_MAGIC_TYPE_FUNCTION_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_MAGIC_TYPE_FUNCTION))
#define G_SCAN_MAGIC_TYPE_FUNCTION_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_MAGIC_TYPE_FUNCTION, GScanMagicTypeFunctionClass))


/* Reconnaissance de types de contenus (instance) */
typedef GRegisteredItem GScanMagicTypeFunction;

/* Reconnaissance de types de contenus (classe) */
typedef GRegisteredItemClass GScanMagicTypeFunctionClass;


/* Indique le type défini pour une reconnaissance de types de contenus. */
GType g_scan_magic_type_function_get_type(void);

/* Constitue une fonction d'identification de types de contenus. */
GRegisteredItem *g_scan_magic_type_function_new(void);



#endif  /* _ANALYSIS_SCAN_ITEMS_MAGIC_TYPE_H */
