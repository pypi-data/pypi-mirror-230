
/* Chrysalide - Outil d'analyse de fichiers binaires
 * menubar.h - prototypes pour la gestion des différents menus de la fenêtre principale
 *
 * Copyright (C) 2011-2018 Cyrille Bagard
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


#ifndef _GUI_MENUBAR_H
#define _GUI_MENUBAR_H


#include "item.h"



#define G_TYPE_MENU_BAR               g_menu_bar_get_type()
#define G_MENU_BAR(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), g_menu_bar_get_type(), GMenuBar))
#define G_IS_MENU_BAR(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_menu_bar_get_type()))
#define G_MENU_BAR_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_MENU_BAR, GMenuBarClass))
#define G_IS_MENU_BAR_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_MENU_BAR))
#define G_MENU_BAR_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_MENU_BAR, GMenuBarClass))


/* Barre de menus de la fenêtre principale (instance) */
typedef struct _GMenuBar GMenuBar;

/* Barre de menus de la fenêtre principale (classe) */
typedef struct _GMenuBarClass GMenuBarClass;


/* Indique le type défini pour la barre de menus de la fenêtre principale. */
GType g_menu_bar_get_type(void);

/* Compose la barre de menus principale. */
GEditorItem *g_menu_bar_new(GtkBuilder *);

/* Fournit le constructeur associé à la barre de menus. */
GtkBuilder *g_menu_bar_get_builder(const GMenuBar *);



#endif  /* _GUI_MENUBAR_H */
