
/* Chrysalide - Outil d'analyse de fichiers binaires
 * lower.c - bascule de lettres en minuscules
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


#include "lower.h"


#include <ctype.h>


#include "../../item-int.h"
#include "../../exprs/literal.h"



/* ---------------------- INTRODUCTION D'UNE NOUVELLE FONCTION ---------------------- */


/* Initialise la classe des bascules de lettres en minuscules. */
static void g_scan_string_lower_function_class_init(GScanStringLowerFunctionClass *);

/* Initialise une instance de bascule de lettres en minuscules. */
static void g_scan_string_lower_function_init(GScanStringLowerFunction *);

/* Supprime toutes les références externes. */
static void g_scan_string_lower_function_dispose(GScanStringLowerFunction *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_string_lower_function_finalize(GScanStringLowerFunction *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Indique le nom associé à une expression d'évaluation. */
static char *g_scan_string_lower_function_get_name(const GScanStringLowerFunction *);

/* Réduit une expression à une forme plus simple. */
static bool g_scan_string_lower_function_run_call(GScanStringLowerFunction *, GScanExpression **, size_t, GScanContext *, GScanScope *, GObject **);



/* ---------------------------------------------------------------------------------- */
/*                        INTRODUCTION D'UNE NOUVELLE FONCTION                        */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une bascule de la casse d'une suite de caractères. */
G_DEFINE_TYPE(GScanStringLowerFunction, g_scan_string_lower_function, G_TYPE_REGISTERED_ITEM);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des bascules de lettres en minuscules.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_string_lower_function_class_init(GScanStringLowerFunctionClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GRegisteredItemClass *registered;       /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_string_lower_function_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_string_lower_function_finalize;

    registered = G_REGISTERED_ITEM_CLASS(klass);

    registered->get_name = (get_registered_item_name_fc)g_scan_string_lower_function_get_name;
    registered->run_call = (run_registered_item_call_fc)g_scan_string_lower_function_run_call;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : func = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance de bascule de lettres en minuscules. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_string_lower_function_init(GScanStringLowerFunction *func)
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

static void g_scan_string_lower_function_dispose(GScanStringLowerFunction *func)
{
    G_OBJECT_CLASS(g_scan_string_lower_function_parent_class)->dispose(G_OBJECT(func));

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

static void g_scan_string_lower_function_finalize(GScanStringLowerFunction *func)
{
    G_OBJECT_CLASS(g_scan_string_lower_function_parent_class)->finalize(G_OBJECT(func));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Constitue une fonction de bascule de lettres en minuscules.  *
*                                                                             *
*  Retour      : Fonction mise en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GRegisteredItem *g_scan_string_lower_function_new(void)
{
    GRegisteredItem *result;                /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_STRING_LOWER_FUNCTION, NULL);

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

static char *g_scan_string_lower_function_get_name(const GScanStringLowerFunction *item)
{
    char *result;                           /* Désignation à retourner     */

    result = strdup("lower");

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

static bool g_scan_string_lower_function_run_call(GScanStringLowerFunction *item, GScanExpression **args, size_t count, GScanContext *ctx, GScanScope *scope, GObject **out)
{
    bool result;                            /* Bilan à retourner           */
    GScanLiteralExpression *literal;        /* Version plus accessible     */
    LiteralValueType vtype;                 /* Type de valeur portée       */
    const sized_string_t *string;           /* Description du chaîne       */
    sized_string_t new;                     /* Description transformée     */
    size_t i;                               /* Boucle de parcours          */

    /* Validation des arguments */

    result = (count == 1);
    if (!result) goto exit;

    result = G_IS_SCAN_LITERAL_EXPRESSION(args[0]);
    if (!result) goto exit;

    literal = G_SCAN_LITERAL_EXPRESSION(args[0]);

    vtype = g_scan_literal_expression_get_value_type(literal);

    result = (vtype == LVT_STRING);
    if (!result) goto exit;

    result = g_scan_literal_expression_get_string_value(literal, &string);
    if (!result) goto exit;

    /* Réalisation de l'opération attendue */

    new.data = malloc(string->len);
    new.len = string->len;

    for (i = 0; i < string->len; i++)
        new.data[i] = tolower(string->data[i]);

    *out = G_OBJECT(g_scan_literal_expression_new(LVT_STRING, &new));

    exit_szstr(&new);

 exit:

    return result;

}
