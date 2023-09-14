
/* Chrysalide - Outil d'analyse de fichiers binaires
 * proto.c - équivalent Python du fichier "analysis/types/proto.c"
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


#include "proto.h"


#include <pygobject.h>


#include <i18n.h>
#include <analysis/types/proto.h>


#include "../type.h"
#include "../../access.h"
#include "../../helpers.h"



/* Crée un nouvel objet Python de type 'ProtoType'. */
static PyObject *py_proto_type_new(PyTypeObject *, PyObject *, PyObject *);

/* Ajoute un argument à un prototype. */
static PyObject *py_proto_type_add_arg(PyObject *, PyObject *);

/* Fournit le type de retour d'un prototype. */
static PyObject *py_proto_type_get_return_type(PyObject *, void *);

/* Définit le type de retour d'un prototype. */
static int py_proto_type_set_return_type(PyObject *, PyObject *, void *);

/* Fournit les arguments du prototype. */
static PyObject *py_proto_type_get_args(PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de l'objet à instancier.                         *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Crée un nouvel objet Python de type 'ProtoType'.             *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_proto_type_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Instance à retourner        */
    GDataType *dtype;                       /* Version GLib du type        */

#define PROTO_TYPE_DOC                                                      \
    "The ProtoType class defines an empty prototype of function.\n"         \
    "\n"                                                                    \
    "Instances can be created using the following constructor:\n"           \
    "\n"                                                                    \
    "    ProtoType()"                                                       \
    "\n"                                                                    \
    "The arguments and return types have then to be filled in the created"  \
    " prototype with the relevant methods or properties."

    dtype = g_proto_type_new();
    result = pygobject_new(G_OBJECT(dtype));
    g_object_unref(dtype);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = projet d'étude à manipuler.                           *
*                args = arguments accompagnant l'appel.                       *
*                                                                             *
*  Description : Ajoute un argument à un prototype.                           *
*                                                                             *
*  Retour      : Py_None.                                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_proto_type_add_arg(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Absence de retour Python    */
    GDataType *arg;                         /* Version GLib du type        */
    int ret;                                /* Bilan de lecture des args.  */
    GProtoType *type;                       /* Version GLib du type        */

#define PROTO_TYPE_ADD_PARAM_METHOD PYTHON_METHOD_DEF                   \
(                                                                       \
    add_arg, "$self, arg, /",                                           \
    METH_VARARGS, py_proto_type,                                        \
    "Add an extra argument to the prototype.\n"                         \
    "\n"                                                                \
    "This extra argument has to be a pychrysalide.analysis.DataType"    \
    " instance."                                                        \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_data_type, &arg);
    if (!ret) return NULL;

    type = G_PROTO_TYPE(pygobject_get(self));

    g_proto_type_add_arg(type, arg);

    result = Py_None;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le type de retour d'un prototype.                    *
*                                                                             *
*  Retour      : Indication sur le type de retour en place.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_proto_type_get_return_type(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GProtoType *type;                       /* Version GLib du type        */
    GDataType *ret;                         /* Type de retour du prototype */

#define PROTO_TYPE_RETURN_TYPE_ATTRIB PYTHON_GETSET_DEF_FULL            \
(                                                                       \
    return_type, py_proto_type,                                         \
    "Type of the prototype return value.\n"                             \
    "\n"                                                                \
    "This type is a pychrysalide.analysis.DataType instance,"           \
    " or None if no return type has been defined for the prototype."    \
)

    type = G_PROTO_TYPE(pygobject_get(self));

    ret = g_proto_type_get_return_type(type);

    if (ret == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }
    else
    {
        result = pygobject_new(G_OBJECT(ret));
        g_object_unref(ret);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Définit le type de retour d'un prototype.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_proto_type_set_return_type(PyObject *self, PyObject *value, void *closure)
{
    GProtoType *type;                       /* Version GLib du type        */
    GDataType *ret;                         /* Type de retour du prototype */

    if (!PyObject_IsInstance(value, (PyObject *)get_python_data_type_type()))
    {
        PyErr_SetString(PyExc_TypeError, _("The attribute value must be a GDataType."));
        return -1;
    }

    type = G_PROTO_TYPE(pygobject_get(self));

    ret = G_DATA_TYPE(pygobject_get(value));

    g_proto_type_set_return_type(type, ret);

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit les arguments du prototype.                          *
*                                                                             *
*  Retour      : Liste de types d'arguments.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_proto_type_get_args(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GProtoType *type;                       /* Version GLib du type        */
    size_t count;                           /* Nombre d'arguments          */
    size_t i;                               /* Boucle de parcours          */
    GDataType *arg;                         /* Argument du prototype       */

#define PROTO_TYPE_ARGS_ATTRIB PYTHON_GET_DEF_FULL                      \
(                                                                       \
    args, py_proto_type,                                                \
    "List of all arguments for the prototype.\n"                        \
    "\n"                                                                \
    "The returned value is a tuple of pychrysalide.analysis.DataType"   \
    " instances."                                                       \
)

    type = G_PROTO_TYPE(pygobject_get(self));

    count = g_proto_type_count_args(type);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
        arg = g_proto_type_get_arg(type, i);

        PyTuple_SetItem(result, i, pygobject_new(G_OBJECT(arg)));

        g_object_unref(arg);

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

PyTypeObject *get_python_proto_type_type(void)
{
    static PyMethodDef py_proto_type_methods[] = {
        PROTO_TYPE_ADD_PARAM_METHOD,
        { NULL }
    };

    static PyGetSetDef py_proto_type_getseters[] = {
        PROTO_TYPE_RETURN_TYPE_ATTRIB,
        PROTO_TYPE_ARGS_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_proto_type_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.types.ProtoType",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = PROTO_TYPE_DOC,

        .tp_methods     = py_proto_type_methods,
        .tp_getset      = py_proto_type_getseters,
        .tp_new         = py_proto_type_new

    };

    return &py_proto_type_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.....types.ProtoType'.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_proto_type_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'ProtoType'     */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_proto_type_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.types");

        dict = PyModule_GetDict(module);

        if (!ensure_python_data_type_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_PROTO_TYPE, type))
            return false;

    }

    return true;

}
