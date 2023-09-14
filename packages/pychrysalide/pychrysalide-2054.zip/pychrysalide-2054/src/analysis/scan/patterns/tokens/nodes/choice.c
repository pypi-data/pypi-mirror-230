
/* Chrysalide - Outil d'analyse de fichiers binaires
 * choice.c - décompositions alternatives de motif de recherche
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


#include "choice.h"


#include "choice-int.h"



/* ------------------------ DECOMPOSITION DE MOTIF RECHERCHE ------------------------ */


/* Initialise la classe des décompositions alternatives. */
static void g_scan_token_node_choice_class_init(GScanTokenNodeChoiceClass *);

/* Initialise une instance de décompositions alternatives. */
static void g_scan_token_node_choice_init(GScanTokenNodeChoice *);

/* Supprime toutes les références externes. */
static void g_scan_token_node_choice_dispose(GScanTokenNodeChoice *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_token_node_choice_finalize(GScanTokenNodeChoice *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Prend acte d'une nouvelle propriété pour le noeud. */
static void g_scan_token_node_choice_apply_flags(GScanTokenNodeChoice *, ScanTokenNodeFlags);

/* Parcourt une arborescence de noeuds et y relève des éléments. */
static void g_scan_token_node_choice_visit(GScanTokenNodeChoice *, scan_tree_points_t *);

/* Inscrit la définition d'un motif dans un moteur de recherche. */
static bool g_scan_token_node_choice_enroll(GScanTokenNodeChoice *, GScanContext *, GEngineBackend *, size_t, size_t *);

/* Transforme les correspondances locales en trouvailles. */
static void g_scan_token_node_choice_check_forward(const GScanTokenNodeChoice *, GScanContext *, GBinContent *, pending_matches_t *, node_search_offset_t *, bool, bool *);

/* Transforme les correspondances locales en trouvailles. */
static void g_scan_token_node_choice_check_backward(const GScanTokenNodeChoice *, GScanContext *, GBinContent *, pending_matches_t *, node_search_offset_t *, bool, bool *);



/* ---------------------------------------------------------------------------------- */
/*                          DECOMPOSITION DE MOTIF RECHERCHE                          */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour des décompositions alternatives de motif de recherche. */
G_DEFINE_TYPE(GScanTokenNodeChoice, g_scan_token_node_choice, G_TYPE_SCAN_TOKEN_NODE);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des décompositions alternatives.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_node_choice_class_init(GScanTokenNodeChoiceClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GScanTokenNodeClass *node;              /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_token_node_choice_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_token_node_choice_finalize;

    node = G_SCAN_TOKEN_NODE_CLASS(klass);

    node->apply = (apply_scan_token_node_flags_fc)g_scan_token_node_choice_apply_flags;
    node->visit = (visit_scan_token_node_fc)g_scan_token_node_choice_visit;
    node->enroll = (enroll_scan_token_node_fc)g_scan_token_node_choice_enroll;
    node->check_forward = (check_scan_token_node_fc)g_scan_token_node_choice_check_forward;
    node->check_backward = (check_scan_token_node_fc)g_scan_token_node_choice_check_backward;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : choice = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une instance de décompositions alternatives.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_node_choice_init(GScanTokenNodeChoice *choice)
{
    choice->children = NULL;
    choice->count = 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : choice = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_node_choice_dispose(GScanTokenNodeChoice *choice)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < choice->count; i++)
        g_clear_object(&choice->children[i]);

    G_OBJECT_CLASS(g_scan_token_node_choice_parent_class)->dispose(G_OBJECT(choice));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : choice = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_node_choice_finalize(GScanTokenNodeChoice *choice)
{
    if (choice->children != NULL)
        free(choice->children);

    G_OBJECT_CLASS(g_scan_token_node_choice_parent_class)->finalize(G_OBJECT(choice));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Construit une série de décompositions alternatives de motif. *
*                                                                             *
*  Retour      : Mécanismes mis en place.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanTokenNode *g_scan_token_node_choice_new(void)
{
    GScanTokenNode *result;                 /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_TOKEN_NODE_CHOICE, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : choice = ensemble de noeuds à compléter.                     *
*                node   = nouveau noeud à intégrer.                           *
*                                                                             *
*  Description : Ajoute un noeud à aux décompositions alternatives de motif.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_scan_token_node_choice_add(GScanTokenNodeChoice *choice, GScanTokenNode *node)
{
    choice->children = realloc(choice->children, ++choice->count * sizeof(GScanTokenNode *));

    choice->children[choice->count - 1] = node;
    g_object_ref(G_OBJECT(node));

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : node  = noeud de motif à mettre à jour.                      *
*                flags = propriétés particulières à associer au noeud.        *
*                                                                             *
*  Description : Prend acte d'une nouvelle propriété pour le noeud.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_node_choice_apply_flags(GScanTokenNodeChoice *node, ScanTokenNodeFlags flags)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < node->count; i++)
        g_scan_token_node_set_flags(node->children[i], flags);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node   = point de départ du parcours à effectuer.            *
*                points = points capitaux de l'arborescence. [OUT]            *
*                                                                             *
*  Description : Parcourt une arborescence de noeuds et y relève des éléments.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_node_choice_visit(GScanTokenNodeChoice *node, scan_tree_points_t *points)
{
    size_t first_plain_count;               /* Décompte de noeuds textuels */
    size_t i;                               /* Boucle de parcours          */
    scan_tree_points_t tmp_points;          /* Synthèse d'analyse locale   */

    if (points->first_plain != NULL)
        return;

    first_plain_count = 0;

    for (i = 0; i < node->count; i++)
    {
        tmp_points.first_node = NULL;
        tmp_points.last_node = NULL;

        tmp_points.first_plain = NULL;
        tmp_points.best_masked = NULL;

        g_scan_token_node_visit(node->children[i], &tmp_points);

        if (tmp_points.first_plain != NULL)
            first_plain_count++;

    }

    if (first_plain_count == node->count)
        points->first_plain = G_SCAN_TOKEN_NODE(node);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node    = définition de la bribe à enregistrer.              *
*                context = contexte de l'analyse à mener.                     *
*                backend = moteur de recherche à préchauffer.                 *
*                maxsize = taille max. des atomes (mise en commun optimisée). *
*                slow    = niveau de ralentissement induit (0 = idéal). [OUT] *
*                                                                             *
*  Description : Inscrit la définition d'un motif dans un moteur de recherche.*
*                                                                             *
*  Retour      : Bilan de l'opération à renvoyer.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_scan_token_node_choice_enroll(GScanTokenNodeChoice *node, GScanContext *context, GEngineBackend *backend, size_t maxsize, size_t *slow)
{
    bool result;                            /* Statut à retourner          */
    size_t i;                               /* Boucle de parcours          */

    result = true;

    for (i = 0; i < node->count && result; i++)
        result = _g_scan_token_node_enroll(node->children[i], context, backend, maxsize, slow);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node    = définition de la bribe à manipuler.                *
*                context = contexte de l'analyse à mener.                     *
*                content = accès au contenu brut pour vérifications (optim.)  *
*                matches = suivi des correspondances à consolider.            *
*                offset  = tolérance dans les positions à appliquer.          *
*                not     = indique si les résultats doivent être inversés.    *
*                skip    = détermine si l'analyse est différée. [OUT]         *
*                                                                             *
*  Description : Transforme les correspondances locales en trouvailles.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_node_choice_check_forward(const GScanTokenNodeChoice *node, GScanContext *context, GBinContent *content, pending_matches_t *matches, node_search_offset_t *offset, bool not, bool *skip)
{
    pending_matches_t init_matches;         /* Correspondances initiales   */
    node_search_offset_t init_offset;       /* Intervales initiaux         */ 
    size_t new_offset;                      /* Décompte d'intervales       */
    size_t i;                               /* Boucle de parcours          */
    pending_matches_t tmp_matches;          /* Copie locale de travail #1  */
    node_search_offset_t tmp_offset;        /* Copie locale de travail #2  */

    if (*skip)
        return;

    /* Copie des contextes de départ */

    copy_pending_matches(&init_matches, matches);

    exit_pending_matches(matches);
    init_pending_matches(matches, &init_matches.content_start, &init_matches.content_end);

    copy_node_search_offset(&init_offset, offset);

    exit_node_search_offset(offset);
    init_node_search_offset(offset);

    /* Lancement des sous-traitements */

    new_offset = 0;

    for (i = 0; i < node->count; i++)
    {
        copy_pending_matches(&tmp_matches, &init_matches);
        copy_node_search_offset(&tmp_offset, &init_offset);

        _g_scan_token_node_check_forward(node->children[i], context, content,
                                         &tmp_matches, &tmp_offset, not, skip);

        merge_pending_matches(matches, &tmp_matches);
        merge_node_search_offset(offset, &tmp_offset);

        if (tmp_offset.used > 0)
            new_offset++;

        exit_pending_matches(&tmp_matches);
        exit_node_search_offset(&tmp_offset);

    }

    /* Sortie propre */

    exit_pending_matches(&init_matches);
    exit_node_search_offset(&init_offset);

    /* "Alternative" directe en cas de motif(s) non terminé(s) par un intervale */

    if (new_offset != node->count)
    {
        assert(node->count > 1);
        add_range_to_node_search_offset(offset, 0, 0, NULL);
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node    = définition de la bribe à manipuler.                *
*                context = contexte de l'analyse à mener.                     *
*                content = accès au contenu brut pour vérifications (optim.)  *
*                matches = suivi des correspondances à consolider.            *
*                offsets = tolérance dans les positions à appliquer.          *
*                not     = indique si les résultats doivent être inversés.    *
*                skip    = détermine si l'analyse est différée. [OUT]         *
*                                                                             *
*  Description : Transforme les correspondances locales en trouvailles.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_node_choice_check_backward(const GScanTokenNodeChoice *node, GScanContext *context, GBinContent *content, pending_matches_t *matches, node_search_offset_t *offset, bool not, bool *skip)
{
    pending_matches_t init_matches;         /* Correspondances initiales   */
    node_search_offset_t init_offset;       /* Intervales initiaux         */ 
    size_t new_offset;                      /* Décompte d'intervales       */
    size_t i;                               /* Boucle de parcours          */
    pending_matches_t tmp_matches;          /* Copie locale de travail #1  */
    node_search_offset_t tmp_offset;        /* Copie locale de travail #2  */

    if (*skip)
        return;

    /* Copie des contextes de départ */

    copy_pending_matches(&init_matches, matches);

    exit_pending_matches(matches);
    init_pending_matches(matches, &init_matches.content_start, &init_matches.content_end);

    copy_node_search_offset(&init_offset, offset);

    exit_node_search_offset(offset);
    init_node_search_offset(offset);

    /* Lancement des sous-traitements */

    new_offset = 0;

    for (i = 0; i < node->count; i++)
    {
        copy_pending_matches(&tmp_matches, &init_matches);
        copy_node_search_offset(&tmp_offset, &init_offset);

        _g_scan_token_node_check_backward(node->children[i], context, content,
                                          &tmp_matches, &tmp_offset, not, skip);

        merge_pending_matches(matches, &tmp_matches);
        merge_node_search_offset(offset, &tmp_offset);

        if (tmp_offset.used > 0)
            new_offset++;

        exit_pending_matches(&tmp_matches);
        exit_node_search_offset(&tmp_offset);

    }

    /* Sortie propre */

    exit_pending_matches(&init_matches);
    exit_node_search_offset(&init_offset);

    /* "Alternative" directe en cas de motif(s) non terminé(s) par un intervale */

    if (new_offset != node->count)
    {
        assert(node->count > 1);
        add_range_to_node_search_offset(offset, 0, 0, NULL);
    }

}
