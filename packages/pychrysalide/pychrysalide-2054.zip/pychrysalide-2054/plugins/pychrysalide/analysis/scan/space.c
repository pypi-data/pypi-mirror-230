
/* Chrysalide - Outil d'analyse de fichiers binaires
 * space.c - équivalent Python du fichier "analysis/scan/space.c"
 *
 * Copyright (C) 2022 Cyrille Bagard
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


#include "space.h"


#include <pygobject.h>


#include <i18n.h>
#include <analysis/content.h>
#include <analysis/scan/item.h>
#include <analysis/scan/space-int.h>
#include <plugins/pychrysalide/access.h>
#include <plugins/pychrysalide/helpers.h>
#include <plugins/pychrysalide/analysis/content.h>


#include "item.h"



CREATE_DYN_CONSTRUCTOR(scan_namespace, G_TYPE_SCAN_NAMESPACE);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_scan_namespace_init(PyObject *, PyObject *, PyObject *);

/* Intègre un nouvel élément dans l'esapce de noms. */
static PyObject *py_scan_namespace_register_item(PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet à initialiser (théoriquement).                  *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Initialise une instance sur la base du dérivé de GObject.    *
*                                                                             *
*  Retour      : 0.                                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_scan_namespace_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    const char *name;                       /* Désignation de l'espace     */
    int ret;                                /* Bilan de lecture des args.  */
    GScanNamespace *space;                  /* Création GLib à transmettre */

#define SCAN_NAMESPACE_DOC                                              \
    "ScanNamespace defines a group of properties and functions for a"   \
    " given scan theme.\n"                                              \
    "\n"                                                                \
    "Instances can be created using the following constructor:\n"       \
    "\n"                                                                \
    "    ScanNamespace(name)"                                           \
    "\n"                                                                \
    "Where *name* is a string providing the name of the new namespace."

    /* Récupération des paramètres */

    ret = PyArg_ParseTuple(args, "s", &name);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Elément de base */

    space = G_SCAN_NAMESPACE(pygobject_get(self));

    if (!g_scan_namespace_create(space, name))
    {
        PyErr_SetString(PyExc_ValueError, _("Unable to create scan namespace."));
        return -1;
    }

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet représentant une table de chaînes.              *
*                args = arguments fournis pour l'opération.                   *
*                                                                             *
*  Description : Intègre un nouvel élément dans l'esapce de noms.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_scan_namespace_register_item(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    GRegisteredItem *item;                  /* Elément d'évaluation à lier */
    int ret;                                /* Bilan de lecture des args.  */
    GScanNamespace *space;                  /* Version native              */
    bool status;                            /* Bilan de l'opération        */

#define SCAN_NAMESPACE_REGISTER_ITEM_METHOD PYTHON_METHOD_DEF                   \
(                                                                               \
    register_item, "$self, item, /",                                            \
    METH_VARARGS, py_scan_namespace,                                            \
    "Include an item into a namespace.\n"                                       \
    "\n"                                                                        \
    "The *item* argument has to be a pychrysalide.analysis.scan.RegisteredItem" \
    " instance.\n"                                                              \
    "\n"                                                                        \
    "The function returns a boolean value translating the operation status:"    \
    " *True* in case of success, *False* for a failure.\n"                      \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_registered_item, &item);
    if (!ret) return NULL;

    space = G_SCAN_NAMESPACE(pygobject_get(self));

    status = g_scan_namespace_register_item(space, item);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

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

PyTypeObject *get_python_scan_namespace_type(void)
{
    static PyMethodDef py_scan_namespace_methods[] = {
        SCAN_NAMESPACE_REGISTER_ITEM_METHOD,
        { NULL }
    };

    static PyGetSetDef py_scan_namespace_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_scan_namespace_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.scan.ScanNamespace",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = SCAN_NAMESPACE_DOC,

        .tp_methods     = py_scan_namespace_methods,
        .tp_getset      = py_scan_namespace_getseters,

        .tp_init        = py_scan_namespace_init,
        .tp_new         = py_scan_namespace_new,

    };

    return &py_scan_namespace_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide...scan.ScanNamespace'. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_scan_namespace_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'ScanNamespace' */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_scan_namespace_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.scan");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_SCAN_NAMESPACE, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en espace de noms pour scan.              *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_scan_namespace(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_scan_namespace_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to scan namespace");
            break;

        case 1:
            *((GScanNamespace **)dst) = G_SCAN_NAMESPACE(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
