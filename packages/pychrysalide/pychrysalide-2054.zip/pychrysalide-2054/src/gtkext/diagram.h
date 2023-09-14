
/* Chrysalide - Outil d'analyse de fichiers binaires
 * diagram.h - prototypes pour un composant d'affichage avec de digrammes
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#ifndef _GTKEXT_DIAGRAM_H
#define _GTKEXT_DIAGRAM_H


#include <gtk/gtk.h>



#define GTK_TYPE_DIAGRAM            gtk_diagram_get_type()
#define GTK_DIAGRAM(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), GTK_TYPE_DIAGRAM, GtkDiagram))
#define GTK_IS_DIAGRAM(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), GTK_TYPE_DIAGRAM))
#define GTK_DIAGRAM_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), GTK_TYPE_DIAGRAM, GtkDiagramClass))
#define GTK_IS_DIAGRAM_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), GTK_TYPE_DIAGRAM))
#define GTK_DIAGRAM_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), GTK_TYPE_DIAGRAM, GtkDiagramClass))


/* Composant de dessin de diagramme (instance) */
typedef struct _GtkDiagram GtkDiagram;

/* Composant de dessin de diagramme (classe) */
typedef struct _GtkDiagramClass GtkDiagramClass;

/* Types de diagrammes supportés */
typedef enum _DiagramRenderingType
{
    DRT_PIE,                                /* En camembert                */
    DRT_HISTO                               /* En barres                   */

} DiagramRenderingType;

/* Transmission de statistiques */
typedef struct _diagram_stat_t
{
    double value;                           /* Valeur à représenter        */
    GdkRGBA color;                          /* Couleur de représentation   */

    char *desc;                             /* Eventuelle description      */

} diagram_stat_t;


#define DIAGRAM_MARGIN 20


/* Détermine le type de l'afficheur de diagramme. */
GType gtk_diagram_get_type(void);

/* Crée une nouvelle instance de dessinateur de diagramme. */
GtkWidget *gtk_diagram_new(DiagramRenderingType, const GdkRGBA *);

/* Supprime tous les éléments représentés dans le diagramme. */
void gtk_diagram_clear_stats(GtkDiagram *);

/* Ajoute des éléments à représenter dans le diagramme. */
void gtk_diagram_add_stats(GtkDiagram *, const diagram_stat_t *, size_t);



#endif  /* _GTKEXT_DIAGRAM_H */
