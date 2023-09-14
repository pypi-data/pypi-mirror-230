
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


#ifndef _DIALOGS_GOTOX_H
#define _DIALOGS_GOTOX_H


#include <gtk/gtk.h>



/* Crée et affiche un assistant de sélection de gadgets ROP. */
void run_rop_finder_assistant(GtkWindow *);



#endif  /* _DIALOGS_GOTOX_H */
