
/* Chrysalide - Outil d'analyse de fichiers binaires
 * preload.c - équivalent Python du fichier "format/preload.c"
 *
 * Copyright (C) 2023 Cyrille Bagard
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


#include "preload.h"


#include <pygobject.h>


#include <format/preload-int.h>


#include "../access.h"
#include "../helpers.h"



CREATE_DYN_CONSTRUCTOR(preload_info, G_TYPE_PRELOAD_INFO);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_preload_info_init(PyObject *, PyObject *, PyObject *);



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

static int py_preload_info_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    int ret;                                /* Bilan d'initialisation      */

#define PRELOAD_INFO_DOC                                                \
    "The PreloadInfo object stores all kinds of disassembling"          \
    " information available from the analysis of a file format"         \
    " itsself.\n"                                                       \
    "\n"                                                                \
    "Instances can be created using the following constructor:\n"       \
    "\n"                                                                \
    "    PreloadInfo()"

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

PyTypeObject *get_python_preload_info_type(void)
{
    static PyMethodDef py_preload_info_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_preload_info_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_preload_info_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.format.PreloadInfo",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = PRELOAD_INFO_DOC,

        .tp_methods     = py_preload_info_methods,
        .tp_getset      = py_preload_info_getseters,

        .tp_init        = py_preload_info_init,
        .tp_new         = py_preload_info_new,

    };

    return &py_preload_info_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.format.PreloadInfo'.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_preload_info_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'ArchContext'   */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_preload_info_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.format");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_PRELOAD_INFO, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en espace de préchargement.               *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_preload_info(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_preload_info_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to disassembly context");
            break;

        case 1:
            *((GPreloadInfo **)dst) = G_PRELOAD_INFO(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
