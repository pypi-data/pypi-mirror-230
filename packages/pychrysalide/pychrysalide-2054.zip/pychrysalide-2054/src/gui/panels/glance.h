
/* Chrysalide - Outil d'analyse de fichiers binaires
 * glance.h - prototypes pour le panneau d'aperçu rapide
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


#ifndef _PANEL_GLANCE_H
#define _PANEL_GLANCE_H


#include <i18n.h>


#include "../panel.h"



#define PANEL_GLANCE_ID "glance"


#define G_TYPE_GLANCE_PANEL               g_glance_panel_get_type()
#define G_GLANCE_PANEL(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), g_glance_panel_get_type(), GGlancePanel))
#define G_IS_GLANCE_PANEL(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_glance_panel_get_type()))
#define G_GLANCE_PANEL_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_GLANCE_PANEL, GGlancePanelClass))
#define G_IS_GLANCE_PANEL_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_GLANCE_PANEL))
#define G_GLANCE_PANEL_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_GLANCE_PANEL, GGlancePanelClass))


/* Panneau d'aperçu rapide (instance) */
typedef struct _GGlancePanel GGlancePanel;

/* Panneau d'aperçu rapide (classe) */
typedef struct _GGlancePanelClass GGlancePanelClass;



/* Indique le type défini pour un panneau d'aperçu rapide. */
GType g_glance_panel_get_type(void);

/* Crée un panneau d'aperçu rapide. */
GPanelItem *g_glance_panel_new(void);



#endif  /* _PANEL_GLANCE_H */
