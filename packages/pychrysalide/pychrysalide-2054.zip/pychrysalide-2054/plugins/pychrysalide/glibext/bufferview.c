
/* Chrysalide - Outil d'analyse de fichiers binaires
 * bufferview.c - équivalent Python du fichier "glibext/bufferview.c"
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


#include "bufferview.h"


#include <pygobject.h>


#include <glibext/bufferview.h>


#include "../access.h"
#include "../helpers.h"



/* Fournit le tampon de code lié à un visualisateur donné. */
static PyObject *py_buffer_view_get_cache(PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le tampon de code lié à un visualisateur donné.      *
*                                                                             *
*  Retour      : Tampon de code associé au gestionnaire d'affichage.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_buffer_view_get_cache(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    GBufferView *view;                      /* Vue GLib à consulter        */
    GBufferCache *cache;                    /* Tampon associé à cette vue  */

    view = G_BUFFER_VIEW(pygobject_get(self));

    cache = g_buffer_view_get_cache(view);

    result = pygobject_new(G_OBJECT(cache));

    g_object_unref(G_OBJECT(cache));

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

PyTypeObject *get_python_buffer_view_type(void)
{
    static PyMethodDef py_buffer_view_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_buffer_view_getseters[] = {
        {
            "cache", py_buffer_view_get_cache, NULL,
            "Provide the buffer cache for the view.", NULL
        },
        { NULL }
    };

    static PyTypeObject py_buffer_view_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.glibext.BufferView",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = "PyChrysalide code buffer",

        .tp_methods     = py_buffer_view_methods,
        .tp_getset      = py_buffer_view_getseters,

    };

    return &py_buffer_view_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.glibext.BufferView'.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_buffer_view_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'BufferView'    */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_buffer_view_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.glibext");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_BUFFER_VIEW, type))
            return false;

    }

    return true;

}
