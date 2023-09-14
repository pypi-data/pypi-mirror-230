
/* Chrysalide - Outil d'analyse de fichiers binaires
 * agroup.h - prototypes pour l'activation et la désactivation de tous les raccourcis clavier
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#ifndef _GUI_AGROUP_H
#define _GUI_AGROUP_H


#include <gtk/gtk.h>



/* Précise l'accès aux menus avec raccourcis. */
void setup_accel_group_callbacks(GtkBuilder *);

/* Ajoute un accélérateur à un composant graphique. */
void add_accelerator_to_widget(GtkBuilder *, GtkWidget *, const char *);

/* Prend note d'un changement de focus sur une zone de saisie. */
gboolean track_focus_change_in_text_area(GtkWidget *, GdkEventFocus *, gpointer);



#endif  /* _GUI_AGROUP_H */
