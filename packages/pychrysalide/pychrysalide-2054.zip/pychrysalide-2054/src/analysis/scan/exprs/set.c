
/* Chrysalide - Outil d'analyse de fichiers binaires
 * set.c - base d'ensembles de valeurs diverses, de types hétérogènes ou homogènes
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


#include "set.h"


#include <assert.h>
#include <malloc.h>


#include "literal.h"
#include "set-int.h"



/* --------------------- INTRODUCTION D'UNE NOUVELLE EXPRESSION --------------------- */


/* Initialise la classe des bases d'ensembles d'éléments. */
static void g_scan_generic_set_class_init(GScanGenericSetClass *);

/* Initialise une instance de base d'ensemble d'éléments. */
static void g_scan_generic_set_init(GScanGenericSet *);

/* Supprime toutes les références externes. */
static void g_scan_generic_set_dispose(GScanGenericSet *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_generic_set_finalize(GScanGenericSet *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Réduit une expression à une forme plus simple. */
static ScanReductionState g_scan_generic_set_reduce(const GScanGenericSet *, GScanContext *, GScanScope *, GScanExpression **);

/* Réduit une expression à une forme booléenne. */
static bool g_scan_generic_set_reduce_to_boolean(const GScanGenericSet *, GScanContext *, GScanScope *, GScanExpression **);

/* Dénombre les éléments portés par une expression. */
static bool g_scan_generic_set_count_items(const GScanGenericSet *, GScanContext *, size_t *);

/* Fournit un élément donné issu d'un ensemble constitué. */
static bool g_scan_generic_set_get_item(const GScanGenericSet *, size_t, GScanContext *, GScanExpression **);



/* ---------------------------------------------------------------------------------- */
/*                       INTRODUCTION D'UNE NOUVELLE EXPRESSION                       */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une base d'ensembles d'éléments homogènes ou hétérogènes. */
G_DEFINE_TYPE(GScanGenericSet, g_scan_generic_set, G_TYPE_SCAN_EXPRESSION);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des bases d'ensembles d'éléments.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_generic_set_class_init(GScanGenericSetClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GScanExpressionClass *expr;             /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_generic_set_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_generic_set_finalize;

    expr = G_SCAN_EXPRESSION_CLASS(klass);

    expr->reduce = (reduce_expr_fc)g_scan_generic_set_reduce;
    expr->reduce_to_bool = (reduce_expr_to_bool_fc)g_scan_generic_set_reduce_to_boolean;
    expr->count = (count_scan_expr_fc)g_scan_generic_set_count_items;
    expr->get = (get_scan_expr_fc)g_scan_generic_set_get_item;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : set = instance à initialiser.                                *
*                                                                             *
*  Description : Initialise une instance de base d'ensemble d'éléments.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_generic_set_init(GScanGenericSet *set)
{
    set->items = NULL;
    set->count = 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : set = instance d'objet GLib à traiter.                       *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_generic_set_dispose(GScanGenericSet *set)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < set->count; i++)
        g_clear_object(&set->items[i]);

    G_OBJECT_CLASS(g_scan_generic_set_parent_class)->dispose(G_OBJECT(set));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : set = instance d'objet GLib à traiter.                       *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_generic_set_finalize(GScanGenericSet *set)
{
    if (set->items != NULL)
        free(set->items);

    G_OBJECT_CLASS(g_scan_generic_set_parent_class)->finalize(G_OBJECT(set));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Constitue un ensemble d'éléments homogènes ou hétérogènes.   *
*                                                                             *
*  Retour      : Expression mise en place.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanExpression *g_scan_generic_set_new(void)
{
    GScanExpression *result;                /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_GENERIC_SET, NULL);

    if (!g_scan_generic_set_create(G_SCAN_GENERIC_SET(result)))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : set = instance à initialiser pleinement.                     *
*                                                                             *
*  Description : Met en place un ensemble d'éléments homogènes ou hétérogènes.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_generic_set_create(GScanGenericSet *set)
{
    bool result;                            /* Bilan à retourner           */

    result = g_scan_expression_create(G_SCAN_EXPRESSION(set), SRS_PENDING);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : set  = ensemble à compléter.                                 *
*                item = nouvel élément à intégrer.                            *
*                                                                             *
*  Description : Ajoute un nouvel élément à un ensemble.                      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_scan_generic_set_add_item(GScanGenericSet *set, GScanExpression *item)
{
    set->items = realloc(set->items, ++set->count * sizeof(GScanExpression *));

    set->items[set->count - 1] = item;
    g_object_ref(G_OBJECT(item));

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

static ScanReductionState g_scan_generic_set_reduce(const GScanGenericSet *expr, GScanContext *ctx, GScanScope *scope, GScanExpression **out)
{
    ScanReductionState result;              /* Etat synthétisé à retourner */
    size_t i;                               /* Boucle de parcours #1       */
    GScanExpression *item;                  /* Elément en cours d'analyse  */
    GScanExpression *new;                   /* Nouvelle réduction obtenue  */
    ScanReductionState state;               /* Etat synthétisé d'un élément*/
    size_t k;                               /* Boucle de parcours #2       */

    result = SRS_REDUCED;

    for (i = 0; i < expr->count; i++)
    {
        item = expr->items[i];

        state = g_scan_expression_reduce(item, ctx, scope, &new);
        if (state == SRS_UNRESOLVABLE)
        {
            result = SRS_UNRESOLVABLE;
            g_clear_object(out);
            break;
        }

        if (state == SRS_WAIT_FOR_SCAN)
            result = SRS_WAIT_FOR_SCAN;

        if (new != item)
        {
            if (*out == NULL)
            {
                *out = g_scan_generic_set_new();

                for (k = 0; k < i; k++)
                    g_scan_generic_set_add_item(G_SCAN_GENERIC_SET(*out), expr->items[k]);

            }

            g_scan_generic_set_add_item(G_SCAN_GENERIC_SET(*out), new);

        }

        else
        {
            if (*out != NULL)
                g_scan_generic_set_add_item(G_SCAN_GENERIC_SET(*out), item);
        }

        g_object_unref(G_OBJECT(new));

    }

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

static bool g_scan_generic_set_reduce_to_boolean(const GScanGenericSet *expr, GScanContext *ctx, GScanScope *scope, GScanExpression **out)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    *out = g_scan_literal_expression_new(LVT_BOOLEAN, (bool []){ expr->count > 0 });

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

static bool g_scan_generic_set_count_items(const GScanGenericSet *expr, GScanContext *ctx, size_t *count)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    *count = expr->count;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : expr  = expression à consulter.                              *
*                index = indice de l'élément à transférer.                    *
*                ctx   = contexte de suivi de l'analyse courante.             *
*                out   = zone d'enregistrement de la réduction opérée. [OUT]  *
*                                                                             *
*  Description : Fournit un élément donné issu d'un ensemble constitué.       *
*                                                                             *
*  Retour      : Bilan de l'opération : false en cas d'erreur irrécupérable.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_scan_generic_set_get_item(const GScanGenericSet *expr, size_t index, GScanContext *ctx, GScanExpression **out)
{
    bool result;                            /* Bilan à retourner           */

    result = (index < expr->count);

    if (result)
        *out = expr->items[index];

    return result;

}
