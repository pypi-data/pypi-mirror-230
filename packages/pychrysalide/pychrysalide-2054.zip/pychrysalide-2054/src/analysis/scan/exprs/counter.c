
/* Chrysalide - Outil d'analyse de fichiers binaires
 * counter.c - décompte de correspondances identifiées dans du contenu binaire
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


#include "counter.h"


#include "counter-int.h"
#include "literal.h"



/* --------------------- INSTANCIATION D'UNE FORME DE CONDITION --------------------- */


/* Initialise la classe des opérations booléennes. */
static void g_scan_match_counter_class_init(GScanMatchCounterClass *);

/* Initialise une instance d'opération booléenne. */
static void g_scan_match_counter_init(GScanMatchCounter *);

/* Supprime toutes les références externes. */
static void g_scan_match_counter_dispose(GScanMatchCounter *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_match_counter_finalize(GScanMatchCounter *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Réduit une expression à une forme plus simple. */
static ScanReductionState g_scan_match_counter_reduce(const GScanMatchCounter *, GScanContext *, GScanScope *, GScanExpression **);



/* ---------------------------------------------------------------------------------- */
/*                       INSTANCIATION D'UNE FORME DE CONDITION                       */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un décompte de résultats lors d'une recherche de motifs. */
G_DEFINE_TYPE(GScanMatchCounter, g_scan_match_counter, G_TYPE_SCAN_EXPRESSION);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des opérations booléennes.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_match_counter_class_init(GScanMatchCounterClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GScanExpressionClass *expr;             /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_match_counter_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_match_counter_finalize;

    expr = G_SCAN_EXPRESSION_CLASS(klass);

    expr->cmp_rich = (compare_expr_rich_fc)NULL;
    expr->reduce = (reduce_expr_fc)g_scan_match_counter_reduce;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : op = instance à initialiser.                                 *
*                                                                             *
*  Description : Initialise une instance d'opération booléenne.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_match_counter_init(GScanMatchCounter *counter)
{
    counter->pattern = NULL;

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

static void g_scan_match_counter_dispose(GScanMatchCounter *counter)
{
    g_clear_object(&counter->pattern);

    G_OBJECT_CLASS(g_scan_match_counter_parent_class)->dispose(G_OBJECT(counter));

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

static void g_scan_match_counter_finalize(GScanMatchCounter *counter)
{
    G_OBJECT_CLASS(g_scan_match_counter_parent_class)->finalize(G_OBJECT(counter));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pattern = motif à impliquer.                                 *
*                                                                             *
*  Description : Met en place un décompte de correspondances obtenues.        *
*                                                                             *
*  Retour      : Expression mise en place.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanExpression *g_scan_match_counter_new(GSearchPattern *pattern)
{
    GScanExpression *result;                /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_MATCH_COUNTER, NULL);

    if (!g_scan_match_counter_create(G_SCAN_MATCH_COUNTER(result), pattern))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : counter = instance à initialiser pleinement.                 *
*                pattern = motif à impliquer.                                 *
*                                                                             *
*  Description : Met en place un compteur de correspondances.                 *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_match_counter_create(GScanMatchCounter *counter, GSearchPattern *pattern)
{
    bool result;                            /* Bilan à retourner           */

    result = g_scan_expression_create(G_SCAN_EXPRESSION(counter), SRS_WAIT_FOR_SCAN);
    if (!result) goto exit;

    counter->pattern = pattern;
    g_object_ref(G_OBJECT(pattern));

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

static ScanReductionState g_scan_match_counter_reduce(const GScanMatchCounter *expr, GScanContext *ctx, GScanScope *scope, GScanExpression **out)
{
    ScanReductionState result;              /* Etat synthétisé à retourner */
    size_t count;                           /* Quantité de correspondances */

    if (g_scan_context_is_scan_done(ctx))
    {
        g_scan_context_get_full_matches(ctx, expr->pattern, &count);

        *out = g_scan_literal_expression_new(LVT_UNSIGNED_INTEGER, (unsigned long long []){ count });

        result = SRS_REDUCED;

    }
    else
        result = SRS_WAIT_FOR_SCAN;

    return result;

}
