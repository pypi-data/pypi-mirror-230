
/* Chrysalide - Outil d'analyse de fichiers binaires
 * weak.h - prototypes pour la définition de symboles qui n'ont pas leur place dans la version autonome
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


#ifndef _PLUGINS_PYCHRYSALIDE_WEAK_H
#define _PLUGINS_PYCHRYSALIDE_WEAK_H


#include <glibext/notifier.h>


#if 0
/* Démarre le suivi d'une nouvelle activité. */
activity_id_t gtk_status_stack_add_activity(GtkStatusStack *, const char *, unsigned long) __attribute__((weak));

/* Etend la portée des travaux d'une nouvelle activité. */
void gtk_status_stack_extend_activity(GtkStatusStack *, activity_id_t, unsigned long) __attribute__((weak));

/* Actualise les informations concernant une activité. */
void gtk_status_stack_update_activity(GtkStatusStack *, activity_id_t, const char *) __attribute__((weak));

/* Actualise la progression d'une activité. */
void gtk_status_stack_update_activity_value(GtkStatusStack *, activity_id_t, unsigned long) __attribute__((weak));

/* Met fin au suivi d'une activité donnée. */
void gtk_status_stack_remove_activity(GtkStatusStack *, activity_id_t) __attribute__((weak));
#endif


#endif  /* _PLUGINS_PYCHRYSALIDE_WEAK_H */
