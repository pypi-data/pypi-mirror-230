
/* Chrysalide - Outil d'analyse de fichiers binaires
 * bookmarks.h - prototypes pour le panneau d'affichage des signets d'un binaire
 *
 * Copyright (C) 2014-2019 Cyrille Bagard
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


#ifndef _GUI_PANELS_BOOKMARKS_H
#define _GUI_PANELS_BOOKMARKS_H


#include <i18n.h>


#include "../panel.h"



#define PANEL_BOOKMARKS_ID "bookmarks"


#define G_TYPE_BOOKMARKS_PANEL               g_bookmarks_panel_get_type()
#define G_BOOKMARKS_PANEL(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), g_bookmarks_panel_get_type(), GBookmarksPanel))
#define G_IS_BOOKMARKS_PANEL(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_bookmarks_panel_get_type()))
#define G_BOOKMARKS_PANEL_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_BOOKMARKS_PANEL, GBookmarksPanelClass))
#define G_IS_BOOKMARKS_PANEL_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_BOOKMARKS_PANEL))
#define G_BOOKMARKS_PANEL_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_BOOKMARKS_PANEL, GBookmarksPanelClass))


/* Panneau d'affichage des signets liés à un binaire (instance) */
typedef struct _GBookmarksPanel GBookmarksPanel;

/* Panneau d'affichage des signets liés à un binaire (classe) */
typedef struct _GBookmarksPanelClass GBookmarksPanelClass;


/* Indique le type défini pour un panneau d'affichage des signets liés à un binaire. */
GType g_bookmarks_panel_get_type(void);

/* Crée un panneau d'affichage des paramètres de configuration. */
GPanelItem *g_bookmarks_panel_new(void);



#endif  /* _GUI_PANELS_BOOKMARKS_H */
