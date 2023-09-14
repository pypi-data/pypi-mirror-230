
/* Chrysalide - Outil d'analyse de fichiers binaires
 * bookmark.h - prototypes pour la boîte de dialogue pour les sauts à une adresse donnée
 *
 * Copyright (C) 2015-2018 Cyrille Bagard
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


#ifndef _GUI_DIALOGS_BOOKMARK_H
#define _GUI_DIALOGS_BOOKMARK_H


#include <gtk/gtk.h>


#include "../../arch/vmpa.h"
#include "../../analysis/db/item.h"



/* Construit la fenêtre de création de signet. */
GtkWidget *create_bookmark_dialog(GtkWindow *, GtkBuilder **);

/* Fournit le signet conçu via la saisie de l'utilisateur. */
GDbItem *get_item_from_bookmark_dialog(GtkBuilder *, const vmpa2t *);



#endif  /* _GUI_DIALOGS_BOOKMARK_H */
