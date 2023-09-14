
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gdb.c - équivalent Python du fichier "debug/gdbrsp/gdb.c"
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


#include "gdb.h"


#include <pygobject.h>


#include <i18n.h>


#include <debug/gdbrsp/gdb.h>


#include "../debugger.h"
#include "../../access.h"
#include "../../helpers.h"
#include "../../analysis/binary.h"



/* Crée un nouvel objet Python de type 'GdbDebugger'. */
static PyObject *py_gdb_debugger_new(PyTypeObject *, PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de l'objet à instancier.                         *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Crée un nouvel objet Python de type 'GdbDebugger'.           *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_gdb_debugger_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Instance à retourner        */
    PyObject *binary_obj;                   /* Objet pour le binaire lié   */
    const char *server;                     /* Nom du serveur à contacter  */
    unsigned short port;                    /* Port de connexion           */
    int ret;                                /* Bilan de lecture des args.  */
    GLoadedBinary *binary;                  /* Binaire chargé en mémoire   */
    GBinaryDebugger *debugger;              /* Création GLib à transmettre */

    ret = PyArg_ParseTuple(args, "OsH", &binary_obj, &server, &port);
    if (!ret) return NULL;

    ret = PyObject_IsInstance(binary_obj, (PyObject *)get_python_loaded_binary_type());
    if (!ret)
    {
        PyErr_SetString(PyExc_TypeError, _("The first argument must be an instance of LoadedBinary."));
        return NULL;
    }

    binary = G_LOADED_BINARY(pygobject_get(binary_obj));

    debugger = g_gdb_debugger_new(binary, server, port);

    result = pygobject_new(G_OBJECT(debugger));

    g_object_unref(debugger);

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

PyTypeObject *get_python_gdb_debugger_type(void)
{
    static PyMethodDef py_gdb_debugger_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_gdb_debugger_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_gdb_debugger_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.debug.gdbrsp.GdbDebugger",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = "PyChrysalide GDB debugger",

        .tp_methods     = py_gdb_debugger_methods,
        .tp_getset      = py_gdb_debugger_getseters,
        .tp_new         = py_gdb_debugger_new

    };

    return &py_gdb_debugger_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide....gdbrsp.GdbDebugger'.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_gdb_debugger_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'GdbDebugger'   */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_gdb_debugger_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.debug.gdbrsp");

        dict = PyModule_GetDict(module);

        if (!ensure_python_binary_debugger_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_GDB_DEBUGGER, type))
            return false;

    }

    return true;

}
