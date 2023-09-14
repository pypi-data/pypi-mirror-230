
/* Chrysalide - Outil d'analyse de fichiers binaires
 * variable.c - équivalent Python du fichier "analysis/variable.c"
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


#include "variable.h"


#include <string.h>
#include <pygobject.h>


#include <i18n.h>


#include <analysis/variable.h>


#include "../access.h"
#include "../helpers.h"



/* Décrit la variable donnée sous forme de caractères. */
static PyObject *py_binary_variable_to_str(PyObject *);

/* Fournit le type d'une variable donnée. */
static PyObject *py_binary_variable_get_type(PyObject *, void *);

/* Fournit le nom d'une variable donnée. */
static PyObject *py_binary_variable_get_name(PyObject *, void *);

/* Définit le nom d'une variable donnée. */
static int py_binary_variable_set_name(PyObject *, PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = instance d'une variable version Python à traiter.     *
*                                                                             *
*  Description : Décrit la variable donnée sous forme de caractères.          *
*                                                                             *
*  Retour      : Chaîne de caractère construite pour l'occasion.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_variable_to_str(PyObject *self)
{
    PyObject *result;                       /* Représentation à retourner  */
    GBinVariable *variable;                 /* Version native de l'objet   */
    char *desc;                             /* Description du type         */

    variable = G_BIN_VARIABLE(pygobject_get(self));

    desc = g_binary_variable_to_string(variable, true);

    result = PyUnicode_FromString(desc);

    free(desc);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le type d'une variable donnée.                       *
*                                                                             *
*  Retour      : Type de la variable.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_variable_get_type(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GBinVariable *variable;                 /* Elément à consulter         */
    GDataType *type;                        /* Type natif de la variable   */

    variable = G_BIN_VARIABLE(pygobject_get(self));

    type = g_binary_variable_get_vtype(variable);

    result = pygobject_new(G_OBJECT(type));

    g_object_unref(G_OBJECT(type));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le nom d'une variable donnée.                        *
*                                                                             *
*  Retour      : Nom de la variable ou None si non précisé.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_variable_get_name(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GBinVariable *variable;                 /* Elément à consulter         */
    const char *name;                       /* Désignation courante        */

    variable = G_BIN_VARIABLE(pygobject_get(self));
    name = g_binary_variable_get_name(variable);

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
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Définit le nom d'une variable donnée.                        *
*                                                                             *
*  Retour      : Bilan de l'opération pour Python.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_binary_variable_set_name(PyObject *self, PyObject *value, void *closure)
{
    GBinVariable *variable;                 /* Elément à traiter           */

    if (!PyUnicode_Check(value) && value != Py_None)
    {
        PyErr_SetString(PyExc_TypeError, _("The attribute value must be a string."));
        return -1;
    }

    variable = G_BIN_VARIABLE(pygobject_get(self));

    if (value == Py_None)
        g_binary_variable_set_name(variable, NULL);
    else
        g_binary_variable_set_name(variable, PyUnicode_DATA(value));

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

PyTypeObject *get_python_binary_variable_type(void)
{
    static PyMethodDef py_binary_variable_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_binary_variable_getseters[] = {
        {
            "type", py_binary_variable_get_type, NULL,
            "Type of the current variable.", NULL
        },
        {
            "name", py_binary_variable_get_name, py_binary_variable_set_name,
            "Name of the current variable.", NULL
        },
        { NULL }
    };

    static PyTypeObject py_binary_variable_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.BinVariable",

        .tp_str         = py_binary_variable_to_str,

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = "PyChrysalide binary variable",

        .tp_methods     = py_binary_variable_methods,
        .tp_getset      = py_binary_variable_getseters

    };

    return &py_binary_variable_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.analysis.BinVariable'. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_binary_variable_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'ProxyFeeder'   */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_binary_variable_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_BIN_VARIABLE, type))
            return false;

    }

    return true;

}
