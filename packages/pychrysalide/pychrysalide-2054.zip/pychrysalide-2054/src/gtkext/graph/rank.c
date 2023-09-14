
/* Chrysalide - Outil d'analyse de fichiers binaires
 * rank.c - classement par rang des descendants directs
 *
 * Copyright (C) 2019 Cyrille Bagard
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


#include "rank.h"


#include <assert.h>
#include <malloc.h>


#include "cluster-int.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : grank   = structure à initialiser. [OUT]                     *
*                cluster = chef de file d'un ensemble de blocs.               *
*                                                                             *
*  Description : Initialise la gestion d'un ensemble de blocs de même rang.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void init_graph_rank(graph_rank_t *grank, GGraphCluster *cluster)
{
    grank->right2left = NULL;
    grank->r2l_count = 0;

    grank->left2right = NULL;
    grank->l2r_count = 0;

    grank->clusters = malloc(sizeof(GGraphCluster *));
    grank->count = 1;

    grank->clusters[0] = cluster;

    init_vspace_manager(&grank->vspaces);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : grank = structure à vider.                                   *
*                                                                             *
*  Description : Termine la gestion d'un ensemble de blocs de même rang.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void exit_graph_rank(graph_rank_t *grank)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < grank->r2l_count; i++)
        free(grank->right2left[i]);

    if (grank->right2left != NULL)
        free(grank->right2left);

    for (i = 0; i < grank->l2r_count; i++)
        free(grank->left2right[i]);

    if (grank->left2right != NULL)
        free(grank->left2right);

    assert(grank->clusters != NULL);

    free(grank->clusters);

    exit_vspace_manager(&grank->vspaces);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : grank = ensemble de même rang à consulter.                   *
*                                                                             *
*  Description : Parcours l'ensemble des blocs du rang avec un visiteur.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void visit_graph_rank(const graph_rank_t *grank, graph_rank_cb cb)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < grank->count; i++)
        cb(grank->clusters[i]);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : grank = ensemble de même rang à consulter.                   *
*                                                                             *
*  Description : Parcours l'ensemble des blocs du rang avec un visiteur.      *
*                                                                             *
*  Retour      : Bilan à retourner.                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool visit_and_accumulate_graph_rank(const graph_rank_t *grank, graph_rank_acc_cb cb)
{
    bool result;                            /* Bilan cumulé à renvoyer     */
    size_t i;                               /* Boucle de parcours          */

    result = false;

    for (i = 0; i < grank->count; i++)
        result |= cb(grank->clusters[i]);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : grank = ensemble de même rang à consulter.                   *
*                                                                             *
*  Description : Fournit le rang d'un ensemble de blocs.                      *
*                                                                             *
*  Retour      : Rang d'un ensemble de blocs de même rang.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t get_graph_rank(const graph_rank_t *grank)
{
    size_t result;                          /* Rang à retourner            */
    GCodeBlock *block;                      /* Bloc de code de référence   */

    block = g_graph_cluster_get_block(grank->clusters[0]);

    result = g_code_block_get_rank(block);

    g_object_unref(G_OBJECT(block));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = premier ensemble de même rang à comparer.                *
*                b = second ensemble de même rang à comparer.                 *
*                                                                             *
*  Description : Compare deux rangées de blocs de code.                       *
*                                                                             *
*  Retour      : Bilan de comparaison.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int cmp_graph_rank(const graph_rank_t *a, const graph_rank_t *b)
{
    int result;                             /* Bilan à retourner           */
    size_t level_a;                         /* Niveau de l'ensemble A      */
    size_t level_b;                         /* Niveau de l'ensemble B      */

    level_a = get_graph_rank(a);
    level_b = get_graph_rank(b);

    if (level_a < level_b)
        result = -1;

    else if (level_a > level_b)
        result = 1;

    else
        result = 0;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : grank   = structure à compléter.                             *
*                cluster = chef de file d'un ensemble de blocs.               *
*                                                                             *
*  Description : Etend un ensemble de blocs de même rang.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void extend_graph_rank(graph_rank_t *grank, GGraphCluster *cluster)
{
    grank->count++;
    grank->clusters = realloc(grank->clusters, sizeof(GGraphCluster *) * grank->count);

    grank->clusters[grank->count - 1] = cluster;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : grank   = structure à compléter.                             *
*                cluster = chef de file d'un ensemble de blocs.               *
*                                                                             *
*  Description : Détermine si un groupe de blocs contient un bloc particulier.*
*                                                                             *
*  Retour      : true si le chef est bien contenu, false sinon.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool has_graph_rank_cluster(const graph_rank_t *grank, GGraphCluster *cluster)
{
    bool result;                            /* Bilan à renvoyer            */
    size_t i;                               /* Boucle de parcours          */

    result = false;

    for (i = 0; i < grank->count && !result; i++)
        result = (grank->clusters[i] == cluster);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : grank    = ensemble de descendants d'un même rang.           *
*                from     = point de départ du lien concerné.                 *
*                to       = point d'arrivée du lien concerné.                 *
*                pts      = points intermédiaires du tracé complet final.     *
*                external = précise une sortie du cadre du cluster premier.   *
*                                                                             *
*  Description : Inscrit à l'endroit idéal une réservation d'espace latéral.  *
*                                                                             *
*  Retour      : true si la demande a bien été traitée.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool extend_graph_rank_vspace_manager(graph_rank_t *grank, leaving_link_t *from, incoming_link_t *to, GdkPoint *pts, bool external)
{
    bool result;                            /* Bilan à renvoyer            */

    result = has_graph_rank_cluster(grank, from->owner);

    if (result)
        extend_vspace_manager(&grank->vspaces, from, to, pts, external);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : grank = ensemble de descendants d'un même rang.              *
*                all   = table regroupant tous les groupes créés.             *
*                                                                             *
*  Description : Met en place les embryons de liens nécessaires.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void define_graph_rank_links(const graph_rank_t *grank, GHashTable *all)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < grank->count; i++)
        g_graph_cluster_define_links(grank->clusters[i], all);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : grank = ensemble de descendants d'un même rang.              *
*                last  = indique s'il s'agit du dernier étage de l'ensemble.  *
*                alloc = emplacement idéal pour l'affichage. [OUT]            *
*                                                                             *
*  Description : Détermine l'emplacement requis d'un ensemble de blocs.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void compute_graph_rank_needed_alloc(const graph_rank_t *grank, bool last, GtkAllocation *alloc)
{
    GtkAllocation needed;                   /* Taille requise              */

    switch (grank->count)
    {
        case 1:

            g_graph_cluster_compute_needed_alloc(grank->clusters[0], &needed);

            if (needed.x < alloc->x)
            {
                alloc->width += (alloc->x - needed.x);
                alloc->x = needed.x;
            }

            if ((needed.x + needed.width) > (alloc->x + alloc->width))
                alloc->width += needed.x + needed.width - alloc->x - alloc->width;

            /* La hauteur maximale n'est présente qu'avec le dernier morceau */
            if (last)
            {
                if ((needed.y + needed.height) > (alloc->y + alloc->height))
                    alloc->height += needed.y + needed.height - alloc->y - alloc->height;
            }

            break;

        default:

            assert(grank->count >= 2);

            g_graph_cluster_compute_needed_alloc(grank->clusters[0], &needed);

            if (needed.x < alloc->x)
            {
                alloc->width += (alloc->x - needed.x);
                alloc->x = needed.x;
            }

            /* La hauteur maximale n'est présente qu'avec le dernier morceau */
            if (last)
            {
                if ((needed.y + needed.height) > (alloc->y + alloc->height))
                    alloc->height += needed.y + needed.height - alloc->y - alloc->height;
            }

            g_graph_cluster_compute_needed_alloc(grank->clusters[grank->count - 1], &needed);

            if ((needed.x + needed.width) > (alloc->x + alloc->width))
                alloc->width += needed.x + needed.width - alloc->x - alloc->width;

            /* La hauteur maximale n'est présente qu'avec le dernier morceau */
            if (last)
            {
                if ((needed.y + needed.height) > (alloc->y + alloc->height))
                    alloc->height += needed.y + needed.height - alloc->y - alloc->height;
            }

            break;

    }

    compute_vspace_manager_needed_alloc(&grank->vspaces, false, alloc);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : iter = début de la boucle de parcours.                       *
*                loop = nombre d'itérations à mener.                          *
*                base = position de base sur l'axe des abscisses.             *
*                dir  = direction du parcours.                                *
*                                                                             *
*  Description : Affine l'abscisse d'un ensemble de blocs de même rang.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void _place_graph_rank_clusters(GGraphCluster **iter, size_t loop, gint base, int dir)
{
    size_t i;                               /* Boucle de parcours          */
    GtkAllocation needed;                   /* Taille requise              */

    assert(dir == -1 || dir == 1);

    for (i = 0; i < loop; i++, iter += dir)
    {
        g_graph_cluster_dispatch_x(*iter);

        g_graph_cluster_compute_needed_alloc(*iter, &needed);

        if (dir > 0)
            g_graph_cluster_offset_x(*iter, base - needed.x);
        else
            g_graph_cluster_offset_x(*iter, base - needed.x - needed.width);

        base += dir * (needed.width + HORIZONTAL_MARGIN);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : grank = ensemble de blocs de même rang à manipuler.          *
*                                                                             *
*  Description : Organise la disposition d'un ensemble de blocs basiques.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void dispatch_x_graph_rank(const graph_rank_t *grank)
{
    size_t mid;                             /* Position centrale de départ */
    GtkAllocation alloc;                    /* Emplacement de cluster      */
    gint start;                             /* Position initiale de départ */

    if (grank->count % 2 == 1)
    {
        if (grank->count > 1)
        {
            mid = grank->count / 2;

            g_graph_cluster_get_allocation(grank->clusters[mid], &alloc);

            start = alloc.x - HORIZONTAL_MARGIN;

            _place_graph_rank_clusters(grank->clusters + mid - 1, mid, start, -1);

            start *= -1;

            _place_graph_rank_clusters(grank->clusters + mid + 1, mid, start, 1);

        }

        else
            g_graph_cluster_dispatch_x(grank->clusters[0]);

    }

    else
    {
        mid = grank->count / 2 - 1;

        start = - HORIZONTAL_MARGIN / 2;

        _place_graph_rank_clusters(grank->clusters + mid, mid + 1, start, -1);

        start *= -1;

        _place_graph_rank_clusters(grank->clusters + mid + 1, mid + 1, start, 1);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : grank  = ensemble de blocs de même rang à actualiser.        *
*                origin = cluster d'origine à considérer.                     *
*                                                                             *
*  Description : Réorganise au besoin les blocs selon les liens d'origine.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void reorder_graph_rank_clusters(graph_rank_t *grank, const GGraphCluster *origin)
{
    size_t i;                               /* Boucle de parcours          */
    GGraphCluster **filtered;               /* Blocs à réorganiser         */
    size_t fcount;                          /* Nombre de ces blocs         */
    size_t next;                            /* Prochain indice à réinsérer */

    if (grank->count > 1)
    {
        /**
         * On prend garde de ne déplacer que les blocs avec un lien concernant
         * un bloc d'origine, dont les liens au départ ont été réorganisés.
         */

        filtered = malloc(grank->count * sizeof(GGraphCluster *));
        fcount = 0;

        for (i = 0; i < grank->count; i++)
            if (g_graph_cluster_has_origin(grank->clusters[i], origin) != NULL)
            {
                filtered[fcount++] = grank->clusters[i];
                grank->clusters[i] = NULL;
            }

        qsort_r(filtered, fcount, sizeof(GGraphCluster *),
                (__compar_d_fn_t)g_graph_cluster_compare_by_origin, (void *)origin);

        next = 0;

        for (i = 0; i < grank->count; i++)
            if (grank->clusters[i] == NULL)
            {
                assert(next < fcount);
                grank->clusters[i] = filtered[next++];
            }

        free(filtered);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : grank = ensemble de blocs de même rang à actualiser.         *
*                                                                             *
*  Description : Réorganise au besoin les liens entrants un ensemble de blocs.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void sort_graph_rank_incoming_links(graph_rank_t *grank)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < grank->count; i++)
        g_graph_cluster_sort_incoming_links(grank->clusters[i]);

    sort_incoming_links_for_vspace_manager(&grank->vspaces);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : grank = ensemble de blocs de même rang à actualiser.         *
*                                                                             *
*  Description : Réordonne les blocs de départ de boucle d'un ensemble.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void reorder_graph_rank_loop_blocks(graph_rank_t *grank)
{
    size_t i;                               /* Boucle de parcours #1       */
    size_t k;                               /* Boucle de parcours #2       */
    GGraphCluster *tmp;                     /* Stockage temporaire         */

    for (i = 0; i < grank->count; i++)
        g_graph_cluster_reorder_loop_blocks(grank->clusters[i]);

    if (grank->count > 1)
    {
        /* Placement des départs de boucle à gauche ! */

        for (i = 0; i < grank->vspaces.left_count; i++)
        {
            tmp = grank->vspaces.left[i]->from->owner;

            for (k = 0; k < grank->count; k++)
                if (grank->clusters[k] == tmp)
                    break;

            assert(k < grank->count);

            memmove(&grank->clusters[1], &grank->clusters[0],
                    k * sizeof(GGraphCluster *));

            grank->clusters[0] = tmp;

            g_graph_cluster_reorder_link_origins(tmp, true);

        }

        /* Placement des départs de boucle à droite ! */

        for (i = 0; i < grank->vspaces.right_count; i++)
        {
            tmp = grank->vspaces.right[i]->from->owner;

            for (k = 0; k < grank->count; k++)
                if (grank->clusters[k] == tmp)
                    break;

            assert(k < grank->count);

            memmove(&grank->clusters[k], &grank->clusters[k + 1],
                    (grank->count - k - 1) * sizeof(GGraphCluster *));

            grank->clusters[grank->count - 1] = tmp;

            g_graph_cluster_reorder_link_origins(tmp, false);

        }

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : grank  = ensemble de blocs de même rang à actualiser.        *
*                offset = décalage à appliquer.                               *
*                                                                             *
*  Description : Décale vers la droite un ensemble de blocs basiques.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void offset_x_graph_rank(graph_rank_t *grank, gint offset)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < grank->count; i++)
        g_graph_cluster_offset_x(grank->clusters[i], offset);

    offset_x_vspace_manager(&grank->vspaces, offset);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : grank  = ensemble de blocs de même rang à actualiser.        *
*                needed = espace nécessaire et alloué pour les blocs.         *
*                                                                             *
*  Description : Détermine les abscisses des liens de boucle en place.        *
*                                                                             *
*  Retour      : Eventuelle marge à gauche devenue nécessaire.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

gint compute_loop_link_x_positions_with_graph_rank(const graph_rank_t *grank, const GtkAllocation *needed)
{
    gint result;                            /* Eventuelle marge à renvoyer */
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < grank->count; i++)
        g_graph_cluster_compute_loop_link_x_positions(grank->clusters[i]);

    result = compute_loop_link_x_with_vspace_manager(&grank->vspaces, needed, false);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : grank = ensemble de blocs de même rang à actualiser.         *
*                base  = position ordonnée à appliquer.                       *
*                                                                             *
*  Description : Décale vers le bas un ensemble de blocs basiques.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void set_y_for_graph_rank(const graph_rank_t *grank, gint *base)
{
    gint max;                               /* Hauteur maximale rencontrée */
    size_t i;                               /* Boucle de parcours          */
    GGraphCluster *sub;                     /* Sous-ensemble traité        */
    GtkAllocation alloc;                    /* Allocation courante         */

    /* On ajoute l'espace vertical pour les lignes horizontales */

    if (grank->r2l_count > grank->l2r_count)
        max = grank->r2l_count;
    else
        max = grank->l2r_count;

    *base += VERTICAL_MARGIN;

    /**
     * Comme les liens purement verticaux n'entrainent pas de réservation,
     * il n'y a potentiellement pas toujours d'espace à ajouter.
     */

    if (max > 0)
    {
        *base += ((max - 1) * LINK_MARGIN);
        *base += VERTICAL_MARGIN;
    }

    /* On ajoute l'espace requis pour l'affichage des blocs */

    max = 0;

    for (i = 0; i < grank->count; i++)
    {
        sub = grank->clusters[i];

        g_graph_cluster_set_y(sub, *base);

        g_graph_cluster_compute_needed_alloc(sub, &alloc);

        if ((alloc.y + alloc.height) > max)
            max = alloc.y + alloc.height;

    }

    *base = max;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : grank = ensemble de blocs de même rang à actualiser.         *
*                needed  = espace nécessaire et alloué pour les blocs.        *
*                                                                             *
*  Description : Détermine les ordonnées de tous les liens en place.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void compute_loop_link_with_graph_rank(const graph_rank_t *grank, const GtkAllocation *needed)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < grank->count; i++)
        g_graph_cluster_compute_link_y_positions(grank->clusters[i]);

    compute_loop_link_y_with_vspace_manager(&grank->vspaces, needed);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : grank = ensemble de blocs de même rang à analyser.           *
*                block = bloc de code à retrouver.                            *
*                                                                             *
*  Description : Recherche le groupe de blocs avec un bloc donné comme chef.  *
*                                                                             *
*  Retour      : Groupe trouvé ou NULL en cas d'échec.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GGraphCluster *find_cluster_by_block_in_graph_rank(const graph_rank_t *grank, GCodeBlock *block)
{
    GGraphCluster *result;                  /* Trouvaille à retourner      */
    size_t i;                               /* Boucle de parcours          */

    result = NULL;

    for (i = 0; i < grank->count && result == NULL; i++)
        result = g_graph_cluster_find_by_block(grank->clusters[i], block);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : grank  = ensemble de blocs de même rang à analyser.          *
*                widget = composant graphique à retrouver.                    *
*                                                                             *
*  Description : Recherche le groupe de blocs avec un composant comme chef.   *
*                                                                             *
*  Retour      : Groupe trouvé ou NULL en cas d'échec.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GGraphCluster *find_cluster_by_widget_in_graph_rank(const graph_rank_t *grank, GtkWidget *widget)
{
    GGraphCluster *result;                  /* Trouvaille à retourner      */
    size_t i;                               /* Boucle de parcours          */

    result = NULL;

    for (i = 0; i < grank->count && result == NULL; i++)
        result = g_graph_cluster_find_by_widget(grank->clusters[i], widget);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : grank = ensemble de blocs de même rang à analyser.           *
*                list  = liste en cours de constitution. [OUT]                *
*                count = taille de cette liste. [OUT]                         *
*                                                                             *
*  Description : Collecte tous les chefs de file de blocs de code.            *
*                                                                             *
*  Retour      : Liste de graphiques de blocs rassemblés.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GGraphCluster **collect_graph_ranks_clusters(const graph_rank_t *grank, GGraphCluster **list, size_t *count)
{
    GGraphCluster **result;                 /* Liste complétée à renvoyer  */
    size_t i;                               /* Boucle de parcours          */

    result = list;

    for (i = 0; i < grank->count; i++)
        result = g_graph_cluster_collect(grank->clusters[i], result, count);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : grank = ensemble de blocs de même rang à analyser.           *
*                list  = liste en cours de constitution. [OUT]                *
*                count = taille de cette liste. [OUT]                         *
*                                                                             *
*  Description : Collecte tous les liens de chefs de file de blocs de code.   *
*                                                                             *
*  Retour      : Liste de liens graphiques de blocs rassemblés.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GGraphEdge **collect_graph_ranks_cluster_edges(const graph_rank_t *grank, GGraphEdge **list, size_t *count)
{
    GGraphEdge **result;                    /* Liste complétée à renvoyer  */
    size_t i;                               /* Boucle de parcours          */

    result = list;

    for (i = 0; i < grank->count; i++)
        result = g_graph_cluster_collect_edges(grank->clusters[i], result, count);

    return result;

}
