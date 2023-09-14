
/* Chrysalide - Outil d'analyse de fichiers binaires
 * module.c - intégration du répertoire gui en tant que module
 *
 * Copyright (C) 2018-2020 Cyrille Bagard
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


#include "module.h"


#include <assert.h>


#include "item.h"
#include "menubar.h"
#include "panel.h"
#include "core/module.h"
#include "panels/module.h"
#include "../helpers.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : super = module dont la définition est à compléter.           *
*                                                                             *
*  Description : Ajoute le module 'gui' à un module Python.                   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool add_gui_module(PyObject *super)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Sous-module mis en place    */

#define PYCHRYSALIDE_GUI_DOC                                                \
    "This module contains all the items useful for dealing with the GUI"    \
    " of Chrysalide."

    static PyModuleDef py_chrysalide_gui_module = {

        .m_base = PyModuleDef_HEAD_INIT,

        .m_name = "pychrysalide.gui",
        .m_doc  = PYCHRYSALIDE_GUI_DOC,

        .m_size = -1,

    };

    module = build_python_module(super, &py_chrysalide_gui_module);

    result = (module != NULL);

    if (result) result = add_gui_core_module(module);
    if (result) result = add_gui_panels_module(module);

    if (!result)
        Py_XDECREF(module);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Intègre les objets du module 'gui'.                          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool populate_gui_module(void)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    if (result) result = ensure_python_editor_item_is_registered();
    if (result) result = ensure_python_menu_bar_is_registered();
    if (result) result = ensure_python_panel_item_is_registered();

    if (result) result = populate_gui_core_module();
    if (result) result = populate_gui_panels_module();

    assert(result);

    return result;

}
