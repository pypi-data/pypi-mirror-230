
/* Chrysalide - Outil d'analyse de fichiers binaires
 * theme.h - prototypes pour la gestion d'un thème pour l'interface grahique
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


#ifndef _GUI_THEME_H
#define _GUI_THEME_H


#include <stdbool.h>
#include <gtk/gtk.h>



#define G_TYPE_EDITOR_THEME            g_editor_theme_get_type()
#define G_EDITOR_THEME(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_EDITOR_THEME, GEditorTheme))
#define G_IS_EDITOR_THEME(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_EDITOR_THEME))
#define G_EDITOR_THEME_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_EDITOR_THEME, GEditorThemeClass))
#define G_IS_EDITOR_THEME_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_EDITOR_THEME))
#define G_EDITOR_THEME_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_EDITOR_THEME, GEditorThemeClass))


/* Thème graphique pour l'éditeur (instance) */
typedef struct _GEditorTheme GEditorTheme;

/* Thème graphique pour l'éditeur (classe) */
typedef struct _GEditorThemeClass GEditorThemeClass;


/* Indique le type défini pour un theme de l'interface graphique. */
GType g_editor_theme_get_type(void);

/* Charge les éléments associés à un thème graphique. */
GEditorTheme *g_editor_theme_new(const char *, bool);

/* Indique le nom d'un thème donné. */
const char *g_editor_theme_get_name(const GEditorTheme *);

/* Active un thème graphique particulier. */
void g_editor_theme_load(GEditorTheme *, GdkScreen *, gboolean);



#endif  /* _GUI_THEME_H */
