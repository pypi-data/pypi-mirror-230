
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gloadedpanel.h - prototypes pour l'affichage de contenus chargés
 *
 * Copyright (C) 2017-2018 Cyrille Bagard
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


#ifndef _GLIBEXT_LOADEDPANEL_H
#define _GLIBEXT_LOADEDPANEL_H


#include <glib-object.h>
#include <stdbool.h>
#include <gtk/gtk.h>


#include "glinecursor.h"
#include "../analysis/loaded.h"



#define G_TYPE_LOADED_PANEL             (g_loaded_panel_get_type())
#define G_LOADED_PANEL(obj)             (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_LOADED_PANEL, GLoadedPanel))
#define G_LOADED_PANEL_CLASS(vtable)    (G_TYPE_CHECK_CLASS_CAST((vtable), G_TYPE_LOADED_PANEL, GLoadedPanelIface))
#define G_IS_LOADED_PANEL(obj)          (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_LOADED_PANEL))
#define G_IS_LOADED_PANEL_CLASS(vtable) (G_TYPE_CHECK_CLASS_TYPE((vtable), G_TYPE_LOADED_PANEL))
#define G_LOADED_PANEL_GET_IFACE(inst)  (G_TYPE_INSTANCE_GET_INTERFACE((inst), G_TYPE_LOADED_PANEL, GLoadedPanelIface))


/* Composant d'affichage basique (coquille vide) */
typedef struct _GLoadedPanel GLoadedPanel;

/* Composant d'affichage basique (interface) */
typedef struct _GLoadedPanelIface GLoadedPanelIface;


/* Détermine le type d'une interface pour la mise en place de lignes. */
GType g_loaded_panel_get_type(void) G_GNUC_CONST;

/* Définit le contenu associé à un panneau de chargement. */
void g_loaded_panel_set_content(GLoadedPanel *, GLoadedContent *);

/* Fournit le contenu associé à un panneau de chargement. */
GLoadedContent *g_loaded_panel_get_content(const GLoadedPanel *);

/* Fournit le position courante dans un panneau de chargement. */
GLineCursor *g_loaded_panel_get_cursor(const GLoadedPanel *);

/* Demande à qui veut répondre un déplacement du curseur. */
void g_loaded_panel_request_move(GLoadedPanel *, const GLineCursor *, gboolean);

/* Adaptation d'une position sur une surface */
typedef enum _ScrollPositionTweak
{
    SPT_RAW,                                /* Aucun ajustement            */
    SPT_TOP,                                /* Le plus haut possible       */
    SPT_CENTER,                             /* Au centre de la surface     */
    SPT_BOTTOM                              /* Le plus bas possible        */

} ScrollPositionTweak;

#define IS_VALID_STP(t) (SPT_RAW <= (t) && (t) <= SPT_BOTTOM)

/* S'assure qu'un emplacement donné est visible à l'écran. */
void g_loaded_panel_scroll_to_cursor(GLoadedPanel *, const GLineCursor *, ScrollPositionTweak, bool);

/* Place en cache un rendu destiné à l'aperçu graphique rapide. */
void g_loaded_panel_cache_glance(GLoadedPanel *, cairo_t *, const GtkAllocation *, double);



#endif  /* _GLIBEXT_LOADEDPANEL_H */
