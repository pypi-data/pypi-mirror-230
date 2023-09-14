
/* Chrysalide - Outil d'analyse de fichiers binaires
 * log.h - prototypes pour le panneau d'affichage des messages système
 *
 * Copyright (C) 2012-2019 Cyrille Bagard
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


#ifndef _GUI_PANELS_LOG_H
#define _GUI_PANELS_LOG_H


#include <i18n.h>


#include "../panel.h"
#include "../../core/logs.h"



#define PANEL_LOG_ID "log"


#define G_TYPE_LOG_PANEL               g_log_panel_get_type()
#define G_LOG_PANEL(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), g_log_panel_get_type(), GLogPanel))
#define G_IS_LOG_PANEL(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_log_panel_get_type()))
#define G_LOG_PANEL_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_LOG_PANEL, GLogPanelClass))
#define G_IS_LOG_PANEL_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_LOG_PANEL))
#define G_LOG_PANEL_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_LOG_PANEL, GLogPanelClass))


/* Panneau d'affichage de messages (instance) */
typedef struct _GLogPanel GLogPanel;

/* Panneau d'affichage de messages (classe) */
typedef struct _GLogPanelClass GLogPanelClass;



/* Indique le type défini pour un panneau d'affichage de messages. */
GType g_log_panel_get_type(void);

/* Crée un panneau d'affichage des messages système. */
GPanelItem *g_log_panel_new(void);

/* Affiche un message dans le journal des messages système. */
void g_log_panel_add_message(GLogPanel *, LogMessageType, const char *);



#endif  /* _GUI_PANELS_LOG_H */
