
/* Chrysalide - Outil d'analyse de fichiers binaires
 * named.h - prototypes pour la manipulation de composants nommés
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


#ifndef _GLIBEXT_NAMED_H
#define _GLIBEXT_NAMED_H


#include <glib-object.h>
#include <stdbool.h>
#include <gtk/gtk.h>



#define G_TYPE_NAMED_WIDGET               g_named_widget_get_type()
#define G_NAMED_WIDGET(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_NAMED_WIDGET, GNamedWidget))
#define G_NAMED_WIDGET_CLASS(vtable)      (G_TYPE_CHECK_CLASS_CAST((vtable), G_TYPE_NAMED_WIDGET, GNamedWidgetIface))
#define GTK_IS_NAMED_WIDGET(obj)          (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_NAMED_WIDGET))
#define GTK_IS_NAMED_WIDGET_CLASS(vtable) (G_TYPE_CHECK_CLASS_TYPE((vtable), G_TYPE_NAMED_WIDGET))
#define G_NAMED_WIDGET_GET_IFACE(inst)    (G_TYPE_INSTANCE_GET_INTERFACE((inst), G_TYPE_NAMED_WIDGET, GNamedWidgetIface))


/* Manipulation d'un composant avec ses noms (coquille vide) */
typedef struct _GNamedWidget GNamedWidget;

/* Manipulation d'un composant avec ses noms (interface) */
typedef struct _GNamedWidgetIface GNamedWidgetIface;


/* Détermine le type d'une interface pour les composants nommés. */
GType g_named_widget_get_type(void) G_GNUC_CONST;

/* Fournit le désignation associée à un composant nommé. */
char *g_named_widget_get_name(const GNamedWidget *, bool);

/* Fournit le composant associé à un composant nommé. */
GtkWidget *g_named_widget_get_widget(const GNamedWidget *);



#endif  /* _GLIBEXT_NAMED_H */
