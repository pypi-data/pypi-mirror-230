
/* Chrysalide - Outil d'analyse de fichiers binaires
 * edge.h - prototypes pour les liens entre les noeuds d'un graphique
 *
 * Copyright (C) 2013-2019 Cyrille Bagard
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


#ifndef _GTKEXT_GRAPH_EDGE_H
#define _GTKEXT_GRAPH_EDGE_H


#include <glib-object.h>
#include <stdbool.h>
#include <gtk/gtk.h>


#include "../../analysis/block.h"



#define G_TYPE_GRAPH_EDGE            g_graph_edge_get_type()
#define G_GRAPH_EDGE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_GRAPH_EDGE, GGraphEdge))
#define G_IS_GRAPH_EDGE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_GRAPH_EDGE))
#define G_GRAPH_EDGE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_GRAPH_EDGE, GGraphEdgeClass))
#define G_IS_GRAPH_EDGE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_GRAPH_EDGE))
#define G_GRAPH_EDGE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_GRAPH_EDGE, GGraphEdgeClass))


/* Lien graphique entre deux noeuds graphiques (instance) */
typedef struct _GGraphEdge GGraphEdge;

/* Lien graphique entre deux noeuds graphiques (classe) */
typedef struct _GGraphEdgeClass GGraphEdgeClass;


/* Couleur de représentation */
typedef enum _EdgeColor
{
    EGC_DEFAULT,                            /* Noir, par défaut            */
    EGC_GREEN,                              /* Condition vérifiée          */
    EGC_RED,                                /* Condition non vérifiée      */
    EGC_BLUE,                               /* Boucle détectée             */
    EGC_DASHED_GRAY,                        /* Exception omniprésente      */

    EGC_COUNT

} EdgeColor;


/* Espace minimal entre les liens */
#define LINK_MARGIN 10


/* Indique le type défini par la GLib pour les liens graphiques entre noeuds. */
GType g_graph_edge_get_type(void);

/* Etablit un lien graphique entre deux noeuds graphiques. */
GGraphEdge *_g_graph_edge_new(GCodeBlock *, GCodeBlock *, const GdkPoint **, size_t, EdgeColor);

#define g_graph_edge_new(src, dst, pts0, pts1, pte0, pte1) \
    _g_graph_edge_new(src, dst, (const GdkPoint *[]) { pts0, pts1, pte0, pte1 }, 4, EGC_DEFAULT)

#define g_graph_edge_new_true(src, dst, pts0, pts1, pte0, pte1) \
    _g_graph_edge_new(src, dst, (const GdkPoint *[]) { pts0, pts1, pte0, pte1 }, 4, EGC_GREEN)

#define g_graph_edge_new_false(src, dst, pts0, pts1, pte0, pte1) \
    _g_graph_edge_new(src, dst, (const GdkPoint *[]) { pts0, pts1, pte0, pte1 }, 4, EGC_RED)

#define g_graph_edge_new_loop(src, dst, pts0, pts1, ptl0, ptl1, pte0, pte1) \
    _g_graph_edge_new(src, dst, (const GdkPoint *[]) { pts0, pts1, ptl0, ptl1, pte0, pte1 }, 6, EGC_BLUE)

/* Fournit les deux blocs aux extrémités d'un lien. */
void g_graph_edge_get_boundaries(const GGraphEdge *, GCodeBlock **, GCodeBlock **);

/* Fournit la couleur de rendu d'un lien graphique. */
EdgeColor g_graph_edge_get_color(const GGraphEdge *);

/* Fournit les abscisses des points extrèmes de la ligne. */
void g_graph_edge_get_x_borders(const GGraphEdge *, gint *, gint *);

/* Détermine les positions finales d'un lien graphique. */
void g_graph_edge_resolve(GGraphEdge *);

/* Opère un décalage du lien dans une direction donnée. */
void g_graph_edge_offset(GGraphEdge *, gint, gint);

/* Fournit l'ensemble des points constituant un lien graphique. */
const GdkPoint *g_graph_edge_get_points(const GGraphEdge *, size_t *);

/* Opère un décalage du lien dans une direction donnée. */
bool g_graph_edge_detect_at(const GGraphEdge *, gint, gint);

/* Dessine les liens graphiques enregistrés dans le moteur. */
void g_graph_edge_draw(const GGraphEdge *, cairo_t *, bool, bool);



#endif  /* _GTKEXT_GRAPH_EDGE_H */
