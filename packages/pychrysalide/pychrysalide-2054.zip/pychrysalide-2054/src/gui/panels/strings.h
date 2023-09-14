
/* Chrysalide - Outil d'analyse de fichiers binaires
 * strings.h - prototypes pour le panneau d'affichage des chaînes de caractères
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


#ifndef _GUI_PANELS_STRINGS_H
#define _GUI_PANELS_STRINGS_H


#include <i18n.h>


#include "../panel.h"



#define PANEL_STRINGS_ID "strings"


#define G_TYPE_STRINGS_PANEL               g_strings_panel_get_type()
#define G_STRINGS_PANEL(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), g_strings_panel_get_type(), GStringsPanel))
#define G_IS_STRINGS_PANEL(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_strings_panel_get_type()))
#define G_STRINGS_PANEL_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_STRINGS_PANEL, GStringsPanelClass))
#define G_IS_STRINGS_PANEL_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_STRINGS_PANEL))
#define G_STRINGS_PANEL_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_STRINGS_PANEL, GStringsPanelClass))


/* Panneau d'affichage des chaînes (instance) */
typedef struct _GStringsPanel GStringsPanel;

/* Panneau d'affichage des chaînes (classe) */
typedef struct _GStringsPanelClass GStringsPanelClass;


/* Indique le type défini pour un panneau d'affichage des chaînes. */
GType g_strings_panel_get_type(void);

/* Crée un panneau d'affichage des chaînes. */
GPanelItem *g_strings_panel_new(void);



#endif  /* _GUI_PANELS_STRINGS_H */
