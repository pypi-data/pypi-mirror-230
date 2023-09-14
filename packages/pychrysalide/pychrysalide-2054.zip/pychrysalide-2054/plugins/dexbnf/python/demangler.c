
/* Chrysalide - Outil d'analyse de fichiers binaires
 * demangler.c - équivalent Python du fichier "plugins/dexbnf/demangler.c"
 *
 * Copyright (C) 2018-2020 Cyrille Bagard
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


#include "demangler.h"


#include <pygobject.h>


#include <plugins/pychrysalide/helpers.h>
#include <plugins/pychrysalide/mangling/demangler.h>


#include "../demangler.h"



/* Crée un nouvel objet Python de type 'DexDemangler'. */
static PyObject *py_dex_demangler_new(PyTypeObject *, PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de l'objet à instancier.                         *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Crée un nouvel objet Python de type 'DexDemangler'.          *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dex_demangler_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Instance à retourner        */
    GCompDemangler *demangler;              /* Instance à transposer       */

#define DEX_DEMANGLER_DOC                                                       \
    "DexDemangler is an implementation of a demangler suitable for processing"  \
    " Dex files.\n"                                                             \
    "\n"                                                                        \
    "Instances can be created using the following constructor:\n"               \
    "\n"                                                                        \
    "    DexDemangler()"                                                        \
    "\n"                                                                        \
    "The Android BNF-style definitions for mangled names is available at:"      \
    " https://source.android.com/devices/tech/dalvik/dex-format#string-syntax."

    demangler = g_dex_demangler_new();

    result = pygobject_new(G_OBJECT(demangler));

    g_object_unref(G_OBJECT(demangler));

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

PyTypeObject *get_python_dex_demangler_type(void)
{
    static PyMethodDef py_dex_demangler_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_dex_demangler_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_dex_demangler_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.mangling.DexDemangler",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = DEX_DEMANGLER_DOC,

        .tp_methods     = py_dex_demangler_methods,
        .tp_getset      = py_dex_demangler_getseters,
        .tp_new         = py_dex_demangler_new

    };

    return &py_dex_demangler_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.mangling.DexDemangler'.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool register_python_dex_demangler(PyObject *module)
{
    PyTypeObject *type;                     /* Type Python 'DexDemangler'  */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_dex_demangler_type();

    dict = PyModule_GetDict(module);

    if (!ensure_python_compiler_demangler_is_registered())
        return false;

    if (!register_class_for_pygobject(dict, G_TYPE_DEX_DEMANGLER, type))
        return false;

    return true;

}
