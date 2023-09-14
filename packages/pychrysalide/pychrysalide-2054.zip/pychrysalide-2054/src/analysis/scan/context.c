
/* Chrysalide - Outil d'analyse de fichiers binaires
 * context.c - suivi d'analyses via contextes
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


#include "context.h"


#include <assert.h>
#include <malloc.h>
#include <stdlib.h>
#include <string.h>


#include "context-int.h"
#include "exprs/literal.h"
#include "../../common/sort.h"





/* ------------------- ADMINISTRATION DES CORRESPONDANCES TOTALES ------------------- */


/* Initialise un suivi de trouvailles pour un premier motif. */
static full_match_tracker_t *create_full_match_tracker(GSearchPattern *);

/* Termine le suivi de trouvailles pour un motif. */
static void delete_full_match_tracker(full_match_tracker_t *);

/* Etablit la comparaison entre deux structures de suivi. */
static int compare_full_match_trackers(const full_match_tracker_t **, const full_match_tracker_t **);

/* Note l'existence d'une nouvelle correspondance pour un motif. */
static void add_match_to_full_match_tracker(full_match_tracker_t *, GScanMatch *);



/* --------------------- MEMORISATION DE PROGRESSIONS D'ANALYSE --------------------- */


/* Initialise la classe des contextes de suivi d'analyses. */
static void g_scan_context_class_init(GScanContextClass *);

/* Initialise une instance de contexte de suivi d'analyse. */
static void g_scan_context_init(GScanContext *);

/* Supprime toutes les références externes. */
static void g_scan_context_dispose(GScanContext *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_context_finalize(GScanContext *);



/* ---------------------------------------------------------------------------------- */
/*                     ADMINISTRATION DES CORRESPONDANCES TOTALES                     */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : pattern = motif de recherche trouvé.                         *
*                                                                             *
*  Description : Initialise un suivi de trouvailles pour un premier motif.    *
*                                                                             *
*  Retour      : Structure de suivi mise en place.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static full_match_tracker_t *create_full_match_tracker(GSearchPattern *pattern)
{
    full_match_tracker_t *result;           /* Structure à retourner       */

    result = malloc(sizeof(full_match_tracker_t));

    result->pattern = pattern;
    g_object_ref(G_OBJECT(pattern));

    result->matches = malloc(ALLOCATION_STEP * sizeof(GScanMatch *));
    result->allocated = ALLOCATION_STEP;
    result->used = 0;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tracker = structure de gestion à manipuler.                  *
*                                                                             *
*  Description : Termine le suivi de trouvailles pour un motif.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void delete_full_match_tracker(full_match_tracker_t *tracker)
{
    size_t i;                               /* Boucle de parcours          */

    g_object_unref(G_OBJECT(tracker->pattern));

    for (i = 0; i < tracker->used; i++)
        g_object_unref(G_OBJECT(tracker->matches[i]));

    free(tracker->matches);

    free(tracker);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = première structure de suivi à consulter.                 *
*                b = seconde structure de suivi à consulter.                  *
*                                                                             *
*  Description : Etablit la comparaison entre deux structures de suivi.       *
*                                                                             *
*  Retour      : Bilan : -1 (a < b), 0 (a == b) ou 1 (a > b).                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int compare_full_match_trackers(const full_match_tracker_t **a, const full_match_tracker_t **b)
{
    int result;                             /* Bilan à renvoyer            */

    result = sort_unsigned_long((unsigned long)(*a)->pattern, (unsigned long)(*b)->pattern);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tracker = structure de gestion à manipuler.                  *
*                match   = correspondance complète établie.                   *
*                                                                             *
*  Description : Note l'existence d'une nouvelle correspondance pour un motif.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void add_match_to_full_match_tracker(full_match_tracker_t *tracker, GScanMatch *match)
{
    if (tracker->used == tracker->allocated)
    {
        tracker->allocated += ALLOCATION_STEP;
        tracker->matches = realloc(tracker->matches, tracker->allocated * sizeof(GScanMatch *));
    }

    tracker->matches[tracker->used++] = match;
    g_object_ref(G_OBJECT(match));

}



/* ---------------------------------------------------------------------------------- */
/*                       MEMORISATION DE PROGRESSIONS D'ANALYSE                       */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un contexte de suivi d'analyse. */
G_DEFINE_TYPE(GScanContext, g_scan_context, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des contextes de suivi d'analyses.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_context_class_init(GScanContextClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_context_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_context_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance de contexte de suivi d'analyse.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_context_init(GScanContext *context)
{
    context->options = NULL;

    context->content = NULL;
    context->scan_done = false;

    context->next_patid = 0;

    context->atom_trackers = NULL;

    context->full_trackers = NULL;
    context->full_count = 0;

    context->conditions = NULL;
    context->cond_count = 0;

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

static void g_scan_context_dispose(GScanContext *context)
{
    size_t i;                               /* Boucle de parcours          */

    g_clear_object(&context->options);

    g_clear_object(&context->content);

    for (i = 0; i < context->full_count; i++)
        if (context->full_trackers[i] != NULL)
        {
            delete_full_match_tracker(context->full_trackers[i]);
            context->full_trackers[i] = NULL;
        }

    for (i = 0; i < context->cond_count; i++)
        g_clear_object(&context->conditions[i].expr);

    G_OBJECT_CLASS(g_scan_context_parent_class)->dispose(G_OBJECT(context));

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

static void g_scan_context_finalize(GScanContext *context)
{
    size_t i;                               /* Boucle de parcours          */
    atom_match_tracker_t *atracker;         /* Conservateur à manipuler #1 */

    if (context->atom_trackers != NULL)
    {
        for (i = 0; i < context->next_patid; i++)
        {
            atracker = context->atom_trackers + i;

            if (atracker->matches != NULL)
                free(atracker->matches);

        }

        free(context->atom_trackers);

    }

    if (context->full_trackers != NULL)
        free(context->full_trackers);

    if (context->conditions != NULL)
    {
        for (i = 0; i < context->cond_count; i++)
            free(context->conditions[i].name);

        free(context->conditions);

    }

    G_OBJECT_CLASS(g_scan_context_parent_class)->finalize(G_OBJECT(context));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : options = ensemble d'options d'analyses à respecter.         *
*                                                                             *
*  Description : Définit un contexte pour suivi d'analyse.                    *
*                                                                             *
*  Retour      : Fonction mise en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanContext *g_scan_context_new(GScanOptions *options)
{
    GScanContext *result;                   /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_CONTEXT, NULL);

    result->options = options;
    g_object_ref(G_OBJECT(options));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = instance à consulter.                              *
*                                                                             *
*  Description : Fournit l'ensemble des options à respecter pour les analyses.*
*                                                                             *
*  Retour      : Ensemble d'options en vigueur.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanOptions *g_scan_context_get_options(const GScanContext *context)
{
    GScanOptions *result;                   /* Ensemble à retourner        */

    result = context->options;

    g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = instance à consulter.                              *
*                                                                             *
*  Description : Fournit un identifiant unique pour un motif recherché.       *
*                                                                             *
*  Retour      : Identifiant nouveau à utiliser.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

patid_t g_scan_context_get_new_pattern_id(GScanContext *context)
{
    patid_t result;                         /* Identifiant à retourner     */

    result = context->next_patid++;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = instance à consulter.                              *
*                content = contenu binaire en cours d'analyse.                *
*                                                                             *
*  Description : Définit le contenu principal à analyser.                     *
*                                                                             *
*  Retour      : Content binaire associé au context.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_scan_context_set_content(GScanContext *context, GBinContent *content)
{
    g_clear_object(&context->content);

    context->content = content;

    g_object_ref(G_OBJECT(content));

    context->atom_trackers = calloc(context->next_patid, sizeof(atom_match_tracker_t));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = instance à consulter.                              *
*                                                                             *
*  Description : Fournit une référence au contenu principal analysé.          *
*                                                                             *
*  Retour      : Content binaire associé au context.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinContent *g_scan_context_get_content(const GScanContext *context)
{
    GBinContent *result;                    /* Instance à retourner        */

    result = context->content;

    g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = instance à consulter.                              *
*                                                                             *
*  Description : Indique si la phase d'analyse de contenu est terminée.       *
*                                                                             *
*  Retour      : true si la phase de scan est terminée, false sinon.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_context_is_scan_done(const GScanContext *context)
{
    bool result;                            /* Statut à retourner          */

    result = context->scan_done;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = instance à mettre à jour.                          *
*                                                                             *
*  Description : Note que la phase d'analyse de contenu est terminée.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_scan_context_mark_scan_as_done(GScanContext *context)
{
    context->scan_done = true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = instance à mettre à jour.                          *
*                id      = identifiant du motif trouvé.                       *
*                offset  = localisation du motif au sein d'un contenu.        *
*                                                                             *
*  Description : Enregistre une correspondance partielle dans un contenu.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_scan_context_register_atom_match(GScanContext *context, patid_t id, phys_t offset)
{
    atom_match_tracker_t *tracker;          /* Gestionnaire concerné       */

    tracker = &context->atom_trackers[id];

    if (tracker->used == tracker->allocated)
    {
        tracker->allocated += ALLOCATION_STEP;
        tracker->matches = realloc(tracker->matches, tracker->allocated * sizeof(phys_t));
    }

    tracker->matches[tracker->used++] = offset;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = instance à mettre à jour.                          *
*                id      = identifiant du motif trouvé.                       *
*                count   = nombre de localisations renvoyées. [OUT]           *
*                                                                             *
*  Description : Retourne tous les correspondances partielles notées.         *
*                                                                             *
*  Retour      : Liste interne des localisations conservées.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const phys_t *g_scan_context_get_atom_matches(const GScanContext *context, patid_t id, size_t *count)
{
    const phys_t *result;                   /* Liste constituée à renvoyer */
    atom_match_tracker_t *tracker;          /* Gestionnaire concerné       */

    tracker = &context->atom_trackers[id];

    result = tracker->matches;
    *count = tracker->used;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = instance à mettre à jour.                          *
*                match   = représentation d'une plein ecorrespondance.        *
*                                                                             *
*  Description : Enregistre une correspondance complète avec un contenu.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_scan_context_register_full_match(GScanContext *context, GScanMatch *match)
{
    GSearchPattern *pattern;                /* Clef d'un suivi             */
    full_match_tracker_t key;               /* Modèle d'identification     */
    full_match_tracker_t **found;           /* Structure à actualiser      */
    full_match_tracker_t *tracker;          /* Nouveau suivi à intégrer    */

    pattern = g_scan_match_get_source(match);

    key.pattern = pattern;

    found = bsearch((full_match_tracker_t *[]) { &key }, context->full_trackers, context->full_count,
                    sizeof(full_match_tracker_t *), (__compar_fn_t)compare_full_match_trackers);

    if (found == NULL)
    {
        tracker = create_full_match_tracker(pattern);

        context->full_trackers = qinsert(context->full_trackers, &context->full_count,
                                         sizeof(full_match_tracker_t *),
                                         (__compar_fn_t)compare_full_match_trackers, &tracker);

    }
    else
        tracker = *found;

    add_match_to_full_match_tracker(tracker, match);

    g_object_unref(G_OBJECT(pattern));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = instance à mettre à jour.                          *
*                pattern = motif dont des correspondances sont à retrouver.   *
*                count   = quantité de correspondances enregistrées. [OUT]    *
*                                                                             *
*  Description : Fournit la liste de toutes les correspondances d'un motif.   *
*                                                                             *
*  Retour      : Liste courante de correspondances établies.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const GScanMatch **g_scan_context_get_full_matches(const GScanContext *context, const GSearchPattern *pattern, size_t *count)
{
    GScanMatch **result;                    /* Correspondance à renvoyer   */
    full_match_tracker_t key;               /* Modèle d'identification     */
    full_match_tracker_t **found;           /* Structure à actualiser      */

    key.pattern = pattern;

    found = bsearch((full_match_tracker_t *[]) { &key }, context->full_trackers, context->full_count,
                    sizeof(full_match_tracker_t *), (__compar_fn_t)compare_full_match_trackers);

    if (found == NULL)
    {
        result = NULL;
        *count = 0;
    }

    else
    {
        result = (*found)->matches;
        *count = (*found)->used;
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = mémoire de résultats d'analyse à compléter.        *
*                name    = désignation de la règle ciblée.                    *
*                expr    = expression de condition à réduire.                 *
*                                                                             *
*  Description : Intègre une condition de correspondance pour règle.          *
*                                                                             *
*  Retour      : Bilan final d'une intégration (false si nom déjà présent).   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_context_set_rule_condition(GScanContext *context, const char *name, GScanExpression *expr)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours          */
    rule_condition_t *new;                  /* Nouvel élément à intégrer   */

    result = true;

    /* Recherche d'antécédent */

    for (i = 0; i < context->cond_count; i++)
        if (strcmp(name, context->conditions[i].name) == 0)
        {
            result = false;
            break;
        }

    /* Ajout d'un nouvel élément ? */

    if (result)
    {
        context->conditions = realloc(context->conditions, ++context->cond_count * sizeof(rule_condition_t));

        new = &context->conditions[context->cond_count - 1];

        new->name = strdup(name);
        new->name_hash = fnv_64a_hash(name);

        new->expr = expr;
        g_object_ref(G_OBJECT(expr));
        new->final_reduced = false;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = mémoire de résultats d'analyse à consulter.        *
*                name    = désignation de la règle ciblée.                    *
*                                                                             *
*  Description : Indique si un nom donné correspond à une règle.              *
*                                                                             *
*  Retour      : Bilan de la présence d'une règle désignée.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_context_has_rule_for_name(const GScanContext *context, const char *name)
{
    bool result;                            /* Bilan à retourner           */
    fnv64_t hash;                           /* Empreinte du nom à retrouver*/
    size_t i;                               /* Boucle de parcours          */
    const rule_condition_t *cond;           /* Condition connue du contexte*/

    result = false;

    hash = fnv_64a_hash(name);

    for (i = 0; i < context->cond_count; i++)
    {
        cond = context->conditions + i;

        if (cond->name_hash != hash)
            continue;

        if (strcmp(cond->name, name) == 0)
        {
            result = true;
            break;
        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = mémoire de résultats d'analyse à consulter.        *
*                name    = désignation de la règle ciblée.                    *
*                                                                             *
*  Description : Indique si une correspondance globale a pu être établie.     *
*                                                                             *
*  Retour      : Bilan final d'une analyse (false par défaut).                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_context_has_match_for_rule(GScanContext *context, const char *name)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours          */
    rule_condition_t *cond;                 /* Condition à considérer      */
    GScanScope *scope;                      /* Définition de portées       */
    GScanExpression *new;                   /* Nouvelle expression réduite */
    ScanReductionState state;               /* Statut d'une réduction      */
    bool valid;                             /* Validité d'une récupération */

    result = false;

    /* Recherche de la règle visée */

    cond = NULL;

    for (i = 0; i < context->cond_count; i++)
        if (strcmp(name, context->conditions[i].name) == 0)
        {
            cond = &context->conditions[i];
            break;
        }

    if (cond == NULL)
        goto exit;

    /* Tentative de réduction finale */

    if (!cond->final_reduced)
    {
        scope = g_scan_scope_new(name);

        state = g_scan_expression_reduce(cond->expr, context, scope, &new);
        if (state == SRS_UNRESOLVABLE) goto exit_reduction;

        g_object_unref(G_OBJECT(cond->expr));
        cond->expr = new;

        valid = g_scan_expression_reduce_to_boolean(cond->expr, context, scope, &new);
        if (!valid || new == NULL) goto exit_reduction;

        g_object_unref(G_OBJECT(cond->expr));
        cond->expr = new;

        cond->final_reduced = true;

 exit_reduction:

        g_object_unref(G_OBJECT(scope));

    }

    /* Tentative de récupération d'un bilan final */

    if (cond->final_reduced)
    {
        valid = g_scan_literal_expression_get_boolean_value(G_SCAN_LITERAL_EXPRESSION(cond->expr), &result);

        if (!valid)
        {
            assert(!result);
            result = false;
        }

    }

 exit:

    return result;

}
