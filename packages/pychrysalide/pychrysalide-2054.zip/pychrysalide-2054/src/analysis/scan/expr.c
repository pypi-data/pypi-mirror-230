
/* Chrysalide - Outil d'analyse de fichiers binaires
 * expr.c - définition d'une expression servant aux conditions de correspondance
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


#include "expr.h"


#include <assert.h>


#include "expr-int.h"
#include "exprs/literal.h"
#include "exprs/set.h"



/* ----------------------- BASES D'OBJET POUR LE SYSTEME GLIB ----------------------- */


/* Initialise la classe des expressions de validation. */
static void g_scan_expression_class_init(GScanExpressionClass *);

/* Initialise une instance d'expression de validation. */
static void g_scan_expression_init(GScanExpression *);

/* Procède à l'initialisation de l'interface de comparaison. */
static void g_scan_expression_cmp_interface_init(GComparableItemInterface *);

/* Supprime toutes les références externes. */
static void g_scan_expression_dispose(GScanExpression *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_expression_finalize(GScanExpression *);

/* Réalise l'intersection entre deux ensembles. */
static GScanExpression *_g_scan_expression_intersect(GScanExpression *, const GScanExpression *, GScanContext *, GScanScope *);



/* ----------------------- INTERFACE OFFRANT DES COMPARAISONS ----------------------- */


/* Réalise une comparaison entre objets selon un critère précis. */
static bool g_scan_expression_compare_rich(const GScanExpression *, const GScanExpression *, RichCmpOperation, bool *);



/* ---------------------------------------------------------------------------------- */
/*                         BASES D'OBJET POUR LE SYSTEME GLIB                         */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une expression de validation. */
G_DEFINE_TYPE_WITH_CODE(GScanExpression, g_scan_expression, G_TYPE_OBJECT,
                        G_IMPLEMENT_INTERFACE(G_TYPE_COMPARABLE_ITEM, g_scan_expression_cmp_interface_init));


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des expressions de validation.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_expression_class_init(GScanExpressionClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_expression_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_expression_finalize;

    klass->intersect = _g_scan_expression_intersect;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance d'expression de validation.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_expression_init(GScanExpression *expr)
{
    expr->state = SRS_PENDING;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de comparaison.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_expression_cmp_interface_init(GComparableItemInterface *iface)
{
    iface->cmp_rich = (compare_rich_fc)g_scan_expression_compare_rich;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_expression_dispose(GScanExpression *expr)
{
    G_OBJECT_CLASS(g_scan_expression_parent_class)->dispose(G_OBJECT(expr));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_expression_finalize(GScanExpression *expr)
{
    G_OBJECT_CLASS(g_scan_expression_parent_class)->finalize(G_OBJECT(expr));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr  = instance à initialiser pleinement.                   *
*                state = état de réduction initial associé par l'expression.  *
*                                                                             *
*  Description : Met en place une expression d'évaluation pour analyse.       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_expression_create(GScanExpression *expr, ScanReductionState state)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    expr->state = state;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr = expression à consulter.                               *
*                                                                             *
*  Description : Indique l'état de réduction d'une expression.                *
*                                                                             *
*  Retour      : Etat courant associé à l'expression.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

ScanReductionState g_scan_expression_get_state(const GScanExpression *expr)
{
    ScanReductionState result;              /* Etat à retourner            */

    result = expr->state;

    return result;

}


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

ScanReductionState g_scan_expression_reduce(GScanExpression *expr, GScanContext *ctx, GScanScope *scope, GScanExpression **out)
{
    GScanExpressionClass *class;            /* Classe à activer            */

    if (expr->state == SRS_REDUCED)
    {
        *out = expr;
        g_object_ref(G_OBJECT(expr));
    }

    else
    {
        *out = NULL;

        class = G_SCAN_EXPRESSION_GET_CLASS(expr);

        if (class->reduce != NULL)
        {
            expr->state = class->reduce(expr, ctx, scope, out);

            if (expr->state != SRS_UNRESOLVABLE && *out == NULL)
            {
                *out = expr;
                g_object_ref(G_OBJECT(expr));
            }

        }

        else
            expr->state = SRS_UNRESOLVABLE;

#ifndef NDEBUG
        if (*out != NULL)
            assert(expr->state != SRS_UNRESOLVABLE);
#endif

    }

    assert(expr->state != SRS_PENDING);


    return expr->state;

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

bool g_scan_expression_reduce_to_boolean(GScanExpression *expr, GScanContext *ctx, GScanScope *scope, GScanExpression **out)
{
    bool result;                            /* Bilan à retourner           */
    GScanExpression *inter;                 /* Expression intermédiaire    */
    GScanExpressionClass *class;            /* Classe à activer            */

    *out = NULL;

    result = g_scan_expression_reduce(expr, ctx, scope, &inter);
    if (!result) goto exit;

    if (inter != NULL)
    {
        class = G_SCAN_EXPRESSION_GET_CLASS(inter);

        if (class->reduce_to_bool != NULL)
            result = class->reduce_to_bool(inter, ctx, scope, out);
        else
            result = false;

        g_object_unref(G_OBJECT(inter));

        /* Validation d'un type booléen */
        if (result && *out != NULL)
        {
            if (!G_IS_SCAN_LITERAL_EXPRESSION(*out))
            {
                g_clear_object(out);
                result = false;
            }

            if (g_scan_literal_expression_get_value_type(G_SCAN_LITERAL_EXPRESSION(*out)) != LVT_BOOLEAN)
            {
                g_clear_object(out);
                result = false;
            }

        }

    }

 exit:

#ifndef NDEBUG
    if (*out != NULL)
        assert(result);
#endif

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr = expression à consulter.                               *
*                                                                             *
*  Description : Détermine si l'expression peut représenter un ensemble.      *
*                                                                             *
*  Retour      : Bilan de la consultation.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_expression_handle_set_features(const GScanExpression *expr)
{
    bool result;                            /* Bilan à retourner           */
    GScanExpressionClass *class;            /* Classe à activer            */

    class = G_SCAN_EXPRESSION_GET_CLASS(expr);

    result = (class->count != NULL);

    assert((result && (class->get != NULL)) || (!result && (class->get == NULL)));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr  = expression à consulter.                              *
*                ctx   = contexte de suivi de l'analyse courante.             *
*                count = quantité d'éléments déterminée. [OUT]                *
*                                                                             *
*  Description : Dénombre les éléments portés par une expression.             *
*                                                                             *
*  Retour      : Bilan de l'opération : false en cas d'erreur irrécupérable.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_expression_count_items(const GScanExpression *expr, GScanContext *ctx, size_t *count)
{
    bool result;                            /* Bilan à retourner           */
    GScanExpressionClass *class;            /* Classe à activer            */

    *count = -1;

    class = G_SCAN_EXPRESSION_GET_CLASS(expr);

    if (class->count != NULL)
        result = class->count(expr, ctx, count);
    else
        result = false;

#ifndef NDEBUG
    if (*count != -1)
        assert(result);
#endif

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr  = expression à consulter.                              *
*                index = indice de l'élément à transférer.                    *
*                ctx   = contexte de suivi de l'analyse courante.             *
*                out   = zone d'enregistrement de la réduction opérée. [OUT]  *
*                                                                             *
*  Description : Fournit un élément donné issu d'un ensemble constitué.       *
*                                                                             *
*  Retour      : Bilan de l'opération : false en cas d'erreur irrécupérable.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_expression_get_item(const GScanExpression *expr, size_t index, GScanContext *ctx, GScanExpression **out)
{
    bool result;                            /* Bilan à retourner           */
    GScanExpressionClass *class;            /* Classe à activer            */

    *out = NULL;

    class = G_SCAN_EXPRESSION_GET_CLASS(expr);

    if (class->get != NULL)
    {
        result = class->get(expr, index, ctx, out);

        if (*out != NULL)
            g_object_ref(G_OBJECT(*out));

    }

    else
        result = false;

#ifndef NDEBUG
    if (*out != NULL)
        assert(result);
#endif

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

static GScanExpression *_g_scan_expression_intersect(GScanExpression *expr, const GScanExpression *other, GScanContext *ctx, GScanScope *scope)
{
    GScanExpression *result;                /* Instance à retourner        */
    size_t other_count;                     /* Taille du second ensemble   */
    bool valid;                             /* Bilan de validité           */
    size_t expr_count;                      /* Taille du premier ensemble  */
    size_t k;                               /* Boucle de parcours #1       */
    GComparableItem *comparable;            /* Premier élément à comparer  */
    size_t i;                               /* Boucle de parcours #2       */
    GScanExpression *item;                  /* Elément à comparer          */
    bool status;                            /* Bilan d'une comparaison     */

    result = NULL;

    valid = g_scan_expression_count_items(other, ctx, &other_count);
    if (!valid) goto done;

    /* Intersection entre deux ensembles ? */
    if (g_scan_expression_handle_set_features(expr))
    {
        valid = g_scan_expression_count_items(expr, ctx, &expr_count);
        if (!valid) goto done;

        result = g_scan_generic_set_new();

        for (k = 0; k < expr_count; k++)
        {
            valid = g_scan_expression_get_item(expr, k, ctx, &item);
            if (!valid) break;

            comparable = G_COMPARABLE_ITEM(item);

            for (i = 0; i < other_count; i++)
            {
                valid = g_scan_expression_get_item(other, i, ctx, &item);
                if (!valid) break;

                valid = g_comparable_item_compare_rich(comparable, G_COMPARABLE_ITEM(item), RCO_EQ, &status);

                if (valid && status)
                    g_scan_generic_set_add_item(G_SCAN_GENERIC_SET(result), item);

                g_object_unref(G_OBJECT(item));

            }

            g_object_unref(G_OBJECT(comparable));

        }

    }

    /* Intersection entre un élément et un ensemble */
    else
    {
        comparable = G_COMPARABLE_ITEM(expr);

        for (i = 0; i < other_count && result == NULL; i++)
        {
            valid = g_scan_expression_get_item(other, i, ctx, &item);
            if (!valid) break;

            valid = g_comparable_item_compare_rich(comparable, G_COMPARABLE_ITEM(item), RCO_EQ, &status);

            if (valid && status)
                result = g_scan_literal_expression_new(LVT_BOOLEAN, (bool []) { true });

            g_object_unref(G_OBJECT(item));

        }

        if (result && result == NULL)
            result = g_scan_literal_expression_new(LVT_BOOLEAN, (bool []) { false });

    }

 done:

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

GScanExpression *g_scan_expression_intersect(GScanExpression *expr, const GScanExpression *other, GScanContext *ctx, GScanScope *scope)
{
    GScanExpression *result;                /* Instance à retourner        */
    GScanExpressionClass *class;            /* Classe à activer            */

    class = G_SCAN_EXPRESSION_GET_CLASS(expr);

    result = class->intersect(expr, other, ctx, scope);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                         INTERFACE OFFRANT DES COMPARAISONS                         */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : item   = premier objet à cnsulter pour une comparaison.      *
*                other  = second objet à cnsulter pour une comparaison.       *
*                op     = opération de comparaison à réaliser.                *
*                status = bilan des opérations de comparaison. [OUT]          *
*                                                                             *
*  Description : Réalise une comparaison entre objets selon un critère précis.*
*                                                                             *
*  Retour      : true si la comparaison a pu être effectuée, false sinon.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_scan_expression_compare_rich(const GScanExpression *item, const GScanExpression *other, RichCmpOperation op, bool *status)
{
    bool result;                            /* Etat à retourner            */
    GScanExpressionClass *class;            /* Classe à activer            */

    class = G_SCAN_EXPRESSION_GET_CLASS(item);

    if (class->cmp_rich != NULL)
    {
        result = (G_TYPE_FROM_INSTANCE(item) == G_TYPE_FROM_INSTANCE(other));   // FIXME : subtype ? cf. literal ?

        if (result)
            result = class->cmp_rich(item, other, op, status);

    }

    else
        result = false;

    return result;

}
