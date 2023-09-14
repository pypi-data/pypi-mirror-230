
/* Chrysalide - Outil d'analyse de fichiers binaires
 * easygtk.h - prototypes pour la mise en place rapide de composants GTK
 *
 * Copyright (C) 2009-2018 Cyrille Bagard
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


#ifndef _GTKEXT_EASYGTK_H
#define _GTKEXT_EASYGTK_H


#include <stdbool.h>
#include <gtk/gtk.h>


/* Conversion anonyme */
#define ALLOC_2_REQ(a) ((GtkRequisition []){ { .width = (a)->width, .height = (a)->height }})

/* Transition vers GTK-3.x claire */
#define HAS_H_ORIENTATION(wid) gtk_orientable_get_orientation(GTK_ORIENTABLE(wid)) == GTK_ORIENTATION_HORIZONTAL

/* Enregistrement des fonctions pour GtkBuilder */
#define BUILDER_CALLBACK(cb) #cb, G_CALLBACK(cb)


/* Définit des bordures extérieures à appliquer à un composant. */
void qck_set_margins(GtkWidget *, guint, guint, guint, guint);

/* Met en place une frame. */
GtkWidget *qck_create_frame(const char *, GtkWidget *, guint, guint, guint, guint);

/* Met en place un support avec défilement automatique. */
GtkWidget *qck_create_scrolled_window(GObject *, const char *);

/* Crée un composant 'GtkLabel'. */
GtkWidget *qck_create_label(GObject *, const char *, const char *);

/* Crée et enregistre un composant 'GtkEntry'. */
GtkWidget *qck_create_entry(GObject *, const char *, const char *);

/* Crée et enregistre un composant 'GtkButton'. */
GtkWidget *qck_create_button(GObject *, const char *, const char *, GCallback, gpointer);

/* Crée et enregistre un composant 'GtkButton'. */
GtkWidget *qck_create_button_with_named_img(GObject *, const char *, const char *, GtkIconSize, const char *, GCallback, gpointer);

/* Crée et enregistre un composant 'GtkCheckButton'. */
GtkWidget *qck_create_toggle_button_with_named_img(GObject *, const char *, const char *, GtkIconSize, const char *, GCallback, gpointer);

/* Crée et enregistre un composant 'GtkCheckButton'. */
GtkWidget *qck_create_check_button(GObject *, const char *, const char *, GCallback, gpointer);

/* Crée et enregistre un composant 'GtkRadioButton'. */
GtkWidget *qck_create_radio_button(GObject *, const char *, const char *, GtkRadioButton *, GCallback, gpointer);

/* Crée et enregistre un composant 'GtkComboBox'. */
GtkWidget *qck_create_combobox(GObject *, const char *, GCallback, gpointer);

/* Crée et enregistre un composant 'GtkComboBox'. */
GtkWidget *qck_create_combobox_with_entry(GObject *, const char *, GCallback, gpointer);

/* Met en place un support de menu 'GtkMenu'. */
GtkWidget *qck_create_menu(GtkMenuItem *);

/* Crée et enregistre un composant 'GtkMenuItem'. */
GtkWidget *qck_create_menu_item(GObject *, const char *, const char *, GCallback, gpointer);

/* Crée et enregistre un composant 'GtkCheckMenuItem'. */
GtkWidget *qck_create_check_menu_item(GObject *, const char *, const char *, GCallback, gpointer);

/* Crée et enregistre un composant 'GtkRadioMenuItem'. */
GtkWidget *qck_create_radio_menu_item(GObject *, const char *, GSList *, const char *, GCallback, gpointer);

/* Crée et enregistre un composant 'GtkSeparatorMenuItem'. */
GtkWidget *qck_create_menu_separator(void);





/* Identifie la couleur de base associée à un style GTK. */
bool get_color_from_style(const char *, bool, GdkRGBA *);

/* Détermine l'indice d'un composant dans un conteneur GTK. */
gint find_contained_child_index(GtkContainer *, GtkWidget *);

/* Récupère le nième composant d'un conteneur GTK. */
GtkWidget *get_nth_contained_child(GtkContainer *, guint);

/* Affiche une boîte de dialogue offrant un choix "Oui/Non". */
gint qck_show_question(GtkWindow *, const char *, const char *);

/* Fait défiler une liste jusqu'à un point donné. */
void scroll_to_treeview_iter(GtkTreeView *, GtkTreeModel *, GtkTreeIter *);



#endif  /* _GTKEXT_EASYGTK_H */
