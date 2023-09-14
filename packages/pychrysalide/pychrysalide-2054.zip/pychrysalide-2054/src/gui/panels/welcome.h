
/* Chrysalide - Outil d'analyse de fichiers binaires
 * welcome.h - prototypes pour le panneau d'accueil par défaut
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


#ifndef _GUI_PANELS_WELCOME_H
#define _GUI_PANELS_WELCOME_H


#include <i18n.h>


#include "../panel.h"



#define PANEL_WELCOME_ID "welcome"


#define G_TYPE_WELCOME_PANEL               g_welcome_panel_get_type()
#define G_WELCOME_PANEL(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), g_welcome_panel_get_type(), GWelcomePanel))
#define G_IS_WELCOME_PANEL(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_welcome_panel_get_type()))
#define G_WELCOME_PANEL_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_WELCOME_PANEL, GWelcomePanelClass))
#define G_IS_WELCOME_PANEL_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_WELCOME_PANEL))
#define G_WELCOME_PANEL_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_WELCOME_PANEL, GWelcomePanelClass))


/* Panneau d'accueil par défaut (instance) */
typedef struct _GWelcomePanel GWelcomePanel;

/* Panneau d'accueil par défaut (classe) */
typedef struct _GWelcomePanelClass GWelcomePanelClass;


/* Indique le type défini pour un panneau d'accueil. */
GType g_welcome_panel_get_type(void);

/* Crée un panneau d'accueil par défaut. */
GPanelItem *g_welcome_panel_new(void);

/* Indique l'origine de l'affichage du panneau d'accueil. */
bool g_welcome_panel_get_user_origin(const GWelcomePanel *);

/* Détermine l'origine de l'affichage du panneau d'accueil. */
void g_welcome_panel_set_user_origin(GWelcomePanel *, bool);



#endif  /* _GUI_PANELS_WELCOME_H */
