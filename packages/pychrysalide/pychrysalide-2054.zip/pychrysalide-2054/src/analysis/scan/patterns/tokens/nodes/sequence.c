
/* Chrysalide - Outil d'analyse de fichiers binaires
 * sequence.c - décompositions séquentielles de motif de recherche
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


#include "sequence.h"


#include "sequence-int.h"



/* ------------------------ DECOMPOSITION DE MOTIF RECHERCHE ------------------------ */


/* Initialise la classe des décompositions séquentielles. */
static void g_scan_token_node_sequence_class_init(GScanTokenNodeSequenceClass *);

/* Initialise une instance de décompositions séquentielles. */
static void g_scan_token_node_sequence_init(GScanTokenNodeSequence *);

/* Supprime toutes les références externes. */
static void g_scan_token_node_sequence_dispose(GScanTokenNodeSequence *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_token_node_sequence_finalize(GScanTokenNodeSequence *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Parcourt une arborescence de noeuds et y relève des éléments. */
static void g_scan_token_node_sequence_visit(GScanTokenNodeSequence *node, scan_tree_points_t *);

/* Inscrit la définition d'un motif dans un moteur de recherche. */
static bool g_scan_token_node_sequence_enroll(GScanTokenNodeSequence *, GScanContext *, GEngineBackend *, size_t, size_t *);

/* Transforme les correspondances locales en trouvailles. */
static void g_scan_token_node_sequence_check_forward(const GScanTokenNodeSequence *, GScanContext *, GBinContent *, pending_matches_t *, node_search_offset_t *, bool, bool *);

/* Transforme les correspondances locales en trouvailles. */
static void g_scan_token_node_sequence_check_backward(const GScanTokenNodeSequence *, GScanContext *, GBinContent *, pending_matches_t *, node_search_offset_t *, bool, bool *);



/* ---------------------------------------------------------------------------------- */
/*                          DECOMPOSITION DE MOTIF RECHERCHE                          */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour des décompositions séquentielles de motif de recherche. */
G_DEFINE_TYPE(GScanTokenNodeSequence, g_scan_token_node_sequence, G_TYPE_SCAN_TOKEN_NODE);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des décompositions séquentielles.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_node_sequence_class_init(GScanTokenNodeSequenceClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GScanTokenNodeClass *node;              /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_token_node_sequence_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_token_node_sequence_finalize;

    node = G_SCAN_TOKEN_NODE_CLASS(klass);

    node->visit = (visit_scan_token_node_fc)g_scan_token_node_sequence_visit;
    node->enroll = (enroll_scan_token_node_fc)g_scan_token_node_sequence_enroll;
    node->check_forward = (check_scan_token_node_fc)g_scan_token_node_sequence_check_forward;
    node->check_backward = (check_scan_token_node_fc)g_scan_token_node_sequence_check_backward;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : sequence = instance à initialiser.                           *
*                                                                             *
*  Description : Initialise une instance de décompositions séquentielles.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_node_sequence_init(GScanTokenNodeSequence *sequence)
{
    sequence->children = NULL;
    sequence->count = 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : sequence = instance d'objet GLib à traiter.                  *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_node_sequence_dispose(GScanTokenNodeSequence *sequence)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < sequence->count; i++)
        g_clear_object(&sequence->children[i]);

    G_OBJECT_CLASS(g_scan_token_node_sequence_parent_class)->dispose(G_OBJECT(sequence));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : sequence = instance d'objet GLib à traiter.                  *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_node_sequence_finalize(GScanTokenNodeSequence *sequence)
{
    if (sequence->children != NULL)
        free(sequence->children);

    G_OBJECT_CLASS(g_scan_token_node_sequence_parent_class)->finalize(G_OBJECT(sequence));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : child    = noeud dont les résultats sont à écarter.          *
*                                                                             *
*  Description : Construit une série de décompositions séquentielles de motif.*
*                                                                             *
*  Retour      : Mécanismes mis en place.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanTokenNode *g_scan_token_node_sequence_new(GScanTokenNode *child)
{
    GScanTokenNode *result;                 /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_TOKEN_NODE_SEQUENCE, NULL);

    if (!g_scan_token_node_sequence_create(G_SCAN_TOKEN_NODE_SEQUENCE(result), child))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : sequence = décompositions à initialiser pleinement.          *
*                child    = noeud dont les résultats sont à écarter.          *
*                                                                             *
*  Description : Met en place une série de décompositions séquentielles.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_token_node_sequence_create(GScanTokenNodeSequence *sequence, GScanTokenNode *child)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    g_scan_token_node_sequence_add(sequence, child);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : sequence = ensemble de noeuds à compléter.                   *
*                child  = nouveau noeud à intégrer.                           *
*                                                                             *
*  Description : Ajoute un noeud à aux décompositions séquentielles de motif. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_scan_token_node_sequence_add(GScanTokenNodeSequence *sequence, GScanTokenNode *child)
{
    sequence->children = realloc(sequence->children, ++sequence->count * sizeof(GScanTokenNode *));

    sequence->children[sequence->count - 1] = child;
    g_object_ref(G_OBJECT(child));

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


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

static void g_scan_token_node_sequence_visit(GScanTokenNodeSequence *node, scan_tree_points_t *points)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < node->count; i++)
        g_scan_token_node_visit(node->children[i], points);

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

static bool g_scan_token_node_sequence_enroll(GScanTokenNodeSequence *node, GScanContext *context, GEngineBackend *backend, size_t maxsize, size_t *slow)
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

static void g_scan_token_node_sequence_check_forward(const GScanTokenNodeSequence *node, GScanContext *context, GBinContent *content, pending_matches_t *matches, node_search_offset_t *offset, bool not, bool *skip)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < node->count; i++)
        _g_scan_token_node_check_forward(node->children[i], context, content, matches, offset, not, skip);

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

static void g_scan_token_node_sequence_check_backward(const GScanTokenNodeSequence *node, GScanContext *context, GBinContent *content, pending_matches_t *matches, node_search_offset_t *offset, bool not, bool *skip)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = node->count; i > 0 ; i--)
        _g_scan_token_node_check_backward(node->children[i - 1], context, content, matches, offset, not, skip);

}
