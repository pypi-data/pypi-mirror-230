
/* Chrysalide - Outil d'analyse de fichiers binaires
 * module.c - intégration du répertoire arch en tant que module
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


#include <arch/archbase.h>
#include <common/endianness.h>


#include "context.h"
#include "instriter.h"
#include "instruction.h"
#include "operand.h"
#include "processor.h"
#include "register.h"
#include "vmpa.h"
#include "instructions/module.h"
#include "operands/module.h"
#include "../helpers.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : super = module dont la définition est à compléter.           *
*                                                                             *
*  Description : Ajoute le module 'arch' à un module Python.                  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool add_arch_module(PyObject *super)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Sous-module mis en place    */

    static PyModuleDef py_chrysalide_arch_module = {

        .m_base = PyModuleDef_HEAD_INIT,

        .m_name = "pychrysalide.arch",
        .m_doc = "Python module for Chrysalide.arch",

        .m_size = -1,

    };

    module = build_python_module(super, &py_chrysalide_arch_module);

    result = (module != NULL);

    if (result) result = add_arch_instructions_module(module);
    if (result) result = add_arch_operands_module(module);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Intègre les objets du module 'arch'.                         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool populate_arch_module(void)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    if (result) result = ensure_python_proc_context_is_registered();
    if (result) result = ensure_python_instr_iterator_is_registered();
    if (result) result = ensure_python_arch_instruction_is_registered();
    if (result) result = ensure_python_arch_operand_is_registered();
    if (result) result = ensure_python_arch_processor_is_registered();
    if (result) result = ensure_python_arch_register_is_registered();
    if (result) result = ensure_python_vmpa_is_registered();
    if (result) result = ensure_python_mrange_is_registered();

    if (result) result = populate_arch_instructions_module();
    if (result) result = populate_arch_operands_module();

    assert(result);

    return result;

}
