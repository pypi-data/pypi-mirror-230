
/* Chrysalide - Outil d'analyse de fichiers binaires
 * module.c - intégration du répertoire operands en tant que module
 *
 * Copyright (C) 2019-2020 Cyrille Bagard
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


#include "feeder.h"
#include "immediate.h"
#include "known.h"
#include "proxy.h"
#include "register.h"
#include "rename.h"
#include "target.h"
#include "targetable.h"
#include "../../helpers.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : super = module dont la définition est à compléter.           *
*                                                                             *
*  Description : Ajoute le module 'arch.operands' à un module Python.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool add_arch_operands_module(PyObject *super)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Sous-module mis en place    */

#define PYCHRYSALIDE_ARCH_OPERANDS_DOC                                          \
    "This module contains implementations for most common operand usages.\n"    \
    "\n"                                                                        \
    "These operands are usually added to objects such as"                       \
    " pychrysalide.arch.ArchInstruction when disassembling a binary."

    static PyModuleDef py_chrysalide_arch_operands_module = {

        .m_base = PyModuleDef_HEAD_INIT,

        .m_name = "pychrysalide.arch.operands",
        .m_doc = PYCHRYSALIDE_ARCH_OPERANDS_DOC,

        .m_size = -1,

    };

    module = build_python_module(super, &py_chrysalide_arch_operands_module);

    result = (module != NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Intègre les objets du module 'arch.operands'.                *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool populate_arch_operands_module(void)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    if (result) result = ensure_python_proxy_feeder_is_registered();
    if (result) result = ensure_python_imm_operand_is_registered();
    if (result) result = ensure_python_known_imm_operand_is_registered();
    if (result) result = ensure_python_proxy_operand_is_registered();
    if (result) result = ensure_python_register_operand_is_registered();
    if (result) result = ensure_python_renamed_operand_is_registered();
    if (result) result = ensure_python_renameable_operand_is_registered();
    if (result) result = ensure_python_target_operand_is_registered();
    if (result) result = ensure_python_targetable_operand_is_registered();

    assert(result);

    return result;

}
