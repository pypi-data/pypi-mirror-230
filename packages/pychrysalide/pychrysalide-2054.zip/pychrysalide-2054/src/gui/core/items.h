
/* Chrysalide - Outil d'analyse de fichiers binaires
 * items.h - prototypes pour la manipulation de l'ensemble des composants graphiques actifs
 *
 * Copyright (C) 2017-2018 Cyrille Bagard
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
 *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _GUI_CORE_ITEMS_H
#define _GUI_CORE_ITEMS_H


#include "../item.h"
#include "../../analysis/loaded.h"
#include "../../glibext/gloadedpanel.h"



/* Procède à l'enregistrement d'un élément reactif de l'éditeur. */
void register_editor_item(GEditorItem *);

/* Retrouve un élément reactif de l'éditeur par son type. */
GEditorItem *find_editor_item_by_type(GType);

/* Retire un des éléments reactifs de l'éditeur. */
void unregister_editor_item(GEditorItem *);

/* Lance une actualisation du fait d'un changement de contenu. */
void change_editor_items_current_content(GLoadedContent *);

/* Lance une actualisation du fait d'un changement de vue. */
void change_editor_items_current_view(GLoadedPanel *);

/* Lance une actualisation du fait d'un changement de contenu. */
void update_editor_items_current_view(GLoadedPanel *);

/* Concentre l'attention de l'ensemble sur une adresse donnée. */
void focus_cursor_in_editor_items(GLoadedContent *, const GLineCursor *, GEditorItem *);

/* Lance une actualisation relative à l'étendue du projet. */
void update_project_area(GStudyProject *);



#endif  /* _GUI_CORE_ITEMS_H */
