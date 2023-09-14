
/* Chrysalide - Outil d'analyse de fichiers binaires
 * log.c - affichage de message à partir des conditions d'une règle
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


#include "log.h"


#include <ctype.h>


#include "../../item-int.h"
#include "../../exprs/literal.h"



/* ---------------------- INTRODUCTION D'UNE NOUVELLE FONCTION ---------------------- */


/* Initialise la classe des affichages de messages. */
static void g_scan_console_log_function_class_init(GScanConsoleLogFunctionClass *);

/* Initialise une instance d'affichage de message. */
static void g_scan_console_log_function_init(GScanConsoleLogFunction *);

/* Supprime toutes les références externes. */
static void g_scan_console_log_function_dispose(GScanConsoleLogFunction *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_console_log_function_finalize(GScanConsoleLogFunction *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Indique le nom associé à une expression d'évaluation. */
static char *g_scan_console_log_function_get_name(const GScanConsoleLogFunction *);

/* Réduit une expression à une forme plus simple. */
static bool g_scan_console_log_function_run_call(GScanConsoleLogFunction *, GScanExpression **, size_t, GScanContext *, GScanScope *, GObject **);



/* ---------------------------------------------------------------------------------- */
/*                        INTRODUCTION D'UNE NOUVELLE FONCTION                        */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un afficheur de messages arbitraires. */
G_DEFINE_TYPE(GScanConsoleLogFunction, g_scan_console_log_function, G_TYPE_REGISTERED_ITEM);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des affichages de messages.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_console_log_function_class_init(GScanConsoleLogFunctionClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GRegisteredItemClass *registered;       /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_console_log_function_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_console_log_function_finalize;

    registered = G_REGISTERED_ITEM_CLASS(klass);

    registered->get_name = (get_registered_item_name_fc)g_scan_console_log_function_get_name;
    registered->run_call = (run_registered_item_call_fc)g_scan_console_log_function_run_call;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : func = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance d'affichage de message.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_console_log_function_init(GScanConsoleLogFunction *func)
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

static void g_scan_console_log_function_dispose(GScanConsoleLogFunction *func)
{
    G_OBJECT_CLASS(g_scan_console_log_function_parent_class)->dispose(G_OBJECT(func));

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

static void g_scan_console_log_function_finalize(GScanConsoleLogFunction *func)
{
    G_OBJECT_CLASS(g_scan_console_log_function_parent_class)->finalize(G_OBJECT(func));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Constitue une fonction d'affichage de messages quelconques.  *
*                                                                             *
*  Retour      : Fonction mise en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanConsoleLogFunction *g_scan_console_log_function_new(void)
{
    GScanConsoleLogFunction *result;              /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_CONSOLE_LOG_FUNCTION, NULL);

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

static char *g_scan_console_log_function_get_name(const GScanConsoleLogFunction *item)
{
    char *result;                           /* Désignation à retourner     */

    result = strdup("log");

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

static bool g_scan_console_log_function_run_call(GScanConsoleLogFunction *item, GScanExpression **args, size_t count, GScanContext *ctx, GScanScope *scope, GObject **out)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours #1       */
    GScanLiteralExpression *literal;        /* Version plus accessible     */
    LiteralValueType vtype;                 /* Type de valeur portée       */
    bool boolean;                           /* Valeur booléenne            */
    long long sinteger;                     /* Valeur entière signée   */
    unsigned long long uinteger;            /* Valeur entière non signée   */
    const sized_string_t *string;           /* Description du chaîne       */
    size_t k;                               /* Boucle de parcours #2       */

    result = true;

    if (count == 0)
        goto done;

    for (i = 0; i < count && result; i++)
        result = G_IS_SCAN_LITERAL_EXPRESSION(args[i]);

    if (!result)
        goto done;

    for (i = 0; i < count; i++)
    {
        literal = G_SCAN_LITERAL_EXPRESSION(args[i]);

        vtype = g_scan_literal_expression_get_value_type(literal);

        switch (vtype)
        {
            case LVT_BOOLEAN:
                result = g_scan_literal_expression_get_boolean_value(literal, &boolean);
                if (result)
                    fprintf(stderr, "%s", boolean ? "true" : "false");
                break;

            case LVT_SIGNED_INTEGER:
                result = g_scan_literal_expression_get_signed_integer_value(literal, &sinteger);
                if (result)
                    fprintf(stderr, "0x%llx", sinteger);
                break;

            case LVT_UNSIGNED_INTEGER:
                result = g_scan_literal_expression_get_unsigned_integer_value(literal, &uinteger);
                if (result)
                    fprintf(stderr, "0x%llx", uinteger);
                break;

            case LVT_STRING:
                result = g_scan_literal_expression_get_string_value(literal, &string);
                if (result)
                    for (k = 0; k < string->len; k++)
                    {
                        if (isprint(string->data[k]))
                            fprintf(stderr, "%c", string->data[k]);
                        else
                            fprintf(stderr, "\\x%02hhx", string->data[k]);
                    }
                break;

            default:
                break;

        }

    }

    fprintf(stderr, "\n");

 done:

    if (result)
        *out = G_OBJECT(g_scan_literal_expression_new(LVT_BOOLEAN, (bool []){ result }));

    return result;

}
