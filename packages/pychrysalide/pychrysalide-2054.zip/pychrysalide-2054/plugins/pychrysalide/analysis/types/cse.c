
/* Chrysalide - Outil d'analyse de fichiers binaires
 * cse.c - équivalent Python du fichier "analysis/types/cse.c"
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#include "cse.h"


#include <pygobject.h>


#include <i18n.h>
#include <analysis/types/cse.h>


#include "constants.h"
#include "../type.h"
#include "../../access.h"
#include "../../helpers.h"



/* Crée un nouvel objet Python de type 'ClassEnumType'. */
static PyObject *py_class_enum_type_new(PyTypeObject *, PyObject *, PyObject *);

/* Fournit le type pris en compte géré par le type. */
static PyObject *py_class_enum_type_get_kind(PyObject *, void *);

/* Donne la désignation de la classe / structure / énumération. */
static PyObject *py_class_enum_type_get_name(PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de l'objet à instancier.                         *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Crée un nouvel objet Python de type 'ClassEnumType'.         *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_class_enum_type_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Instance à retourner        */
    ClassEnumKind kind;                     /* Type de base à créer        */
    const char *name;                       /* Désignation humaine         */
    int ret;                                /* Bilan de lecture des args.  */
    GDataType *dtype;                       /* Version GLib du type        */

#define CLASS_ENUM_TYPE_DOC                                                 \
    "The ClassEnumType class handles types embedding other types, such as"  \
    " classes, structures or enumerations.\n"                               \
    "\n"                                                                    \
    "Instances can be created using the following constructor:\n"           \
    "\n"                                                                    \
    "    ClassEnumType(kind, name=None)"                                    \
    "\n"                                                                    \
    "Where *kind* is one of the"                                            \
    " pychrysalide.analysis.types.ClassEnumType.ClassEnumKind values,"      \
    " except *ClassEnumKind.COUNT*, and *name* is an optional string."

    name = NULL;

    ret = PyArg_ParseTuple(args, "O&|s", convert_to_class_enum_type_class_enum_kind, &kind, &name);
    if (!ret) return NULL;

    if (kind >= CEK_COUNT)
    {
        PyErr_SetString(PyExc_TypeError, _("Bad class/enum kind."));
        return NULL;
    }

    dtype = g_class_enum_type_new(kind, name != NULL ? strdup(name) : NULL);
    result = pygobject_new(G_OBJECT(dtype));
    g_object_unref(dtype);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le type pris en compte géré par le type.             *
*                                                                             *
*  Retour      : Type pris en compte.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_class_enum_type_get_kind(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GClassEnumType *type;                   /* Version GLib du type        */
    ClassEnumKind kind;                     /* Type de base à renvoyer     */

#define CLASS_ENUM_TYPE_KIND_ATTRIB PYTHON_GET_DEF_FULL                 \
(                                                                       \
    kind, py_class_enum_type,                                           \
    "Provide the internal identifier for the kind of the type.\n"       \
    "\n"                                                                \
    "This property provides a"                                          \
    " pychrysalide.analysis.types.ClassEnumType.ClassEnumKind value."   \
)

    type = G_CLASS_ENUM_TYPE(pygobject_get(self));

    kind = g_class_enum_type_get_kind(type);

    result = cast_with_constants_group_from_type(get_python_class_enum_type_type(), "ClassEnumKind", kind);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Donne la désignation de la classe / structure / énumération. *
*                                                                             *
*  Retour      : Chaîne de caractères.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_class_enum_type_get_name(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GClassEnumType *type;                   /* Version GLib du type        */
    const char *name;                       /* Désignation humaine         */

#define CLASS_ENUM_TYPE_NAME_ATTRIB PYTHON_GET_DEF_FULL                 \
(                                                                       \
    name, py_class_enum_type,                                           \
    "Provide the name registered for the type.\n"                       \
    "\n"                                                                \
    "This property provides a string or None if no value is defined."   \
)

    type = G_CLASS_ENUM_TYPE(pygobject_get(self));

    name = g_class_enum_type_get_name(type);

    if (name != NULL)
        result = PyUnicode_FromString(name);
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

PyTypeObject *get_python_class_enum_type_type(void)
{
    static PyMethodDef py_class_enum_type_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_class_enum_type_getseters[] = {
        CLASS_ENUM_TYPE_KIND_ATTRIB,
        CLASS_ENUM_TYPE_NAME_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_class_enum_type_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.types.ClassEnumType",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = CLASS_ENUM_TYPE_DOC,

        .tp_methods     = py_class_enum_type_methods,
        .tp_getset      = py_class_enum_type_getseters,
        .tp_new         = py_class_enum_type_new

    };

    return &py_class_enum_type_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.....ClassEnumType'.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_class_enum_type_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'ClassEnumType' */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_class_enum_type_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.types");

        dict = PyModule_GetDict(module);

        if (!ensure_python_data_type_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_CLASS_ENUM_TYPE, type))
            return false;

        if (!define_class_enum_type_constants(type))
            return false;

    }

    return true;

}
