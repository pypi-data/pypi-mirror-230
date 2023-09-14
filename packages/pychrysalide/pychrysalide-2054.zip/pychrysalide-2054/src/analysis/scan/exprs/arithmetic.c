
/* Chrysalide - Outil d'analyse de fichiers binaires
 * arithmetic.c - gestion des opérations arithmétiques
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


#include "arithmetic.h"


#include <assert.h>


#include "arithmetic-int.h"
#include "literal.h"



/* --------------------- INTRODUCTION D'UNE NOUVELLE EXPRESSION --------------------- */


/* Initialise la classe des opérations arithmétiques. */
static void g_scan_arithmetic_operation_class_init(GScanArithmeticOperationClass *);

/* Initialise une instance d'opération arithmétique. */
static void g_scan_arithmetic_operation_init(GScanArithmeticOperation *);

/* Supprime toutes les références externes. */
static void g_scan_arithmetic_operation_dispose(GScanArithmeticOperation *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_arithmetic_operation_finalize(GScanArithmeticOperation *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Réalise une comparaison entre objets selon un critère précis. */
static bool g_scan_arithmetic_operation_compare_rich(const GScanArithmeticOperation *, const GScanArithmeticOperation *, RichCmpOperation, bool *);

/* Réduit une expression à une forme plus simple. */
static ScanReductionState g_scan_arithmetic_operation_reduce(const GScanArithmeticOperation *, GScanContext *, GScanScope *, GScanExpression **);



/* ---------------------------------------------------------------------------------- */
/*                       INTRODUCTION D'UNE NOUVELLE EXPRESSION                       */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une opération de relation entre expressions. */
G_DEFINE_TYPE(GScanArithmeticOperation, g_scan_arithmetic_operation, G_TYPE_SCAN_EXPRESSION);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des opérations arithmétiques.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_arithmetic_operation_class_init(GScanArithmeticOperationClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GScanExpressionClass *expr;             /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_arithmetic_operation_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_arithmetic_operation_finalize;

    expr = G_SCAN_EXPRESSION_CLASS(klass);

    expr->cmp_rich = (compare_expr_rich_fc)g_scan_arithmetic_operation_compare_rich;
    expr->reduce = (reduce_expr_fc)g_scan_arithmetic_operation_reduce;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : op = instance à initialiser.                                 *
*                                                                             *
*  Description : Initialise une instance d'opération arithmétique.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_arithmetic_operation_init(GScanArithmeticOperation *op)
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

static void g_scan_arithmetic_operation_dispose(GScanArithmeticOperation *op)
{
    g_clear_object(&op->left);
    g_clear_object(&op->right);

    G_OBJECT_CLASS(g_scan_arithmetic_operation_parent_class)->dispose(G_OBJECT(op));

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

static void g_scan_arithmetic_operation_finalize(GScanArithmeticOperation *op)
{
    G_OBJECT_CLASS(g_scan_arithmetic_operation_parent_class)->finalize(G_OBJECT(op));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operator = type d'opération arithmétique à représenter.      *
*                left     = premier opérande concerné.                        *
*                right    = éventuel second opérande impliqué ou NULL.        *
*                                                                             *
*  Description : Organise une opération arithmétique entre expressions.       *
*                                                                             *
*  Retour      : Fonction mise en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanExpression *g_scan_arithmetic_operation_new(ArithmeticExpressionOperator operator, GScanExpression *left, GScanExpression *right)
{
    GScanExpression *result;                /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_ARITHMETIC_OPERATION, NULL);

    if (!g_scan_arithmetic_operation_create(G_SCAN_ARITHMETIC_OPERATION(result), operator, left, right))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : op       = instance à initialiser pleinement.                *
*                operator = type d'opération booléenne à représenter.         *
*                left     = premier opérande concerné.                        *
*                right    = éventuel second opérande impliqué ou NULL.        *
*                                                                             *
*  Description : Met en place une opération arithmétique entre expressions.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_arithmetic_operation_create(GScanArithmeticOperation *op, ArithmeticExpressionOperator operator, GScanExpression *left, GScanExpression *right)
{
    bool result;                            /* Bilan à retourner           */

    result = g_scan_expression_create(G_SCAN_EXPRESSION(op), SRS_PENDING);
    if (!result) goto exit;

    op->operator = operator;

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

static bool g_scan_arithmetic_operation_compare_rich(const GScanArithmeticOperation *item, const GScanArithmeticOperation *other, RichCmpOperation op, bool *status)
{
    bool result;                            /* Etat à retourner            */

    result = g_type_is_a(G_TYPE_FROM_INSTANCE(other), G_TYPE_SCAN_ARITHMETIC_OPERATION);
    if (!result) goto done;

    if (item->operator != other->operator)
    {
        result = compare_rich_integer_values_unsigned(item->operator, other->operator, op);
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

static ScanReductionState g_scan_arithmetic_operation_reduce(const GScanArithmeticOperation *expr, GScanContext *ctx, GScanScope *scope, GScanExpression **out)
{
    ScanReductionState result;              /* Etat synthétisé à retourner */
    GScanExpression *new_left;              /* Expression réduite (gauche) */
    GScanExpression *new_right;             /* Expression réduite (droite) */
    ScanReductionState state_left;          /* Etat synthétisé #1          */
    ScanReductionState state_right;         /* Etat synthétisé #2          */
    GScanLiteralExpression *op_left;        /* Opérande gauche final       */
    GScanLiteralExpression *op_right;       /* Opérande droite final       */
    LiteralValueType vtype_left;            /* Type de valeur portée #1    */
    LiteralValueType vtype_right;           /* Type de valeur portée #2    */
    long long val_1_s;                      /* Première valeur à traiter   */
    unsigned long long val_1_u;             /* Première valeur à traiter   */
    long long val_2_s;                      /* Seconde valeur à traiter    */
    unsigned long long val_2_u;             /* Seconde valeur à traiter    */
    LiteralValueType state_final;           /* Nature de la valeur finale  */
    long long reduced_s;                    /* Valeur réduite finale       */
    unsigned long long reduced_u;           /* Valeur réduite finale       */

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

    /* Construction d'une réduction locale ? */

    if (G_IS_SCAN_LITERAL_EXPRESSION(new_left) && G_IS_SCAN_LITERAL_EXPRESSION(new_right))
    {
        /* Récupération de l'opérande de gauche */

        op_left = G_SCAN_LITERAL_EXPRESSION(new_left);
        vtype_left = g_scan_literal_expression_get_value_type(op_left);

        if (vtype_left == LVT_SIGNED_INTEGER)
        {
            if (!g_scan_literal_expression_get_signed_integer_value(op_left, &val_1_s))
            {
                result = SRS_UNRESOLVABLE;
                goto exit;
            }
        }
        else if (vtype_left == LVT_UNSIGNED_INTEGER)
        {
            if (!g_scan_literal_expression_get_unsigned_integer_value(op_left, &val_1_u))
            {
                result = SRS_UNRESOLVABLE;
                goto exit;
            }
        }
        else
        {
            result = SRS_UNRESOLVABLE;
            goto exit;
        }

        /* Récupération de l'opérande de droite */

        op_right = G_SCAN_LITERAL_EXPRESSION(new_right);
        vtype_right = g_scan_literal_expression_get_value_type(op_right);

        if (vtype_right == LVT_SIGNED_INTEGER)
        {
            if (!g_scan_literal_expression_get_signed_integer_value(op_right, &val_2_s))
            {
                result = SRS_UNRESOLVABLE;
                goto exit;
            }
        }
        else if (vtype_right == LVT_UNSIGNED_INTEGER)
        {
            if (!g_scan_literal_expression_get_unsigned_integer_value(op_right, &val_2_u))
            {
                result = SRS_UNRESOLVABLE;
                goto exit;
            }
        }
        else
        {
            result = SRS_UNRESOLVABLE;
            goto exit;
        }

        /* Partie des calculs */

        result = SRS_REDUCED;

        switch (expr->operator)
        {
            case AEO_PLUS:
                if (vtype_left == LVT_SIGNED_INTEGER)
                {
                    if (vtype_right == LVT_SIGNED_INTEGER)
                    {
                        state_final = LVT_SIGNED_INTEGER;
                        reduced_s = val_1_s + val_2_s;
                    }
                    else
                    {
                        assert(vtype_right == LVT_UNSIGNED_INTEGER);

                        if ((long long)val_2_u > val_1_s)
                        {
                            state_final = LVT_UNSIGNED_INTEGER;
                            reduced_u = val_1_s + (long long)val_2_u;
                        }
                        else
                        {
                            state_final = LVT_SIGNED_INTEGER;
                            reduced_s = val_1_s + (long long)val_2_u;
                        }

                    }
                }
                else
                {
                    assert(vtype_left == LVT_UNSIGNED_INTEGER);

                    if (vtype_right == LVT_SIGNED_INTEGER)
                    {
                        if ((long long)val_1_u > val_2_s)
                        {
                            state_final = LVT_UNSIGNED_INTEGER;
                            reduced_u = (long long)val_1_u + val_2_s;
                        }
                        else
                        {
                            state_final = LVT_SIGNED_INTEGER;
                            reduced_s = (long long)val_1_u + val_2_s;
                        }

                    }
                    else
                    {
                        assert(vtype_right == LVT_UNSIGNED_INTEGER);

                        state_final = LVT_UNSIGNED_INTEGER;
                        reduced_u = val_1_u + val_2_u;

                    }
                }
                break;

            case AEO_MINUS:
                if (vtype_left == LVT_SIGNED_INTEGER)
                {
                    if (vtype_right == LVT_SIGNED_INTEGER)
                    {
                        if (val_2_s < val_1_s)
                        {
                            state_final = LVT_UNSIGNED_INTEGER;
                            reduced_u = val_1_s - val_2_s;
                        }
                        else
                        {
                            state_final = LVT_SIGNED_INTEGER;
                            reduced_s = val_1_s - val_2_s;
                        }

                    }
                    else
                    {
                        assert(vtype_right == LVT_UNSIGNED_INTEGER);

                        state_final = LVT_SIGNED_INTEGER;
                        reduced_s = val_1_s - (long long)val_2_u;

                    }
                }
                else
                {
                    assert(vtype_left == LVT_UNSIGNED_INTEGER);

                    if (vtype_right == LVT_SIGNED_INTEGER)
                    {
                        state_final = LVT_UNSIGNED_INTEGER;
                        reduced_u = (long long)val_1_u - val_2_s;
                    }
                    else
                    {
                        assert(vtype_right == LVT_UNSIGNED_INTEGER);

                        if (val_1_u > val_2_u)
                        {
                            state_final = LVT_UNSIGNED_INTEGER;
                            reduced_u = val_1_u - val_2_u;
                        }
                        else
                        {
                            state_final = LVT_SIGNED_INTEGER;
                            reduced_s = val_1_u - val_2_u;
                        }

                    }
                }
                break;

            case AEO_MUL:
                if (vtype_left == LVT_SIGNED_INTEGER)
                {
                    if (vtype_right == LVT_SIGNED_INTEGER)
                    {
                        state_final = LVT_UNSIGNED_INTEGER;
                        reduced_u = val_1_s * val_2_s;
                    }
                    else
                    {
                        assert(vtype_right == LVT_UNSIGNED_INTEGER);

                        state_final = LVT_SIGNED_INTEGER;
                        reduced_s = val_1_s * (long long)val_2_u;

                    }
                }
                else
                {
                    assert(vtype_left == LVT_UNSIGNED_INTEGER);

                    if (vtype_right == LVT_SIGNED_INTEGER)
                    {
                        state_final = LVT_SIGNED_INTEGER;
                        reduced_s = (long long)val_1_u * val_2_s;
                    }
                    else
                    {
                        assert(vtype_right == LVT_UNSIGNED_INTEGER);

                        state_final = LVT_UNSIGNED_INTEGER;
                        reduced_u = val_1_u * val_2_u;

                    }
                }
                break;

            case AEO_DIV:
                if ((vtype_right == LVT_SIGNED_INTEGER && val_2_s == 0)
                    || (vtype_right == LVT_UNSIGNED_INTEGER && val_2_u == 0))
                {
                    result = SRS_UNRESOLVABLE;
                    break;
                }

                if (vtype_left == LVT_SIGNED_INTEGER)
                {
                    if (vtype_right == LVT_SIGNED_INTEGER)
                    {
                        state_final = LVT_UNSIGNED_INTEGER;
                        reduced_u = val_1_s / val_2_s;
                    }
                    else
                    {
                        assert(vtype_right == LVT_UNSIGNED_INTEGER);

                        state_final = LVT_SIGNED_INTEGER;
                        reduced_s = val_1_s / (long long)val_2_u;

                    }
                }
                else
                {
                    assert(vtype_left == LVT_UNSIGNED_INTEGER);

                    if (vtype_right == LVT_SIGNED_INTEGER)
                    {
                        state_final = LVT_SIGNED_INTEGER;
                        reduced_s = (long long)val_1_u / val_2_s;
                    }
                    else
                    {
                        assert(vtype_right == LVT_UNSIGNED_INTEGER);

                        state_final = LVT_UNSIGNED_INTEGER;
                        reduced_u = val_1_u / val_2_u;

                    }
                }
                break;

            case AEO_MOD:
                result = SRS_UNRESOLVABLE;
                /* FIXME 
                result = (val_2 != 0);
                if (result)
                    reduced = val_1 % val_2;
                */
                break;

        }

        if (result == SRS_REDUCED)
        {
            if (state_final == LVT_SIGNED_INTEGER)
                *out = g_scan_literal_expression_new(LVT_SIGNED_INTEGER, &reduced_s);
            else
            {
                assert(state_final == LVT_UNSIGNED_INTEGER);
                *out = g_scan_literal_expression_new(LVT_UNSIGNED_INTEGER, &reduced_u);
            }

        }

    }

    /* Mise à jour de la progression ? */

    else if (state_left == SRS_WAIT_FOR_SCAN || state_right == SRS_WAIT_FOR_SCAN)
    {
        if (new_left != expr->left || new_right != expr->right)
            *out = g_scan_arithmetic_operation_new(expr->operator, new_left, new_right);

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
