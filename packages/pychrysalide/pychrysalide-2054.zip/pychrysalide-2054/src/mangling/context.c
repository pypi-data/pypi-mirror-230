
/* Chrysalide - Outil d'analyse de fichiers binaires
 * context.c - fourniture de contexte aux phases de décodage
 *
 * Copyright (C) 2018 Cyrille Bagard
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
 *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.
 */


#include "context.h"


#include <assert.h>


#include "context-int.h"



/* Initialise la classe des contextes de décodage. */
static void g_demangling_context_class_init(GDemanglingContextClass *);

/* Initialise une instance de contexte pour décodage. */
static void g_demangling_context_init(GDemanglingContext *);

/* Supprime toutes les références externes. */
static void g_demangling_context_dispose(GDemanglingContext *);

/* Procède à la libération totale de la mémoire. */
static void g_demangling_context_finalize(GDemanglingContext *);



/* Indique le type défini pour un contexte de décodage. */
G_DEFINE_TYPE(GDemanglingContext, g_demangling_context, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des contextes de décodage.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_demangling_context_class_init(GDemanglingContextClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_demangling_context_dispose;
    object->finalize = (GObjectFinalizeFunc)g_demangling_context_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance de contexte pour décodage.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_demangling_context_init(GDemanglingContext *context)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : demangler = instance d'objet GLib à traiter.                 *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_demangling_context_dispose(GDemanglingContext *context)
{
    if (context->gobj != NULL)
        g_object_unref(context->gobj);

    G_OBJECT_CLASS(g_demangling_context_parent_class)->dispose(G_OBJECT(context));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : demangler = instance d'objet GLib à traiter.                 *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_demangling_context_finalize(GDemanglingContext *context)
{
    G_OBJECT_CLASS(g_demangling_context_parent_class)->finalize(G_OBJECT(context));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = instance à consulter.                              *
*                desc    = chaîne de caractères à décoder.                    *
*                                                                             *
*  Description : Fournit la routine créée à l'issue du codage.                *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinRoutine *g_demangling_context_get_decoded_routine(GDemanglingContext *context, const char *desc)
{
    GBinRoutine *result;                    /* Construction à remonter     */

    context->routine = g_binary_routine_new();

    if (G_DEMANGLING_CONTEXT_GET_CLASS(context)->demangle_routine(context, desc))
    {
        g_object_ref(context->routine);
        result = context->routine;
    }

    else
        result = NULL;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = instance à consulter.                              *
*                desc    = chaîne de caractères à décoder.                    *
*                                                                             *
*  Description : Fournit le type créé à l'issue du codage.                    *
*                                                                             *
*  Retour      : Instance en place ou NULL en cas d'erreur fatale.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDataType *g_demangling_context_get_decoded_type(GDemanglingContext *context, const char *desc)
{
    GDataType *result;                      /* Construction à remonter     */

    if (G_DEMANGLING_CONTEXT_GET_CLASS(context)->demangle_type(context, desc))
    {
        g_object_ref(context->type);
        result = context->type;
    }

    else
        result = NULL;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = environnement de décodage à manipuler.             *
*                desc    = chaîne de caractères à décoder.                    *
*                                                                             *
*  Description : Décode une définition de type.                               *
*                                                                             *
*  Retour      : Nouvelle instance créée ou NULL en cas d'erreur fatale.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDataType *g_demangling_context_decode_type(GDemanglingContext *context, const char *desc)
{
    GDataType *result;                      /* Construction à remonter     */

    if (context->type != NULL)
        result = context->type;

    else
    {
        assert(context->buffer.text == NULL);

        init_text_input_buffer(&context->buffer, desc);

        result = G_DEMANGLING_CONTEXT_GET_CLASS(context)->decode_type(context);

        if (result != NULL)
            context->type = result;

    }

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = environnement de décodage à manipuler.             *
*                desc    = chaîne de caractères à décoder.                    *
*                                                                             *
*  Description : Décode une définition de routine.                            *
*                                                                             *
*  Retour      : Nouvelle instance créée ou NULL en cas d'erreur fatale.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinRoutine *g_demangling_context_decode_routine(GDemanglingContext *context, const char *desc)
{
    GBinRoutine *result;                    /* Construction à remonter     */

    if (context->routine != NULL)
        result = context->routine;

    else
    {
        assert(context->buffer.text == NULL);

        init_text_input_buffer(&context->buffer, desc);

        result = G_DEMANGLING_CONTEXT_GET_CLASS(context)->decode_routine(context);

        if (result != NULL)
            context->routine = result;

    }

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}
