
/* Chrysalide - Outil d'analyse de fichiers binaires
 * handler-int.h - prototypes internes pour la manipulation des correspondances établies lors d'un scan
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


#ifndef _ANALYSIS_SCAN_EXPRS_HANDLER_INT_H
#define _ANALYSIS_SCAN_EXPRS_HANDLER_INT_H


#include "handler.h"


#include "../expr-int.h"



/* Manipulation des correspondances établies lors d'un scan de binaire (instance) */
struct _GScanPatternHandler
{
    GScanExpression parent;                 /* A laisser en premier        */

    GSearchPattern *pattern;                /* Motif associé               */
    ScanHandlerType type;                   /* Manipulation attendue       */

};

/* Manipulation des correspondances établies lors d'un scan de binaire (classe) */
struct _GScanPatternHandlerClass
{
    GScanExpressionClass parent;            /* A laisser en premier        */

};


/* Met en place une manipulation de correspondances établies. */
bool g_scan_pattern_handler_create(GScanPatternHandler *, GSearchPattern *, ScanHandlerType);



#endif  /* _ANALYSIS_SCAN_EXPRS_HANDLER_INT_H */
