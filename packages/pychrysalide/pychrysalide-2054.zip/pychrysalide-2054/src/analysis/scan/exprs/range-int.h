
/* Chrysalide - Outil d'analyse de fichiers binaires
 * range-int.h - prototypes internes pour la représentation compacte d'un éventail de valeurs
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


#ifndef _ANALYSIS_SCAN_EXPRS_RANGE_INT_H
#define _ANALYSIS_SCAN_EXPRS_RANGE_INT_H


#include "range.h"


#include "../expr-int.h"



/* Représentation compacte d'un éventail de valeurs (instance) */
struct _GScanCompactRange
{
    GScanExpression parent;                 /* A laisser en premier        */

    GScanExpression *start;                 /* Point de départ             */
    GScanExpression *end;                   /* Point d'arrivée             */

};

/* Représentation compacte d'un éventail de valeurs (classe) */
struct _GScanCompactRangeClass
{
    GScanExpressionClass parent;            /* A laisser en premier        */

};


/* Met en place une réprésentation d'un éventail de valeurs. */
bool g_scan_compact_range_create(GScanCompactRange *, GScanExpression *, GScanExpression *);



#endif  /* _ANALYSIS_SCAN_EXPRS_RANGE_INT_H */
