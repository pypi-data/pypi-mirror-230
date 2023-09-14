
/* Chrysalide - Outil d'analyse de fichiers binaires
 * struct.c - conversion de structures C en équivalent Python
 *
 * Copyright (C) 2018-2019 Cyrille Bagard
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


#include "struct.h"


#include "access.h"
#include "helpers.h"



#define STRUCT_OBJ_DOC                                                      \
    "StructObject is a sugar glue used to transmit C structures to Python." \
    "\n"                                                                    \
    "For instance, let's consider the following C structure :\n"            \
    "\n"                                                                    \
    "    struct _my_struct_t { int a; int b } var;\n"                       \
    "\n"                                                                    \
    "Such a structure will be translated into a Python dictionary.\n"       \
    "\n"                                                                    \
    "Each previous field gets then accessible using :\n"                    \
    "* a direct access: *var.a*;\n"                                         \
    "* an access by name thanks to the dictionary: *var['b']*."


/* Objet à vocation abstraite */
typedef struct _PyStructObject
{
    PyDictObject base;                      /* A laisser en premier        */

} PyStructObject;


/* Assure l'encadrement des accès aux champs d'une structure. */
static PyObject *py_struct_getattr(PyObject *, char *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = structure C convertie en Python.                      *
*                name = nom du champ auquel un accès est demandé.             *
*                                                                             *
*  Description : Assure l'encadrement des accès aux champs d'une structure.   *
*                                                                             *
*  Retour      : Valeur du champ demandé.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_struct_getattr(PyObject *self, char *name)
{
    PyObject *result;                       /* Elément à retourner         */
    PyObject *w;                            /* Conversion du nom de champ  */
    PyTypeObject *tp;                       /* Type de l'objet manipulé    */

    result = PyDict_GetItemString(self, name);

    if (result != NULL)
        Py_INCREF(result);

    else
    {
        w = PyUnicode_InternFromString(name);
        if (w == NULL) return NULL;

        tp = Py_TYPE(self);

        if (tp->tp_base->tp_getattro != NULL)
            result = tp->tp_base->tp_getattro(self, w);

        Py_DECREF(w);

    }

    return result;

}


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

PyTypeObject *get_python_py_struct_type(void)
{
    static PyMethodDef py_struct_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_struct_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_struct_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.StructObject",
        .tp_basicsize   = sizeof(PyStructObject),

        .tp_getattr     = py_struct_getattr,

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = STRUCT_OBJ_DOC,

        .tp_methods     = py_struct_methods,
        .tp_getset      = py_struct_getseters,
        .tp_base        = &PyDict_Type,

    };

    return &py_struct_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.StructObject'.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_py_struct_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'StructObject'  */
    PyObject *module;                       /* Module à recompléter        */

    type = get_python_py_struct_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide");

        if (PyType_Ready(type) != 0)
            return false;

        if (!register_python_module_object(module, type))
            return false;

    }

    return true;

}
