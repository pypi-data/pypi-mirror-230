
/* Chrysalide - Outil d'analyse de fichiers binaires
 * edition.h - prototypes pour la gestion du menu 'Edition'
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


#ifndef _GUI_MENUS_EDITION_H
#define _GUI_MENUS_EDITION_H


#include <gtk/gtk.h>


#include "../../glibext/gloadedpanel.h"



/* Complète la définition du menu "Edition". */
void setup_menu_edition_callbacks(GtkBuilder *);

/* Lance une actualisation du fait d'un changement de support. */
void update_access_for_view_in_menu_edition(GtkBuilder *, GLoadedPanel *);

/* Met à jour les accès du menu "Edition" selon une position. */
void update_access_for_cursor_in_menu_edition(GtkBuilder *, GLoadedPanel *, const GLineCursor *);



#endif  /* _GUI_MENUS_EDITION_H */
