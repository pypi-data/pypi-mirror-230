
/* Chrysalide - Outil d'analyse de fichiers binaires
 * make.c - construction de volume de secondes à partir d'une date
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


#include "make.h"


#include <assert.h>
#include <time.h>


#include "../../item-int.h"
#include "../../exprs/literal.h"



/* ---------------------- INTRODUCTION D'UNE NOUVELLE FONCTION ---------------------- */


/* Initialise la classe des conversions de dates en secondes. */
static void g_scan_time_make_function_class_init(GScanTimeMakeFunctionClass *);

/* Initialise une instance de convertisseur de date en secondes. */
static void g_scan_time_make_function_init(GScanTimeMakeFunction *);

/* Supprime toutes les références externes. */
static void g_scan_time_make_function_dispose(GScanTimeMakeFunction *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_time_make_function_finalize(GScanTimeMakeFunction *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Indique le nom associé à une expression d'évaluation. */
static char *g_scan_time_make_function_get_name(const GScanTimeMakeFunction *);

/* Réduit une expression à une forme plus simple. */
static bool g_scan_time_make_function_run_call(GScanTimeMakeFunction *, GScanExpression **, size_t, GScanContext *, GScanScope *, GObject **);



/* ---------------------------------------------------------------------------------- */
/*                        INTRODUCTION D'UNE NOUVELLE FONCTION                        */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une conversion de date en nombre de secondes. */
G_DEFINE_TYPE(GScanTimeMakeFunction, g_scan_time_make_function, G_TYPE_REGISTERED_ITEM);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des conversions de dates en secondes.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_time_make_function_class_init(GScanTimeMakeFunctionClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GRegisteredItemClass *registered;       /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_time_make_function_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_time_make_function_finalize;

    registered = G_REGISTERED_ITEM_CLASS(klass);

    registered->get_name = (get_registered_item_name_fc)g_scan_time_make_function_get_name;
    registered->run_call = (run_registered_item_call_fc)g_scan_time_make_function_run_call;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : func = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance de convertisseur de date en secondes.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_time_make_function_init(GScanTimeMakeFunction *func)
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

static void g_scan_time_make_function_dispose(GScanTimeMakeFunction *func)
{
    G_OBJECT_CLASS(g_scan_time_make_function_parent_class)->dispose(G_OBJECT(func));

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

static void g_scan_time_make_function_finalize(GScanTimeMakeFunction *func)
{
    G_OBJECT_CLASS(g_scan_time_make_function_parent_class)->finalize(G_OBJECT(func));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Constitue une fonction de décompte du temps écoulé.          *
*                                                                             *
*  Retour      : Fonction mise en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GRegisteredItem *g_scan_time_make_function_new(void)
{
    GRegisteredItem *result;                /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_TIME_MAKE_FUNCTION, NULL);

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

static char *g_scan_time_make_function_get_name(const GScanTimeMakeFunction *item)
{
    char *result;                           /* Désignation à retourner     */

    result = strdup("make");

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

static bool g_scan_time_make_function_run_call(GScanTimeMakeFunction *item, GScanExpression **args, size_t count, GScanContext *ctx, GScanScope *scope, GObject **out)
{
    bool result;                            /* Bilan à retourner           */
    bool status;                            /* Possibilité de construction */
    size_t i;                               /* Boucle de parcours          */
    LiteralValueType vtype;                 /* Type de valeur portée       */
    struct tm date;                         /* Date à mettre en place      */
    unsigned long long value;               /* Valeur entière à utiliser   */
    time_t computed;                        /* Nombre de secondes déterminé*/

    /* Validation des arguments */

    result = (count == 3 || count == 6);
    if (!result) goto exit;

    status = true;

    for (i = 0; i < count && status; i++)
    {
        status = G_IS_SCAN_LITERAL_EXPRESSION(args[i]);
        if (!status) break;

        vtype = g_scan_literal_expression_get_value_type(G_SCAN_LITERAL_EXPRESSION(args[i]));

        status = (vtype == LVT_UNSIGNED_INTEGER);
        if (!status) break;

    }

    if (!status) goto exit;

    /* Lecture des arguments */

    memset(&date, 0, sizeof(struct tm));

    status = g_scan_literal_expression_get_unsigned_integer_value(G_SCAN_LITERAL_EXPRESSION(args[0]), &value);
    assert(status);
    if (!status) goto exit;

    if (value < 1900)
    {
        result = false;
        goto exit;
    }

    date.tm_year = value - 1900;

    status = g_scan_literal_expression_get_unsigned_integer_value(G_SCAN_LITERAL_EXPRESSION(args[1]), &value);
    assert(status);
    if (!status) goto exit;

    if (value > 12)
    {
        result = false;
        goto exit;
    }

    date.tm_mon = value - 1;

    status = g_scan_literal_expression_get_unsigned_integer_value(G_SCAN_LITERAL_EXPRESSION(args[2]), &value);
    assert(status);
    if (!status) goto exit;

    if (value < 1 || value > 31)
    {
        result = false;
        goto exit;
    }

    date.tm_mday = value;

    if (count == 6)
    {
        status = g_scan_literal_expression_get_unsigned_integer_value(G_SCAN_LITERAL_EXPRESSION(args[3]), &value);
        assert(status);
        if (!status) goto exit;

        if (value >= 24)
        {
            result = false;
            goto exit;
        }

        date.tm_hour = value;

        status = g_scan_literal_expression_get_unsigned_integer_value(G_SCAN_LITERAL_EXPRESSION(args[4]), &value);
        assert(status);
        if (!status) goto exit;

        if (value >= 60)
        {
            result = false;
            goto exit;
        }

        date.tm_min = value;

        status = g_scan_literal_expression_get_unsigned_integer_value(G_SCAN_LITERAL_EXPRESSION(args[5]), &value);
        assert(status);
        if (!status) goto exit;

        if (value >= 60)
        {
            result = false;
            goto exit;
        }

        date.tm_sec = value;

    }

    /* Construction de la valeur finale */

    computed = timegm(&date);

    if (computed != (time_t)-1)
        *out = G_OBJECT(g_scan_literal_expression_new(LVT_UNSIGNED_INTEGER, (unsigned long long []){ computed }));

 exit:

    return result;

}
