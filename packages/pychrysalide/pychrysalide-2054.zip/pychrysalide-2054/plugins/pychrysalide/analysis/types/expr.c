
/* Chrysalide - Outil d'analyse de fichiers binaires
 * expr.c - équivalent Python du fichier "analysis/types/expr.c"
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


#include "expr.h"


#include <pygobject.h>
#include <string.h>


#include <analysis/types/expr.h>


#include "../type.h"
#include "../../access.h"
#include "../../helpers.h"



/* Crée un nouvel objet Python de type 'ExprType'. */
static PyObject *py_expr_type_new(PyTypeObject *, PyObject *, PyObject *);

/* Fournit la valeur d'un type fourni sous forme de caractères. */
static PyObject *py_expr_type_get_value(PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de l'objet à instancier.                         *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Crée un nouvel objet Python de type 'ExprType'.              *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_expr_type_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Instance à retourner        */
    const char *value;                      /* Valeur brute de l'expression*/
    int ret;                                /* Bilan de lecture des args.  */
    GDataType *dtype;                       /* Version GLib du type        */

#define EXPR_TYPE_DOC                                                       \
    "The ExprType class handles raw expressions defined for some types.\n"  \
    "\n"                                                                    \
    "Instances can be created using the following constructor:\n"           \
    "\n"                                                                    \
    "    ExprType(value)"                                                   \
    "\n"                                                                    \
    "The *value* expression can be any string value, which is not further"  \
    " processed."

    ret = PyArg_ParseTuple(args, "s", &value);
    if (!ret) return NULL;

    dtype = g_expr_type_new(value);
    result = pygobject_new(G_OBJECT(dtype));
    g_object_unref(dtype);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la valeur d'un type fourni sous forme de caractères. *
*                                                                             *
*  Retour      : Chaîne formant une expression.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_expr_type_get_value(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GExprType *type;                        /* Version GLib du type        */
    const char *value;                      /* Valeur exprimée             */

#define EXPR_TYPE_VALUE_ATTRIB PYTHON_GET_DEF_FULL  \
(                                                   \
    value, py_expr_type,                            \
    "Value of the expression type.\n"               \
    "\n"                                            \
    "This value can be any string."                 \
)

    type = G_EXPR_TYPE(pygobject_get(self));

    value = g_expr_type_get_value(type);

    result = PyUnicode_FromString(value);

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

PyTypeObject *get_python_expr_type_type(void)
{
    static PyMethodDef py_expr_type_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_expr_type_getseters[] = {
        EXPR_TYPE_VALUE_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_expr_type_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.types.ExprType",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = EXPR_TYPE_DOC,

        .tp_methods     = py_expr_type_methods,
        .tp_getset      = py_expr_type_getseters,
        .tp_new         = py_expr_type_new

    };

    return &py_expr_type_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.....types.ExprType'.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_expr_type_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'ExprType'      */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_expr_type_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.types");

        dict = PyModule_GetDict(module);

        if (!ensure_python_data_type_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_EXPR_TYPE, type))
            return false;

    }

    return true;

}
