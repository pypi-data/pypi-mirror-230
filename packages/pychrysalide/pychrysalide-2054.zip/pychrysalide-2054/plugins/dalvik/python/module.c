
/* Chrysalide - Outil d'analyse de fichiers binaires
 * module.c - intégration du répertoire dalvik en tant que module
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


#include "module.h"


#include <Python.h>


#include <plugins/pychrysalide/access.h>
#include <plugins/pychrysalide/helpers.h>


#include "instruction.h"
#include "processor.h"
#include "v35/module.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Ajoute le module 'dalvik' au module Python.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool add_arch_dalvik_module_to_python_module(void)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *super;                        /* Module à compléter          */
    PyObject *module;                       /* Sous-module mis en place    */

    static PyModuleDef py_chrysalide_dalvik_module = {

        .m_base = PyModuleDef_HEAD_INIT,

        .m_name = "pychrysalide.arch.dalvik",
        .m_doc = "Python module for Chrysalide.arch.dalvik",

        .m_size = -1,

    };

    result = false;

    super = get_access_to_python_module("pychrysalide.arch");

    module = build_python_module(super, &py_chrysalide_dalvik_module);

    result = (module != NULL);

    if (result) result = register_python_dalvik_instruction(module);
    if (result) result = register_python_dalvik_processor(module);

    if (result) result = add_arch_dalvik_v35_module_to_python_module(module);

    assert(result);

    return result;

}
