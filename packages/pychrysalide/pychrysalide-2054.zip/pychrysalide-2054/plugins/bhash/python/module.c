
/* Chrysalide - Outil d'analyse de fichiers binaires
 * module.c - intégration du répertoire bhash en tant que module
 *
 * Copyright (C) 2020 Cyrille Bagard
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


#include "imphash.h"
#include "tlsh.h"
#include "rich.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Ajoute le module 'plugins.bhash' au module Python.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool add_bhash_module_to_python_module(void)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *super;                        /* Module à compléter          */
    PyObject *module;                       /* Sous-module mis en place    */

#define PYCHRYSALIDE_PLUGINS_BHASH_DOC                           \
    "bhash is a module providing several kinds of hashes for binary files."

    static PyModuleDef py_chrysalide_bhash_module = {

        .m_base = PyModuleDef_HEAD_INIT,

        .m_name = "pychrysalide.plugins.bhash",
        .m_doc = PYCHRYSALIDE_PLUGINS_BHASH_DOC,

        .m_size = -1,

    };

    result = false;

    super = get_access_to_python_module("pychrysalide.plugins");

    module = build_python_module(super, &py_chrysalide_bhash_module);

    result = (module != NULL);

    if (result) result = populate_bhash_module_with_imphash(module);
    if (result) result = populate_bhash_module_with_tlsh(module);
    if (result) result = populate_bhash_module_with_rich_header(module);

    assert(result);

    return result;

}
