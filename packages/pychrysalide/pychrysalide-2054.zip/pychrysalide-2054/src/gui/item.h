
/* Chrysalide - Outil d'analyse de fichiers binaires
 * item.h - prototypes pour la gestion des différents éléments réactifs de l'éditeurs
 *
 * Copyright (C) 2010-2020 Cyrille Bagard
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


#ifndef _GUI_ITEM_H
#define _GUI_ITEM_H


#include <glib-object.h>
#include <gtk/gtk.h>


#include "../analysis/loaded.h"
#include "../analysis/project.h"
#include "../glibext/gloadedpanel.h"



#define G_TYPE_EDITOR_ITEM            g_editor_item_get_type()
#define G_EDITOR_ITEM(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), g_editor_item_get_type(), GEditorItem))
#define G_IS_EDITOR_ITEM(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_editor_item_get_type()))
#define G_EDITOR_ITEM_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), g_editor_item_get_type(), GEditorItemClass))
#define G_IS_EDITOR_ITEM_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), g_editor_item_get_type()))
#define G_EDITOR_ITEM_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), g_editor_item_get_type(), GEditorItemClass))


/* Elément réactif quelconque de l'éditeur (instance) */
typedef struct _GEditorItem GEditorItem;

/* Elément réactif quelconque de l'éditeur (classe) */
typedef struct _GEditorItemClass GEditorItemClass;


/* Indique le type défini pour un élément réactif d'éditeur. */
GType g_editor_item_get_type(void);

/* Fournit le nom interne attribué à l'élément réactif. */
char *g_editor_item_class_get_key(const GEditorItemClass *);

/* Fournit le composant GTK associé à l'élément réactif. */
GtkWidget *g_editor_item_get_widget(const GEditorItem *);

/* Réagit à un changement de contenu chargé en cours d'analyse. */
void g_editor_item_change_content(GEditorItem *, GLoadedContent *, GLoadedContent *);

/* Réagit à un changement de vue du contenu en cours d'analyse. */
void g_editor_item_change_view(GEditorItem *, GLoadedPanel *, GLoadedPanel *);

/* Réagit à une modification de la vue du contenu analysé. */
void g_editor_item_update_view(GEditorItem *, GLoadedPanel *);

/* Réagit à une modification de la vue du contenu analysé. */
void g_editor_item_track_cursor(GEditorItem *, GLoadedPanel *, const GLineCursor *);

/* Réagit à une modification de la vue du contenu analysé. */
void g_editor_item_focus_cursor(GEditorItem *, GLoadedContent *, const GLineCursor *);

/* Lance une actualisation relative à l'étendue du projet. */
void g_editor_item_update_project_area(GEditorItem *, GStudyProject *);



#endif  /* _GUI_ITEM_H */
