
/* Chrysalide - Outil d'analyse de fichiers binaires
 * setcounter.c - décompte global de correspondances locales
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


#include "setcounter.h"


#include "setcounter-int.h"
#include "literal.h"



/* --------------------- INSTANCIATION D'UNE FORME DE CONDITION --------------------- */


/* Initialise la classe des opérations booléennes. */
static void g_scan_set_match_counter_class_init(GScanSetMatchCounterClass *);

/* Initialise une instance d'opération booléenne. */
static void g_scan_set_match_counter_init(GScanSetMatchCounter *);

/* Supprime toutes les références externes. */
static void g_scan_set_match_counter_dispose(GScanSetMatchCounter *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_set_match_counter_finalize(GScanSetMatchCounter *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Réduit une expression à une forme plus simple. */
static ScanReductionState g_scan_set_match_counter_reduce(const GScanSetMatchCounter *, GScanContext *, GScanScope *, GScanExpression **);



/* ---------------------------------------------------------------------------------- */
/*                       INSTANCIATION D'UNE FORME DE CONDITION                       */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un décompte de résultats lors d'une recherche de motifs. */
G_DEFINE_TYPE(GScanSetMatchCounter, g_scan_set_match_counter, G_TYPE_SCAN_EXPRESSION);


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

static void g_scan_set_match_counter_class_init(GScanSetMatchCounterClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GScanExpressionClass *expr;             /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_set_match_counter_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_set_match_counter_finalize;

    expr = G_SCAN_EXPRESSION_CLASS(klass);

    expr->cmp_rich = (compare_expr_rich_fc)NULL;
    expr->reduce = (reduce_expr_fc)g_scan_set_match_counter_reduce;

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

static void g_scan_set_match_counter_init(GScanSetMatchCounter *counter)
{
    counter->patterns = NULL;
    counter->count = 0;

    counter->type = SSCT_NONE;
    counter->number = 0;

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

static void g_scan_set_match_counter_dispose(GScanSetMatchCounter *counter)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < counter->count; i++)
         g_clear_object(&counter->patterns[i]);

    G_OBJECT_CLASS(g_scan_set_match_counter_parent_class)->dispose(G_OBJECT(counter));

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

static void g_scan_set_match_counter_finalize(GScanSetMatchCounter *counter)
{
    if (counter->patterns != NULL)
        free(counter->patterns);

    G_OBJECT_CLASS(g_scan_set_match_counter_parent_class)->finalize(G_OBJECT(counter));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : patterns = motifs à impliquer.                               *
*                count    = quantité de ces motifs.                           *
*                                                                             *
*  Description : Constitue un décompte de motifs avec correspondances.        *
*                                                                             *
*  Retour      : Expression mise en place.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanExpression *g_scan_set_match_counter_new(GSearchPattern ** const patterns, size_t count)
{
    GScanExpression *result;                /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_SET_MATCH_COUNTER, NULL);

    if (!g_scan_set_match_counter_create(G_SCAN_SET_MATCH_COUNTER(result), patterns, count))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : counter  = instance à initialiser pleinement.                *
*                patterns = motifs à impliquer.                               *
*                count    = quantité de ces motifs.                           *
*                                                                             *
*  Description : Met en place un décompte de motifs avec correspondances.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_set_match_counter_create(GScanSetMatchCounter *counter, GSearchPattern ** const patterns, size_t count)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours          */

    result = g_scan_expression_create(G_SCAN_EXPRESSION(counter), SRS_WAIT_FOR_SCAN);
    if (!result) goto exit;

    counter->patterns = malloc(count * sizeof(GSearchPattern *));
    counter->count = count;

    for (i = 0; i < count; i++)
    {
        counter->patterns[i] = patterns[i];
        g_object_ref(G_OBJECT(patterns[i]));
    }

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : counter  = décompte à compléter.                             *
*                patterns = motifs à impliquer.                               *
*                count    = quantité de ces motifs.                           *
*                                                                             *
*  Description : Ajoute de nouveaux motifs à un ensemble à décompter.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_scan_set_match_counter_add_extra_patterns(GScanSetMatchCounter *counter, GSearchPattern ** const patterns, size_t count)
{
    size_t first;                           /* Premier emplacement libre   */
    size_t i;                               /* Boucle de parcours          */

    first = counter->count;

    counter->count += count;
    counter->patterns = realloc(counter->patterns, counter->count * sizeof(GSearchPattern *));

    for (i = 0; i < count; i++)
    {
        counter->patterns[first + i] = patterns[i];
        g_object_ref(G_OBJECT(patterns[i]));
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : counter = décompte à configurer.                             *
*                type    = type de décompte à considérer.                     *
*                number  = volume minimal de motifs avec correspondances.     *
*                                                                             *
*  Description : Précise le volume de motifs avec correspondances à retrouver.*
*                                                                             *
*  Retour      : Bilan de validité des arguments fournis.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_set_match_counter_define_expected_matches(GScanSetMatchCounter *counter, ScanSetCounterType type, size_t *number)
{
    bool result;                            /* Bilan à retourner           */

    counter->type = type;

    if (type == SSCT_NUMBER)
    {
        counter->number = *number;
        result = (counter->number <= counter->count);
    }
    else
        result = true;

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

static ScanReductionState g_scan_set_match_counter_reduce(const GScanSetMatchCounter *expr, GScanContext *ctx, GScanScope *scope, GScanExpression **out)
{
    ScanReductionState result;              /* Etat synthétisé à retourner */
    size_t matched;                         /* Qté de motifs avec résultats*/
    size_t i;                               /* Boucle de parcours          */
    size_t count;                           /* Quantité de correspondances */
    bool status;                            /* Bilan d'évaluation finale   */

    if (g_scan_context_is_scan_done(ctx))
    {
        matched = 0;

        for (i = 0; i < expr->count; i++)
        {
            g_scan_context_get_full_matches(ctx, expr->patterns[i], &count);

            if (count > 0)
                matched++;

        }

        switch (expr->type)
        {
            case SSCT_NONE:
                status = (matched == 0);
                break;

            case SSCT_ANY:
                status = (matched >= 1);
                break;

            case SSCT_ALL:
                status = (matched == expr->count);
                break;

            case SSCT_NUMBER:
                status = (matched >= expr->number);
                break;

        }

        *out = g_scan_literal_expression_new(LVT_BOOLEAN, &status);

        result = SRS_REDUCED;

    }
    else
        result = SRS_WAIT_FOR_SCAN;

    return result;

}
