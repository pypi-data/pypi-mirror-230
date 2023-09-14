
/* Chrysalide - Outil d'analyse de fichiers binaires
 * relational.c - gestion des opérations relationnelles
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


#include "relational.h"


#include <assert.h>


#include "relational-int.h"
#include "literal.h"



/* --------------------- INTRODUCTION D'UNE NOUVELLE EXPRESSION --------------------- */


/* Initialise la classe des opérations de relations. */
static void g_scan_relational_operation_class_init(GScanRelationalOperationClass *);

/* Initialise une instance d'opération de relation. */
static void g_scan_relational_operation_init(GScanRelationalOperation *);

/* Supprime toutes les références externes. */
static void g_scan_relational_operation_dispose(GScanRelationalOperation *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_relational_operation_finalize(GScanRelationalOperation *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Réalise une comparaison entre objets selon un critère précis. */
static bool g_scan_relational_operation_compare_rich(const GScanRelationalOperation *, const GScanRelationalOperation *, RichCmpOperation, bool *);

/* Réduit une expression à une forme plus simple. */
static ScanReductionState g_scan_relational_operation_reduce(const GScanRelationalOperation *, GScanContext *, GScanScope *, GScanExpression **);



/* ---------------------------------------------------------------------------------- */
/*                       INTRODUCTION D'UNE NOUVELLE EXPRESSION                       */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une opération de relation entre expressions. */
G_DEFINE_TYPE(GScanRelationalOperation, g_scan_relational_operation, G_TYPE_SCAN_EXPRESSION);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des opérations de relations.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_relational_operation_class_init(GScanRelationalOperationClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GScanExpressionClass *expr;             /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_relational_operation_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_relational_operation_finalize;

    expr = G_SCAN_EXPRESSION_CLASS(klass);

    expr->cmp_rich = (compare_expr_rich_fc)g_scan_relational_operation_compare_rich;
    expr->reduce = (reduce_expr_fc)g_scan_relational_operation_reduce;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : op = instance à initialiser.                                 *
*                                                                             *
*  Description : Initialise une instance d'opération de relation.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_relational_operation_init(GScanRelationalOperation *op)
{
    op->left = NULL;
    op->right = NULL;

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

static void g_scan_relational_operation_dispose(GScanRelationalOperation *op)
{
    g_clear_object(&op->left);
    g_clear_object(&op->right);

    G_OBJECT_CLASS(g_scan_relational_operation_parent_class)->dispose(G_OBJECT(op));

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

static void g_scan_relational_operation_finalize(GScanRelationalOperation *op)
{
    G_OBJECT_CLASS(g_scan_relational_operation_parent_class)->finalize(G_OBJECT(op));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type  = type d'opération booléenne à représenter.            *
*                left  = premier opérande concerné.                           *
*                right = éventuel second opérande impliqué ou NULL.           *
*                                                                             *
*  Description : Organise une opération relationnelle entre expressions.      *
*                                                                             *
*  Retour      : Fonction mise en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanExpression *g_scan_relational_operation_new(RichCmpOperation type, GScanExpression *left, GScanExpression *right)
{
    GScanExpression *result;                /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_RELATIONAL_OPERATION, NULL);

    if (!g_scan_relational_operation_create(G_SCAN_RELATIONAL_OPERATION(result), type, left, right))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : op    = instance à initialiser pleinement.                   *
*                type  = type d'opération booléenne à représenter.            *
*                left  = premier opérande concerné.                           *
*                right = éventuel second opérande impliqué ou NULL.           *
*                                                                             *
*  Description : Met en place une opération relationnelle entre expressions.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_relational_operation_create(GScanRelationalOperation *op, RichCmpOperation type, GScanExpression *left, GScanExpression *right)
{
    bool result;                            /* Bilan à retourner           */

    result = g_scan_expression_create(G_SCAN_EXPRESSION(op), SRS_PENDING);
    if (!result) goto exit;

    op->rel_type = type;

    op->left = left;
    g_object_ref(G_OBJECT(op->left));

    op->right = right;
    g_object_ref(G_OBJECT(op->right));

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

static bool g_scan_relational_operation_compare_rich(const GScanRelationalOperation *item, const GScanRelationalOperation *other, RichCmpOperation op, bool *status)
{
    bool result;                            /* Etat à retourner            */

    result = g_type_is_a(G_TYPE_FROM_INSTANCE(other), G_TYPE_SCAN_RELATIONAL_OPERATION);
    if (!result) goto done;

    if (item->rel_type != other->rel_type)
    {
        *status = compare_rich_integer_values_unsigned(item->rel_type, other->rel_type, op);
        goto done;
    }

    result = g_comparable_item_compare_rich(G_COMPARABLE_ITEM(item), G_COMPARABLE_ITEM(other), RCO_EQ, status);
    if (!result || STATUS_NOT_EQUAL(*status, op)) goto done;

    result = g_comparable_item_compare_rich(G_COMPARABLE_ITEM(item->left),
                                            G_COMPARABLE_ITEM(other->left),
                                            op, status);
    if (!result || STATUS_NOT_EQUAL(*status, op)) goto done;

    result = g_comparable_item_compare_rich(G_COMPARABLE_ITEM(item->right),
                                            G_COMPARABLE_ITEM(other->right),
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

static ScanReductionState g_scan_relational_operation_reduce(const GScanRelationalOperation *expr, GScanContext *ctx, GScanScope *scope, GScanExpression **out)
{
    ScanReductionState result;              /* Etat synthétisé à retourner */
    GScanExpression *new_left;              /* Expression réduite (gauche) */
    GScanExpression *new_right;             /* Expression réduite (droite) */
    ScanReductionState state_left;          /* Etat synthétisé #1          */
    ScanReductionState state_right;         /* Etat synthétisé #2          */
    LiteralValueType vtype_left;            /* Type de valeur portée #1    */
    LiteralValueType vtype_right;           /* Type de valeur portée #2    */
    GScanExpression *casted;                /* Nouvelle forme en booléen   */
    bool status;                            /* Bilan d'une comparaison     */
    bool valid;                             /* Validité de ce bilan obtenu */

    /* Réduction des éléments considérés */

    new_left = NULL;
    new_right = NULL;

    state_left = g_scan_expression_reduce(expr->left, ctx, scope, &new_left);
    if (state_left == SRS_UNRESOLVABLE)
    {
        result = SRS_UNRESOLVABLE;
        goto exit;
    }

    state_right = g_scan_expression_reduce(expr->right, ctx, scope, &new_right);
    if (state_right == SRS_UNRESOLVABLE)
    {
        result = SRS_UNRESOLVABLE;
        goto exit;
    }

    /* Transtypage vers des booléens imposé ? */

    if (expr->rel_type == RCO_EQ || expr->rel_type == RCO_NE)
    {
        if (G_IS_SCAN_LITERAL_EXPRESSION(new_left))
        {
            vtype_left = g_scan_literal_expression_get_value_type(G_SCAN_LITERAL_EXPRESSION(new_left));

            if (vtype_left == LVT_BOOLEAN)
            {
                if (g_scan_expression_reduce_to_boolean(new_right, ctx, scope, &casted))
                {
                    g_object_unref(G_OBJECT(new_right));
                    new_right = casted;
                }
            }

        }

        if (G_IS_SCAN_LITERAL_EXPRESSION(new_right))
        {
            vtype_right = g_scan_literal_expression_get_value_type(G_SCAN_LITERAL_EXPRESSION(new_right));

            if (vtype_right == LVT_BOOLEAN)
            {
                if (g_scan_expression_reduce_to_boolean(new_left, ctx, scope, &casted))
                {
                    g_object_unref(G_OBJECT(new_left));
                    new_left = casted;
                }
            }

        }

    }

    /* Construction d'une réduction locale ? */

    if (G_IS_SCAN_LITERAL_EXPRESSION(new_left) && G_IS_SCAN_LITERAL_EXPRESSION(new_right))
    {
        valid = g_comparable_item_compare_rich(G_COMPARABLE_ITEM(new_left),
                                               G_COMPARABLE_ITEM(new_right),
                                               expr->rel_type, &status);

        if (valid)
        {
            *out = g_scan_literal_expression_new(LVT_BOOLEAN, (bool []) { status });
            result = SRS_REDUCED;
        }
        else
            result = SRS_UNRESOLVABLE;

    }

    /* Mise à jour de la progression ? */

    else if (state_left == SRS_WAIT_FOR_SCAN || state_right == SRS_WAIT_FOR_SCAN)
    {
        if (new_left != expr->left || new_right != expr->right)
            *out = g_scan_relational_operation_new(expr->rel_type, new_left, new_right);

        result = SRS_WAIT_FOR_SCAN;

    }

    /* Cas des situations où les expressions ne sont pas exploitables (!) */
    else
    {
        assert(state_left == SRS_REDUCED && state_right == SRS_REDUCED);

        result = SRS_UNRESOLVABLE;

    }

    /* Sortie propre */

 exit:

    g_clear_object(&new_left);
    g_clear_object(&new_right);

    return result;

}
