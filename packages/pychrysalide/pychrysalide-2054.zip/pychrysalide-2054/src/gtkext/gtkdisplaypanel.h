
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gtkdisplaypanel.h - prototypes pour l'affichage de contenus de binaire
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


#ifndef _GTKEXT_DISPLAYPANEL_H
#define _GTKEXT_DISPLAYPANEL_H


#include <glib-object.h>
#include <stdbool.h>


#include "../arch/vmpa.h"
#include "../glibext/gloadedpanel.h"



#define GTK_TYPE_DISPLAY_PANEL              (gtk_display_panel_get_type())
#define GTK_DISPLAY_PANEL(obj)              (G_TYPE_CHECK_INSTANCE_CAST((obj), GTK_TYPE_DISPLAY_PANEL, GtkDisplayPanel))
#define GTK_DISPLAY_PANEL_CLASS(klass)      (G_TYPE_CHECK_CLASS_CAST((klass), GTK_TYPE_DISPLAY_PANEL, GtkDisplayPanelClass))
#define GTK_IS_DISPLAY_PANEL(obj)           (G_TYPE_CHECK_INSTANCE_TYPE((obj), GTK_TYPE_DISPLAY_PANEL))
#define GTK_IS_DISPLAY_PANEL_CLASS(klass)   (G_TYPE_CHECK_CLASS_TYPE((klass), GTK_TYPE_DISPLAY_PANEL))
#define GTK_DISPLAY_PANEL_GET_CLASS(obj)    (G_TYPE_INSTANCE_GET_CLASS((obj), GTK_TYPE_DISPLAY_PANEL, GtkDisplayPanelClass))


/* Composant d'affichage générique (instance) */
typedef struct _GtkDisplayPanel GtkDisplayPanel;

/* Composant d'affichage générique (classe) */
typedef struct _GtkDisplayPanelClass GtkDisplayPanelClass;


/* Détermine le type du composant d'affichage générique. */
GType gtk_display_panel_get_type(void);

/* Indique l'échelle appliquée à l'affichage du composant. */
double gtk_display_panel_get_scale(const GtkDisplayPanel *);

/* Spécifie l'échelle à appliquer à l'affichage du composant. */
void gtk_display_panel_set_scale(GtkDisplayPanel *, double);

/* Définit si une bordure est à afficher. */
void gtk_display_panel_show_border(GtkDisplayPanel *, bool);

/* Marque ou non le composant pour une exportation prochaine. */
void gtk_display_panel_prepare_export(GtkDisplayPanel *, bool);

/* Indique la position d'affichage d'un emplacement donné. */
bool gtk_display_panel_get_cursor_coordinates(const GtkDisplayPanel *, const GLineCursor *, gint *, gint *, ScrollPositionTweak);

/* Fournit l'élément actif lié à la position courante. */
GObject *gtk_display_panel_get_active_object(const GtkDisplayPanel *);

/* Demande à qui veut répondre un déplacement du curseur. */
void gtk_display_panel_request_move(GtkDisplayPanel *, const vmpa2t *);



#endif  /* _GTKEXT_DISPLAYPANEL_H */
