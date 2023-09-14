
/* Chrysalide - Outil d'analyse de fichiers binaires
 * tiledgrid.h - prototypes pour un composant d'affichage avec des chemins vers les composants contenus
 *
 * Copyright (C) 2018-2019 Cyrille Bagard
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


#ifndef _GTKEXT_TILEDGRID_H
#define _GTKEXT_TILEDGRID_H


#include <gtk/gtk.h>


#include "gtkdockstation.h"
#include "../glibext/configuration.h"
#include "../gui/panel.h"



/* --------------------------- INTERFACE DU COMPOSANT GTK --------------------------- */


#define GTK_TYPE_TILED_GRID            gtk_tiled_grid_get_type()
#define GTK_TILED_GRID(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), GTK_TYPE_TILED_GRID, GtkTiledGrid))
#define GTK_IS_TILED_GRID(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), GTK_TYPE_TILED_GRID))
#define GTK_TILED_GRID_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), GTK_TYPE_TILED_GRID, GtkTiledGridClass))
#define GTK_IS_TILED_GRID_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), GTK_TYPE_TILED_GRID))
#define GTK_TILED_GRID_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), GTK_TYPE_TILED_GRID, GtkTiledGridClass))



/* Conteneur pour un affichage en tuiles nommées (instance) */
typedef struct _GtkTiledGrid GtkTiledGrid;

/* Conteneur pour un affichage en tuiles nommées (classe) */
typedef struct _GtkTiledGridClass GtkTiledGridClass;


/* Détermine le type du conteneur d'affichage en tuiles nommées. */
GType gtk_tiled_grid_get_type(void);

/* Crée une nouvelle instance de conteneur avec tuiles. */
GtkWidget *gtk_tiled_grid_new(void);

/* Donne le panneau fourni par défaut pour la zone principale. */
GPanelItem *gtk_tiled_grid_get_default_main_panel(const GtkTiledGrid *);

/* Fournit le panneau par défaut pour la zone principale. */
void gtk_tiled_grid_set_default_main_panel(GtkTiledGrid *, GPanelItem *);

/* Incorpore un nouveau panneau dans le conteneur en tuiles. */
void gtk_tiled_grid_add(GtkTiledGrid *, GPanelItem *);

/* Retire un panneau dans le conteneur en tuiles. */
void gtk_tiled_grid_remove(GtkTiledGrid *, GPanelItem *);

/* Indique le chemin correspondant à une station intégrée. */
char *gtk_tiled_grid_get_path_for_station(const GtkTiledGrid *, GtkDockStation *);

/* Replace les positions des séparateurs de tuiles. */
void gtk_tiled_grid_restore_positions(const GtkTiledGrid *, GGenConfig *);

/* Sauvegarde les positions des séparateurs de tuiles. */
void gtk_tiled_grid_save_positions(const GtkTiledGrid *, GGenConfig *);



#endif  /* _GTKEXT_TILEDGRID_H */
