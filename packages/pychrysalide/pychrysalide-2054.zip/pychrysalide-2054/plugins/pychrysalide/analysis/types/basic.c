
/* Chrysalide - Outil d'analyse de fichiers binaires
 * basic.c - équivalent Python du fichier "analysis/types/basic.c"
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


#include "basic.h"


#include <pygobject.h>


#include <i18n.h>
#include <analysis/types/basic.h>


#include "constants.h"
#include "../type.h"
#include "../../access.h"
#include "../../helpers.h"



/* Crée un nouvel objet Python de type 'BasicType'. */
static PyObject *py_basic_type_new(PyTypeObject *, PyObject *, PyObject *);

/* Fournit le type de base géré par le type. */
static PyObject *py_basic_type_get_base(PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de l'objet à instancier.                         *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Crée un nouvel objet Python de type 'BasicType'.             *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_basic_type_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Instance à retourner        */
    BaseType base;                          /* Type de base à créer        */
    int ret;                                /* Bilan de lecture des args.  */
    GDataType *dtype;                       /* Version GLib du type        */

#define BASIC_TYPE_DOC                                                          \
    "The BasicType class handles all the primary types of data, such as"        \
    " integers, characters or floating numbers.\n"                              \
    "\n"                                                                        \
    "Instances can be created using the following constructor:\n"               \
    "\n"                                                                        \
    "    BasicType(base)"                                               \
    "\n"                                                                        \
    "Where *base* is one of the pychrysalide.analysis.types.BasicType.BaseType" \
    " values, except *BaseType.INVALID*."

    ret = PyArg_ParseTuple(args, "O&", convert_to_basic_type_base_type, &base);
    if (!ret) return NULL;

    if (base >= BTP_INVALID)
    {
        PyErr_SetString(PyExc_TypeError, _("Bad basic type."));
        return NULL;
    }

    dtype = g_basic_type_new(base);
    result = pygobject_new(G_OBJECT(dtype));
    g_object_unref(dtype);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le type de base géré par le type.                    *
*                                                                             *
*  Retour      : Type basique.                                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_basic_type_get_base(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GBasicType *type;                       /* Version GLib du type        */
    BaseType base;                          /* Type de base à renvoyer     */

#define BASIC_TYPE_BASE_ATTRIB PYTHON_GET_DEF_FULL              \
(                                                               \
    base, py_basic_type,                                        \
    "Provide the internal identifier of the basic type.\n"      \
    "\n"                                                        \
    "This property provides a"                                  \
    " pychrysalide.analysis.types.BasicType.BaseType value."    \
)

    type = G_BASIC_TYPE(pygobject_get(self));

    base = g_basic_type_get_base(type);

    result = cast_with_constants_group_from_type(get_python_basic_type_type(), "BaseType", base);

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

PyTypeObject *get_python_basic_type_type(void)
{
    static PyMethodDef py_basic_type_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_basic_type_getseters[] = {
        BASIC_TYPE_BASE_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_basic_type_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.types.BasicType",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = BASIC_TYPE_DOC,

        .tp_methods     = py_basic_type_methods,
        .tp_getset      = py_basic_type_getseters,
        .tp_new         = py_basic_type_new

    };

    return &py_basic_type_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.....types.BasicType'.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_basic_type_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'BasicType'     */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_basic_type_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.types");

        dict = PyModule_GetDict(module);

        if (!ensure_python_data_type_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_BASIC_TYPE, type))
            return false;

        if (!define_basic_type_constants(type))
            return false;

    }

    return true;

}
