
/* Chrysalide - Outil d'analyse de fichiers binaires
 * handler.h - prototypes pour la manipulation des correspondances établies lors d'un scan
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


#ifndef _ANALYSIS_SCAN_EXPRS_HANDLER_H
#define _ANALYSIS_SCAN_EXPRS_HANDLER_H


#include "../expr.h"



#define G_TYPE_SCAN_PATTERN_HANDLER            g_scan_pattern_handler_get_type()
#define G_SCAN_PATTERN_HANDLER(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_PATTERN_HANDLER, GScanPatternHandler))
#define G_IS_SCAN_PATTERN_HANDLER(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_PATTERN_HANDLER))
#define G_SCAN_PATTERN_HANDLER_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_PATTERN_HANDLER, GScanPatternHandlerClass))
#define G_IS_SCAN_PATTERN_HANDLER_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_PATTERN_HANDLER))
#define G_SCAN_PATTERN_HANDLER_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_PATTERN_HANDLER, GScanPatternHandlerClass))


/* Manipulation des correspondances établies lors d'un scan de binaire (instance) */
typedef struct _GScanPatternHandler GScanPatternHandler;

/* Manipulation des correspondances établies lors d'un scan de binaire (classe) */
typedef struct _GScanPatternHandlerClass GScanPatternHandlerClass;


/* Type de manipulation représentée */
typedef enum _ScanHandlerType
{
    SHT_RAW,                                /* Correspondances brutes      */
    SHT_START,                              /* Départs de correspondances  */
    SHT_LENGTH,                             /* Taille de correspondances   */
    SHT_END,                                /* Fins de correspondances     */

} ScanHandlerType;


/* Indique le type défini pour une manipulation de correspondances établies lors d'un scan. */
GType g_scan_pattern_handler_get_type(void);

/* Met en place une manipulation de correspondances établies. */
GScanExpression *g_scan_pattern_handler_new(GSearchPattern *, ScanHandlerType);



#endif  /* _ANALYSIS_SCAN_EXPRS_HANDLER_H */
