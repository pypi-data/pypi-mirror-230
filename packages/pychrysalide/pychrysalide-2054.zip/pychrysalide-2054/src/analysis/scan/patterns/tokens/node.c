
/* Chrysalide - Outil d'analyse de fichiers binaires
 * node.c - décomposition d'un motif de recherche en atomes assemblés
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


#include "node.h"


#include <assert.h>


#include "node-int.h"
#include "nodes/any.h"



/* ------------------------ DECOMPOSITION DE MOTIF RECHERCHE ------------------------ */


/* Initialise la classe des éléments de décomposition. */
static void g_scan_token_node_class_init(GScanTokenNodeClass *);

/* Initialise une instance d'élément décomposant un motif. */
static void g_scan_token_node_init(GScanTokenNode *);

/* Supprime toutes les références externes. */
static void g_scan_token_node_dispose(GScanTokenNode *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_token_node_finalize(GScanTokenNode *);



/* ---------------------------------------------------------------------------------- */
/*                          DECOMPOSITION DE MOTIF RECHERCHE                          */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un élément décomposant un motif d'octets à rechercher. */
G_DEFINE_TYPE(GScanTokenNode, g_scan_token_node, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des éléments de décomposition.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_node_class_init(GScanTokenNodeClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_token_node_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_token_node_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance d'élément décomposant un motif.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_node_init(GScanTokenNode *node)
{
    node->flags = STNF_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_node_dispose(GScanTokenNode *node)
{
    G_OBJECT_CLASS(g_scan_token_node_parent_class)->dispose(G_OBJECT(node));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_node_finalize(GScanTokenNode *node)
{
    G_OBJECT_CLASS(g_scan_token_node_parent_class)->finalize(G_OBJECT(node));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node = noeud de motif à consulter.                           *
*                                                                             *
*  Description : Indique les propriétés particulières d'un noeud d'analyse.   *
*                                                                             *
*  Retour      : Propriétés particulières associées au noeud.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

ScanTokenNodeFlags g_scan_token_node_get_flags(const GScanTokenNode *node)
{
    ScanTokenNodeFlags result;              /* Statut à retourner          */

    result = node->flags;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node  = noeud de motif à mettre à jour.                      *
*                flags = propriétés particulières à associer au noeud.        *
*                                                                             *
*  Description : Marque le noeud avec des propriétés particulières.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_scan_token_node_set_flags(GScanTokenNode *node, ScanTokenNodeFlags flags)
{
    GScanTokenNodeClass *class;             /* Classe de l'instance        */

    node->flags |= flags;

    class = G_SCAN_TOKEN_NODE_GET_CLASS(node);

    if (class->apply != NULL)
        class->apply(node, flags);

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

void g_scan_token_node_visit(GScanTokenNode *node, scan_tree_points_t *points)
{
    GScanTokenNodeClass *class;             /* Classe de l'instance        */

    if (node->flags & STNF_PROD)
    {
        if (points->first_node == NULL)
            points->first_node = node;

        points->last_node = node;

    }

    class = G_SCAN_TOKEN_NODE_GET_CLASS(node);

    if (class->visit != NULL)
        class->visit(node, points);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node   = point de départ du parcours à préparer.             *
*                                                                             *
*  Description : Détermine et prépare les éléments clefs d'une arborescence.  *
*                                                                             *
*  Retour      : true si une analyse à rebourd complémentaire est requise.    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_token_node_setup_tree(GScanTokenNode *node)
{
    bool result;                            /* Prévision à retourner       */
    scan_tree_points_t points;              /* Repérage de points capitaux */
    GScanTokenNode *main;                   /* Principal noeud d'opération */

    /* Phase de localisation */

    points.first_node = NULL;
    points.last_node = NULL;

    points.first_plain = NULL;
    points.best_masked = NULL;

    g_scan_token_node_visit(node, &points);

    /* Phase d'application */

    //g_scan_token_node_set_flags(points.first_node, STNF_FIRST);
    //g_scan_token_node_set_flags(points.last_node, STNF_LAST);

    if (points.first_plain != NULL)
        main = points.first_plain;

    else if (points.best_masked != NULL)
        main = points.best_masked;

    else
        main = node;//points.first_node;

    g_scan_token_node_set_flags(main, STNF_MAIN);

    result = (main != node/*points.first_node*/);

    return result;

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

bool _g_scan_token_node_enroll(GScanTokenNode *node, GScanContext *context, GEngineBackend *backend, size_t maxsize, size_t *slow)
{
    bool result;                            /* Statut à retourner          */
    GScanTokenNodeClass *class;             /* Classe de l'instance        */

    class = G_SCAN_TOKEN_NODE_GET_CLASS(node);

    result = class->enroll(node, context, backend, maxsize, slow);

    return result;

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

bool g_scan_token_node_enroll(GScanTokenNode *node, GScanContext *context, GEngineBackend *backend, size_t maxsize, size_t *slow)
{
    bool result;                            /* Statut à retourner          */

    assert(g_engine_backend_get_atom_max_size(backend) == maxsize);

    *slow = 0;

    result = _g_scan_token_node_enroll(node, context, backend, maxsize, slow);

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

void _g_scan_token_node_check_forward(const GScanTokenNode *node, GScanContext *context, GBinContent *content, pending_matches_t *matches, node_search_offset_t *offset, bool not, bool *skip)
{
    GScanTokenNodeClass *class;             /* Classe de l'instance        */

    if (node->flags & STNF_MAIN)
    {
        //assert(*skip); //REMME
        *skip = false;
    }

    class = G_SCAN_TOKEN_NODE_GET_CLASS(node);

    class->check_forward(node, context, content, matches, offset, not, skip);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node    = définition de la bribe à manipuler.                *
*                context = contexte de l'analyse à mener.                     *
*                content = accès au contenu brut pour vérifications (optim.)  *
*                matches = suivi des correspondances à consolider.            *
*                                                                             *
*  Description : Transforme les correspondances locales en trouvailles.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_scan_token_node_check_forward(const GScanTokenNode *node, GScanContext *context, GBinContent *content, pending_matches_t *matches)
{
    node_search_offset_t offset;            /* Espace des correspondances  */
    bool skip;                              /* Mise en attente des analyses*/
    size_t ocount;                          /* Quantité de bornes présentes*/
    node_offset_range_t * const *ranges_ptr;/* Bornes d'espace à parcourir */
    size_t pcount;                          /* Nombre de correspondances   */
    match_area_t * const *pending_ptr;      /* Correspondances actuelles   */
    size_t p;                               /* Boucle de parcours #2       */
    match_area_t *pending;                  /* Correspondance à traiter    */
    phys_t old_end;                         /* Ancien point d'arrivée      */
    size_t o;                               /* Boucle de parcours #1       */
    const node_offset_range_t *range;       /* Bornes d'espace à parcourir */
    phys_t new_end;                         /* Nouveau point d'arrivée     */

    init_node_search_offset(&offset);

    skip = true;

    _g_scan_token_node_check_forward(node, context, content, matches, &offset, false, &skip);

    /**
     * Si un décalage entre octets n'a pas été consommé,
     * les résultats sont étendus à minima.
     */

    ranges_ptr = get_node_search_offset_ranges(&offset, &ocount);

    if (ocount > 0)
    {
        reset_pending_matches_ttl(matches);

        pending_ptr = get_all_pending_matches(matches, &pcount);

        for (p = 0; p < pcount; p++)
        {
            pending = (*pending_ptr) + p;

            old_end = pending->end;

            for (o = 0; o < ocount; o++)
            {
                range = (*ranges_ptr) + o;

                new_end = old_end + range->min;

                if (new_end > matches->content_end)
                    new_end = matches->content_end;

                extend_pending_match_ending(matches, p, new_end);

            }

        }

        /**
         * Pas besoin de purge ici puisque tous les résultats ont été traités
         * au moins une fois, sans condition.
         */
        /* purge_pending_matches(matches); */

        disable_all_ranges_in_node_search_offset(&offset);

    }

    assert(offset.used == 0);

    exit_node_search_offset(&offset);

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

void _g_scan_token_node_check_backward(const GScanTokenNode *node, GScanContext *context, GBinContent *content, pending_matches_t *matches, node_search_offset_t *offset, bool not, bool *skip)
{
    GScanTokenNodeClass *class;             /* Classe de l'instance        */

    class = G_SCAN_TOKEN_NODE_GET_CLASS(node);

    class->check_backward(node, context, content, matches, offset, not, skip);

    if (node->flags & STNF_MAIN)
    {
        //assert(*skip); //REMME
        *skip = false;
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node    = définition de la bribe à manipuler.                *
*                context = contexte de l'analyse à mener.                     *
*                content = accès au contenu brut pour vérifications (optim.)  *
*                matches = suivi des correspondances à consolider.            *
*                                                                             *
*  Description : Transforme les correspondances locales en trouvailles.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_scan_token_node_check_backward(const GScanTokenNode *node, GScanContext *context, GBinContent *content, pending_matches_t *matches)
{
    node_search_offset_t offset;            /* Espace des correspondances  */
    bool skip;                              /* Mise en attente des analyses*/
    size_t ocount;                          /* Quantité de bornes présentes*/
    node_offset_range_t * const *ranges_ptr;/* Bornes d'espace à parcourir */
    size_t pcount;                          /* Nombre de correspondances   */
    match_area_t * const *pending_ptr;      /* Correspondances actuelles   */
    size_t p;                               /* Boucle de parcours #2       */
    match_area_t *pending;                  /* Correspondance à traiter    */
    phys_t old_start;                       /* Ancien point d'arrivée      */
    size_t o;                               /* Boucle de parcours #1       */
    const node_offset_range_t *range;       /* Bornes d'espace à parcourir */
    phys_t new_start;                       /* Nouveau point d'arrivée     */

    init_node_search_offset(&offset);

    skip = true;

    _g_scan_token_node_check_backward(node, context, content, matches, &offset, false, &skip);

    /**
     * Si un décalage entre octets n'a pas été consommé,
     * les résultats sont étendus à minima.
     */

    ranges_ptr = get_node_search_offset_ranges(&offset, &ocount);

    if (ocount > 0)
    {
        reset_pending_matches_ttl(matches);

        pending_ptr = get_all_pending_matches(matches, &pcount);

        for (p = 0; p < pcount; p++)
        {
            pending = (*pending_ptr) + p;

            old_start = pending->start;

            for (o = 0; o < ocount; o++)
            {
                range = (*ranges_ptr) + o;

                if (old_start < range->min)
                    new_start = 0;
                else
                    new_start = old_start - range->min;

                if (new_start < matches->content_start)
                    new_start = matches->content_start;

                extend_pending_match_beginning(matches, p, new_start);

            }

        }

        /**
         * Pas besoin de purge ici puisque tous les résultats ont été traités
         * au moins une fois, sans condition.
         */
        /* purge_pending_matches(matches); */

        disable_all_ranges_in_node_search_offset(&offset);

    }

    assert(offset.used == 0);

    exit_node_search_offset(&offset);

}
