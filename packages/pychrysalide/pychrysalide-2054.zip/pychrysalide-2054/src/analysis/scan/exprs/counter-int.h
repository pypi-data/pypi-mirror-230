
/* Chrysalide - Outil d'analyse de fichiers binaires
 * counter-int.h - prototypes internes pour le décompte de correspondances identifiées dans du contenu binaire
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


#ifndef _ANALYSIS_SCAN_EXPRS_COUNTER_INT_H
#define _ANALYSIS_SCAN_EXPRS_COUNTER_INT_H


#include "counter.h"


#include "../expr-int.h"



/* Décompte des identifications de motifs (instance) */
struct _GScanMatchCounter
{
    GScanExpression parent;                 /* A laisser en premier        */

    GSearchPattern *pattern;                /* Motif associé               */

};

/* Décompte des identifications de motifs (classe) */
struct _GScanMatchCounterClass
{
    GScanExpressionClass parent;            /* A laisser en premier        */

};


/* Met en place un compteur de correspondances. */
bool g_scan_match_counter_create(GScanMatchCounter *, GSearchPattern *);



#endif  /* _ANALYSIS_SCAN_EXPRS_COUNTER_INT_H */
