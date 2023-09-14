
/* Chrysalide - Outil d'analyse de fichiers binaires
 * flat.c - équivalent Python du fichier "format/flat.c"
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


#include "flat.h"


#include <pygobject.h>


#include <format/flat.h>


#include "executable.h"
#include "../access.h"
#include "../helpers.h"
#include "../analysis/content.h"



/* Crée un nouvel objet Python de type 'FlatFormat'. */
static PyObject *py_flat_format_new(PyTypeObject *, PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de l'objet à instancier.                         *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Crée un nouvel objet Python de type 'FlatFormat'.            *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_flat_format_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinContent *content;                   /* Instance GLib du contenu    */
    const char *machine;                    /* Identifiant d'architecture  */
    unsigned int endian;                    /* Boutisme de l'architecture  */
    int ret;                                /* Bilan de lecture des args.  */
    GExeFormat *format;                     /* Création GLib à transmettre */

#define FLAT_FORMAT_DOC                                                     \
    "FlatFormat is suitable for all executable contents without a proper"   \
    " file format, such as shellcodes ou eBPF programs.\n"                  \
    "\n"                                                                    \
    "Instances can be created using the following constructor:\n"           \
    "\n"                                                                    \
    "    FlatFormat(content, machine, endian)"                              \
    "\n"                                                                    \
    "Where content is a pychrysalide.analysis.BinContent object, machine"   \
    " defines the target architecture and endian provides the right"        \
    " endianness of the data."

    ret = PyArg_ParseTuple(args, "O&sI", convert_to_binary_content, &content, &machine, &endian);
    if (!ret) return NULL;

    format = g_flat_format_new(content, machine, endian);

    if (format == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }

    else
    {
        result = pygobject_new(G_OBJECT(format));
        g_object_unref(format);
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

PyTypeObject *get_python_flat_format_type(void)
{
    static PyMethodDef py_flat_format_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_flat_format_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_flat_format_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.format.FlatFormat",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = FLAT_FORMAT_DOC,

        .tp_methods     = py_flat_format_methods,
        .tp_getset      = py_flat_format_getseters,
        .tp_new         = py_flat_format_new

    };

    return &py_flat_format_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.format.FlatFormat'.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_flat_format_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'FlatFormat'    */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_flat_format_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.format");

        dict = PyModule_GetDict(module);

        if (!ensure_python_executable_format_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_FLAT_FORMAT, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en format à plat.                         *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_flat_format(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_flat_format_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to flat format");
            break;

        case 1:
            *((GFlatFormat **)dst) = G_FLAT_FORMAT(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
