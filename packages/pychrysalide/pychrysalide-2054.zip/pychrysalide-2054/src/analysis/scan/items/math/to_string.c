
/* Chrysalide - Outil d'analyse de fichiers binaires
 * to_string.c - conversion d'une valeur entière en chaîne
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


#include "to_string.h"


#include <assert.h>
#include <stdlib.h>


#include "../../item-int.h"
#include "../../exprs/literal.h"



/* ---------------------- INTRODUCTION D'UNE NOUVELLE FONCTION ---------------------- */


/* Initialise la classe des conversions de texte en entier. */
static void g_scan_math_to_string_function_class_init(GScanMathToStringFunctionClass *);

/* Initialise une instance de conversion de texte en entier. */
static void g_scan_math_to_string_function_init(GScanMathToStringFunction *);

/* Supprime toutes les références externes. */
static void g_scan_math_to_string_function_dispose(GScanMathToStringFunction *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_math_to_string_function_finalize(GScanMathToStringFunction *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Indique le nom associé à une expression d'évaluation. */
static char *g_scan_math_to_string_function_get_name(const GScanMathToStringFunction *);

/* Réalise la conversion d'une valeur en texte. */
static void convert_integer_to_string(unsigned long long, unsigned long long, char **);

/* Réduit une expression à une forme plus simple. */
static bool g_scan_math_to_string_function_run_call(GScanMathToStringFunction *, GScanExpression **, size_t, GScanContext *, GScanScope *, GObject **);



/* ---------------------------------------------------------------------------------- */
/*                        INTRODUCTION D'UNE NOUVELLE FONCTION                        */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une conversion d'entier en texte. */
G_DEFINE_TYPE(GScanMathToStringFunction, g_scan_math_to_string_function, G_TYPE_REGISTERED_ITEM);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des conversions de texte en entier.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_math_to_string_function_class_init(GScanMathToStringFunctionClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GRegisteredItemClass *registered;       /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_math_to_string_function_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_math_to_string_function_finalize;

    registered = G_REGISTERED_ITEM_CLASS(klass);

    registered->get_name = (get_registered_item_name_fc)g_scan_math_to_string_function_get_name;
    registered->run_call = (run_registered_item_call_fc)g_scan_math_to_string_function_run_call;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : func = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance de conversion de texte en entier.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_math_to_string_function_init(GScanMathToStringFunction *func)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : func = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_math_to_string_function_dispose(GScanMathToStringFunction *func)
{
    G_OBJECT_CLASS(g_scan_math_to_string_function_parent_class)->dispose(G_OBJECT(func));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : func = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_math_to_string_function_finalize(GScanMathToStringFunction *func)
{
    G_OBJECT_CLASS(g_scan_math_to_string_function_parent_class)->finalize(G_OBJECT(func));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée une fonction de conversion de valeur entière en texte.  *
*                                                                             *
*  Retour      : Fonction mise en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GRegisteredItem *g_scan_math_to_string_function_new(void)
{
    GRegisteredItem *result;                /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_MATH_TO_STRING_FUNCTION, NULL);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : item = élément d'appel à consulter.                          *
*                                                                             *
*  Description : Indique le nom associé à une expression d'évaluation.        *
*                                                                             *
*  Retour      : Désignation humaine de l'expression d'évaluation.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_scan_math_to_string_function_get_name(const GScanMathToStringFunction *item)
{
    char *result;                           /* Désignation à retourner     */

    result = strdup("to_string");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : val  = valeur entière à traiter.                             *
*                base = base à considérer.                                    *
*                data = tête d'écriture à faire évoluer. [OUT]                *
*                                                                             *
*  Description : Réalise la conversion d'une valeur en texte.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void convert_integer_to_string(unsigned long long val, unsigned long long base, char **data)
{
    static const char digits[16] = "0123456789abcdef";

    if (val < base)
        *((*data)++) = digits[val];

    else
    {
        convert_integer_to_string(val / base, base, data);

        *((*data)++) = digits[val % base];

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item  = élément d'appel à consulter.                         *
*                args  = liste d'éventuels arguments fournis.                 *
*                count = taille de cette liste.                               *
*                ctx   = contexte de suivi de l'analyse courante.             *
*                scope = portée courante des variables locales.               *
*                out   = zone d'enregistrement de la résolution opérée. [OUT] *
*                                                                             *
*  Description : Réduit une expression à une forme plus simple.               *
*                                                                             *
*  Retour      : Réduction correspondante, expression déjà réduite, ou NULL.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_scan_math_to_string_function_run_call(GScanMathToStringFunction *item, GScanExpression **args, size_t count, GScanContext *ctx, GScanScope *scope, GObject **out)
{
    bool result;                            /* Bilan à retourner           */
    GScanLiteralExpression *literal;        /* Version plus accessible     */
    LiteralValueType vtype;                 /* Type de valeur portée       */
    long long sval;                         /* Valeur signée obtenue       */
    unsigned long long uval;                /* Valeur non signée obtenue   */
    bool negative;                          /* Besoin de signe en préfixe ?*/
    unsigned long long base;                /* Base de conversion          */
    char *data;                             /* Chaîne "C" à constituer     */
    char *iter;                             /* Tête d'écriture             */
    sized_string_t string;                  /* Chaîne finale complète      */

    /* Validation des arguments */

    result = (count == 1 || count == 2);
    if (!result) goto exit;

    result = G_IS_SCAN_LITERAL_EXPRESSION(args[0]);
    if (!result) goto exit;

    literal = G_SCAN_LITERAL_EXPRESSION(args[0]);

    vtype = g_scan_literal_expression_get_value_type(literal);

    result = (vtype == LVT_SIGNED_INTEGER || vtype == LVT_UNSIGNED_INTEGER);
    if (!result) goto exit;

    if (vtype == LVT_SIGNED_INTEGER)
    {
        result = g_scan_literal_expression_get_signed_integer_value(literal, &sval);
        if (!result) goto exit;

        assert(sval < 0);

        negative = (sval < 0);

        if (negative)
            uval = -sval;

    }
    else
    {
        result = g_scan_literal_expression_get_unsigned_integer_value(literal, &uval);
        if (!result) goto exit;
    }

    if (count == 1)
        base = 10;

    else
    {
        result = G_IS_SCAN_LITERAL_EXPRESSION(args[1]);
        if (!result) goto exit;

        literal = G_SCAN_LITERAL_EXPRESSION(args[1]);

        vtype = g_scan_literal_expression_get_value_type(literal);

        result = (vtype == LVT_UNSIGNED_INTEGER);
        if (!result) goto exit;

        result = g_scan_literal_expression_get_unsigned_integer_value(literal, &base);
        if (!result) goto exit;

        result = (base == 2 || base == 8 || base == 10 || base == 16);
        if (!result) goto exit;

    }

    /* Réalisation de l'opération attendue */

    data = malloc((1 + 2 + 64 * 8 + 1) * sizeof(char));
    iter = data;

    if (negative)
        *(iter++) = '-';

    switch (base)
    {
        case 2:
            *(iter++) = '0';
            *(iter++) = 'b';
            break;

        case 8:
            *(iter++) = '0';
            break;

        case 10:
            break;

        case 16:
            *(iter++) = '0';
            *(iter++) = 'x';
            break;

        default:
            assert(false);
            break;

    }

    convert_integer_to_string(uval, base, &iter);

    string.data = data;
    string.len = iter - data;

    *out = G_OBJECT(g_scan_literal_expression_new(LVT_STRING, &string));

    free(data);

    result = true;

 exit:

    return result;

}
