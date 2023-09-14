
/* Chrysalide - Outil d'analyse de fichiers binaires
 * handler.c - manipulation des correspondances établies lors d'un scan
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


#include "handler.h"


#include <assert.h>


#include "literal.h"
#include "handler-int.h"
#include "../matches/bytes.h"



/* --------------------- INTRODUCTION D'UNE NOUVELLE EXPRESSION --------------------- */


/* Initialise la classe des manipulations de correspondances. */
static void g_scan_pattern_handler_class_init(GScanPatternHandlerClass *);

/* Initialise une instance de manipulation de correspondances. */
static void g_scan_pattern_handler_init(GScanPatternHandler *);

/* Supprime toutes les références externes. */
static void g_scan_pattern_handler_dispose(GScanPatternHandler *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_pattern_handler_finalize(GScanPatternHandler *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Réduit une expression à une forme plus simple. */
static ScanReductionState g_scan_pattern_handler_reduce(const GScanPatternHandler *, GScanContext *, GScanScope *, GScanExpression **);

/* Réduit une expression à une forme booléenne. */
static bool g_scan_pattern_handler_reduce_to_boolean(const GScanPatternHandler *, GScanContext *, GScanScope *, GScanExpression **);

/* Dénombre les éléments portés par une expression. */
static bool g_scan_pattern_handler_count_items(const GScanPatternHandler *, GScanContext *, size_t *);

/* Fournit un élément donné issu d'un ensemble constitué. */
static bool g_scan_pattern_handler_get_item(const GScanPatternHandler *, size_t, GScanContext *, GScanExpression **);



/* ---------------------------------------------------------------------------------- */
/*                       INTRODUCTION D'UNE NOUVELLE EXPRESSION                       */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une manipulation de correspondances établies lors d'un scan. */
G_DEFINE_TYPE(GScanPatternHandler, g_scan_pattern_handler, G_TYPE_SCAN_EXPRESSION);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des manipulations de correspondances.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_pattern_handler_class_init(GScanPatternHandlerClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GScanExpressionClass *expr;             /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_pattern_handler_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_pattern_handler_finalize;

    expr = G_SCAN_EXPRESSION_CLASS(klass);

    expr->reduce = (reduce_expr_fc)g_scan_pattern_handler_reduce;
    expr->reduce_to_bool = (reduce_expr_to_bool_fc)g_scan_pattern_handler_reduce_to_boolean;
    expr->count = (count_scan_expr_fc)g_scan_pattern_handler_count_items;
    expr->get = (get_scan_expr_fc)g_scan_pattern_handler_get_item;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : handler = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance de manipulation de correspondances.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_pattern_handler_init(GScanPatternHandler *handler)
{
    handler->pattern = NULL;
    handler->type = SHT_RAW;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : handler = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_pattern_handler_dispose(GScanPatternHandler *handler)
{
    g_clear_object(&handler->pattern);

    G_OBJECT_CLASS(g_scan_pattern_handler_parent_class)->dispose(G_OBJECT(handler));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : handler = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_pattern_handler_finalize(GScanPatternHandler *handler)
{
    G_OBJECT_CLASS(g_scan_pattern_handler_parent_class)->finalize(G_OBJECT(handler));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pattern = motif à impliquer.                                 *
*                type    = type de manipulation attendue.                     *
*                                                                             *
*  Description : Met en place une manipulation de correspondances établies.   *
*                                                                             *
*  Retour      : Expression mise en place.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanExpression *g_scan_pattern_handler_new(GSearchPattern *pattern, ScanHandlerType type)
{
    GScanExpression *result;                /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_PATTERN_HANDLER, NULL);

    if (!g_scan_pattern_handler_create(G_SCAN_PATTERN_HANDLER(result), pattern, type))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : handler = instance à initialiser pleinement.                 *
*                pattern = motif à impliquer.                                 *
*                type    = type de manipulation attendue.                     *
*                                                                             *
*  Description : Met en place une manipulation de correspondances établies.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_pattern_handler_create(GScanPatternHandler *handler, GSearchPattern *pattern, ScanHandlerType type)
{
    bool result;                            /* Bilan à retourner           */

    result = g_scan_expression_create(G_SCAN_EXPRESSION(handler), SRS_WAIT_FOR_SCAN);
    if (!result) goto exit;

    handler->pattern = pattern;
    g_object_ref(G_OBJECT(pattern));

    handler->type = type;

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

static ScanReductionState g_scan_pattern_handler_reduce(const GScanPatternHandler *expr, GScanContext *ctx, GScanScope *scope, GScanExpression **out)
{
    ScanReductionState result;              /* Etat synthétisé à retourner */

    if (g_scan_context_is_scan_done(ctx))
        result = SRS_REDUCED;

    else
        result = SRS_WAIT_FOR_SCAN;

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

static bool g_scan_pattern_handler_reduce_to_boolean(const GScanPatternHandler *expr, GScanContext *ctx, GScanScope *scope, GScanExpression **out)
{
    bool result;                            /* Bilan à retourner           */
    size_t count;                           /* Quantité de correspondances */

    result = true;

    g_scan_context_get_full_matches(ctx, expr->pattern, &count);

    *out = g_scan_literal_expression_new(LVT_BOOLEAN, (bool []){ count > 0 });

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

static bool g_scan_pattern_handler_count_items(const GScanPatternHandler *expr, GScanContext *ctx, size_t *count)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    assert(g_scan_context_is_scan_done(ctx));

    g_scan_context_get_full_matches(ctx, expr->pattern, count);

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

static bool g_scan_pattern_handler_get_item(const GScanPatternHandler *expr, size_t index, GScanContext *ctx, GScanExpression **out)
{
    bool result;                            /* Bilan à retourner           */
    size_t count;                           /* Quantité de correspondances */
    const GScanMatch **matches;             /* Correspondances en place    */
    const GScanBytesMatch *match;           /* Correspondance ciblée       */
    phys_t start;                           /* Point de départ du motif    */
    phys_t end;                             /* Point d'arrivée du motif    */
    phys_t len;                             /* Taille du motif             */
    GBinContent *content;                   /* Contenu binaire à relire    */
    vmpa2t pos;                             /* Tête de lecture             */
    const bin_t *data;                      /* Accès aux données brutes    */
    sized_string_t binary;                  /* Conversion de formats       */

    assert(g_scan_context_is_scan_done(ctx));

    matches = g_scan_context_get_full_matches(ctx, expr->pattern, &count);

    result = (index < count);
    if (!result) goto done;

    result = G_IS_SCAN_BYTES_MATCH(matches[index]);
    if (!result) goto done;

    match = G_SCAN_BYTES_MATCH(matches[index]);

    len = g_scan_bytes_match_get_location(match, &start, &end);

    switch (expr->type)
    {
        case SHT_RAW:
            content = g_scan_bytes_match_get_content(match);

            init_vmpa(&pos, start, VMPA_NO_VIRTUAL);

            data = g_binary_content_get_raw_access(content, &pos, len);

            binary.data = data;
            binary.len = len;

            *out = g_scan_literal_expression_new(LVT_STRING, &binary);

            g_object_unref(G_OBJECT(content));
            break;

        case SHT_START:
            *out = g_scan_literal_expression_new(LVT_UNSIGNED_INTEGER, (unsigned long long []){ start });
            break;

        case SHT_LENGTH:
            *out = g_scan_literal_expression_new(LVT_UNSIGNED_INTEGER, (unsigned long long []){ len });
            break;

        case SHT_END:
            *out = g_scan_literal_expression_new(LVT_UNSIGNED_INTEGER, (unsigned long long []){ end });
            break;

    }

 done:

    return result;

}
