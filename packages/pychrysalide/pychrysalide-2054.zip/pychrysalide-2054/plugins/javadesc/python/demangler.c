
/* Chrysalide - Outil d'analyse de fichiers binaires
 * demangler.c - équivalent Python du fichier "plugins/javadesc/demangler.c"
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



/* Crée un nouvel objet Python de type 'JavaDemangler'. */
static PyObject *py_java_demangler_new(PyTypeObject *, PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de l'objet à instancier.                         *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Crée un nouvel objet Python de type 'JavaDemangler'.         *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_java_demangler_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Instance à retourner        */
    GCompDemangler *demangler;              /* Instance à transposer       */

#define JAVA_DEMANGLER_DOC                                                      \
    "JavaDemangler is an implementation of a demangler suitable for processing" \
    " JVM files.\n"                                                             \
    "\n"                                                                        \
    "Instances can be created using the following constructor:\n"               \
    "\n"                                                                        \
    "    JavaDemangler()"                                                       \
    "\n"                                                                        \
    "The descriptors used in the Java VM are described in the Java"             \
    " specifications ; for instance, for the Java SE 13 Edition, such"          \
    " descriptors definitions are available at:"                                \
    " https://docs.oracle.com/javase/specs/jvms/se13/html/jvms-4.html#jvms-4.3."

    demangler = g_java_demangler_new();

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

PyTypeObject *get_python_java_demangler_type(void)
{
    static PyMethodDef py_java_demangler_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_java_demangler_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_java_demangler_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.mangling.JavaDemangler",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = JAVA_DEMANGLER_DOC,

        .tp_methods     = py_java_demangler_methods,
        .tp_getset      = py_java_demangler_getseters,
        .tp_new         = py_java_demangler_new

    };

    return &py_java_demangler_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.....JavaDemangler'.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool register_python_java_demangler(PyObject *module)
{
    PyTypeObject *type;                     /* Type Python 'JavaDemangler'  */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_java_demangler_type();

    dict = PyModule_GetDict(module);

    if (!ensure_python_compiler_demangler_is_registered())
        return false;

    if (!register_class_for_pygobject(dict, G_TYPE_JAVA_DEMANGLER, type))
        return false;

    return true;

}
