
/* Chrysalide - Outil d'analyse de fichiers binaires
 * module.c - intégration du répertoire winordinals en tant que module
 *
 * Copyright (C) 2021 Cyrille Bagard
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
#include <Python.h>


#include <plugins/pychrysalide/access.h>
#include <plugins/pychrysalide/helpers.h>



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Ajoute le module 'plugins.winordinals' au module Python.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool add_winordinals_module_to_python_module(void)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *super;                        /* Module à compléter          */
    PyObject *module;                       /* Sous-module mis en place    */

#define PYCHRYSALIDE_PLUGINS_WINORDINALS_DOC                        \
    "winordinals is a module providing the value of known ordinals" \
    " for some DLL files."

    static PyModuleDef py_chrysalide_winordinals_module = {

        .m_base = PyModuleDef_HEAD_INIT,

        .m_name = "pychrysalide.plugins.winordinals",
        .m_doc = PYCHRYSALIDE_PLUGINS_WINORDINALS_DOC,

        .m_size = -1,

    };

    result = false;

    super = get_access_to_python_module("pychrysalide.plugins");

    module = build_python_module(super, &py_chrysalide_winordinals_module);

    result = (module != NULL);

    assert(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Intègre les objets du module 'plugins.winordinals'.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool populate_winordinals_module(void)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Module à recompléter        */

    result = true;

    module = get_access_to_python_module("pychrysalide.plugins.winordinals");

    //if (result) result = register_python_winordinals_node(module);

    assert(result);

    return result;

}
