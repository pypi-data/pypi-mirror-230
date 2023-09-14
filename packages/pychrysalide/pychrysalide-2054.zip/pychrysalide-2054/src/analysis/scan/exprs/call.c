
/* Chrysalide - Outil d'analyse de fichiers binaires
 * call.c - organisation d'un appel à un élément de scan enregistré
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


#include "call.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>


#include "call-int.h"
#include "../../../core/global.h"



/* --------------------- INTRODUCTION D'UNE NOUVELLE EXPRESSION --------------------- */


/* Initialise la classe des appels de fonction avec arguments. */
static void g_scan_pending_call_class_init(GScanPendingCallClass *);

/* Initialise une instance d'appel de fonction avec arguments. */
static void g_scan_pending_call_init(GScanPendingCall *);

/* Supprime toutes les références externes. */
static void g_scan_pending_call_dispose(GScanPendingCall *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_pending_call_finalize(GScanPendingCall *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Réduit une expression à une forme plus simple. */
static ScanReductionState g_scan_pending_call_reduce(const GScanPendingCall *, GScanContext *, GScanScope *, GScanExpression **);

/* Reproduit un accès en place dans une nouvelle instance. */
static void g_scan_pending_call_copy(GScanPendingCall *, const GScanPendingCall *);



/* ---------------------------------------------------------------------------------- */
/*                       INTRODUCTION D'UNE NOUVELLE EXPRESSION                       */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un appel de fonction enregistrée. */
G_DEFINE_TYPE(GScanPendingCall, g_scan_pending_call, G_TYPE_SCAN_NAMED_ACCESS);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des appels de fonction avec arguments.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_pending_call_class_init(GScanPendingCallClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GScanExpressionClass *expr;             /* Version de classe parente   */
    GScanNamedAccessClass *access;          /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_pending_call_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_pending_call_finalize;

    expr = G_SCAN_EXPRESSION_CLASS(klass);

    expr->cmp_rich = (compare_expr_rich_fc)NULL;
    expr->reduce = (reduce_expr_fc)g_scan_pending_call_reduce;

    access = G_SCAN_NAMED_ACCESS_CLASS(klass);

    access->copy = (copy_scan_access_fc)g_scan_pending_call_copy;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : call = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance d'appel de fonction avec arguments.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_pending_call_init(GScanPendingCall *call)
{
    call->args = NULL;
    call->count = 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : call = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_pending_call_dispose(GScanPendingCall *call)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < call->count; i++)
        g_clear_object(&call->args[i]);

    G_OBJECT_CLASS(g_scan_pending_call_parent_class)->dispose(G_OBJECT(call));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : call = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_pending_call_finalize(GScanPendingCall *call)
{
    if (call->args != NULL)
        free(call->args);

    G_OBJECT_CLASS(g_scan_pending_call_parent_class)->finalize(G_OBJECT(call));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : target = désignation de l'objet d'appel à identifier.        *
*                args   = éventuelle liste d'arguments à actionner.           *
*                count  = quantité de ces arguments.                          *
*                                                                             *
*  Description : Organise un appel de fonction avec ses arguments.            *
*                                                                             *
*  Retour      : Fonction mise en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanExpression *g_scan_pending_call_new(const sized_string_t *target, GScanExpression **args, size_t count)
{
    GScanExpression *result;                /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_PENDING_CALL, NULL);

    if (!g_scan_pending_call_create(G_SCAN_PENDING_CALL(result), target, args, count))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : call   = instance à initialiser pleinement.                  *
*                target = désignation de l'objet d'appel à identifier.        *
*                args   = éventuelle liste d'arguments à actionner.           *
*                count  = quantité de ces arguments.                          *
*                                                                             *
*  Description : Met en place une expression d'appel.                         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_pending_call_create(GScanPendingCall *call, const sized_string_t *target, GScanExpression **args, size_t count)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours          */

    result = g_scan_named_access_create(G_SCAN_NAMED_ACCESS(call), target);
    if (!result) goto exit;

    call->args = malloc(count * sizeof(GScanExpression *));
    call->count = count;

    for (i = 0; i < count; i++)
    {
        call->args[i] = args[i];
        g_object_ref(G_OBJECT(args[i]));
    }

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

static ScanReductionState g_scan_pending_call_reduce(const GScanPendingCall *expr, GScanContext *ctx, GScanScope *scope, GScanExpression **out)
{
    ScanReductionState result;              /* Etat synthétisé à retourner */
    GScanNamedAccess *access;               /* Autre vision de l'expression*/
    GRegisteredItem *resolved;              /* Cible concrète obtenue      */
    size_t i;                               /* Boucle de parcours #1       */
    GScanExpression *arg;                   /* Argument réduit à échanger  */
    GScanExpression *new;                   /* Nouvelle réduction obtenue  */
    ScanReductionState state;               /* Etat synthétisé d'un élément*/
    size_t k;                               /* Boucle de parcours #2       */
    GScanExpression **new_args;             /* Nouvelle séquence d'args.   */
    GScanExpression *new_next;              /* Nouvelle version du suivant */
    GObject *final;                         /* Expression ou élément ?     */
    bool valid;                             /* Validité de l'élément       */

    access = G_SCAN_NAMED_ACCESS(expr);

    resolved = _g_scan_named_access_prepare_reduction(access, ctx, scope);

    if (resolved == NULL)
        result = SRS_UNRESOLVABLE;

    else
    {
        result = SRS_PENDING;

        /* Actualisation nécessaire des arguments ? */

        new_args = NULL;

        for (i = 0; i < expr->count; i++)
        {
            arg = expr->args[i];

            state = g_scan_expression_reduce(arg, ctx, scope, &new);
            if (state == SRS_UNRESOLVABLE)
            {
                result = SRS_UNRESOLVABLE;
                break;
            }

            if (state == SRS_WAIT_FOR_SCAN)
                result = SRS_WAIT_FOR_SCAN;

            if (new != arg)
            {
                if (new_args == NULL)
                {
                    new_args = calloc(expr->count, sizeof(GScanExpression *));

                    for (k = 0; k < i; k++)
                    {
                        new_args[k] = expr->args[k];
                        g_object_ref(G_OBJECT(new_args[k]));
                    }

                }

                new_args[i] = new;

            }

            else
            {
                if (new_args != NULL)
                    new_args[i] = new;
            }

        }

        /* Suite des traitements */

        if (result == SRS_WAIT_FOR_SCAN)
        {
            /**
             * Si changement il y a eu...
             */
            if (new_args != NULL)
            {
                *out = g_scan_pending_call_new(NULL, new_args, expr->count);

                /**
                 * Fonctionnement équivalent de :
                 *    g_scan_named_access_set_base(G_SCAN_NAMED_ACCESS(*out), resolved);
                 */
                G_SCAN_NAMED_ACCESS(*out)->resolved = resolved;
                g_object_ref(G_OBJECT(resolved));

                if (G_SCAN_NAMED_ACCESS(expr)->next != NULL)
                    g_scan_named_access_attach_next(G_SCAN_NAMED_ACCESS(*out), G_SCAN_NAMED_ACCESS(expr)->next);

            }

        }

        else if (result == SRS_PENDING)
        {
            if (new_args == NULL)
                valid = g_registered_item_run_call(resolved,
                                                   expr->args,
                                                   expr->count,
                                                   ctx, scope, &final);
            else
                valid = g_registered_item_run_call(resolved,
                                                   new_args,
                                                   expr->count,
                                                   ctx, scope, &final);

            if (valid && final != NULL)
            {
                /**
                 * Si le produit de l'appel à la fonction est une expression d'évaluation
                 * classique, alors ce produit constitue la réduction finale de la chaîne.
                 *
                 * Ce cas de figure ne se rencontre normalement qu'en bout de chaîne.
                 */
                if (!G_IS_REGISTERED_ITEM(final))
                {
                    if (access->next != NULL)
                        result = SRS_UNRESOLVABLE;

                    else
                    {
                        *out = G_SCAN_EXPRESSION(final);
                        g_object_ref(G_OBJECT(final));

                        result = SRS_REDUCED;

                    }

                }
                else
                {
                    assert(access->next != NULL);

                    new_next = g_scan_named_access_duplicate(access->next, G_REGISTERED_ITEM(final));

                    result = g_scan_expression_reduce(new_next, ctx, scope, out);

                    g_object_unref(G_OBJECT(new_next));

                }

            }

            else
                result = SRS_UNRESOLVABLE;

            g_clear_object(&final);

        }

        /* Libération locale des arguments reconstruits */

        if (new_args != NULL)
        {
            for (i = 0; i < expr->count; i++)
                g_clear_object(&new_args[i]);
        }

        g_object_unref(G_OBJECT(resolved));

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dest = emplacement d'enregistrement à constituer. [OUT]      *
*                src  = expression source à copier.                           *
*                                                                             *
*  Description : Reproduit un accès en place dans une nouvelle instance.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_pending_call_copy(GScanPendingCall *dest, const GScanPendingCall *src)
{
    GScanNamedAccessClass *class;           /* Classe parente à solliciter */
    size_t i;                               /* Boucle de parcours          */

    class = G_SCAN_NAMED_ACCESS_CLASS(g_scan_pending_call_parent_class);

    class->copy(G_SCAN_NAMED_ACCESS(dest), G_SCAN_NAMED_ACCESS(src));

    dest->args = malloc(src->count * sizeof(GScanExpression *));
    dest->count = src->count;

    for (i = 0; i < src->count; i++)
    {
        dest->args[i] = src->args[i];
        g_object_ref(G_OBJECT(src->args[i]));
    }

}
