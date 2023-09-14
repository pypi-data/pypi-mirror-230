
/* Chrysalide - Outil d'analyse de fichiers binaires
 * named.h - prototypes pour la préparation de composants à l'affichage avec leurs noms
 *
 * Copyright (C) 2020 Cyrille Bagard
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


#ifndef _GTKEXT_NAMED_H
#define _GTKEXT_NAMED_H


#include <glib-object.h>
#include <gtk/gtk.h>



#define GTK_TYPE_BUILT_NAMED_WIDGET            (gtk_built_named_widget_get_type())
#define GTK_BUILT_NAMED_WIDGET(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), GTK_TYPE_BUILT_NAMED_WIDGET, GtkBuiltNamedWidget))
#define GTK_BUILT_NAMED_WIDGET_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), GTK_TYPE_BUILT_NAMED_WIDGET, GtkBuiltNamedWidgetClass))
#define GTK_IS_BUILT_NAMED_WIDGET(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), GTK_TYPE_BUILT_NAMED_WIDGET))
#define GTK_IS_BUILT_NAMED_WIDGET_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), GTK_TYPE_BUILT_NAMED_WIDGET))
#define GTK_BUILT_NAMED_WIDGET_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), GTK_TYPE_BUILT_NAMED_WIDGET, GtkBuiltNamedWidgetClass))


/* Préparation d'un composant pour affichage avec ses noms (instance) */
typedef struct _GtkBuiltNamedWidget GtkBuiltNamedWidget;

/* Préparation d'un composant pour affichage avec ses noms (classe) */
typedef struct _GtkBuiltNamedWidgetClass GtkBuiltNamedWidgetClass;


/* Détermine le type des préparations de composant pour affichage avec noms. */
GType gtk_built_named_widget_get_type(void);

/* Crée une préparation pour l'affichage d'un composant nommé. */
GtkBuiltNamedWidget *gtk_built_named_widget_new(const char *, const char *, const char *);

/* Crée une préparation pour l'affichage d'un composant nommé. */
GtkBuiltNamedWidget *gtk_built_named_widget_new_for_panel(const char *, const char *, const char *);

/* Fournit le constructeur facilitant l'affichage. */
GtkBuilder *gtk_built_named_widget_get_builder(const GtkBuiltNamedWidget *);



#endif  /* _GTKEXT_NAMED_H */
