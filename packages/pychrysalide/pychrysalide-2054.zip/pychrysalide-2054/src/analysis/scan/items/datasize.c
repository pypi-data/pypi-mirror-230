
/* Chrysalide - Outil d'analyse de fichiers binaires
 * datasize.c - récupération de la taille du contenu scanné
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


#include "datasize.h"


#include "../item-int.h"
#include "../exprs/literal.h"



/* ---------------------- INTRODUCTION D'UNE NOUVELLE FONCTION ---------------------- */


/* Initialise la classe des mesures de quantité de données. */
static void g_scan_datasize_function_class_init(GScanDatasizeFunctionClass *);

/* Initialise une instance de mesure de quantité de données. */
static void g_scan_datasize_function_init(GScanDatasizeFunction *);

/* Supprime toutes les références externes. */
static void g_scan_datasize_function_dispose(GScanDatasizeFunction *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_datasize_function_finalize(GScanDatasizeFunction *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Indique le nom associé à une expression d'évaluation. */
static char *g_scan_datasize_function_get_name(const GScanDatasizeFunction *);

/* Réduit une expression à une forme plus simple. */
static bool g_scan_datasize_function_reduce(GScanDatasizeFunction *, GScanContext *, GScanScope *, GScanExpression **);

/* Réduit une expression à une forme plus simple. */
static bool g_scan_datasize_function_run_call(GScanDatasizeFunction *, GScanExpression **, size_t, GScanContext *, GScanScope *, GObject **);



/* ---------------------------------------------------------------------------------- */
/*                        INTRODUCTION D'UNE NOUVELLE FONCTION                        */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une mesure de quantité de données scannées. */
G_DEFINE_TYPE(GScanDatasizeFunction, g_scan_datasize_function, G_TYPE_REGISTERED_ITEM);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des mesures de quantité de données.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_datasize_function_class_init(GScanDatasizeFunctionClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GRegisteredItemClass *registered;       /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_datasize_function_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_datasize_function_finalize;

    registered = G_REGISTERED_ITEM_CLASS(klass);

    registered->get_name = (get_registered_item_name_fc)g_scan_datasize_function_get_name;
    registered->reduce = (reduce_registered_item_fc)g_scan_datasize_function_reduce;
    registered->run_call = (run_registered_item_call_fc)g_scan_datasize_function_run_call;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : func = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance de mesure de quantité de données.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_datasize_function_init(GScanDatasizeFunction *func)
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

static void g_scan_datasize_function_dispose(GScanDatasizeFunction *func)
{
    G_OBJECT_CLASS(g_scan_datasize_function_parent_class)->dispose(G_OBJECT(func));

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

static void g_scan_datasize_function_finalize(GScanDatasizeFunction *func)
{
    G_OBJECT_CLASS(g_scan_datasize_function_parent_class)->finalize(G_OBJECT(func));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Constitue une fonction de récupération de taille de données. *
*                                                                             *
*  Retour      : Fonction mise en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GRegisteredItem *g_scan_datasize_function_new(void)
{
    GScanDatasizeFunction *result;              /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_DATASIZE_FUNCTION, NULL);

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

static char *g_scan_datasize_function_get_name(const GScanDatasizeFunction *item)
{
    char *result;                           /* Désignation à retourner     */

    result = strdup("datasize");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item  = élément d'appel à consulter.                         *
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

static bool g_scan_datasize_function_reduce(GScanDatasizeFunction *item, GScanContext *ctx, GScanScope *scope, GScanExpression **out)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu à manipuler         */
    phys_t size;                            /* Quantité de données liées   */

    result = true;

    content = g_scan_context_get_content(ctx);

    size = g_binary_content_compute_size(content);

    *out = g_scan_literal_expression_new(LVT_UNSIGNED_INTEGER, (unsigned long long []){ size });

    g_object_unref(G_OBJECT(content));

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

static bool g_scan_datasize_function_run_call(GScanDatasizeFunction *item, GScanExpression **args, size_t count, GScanContext *ctx, GScanScope *scope, GObject **out)
{
    bool result;                            /* Bilan à retourner           */

    result = g_scan_datasize_function_reduce(item, ctx, scope, (GScanExpression **)out);

    return result;

}
