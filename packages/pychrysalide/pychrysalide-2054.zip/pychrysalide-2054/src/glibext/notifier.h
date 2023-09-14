
/* Chrysalide - Outil d'analyse de fichiers binaires
 * notifier.h - prototypes pour les opérations de comparaison d'objets
 *
 * Copyright (C) 2022 Cyrille Bagard
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _GLIBEXT_NOTIFIER_H
#define _GLIBEXT_NOTIFIER_H








#ifdef INCLUDE_GTK_SUPPORT
#   include "../gtkext/gtkstatusstack.h"
#else






typedef void GtkStatusStack;



/* -------------------------- STATUT DES SUIVIS D'ACTIVITE -------------------------- */


/* Identifiant unique de rapport de progression */
typedef unsigned long activity_id_t;

/* Identifiant particulier pour une absence d'identifiant */
#define NO_ACTIVITY_ID 0


#define gtk_status_stack_update_current_location(a0, a1, a2, a3, a4)
#define gtk_status_stack_reset_current_location(a0)

#define gtk_status_stack_add_activity(a0, a1, a2) 0
#define gtk_status_stack_extend_activity(a0, a1, a2)
#define gtk_status_stack_update_activity(a0, a1, a2)
#define gtk_status_stack_update_activity_value(a0, a1, a2)
#define gtk_status_stack_remove_activity(a0, a1)



#endif





#endif  /* _GLIBEXT_NOTIFIER_H */
