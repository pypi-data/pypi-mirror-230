
/* Chrysalide - Outil d'analyse de fichiers binaires
 * range.h - prototypes pour la représentation compacte d'un éventail de valeurs
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


#ifndef _ANALYSIS_SCAN_EXPRS_SET_H
#define _ANALYSIS_SCAN_EXPRS_SET_H


#include "../expr.h"



#define G_TYPE_SCAN_COMPACT_RANGE            g_scan_compact_range_get_type()
#define G_SCAN_COMPACT_RANGE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_COMPACT_RANGE, GScanCompactRange))
#define G_IS_SCAN_COMPACT_RANGE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_COMPACT_RANGE))
#define G_SCAN_COMPACT_RANGE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_COMPACT_RANGE, GScanCompactRangeClass))
#define G_IS_SCAN_COMPACT_RANGE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_COMPACT_RANGE))
#define G_SCAN_COMPACT_RANGE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_COMPACT_RANGE, GScanCompactRangeClass))


/* Représentation compacte d'un éventail de valeurs (instance) */
typedef struct _GScanCompactRange GScanCompactRange;

/* Représentation compacte d'un éventail de valeurs (classe) */
typedef struct _GScanCompactRangeClass GScanCompactRangeClass;


/* Indique le type défini pour une représentation compacte d'un éventail de valeurs. */
GType g_scan_compact_range_get_type(void);

/* Organise une réprésentation d'un éventail de valeurs. */
GScanExpression *g_scan_compact_range_new(GScanExpression *, GScanExpression *);



#endif  /* _ANALYSIS_SCAN_EXPRS_SET_H */
