
/* Chrysalide - Outil d'analyse de fichiers binaires
 * backend.c - équivalent Python du fichier "analysis/scan/backend.c"
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


#include "backend.h"


#include <pygobject.h>


#include <analysis/scan/patterns/backend-int.h>


#include "../../../access.h"
#include "../../../helpers.h"



CREATE_DYN_ABSTRACT_CONSTRUCTOR(engine_backend, G_TYPE_ENGINE_BACKEND, NULL);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_engine_backend_init(PyObject *, PyObject *, PyObject *);



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

static int py_engine_backend_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    int ret;                                /* Bilan de lecture des args.  */

#define ENGINE_BACKEND_DOC                                              \
    "An *EngineBackend* object is the root class of all scan algorithm" \
    " looking for data patterns."

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

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

PyTypeObject *get_python_engine_backend_type(void)
{
    static PyMethodDef py_engine_backend_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_engine_backend_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_engine_backend_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.scan.patterns.EngineBackend",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = ENGINE_BACKEND_DOC,

        .tp_methods     = py_engine_backend_methods,
        .tp_getset      = py_engine_backend_getseters,

        .tp_init        = py_engine_backend_init,
        .tp_new         = py_engine_backend_new,

    };

    return &py_engine_backend_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide....EngineBackend'.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_engine_backend_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'ScanNamespace' */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_engine_backend_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.scan");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_ENGINE_BACKEND, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en méthode de recherches.                 *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_engine_backend(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_engine_backend_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to engine backend");
            break;

        case 1:
            *((GEngineBackend **)dst) = G_ENGINE_BACKEND(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
