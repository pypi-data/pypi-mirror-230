
/* Chrysalide - Outil d'analyse de fichiers binaires
 * routine.c - équivalent Python du fichier "plugins/dex/routine.c"
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


#include "routine.h"


#include <pygobject.h>


#include <plugins/pychrysalide/helpers.h>
#include <plugins/pychrysalide/analysis/routine.h>


#include "../routine.h"



#define DEX_ROUTINE_DOC                                                 \
    "The DexRoutine is a definition of binary routine for DEX methods." \
    "\n"                                                                \
    "The only reason for such an object to exist is to provide a link"  \
    " to a pychrysalide.format.dex.DexMethod from a"                    \
    " pychrysalide.analysis.BinRoutine."



/* Fournit la méthode liée à une routine d'origine Dex. */
static PyObject *py_dex_routine_get_method(PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la méthode liée à une routine d'origine Dex.         *
*                                                                             *
*  Retour      : Méthode Dex liée à la routine ou None.                       *
*                                                                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dex_routine_get_method(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GDexRoutine *routine;                   /* Version native              */
    GDexMethod *method;                     /* Méthode correspondante      */

#define DEX_ROUTINE_METHOD_ATTRIB PYTHON_GET_DEF_FULL                       \
(                                                                           \
    method, py_dex_routine,                                                 \
    "Dex method attached to the Dex routine."                               \
    "\n"                                                                    \
    "The result is a pychrysalide.format.dex.DexMethod instance or None."   \
)

    routine = G_DEX_ROUTINE(pygobject_get(self));

    method = g_dex_routine_get_method(routine);

    if (method != NULL)
    {
        result = pygobject_new(G_OBJECT(method));

        g_object_unref(G_OBJECT(method));

    }
    else
    {
        result = Py_None;
        Py_INCREF(result);
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

PyTypeObject *get_python_dex_routine_type(void)
{
    static PyMethodDef py_dex_routine_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_dex_routine_getseters[] = {
        DEX_ROUTINE_METHOD_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_dex_routine_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.format.dex.DexRoutine",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = DEX_ROUTINE_DOC,

        .tp_methods     = py_dex_routine_methods,
        .tp_getset      = py_dex_routine_getseters

    };

    return &py_dex_routine_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.format.dex.DexRoutine'.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool register_python_dex_routine(PyObject *module)
{
    PyTypeObject *type;                     /* Type Python 'DexRoutine'     */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_dex_routine_type();

    dict = PyModule_GetDict(module);

    if (!ensure_python_binary_routine_is_registered())
        return false;

    if (!register_class_for_pygobject(dict, G_TYPE_DEX_ROUTINE, type))
        return false;

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en routine de fichier Dex.                *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_dex_routine(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_dex_routine_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to dex routine");
            break;

        case 1:
            *((GDexRoutine **)dst) = G_DEX_ROUTINE(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
