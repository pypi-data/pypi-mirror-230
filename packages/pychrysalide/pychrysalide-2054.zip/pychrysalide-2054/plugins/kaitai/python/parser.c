
/* Chrysalide - Outil d'analyse de fichiers binaires
 * parser.h - équivalent Python du fichier "plugins/kaitai/parser.h"
 *
 * Copyright (C) 2019 Cyrille Bagard
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


#include "parser.h"


#include <pygobject.h>


#include <plugins/pychrysalide/access.h>
#include <plugins/pychrysalide/helpers.h>


#include "../parser.h"



CREATE_DYN_ABSTRACT_CONSTRUCTOR(kaitai_parser, G_TYPE_KAITAI_PARSER, NULL);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_kaitai_parser_init(PyObject *, PyObject *, PyObject *);



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

static int py_kaitai_parser_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    int ret;                                /* Bilan de lecture des args.  */

#define KAITAI_PARSER_DOC                                                       \
    "KaitaiParser is the class providing support for parsing binary contents"   \
    " using a special declarative language."                                    \
    "\n"                                                                        \
    "It is the Python bindings for a C implementation of the specifications"    \
    " described at http://kaitai.io/."

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

PyTypeObject *get_python_kaitai_parser_type(void)
{
    static PyMethodDef py_kaitai_parser_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_kaitai_parser_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_kaitai_parser_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.plugins.kaitai.KaitaiParser",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = KAITAI_PARSER_DOC,

        .tp_methods     = py_kaitai_parser_methods,
        .tp_getset      = py_kaitai_parser_getseters,

        .tp_init        = py_kaitai_parser_init,
        .tp_new         = py_kaitai_parser_new,

    };

    return &py_kaitai_parser_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.plugins...KaitaiParser.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_kaitai_parser_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'KaitaiParser'  */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_kaitai_parser_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.plugins.kaitai");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_KAITAI_PARSER, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en lecteur de données Kaitai.             *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_kaitai_parser(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_kaitai_parser_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to Kaitai parser");
            break;

        case 1:
            *((GKaitaiParser **)dst) = G_KAITAI_PARSER(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
