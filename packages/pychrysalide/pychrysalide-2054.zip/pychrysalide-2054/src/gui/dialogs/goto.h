
/* Chrysalide - Outil d'analyse de fichiers binaires
 * goto.h - prototypes pour la boîte de dialogue pour les sauts à une adresse donnée
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


#ifndef _GUI_DIALOGS_GOTO_H
#define _GUI_DIALOGS_GOTO_H


#include <gtk/gtk.h>


#include "../../arch/vmpa.h"



/* Construit la fenêtre de saut à une adresse. */
GtkWidget *create_goto_dialog(GtkWindow *);

/* Fournit l'adresse obtenue par la saisie de l'utilisateur. */
vmpa2t *get_address_from_goto_dialog(GtkWidget *);



#endif  /* _GUI_DIALOGS_GOTO_H */
