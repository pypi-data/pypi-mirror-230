
/* Chrysalide - Outil d'analyse de fichiers binaires
 * strop.c - gestion des opérations booléennes
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


#include "strop.h"


#include <assert.h>
#include <string.h>
#include <strings.h>


#include "strop-int.h"
#include "literal.h"



/* --------------------- INTRODUCTION D'UNE NOUVELLE EXPRESSION --------------------- */


/* Initialise la classe des opérations visant des chaînes. */
static void g_scan_string_operation_class_init(GScanStringOperationClass *);

/* Initialise une instance d'opération visant une chaîne. */
static void g_scan_string_operation_init(GScanStringOperation *);

/* Supprime toutes les références externes. */
static void g_scan_string_operation_dispose(GScanStringOperation *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_string_operation_finalize(GScanStringOperation *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Réduit une expression à une forme plus simple. */
static ScanReductionState g_scan_string_operation_reduce(const GScanStringOperation *, GScanContext *, GScanScope *, GScanExpression **);



/* ---------------------------------------------------------------------------------- */
/*                       INTRODUCTION D'UNE NOUVELLE EXPRESSION                       */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une opération traitant une chaîne de caractères. */
G_DEFINE_TYPE(GScanStringOperation, g_scan_string_operation, G_TYPE_SCAN_EXPRESSION);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des opérations visant des chaînes.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_string_operation_class_init(GScanStringOperationClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GScanExpressionClass *expr;             /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_string_operation_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_string_operation_finalize;

    expr = G_SCAN_EXPRESSION_CLASS(klass);

    expr->cmp_rich = (compare_expr_rich_fc)NULL;
    expr->reduce = (reduce_expr_fc)g_scan_string_operation_reduce;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : op = instance à initialiser.                                 *
*                                                                             *
*  Description : Initialise une instance d'opération visant une chaîne.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_string_operation_init(GScanStringOperation *op)
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

static void g_scan_string_operation_dispose(GScanStringOperation *op)
{
    g_clear_object(&op->left);
    g_clear_object(&op->right);

    G_OBJECT_CLASS(g_scan_string_operation_parent_class)->dispose(G_OBJECT(op));

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

static void g_scan_string_operation_finalize(GScanStringOperation *op)
{
    G_OBJECT_CLASS(g_scan_string_operation_parent_class)->finalize(G_OBJECT(op));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type      = type d'opération booléenne à représenter.        *
*                first     = premier opérande concerné.                       *
*                second    = éventuel second opérande impliqué ou NULL.       *
*                sensitive =  détermine la prise en compte de la casse.       *
*                                                                             *
*  Description : Organise un appel de fonction avec ses arguments.            *
*                                                                             *
*  Retour      : Fonction mise en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanExpression *g_scan_string_operation_new(StringOperationType type, GScanExpression *first, GScanExpression *second, bool sensitive)
{
    GScanExpression *result;                /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_STRING_OPERATION, NULL);

    if (!g_scan_string_operation_create(G_SCAN_STRING_OPERATION(result), type, first, second, sensitive))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : op        = instance à initialiser pleinement.               *
*                type      = type d'opération booléenne à représenter.        *
*                left      = premier opérande concerné.                       *
*                right     = éventuel second opérande impliqué ou NULL.       *
*                sensitive = détermine la prise en compte de la casse.        *
*                                                                             *
*  Description : Met en place une expression d'opération traite une chaîne.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_string_operation_create(GScanStringOperation *op, StringOperationType type, GScanExpression *left, GScanExpression *right, bool sensitive)
{
    bool result;                            /* Bilan à retourner           */

    result = g_scan_expression_create(G_SCAN_EXPRESSION(op), SRS_PENDING);
    if (!result) goto exit;

    op->type = type;

    switch (type)
    {
        case SOT_CONTAINS:
        case SOT_STARTSWITH:
        case SOT_ENDSWITH:
            op->case_sensitive = sensitive;
            break;

        case SOT_MATCHES:
            break;

        case SOT_IEQUALS:
            assert(!sensitive);
            op->case_sensitive = false;
            break;

    }

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

static ScanReductionState g_scan_string_operation_reduce(const GScanStringOperation *expr, GScanContext *ctx, GScanScope *scope, GScanExpression **out)
{
    ScanReductionState result;              /* Etat synthétisé à retourner */
    GScanExpression *new_left;              /* Expression réduite (gauche) */
    GScanExpression *new_right;             /* Expression réduite (droite) */
    ScanReductionState state_left;          /* Etat synthétisé #1          */
    ScanReductionState state_right;         /* Etat synthétisé #2          */
    GScanLiteralExpression *op_left;        /* Opérande gauche final       */
    GScanLiteralExpression *op_right;       /* Opérande droite final       */
    const sized_string_t *strings[2];       /* Chaînes en jeu              */
    const void *found;                      /* Présence d'une bribe ?      */
    bool status;                            /* Bilan de comparaison #1     */
    int ret;                                /* Bilan de comparaison #2     */
    size_t offset;                          /* Point de départ d'analyse   */
    const regex_t *preg;                    /* Expression rationnelle      */

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
        op_left = G_SCAN_LITERAL_EXPRESSION(new_left);
        op_right = G_SCAN_LITERAL_EXPRESSION(new_right);

        if (!g_scan_literal_expression_get_string_value(op_left, &strings[0]))
        {
            result = SRS_UNRESOLVABLE;
            goto exit;
        }

        result = SRS_REDUCED;

        switch (expr->type)
        {
            case SOT_CONTAINS:

                if (!g_scan_literal_expression_get_string_value(op_right, &strings[1]))
                {
                    result = SRS_UNRESOLVABLE;
                    goto exit;
                }

                if (expr->case_sensitive)
                    found = memmem(strings[0]->data, strings[0]->len, strings[1]->data, strings[1]->len);

                else
                    found = memcasemem(strings[0]->data, strings[0]->len, strings[1]->data, strings[1]->len);

                *out = g_scan_literal_expression_new(LVT_BOOLEAN, (bool []) { found != NULL });
                break;

            case SOT_STARTSWITH:

                if (!g_scan_literal_expression_get_string_value(op_right, &strings[1]))
                {
                    result = SRS_UNRESOLVABLE;
                    goto exit;
                }

                if (strings[0]->len < strings[1]->len)
                    status = false;

                else
                {
                    if (expr->case_sensitive)
                        ret = memcmp(strings[0]->data, strings[1]->data, strings[1]->len);
                    else
                        ret = memcasecmp(strings[0]->data, strings[1]->data, strings[1]->len);

                    status = (ret == 0);

                }

                *out = g_scan_literal_expression_new(LVT_BOOLEAN, &status);
                break;

            case SOT_ENDSWITH:

                if (!g_scan_literal_expression_get_string_value(op_right, &strings[1]))
                {
                    result = SRS_UNRESOLVABLE;
                    goto exit;
                }

                if (strings[0]->len < strings[1]->len)
                    status = false;

                else
                {
                    offset = strings[0]->len - strings[1]->len;

                    if (expr->case_sensitive)
                        ret = memcmp(strings[0]->data + offset, strings[1]->data, strings[1]->len);
                    else
                        ret = memcasecmp(strings[0]->data + offset, strings[1]->data, strings[1]->len);

                    status = (ret == 0);

                }

                *out = g_scan_literal_expression_new(LVT_BOOLEAN, &status);
                break;

            case SOT_MATCHES:

                if (!g_scan_literal_expression_get_regex_value(op_right, &preg))
                {
                    result = SRS_UNRESOLVABLE;
                    goto exit;
                }

                ret = regexec(preg, strings[0]->data, 0, NULL, 0);

                *out = g_scan_literal_expression_new(LVT_BOOLEAN, (bool []) { ret != REG_NOMATCH });
                break;

            case SOT_IEQUALS:

                if (!g_scan_literal_expression_get_string_value(op_right, &strings[1]))
                {
                    result = SRS_UNRESOLVABLE;
                    goto exit;
                }

                if (strings[0]->len != strings[1]->len)
                    status = false;

                else
                {
                    ret = memcasecmp(strings[0]->data, strings[1]->data, strings[1]->len);
                    status = (ret == 0);
                }

                *out = g_scan_literal_expression_new(LVT_BOOLEAN, &status);
                break;

        }

    }

    /* Mise à jour de la progression ? */

    else if (state_left == SRS_WAIT_FOR_SCAN || state_right == SRS_WAIT_FOR_SCAN)
    {
        if (new_left != expr->left || new_right != expr->right)
            *out = g_scan_string_operation_new(expr->type, new_left, new_right, expr->case_sensitive);

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
