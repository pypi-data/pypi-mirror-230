
/* Chrysalide - Outil d'analyse de fichiers binaires
 * context.c - contexte de décodage à la sauce ABI C++ Itanium
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
#include <malloc.h>
#include <string.h>


#include <mangling/context-int.h>


#include "abi.h"
#include "component-int.h"



/* Contexte de décodage Itanium (instance) */
struct _GItaniumDemangling
{
    GDemanglingContext parent;              /* A laisser en premier        */

    itanium_component **template_args;      /* Paramètres de modèle        */
    size_t targs_count;                     /* Quantité utilisée           */

    itanium_component **substitutions;      /* Table de substitutions      */
    size_t subst_count;                     /* Quantité utilisée           */

};

/* Contexte de décodage Itanium (classe) */
struct _GItaniumDemanglingClass
{
    GDemanglingContextClass parent;         /* A laisser en premier        */

};


/* Initialise la classe des contextes de décodage. */
static void g_itanium_demangling_class_init(GItaniumDemanglingClass *);

/* Initialise une instance de contexte pour décodage. */
static void g_itanium_demangling_init(GItaniumDemangling *);

/* Supprime toutes les références externes. */
static void g_itanium_demangling_dispose(GItaniumDemangling *);

/* Procède à la libération totale de la mémoire. */
static void g_itanium_demangling_finalize(GItaniumDemangling *);

/* Prépare l'environnement de contexte pour un décodage Itanium. */
static void g_itanium_demangling_prepare(GItaniumDemangling *);

/* Valide un composant final issu d'un décodage Itanium. */
static void g_itanium_demangling_check(GItaniumDemangling *, itanium_component **);

/* Décode une définition de type pour Itanium. */
static GDataType *g_itanium_demangling_decode_type(GItaniumDemangling *);

/* Décode une définition de routine pour Itanium. */
static GBinRoutine *g_itanium_demangling_decode_routine(GItaniumDemangling *);



/* Indique le type défini pour un contexte de décodage. */
G_DEFINE_TYPE(GItaniumDemangling, g_itanium_demangling, G_TYPE_DEMANGLING_CONTEXT);


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

static void g_itanium_demangling_class_init(GItaniumDemanglingClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDemanglingContextClass *context;       /* Version de base du contexte */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_itanium_demangling_dispose;
    object->finalize = (GObjectFinalizeFunc)g_itanium_demangling_finalize;

    context = G_DEMANGLING_CONTEXT_CLASS(klass);

    context->decode_type = (decode_type_fc)g_itanium_demangling_decode_type;
    context->decode_routine = (decode_routine_fc)g_itanium_demangling_decode_routine;

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

static void g_itanium_demangling_init(GItaniumDemangling *context)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_itanium_demangling_dispose(GItaniumDemangling *context)
{
    G_OBJECT_CLASS(g_itanium_demangling_parent_class)->dispose(G_OBJECT(context));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_itanium_demangling_finalize(GItaniumDemangling *context)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < context->targs_count; i++)
        itd_unref_comp(context->template_args[i]);

    if (context->template_args != NULL)
        free(context->template_args);

    for (i = 0; i < context->subst_count; i++)
        itd_unref_comp(context->substitutions[i]);

    if (context->substitutions != NULL)
        free(context->substitutions);

    G_OBJECT_CLASS(g_itanium_demangling_parent_class)->finalize(G_OBJECT(context));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = environnement de décodage à manipuler.             *
*                                                                             *
*  Description : Prépare l'environnement de contexte pour un décodage Itanium.*
*                                                                             *
*  Retour      : -                                                     .      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_itanium_demangling_prepare(GItaniumDemangling *context)
{
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    size_t len;                             /* Taille de chaîne à traiter  */

    /**
     * On part du principe qu'il n'y aura jamais plus de paramètres de modèle
     * ou de substitutions à enregistrer que de caractères dans la chaîne à traiter.
     * Du coup, on peut tout allouer d'un coup !
     */

    assert(context->template_args == NULL);

    assert(context->substitutions == NULL);

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    len = get_input_buffer_size(ibuf);

    context->template_args = (itanium_component **)malloc(len * sizeof(itanium_component *));

    context->substitutions = (itanium_component **)malloc(len * sizeof(itanium_component *));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = environnement de décodage à manipuler.             *
*                comp    = composant final à valider. [OUT]                   *
*                                                                             *
*  Description : Valide un composant final issu d'un décodage Itanium.        *
*                                                                             *
*  Retour      : -                                                     .      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_itanium_demangling_check(GItaniumDemangling *context, itanium_component **comp)
{
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */
    size_t remaining;                       /* Données restant à consommer */

    if (*comp != NULL)
    {
        ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

        remaining = count_input_buffer_remaining(ibuf);

        if (remaining > 0)
        {
            itd_unref_comp(*comp);
            *comp = NULL;
        }

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = environnement de décodage à manipuler.             *
*                                                                             *
*  Description : Décode une définition de type pour Itanium.                  *
*                                                                             *
*  Retour      : Nouvelle instance créée ou NULL en cas d'erreur fatale.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GDataType *g_itanium_demangling_decode_type(GItaniumDemangling *context)
{
    GDataType *result;                      /* Type construit à retourner  */
    itanium_component *comp;                /* Composants décodés          */

    g_itanium_demangling_prepare(context);

    comp = itd_mangled_name(context);

    g_itanium_demangling_check(context, &comp);

    if (comp == NULL)
        result = NULL;

    else
    {
        result = itd_translate_component_to_type(comp, NULL);

        itd_unref_comp(comp);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = environnement de décodage à manipuler.             *
*                                                                             *
*  Description : Décode une définition de routine pour Itanium.               *
*                                                                             *
*  Retour      : Nouvelle instance créée ou NULL en cas d'erreur fatale.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GBinRoutine *g_itanium_demangling_decode_routine(GItaniumDemangling *context)
{
    GBinRoutine *result;                    /* Routine en place à retourner*/
    itanium_component *comp;                /* Composants décodés          */

    g_itanium_demangling_prepare(context);

    comp = itd_mangled_name(context);

    g_itanium_demangling_check(context, &comp);

    if (comp == NULL)
        result = NULL;

    else
    {
        result = itd_translate_component_to_routine(comp);

        itd_unref_comp(comp);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à manipuler.                  *
*                state   = état courant à sauvegarder. [OUT]                  *
*                                                                             *
*  Description : Fournit l'état courant à une fin de retour en arrière.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_itanium_demangling_push_state(const GItaniumDemangling *context, itd_state *state)
{
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    save_input_buffer_pos(ibuf, &state->pos);
    state->targs_count = context->targs_count;
    state->subst_count = context->subst_count;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à manipuler.                  *
*                state   = état courant à restaurer.                          *
*                                                                             *
*  Description : Définit l'état courant suite à un retour en arrière.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_itanium_demangling_pop_state(GItaniumDemangling *context, const itd_state *state)
{
    size_t i;                               /* Boucle de parcours          */
    input_buffer *ibuf;                     /* Tampon de texte manipulé    */

    for (i = state->targs_count; i < context->targs_count; i++)
        itd_unref_comp(context->template_args[i]);

    for (i = state->subst_count; i < context->subst_count; i++)
        itd_unref_comp(context->substitutions[i]);

    ibuf = &G_DEMANGLING_CONTEXT(context)->buffer;

    restore_input_buffer_pos(ibuf, state->pos);
    context->targs_count = state->targs_count;
    context->subst_count = state->subst_count;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à manipuler.                  *
*                comp    = composant à conserver en mémoire.                  *
*                                                                             *
*  Description : Indexe un composant représentant un argument de modèle.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_itanium_demangling_add_template_args(GItaniumDemangling *context, itanium_component *comp)
{
    assert(comp != NULL);

    assert(itd_get_component_type(comp) == ICT_TEMPLATE_ARGS);

    context->template_args[context->targs_count++] = comp;
    itd_ref_comp(comp);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à manipuler.                  *
*                index   = indice de l'argument visé.                         *
*                                                                             *
*  Description : Fournit un composant représentant un argument de modèle.     *
*                                                                             *
*  Retour      : Composant déjà extrait et conservé.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

itanium_component *g_itanium_demangling_get_template_arg(GItaniumDemangling *context, size_t index)
{
    itanium_component *result;              /* Composant à retourner       */
    itanium_component *targs;               /* Racine des arguments        */
    itanium_component *iter;                /* Boucle de parcours #1       */

    if (context->targs_count == 0)
        result = NULL;

    else
    {
        targs = context->template_args[context->targs_count - 1];

        for (iter = targs->unary; iter != NULL; iter = iter->binary.right)
        {
            assert(itd_get_component_type(iter) == ICT_TYPES_LIST);

            if (index == 0)
                break;

            index--;

        }

        if (iter != NULL)
        {
            result = iter->binary.left;
            itd_ref_comp(result);
        }

        else
            result = NULL;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à manipuler.                  *
*                comp    = composant à conserver en mémoire.                  *
*                                                                             *
*  Description : Indexe un composant comme future substitution potentielle.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_itanium_demangling_add_substitution(GItaniumDemangling *context, itanium_component *comp)
{
    size_t i;                               /* Boucle de parcours          */

    assert(comp != NULL);

    if (itd_get_component_type(comp) == ICT_STD_SUBST)
        return;

    for (i = 0; i < context->subst_count; i++)
        if (comp == context->substitutions[i])
            break;

    if (i == context->subst_count)
    {
        context->substitutions[context->subst_count++] = comp;
        itd_ref_comp(comp);
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte de décodage à manipuler.                  *
*                index   = indice de la substitution visée.                   *
*                                                                             *
*  Description : Fournit un composant en place pour une substitution.         *
*                                                                             *
*  Retour      : Composant déjà extrait et conservé.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

itanium_component *g_itanium_demangling_get_substitution(GItaniumDemangling *context, size_t index)
{
    itanium_component *result;              /* Composant à retourner       */

    if (index < context->subst_count)
    {
        result = context->substitutions[index];
        itd_ref_comp(result);
    }
    else
        result = NULL;

    return result;

}
