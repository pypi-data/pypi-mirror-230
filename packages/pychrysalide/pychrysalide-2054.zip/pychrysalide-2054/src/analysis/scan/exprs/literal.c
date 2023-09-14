
/* Chrysalide - Outil d'analyse de fichiers binaires
 * literal.c - représentation d'une valeur concrète
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


#include "literal.h"


#include <assert.h>
#include <stdarg.h>
#include <string.h>


#include "literal-int.h"



/* --------------------- INTRODUCTION D'UNE NOUVELLE EXPRESSION --------------------- */


/* Initialise la classe des expressions de valeur concrète. */
static void g_scan_literal_expression_class_init(GScanLiteralExpressionClass *);

/* Initialise une instance d'expression de valeur concrète. */
static void g_scan_literal_expression_init(GScanLiteralExpression *);

/* Supprime toutes les références externes. */
static void g_scan_literal_expression_dispose(GScanLiteralExpression *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_literal_expression_finalize(GScanLiteralExpression *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Réalise une comparaison entre objets selon un critère précis. */
static bool g_scan_literal_expression_compare_rich(const GScanLiteralExpression *, const GScanLiteralExpression *, RichCmpOperation, bool *);

/* Réduit une expression à une forme booléenne. */
static bool g_scan_literal_expression_reduce_to_boolean(const GScanLiteralExpression *, GScanContext *, GScanScope *, GScanExpression **);

/* Dénombre les éléments portés par une expression. */
static bool g_scan_literal_expression_count(const GScanLiteralExpression *, GScanContext *, size_t *);



/* ---------------------------------------------------------------------------------- */
/*                       INTRODUCTION D'UNE NOUVELLE EXPRESSION                       */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un appel de fonction enregistrée. */
G_DEFINE_TYPE(GScanLiteralExpression, g_scan_literal_expression, G_TYPE_SCAN_EXPRESSION);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des expressions de valeur concrète.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_literal_expression_class_init(GScanLiteralExpressionClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GScanExpressionClass *expr;             /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_literal_expression_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_literal_expression_finalize;

    expr = G_SCAN_EXPRESSION_CLASS(klass);

    expr->cmp_rich = (compare_expr_rich_fc)g_scan_literal_expression_compare_rich;
    expr->reduce_to_bool = (reduce_expr_to_bool_fc)g_scan_literal_expression_reduce_to_boolean;
    expr->count = (count_scan_expr_fc)g_scan_literal_expression_count;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance d'expression de valeur concrète.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_literal_expression_init(GScanLiteralExpression *expr)
{
    G_SCAN_EXPRESSION(expr)->state = SRS_REDUCED;

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

static void g_scan_literal_expression_dispose(GScanLiteralExpression *expr)
{
    G_OBJECT_CLASS(g_scan_literal_expression_parent_class)->dispose(G_OBJECT(expr));

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

static void g_scan_literal_expression_finalize(GScanLiteralExpression *expr)
{
    G_OBJECT_CLASS(g_scan_literal_expression_parent_class)->finalize(G_OBJECT(expr));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : vtype = type de valeur associée par l'expression.            *
*                ...   = valeur concrête à intégrer.                          *
*                                                                             *
*  Description : Organise un appel de fonction avec ses arguments.            *
*                                                                             *
*  Retour      : Expression mise en place.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanExpression *g_scan_literal_expression_new(LiteralValueType vtype, ...)
{
    GScanExpression *result;                /* Structure à retourner       */
    va_list ap;                             /* Liste d'arguements          */
    void *ptr;                              /* Vision générique de valeur  */

    result = g_object_new(G_TYPE_SCAN_LITERAL_EXPRESSION, NULL);

    va_start(ap, vtype);

    ptr = va_arg(ap, void *);

    if (!g_scan_literal_expression_create(G_SCAN_LITERAL_EXPRESSION(result), vtype, ptr))
        g_clear_object(&result);

    va_end(ap);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr  = instance à initialiser pleinement.                   *
*                vtype = type de valeur associée par l'expression.            *
*                ...   = valeur concrête à intégrer.                          *
*                                                                             *
*  Description : Met en place une expression de valeur concrête.              *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_literal_expression_create(GScanLiteralExpression *expr, LiteralValueType vtype, ...)
{
    bool result;                            /* Bilan à retourner           */
    va_list ap;                             /* Liste d'arguements          */
    const bool *boolean;                    /* Valeur booléenne            */
    const long long *s_integer;             /* Valeur entière 64 bits #1   */
    const unsigned long long *u_integer;    /* Valeur entière 64 bits #2   */
    const sized_string_t *string;           /* Chaîne de caractères        */
    const char *raw;                        /* Chaîne de caractères brute  */
    size_t len;                             /* Taille de la chaîne         */
    int cflags;                             /* Détails de compilation      */
    unsigned int i;                         /* Boucle de parcours          */
    char *tmp;                              /* Zone de travail temporaire  */
    int ret;                                /* Bilan d'une opération       */

    result = g_scan_expression_create(G_SCAN_EXPRESSION(expr), SRS_REDUCED);
    if (!result) goto exit;

    va_start(ap, vtype);

    switch (vtype)
    {
        case LVT_BOOLEAN:
            boolean = va_arg(ap, const bool *);
            expr->value.boolean = *boolean;
            result = true;
            break;

        case LVT_SIGNED_INTEGER:
            s_integer = va_arg(ap, const long long *);
            expr->value.s_integer = *s_integer;
            result = true;
            break;

        case LVT_UNSIGNED_INTEGER:
            u_integer = va_arg(ap, const unsigned long long *);
            expr->value.u_integer = *u_integer;
            result = true;
            break;

        case LVT_STRING:
            string = va_arg(ap, const sized_string_t *);
            szstrdup(&expr->value.string, string);
            result = true;
            break;

        case LVT_REG_EXPR:
            raw = va_arg(ap, const char *);
            len = strlen(raw);

            result = (len > 2 && raw[0] == '/');

            cflags = REG_EXTENDED | REG_NOSUB;

            for (i = 0; i < 2 && result; i++)
            {
                result = (len > 2);

                if (raw[len - 1] == 'i')
                {
                    cflags |= REG_ICASE;
                    len -= 1;
                }

                else if (raw[len - 1] == 's')
                {
                    cflags |= REG_NEWLINE;
                    len -= 1;
                }

                else if (raw[len - 1] == '/')
                    break;

            }

            if (result)
                result = (raw[len - 1] == '/');

            if (result)
            {
                assert(len > 2);

                tmp = strndup(&raw[1], len - 2);
                ret = regcomp(&expr->value.preg, tmp, cflags);
                free(tmp);

                result = (ret == 0);

                if (result)
                    expr->value.regex = strdup(raw);

            }

            break;

        default:
            result = false;
            break;

        }

    va_end(ap);

    expr->value_type = vtype;

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr = expression à consulter.                               *
*                                                                             *
*  Description : Indique le type de valeur portée par une expression.         *
*                                                                             *
*  Retour      : Type de valeur associée à l'expression.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

LiteralValueType g_scan_literal_expression_get_value_type(const GScanLiteralExpression *expr)
{
    LiteralValueType result;                /* Type à retourner            */

    result = expr->value_type;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr  = premier objet à consulter pour une comparaison.      *
*                value = valeur portée portée par l'expression. [OUT]         *
*                                                                             *
*  Description : Indique la valeur portée par une expression booléenne.       *
*                                                                             *
*  Retour      : true si l'expression est de type booléen, false sinon.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_literal_expression_get_boolean_value(const GScanLiteralExpression *expr, bool *value)
{
    bool result;                            /* Etat à retourner            */

    result = (expr->value_type == LVT_BOOLEAN);

    if (result)
        *value = expr->value.boolean;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr  = premier objet à consulter pour une comparaison.      *
*                value = valeur portée portée par l'expression. [OUT]         *
*                                                                             *
*  Description : Indique la valeur portée par une expression d'entier.        *
*                                                                             *
*  Retour      : true si l'expression est de type entier, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_literal_expression_get_signed_integer_value(const GScanLiteralExpression *expr, long long *value)
{
    bool result;                            /* Etat à retourner            */

    result = (expr->value_type == LVT_SIGNED_INTEGER);

    if (result)
        *value = expr->value.u_integer;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr  = premier objet à consulter pour une comparaison.      *
*                value = valeur portée portée par l'expression. [OUT]         *
*                                                                             *
*  Description : Indique la valeur portée par une expression d'entier.        *
*                                                                             *
*  Retour      : true si l'expression est de type entier, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_literal_expression_get_unsigned_integer_value(const GScanLiteralExpression *expr, unsigned long long *value)
{
    bool result;                            /* Etat à retourner            */

    result = (expr->value_type == LVT_UNSIGNED_INTEGER);

    if (result)
        *value = expr->value.u_integer;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr  = premier objet à consulter pour une comparaison.      *
*                value = valeur portée portée par l'expression. [OUT]         *
*                                                                             *
*  Description : Indique la valeur portée par une expression de chaîne.       *
*                                                                             *
*  Retour      : true si l'expression est de type entier, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_literal_expression_get_string_value(const GScanLiteralExpression *expr, const sized_string_t **value)
{
    bool result;                            /* Etat à retourner            */

    result = (expr->value_type == LVT_STRING);

    if (result)
        *value = &expr->value.string;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr  = premier objet à consulter pour une comparaison.      *
*                value = valeur portée portée par l'expression. [OUT]         *
*                                                                             *
*  Description : Indique la valeur portée par une expression rationnelle.     *
*                                                                             *
*  Retour      : true si l'expression est de type entier, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_literal_expression_get_regex_value(const GScanLiteralExpression *expr, const regex_t **value)
{
    bool result;                            /* Etat à retourner            */

    result = (expr->value_type == LVT_REG_EXPR);

    if (result)
        *value = &expr->value.preg;

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : expr   = premier objet à consulter pour une comparaison.     *
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

static bool g_scan_literal_expression_compare_rich(const GScanLiteralExpression *expr, const GScanLiteralExpression *other, RichCmpOperation op, bool *status)
{
    bool result;                            /* Etat à retourner            */
    int cmp;                                /* Bilan intermédiaire         */

    result = g_type_is_a(G_TYPE_FROM_INSTANCE(other), G_TYPE_SCAN_LITERAL_EXPRESSION);
    if (!result) goto done;

    if (expr->value_type != other->value_type)
    {
        *status = compare_rich_integer_values_unsigned(expr->value_type, other->value_type, op);
        goto done;
    }

    switch (expr->value_type)
    {
        case LVT_BOOLEAN:
            switch (op)
            {
                case RCO_EQ:
                    *status = (expr->value.boolean == other->value.boolean);
                    result = true;
                    break;

                case RCO_NE:
                    *status = (expr->value.boolean != other->value.boolean);
                    result = true;
                    break;

                default:
                    result = false;
                    break;

            };
            break;

        case LVT_SIGNED_INTEGER:
            *status = compare_rich_integer_values_signed(expr->value.s_integer, other->value.s_integer, op);
            result = true;
            break;

        case LVT_UNSIGNED_INTEGER:
            *status = compare_rich_integer_values_unsigned(expr->value.u_integer, other->value.u_integer, op);
            result = true;
            break;

        case LVT_STRING:
            cmp = szstrcmp(&expr->value.string, &other->value.string);
            *status = compare_rich_integer_values_signed(cmp, 0, op);
            result = true;
            break;

        case LVT_REG_EXPR:
            cmp = strcmp(expr->value.regex, other->value.regex);
            *status = compare_rich_integer_values_signed(cmp, 0, op);
            result = true;
            break;

        default:
            result = false;
            break;

    }

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
*  Description : Réduit une expression à une forme booléenne.                 *
*                                                                             *
*  Retour      : Bilan de l'opération : false en cas d'erreur irrécupérable.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_scan_literal_expression_reduce_to_boolean(const GScanLiteralExpression *expr, GScanContext *ctx, GScanScope *scope, GScanExpression **out)
{
    bool result;                            /* Bilan à retourner           */

    switch (expr->value_type)
    {
        case LVT_BOOLEAN:
            *out = G_SCAN_EXPRESSION(expr);
            g_object_ref(G_OBJECT(expr));
            result = true;
            break;

        case LVT_SIGNED_INTEGER:
            *out = g_scan_literal_expression_new(LVT_BOOLEAN, (bool []){ expr->value.s_integer != 0 });
            result = true;
            break;

        case LVT_UNSIGNED_INTEGER:
            *out = g_scan_literal_expression_new(LVT_BOOLEAN, (bool []){ expr->value.u_integer != 0 });
            result = true;
            break;

        case LVT_STRING:
            *out = g_scan_literal_expression_new(LVT_BOOLEAN, (bool []){ expr->value.string.len > 0 });
            result = true;
            break;

        default:
            result = false;
            break;

    }

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

static bool g_scan_literal_expression_count(const GScanLiteralExpression *expr, GScanContext *ctx, size_t *count)
{
    bool result;                            /* Bilan à retourner           */

    switch (expr->value_type)
    {
        case LVT_STRING:
            *count = expr->value.string.len;
            result = true;
            break;

        default:
            result = false;
            break;

    }

    return result;

}
