
/* Chrysalide - Outil d'analyse de fichiers binaires
 * uint.h - prototypes pour la lecture d'un mot à partir de données binaires
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


#ifndef _ANALYSIS_SCAN_ITEMS_UINT_H
#define _ANALYSIS_SCAN_ITEMS_UINT_H


#include <glib-object.h>


#include "../item.h"
#include "../../../arch/archbase.h"



#define G_TYPE_SCAN_UINT_FUNCTION            g_scan_uint_function_get_type()
#define G_SCAN_UINT_FUNCTION(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_UINT_FUNCTION, GScanUintFunction))
#define G_IS_SCAN_UINT_FUNCTION(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_UINT_FUNCTION))
#define G_SCAN_UINT_FUNCTION_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_UINT_FUNCTION, GScanUintFunctionClass))
#define G_IS_SCAN_UINT_FUNCTION_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_UINT_FUNCTION))
#define G_SCAN_UINT_FUNCTION_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_UINT_FUNCTION, GScanUintFunctionClass))


/* Fonction conduisant à la lecture d'un mot (instance) */
typedef struct _GScanUintFunction GScanUintFunction;

/* Fonction conduisant à la lecture d'un mot (classe) */
typedef struct _GScanUintFunctionClass GScanUintFunctionClass;


/* Indique le type défini pour une lecture de mot à partir de données binaires. */
GType g_scan_uint_function_get_type(void);

/* Constitue une fonction de lecture de valeur entière. */
GRegisteredItem *g_scan_uint_function_new(MemoryDataSize, SourceEndian);



#endif  /* _ANALYSIS_SCAN_ITEMS_UINT_H */
