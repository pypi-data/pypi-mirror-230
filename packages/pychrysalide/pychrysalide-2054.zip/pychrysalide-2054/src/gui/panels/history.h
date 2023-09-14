
/* Chrysalide - Outil d'analyse de fichiers binaires
 * history.h - prototypes pour le panneau de la liste des évolutions d'utilisateur(s)
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
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#ifndef _GUI_PANELS_HISTORY_H
#define _GUI_PANELS_HISTORY_H


#include <i18n.h>


#include "../panel.h"



#define PANEL_HISTORY_ID "history"


#define G_TYPE_HISTORY_PANEL               g_history_panel_get_type()
#define G_HISTORY_PANEL(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), g_history_panel_get_type(), GHistoryPanel))
#define G_IS_HISTORY_PANEL(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_history_panel_get_type()))
#define G_HISTORY_PANEL_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_HISTORY_PANEL, GHistoryPanelClass))
#define G_IS_HISTORY_PANEL_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_HISTORY_PANEL))
#define G_HISTORY_PANEL_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_HISTORY_PANEL, GHistoryPanelClass))


/* Panneau de la liste des évolutions utilisateur(s) (instance) */
typedef struct _GHistoryPanel GHistoryPanel;

/* Panneau de la liste des évolutions utilisateur(s) (classe) */
typedef struct _GHistoryPanelClass GHistoryPanelClass;


/* Indique le type défini pour un panneau d'affichage des symboles. */
GType g_history_panel_get_type(void);

/* Crée un panneau d'affichage des symboles. */
GPanelItem *g_history_panel_new(void);



#endif  /* _GUI_PANELS_HISTORY_H */
