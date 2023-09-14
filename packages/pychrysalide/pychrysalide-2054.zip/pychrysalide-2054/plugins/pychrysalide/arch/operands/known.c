
/* Chrysalide - Outil d'analyse de fichiers binaires
 * known.c - équivalent Python du fichier "arch/operands/known.h"
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


#include "known.h"


#include <assert.h>
#include <pygobject.h>


#include <arch/operands/known.h>


#include "immediate.h"
#include "rename.h"
#include "../../access.h"
#include "../../helpers.h"



/* Crée un nouvel objet Python de type 'KnownImmOperand'. */
static PyObject *py_known_imm_operand_new(PyTypeObject *, PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de l'objet à instancier.                         *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Crée un nouvel objet Python de type 'KnownImmOperand'.       *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_known_imm_operand_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Instance à retourner        */
    GImmOperand *imm;                       /* Opérande à remplacer        */
    const char *alt;                        /* Impression alternative      */
    int ret;                                /* Bilan de lecture des args.  */
    GArchOperand *operand;                  /* Création GLib à transmettre */

#define KNOWN_IMM_OPERAND_DOC                                               \
    "The KnownImmOperand provides replacement of"                           \
    " pychrysalide.arch.operands.ImmOperand instances by an alternative"    \
    " text.\n"                                                              \
    "\n"                                                                    \
    "Instances can be created using the following constructor:\n"           \
    "\n"                                                                    \
    "    KnownImmOperand(imm, alt)"                                         \
    "\n"                                                                    \
    "Where imm is an operand of type pychrysalide.arch.operands.ImmOperand" \
    " and alt is a string providing the text to be rendered at object"      \
    " display."

    ret = PyArg_ParseTuple(args, "O&s", convert_to_imm_operand, &imm, &alt);
    if (!ret) return NULL;

    operand = g_known_imm_operand_new(imm, alt);

    result = pygobject_new(G_OBJECT(operand));

    g_object_unref(operand);

    return (PyObject *)result;

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

PyTypeObject *get_python_known_imm_operand_type(void)
{
    static PyMethodDef py_known_imm_operand_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_known_imm_operand_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_known_imm_operand_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.arch.operands.KnownImmOperand",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = KNOWN_IMM_OPERAND_DOC,

        .tp_methods     = py_known_imm_operand_methods,
        .tp_getset      = py_known_imm_operand_getseters,
        .tp_new         = py_known_imm_operand_new

    };

    return &py_known_imm_operand_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.arch.KnownImmOperand'. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_known_imm_operand_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'ImmOperand'    */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_known_imm_operand_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.arch.operands");

        dict = PyModule_GetDict(module);

        if (!ensure_python_imm_operand_is_registered())
            return false;

        if (!ensure_python_renamed_operand_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_KNOWN_IMM_OPERAND, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en remplaçant d'opérande d'immédiat.      *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_known_imm_operand(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_known_imm_operand_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to known immediate operand");
            break;

        case 1:
            *((GKnownImmOperand **)dst) = G_KNOWN_IMM_OPERAND(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
