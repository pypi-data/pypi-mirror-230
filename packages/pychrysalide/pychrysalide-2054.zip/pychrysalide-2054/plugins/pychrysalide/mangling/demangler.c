
/* Chrysalide - Outil d'analyse de fichiers binaires
 * demangler.c - équivalent Python du fichier "mangling/demangler.c"
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


#include "demangler.h"


#include <malloc.h>
#include <pygobject.h>


#include <mangling/demangler.h>


#include "../access.h"
#include "../helpers.h"



#define COMPILER_DEMANGLER_DOC                                  \
    "CompDemangler is an abstract class for demangling names."



/* Fournit la désignation interne du décodeur de désignations. */
static PyObject *py_compiler_demangler_get_key(PyObject *, void *);

/* Tente de décoder une chaîne de caractères donnée en type. */
static PyObject *py_compiler_demangler_decode_type(PyObject *, PyObject *);

/* Tente de décoder une chaîne de caractères donnée en routine. */
static PyObject *py_compiler_demangler_decode_routine(PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la désignation interne du décodeur de désignations.  *
*                                                                             *
*  Retour      : Simple chaîne de caractères.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_compiler_demangler_get_key(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    GCompDemangler *demangler;              /* Version GLib de l'opérande  */
    char *key;                              /* Désignation du décodeur     */

#define COMPILER_DEMANGLER_KEY_ATTRIB PYTHON_GET_DEF_FULL       \
(                                                               \
    key, py_compiler_demangler,                                 \
    "Provide the small name used to identify the demangler,"    \
    " as a code string."                                        \
)

    demangler = G_COMP_DEMANGLER(pygobject_get(self));
    assert(demangler != NULL);

    key = g_compiler_demangler_get_key(demangler);

    if (key != NULL)
    {
        result = PyUnicode_FromString(key);
        free(key);
    }
    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = décodeur à solliciter pour l'opération.               *
*                args = chaîne de caractères à décoder.                       *
*                                                                             *
*  Description : Tente de décoder une chaîne de caractères donnée en type.    *
*                                                                             *
*  Retour      : Instance obtenue ou None en cas d'échec.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_compiler_demangler_decode_type(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Désignation à retourner     */
    const char *desc;                       /* Description à traiter       */
    int ret;                                /* Bilan de lecture des args.  */
    GCompDemangler *demangler;              /* Décodeur mis en place       */
    GDataType *type;                        /* Type de données obtenu      */

#define COMPILER_DEMANGLER_DECODED_TYPE_METHOD PYTHON_METHOD_DEF        \
(                                                                       \
    decode_type, "$self, desc, /",                                      \
    METH_VARARGS, py_compiler_demangler,                                \
    "Demangle a type definition from its string mangled description.\n" \
    "\n"                                                                \
    "The result is an instance of type pychrysalide.analysis.DataType"  \
    " on success, None otherwise."                                      \
)

    ret = PyArg_ParseTuple(args, "s", &desc);
    if (!ret) return NULL;

    demangler = G_COMP_DEMANGLER(pygobject_get(self));

    type = g_compiler_demangler_decode_type(demangler, desc);

    if (type != NULL)
    {
        result = pygobject_new(G_OBJECT(type));
        Py_INCREF(result);

        g_object_unref(G_OBJECT(type));

    }
    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = décodeur à solliciter pour l'opération.               *
*                args = chaîne de caractères à décoder.                       *
*                                                                             *
*  Description : Tente de décoder une chaîne de caractères donnée en routine. *
*                                                                             *
*  Retour      : Instance obtenue ou None en cas d'échec.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_compiler_demangler_decode_routine(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Désignation à retourner     */
    const char *desc;                       /* Description à traiter       */
    int ret;                                /* Bilan de lecture des args.  */
    GCompDemangler *demangler;              /* Décodeur mis en place       */
    GBinRoutine *routine;                   /* Routine obtenue             */

#define COMPILER_DEMANGLER_DECODED_ROUTINE_METHOD PYTHON_METHOD_DEF         \
(                                                                           \
    decode_routine, "$self, desc, /",                                       \
    METH_VARARGS, py_compiler_demangler,                                    \
    "Demangle a routine definition from its string mangled description.\n"  \
    "\n"                                                                    \
    "The result is an instance of type pychrysalide.analysis.BinRoutine"    \
    " on success, None otherwise."                                          \
)

    ret = PyArg_ParseTuple(args, "s", &desc);
    if (!ret) return NULL;

    demangler = G_COMP_DEMANGLER(pygobject_get(self));

    routine = g_compiler_demangler_decode_routine(demangler, desc);

    if (routine != NULL)
    {
        result = pygobject_new(G_OBJECT(routine));
        Py_INCREF(result);

        g_object_unref(G_OBJECT(routine));

    }
    else
    {
        result = Py_None;
        Py_INCREF(result);
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

PyTypeObject *get_python_compiler_demangler_type(void)
{
    static PyMethodDef py_comp_demangler_methods[] = {
        COMPILER_DEMANGLER_DECODED_TYPE_METHOD,
        COMPILER_DEMANGLER_DECODED_ROUTINE_METHOD,
        { NULL }
    };

    static PyGetSetDef py_comp_demangler_getseters[] = {
        COMPILER_DEMANGLER_KEY_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_comp_demangler_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.mangling.CompDemangler",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = COMPILER_DEMANGLER_DOC,

        .tp_methods     = py_comp_demangler_methods,
        .tp_getset      = py_comp_demangler_getseters,

    };

    return &py_comp_demangler_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide....CompDemangler'.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_compiler_demangler_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'CompDemangler' */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_compiler_demangler_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.mangling");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_COMP_DEMANGLER, type))
            return false;

    }

    return true;

}
