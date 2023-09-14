
/* Chrysalide - Outil d'analyse de fichiers binaires
 * rank.h - prototypes pour le classement par rang des descendants directs
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


#ifndef _GTKEXT_GRAPH_RANK_H
#define _GTKEXT_GRAPH_RANK_H


#include "cluster.h"
#include "edge.h"
#include "hspace.h"
#include "vspace.h"



/* Découpage vertical */
typedef struct _graph_rank_t
{
    hspace_booking **right2left;            /* Réservations de D -> G      */
    size_t r2l_count;                       /* Quantité de ces réservations*/

    hspace_booking **left2right;            /* Réservations de G -> D      */
    size_t l2r_count;                       /* Quantité de ces réservations*/

    GGraphCluster **clusters;               /* Ensembles de blocs          */
    size_t count;                           /* Nombre de ces ensembles     */

    vspace_manager_t vspaces;               /* Gestion des liens latéraux  */

} graph_rank_t;


/* Initialise la gestion d'un ensemble de blocs de même rang. */
void init_graph_rank(graph_rank_t *, GGraphCluster *);

/* Termine la gestion d'un ensemble de blocs de même rang. */
void exit_graph_rank(graph_rank_t *);

/* Visiteur pour blocs */
typedef void (* graph_rank_cb) (GGraphCluster *);

/* Parcours l'ensemble des blocs du rang avec un visiteur. */
void visit_graph_rank(const graph_rank_t *grank, graph_rank_cb);

/* Visiteur pour blocs */
typedef bool (* graph_rank_acc_cb) (GGraphCluster *);

/* Parcours l'ensemble des blocs du rang avec un visiteur. */
bool visit_and_accumulate_graph_rank(const graph_rank_t *, graph_rank_acc_cb);

/* Fournit le rang d'un ensemble de blocs. */
size_t get_graph_rank(const graph_rank_t *);

/* Compare deux rangées de blocs de code. */
int cmp_graph_rank(const graph_rank_t *, const graph_rank_t *);

/* Etend un ensemble de blocs de même rang. */
void extend_graph_rank(graph_rank_t *, GGraphCluster *);

/* Détermine si un groupe de blocs contient un bloc particulier. */
bool has_graph_rank_cluster(const graph_rank_t *, GGraphCluster *);

/* Inscrit à l'endroit idéal une réservation d'espace latéral. */
bool extend_graph_rank_vspace_manager(graph_rank_t *, leaving_link_t *, incoming_link_t *, GdkPoint *, bool);

/* Met en place les embryons de liens nécessaires. */
void define_graph_rank_links(const graph_rank_t *, GHashTable *);

/* Détermine l'emplacement requis d'un ensemble de blocs. */
void compute_graph_rank_needed_alloc(const graph_rank_t *, bool, GtkAllocation *);

/* Affine l'abscisse d'un ensemble de blocs de même rang. */
void _place_graph_rank_clusters(GGraphCluster **, size_t, gint, int);

/* Organise la disposition d'un ensemble de blocs basiques. */
void dispatch_x_graph_rank(const graph_rank_t *);

/* Réorganise au besoin les blocs selon les liens d'origine. */
void reorder_graph_rank_clusters(graph_rank_t *, const GGraphCluster *);

/* Réorganise au besoin les liens entrants un ensemble de blocs. */
void sort_graph_rank_incoming_links(graph_rank_t *);

/* Réordonne les blocs de départ de boucle d'un ensemble. */
void reorder_graph_rank_loop_blocks(graph_rank_t *);

/* Décale vers la droite un ensemble de blocs basiques. */
void offset_x_graph_rank(graph_rank_t *, gint);

/* Détermine les abscisses des liens de boucle en place. */
gint compute_loop_link_x_positions_with_graph_rank(const graph_rank_t *, const GtkAllocation *);

/* Décale vers le bas un ensemble de blocs basiques. */
void set_y_for_graph_rank(const graph_rank_t *, gint *);

/* Détermine les ordonnées de tous les liens en place. */
void compute_loop_link_with_graph_rank(const graph_rank_t *, const GtkAllocation *);

/* Recherche le groupe de blocs avec un bloc donné comme chef. */
GGraphCluster *find_cluster_by_block_in_graph_rank(const graph_rank_t *, GCodeBlock *);

/* Recherche le groupe de blocs avec un composant comme chef. */
GGraphCluster *find_cluster_by_widget_in_graph_rank(const graph_rank_t *, GtkWidget *);

/* Collecte tous les chefs de file de blocs de code. */
GGraphCluster **collect_graph_ranks_clusters(const graph_rank_t *, GGraphCluster **, size_t *);

/* Collecte tous les liens de chefs de file de blocs de code. */
GGraphEdge **collect_graph_ranks_cluster_edges(const graph_rank_t *, GGraphEdge **, size_t *);



#endif  /* _GTKEXT_GRAPH_RANK_H */
