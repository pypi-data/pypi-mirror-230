
/* Chrysalide - Outil d'analyse de fichiers binaires
 * options.h - prototypes pour la gestion du menu 'Options'
 *
 * Copyright (C) 2019 Cyrille Bagard
 *
 *  This binary is part of Chrysalide.
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


#ifndef _GUI_MENUS_OPTIONS_H
#define _GUI_MENUS_OPTIONS_H


#include <gtk/gtk.h>



/* Complète la définition du menu "Options". */
void setup_menu_options_callbacks(GtkBuilder *);



#endif  /* _GUI_MENUS_OPTIONS_H */
