
/* Chrysalide - Outil d'analyse de fichiers binaires
 * updating.h - prototypes pour la mise à jour des panneaux de l'interface
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
 *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _GUI_PANELS_UPDATING_H
#define _GUI_PANELS_UPDATING_H


#include <glib-object.h>
#include <stdbool.h>
#include <gtk/gtk.h>


#include "../../glibext/delayed.h"
#include "../../gtkext/gtkstatusstack.h"



/* ---------------------- MECANISMES DE MISE A JOUR DE PANNEAU ---------------------- */


#define G_TYPE_UPDATABLE_PANEL             (g_updatable_panel_get_type())
#define G_UPDATABLE_PANEL(obj)             (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_UPDATABLE_PANEL, GUpdatablePanel))
#define G_UPDATABLE_PANEL_CLASS(vtable)    (G_TYPE_CHECK_CLASS_CAST((vtable), G_TYPE_UPDATABLE_PANEL, GUpdatablePanelIface))
#define G_IS_UPDATABLE_PANEL(obj)          (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_UPDATABLE_PANEL))
#define G_IS_UPDATABLE_PANEL_CLASS(vtable) (G_TYPE_CHECK_CLASS_TYPE((vtable), G_TYPE_UPDATABLE_PANEL))
#define G_UPDATABLE_PANEL_GET_IFACE(inst)  (G_TYPE_INSTANCE_GET_INTERFACE((inst), G_TYPE_UPDATABLE_PANEL, GUpdatablePanelIface))


/* Mécanisme de mise à jour d'un panneau (coquille vide) */
typedef struct _GUpdatablePanel GUpdatablePanel;

/* Mécanisme de mise à jour d'un panneau (interface) */
typedef struct _GUpdatablePanelIface GUpdatablePanelIface;


/* Détermine le type d'une interface pour la mise à jour de panneau. */
GType g_updatable_panel_get_type(void) G_GNUC_CONST;

/* Prépare une opération de mise à jour de panneau. */
bool g_updatable_panel_setup(const GUpdatablePanel *, unsigned int, size_t *, void **, char **);

/* Obtient le groupe de travail dédié à une mise à jour. */
wgroup_id_t g_updatable_panel_get_group(const GUpdatablePanel *);

/* Bascule l'affichage d'un panneau avant mise à jour. */
void g_updatable_panel_introduce(const GUpdatablePanel *, unsigned int, void *);

/* Réalise une opération de mise à jour de panneau. */
void g_updatable_panel_process(const GUpdatablePanel *, unsigned int, GtkStatusStack *, activity_id_t, void *);

/* Bascule l'affichage d'un panneau après mise à jour. */
void g_updatable_panel_conclude(GUpdatablePanel *, unsigned int, void *);

/* Supprime les données dynamiques utilisées à la mise à jour. */
void g_updatable_panel_clean_data(const GUpdatablePanel *, unsigned int, void *);



/* ---------------------------- AIDE POUR LA MISE A JOUR ---------------------------- */


#define G_TYPE_PANEL_UPDATE            g_panel_update_get_type()
#define G_PANEL_UPDATE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_PANEL_UPDATE, GPanelUpdate))
#define G_IS_PANEL_UPDATE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_PANEL_UPDATE))
#define G_PANEL_UPDATE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_PANEL_UPDATE, GPanelUpdateClass))
#define G_IS_PANEL_UPDATE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_PANEL_UPDATE))
#define G_PANEL_UPDATE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_PANEL_UPDATE, GPanelUpdateClass))


/* Procédure de mise à jour de panneau graphique (instance) */
typedef struct _GPanelUpdate GPanelUpdate;

/* Procédure de mise à jour de panneau graphique (classe) */
typedef struct _GPanelUpdateClass GPanelUpdateClass;


/* Indique le type défini pour les tâches de mise à jour de panneau. */
GType g_panel_update_get_type(void);

/* Crée une tâche de mise à jour non bloquante. */
GPanelUpdate *g_panel_update_new(GUpdatablePanel *, unsigned int);



/* -------------------------- ENCAPSULATION DE HAUT NIVEAU -------------------------- */


/* Identifiants arbitraires pour distinguer les phases */
typedef enum _PanelUpdateID
{
    PUI_0,                                  /* Phase #0                    */
    PUI_1,                                  /* Phase #1                    */
    PUI_2,                                  /* Phase #2                    */
    PUI_3,                                  /* Phase #3                    */
    PUI_4                                   /* Phase #4                    */

} PanelUpdateID;


/* Prépare et lance l'actualisation d'un panneau. */
void run_panel_update(GUpdatablePanel *, unsigned int);



#endif  /* _GUI_PANELS_UPDATING_H */
