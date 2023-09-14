
/* Chrysalide - Outil d'analyse de fichiers binaires
 * expr-int.h - prototypes internes pour la définition d'une expression servant aux conditions de correspondance
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


#ifndef _ANALYSIS_SCAN_EXPR_INT_H
#define _ANALYSIS_SCAN_EXPR_INT_H


#include "expr.h"


#include <stdbool.h>


#include "../../glibext/comparison-int.h"



/* Réalise une comparaison entre objets selon un critère précis. */
typedef bool (* compare_expr_rich_fc) (const GScanExpression *, const GScanExpression *, RichCmpOperation, bool *);

/* Réduit une expression à une forme plus simple. */
typedef ScanReductionState (* reduce_expr_fc) (GScanExpression *, GScanContext *, GScanScope *, GScanExpression **);

/* Réduit une expression à une forme booléenne. */
typedef bool (* reduce_expr_to_bool_fc) (GScanExpression *, GScanContext *, GScanScope *, GScanExpression **);

/* Dénombre les éléments portés par une expression. */
typedef bool (* count_scan_expr_fc) (const GScanExpression *, GScanContext *, size_t *);

/* Fournit un élément donné issu d'un ensemble constitué. */
typedef bool (* get_scan_expr_fc) (const GScanExpression *, size_t, GScanContext *, GScanExpression **);

/* Réalise l'intersection entre deux ensembles. */
typedef GScanExpression * (* intersect_scan_expr_fc) (GScanExpression *, const GScanExpression *, GScanContext *, GScanScope *);


/* Expression d'évaluation généraliste (instance) */
struct _GScanExpression
{
    GObject parent;                         /* A laisser en premier        */

    ScanReductionState state;               /* Etat synthétisé de l'élément*/

};

/* Expression d'évaluation généraliste (classe) */
struct _GScanExpressionClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    compare_expr_rich_fc cmp_rich;          /* Comparaison de façon précise*/

    reduce_expr_fc reduce;                  /* Simplification d'expression */
    reduce_expr_to_bool_fc reduce_to_bool;  /* Conversion en booléen       */

    count_scan_expr_fc count;               /* Décompte d'éléments         */
    get_scan_expr_fc get;                   /* Extraction d'un élément     */
    intersect_scan_expr_fc intersect;       /* Intersection entre ensembles*/

};


/* Met en place une expression d'évaluation pour analyse. */
bool g_scan_expression_create(GScanExpression *, ScanReductionState);



#endif  /* _ANALYSIS_SCAN_EXPR_INT_H */
