
/* Chrysalide - Outil d'analyse de fichiers binaires
 * item.c - récupération d'un élément à partir d'une série
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


#include "literal.h"
#include "item-int.h"



/* --------------------- INTRODUCTION D'UNE NOUVELLE EXPRESSION --------------------- */


/* Initialise la classe des accès à un élément de série. */
static void g_scan_set_item_class_init(GScanSetItemClass *);

/* Initialise une instance d'accès à un élément de série. */
static void g_scan_set_item_init(GScanSetItem *);

/* Supprime toutes les références externes. */
static void g_scan_set_item_dispose(GScanSetItem *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_set_item_finalize(GScanSetItem *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Réduit une expression à une forme plus simple. */
static ScanReductionState g_scan_set_item_reduce(const GScanSetItem *, GScanContext *, GScanScope *, GScanExpression **);



/* ---------------------------------------------------------------------------------- */
/*                       INTRODUCTION D'UNE NOUVELLE EXPRESSION                       */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour la récupération d'un élément à partir d'une série. */
G_DEFINE_TYPE(GScanSetItem, g_scan_set_item, G_TYPE_SCAN_EXPRESSION);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des accès à un élément de série.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_set_item_class_init(GScanSetItemClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GScanExpressionClass *expr;             /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_set_item_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_set_item_finalize;

    expr = G_SCAN_EXPRESSION_CLASS(klass);

    expr->reduce = (reduce_expr_fc)g_scan_set_item_reduce;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance d'accès à un élément de série.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_set_item_init(GScanSetItem *item)
{
    item->set = NULL;
    item->index = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_set_item_dispose(GScanSetItem *item)
{
    g_clear_object(&item->set);
    g_clear_object(&item->index);

    G_OBJECT_CLASS(g_scan_set_item_parent_class)->dispose(G_OBJECT(item));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_set_item_finalize(GScanSetItem *item)
{
    G_OBJECT_CLASS(g_scan_set_item_parent_class)->finalize(G_OBJECT(item));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : set   = ensemble d'éléments à considérer.                    *
*                index = indice de l'élément à viser.                         *
*                                                                             *
*  Description : Met en place un accès à un élément donné d'une série.        *
*                                                                             *
*  Retour      : Expression mise en place.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanExpression *g_scan_set_item_new(GScanExpression *set, GScanExpression *index)
{
    GScanExpression *result;                /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_SET_ITEM, NULL);

    if (!g_scan_set_item_create(G_SCAN_SET_ITEM(result), set, index))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item  = instance à initialiser pleinement.                   *
*                set   = ensemble d'éléments à considérer.                    *
*                index = indice de l'élément à viser.                         *
*                                                                             *
*  Description : Met en place un accès à un élément donné d'une série.        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_set_item_create(GScanSetItem *item, GScanExpression *set, GScanExpression *index)
{
    bool result;                            /* Bilan à retourner           */

    result = g_scan_expression_create(G_SCAN_EXPRESSION(item), SRS_PENDING);
    if (!result) goto exit;

    item->set = set;
    g_object_ref(G_OBJECT(set));

    item->index = index;
    g_object_ref(G_OBJECT(index));

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

static ScanReductionState g_scan_set_item_reduce(const GScanSetItem *expr, GScanContext *ctx, GScanScope *scope, GScanExpression **out)
{
    ScanReductionState result;              /* Etat synthétisé à retourner */
    GScanExpression *new_set;               /* Expression réduite (série) */
    GScanExpression *new_index;             /* Expression réduite (indice) */
    ScanReductionState state_set;           /* Etat synthétisé #1          */
    ScanReductionState state_index;         /* Etat synthétisé #2          */
    GScanLiteralExpression *op_index;       /* Indice d'accès final        */
    LiteralValueType vtype;                 /* Type de valeur portée       */
    long long val_s;                        /* Valeur de l'indice (signée) */
    unsigned long long val_u;               /* Valeur de l'indice (!signée)*/
    bool status;                            /* Statut final de récupération*/

    /* Réduction des éléments considérés */

    new_set = NULL;
    new_index = NULL;

    state_set = g_scan_expression_reduce(expr->set, ctx, scope, &new_set);
    if (state_set == SRS_UNRESOLVABLE)
    {
        result = SRS_UNRESOLVABLE;
        goto exit;
    }

    state_index = g_scan_expression_reduce(expr->index, ctx, scope, &new_index);
    if (state_index == SRS_UNRESOLVABLE)
    {
        result = SRS_UNRESOLVABLE;
        goto exit;
    }

    /* Validation de la nature des éléments en jeu */

    if (state_set == SRS_REDUCED && !g_scan_expression_handle_set_features(new_set))
    {
        result = SRS_UNRESOLVABLE;
        goto exit;
    }

    if (state_index == SRS_REDUCED && !G_IS_SCAN_LITERAL_EXPRESSION(new_index))
    {
        result = SRS_UNRESOLVABLE;
        goto exit;
    }

    /* Tentative d'accès à un élément de série */

    if (state_set == SRS_REDUCED && state_index == SRS_REDUCED)
    {
        op_index = G_SCAN_LITERAL_EXPRESSION(new_index);
        vtype = g_scan_literal_expression_get_value_type(op_index);

        if (vtype == LVT_SIGNED_INTEGER)
        {
            if (!g_scan_literal_expression_get_signed_integer_value(op_index, &val_s))
            {
                result = SRS_UNRESOLVABLE;
                goto exit;
            }

            if (val_s < 0)
            {
                result = SRS_UNRESOLVABLE;
                goto exit;
            }

            status = g_scan_expression_get_item(expr->set, val_s, ctx, out);

        }
        else if (vtype == LVT_UNSIGNED_INTEGER)
        {
            if (!g_scan_literal_expression_get_unsigned_integer_value(op_index, &val_u))
            {
                result = SRS_UNRESOLVABLE;
                goto exit;
            }

            status = g_scan_expression_get_item(expr->set, val_u, ctx, out);

        }

        result = (status ? SRS_REDUCED : SRS_UNRESOLVABLE);

    }

    /* Mise à jour de la progression ? */

    else
    {
        assert(state_set == SRS_WAIT_FOR_SCAN || state_index == SRS_WAIT_FOR_SCAN);

        if (new_set != expr->set || new_index != expr->index)
            *out = g_scan_set_item_new(new_set, new_index);

        result = SRS_WAIT_FOR_SCAN;

    }

    /* Sortie propre */

 exit:

    g_clear_object(&new_set);
    g_clear_object(&new_index);

    return result;

}
