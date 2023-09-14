
/* Chrysalide - Outil d'analyse de fichiers binaires
 * panel.h - prototypes pour la gestion des éléments réactifs spécifiques aux panneaux
 *
 * Copyright (C) 2019 Cyrille Bagard
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
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#ifndef _GUI_PANELS_PANEL_H
#define _GUI_PANELS_PANEL_H


#include <stdbool.h>
#include <gtk/gtk.h>


#include "../glibext/configuration.h"
#include "../glibext/named.h"



#define G_TYPE_PANEL_ITEM            g_panel_item_get_type()
#define G_PANEL_ITEM(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_PANEL_ITEM, GPanelItem))
#define G_IS_PANEL_ITEM(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_PANEL_ITEM))
#define G_PANEL_ITEM_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_PANEL_ITEM, GPanelItemClass))
#define G_IS_PANEL_ITEM_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_PANEL_ITEM))
#define G_PANEL_ITEM_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_PANEL_ITEM, GPanelItemClass))


/* Elément réactif pour panneaux de l'éditeur (instance) */
typedef struct _GPanelItem GPanelItem;

/* Elément réactif pour panneaux de l'éditeur (classe) */
typedef struct _GPanelItemClass GPanelItemClass;


/* Types de panneaux pour éditeur */
typedef enum _PanelItemPersonality
{
    PIP_INVALID,                            /* Information non initialisée */

    PIP_SINGLETON,                          /* Instance unique             */
    PIP_PERSISTENT_SINGLETON,               /* Instance unique permanente             */
    PIP_BINARY_VIEW,                        /* Affichage d'un binaire      */
    PIP_OTHER,                              /* Reste du monde              */

    PIP_COUNT

} PanelItemPersonality;


/* Indique le type défini pour un élément destiné à un panneau. */
GType g_panel_item_get_type(void);

/* Fournit une indication sur la personnalité du panneau. */
PanelItemPersonality gtk_panel_item_class_get_personality(const GPanelItemClass *);

/* Fournit une indication d'accroche du panneau au démarrage. */
bool gtk_panel_item_class_dock_at_startup(const GPanelItemClass *);

/* Détermine si un panneau peut être filtré. */
bool gtk_panel_item_class_can_search(const GPanelItemClass *);

/* Indique le chemin initial de la localisation d'un panneau. */
char *gtk_panel_item_class_get_path(const GPanelItemClass *);

/* Indique la définition d'un éventuel raccourci clavier. */
char *gtk_panel_item_class_get_key_bindings(const GPanelItemClass *);

/* Met en place les bases de la configuration du panneau. */
bool gtk_panel_item_class_setup_configuration(const GPanelItemClass *, GGenConfig *);

/* Crée un élément de panneau réactif. */
GPanelItem *g_panel_item_new(GType, const char *);

/* Indique le composant graphique principal du panneau. */
GNamedWidget *gtk_panel_item_get_named_widget(const GPanelItem *);

/* Définit le chemin d'accès à utiliser pour les encapsulations. */
void gtk_panel_item_set_path(GPanelItem *, const char *);

/* Place un panneau dans l'ensemble affiché. */
void g_panel_item_dock(GPanelItem *);

/* Définit si le composant repose sur un support de l'éditeur. */
void g_panel_item_set_dock_at_startup(GPanelItem *, bool);

/* Indique si le composant repose sur un support de l'éditeur. */
bool g_panel_item_is_docked(const GPanelItem *);

/* Supprime un panneau de l'ensemble affiché. */
void g_panel_item_undock(GPanelItem *);



#endif  /* _GUI_PANELS_PANEL_H */
