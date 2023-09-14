
/* Chrysalide - Outil d'analyse de fichiers binaires
 * item.h - prototypes pour l'équivalent Python du fichier "gui/item.h"
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#ifndef _PLUGINS_PYCHRYSALIDE_GUI_ITEM_H
#define _PLUGINS_PYCHRYSALIDE_GUI_ITEM_H


#include <Python.h>
#include <stdbool.h>


#include <gui/item.h>



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Initialise la classe des éléments pour l'interface graphique. */
void py_editor_item_init_gclass(GEditorItemClass *, gpointer);



/* -------------------------- FONCTIONNALITES D'UN ELEMENT -------------------------- */


/* Fournit un accès à une définition de type à diffuser. */
PyTypeObject *get_python_editor_item_type(void);

/* Prend en charge l'objet 'pychrysalide.gui.EditorItem'. */
bool ensure_python_editor_item_is_registered(void);



#endif  /* _PLUGINS_PYCHRYSALIDE_GUI_ITEM_H */
