
/* Chrysalide - Outil d'analyse de fichiers binaires
 * to_int.c - conversion d'une chaîne en valeur entière
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


#include "to_int.h"


#include <stdlib.h>


#include "../../item-int.h"
#include "../../exprs/literal.h"



/* ---------------------- INTRODUCTION D'UNE NOUVELLE FONCTION ---------------------- */


/* Initialise la classe des conversions de texte en entier. */
static void g_scan_string_to_int_function_class_init(GScanStringToIntFunctionClass *);

/* Initialise une instance de conversion de texte en entier. */
static void g_scan_string_to_int_function_init(GScanStringToIntFunction *);

/* Supprime toutes les références externes. */
static void g_scan_string_to_int_function_dispose(GScanStringToIntFunction *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_string_to_int_function_finalize(GScanStringToIntFunction *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Indique le nom associé à une expression d'évaluation. */
static char *g_scan_string_to_int_function_get_name(const GScanStringToIntFunction *);

/* Réduit une expression à une forme plus simple. */
static bool g_scan_string_to_int_function_run_call(GScanStringToIntFunction *, GScanExpression **, size_t, GScanContext *, GScanScope *, GObject **);



/* ---------------------------------------------------------------------------------- */
/*                        INTRODUCTION D'UNE NOUVELLE FONCTION                        */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une conversion de texte en entier. */
G_DEFINE_TYPE(GScanStringToIntFunction, g_scan_string_to_int_function, G_TYPE_REGISTERED_ITEM);


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

static void g_scan_string_to_int_function_class_init(GScanStringToIntFunctionClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GRegisteredItemClass *registered;       /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_string_to_int_function_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_string_to_int_function_finalize;

    registered = G_REGISTERED_ITEM_CLASS(klass);

    registered->get_name = (get_registered_item_name_fc)g_scan_string_to_int_function_get_name;
    registered->run_call = (run_registered_item_call_fc)g_scan_string_to_int_function_run_call;

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

static void g_scan_string_to_int_function_init(GScanStringToIntFunction *func)
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

static void g_scan_string_to_int_function_dispose(GScanStringToIntFunction *func)
{
    G_OBJECT_CLASS(g_scan_string_to_int_function_parent_class)->dispose(G_OBJECT(func));

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

static void g_scan_string_to_int_function_finalize(GScanStringToIntFunction *func)
{
    G_OBJECT_CLASS(g_scan_string_to_int_function_parent_class)->finalize(G_OBJECT(func));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée une fonction de conversion de texte en valeur entière.  *
*                                                                             *
*  Retour      : Fonction mise en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GRegisteredItem *g_scan_string_to_int_function_new(void)
{
    GRegisteredItem *result;                /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_STRING_TO_INT_FUNCTION, NULL);

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

static char *g_scan_string_to_int_function_get_name(const GScanStringToIntFunction *item)
{
    char *result;                           /* Désignation à retourner     */

    result = strdup("to_int");

    return result;

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

static bool g_scan_string_to_int_function_run_call(GScanStringToIntFunction *item, GScanExpression **args, size_t count, GScanContext *ctx, GScanScope *scope, GObject **out)
{
    bool result;                            /* Bilan à retourner           */
    GScanLiteralExpression *literal;        /* Version plus accessible     */
    LiteralValueType vtype;                 /* Type de valeur portée       */
    const sized_string_t *string;           /* Chaîne à convertir          */
    unsigned long long base;                /* Base de conversion          */
    char *data;                             /* Chaîne "C" à considérer     */
    long long sval;                         /* Valeur signée obtenue       */
    unsigned long long uval;                /* Valeur non signée obtenue   */

    /* Validation des arguments */

    result = (count == 1 || count == 2);
    if (!result) goto exit;

    result = G_IS_SCAN_LITERAL_EXPRESSION(args[0]);
    if (!result) goto exit;

    literal = G_SCAN_LITERAL_EXPRESSION(args[0]);

    vtype = g_scan_literal_expression_get_value_type(literal);

    result = (vtype == LVT_STRING);
    if (!result) goto exit;

    result = g_scan_literal_expression_get_string_value(literal, &string);
    if (!result) goto exit;

    if (string->len == 0) goto exit;

    if (count == 1)
        base = 0;

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

    }

    /* Réalisation de l'opération attendue */

    data = strndup(string->data, string->len);

    if (string->data[0] == '-')
    {
        sval = strtoll(data, NULL, base);

        *out = G_OBJECT(g_scan_literal_expression_new(LVT_SIGNED_INTEGER, &sval));

    }
    else
    {
        uval = strtoll(data, NULL, base);

        *out = G_OBJECT(g_scan_literal_expression_new(LVT_UNSIGNED_INTEGER, &uval));

    }

    free(data);

 exit:

    return result;

}
