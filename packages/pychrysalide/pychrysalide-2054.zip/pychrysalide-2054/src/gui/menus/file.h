
/* Chrysalide - Outil d'analyse de fichiers binaires
 * file.h - prototypes pour la gestion du menu 'Fichier'
 *
 * Copyright (C) 2011-2018 Cyrille Bagard
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


#ifndef _GUI_MENUS_FILE_H
#define _GUI_MENUS_FILE_H


#include <gtk/gtk.h>



/* Complète la définition du menu "Fichier". */
void setup_menu_file_callbacks(GtkBuilder *);

/* Réagit au menu "Fichier -> Enregistrer le projet". */
void mcb_file_save_project(GtkMenuItem *, gpointer);



#endif  /* _GUI_MENUS_FILE_H */
