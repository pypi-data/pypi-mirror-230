
/* Chrysalide - Outil d'analyse de fichiers binaires
 * panel-int.h - prototypes pour les définitions internes liées aux panneaux d'affichage
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
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#ifndef _GUI_PANELS_PANEL_INT_H
#define _GUI_PANELS_PANEL_INT_H


#include "panel.h"


#include <gtk/gtk.h>


#include "item-int.h"
#include "../glibext/delayed.h"



/* ------------------------- COEUR DES PANNEAUX D'AFFICHAGE ------------------------- */


/* Fournit une indication sur la personnalité du panneau. */
typedef PanelItemPersonality (* get_panel_personality_fc) (const GPanelItemClass *);

/* Fournit une indication d'accroche du panneau au démarrage. */
typedef bool (* dock_panel_at_startup_fc) (const GPanelItemClass *);

/* Détermine si un panneau peut être filtré. */
typedef bool (* can_search_panel_fc) (const GPanelItemClass *);

/* Indique le chemin initial de la localisation d'un panneau. */
typedef char * (* get_panel_path_fc) (const GPanelItemClass *);

/* Indique la définition d'un éventuel raccourci clavier. */
typedef char * (* get_panel_bindings_fc) (const GPanelItemClass *);

/* Place un panneau dans l'ensemble affiché. */
typedef void (* ack_dock_process_fc) (GPanelItem *);

/* Supprime un panneau de l'ensemble affiché. */
typedef void (* ack_undock_process_fc) (GPanelItem *);

/* Démarre l'actualisation du filtrage du contenu. */
typedef void (* update_filtered_fc) (GPanelItem *);


/* Elément réactif pour panneaux de l'éditeur (instance) */
struct _GPanelItem
{
    GEditorItem parent;                     /* A laisser en premier        */

    bool docked;                            /* Panneau inscrusté ?         */

    GNamedWidget *widget;                   /* Composant avec noms         */
    GtkWidget *cached_widget;               /* Composant GTK récupéré      */

    char *filter;                           /* Eventuel filtre textuel     */

    cairo_surface_t *surface;               /* Copie d'écran préalable     */
    gdouble hadj_value;                     /* Sauvegarde de défilement #1 */
    gdouble vadj_value;                     /* Sauvegarde de défilement #2 */
    gint switched;                          /* Mémorise l'état de bascule  */

};

/* Elément réactif pour panneaux de l'éditeur (classe) */
struct _GPanelItemClass
{
    GEditorItemClass parent;                /* A laisser en premier        */

    get_panel_personality_fc get_personality; /* Fourniture de nature      */
    dock_panel_at_startup_fc dock_at_startup; /* Recommandation d'accroche */
    can_search_panel_fc can_search;         /* Contenu fouillable ?        */
    get_panel_path_fc get_path;             /* Chemin vers la place idéale */
    get_panel_bindings_fc get_bindings;     /* Raccourci clavier éventuel  */

    ack_dock_process_fc ack_dock;           /* Prise en compte d'accroche  */
    ack_undock_process_fc ack_undock;       /* Prise en compte de décroche */

    update_filtered_fc update_filtered;     /* Lancement du filtrage       */

    wgroup_id_t gid;                        /* Groupe de travail dédié     */

    /* Signaux */

    void (* dock_request) (GPanelItem);
    void (* undock_request) (GPanelItem);

};


/* Fournit une indication sur la personnalité du panneau. */
PanelItemPersonality gtk_panel_item_class_get_personality_singleton(const GPanelItemClass *);

/* Renvoie false lors d'une consultation de la classe. */
bool gtk_panel_item_class_return_false(const GPanelItemClass *);

/* Renvoie true lors d'une consultation de la classe. */
bool gtk_panel_item_class_return_true(const GPanelItemClass *);



/* ---------------------- MECANISMES DE MISE A JOUR DE PANNEAU ---------------------- */


/* Obtient le groupe de travail dédié à une mise à jour. */
wgroup_id_t g_panel_item_get_group(const GPanelItem *);

/* Bascule l'affichage d'un panneau avant sa mise à jour. */
void g_panel_item_switch_to_updating_mask(GPanelItem *);

/* Bascule l'affichage d'un panneau après sa mise à jour. */
void g_panel_item_switch_to_updated_content(GPanelItem *);



#endif  /* _GUI_PANELS_PANEL_INT_H */
