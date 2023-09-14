
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gtkdockable.h - prototypes pour les éléments acceptés dans les composants de rassemblement
 *
 * Copyright (C) 2015-2019 Cyrille Bagard
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


#ifndef _GTKEXT_GTKDOCKABLE_H
#define _GTKEXT_GTKDOCKABLE_H


#include <stdbool.h>
#include <gtk/gtk.h>



#define GTK_TYPE_DOCKABLE             (gtk_dockable_get_type())
#define GTK_DOCKABLE(obj)             (G_TYPE_CHECK_INSTANCE_CAST((obj), GTK_TYPE_DOCKABLE, GtkDockable))
#define GTK_DOCKABLE_CLASS(vtable)    (G_TYPE_CHECK_CLASS_CAST((vtable), GTK_TYPE_DOCKABLE, GtkDockableIface))
#define GTK_IS_DOCKABLE(obj)          (G_TYPE_CHECK_INSTANCE_TYPE((obj), GTK_TYPE_DOCKABLE))
#define GTK_IS_DOCKABLE_CLASS(vtable) (G_TYPE_CHECK_CLASS_TYPE((vtable), GTK_TYPE_DOCKABLE))
#define GTK_DOCKABLE_GET_IFACE(inst)  (G_TYPE_INSTANCE_GET_INTERFACE((inst), GTK_TYPE_DOCKABLE, GtkDockableIface))


/* Elément accepté dans les rassemblements (coquille vide) */
typedef struct _GtkDockable GtkDockable;

/* Elément accepté dans les rassemblements (interface) */
typedef struct _GtkDockableIface GtkDockableIface;



/* Détermine le type d'une interface pour rassemblement. */
GType gtk_dockable_get_type(void) G_GNUC_CONST;

/* Fournit le nom court du composant encapsulable. */
char *gtk_dockable_get_name(const GtkDockable *);

/* Fournit le nom long du composant encapsulable. */
char *gtk_dockable_get_desc(const GtkDockable *);

/* Indique si le composant représenté à du contenu à fouiller. */
bool gtk_dockable_can_search(const GtkDockable *);

/* Fournit le composant graphique intégrable dans un ensemble. */
GtkWidget *gtk_dockable_build_widget(GtkDockable *);

/* Fournit tous les éléments pour un retrait graphique. */
GtkWidget *gtk_dockable_decompose(GtkDockable *, GtkWidget **);

/* Révèle ou cache la zone de recherches. */
void gtk_dockable_toggle_revealer(GtkDockable *, GtkWidget *, gboolean);



/* ----------------------- PROCEDURES POUR LE GLISSER-DEPOSER ----------------------- */


/* Prépare en sous-main la fenêtre de prédiction du déposer. */
void prepare_drag_and_drop_window(void);

/* Initialise les fonctions de glisser/déposer pour un élément. */
void gtk_dockable_setup_dnd(GtkDockable *);



#endif  /* _GTKEXT_GTKDOCKABLE_H */
