
/* Chrysalide - Outil d'analyse de fichiers binaires
 * loading.h - prototypes pour la fenêtre de chargement de nouveaux contenus
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


#ifndef _GUI_DIALOGS_LOADING_H
#define _GUI_DIALOGS_LOADING_H


#include <gtk/gtk.h>


#include "../../analysis/loaded.h"
#include "../../analysis/project.h"



/* Construit une boîte de dialogue dédiée aux chargements. */
GtkWidget *create_loading_dialog(GtkWindow *, GtkBuilder **);

/* Ajoute un binaire à la liste à charger. */
void add_content_to_loading_dialog(GtkBuilder *, GLoadedContent *, GStudyProject *);



#endif  /* _GUI_DIALOGS_LOADING_H */
