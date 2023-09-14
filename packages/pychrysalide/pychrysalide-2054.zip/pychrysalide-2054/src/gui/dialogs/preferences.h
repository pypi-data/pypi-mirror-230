
/* Chrysalide - Outil d'analyse de fichiers binaires
 * preferences.h - prototypes pour la (re)définition de l'identité de l'utilisateur
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
 *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _GUI_DIALOGS_PREFERENCES_H
#define _GUI_DIALOGS_PREFERENCES_H


#include <gtk/gtk.h>



/* Propose une boîte de dialogue pour la configuration générale. */
GtkWidget *create_preferences_dialog(GtkWindow *, GtkBuilder **);



#endif  /* _GUI_DIALOGS_PREFERENCES_H */
