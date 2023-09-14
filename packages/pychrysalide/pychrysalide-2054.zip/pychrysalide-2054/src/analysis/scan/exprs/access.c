
/* Chrysalide - Outil d'analyse de fichiers binaires
 * access.c - accès à un élément d'expression sous-jacent
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


#include "access.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>


#include "access-int.h"
#include "literal.h"
#include "../../../core/global.h"



/* --------------------- INTRODUCTION D'UNE NOUVELLE EXPRESSION --------------------- */


/* Initialise la classe des appels de fonction avec arguments. */
static void g_scan_named_access_class_init(GScanNamedAccessClass *);

/* Initialise une instance d'appel de fonction avec arguments. */
static void g_scan_named_access_init(GScanNamedAccess *);

/* Supprime toutes les références externes. */
static void g_scan_named_access_dispose(GScanNamedAccess *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_named_access_finalize(GScanNamedAccess *);

/* Reproduit un accès en place dans une nouvelle instance. */
static void g_scan_named_access_copy(GScanNamedAccess *, const GScanNamedAccess *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Réduit une expression à une forme plus simple. */
static ScanReductionState g_scan_named_access_reduce(const GScanNamedAccess *, GScanContext *, GScanScope *, GScanExpression **);



/* ---------------------------------------------------------------------------------- */
/*                       INTRODUCTION D'UNE NOUVELLE EXPRESSION                       */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un appel de fonction enregistrée. */
G_DEFINE_TYPE(GScanNamedAccess, g_scan_named_access, G_TYPE_SCAN_EXPRESSION);


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

static void g_scan_named_access_class_init(GScanNamedAccessClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GScanExpressionClass *expr;             /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_named_access_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_named_access_finalize;

    expr = G_SCAN_EXPRESSION_CLASS(klass);

    expr->cmp_rich = (compare_expr_rich_fc)NULL;
    expr->reduce = (reduce_expr_fc)g_scan_named_access_reduce;

    klass->copy = g_scan_named_access_copy;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : access = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une instance d'appel de fonction avec arguments.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_named_access_init(GScanNamedAccess *access)
{
    access->any = NULL;
    access->target = NULL;

    access->next = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : access = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_named_access_dispose(GScanNamedAccess *access)
{
    g_clear_object(&access->any);

    g_clear_object(&access->next);

    G_OBJECT_CLASS(g_scan_named_access_parent_class)->dispose(G_OBJECT(access));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : access = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_named_access_finalize(GScanNamedAccess *access)
{
    if (access->target != NULL)
        free(access->target);

    G_OBJECT_CLASS(g_scan_named_access_parent_class)->finalize(G_OBJECT(access));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : target = désignation de l'objet d'appel à identifier.        *
*                                                                             *
*  Description : Organise un accès à un élément d'expression sous-jacent.     *
*                                                                             *
*  Retour      : Fonction mise en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanExpression *g_scan_named_access_new(const sized_string_t *target)
{
    GScanExpression *result;                /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_NAMED_ACCESS, NULL);

    if (!g_scan_named_access_create(G_SCAN_NAMED_ACCESS(result), target))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : access = instance à initialiser pleinement.                  *
*                target = désignation de l'objet d'appel à identifier.        *
*                                                                             *
*  Description : Met en place une expression d'accès.                         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_named_access_create(GScanNamedAccess *access, const sized_string_t *target)
{
    bool result;                            /* Bilan à retourner           */

    result = g_scan_expression_create(G_SCAN_EXPRESSION(access), SRS_PENDING);
    if (!result) goto exit;

    if (target != NULL)
        access->target = strndup(target->data, target->len);

 exit:

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

static void g_scan_named_access_copy(GScanNamedAccess *dest, const GScanNamedAccess *src)
{
    /**
     * Les champs suivants sont voués à être remplacés ou supprimés.
     *
     * On évite donc une instanciation inutile.
     */

    /*
    if (src->any != NULL)
    {
        dest->any = src->any;
        g_object_ref(src->any);
    }
    */

    if (src->target != NULL)
        dest->target = strdup(src->target);

    if (src->next != NULL)
    {
        dest->next = src->next;
        g_object_ref(src->next);
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : accès    = expression d'accès à copier.                      *
*                resolved = nouvelle base à imposer.                          *
*                                                                             *
*  Description : Reproduit un accès en place dans une nouvelle instance.      *
*                                                                             *
*  Retour      : Nouvelle instance d'expression d'accès.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanExpression *g_scan_named_access_duplicate(const GScanNamedAccess *access, GRegisteredItem *resolved)
{
    GScanExpression *result;                /* Instance copiée à retourner */
    GType type;                             /* Type d'objet à copier       */
    GScanNamedAccessClass *class;           /* Classe à activer            */

    type = G_TYPE_FROM_INSTANCE(access);

    result = g_object_new(type, NULL);

    class = G_SCAN_NAMED_ACCESS_GET_CLASS(access);

    class->copy(G_SCAN_NAMED_ACCESS(result), access);

    g_scan_named_access_set_base(G_SCAN_NAMED_ACCESS(result), resolved);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : access = expression d'appel à actualiser.                    *
*                base   = zone de recherche pour la résolution à venir.       *
*                                                                             *
*  Description : Définit une base de recherche pour la cible d'accès.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_scan_named_access_set_base(GScanNamedAccess *access, GRegisteredItem *base)
{
    g_clear_object(&access->base);

    access->base = base;
    g_object_ref(G_OBJECT(base));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : access = expression d'appel à compléter.                     *
*                next   = expression d'appel suivante dans la chaîne.         *
*                                                                             *
*  Description : Complète la chaine d'accès à des expressions.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_scan_named_access_attach_next(GScanNamedAccess *access, GScanNamedAccess *next)
{
    if (access->next != NULL)
        g_scan_named_access_attach_next(access->next, next);

    else
    {
        access->next = next;
        g_object_ref(G_OBJECT(next));
    }

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : expr  = expression à consulter.                              *
*                ctx   = contexte de suivi de l'analyse courante.             *
*                scope = portée courante des variables locales.               *
*                                                                             *
*  Description : Prépare une réduction en menant une résolution locale.       *
*                                                                             *
*  Retour      : Elément résolu avec les moyens du bord ou NULL si échec.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GRegisteredItem *_g_scan_named_access_prepare_reduction(const GScanNamedAccess *expr, GScanContext *ctx, GScanScope *scope)
{
    GRegisteredItem *result;                /* Etat synthétisé à retourner */
    GRegisteredItem *base;                  /* Base de recherche courante  */

    result = NULL;

    if (expr->target != NULL)
    {
        if (expr->base != NULL)
        {
            base = expr->base;
            g_object_ref(G_OBJECT(base));
        }
        else
            base = G_REGISTERED_ITEM(get_rost_root_namespace());

        g_registered_item_resolve(base, expr->target, ctx, scope, &result);

    }

    /**
     * Si plus aucune indication n'est diponible pour avancer dans les réductions,
     * c'est que l'opération est déjà conclue.
     */
    else
    {
        assert(expr->resolved != NULL);

        result = expr->resolved;
        g_object_ref(G_OBJECT(result));

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
*  Description : Réduit une expression à une forme plus simple.               *
*                                                                             *
*  Retour      : Bilan de l'opération : false en cas d'erreur irrécupérable.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static ScanReductionState g_scan_named_access_reduce(const GScanNamedAccess *expr, GScanContext *ctx, GScanScope *scope, GScanExpression **out)
{
    ScanReductionState result;              /* Etat synthétisé à retourner */
    GRegisteredItem *resolved;              /* Cible concrète obtenue      */
    GScanExpression *new_next;              /* Nouvelle version du suivant */
    const char *current_rule;               /* Nom de la règle courante    */
    bool status;                            /* Bilan d'une autre règle     */

    resolved = _g_scan_named_access_prepare_reduction(expr, ctx, scope);

    if (resolved != NULL)
    {
        result = SRS_PENDING;

        /**
         * Si l'élément résolu se trouve en fin de chaîne, alors cet élément
         * est sollicité pour obtenir une expression d'évaluation classique.
         * Le produit de cette réduction finale bénéficie d'une promotion et
         * représente à lui seul la réduction produite pour la chaîne.
         */
        if (expr->next == NULL)
        {
            status = g_registered_item_reduce(resolved, ctx, scope, out);

            result = (status ? SRS_REDUCED : SRS_UNRESOLVABLE);

        }

        /**
         * Sinon, l'élément résolu constitue une base pour l'étage suivant de
         * la chaîne de résolution.
         */
        else
        {
            new_next = g_scan_named_access_duplicate(expr->next, resolved);

            result = g_scan_expression_reduce(new_next, ctx, scope, out);

            g_object_unref(G_OBJECT(new_next));

        }

        g_object_unref(G_OBJECT(resolved));

    }

    /**
     * Si le nom fournit le correspond à aucun élément de la grammaire,
     * des recherches sont menées ailleurs.
     */
    else
    {
        result = SRS_UNRESOLVABLE;

        if (g_scan_context_has_rule_for_name(ctx, expr->target))
        {
            current_rule = g_scan_scope_get_rule_name(scope);

            /* Si référence circulaire il y a... */
            if (strcmp(current_rule, expr->target) == 0)
                result = SRS_UNRESOLVABLE;

            else
            {
                status = g_scan_context_has_match_for_rule(ctx, expr->target);

                *out = g_scan_literal_expression_new(LVT_BOOLEAN, &status);
                result = SRS_REDUCED;

            }

        }

    }

    return result;

}
