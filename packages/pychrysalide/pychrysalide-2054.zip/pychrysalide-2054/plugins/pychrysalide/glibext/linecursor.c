
/* Chrysalide - Outil d'analyse de fichiers binaires
 * linecursor.c - équivalent Python du fichier "glibext/glinecursor.h"
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


#include "linecursor.h"


#include <malloc.h>
#include <pygobject.h>


#include <i18n.h>
#include <glibext/glinecursor.h>


#include "../access.h"
#include "../helpers.h"



/* Détermine si la position de suivi est pertinente ou non. */
static PyObject *py_line_cursor_is_valid(PyObject *, void *);

/* Construit une étiquette de représentation d'un suivi. */
static PyObject *py_line_cursor_get_label(PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Détermine si la position de suivi est pertinente ou non.     *
*                                                                             *
*  Retour      : Bilan de validité.                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_line_cursor_is_valid(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GLineCursor *cursor;                    /* Curseur à consulter         */
    bool status;                            /* Bilan de validité           */

    cursor = G_LINE_CURSOR(pygobject_get(self));
    status = g_line_cursor_is_valid(cursor);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Construit une étiquette de représentation d'un suivi.        *
*                                                                             *
*  Retour      : Etiquette à libérer de la mémoire après usage.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_line_cursor_get_label(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GLineCursor *cursor;                    /* Curseur à consulter         */
    char *label;                            /* Etiquette mise en place     */

    cursor = G_LINE_CURSOR(pygobject_get(self));
    label = g_line_cursor_build_label(cursor);

    result = PyUnicode_FromString(label);

    free(label);

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

PyTypeObject *get_python_line_cursor_type(void)
{
    static PyMethodDef py_line_cursor_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_line_cursor_getseters[] = {
        {
            "valid", py_line_cursor_is_valid, NULL,
            "Validity status of the line cursor.", NULL
        },
        {
            "label", py_line_cursor_get_label, NULL,
            "Label for the current state of a line cursor.", NULL
        },
        { NULL }
    };

    static PyTypeObject py_line_cursor_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.glibext.LineCursor",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = "PyChrysalide line cursor",

        .tp_methods     = py_line_cursor_methods,
        .tp_getset      = py_line_cursor_getseters,

    };

    return &py_line_cursor_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.glibext.LineCursor'.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_line_cursor_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'LineCursor'    */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_line_cursor_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.glibext");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_LINE_CURSOR, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en curseur pour ligne.                    *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_line_cursor(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_line_cursor_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, _("unable to convert the provided argument to line cursor"));
            break;

        case 1:
            *((GLineCursor **)dst) = G_LINE_CURSOR(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
