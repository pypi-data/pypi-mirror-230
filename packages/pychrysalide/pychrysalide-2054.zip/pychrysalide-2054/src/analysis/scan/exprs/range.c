
/* Chrysalide - Outil d'analyse de fichiers binaires
 * range.c - représentation compacte d'un éventail de valeurs
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


#include "range.h"


#include "literal.h"
#include "range-int.h"



/* --------------------- INTRODUCTION D'UNE NOUVELLE EXPRESSION --------------------- */


/* Initialise la classe des éventail de valeurs. */
static void g_scan_compact_range_class_init(GScanCompactRangeClass *);

/* Initialise une instance d'éventail de valeurs. */
static void g_scan_compact_range_init(GScanCompactRange *);

/* Supprime toutes les références externes. */
static void g_scan_compact_range_dispose(GScanCompactRange *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_compact_range_finalize(GScanCompactRange *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Réduit une expression à une forme plus simple. */
static ScanReductionState g_scan_compact_range_reduce(const GScanCompactRange *, GScanContext *, GScanScope *, GScanExpression **);

/* Réduit une expression à une forme booléenne. */
static bool g_scan_compact_range_reduce_to_boolean(const GScanCompactRange *, GScanContext *, GScanScope *, GScanExpression **);

/* Réalise l'intersection entre deux ensembles. */
static GScanExpression *g_scan_compact_range_intersect(const GScanCompactRange *expr, const GScanExpression *, GScanContext *, GScanScope *);



/* ---------------------------------------------------------------------------------- */
/*                       INTRODUCTION D'UNE NOUVELLE EXPRESSION                       */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une représentation compacte d'un éventail de valeurs. */
G_DEFINE_TYPE(GScanCompactRange, g_scan_compact_range, G_TYPE_SCAN_EXPRESSION);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des éventail de valeurs.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_compact_range_class_init(GScanCompactRangeClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GScanExpressionClass *expr;             /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_compact_range_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_compact_range_finalize;

    expr = G_SCAN_EXPRESSION_CLASS(klass);

    expr->reduce = (reduce_expr_fc)g_scan_compact_range_reduce;
    expr->reduce_to_bool = (reduce_expr_to_bool_fc)g_scan_compact_range_reduce_to_boolean;
    expr->intersect = (intersect_scan_expr_fc)g_scan_compact_range_intersect;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : range = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance d'éventail de valeurs.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_compact_range_init(GScanCompactRange *range)
{
    range->start = NULL;
    range->end = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : range = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_compact_range_dispose(GScanCompactRange *range)
{
    g_clear_object(&range->start);
    g_clear_object(&range->end);

    G_OBJECT_CLASS(g_scan_compact_range_parent_class)->dispose(G_OBJECT(range));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : range = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_compact_range_finalize(GScanCompactRange *range)
{
    G_OBJECT_CLASS(g_scan_compact_range_parent_class)->finalize(G_OBJECT(range));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : start = point de départ de la plage de valeurs.              *
*                end   = point d'arrivée de la plage de valeurs.              *
*                                                                             *
*  Description : Organise une réprésentation d'un éventail de valeurs.        *
*                                                                             *
*  Retour      : Expression mise en place.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanExpression *g_scan_compact_range_new(GScanExpression *start, GScanExpression *end)
{
    GScanExpression *result;                /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_COMPACT_RANGE, NULL);

    if (!g_scan_compact_range_create(G_SCAN_COMPACT_RANGE(result), start, end))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : range = instance à initialiser pleinement.                   *
*                start = point de départ de la plage de valeurs.              *
*                end   = point d'arrivée de la plage de valeurs.              *
*                                                                             *
*  Description : Met en place une réprésentation d'un éventail de valeurs.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_compact_range_create(GScanCompactRange *range, GScanExpression *start, GScanExpression *end)
{
    bool result;                            /* Bilan à retourner           */

    result = g_scan_expression_create(G_SCAN_EXPRESSION(range), SRS_PENDING);
    if (!result) goto exit;

    range->start = start;
    g_object_ref(G_OBJECT(start));

    range->end = end;
    g_object_ref(G_OBJECT(end));

 exit:

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : expr  = expression à consulter.                              *
*                ctx   = contexte de suivi de l'analyse courante.             *
*                scope = portée courante des variables locales.               *
*                out   = zone d'enregistrement de la réduction opérée. [OUT]  *
*                                                                             *
*  Description : Réduit une expression à une forme plus simple.               *
*                                                                             *
*  Retour      : Bilan de l'opération : false en cas d'erreur irrécupérable.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static ScanReductionState g_scan_compact_range_reduce(const GScanCompactRange *expr, GScanContext *ctx, GScanScope *scope, GScanExpression **out)
{
    ScanReductionState result;              /* Etat synthétisé à retourner */
    GScanExpression *new_start;             /* Nouvelle réduction #1       */
    GScanExpression *new_end;               /* Nouvelle réduction #2       */
    ScanReductionState state_start;         /* Etat synthétisé #1          */
    ScanReductionState state_end;           /* Etat synthétisé #2          */

    new_start = NULL;
    new_end = NULL;

    state_start = g_scan_expression_reduce(expr->start, ctx, scope, &new_start);
    if (state_start == SRS_UNRESOLVABLE)
    {
        result = SRS_UNRESOLVABLE;
        goto exit;
    }

    state_end = g_scan_expression_reduce(expr->end, ctx, scope, &new_end);
    if (state_end == SRS_UNRESOLVABLE)
    {
        result = SRS_UNRESOLVABLE;
        goto exit;
    }

    if (state_start == SRS_WAIT_FOR_SCAN || state_end == SRS_WAIT_FOR_SCAN)
        result = SRS_WAIT_FOR_SCAN;
    else
        result = SRS_REDUCED;

    if (new_start != expr->start || new_end != expr->end)
        *out = g_scan_compact_range_new(new_start, new_end);

 exit:

    g_clear_object(&new_start);
    g_clear_object(&new_end);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr  = expression à consulter.                              *
*                ctx   = contexte de suivi de l'analyse courante.             *
*                scope = portée courante des variables locales.               *
*                out   = zone d'enregistrement de la réduction opérée. [OUT]  *
*                                                                             *
*  Description : Réduit une expression à une forme booléenne.                 *
*                                                                             *
*  Retour      : Bilan de l'opération : false en cas d'erreur irrécupérable.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_scan_compact_range_reduce_to_boolean(const GScanCompactRange *expr, GScanContext *ctx, GScanScope *scope, GScanExpression **out)
{
    bool result;                            /* Bilan à retourner           */
    bool status;                            /* Bilan d'une comparaison     */

    result = G_IS_SCAN_LITERAL_EXPRESSION(expr->start) && G_IS_SCAN_LITERAL_EXPRESSION(expr->end);
    if (!result) goto exit;

    result = g_comparable_item_compare_rich(G_COMPARABLE_ITEM(expr->start),
                                            G_COMPARABLE_ITEM(expr->end),
                                            RCO_LE, &status);
    if (!result) goto exit;

    *out = g_scan_literal_expression_new(LVT_BOOLEAN, &status);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr  = expression à filtrer.                                *
*                other = expression utilisée pour le filtrage.                *
*                ctx   = contexte de suivi de l'analyse courante.             *
*                scope = portée courante des variables locales.               *
*                                                                             *
*  Description : Réalise l'intersection entre deux ensembles.                 *
*                                                                             *
*  Retour      : Intersection entre les deux ensembles ou NULL en cas d'échec.*
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GScanExpression *g_scan_compact_range_intersect(const GScanCompactRange *expr, const GScanExpression *other, GScanContext *ctx, GScanScope *scope)
{
    GScanExpression *result;                /* Instance à retourner        */




    result = true;  // TODO




    return result;

}
