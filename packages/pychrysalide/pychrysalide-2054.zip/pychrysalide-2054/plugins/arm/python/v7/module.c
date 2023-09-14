
/* Chrysalide - Outil d'analyse de fichiers binaires
 * module.c - intégration du répertoire v7 en tant que module
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
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#include "module.h"


#include <plugins/pychrysalide/access.h>
#include <plugins/pychrysalide/helpers.h>


#include "instruction.h"
#include "processor.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Ajoute le module 'arm' au module Python.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool add_arch_arm_v7_module_to_python_module(PyObject *super)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Sous-module mis en place    */

    static PyModuleDef py_chrysalide_v7_module = {

        .m_base = PyModuleDef_HEAD_INIT,

        .m_name = "pychrysalide.arch.arm.v7",
        .m_doc = "Python module for Chrysalide.arch.arm.v7",

        .m_size = -1,

    };

    module = build_python_module(super, &py_chrysalide_v7_module);

    result = (module != NULL);

    if (result) result = register_python_armv7_instruction(module);
    if (result) result = register_python_armv7_processor(module);

    assert(result);

    return result;

}
