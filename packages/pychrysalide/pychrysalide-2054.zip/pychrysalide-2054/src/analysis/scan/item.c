
/* Chrysalide - Outil d'analyse de fichiers binaires
 * item.c - définition d'un élément appelable lors de l'exécution d'une règle
 *
 * Copyright (C) 2022 Cyrille Bagard
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


#include "item.h"


#include <assert.h>


#include "item-int.h"



/* ----------------------- BASES D'OBJET POUR LE SYSTEME GLIB ----------------------- */


/* Initialise la classe des éléments appelables enregistrés. */
static void g_registered_item_class_init(GRegisteredItemClass *);

/* Initialise une instance d'élément appelable enregistré. */
static void g_registered_item_init(GRegisteredItem *);

/* Supprime toutes les références externes. */
static void g_registered_item_dispose(GRegisteredItem *);

/* Procède à la libération totale de la mémoire. */
static void g_registered_item_finalize(GRegisteredItem *);



/* ---------------------------------------------------------------------------------- */
/*                         BASES D'OBJET POUR LE SYSTEME GLIB                         */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un élément appelable et enregistré. */
G_DEFINE_TYPE(GRegisteredItem, g_registered_item, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des éléments appelables enregistrés.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_registered_item_class_init(GRegisteredItemClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_registered_item_dispose;
    object->finalize = (GObjectFinalizeFunc)g_registered_item_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance d'élément appelable enregistré.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_registered_item_init(GRegisteredItem *item)
{

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

static void g_registered_item_dispose(GRegisteredItem *item)
{
    G_OBJECT_CLASS(g_registered_item_parent_class)->dispose(G_OBJECT(item));

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

static void g_registered_item_finalize(GRegisteredItem *item)
{
    G_OBJECT_CLASS(g_registered_item_parent_class)->finalize(G_OBJECT(item));

}


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

char *g_registered_item_get_name(const GRegisteredItem *item)
{
    char *result;                           /* Désignation à retourner     */
    GRegisteredItemClass *class;            /* Classe à activer            */

    class = G_REGISTERED_ITEM_GET_CLASS(item);

    result = class->get_name(item);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item   = élément d'appel à consulter.                        *
*                target = désignation de l'objet d'appel à identifier.        *
*                ctx    = contexte de suivi de l'analyse courante.            *
*                scope  = portée courante des variables locales.              *
*                out    = zone d'enregistrement de la résolution opérée. [OUT]*
*                                                                             *
*  Description : Lance une résolution d'élément à solliciter.                 *
*                                                                             *
*  Retour      : Bilan de l'opération : false en cas d'erreur irrécupérable.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_registered_item_resolve(GRegisteredItem *item, const char *target, GScanContext *ctx, GScanScope *scope, GRegisteredItem **out)
{
    bool result;                            /* Bilan à retourner           */
    GRegisteredItemClass *class;            /* Classe à activer            */

    *out = NULL;

    class = G_REGISTERED_ITEM_GET_CLASS(item);

    if (class->resolve == NULL)
        result = false;
    else
    {
        result = class->resolve(item, target, ctx, scope, out);

#ifndef NDEBUG
        if (*out != NULL)
            assert(result);
#endif

    }

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

bool g_registered_item_reduce(GRegisteredItem *item, GScanContext *ctx, GScanScope *scope, GScanExpression **out)
{
    bool result;                            /* Bilan à retourner           */
    GRegisteredItemClass *class;            /* Classe à activer            */

    *out = NULL;

    class = G_REGISTERED_ITEM_GET_CLASS(item);

    if (class->reduce == NULL)
        result = false;
    else
    {
        result = class->reduce(item, ctx, scope, out);

#ifndef NDEBUG
        if (*out != NULL)
            assert(result);
#endif

    }

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
*  Description : Effectue un appel à une fonction enregistrée.                *
*                                                                             *
*  Retour      : Bilan de l'opération : false en cas d'erreur irrécupérable.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_registered_item_run_call(GRegisteredItem *item, GScanExpression **args, size_t count, GScanContext *ctx, GScanScope *scope, GObject **out)
{
    bool result;                            /* Bilan à retourner           */
    GRegisteredItemClass *class;            /* Classe à activer            */

    *out = NULL;

    class = G_REGISTERED_ITEM_GET_CLASS(item);

    if (class->run_call == NULL)
        result = false;
    else
    {
        result = class->run_call(item, args, count, ctx, scope, out);

#ifndef NDEBUG
        if (*out != NULL)
            assert(result);
#endif

    }

    return result;

}
