
/* Chrysalide - Outil d'analyse de fichiers binaires
 * intersect.c - intersection d'ensembles aux types indentiques
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


#include "intersect.h"


#include <assert.h>


#include "intersect-int.h"
#include "literal.h"



/* --------------------- INTRODUCTION D'UNE NOUVELLE EXPRESSION --------------------- */


/* Initialise la classe des intersections entre deux ensembles. */
static void g_scan_sets_intersection_class_init(GScanSetsIntersectionClass *);

/* Initialise une instance d'intersection entre deux ensembles. */
static void g_scan_sets_intersection_init(GScanSetsIntersection *);

/* Supprime toutes les références externes. */
static void g_scan_sets_intersection_dispose(GScanSetsIntersection *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_sets_intersection_finalize(GScanSetsIntersection *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Réduit une expression à une forme plus simple. */
static ScanReductionState g_scan_sets_intersection_reduce(const GScanSetsIntersection *, GScanContext *, GScanScope *, GScanExpression **);



/* ---------------------------------------------------------------------------------- */
/*                       INTRODUCTION D'UNE NOUVELLE EXPRESSION                       */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une intersection entre deux ensembles. */
G_DEFINE_TYPE(GScanSetsIntersection, g_scan_sets_intersection, G_TYPE_SCAN_EXPRESSION);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des intersections entre deux ensembles. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_sets_intersection_class_init(GScanSetsIntersectionClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GScanExpressionClass *expr;             /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_sets_intersection_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_sets_intersection_finalize;

    expr = G_SCAN_EXPRESSION_CLASS(klass);

    expr->reduce = (reduce_expr_fc)g_scan_sets_intersection_reduce;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : op = instance à initialiser.                                 *
*                                                                             *
*  Description : Initialise une instance d'intersection entre deux ensembles. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_sets_intersection_init(GScanSetsIntersection *inter)
{
    inter->first = NULL;
    inter->second = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : inter = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_sets_intersection_dispose(GScanSetsIntersection *inter)
{
    g_clear_object(&inter->first);
    g_clear_object(&inter->second);

    G_OBJECT_CLASS(g_scan_sets_intersection_parent_class)->dispose(G_OBJECT(inter));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : inter = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_sets_intersection_finalize(GScanSetsIntersection *inter)
{
    G_OBJECT_CLASS(g_scan_sets_intersection_parent_class)->finalize(G_OBJECT(inter));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type   = type d'opération booléenne à représenter.           *
*                first  = premier élément concerné.                           *
*                second = second élément concerné.                            *
*                                                                             *
*  Description : Organise une intersection entre deux ensembles.              *
*                                                                             *
*  Retour      : Expression mise en place.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanExpression *g_scan_sets_intersection_new(GScanExpression *first, GScanExpression *second)
{
    GScanExpression *result;                /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_SETS_INTERSECTION, NULL);

    if (!g_scan_sets_intersection_create(G_SCAN_SETS_INTERSECTION(result), first, second))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : inter  = instance à initialiser pleinement.                  *
*                first  = premier élément concerné.                           *
*                second = second élément concerné.                            *
*                                                                             *
*  Description : Met en place une expression d'opération booléenne.           *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_sets_intersection_create(GScanSetsIntersection *inter, GScanExpression *first, GScanExpression *second)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    inter->first = first;
    g_object_ref(G_OBJECT(first));

    inter->second = second;
    g_object_ref(G_OBJECT(second));

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

static ScanReductionState g_scan_sets_intersection_reduce(const GScanSetsIntersection *expr, GScanContext *ctx, GScanScope *scope, GScanExpression **out)
{
    ScanReductionState result;              /* Etat synthétisé à retourner */
    GScanExpression *new_first;             /* Nouvelle réduction #1       */
    GScanExpression *new_second;            /* Nouvelle réduction #2       */
    ScanReductionState state_first;         /* Etat synthétisé #1          */
    ScanReductionState state_second;        /* Etat synthétisé #2          */

    new_first = NULL;
    new_second = NULL;

    state_first = g_scan_expression_reduce(expr->first, ctx, scope, &new_first);
    if (state_first == SRS_UNRESOLVABLE)
    {
        result = SRS_UNRESOLVABLE;
        goto exit;
    }

    state_second = g_scan_expression_reduce(expr->second, ctx, scope, &new_second);
    if (state_second == SRS_UNRESOLVABLE)
    {
        result = SRS_UNRESOLVABLE;
        goto exit;
    }

    if (state_first == SRS_WAIT_FOR_SCAN || state_second == SRS_WAIT_FOR_SCAN)
    {
        if (new_first != expr->first || new_second != expr->second)
            *out = g_scan_sets_intersection_new(new_first, new_second);

        result = SRS_WAIT_FOR_SCAN;

    }

    else
    {
        assert(state_first == SRS_REDUCED && state_second == SRS_REDUCED);

        *out = g_scan_expression_intersect(new_first, new_second, ctx, scope);

        result = (*out != NULL ? SRS_REDUCED : SRS_UNRESOLVABLE);

    }

 exit:

    g_clear_object(&new_first);
    g_clear_object(&new_second);

    return result;

}
