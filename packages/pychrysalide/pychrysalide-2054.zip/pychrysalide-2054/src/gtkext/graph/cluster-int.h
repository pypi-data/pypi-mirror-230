
/* Chrysalide - Outil d'analyse de fichiers binaires
 * cluster-int.h - prototypes pour les définitions internes de mise en place de graphiques
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


#ifndef _GTKEXT_GRAPH_CLUSTER_INT_H
#define _GTKEXT_GRAPH_CLUSTER_INT_H


#include "cluster.h"
#include "leaving.h"



/* Espace minimal horizontal entre les blocs */
#define HORIZONTAL_MARGIN 20

/* Espace minimal vertical entre les blocs */
#define VERTICAL_MARGIN 15


/* Assigne à un bloc et son ensemble un emplacement initial. */
void g_graph_cluster_reset_allocation(GGraphCluster *);

/* Réinitialise les décalages pour les lignes verticales. */
void g_graph_cluster_reset_extra_offsets(GGraphCluster *);

/* Met en place les embryons de liens nécessaires. */
void g_graph_cluster_define_links(GGraphCluster *, GHashTable *);

/* Repère les liens marquants à destination d'autres blocs. */
void g_graph_cluster_setup_links(GGraphCluster *);

/* Détermine un éventuel lien entrant réellement vertical. */
incoming_link_t *g_graph_cluster_find_real_straight_incoming(GGraphCluster *, size_t *);

/* Organise la disposition d'un ensemble de blocs basiques. */
void g_graph_cluster_dispatch_x(GGraphCluster *);

/* Calcule les abscisses extrèmes atteintes via liens de sortie. */
bool g_graph_cluster_compute_min_max_x_exit(const GGraphCluster *, const GGraphCluster *, gint [2]);

/* Calcule les abscisses extrèmes atteintes horizontalement. */
void g_graph_cluster_compute_min_max_horizontal(const GGraphCluster *, gint, gint [2]);

/* Définit d'éventuels décalages pour les lignes verticales. */
bool g_graph_cluster_dispatch_define_extra_offset(GGraphCluster *);

/* Détermine une direction préférée pour la suite du bloc. */
LeavingLinkDir g_graph_cluster_get_link_direction(const GGraphCluster *, gint, gint);

/* Réorganise au besoin les liens sortants d'un bloc. */
void g_graph_cluster_sort_leaving_links(GGraphCluster *);

/* Calcule l'ordonnée la plus profonde via liens sortants. */
bool g_graph_cluster_compute_min_y_target(const GGraphCluster *, const GGraphCluster *, gint *);

/* Retrouve s'il existe un lien entrant vers un bloc d'origine. */
const leaving_link_t *g_graph_cluster_has_origin(const GGraphCluster *, const GGraphCluster *);

/* Compare deux clusters selon un de leurs liens d'origine. */
int g_graph_cluster_compare_by_origin(const GGraphCluster **, const GGraphCluster **, const GGraphCluster *);

/* Réorganise au besoin les liens entrants d'un bloc. */
void g_graph_cluster_sort_incoming_links(GGraphCluster *);

/* Retrouve l'indice d'un lien entrant donné pour un bloc. */
size_t g_graph_cluster_find_incoming_link(const GGraphCluster *, const leaving_link_t *);

/* Réordonne les blocs de départ de boucle au mieux. */
void g_graph_cluster_reorder_loop_blocks(GGraphCluster *);

/* Réordonne le départ des liens en entrée de bloc. */
void g_graph_cluster_reorder_link_origins(GGraphCluster *, bool);

/* Décale vers la droite un ensemble de blocs basiques. */
void g_graph_cluster_offset_x(GGraphCluster *, gint);

/* Décale vers le bas un ensemble de blocs basiques. */
void g_graph_cluster_set_y(GGraphCluster *, gint);

/* Calcule l'abscisse d'un lien pour un bloc. */
gint _g_graph_cluster_compute_link_position(const GGraphCluster *, size_t, size_t, bool);

/* Calcule l'abscisse d'un lien à son départ d'un bloc. */
gint g_graph_cluster_compute_leaving_link_position(const GGraphCluster *, size_t);

/* Calcule l'abscisse d'un lien à son arrivée à un bloc. */
gint g_graph_cluster_compute_incoming_link_position(const GGraphCluster *, size_t);

/* Détermine les abscisses des liens de boucle en place. */
void g_graph_cluster_compute_loop_link_x_positions(GGraphCluster *);

/* Détermine les ordonnées de tous les liens en place. */
void g_graph_cluster_compute_link_y_positions(GGraphCluster *);

/* Collecte tous les chefs de file de blocs de code. */
GGraphCluster **g_graph_cluster_collect(GGraphCluster *, GGraphCluster **, size_t *);

/* Collecte tous les liens de chefs de file de blocs de code. */
GGraphEdge **g_graph_cluster_collect_edges(GGraphCluster *, GGraphEdge **, size_t *);



#endif
