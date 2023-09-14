
/* Chrysalide - Outil d'analyse de fichiers contenus
 * global.h - prototypes pour la conservation de variables globales à vocation graphique
 *
 * Copyright (C) 2016-2018 Cyrille Bagard
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


#ifndef _GUI_CORE_GLOBAL_H
#define _GUI_CORE_GLOBAL_H


#include "../../analysis/loaded.h"
#include "../../glibext/gloadedpanel.h"
#include "../../gtkext/gtkstatusstack.h"
#include "../../gtkext/tiledgrid.h"



/* Note l'adresse du constructeur principal de l'éditeur. */
void set_editor_builder(GtkBuilder *);

/* Fournit l'adresse du constructeur principal de l'éditeur. */
GtkBuilder *get_editor_builder(void);

/* Fournit l'adresse de la fenêtre principale de l'éditeur. */
GtkWindow *get_editor_window(void);

/* Note l'adresse du composant d'affichage en tuiles. */
void set_tiled_grid(GtkTiledGrid *);

/* Fournit l'adresse du composant d'affichage en tuiles. */
GtkTiledGrid *get_tiled_grid(void);

/* Note l'adresse de la barre de statut principale. */
void set_global_status(GtkStatusStack *);

/* Fournit l'adresse de la barre de statut principale. */
GtkStatusStack *get_global_status(void);

/* Définit le contenu actif en cours d'étude. */
void set_current_content(GLoadedContent *);

/* Fournit le contenu actif en cours d'étude. */
GLoadedContent *get_current_content(void);

/* Définit l'affichage de contenu courant. */
void set_current_view(GLoadedPanel *);

/* Fournit l'affichage de contenu courant. */
GLoadedPanel *get_current_view(void);



#endif  /* _GUI_CORE_GLOBAL_H */
