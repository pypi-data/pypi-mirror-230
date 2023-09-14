
/* Chrysalide - Outil d'analyse de fichiers binaires
 * prefs_labels.h - prototypes pour les paramètres des étiquettes colorées
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


#ifndef _GUI_DIALOGS_PREFS_LABELS_H
#define _GUI_DIALOGS_PREFS_LABELS_H


#include <gtk/gtk.h>


#include "../../glibext/configuration.h"



/* Met en place un panneau de paramétrage d'étiquettes colorées. */
GtkWidget *create_labels_preferences(GtkBuilder **);

/* Charge la configuration des paramétrages pour étiquettes. */
void load_labels_configuration(GtkBuilder *, GGenConfig *);

/* Sauvegarde la configuration des paramétrages pour étiquettes. */
void store_labels_configuration(GtkBuilder *, GGenConfig *);



#endif  /* _GUI_DIALOGS_PREFS_LABELS_H */
