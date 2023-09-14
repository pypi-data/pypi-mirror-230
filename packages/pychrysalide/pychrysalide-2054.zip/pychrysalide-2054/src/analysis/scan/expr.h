
/* Chrysalide - Outil d'analyse de fichiers binaires
 * expr.h - prototypes pour la définition d'une expression servant aux conditions de correspondance
 *
 * Copyright (C) 2022 Cyrille Bagard
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


#ifndef _ANALYSIS_SCAN_EXPR_H
#define _ANALYSIS_SCAN_EXPR_H


#include <glib-object.h>
#include <stdbool.h>


#include "context.h"
#include "scope.h"



#define G_TYPE_SCAN_EXPRESSION            g_scan_expression_get_type()
#define G_SCAN_EXPRESSION(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_EXPRESSION, GScanExpression))
#define G_IS_SCAN_EXPRESSION(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_EXPRESSION))
#define G_SCAN_EXPRESSION_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_EXPRESSION, GScanExpressionClass))
#define G_IS_SCAN_EXPRESSION_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_EXPRESSION))
#define G_SCAN_EXPRESSION_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_EXPRESSION, GScanExpressionClass))


/* Expression d'évaluation généraliste (instance) */
typedef struct _GScanExpression GScanExpression;

/* Expression d'évaluation généraliste (classe) */
typedef struct _GScanExpressionClass GScanExpressionClass;


/* Etat de l'expression vis à vis des réductions */
typedef enum _ScanReductionState
{
    SRS_PENDING,                            /* Nature à déterminer         */
    SRS_REDUCED,                            /* Nature compacte finale      */
    SRS_WAIT_FOR_SCAN,                      /* Nature vouée à évoluer      */
    SRS_UNRESOLVABLE,                       /* Nature indéterminable       */

} ScanReductionState;


/* Indique le type défini pour une expression de validation. */
GType g_scan_expression_get_type(void);

/* Indique l'état de réduction d'une expression. */
ScanReductionState g_scan_expression_get_state(const GScanExpression *);

/* Réduit une expression à une forme plus simple. */
ScanReductionState g_scan_expression_reduce(GScanExpression *, GScanContext *, GScanScope *, GScanExpression **);

/* Réduit une expression à une forme booléenne. */
bool g_scan_expression_reduce_to_boolean(GScanExpression *, GScanContext *, GScanScope *, GScanExpression **);

/* Détermine si l'expression peut représenter un ensemble. */
bool g_scan_expression_handle_set_features(const GScanExpression *);

/* Dénombre les éléments portés par une expression. */
bool g_scan_expression_count_items(const GScanExpression *, GScanContext *, size_t *);

/* Fournit un élément donné issu d'un ensemble constitué. */
bool g_scan_expression_get_item(const GScanExpression *, size_t, GScanContext *, GScanExpression **);

/* Réalise l'intersection entre deux ensembles. */
GScanExpression *g_scan_expression_intersect(GScanExpression *, const GScanExpression *, GScanContext *, GScanScope *);



#endif  /* _ANALYSIS_SCAN_EXPR_H */
