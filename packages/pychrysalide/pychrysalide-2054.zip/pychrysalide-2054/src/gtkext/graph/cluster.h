
/* Chrysalide - Outil d'analyse de fichiers binaires
 * cluster.h - prototypes pour la mise en place de graphiques
 *
 * Copyright (C) 2016-2019 Cyrille Bagard
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


#ifndef _GTKEXT_GRAPH_CLUSTER_H
#define _GTKEXT_GRAPH_CLUSTER_H


#include "edge.h"
#include "../gtkgraphdisplay.h"
#include "../../analysis/binary.h"
#include "../../analysis/disass/block.h"



/* -------------------------- DEFINITION D'UN CHEF DE FILE -------------------------- */


#define G_TYPE_GRAPH_CLUSTER            g_graph_cluster_get_type()
#define G_GRAPH_CLUSTER(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_GRAPH_CLUSTER, GGraphCluster))
#define G_IS_GRAPH_CLUSTER(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_GRAPH_CLUSTER))
#define G_GRAPH_CLUSTER_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_GRAPH_CLUSTER, GGraphClusterClass))
#define G_IS_GRAPH_CLUSTER_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_GRAPH_CLUSTER))
#define G_GRAPH_CLUSTER_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_GRAPH_CLUSTER, GGraphClusterClass))


/* Mise en disposition de blocs en graphique (instance) */
typedef struct _GGraphCluster GGraphCluster;

/* Mise en disposition de blocs en graphique (classe) */
typedef struct _GGraphClusterClass GGraphClusterClass;


/* Indique le type défini par la GLib pour les mises en disposition graphique. */
GType g_graph_cluster_get_type(void);

/* Construit un graphique à partir de blocs de code. */
GGraphCluster *g_graph_cluster_new(GCodeBlock *, segcnt_list *, GLoadedBinary *);

/* Fournit le bloc de code principal du groupe. */
GCodeBlock *g_graph_cluster_get_block(GGraphCluster *);

/* Fournit le composant graphique principal du groupe. */
GtkWidget *g_graph_cluster_get_widget(GGraphCluster *);

/* Fournit l'emplacement prévu pour un chef de file de blocs. */
void g_graph_cluster_get_allocation(const GGraphCluster *, GtkAllocation *);

/* Détermine l'emplacement requis d'un ensemble de blocs. */
void g_graph_cluster_compute_needed_alloc(const GGraphCluster *, GtkAllocation *);

/* Dispose chaque noeud sur la surface de destination donnée. */
void g_graph_cluster_place(GGraphCluster *, GtkGraphDisplay *);

/* Recherche le groupe de blocs avec un bloc donné comme chef. */
GGraphCluster *g_graph_cluster_find_by_block(GGraphCluster *, GCodeBlock *);

/* Recherche le groupe de blocs avec un composant comme chef. */
GGraphCluster *g_graph_cluster_find_by_widget(GGraphCluster *, GtkWidget *);



/* ------------------------- CALCUL DE REPARTITION DE BLOCS ------------------------- */


/* Construit un graphique à partir de blocs basiques. */
GGraphCluster *bootstrap_graph_cluster(GLoadedBinary *, const GBlockList *, segcnt_list *);

/* Collecte tous les chefs de file de blocs de code. */
GGraphCluster **collect_graph_clusters(GGraphCluster *, size_t *);

/* Collecte tous les liens de chefs de file de blocs de code. */
GGraphEdge **collect_graph_cluster_edges(GGraphCluster *, size_t *);



#endif  /* _GTKEXT_GRAPH_CLUSTER_H */
