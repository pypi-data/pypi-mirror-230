
/* Chrysalide - Outil d'analyse de fichiers binaires
 * instruction.c - équivalent Python du fichier "arch/arm/v7/instruction.c"
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


#include "instruction.h"


#include <pygobject.h>


#include <plugins/pychrysalide/helpers.h>


#include "../instruction.h"
#include "../../v7/instruction.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Fournit un accès à une définition de type à diffuser.        *
*                                                                             *
*  Retour      : Définition d'objet pour Python.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyTypeObject *get_python_armv7_instruction_type(void)
{
    static PyMethodDef py_armv7_instruction_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_armv7_instruction_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_armv7_instruction_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.arch.arm.v7.ArmV7Instruction",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = "PyChrysalide instruction for an ARMv7 architecture.",

        .tp_methods     = py_armv7_instruction_methods,
        .tp_getset      = py_armv7_instruction_getseters,

    };

    return &py_armv7_instruction_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.....ArmV7Instruction'. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool register_python_armv7_instruction(PyObject *module)
{
    PyTypeObject *type;                     /* Type 'ArmV7Instruction'     */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_armv7_instruction_type();

    dict = PyModule_GetDict(module);

    /* TODO : ensure get_python_arm_instruction_type() */

    if (!register_class_for_pygobject(dict, G_TYPE_ARMV7_INSTRUCTION, type))
        return false;

    return true;

}
