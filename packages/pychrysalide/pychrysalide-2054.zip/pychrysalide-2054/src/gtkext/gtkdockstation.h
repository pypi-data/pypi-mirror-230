
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gtkdockstation.h - prototypes pour la manipulation et l'affichage de composants rassemblés
 *
 * Copyright (C) 2012-2018 Cyrille Bagard
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


#ifndef _GTKEXT_GTKDOCKSTATION_H
#define _GTKEXT_GTKDOCKSTATION_H


#include <gtk/gtk.h>


#include "gtkdockable.h"



//G_BEGIN_DECLS


#define GTK_TYPE_DOCK_STATION             (gtk_dock_station_get_type())
#define GTK_DOCK_STATION(obj)             G_TYPE_CHECK_INSTANCE_CAST(obj, gtk_dock_station_get_type (), GtkDockStation)
#define GTK_DOCK_STATION_CLASS(klass)     G_TYPE_CHECK_CLASS_CAST(klass, gtk_dock_station_get_type(), GtkDockStationClass)
#define GTK_IS_DOCK_STATION(obj)          G_TYPE_CHECK_INSTANCE_TYPE(obj, gtk_dock_station_get_type())


/* Station de réception pour concentration d'éléments (instance) */
typedef struct _GtkDockStation GtkDockStation;

/* Station de réception pour concentration d'éléments (classe) */
typedef struct _GtkDockStationClass GtkDockStationClass;


/* Station de réception pour concentration d'éléments (instance) */
struct _GtkDockStation
{
    GtkNotebook parent;                     /* A laisser en premier        */

};

/* Station de réception pour concentration d'éléments (classe) */
struct _GtkDockStationClass
{
    GtkNotebookClass parent_class;          /* A laisser en premier        */

    /* Signaux */

    void (* dock_widget) (GtkDockStation *, GtkWidget *);
    void (* undock_widget) (GtkDockStation *, GtkWidget *);

    void (* switch_widget) (GtkDockStation *, GtkWidget *);

    void (* menu_requested) (GtkDockStation *, GtkWidget *);
    void (* close_requested) (GtkDockStation *, GtkWidget *);

};


/* Détermine le type du composant d'affichage concentré. */
GType gtk_dock_station_get_type(void);

/* Crée un nouveau composant pour support d'affichage concentré. */
GtkWidget *gtk_dock_station_new(void);

/* Ajoute un paquet d'informations à l'affichage centralisé. */
void gtk_dock_station_add_dockable(GtkDockStation *, GtkDockable *);

/* Change le contenu de l'onglet courant uniquement. */
void gtk_dock_panel_change_active_widget(GtkDockStation *, GtkWidget *);

/* Retire un paquet d'informations de l'affichage centralisé. */
void gtk_dock_station_remove_dockable(GtkDockStation *, GtkDockable *);



//G_END_DECLS



#endif  /* _GTKEXT_GTKDOCKSTATION_H */
