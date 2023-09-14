
/* Chrysalide - Outil d'analyse de fichiers binaires
 * log.h - prototypes pour l'affichage de message à partir des conditions d'une règle
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


#ifndef _ANALYSIS_SCAN_ITEMS_CONSOLE_LOG_H
#define _ANALYSIS_SCAN_ITEMS_CONSOLE_LOG_H


#include <glib-object.h>


#include "../../item.h"



#define G_TYPE_SCAN_CONSOLE_LOG_FUNCTION            g_scan_console_log_function_get_type()
#define G_SCAN_CONSOLE_LOG_FUNCTION(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_CONSOLE_LOG_FUNCTION, GScanConsoleLogFunction))
#define G_IS_SCAN_CONSOLE_LOG_FUNCTION(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_CONSOLE_LOG_FUNCTION))
#define G_SCAN_CONSOLE_LOG_FUNCTION_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_CONSOLE_LOG_FUNCTION, GScanConsoleLogFunctionClass))
#define G_IS_SCAN_CONSOLE_LOG_FUNCTION_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_CONSOLE_LOG_FUNCTION))
#define G_SCAN_CONSOLE_LOG_FUNCTION_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_CONSOLE_LOG_FUNCTION, GScanConsoleLogFunctionClass))


/* Mesure de la quantité de données scannées (instance) */
typedef GRegisteredItem GScanConsoleLogFunction;

/* Mesure de la quantité de données scannées (classe) */
typedef GRegisteredItemClass GScanConsoleLogFunctionClass;


/* Indique le type défini pour un afficheur de messages arbitraires. */
GType g_scan_console_log_function_get_type(void);

/* Constitue une fonction d'affichage de messages quelconques. */
GScanConsoleLogFunction *g_scan_console_log_function_new(void);



#endif  /* _ANALYSIS_SCAN_ITEMS_CONSOLE_LOG_H */
