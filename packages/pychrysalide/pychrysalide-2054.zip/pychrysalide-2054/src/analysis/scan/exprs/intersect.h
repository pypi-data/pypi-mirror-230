
/* Chrysalide - Outil d'analyse de fichiers binaires
 * intersect.h - prototypes pour l'intersection d'ensembles aux types indentiques
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


#ifndef _ANALYSIS_SCAN_EXPRS_INTERSECT_H
#define _ANALYSIS_SCAN_EXPRS_INTERSECT_H


#include "../expr.h"



#define G_TYPE_SCAN_SETS_INTERSECTION            g_scan_sets_intersection_get_type()
#define G_SCAN_SETS_INTERSECTION(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_SETS_INTERSECTION, GScanSetsIntersection))
#define G_IS_SCAN_SETS_INTERSECTION(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_SETS_INTERSECTION))
#define G_SCAN_SETS_INTERSECTION_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_SETS_INTERSECTION, GScanSetsIntersectionClass))
#define G_IS_SCAN_SETS_INTERSECTION_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_SETS_INTERSECTION))
#define G_SCAN_SETS_INTERSECTION_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_SETS_INTERSECTION, GScanSetsIntersectionClass))


/* Opération d'intersection entre deux ensembles (instance) */
typedef struct _GScanSetsIntersection GScanSetsIntersection;

/* Opération d'intersection entre deux ensembles (classe) */
typedef struct _GScanSetsIntersectionClass GScanSetsIntersectionClass;


/* Indique le type défini pour une intersection entre deux ensembles. */
GType g_scan_sets_intersection_get_type(void);

/* Organise une intersection entre deux ensembles. */
GScanExpression *g_scan_sets_intersection_new(GScanExpression *, GScanExpression *);



#endif  /* _ANALYSIS_SCAN_EXPRS_INTERSECT_H */
