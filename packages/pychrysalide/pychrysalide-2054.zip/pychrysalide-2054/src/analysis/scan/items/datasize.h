
/* Chrysalide - Outil d'analyse de fichiers binaires
 * datasize.h - prototypes pour la récupération de la taille du contenu scanné
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


#ifndef _ANALYSIS_SCAN_ITEMS_DATASIZE_H
#define _ANALYSIS_SCAN_ITEMS_DATASIZE_H


#include <glib-object.h>


#include "../item.h"



#define G_TYPE_SCAN_DATASIZE_FUNCTION            g_scan_datasize_function_get_type()
#define G_SCAN_DATASIZE_FUNCTION(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_DATASIZE_FUNCTION, GScanDatasizeFunction))
#define G_IS_SCAN_DATASIZE_FUNCTION(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_DATASIZE_FUNCTION))
#define G_SCAN_DATASIZE_FUNCTION_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_DATASIZE_FUNCTION, GScanDatasizeFunctionClass))
#define G_IS_SCAN_DATASIZE_FUNCTION_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_DATASIZE_FUNCTION))
#define G_SCAN_DATASIZE_FUNCTION_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_DATASIZE_FUNCTION, GScanDatasizeFunctionClass))


/* Mesure de la quantité de données scannées (instance) */
typedef GRegisteredItem GScanDatasizeFunction;

/* Mesure de la quantité de données scannées (classe) */
typedef GRegisteredItemClass GScanDatasizeFunctionClass;


/* Indique le type défini pour une mesure de quantité de données scannées. */
GType g_scan_datasize_function_get_type(void);

/* Constitue une fonction de récupération de taille de données. */
GRegisteredItem *g_scan_datasize_function_new(void);



#endif  /* _ANALYSIS_SCAN_ITEMS_DATASIZE_H */
