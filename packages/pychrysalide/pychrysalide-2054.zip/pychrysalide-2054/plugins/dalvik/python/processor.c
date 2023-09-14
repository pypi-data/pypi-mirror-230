
/* Chrysalide - Outil d'analyse de fichiers binaires
 * processor.c - équivalent Python du fichier "arch/dalvik/processor.c"
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


#include "processor.h"


#include <pygobject.h>


#include <plugins/pychrysalide/helpers.h>
#include <plugins/pychrysalide/arch/processor.h>


#include "../processor.h"



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

PyTypeObject *get_python_dalvik_processor_type(void)
{
    static PyMethodDef py_dalvik_processor_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_dalvik_processor_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_dalvik_processor_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.arch.dalvik.DalvikProcessor",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = "PyChrysalide processor for an Dalvik architecture.",

        .tp_methods     = py_dalvik_processor_methods,
        .tp_getset      = py_dalvik_processor_getseters,

    };

    return &py_dalvik_processor_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.....DalvikProcessor'.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool register_python_dalvik_processor(PyObject *module)
{
    PyTypeObject *type;                     /* Type Python '...Processor'   */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_dalvik_processor_type();

    dict = PyModule_GetDict(module);

    if (!ensure_python_arch_processor_is_registered())
        return false;

    if (!register_class_for_pygobject(dict, G_TYPE_DALVIK_PROCESSOR, type))
        return false;

    return true;

}
