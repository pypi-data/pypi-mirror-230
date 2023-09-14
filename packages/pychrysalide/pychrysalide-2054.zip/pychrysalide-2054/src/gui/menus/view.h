
/* Chrysalide - Outil d'analyse de fichiers binaires
 * view.h - prototypes pour la gestion du menu 'Affichage'
 *
 * Copyright (C) 2012-2020 Cyrille Bagard
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


#ifndef _GUI_MENUS_VIEW_H
#define _GUI_MENUS_VIEW_H


#include <gtk/gtk.h>


#include "../menubar.h"
#include "../../glibext/gloadedpanel.h"



/* Complète la définition du menu "Affichage". */
void setup_menu_view_callbacks(GtkBuilder *);

/* Réagit avec le menu "Affichage -> Panneaux latéraux". */
void mcb_view_update_side_panels_list(GtkMenuItem *, GMenuBar *);

/* Réagit à un changement d'affichage principal de contenu. */
void rebuild_menu_view_for_content(GtkBuilder *, GLoadedContent *);

/* Lance une actualisation du fait d'un changement de support. */
void rebuild_menu_view_for_view(GtkBuilder *, GLoadedPanel *);

/* Met à jour les accès du menu "Affichage" selon le contenu. */
void update_access_for_view_in_menu_view(GtkBuilder *, GLoadedPanel *);



#endif  /* _GUI_MENUS_VIEW_H */
