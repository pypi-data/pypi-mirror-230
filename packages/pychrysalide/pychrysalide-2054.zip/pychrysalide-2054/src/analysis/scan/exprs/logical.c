
/* Chrysalide - Outil d'analyse de fichiers binaires
 * logical.c - gestion des opérations booléennes
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


#include "logical.h"


#include <assert.h>


#include "logical-int.h"
#include "literal.h"



/* --------------------- INTRODUCTION D'UNE NOUVELLE EXPRESSION --------------------- */


/* Initialise la classe des opérations booléennes. */
static void g_scan_logical_operation_class_init(GScanLogicalOperationClass *);

/* Initialise une instance d'opération booléenne. */
static void g_scan_logical_operation_init(GScanLogicalOperation *);

/* Supprime toutes les références externes. */
static void g_scan_logical_operation_dispose(GScanLogicalOperation *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_logical_operation_finalize(GScanLogicalOperation *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Réalise une comparaison entre objets selon un critère précis. */
static bool g_scan_logical_operation_compare_rich(const GScanLogicalOperation *, const GScanLogicalOperation *, RichCmpOperation, bool *);

/* Réduit une expression à une forme plus simple. */
static ScanReductionState g_scan_logical_operation_reduce(const GScanLogicalOperation *, GScanContext *, GScanScope *, GScanExpression **);



/* ---------------------------------------------------------------------------------- */
/*                       INTRODUCTION D'UNE NOUVELLE EXPRESSION                       */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une opération booléenne sur expression(s). */
G_DEFINE_TYPE(GScanLogicalOperation, g_scan_logical_operation, G_TYPE_SCAN_EXPRESSION);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des opérations booléennes.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_logical_operation_class_init(GScanLogicalOperationClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GScanExpressionClass *expr;             /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_logical_operation_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_logical_operation_finalize;

    expr = G_SCAN_EXPRESSION_CLASS(klass);

    expr->cmp_rich = (compare_expr_rich_fc)g_scan_logical_operation_compare_rich;
    expr->reduce = (reduce_expr_fc)g_scan_logical_operation_reduce;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : op = instance à initialiser.                                 *
*                                                                             *
*  Description : Initialise une instance d'opération booléenne.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_logical_operation_init(GScanLogicalOperation *op)
{
    op->first = NULL;
    op->second = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : op = instance d'objet GLib à traiter.                        *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_logical_operation_dispose(GScanLogicalOperation *op)
{
    g_clear_object(&op->first);
    g_clear_object(&op->second);

    G_OBJECT_CLASS(g_scan_logical_operation_parent_class)->dispose(G_OBJECT(op));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : op = instance d'objet GLib à traiter.                        *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_logical_operation_finalize(GScanLogicalOperation *op)
{
    G_OBJECT_CLASS(g_scan_logical_operation_parent_class)->finalize(G_OBJECT(op));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type   = type d'opération booléenne à représenter.           *
*                first  = premier opérande concerné.                          *
*                second = éventuel second opérande impliqué ou NULL.          *
*                                                                             *
*  Description : Organise un appel de fonction avec ses arguments.            *
*                                                                             *
*  Retour      : Fonction mise en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanExpression *g_scan_logical_operation_new(BooleanOperationType type, GScanExpression *first, GScanExpression *second)
{
    GScanExpression *result;                /* Structure à retourner       */

    result = g_object_new(G_TYPE_BOOLEAN_OPERATION, NULL);

    if (!g_scan_logical_operation_create(G_SCAN_LOGICAL_OPERATION(result), type, first, second))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr   = instance à initialiser pleinement.                  *
*                type   = type d'opération booléenne à représenter.           *
*                first  = premier opérande concerné.                          *
*                second = éventuel second opérande impliqué ou NULL.          *
*                                                                             *
*  Description : Met en place une expression d'opération booléenne.           *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_logical_operation_create(GScanLogicalOperation *op, BooleanOperationType type, GScanExpression *first, GScanExpression *second)
{
    bool result;                            /* Bilan à retourner           */

    result = g_scan_expression_create(G_SCAN_EXPRESSION(op), SRS_PENDING);
    if (!result) goto exit;

    op->type = type;

    switch (type)
    {
        case BOT_AND:
        case BOT_OR:
            op->first = first;
            g_object_ref(G_OBJECT(op->first));

            op->second = second;
            g_object_ref(G_OBJECT(op->second));

            result = true;
            break;

        case BOT_NOT:
            op->first = first;
            g_object_ref(G_OBJECT(op->first));

            result = (second == NULL);
            assert(second != NULL);
            break;

        default:
            result = false;
            break;

    }

 exit:

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : item   = premier objet à consulter pour une comparaison.     *
*                other  = second objet à consulter pour une comparaison.      *
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

static bool g_scan_logical_operation_compare_rich(const GScanLogicalOperation *item, const GScanLogicalOperation *other, RichCmpOperation op, bool *status)
{
    bool result;                            /* Etat à retourner            */

    result = g_type_is_a(G_TYPE_FROM_INSTANCE(other), G_TYPE_BOOLEAN_OPERATION);
    if (!result) goto done;

    if (item->type != other->type)
    {
        *status = compare_rich_integer_values_unsigned(item->type, other->type, op);
        goto done;
    }

    result = g_comparable_item_compare_rich(G_COMPARABLE_ITEM(item), G_COMPARABLE_ITEM(other), RCO_EQ, status);
    if (!result || STATUS_NOT_EQUAL(*status, op)) goto done;

    result = g_comparable_item_compare_rich(G_COMPARABLE_ITEM(item->first),
                                            G_COMPARABLE_ITEM(other->first),
                                            op, status);
    if (!result || STATUS_NOT_EQUAL(*status, op)) goto done;

    if (item->second == NULL)
    {
        assert(other->second == NULL);

        switch (op)
        {
            case RCO_LT:
            case RCO_NE:
            case RCO_GT:
                *status = false;
                break;

            case RCO_LE:
            case RCO_EQ:
            case RCO_GE:
                *status = true;
                break;

        }

    }

    else
        result = g_comparable_item_compare_rich(G_COMPARABLE_ITEM(item->second),
                                                G_COMPARABLE_ITEM(other->second),
                                                op, status);

 done:

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

static ScanReductionState g_scan_logical_operation_reduce(const GScanLogicalOperation *expr, GScanContext *ctx, GScanScope *scope, GScanExpression **out)
{
    ScanReductionState result;              /* Etat synthétisé à retourner */
    GScanExpression *new_first;             /* Expression réduite (gauche) */
    ScanReductionState state[2];            /* Bilan de sous-réductons     */
    GScanExpression *new_second;            /* Expression réduite (droite) */
    GScanExpression *bool_operands[2];      /* Expressions booléennes      */
    bool values[2];                         /* Valeurs des éléments portés */
    bool valid[2];                          /* Validité de ces valeurs     */

    /* Réduction des éléments considérés */

    state[0] = g_scan_expression_reduce(expr->first, ctx, scope, &new_first);

    if (expr->second != NULL)
        state[1] = g_scan_expression_reduce(expr->second, ctx, scope, &new_second);
    else
    {
        new_second = NULL;
        state[1] = SRS_REDUCED;
    }

    /* Récupération des valeurs booléennes */

    if (new_first != NULL)
    {
        valid[0] = g_scan_expression_reduce_to_boolean(new_first, ctx, scope, &bool_operands[0]);

        if (valid[0])
            valid[0] = g_scan_literal_expression_get_boolean_value(G_SCAN_LITERAL_EXPRESSION(bool_operands[0]),
                                                                   &values[0]);
        else
            bool_operands[0] = NULL;

    }
    else
    {
        bool_operands[0] = NULL;
        valid[0] = false;
    }

    if (new_second != NULL)
    {
        valid[1] = g_scan_expression_reduce_to_boolean(new_second, ctx, scope, &bool_operands[1]);

        if (valid[1])
            valid[1] = g_scan_literal_expression_get_boolean_value(G_SCAN_LITERAL_EXPRESSION(bool_operands[1]),
                                                                   &values[1]);
        else
            bool_operands[1] = NULL;

    }
    else
    {
        bool_operands[1] = NULL;
        valid[1] = false;
    }

    /* Construction d'une réduction locale ? */

    switch (expr->type)
    {
        case BOT_AND:
            if (valid[0] && valid[1])
            {
                *out = g_scan_literal_expression_new(LVT_BOOLEAN, (bool []) { values[0] && values[1] });
                result = SRS_REDUCED;
            }

            else if (valid[0] && !values[0])
            {
                *out = g_scan_literal_expression_new(LVT_BOOLEAN, (bool []) { false });
                result = SRS_REDUCED;
            }

            else if (valid[1] && !values[1])
            {
                *out = g_scan_literal_expression_new(LVT_BOOLEAN, (bool []) { false });
                result = SRS_REDUCED;
            }

            else
            {
                if (state[0] == SRS_UNRESOLVABLE || state[1] == SRS_UNRESOLVABLE)
                    result = SRS_UNRESOLVABLE;
                else
                {
                    assert(state[0] == SRS_WAIT_FOR_SCAN || state[1] == SRS_WAIT_FOR_SCAN);
                    result = SRS_WAIT_FOR_SCAN;
                }
            }

            break;

        case BOT_OR:
            if (valid[0] && valid[1])
            {
                *out = g_scan_literal_expression_new(LVT_BOOLEAN, (bool []) { values[0] || values[1] });
                result = SRS_REDUCED;
            }

            else if (valid[0] && values[0])
            {
                *out = g_scan_literal_expression_new(LVT_BOOLEAN, (bool []) { true });
                result = SRS_REDUCED;
            }

            else if (valid[1] && values[1])
            {
                *out = g_scan_literal_expression_new(LVT_BOOLEAN, (bool []) { true });
                result = SRS_REDUCED;
            }

            else
            {
                if (state[0] == SRS_UNRESOLVABLE || state[1] == SRS_UNRESOLVABLE)
                    result = SRS_UNRESOLVABLE;
                else
                {
                    assert(state[0] == SRS_WAIT_FOR_SCAN || state[1] == SRS_WAIT_FOR_SCAN);
                    result = SRS_WAIT_FOR_SCAN;
                }
            }

            break;

        case BOT_NOT:
            if (valid[0])
            {
                *out = g_scan_literal_expression_new(LVT_BOOLEAN, (bool []) { !values[0] });
                result = SRS_REDUCED;
            }

            else
            {
                if (state[0] == SRS_UNRESOLVABLE)
                    result = SRS_UNRESOLVABLE;
                else
                {
                    assert(state[0] == SRS_WAIT_FOR_SCAN);
                    result = SRS_WAIT_FOR_SCAN;
                }
            }

            break;

    }

    /* Mise à jour de la progression ? */

    if (result == SRS_WAIT_FOR_SCAN)
    {
        if (new_first != expr->first || new_second != expr->second)
        {
            assert(new_first != NULL);
            assert(new_second != NULL || expr->second == NULL);

            *out = g_scan_logical_operation_new(expr->type, new_first, new_second);

        }

    }

    /* Sortie propre */

    g_clear_object(&bool_operands[0]);
    g_clear_object(&bool_operands[1]);

    g_clear_object(&new_first);
    g_clear_object(&new_second);

    return result;

}
