
/* Chrysalide - Outil d'analyse de fichiers binaires
 * view.h - prototypes pour le panneau d'affichage de contenu binaire
 *
 * Copyright (C) 2020 Cyrille Bagard
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


#ifndef _GUI_PANELS_VIEW_H
#define _GUI_PANELS_VIEW_H


#include "../panel.h"



#define PANEL_VIEW_ID "binview"


#define G_TYPE_VIEW_PANEL               g_view_panel_get_type()
#define G_VIEW_PANEL(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), g_view_panel_get_type(), GViewPanel))
#define G_IS_VIEW_PANEL(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_view_panel_get_type()))
#define G_VIEW_PANEL_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_VIEW_PANEL, GViewPanelClass))
#define G_IS_VIEW_PANEL_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_VIEW_PANEL))
#define G_VIEW_PANEL_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_VIEW_PANEL, GViewPanelClass))


/* Panneau d'affichage pour contenu binaire (instance) */
typedef struct _GViewPanel GViewPanel;

/* Panneau d'affichage pour contenu binaire (classe) */
typedef struct _GViewPanelClass GViewPanelClass;


/* Indique le type défini pour un panneau de contenu binaire. */
GType g_view_panel_get_type(void);

/*  Crée un panneau pour l'affichage d'un contenu binaire. */
GPanelItem *g_view_panel_new(GNamedWidget *);



#endif  /* _GUI_PANELS_VIEW_H */
