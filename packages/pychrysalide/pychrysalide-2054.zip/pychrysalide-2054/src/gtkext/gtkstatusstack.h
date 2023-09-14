
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gtkstatusstack.h - prototypes pour un empilement d'informations de statut
 *
 * Copyright (C) 2015-2019 Cyrille Bagard
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


#ifndef _GTKEXT_GTKSTATUSSTACK_H
#define _GTKEXT_GTKSTATUSSTACK_H


#include <gtk/gtk.h>


#include "../arch/vmpa.h"



/* ------------------------- GESTION EXTERIEURE DE LA BARRE ------------------------- */


#define GTK_TYPE_STATUS_STACK            (gtk_status_stack_get_type())
#define GTK_STATUS_STACK(obj)            (G_TYPE_CHECK_INSTANCE_CAST(obj, GTK_TYPE_STATUS_STACK, GtkStatusStack))
#define GTK_STATUS_STACK_CLASS(klass)    (G_LOADED_BINARY_GET_CLASS(klass, GTK_TYPE_STATUS_STACK, GtkStatusStackClass))
#define GTK_IS_STATUS_STACK(obj)         (G_TYPE_CHECK_INSTANCE_TYPE(obj, GTK_TYPE_STATUS_STACK))
#define GTK_IS_STATUS_STACK_CLASS(obj)   (G_TYPE_CHECK_INSTANCE_TYPE(obj, GTK_TYPE_STATUS_STACK))
#define GTK_STATUS_STACK_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), GTK_TYPE_STATUS_STACK, GtkStatusStackClass))


/* Abstration d'une gestion de barre de statut (instance) */
typedef struct _GtkStatusStack GtkStatusStack;

/* Abstration d'une gestion de barre de statut (classe) */
typedef struct _GtkStatusStackClass GtkStatusStackClass;


/* Détermine le type de la barre de statut améliorée. */
GType gtk_status_stack_get_type(void);

/* Crée une nouvelle instance de barre de statut. */
GtkStatusStack *gtk_status_stack_new(void);



/* -------------------- STATUT DES INFORMATIONS DE DESASSEMBLAGE -------------------- */


/* Actualise les informations liées une position d'assemblage. */
void gtk_status_stack_update_current_location(GtkStatusStack *, const mrange_t *, const char *, const char *, const char *);

/* Réinitialise les informations associées une position. */
void gtk_status_stack_reset_current_location(GtkStatusStack *);



/* -------------------------- STATUT DES SUIVIS D'ACTIVITE -------------------------- */


/* Identifiant unique de rapport de progression */
typedef unsigned long activity_id_t;

/* Identifiant particulier pour une absence d'identifiant */
#define NO_ACTIVITY_ID 0


/* Démarre le suivi d'une nouvelle activité. */
activity_id_t gtk_status_stack_add_activity(GtkStatusStack *, const char *, unsigned long);

/* Etend la portée des travaux d'une nouvelle activité. */
void gtk_status_stack_extend_activity(GtkStatusStack *, activity_id_t, unsigned long);

/* Actualise les informations concernant une activité. */
void gtk_status_stack_update_activity(GtkStatusStack *, activity_id_t, const char *);

/* Actualise la progression d'une activité. */
void gtk_status_stack_update_activity_value(GtkStatusStack *, activity_id_t, unsigned long);

/* Met fin au suivi d'une activité donnée. */
void gtk_status_stack_remove_activity(GtkStatusStack *, activity_id_t);



#endif  /* _GTKEXT_GTKSTATUSSTACK_H */
