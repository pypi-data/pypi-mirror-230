
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gtkgraphdisplay.h - prototypes pour l'affichage de morceaux de code sous forme graphique
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


#ifndef _GTKEXT_GTKGRAPHDISPLAY_H
#define _GTKEXT_GTKGRAPHDISPLAY_H


#include <gtk/gtk.h>


#include "graph/edge.h"



#define GTK_TYPE_GRAPH_DISPLAY            (gtk_graph_display_get_type())
#define GTK_GRAPH_DISPLAY(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), GTK_TYPE_GRAPH_DISPLAY, GtkGraphDisplay))
#define GTK_GRAPH_DISPLAY_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), GTK_TYPE_GRAPH_DISPLAY, GtkGraphDisplayClass))
#define GTK_IS_GRAPH_DISPLAY(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), GTK_TYPE_GRAPH_DISPLAY))
#define GTK_IS_GRAPH_DISPLAY_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), GTK_TYPE_GRAPH_DISPLAY))
#define GTK_GRAPH_DISPLAY_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), GTK_TYPE_GRAPH_DISPLAY, GtkGraphDisplayClass))


/* Composant d'affichage sous forme graphique (instance) */
typedef struct _GtkGraphDisplay GtkGraphDisplay;

/* Composant d'affichage sous forme graphique (classe) */
typedef struct _GtkGraphDisplayClass GtkGraphDisplayClass;


/* Détermine le type du composant d'affichage en graphique. */
GType gtk_graph_display_get_type(void);

/* Crée un nouveau composant pour l'affichage en graphique. */
GtkWidget *gtk_graph_display_new(void);

/* Fournit le support utilisé pour le rendu graphique. */
GtkWidget *gtk_graph_display_get_support(GtkGraphDisplay *);

/* Place une vue sous forme de bloc dans le graphique. */
void gtk_graph_display_put(GtkGraphDisplay *, GtkWidget *, const GtkAllocation *);

/* Intègre un lien entre blocs graphiques dans l'afficheur. */
void gtk_graph_display_add_edge(GtkGraphDisplay *, GGraphEdge *);



#endif  /* _GTKEXT_GTKGRAPHDISPLAY_H */
