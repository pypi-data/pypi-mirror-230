
/* Chrysalide - Outil d'analyse de fichiers binaires
 * project.h - prototypes pour la gestion du menu 'Projet'
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
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#ifndef _GUI_MENUS_PROJECT_H
#define _GUI_MENUS_PROJECT_H


#include <gtk/gtk.h>


#include "../../analysis/project.h"



/* Complète la définition du menu "Projet". */
void setup_menu_project_callbacks(GtkBuilder *);

/* Lance une actualisation relative à l'étendue du projet. */
void update_menu_project_for_project(GtkBuilder *, GStudyProject *);



#endif  /* _GUI_MENUS_PROJECT_H */
