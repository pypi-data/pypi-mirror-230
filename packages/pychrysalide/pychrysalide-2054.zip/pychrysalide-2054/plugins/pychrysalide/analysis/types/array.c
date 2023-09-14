
/* Chrysalide - Outil d'analyse de fichiers binaires
 * array.c - équivalent Python du fichier "analysis/types/array.c"
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


#include "array.h"


#include <pygobject.h>
#include <string.h>


#include <i18n.h>
#include <analysis/types/array.h>


#include "../type.h"
#include "../../access.h"
#include "../../helpers.h"



/* Crée un nouvel objet Python de type 'ArrayType'. */
static PyObject *py_array_type_new(PyTypeObject *, PyObject *, PyObject *);

/* Fournit le type des membres du tableau. */
static PyObject *py_array_type_get_members_type(PyObject *, void *);

/* Indique si la dimension du tableau est chiffrée. */
static PyObject *py_array_type_is_numbered(PyObject *, void *);

/* Fournit la dimension associée au tableau. */
static PyObject *py_array_type_get_dimension(PyObject *, void *);

/* Fournit la dimension associée au tableau. */
static PyObject *py_array_type_get_dimension_number(PyObject *, void *);

/* Définit la dimension associée au tableau. */
static int py_array_type_set_dimension_number(PyObject *, PyObject *, void *);

/* Fournit la dimension associée au tableau. */
static PyObject *py_array_type_get_dimension_expression(PyObject *, void *);

/* Définit la dimension associée au tableau. */
static int py_array_type_set_dimension_expression(PyObject *, PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de l'objet à instancier.                         *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Crée un nouvel objet Python de type 'ArrayType'.             *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_array_type_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Instance à retourner        */
    GDataType *members;                     /* Version GLib du type        */
    int ret;                                /* Bilan de lecture des args.  */
    GDataType *dtype;                       /* Version GLib du type        */

    ret = PyArg_ParseTuple(args, "O&", convert_to_data_type, &members);
    if (!ret) return NULL;

    dtype = g_array_type_new(members);
    result = pygobject_new(G_OBJECT(dtype));
    g_object_unref(dtype);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le type des membres du tableau.                      *
*                                                                             *
*  Retour      : Instance d'un autre type.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_array_type_get_members_type(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GArrayType *type;                       /* Version GLib du type        */
    GDataType *members;                     /* Type des membres du tableau */

    type = G_ARRAY_TYPE(pygobject_get(self));

    members = g_array_type_get_members_type(type);

    result = pygobject_new(G_OBJECT(members));

    g_object_unref(members);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique si la dimension du tableau est chiffrée.             *
*                                                                             *
*  Retour      : Py_True si la dimension est chiffrée.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_array_type_is_numbered(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GArrayType *type;                       /* Version GLib du type        */
    bool status;                            /* Nature de la dimension liée */

    type = G_ARRAY_TYPE(pygobject_get(self));

    status = g_array_type_is_dimension_numbered(type);

    result = status ? Py_True : Py_False;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la dimension associée au tableau.                    *
*                                                                             *
*  Retour      : Dimension de nature variable.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_array_type_get_dimension(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GArrayType *type;                       /* Version GLib du type        */
    bool status;                            /* Nature de la dimension liée */

    type = G_ARRAY_TYPE(pygobject_get(self));

    status = g_array_type_is_dimension_numbered(type);

    if (status)
        result = py_array_type_get_dimension_number(self, NULL);
    else
        result = py_array_type_get_dimension_expression(self, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la dimension associée au tableau.                    *
*                                                                             *
*  Retour      : Dimension positive ou nulle.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_array_type_get_dimension_number(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GArrayType *type;                       /* Version GLib du type        */
    ssize_t dim;                            /* Taille du tableau           */

    type = G_ARRAY_TYPE(pygobject_get(self));

    dim = g_array_type_get_dimension_number(type);

    result = PyLong_FromSsize_t(dim);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Définit la dimension associée au tableau.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_array_type_set_dimension_number(PyObject *self, PyObject *value, void *closure)
{
    GArrayType *type;                       /* Version GLib du type        */

    if (!PyLong_Check(value))
    {
        PyErr_SetString(PyExc_TypeError, _("The attribute value must be a number."));
        return -1;
    }

    type = G_ARRAY_TYPE(pygobject_get(self));

    g_array_type_set_dimension_number(type, PyLong_AsSsize_t(value));

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la dimension associée au tableau.                    *
*                                                                             *
*  Retour      : Expression de dimension.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_array_type_get_dimension_expression(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GArrayType *type;                       /* Version GLib du type        */
    const char *dim;                        /* Taille du tableau           */

    type = G_ARRAY_TYPE(pygobject_get(self));

    dim = g_array_type_get_dimension_expression(type);

    if (dim != NULL)
        result = PyUnicode_FromString(dim);

    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Définit la dimension associée au tableau.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_array_type_set_dimension_expression(PyObject *self, PyObject *value, void *closure)
{
    GArrayType *type;                       /* Version GLib du type        */

    if (!PyUnicode_Check(value) && value != Py_None)
    {
        PyErr_SetString(PyExc_TypeError, _("The attribute value must be a string or None."));
        return -1;
    }

    type = G_ARRAY_TYPE(pygobject_get(self));

    if (value == Py_None)
        g_array_type_set_empty_dimension(type);

    else
        g_array_type_set_dimension_expression(type, strdup(PyUnicode_DATA(value)));

    return 0;

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

PyTypeObject *get_python_array_type_type(void)
{
    static PyMethodDef py_array_type_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_array_type_getseters[] = {
        {
            "members", py_array_type_get_members_type, NULL,
            "Provide the type of each members of the array.", NULL
        },
        {
            "numbered", py_array_type_is_numbered, NULL,
            "Tell if the dimension of the array is a number.", NULL
        },
        {
            "dimension", py_array_type_get_dimension, NULL,
            "Provide the array dimension.", NULL
        },
        {
            "dimension_number", py_array_type_get_dimension_number, py_array_type_set_dimension_number,
            "Give access to the array dimension as number.", NULL
        },
        {
            "dimension_expression", py_array_type_get_dimension_expression, py_array_type_set_dimension_expression,
            "Give access to the array dimension as expression.", NULL
        },
        { NULL }
    };

    static PyTypeObject py_array_type_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.types.ArrayType",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = "PyChrysalide array type",

        .tp_methods     = py_array_type_methods,
        .tp_getset      = py_array_type_getseters,
        .tp_new         = py_array_type_new

    };

    return &py_array_type_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.....types.ArrayType'.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_array_type_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'ArrayType'     */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_array_type_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.types");

        dict = PyModule_GetDict(module);

        if (!ensure_python_data_type_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_ARRAY_TYPE, type))
            return false;

    }

    return true;

}
