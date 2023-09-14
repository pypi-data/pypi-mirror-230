
/* Chrysalide - Outil d'analyse de fichiers binaires
 * array.h - équivalent Python du fichier "plugins/kaitai/array.h"
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


#include "array.h"


#include <pygobject.h>


#include <i18n.h>
#include <plugins/pychrysalide/access.h>
#include <plugins/pychrysalide/helpers.h>


#include "../array-int.h"



CREATE_DYN_CONSTRUCTOR(kaitai_array, G_TYPE_KAITAI_ARRAY);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_kaitai_array_init(PyObject *, PyObject *, PyObject *);

/* Convertit un tableau Kaitai en série d'octets si possible. */
static PyObject *py_kaitai_array___bytes__(PyObject *, PyObject *);



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

static int py_kaitai_array_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    int ret;                                /* Bilan de lecture des args.  */

#define KAITAI_ARRAY_DOC                                                \
    "KaitaiArray defines an array for collecting various Kaitai items." \
    "\n"                                                                \
    "Instances can be created using following constructor:\n"           \
    "\n"                                                                \
    "    KaitaiArray()"                                                 \
    "\n"                                                                \
    "In this implementation, arrays do not have to carry items all"     \
    " belonging to the same type. Access and conversions to bytes are"  \
    " handled and checked at runtime."

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un binaire.                       *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Convertit un tableau Kaitai en série d'octets si possible.   *
*                                                                             *
*  Retour      : Série d'octets ou None.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_kaitai_array___bytes__(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Représentation à renvoyer   */
    GKaitaiArray *array;                    /* Tableau à manipuler         */
    sized_string_t bytes;                   /* Version en série d'octets   */
    bool status;                            /* Bilan de la conversion      */

#define KAITAI_ARRAY_AS_BYTES_METHOD PYTHON_METHOD_DEF              \
(                                                                   \
    __bytes__, "$self, /",                                          \
    METH_NOARGS, py_kaitai_array,                                   \
    "Provide a bytes representation of the array, when possible"    \
    " and without implementing the Python buffer protocol.\n"       \
    "\n"                                                            \
    "THe result is bytes or a *TypeError* exception is raised if"   \
    " the array is not suitable for a conversion to bytes."         \
)

    array = G_KAITAI_ARRAY(pygobject_get(self));

    status = g_kaitai_array_convert_to_bytes(array, &bytes);

    if (status)
    {
        result = PyBytes_FromStringAndSize(bytes.data, bytes.len);
        exit_szstr(&bytes);
    }
    else
    {
        PyErr_SetString(PyExc_TypeError, "unable to convert the Kaitai array to bytes");
        result = NULL;
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

PyTypeObject *get_python_kaitai_array_type(void)
{
    static PyMethodDef py_kaitai_array_methods[] = {
        KAITAI_ARRAY_AS_BYTES_METHOD,
        { NULL }
    };

    static PyGetSetDef py_kaitai_array_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_kaitai_array_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.plugins.kaitai.KaitaiArray",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = KAITAI_ARRAY_DOC,

        .tp_methods     = py_kaitai_array_methods,
        .tp_getset      = py_kaitai_array_getseters,

        .tp_init        = py_kaitai_array_init,
        .tp_new         = py_kaitai_array_new,

    };

    return &py_kaitai_array_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.plugins...KaitaiArray. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_kaitai_array_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'KaitaiArray'  */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_kaitai_array_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.plugins.kaitai");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_KAITAI_ARRAY, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en tableau d'éléments Kaitai.             *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_kaitai_array(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_kaitai_array_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to Kaitai array");
            break;

        case 1:
            *((GKaitaiArray **)dst) = G_KAITAI_ARRAY(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
