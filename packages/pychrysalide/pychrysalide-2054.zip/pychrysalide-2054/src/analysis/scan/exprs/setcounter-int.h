
/* Chrysalide - Outil d'analyse de fichiers binaires
 * setcounter-int.h - prototypes internes pour le décompte global de correspondances locales
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


#ifndef _ANALYSIS_SCAN_EXPRS_SETCOUNTER_INT_H
#define _ANALYSIS_SCAN_EXPRS_SETCOUNTER_INT_H


#include "setcounter.h"


#include "../expr-int.h"



/* Décompte global de correspondances locales (instance) */
struct _GScanSetMatchCounter
{
    GScanExpression parent;                 /* A laisser en premier        */

    GSearchPattern **patterns;              /* Motifs associés             */
    size_t count;                           /* Nombre de ces motifs        */

    ScanSetCounterType type;                /* Type de décompte            */
    size_t number;                          /* Eventuel volume associé     */

};

/* Décompte global de correspondances locales (classe) */
struct _GScanSetMatchCounterClass
{
    GScanExpressionClass parent;            /* A laisser en premier        */

};



/* Met en place un décompte de motifs avec correspondances. */
bool g_scan_set_match_counter_create(GScanSetMatchCounter *, GSearchPattern ** const, size_t);



#endif  /* _ANALYSIS_SCAN_EXPRS_SETCOUNTER_INT_H */
