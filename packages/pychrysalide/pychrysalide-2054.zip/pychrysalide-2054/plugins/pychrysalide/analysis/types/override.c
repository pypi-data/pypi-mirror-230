
/* Chrysalide - Outil d'analyse de fichiers binaires
 * override.c - équivalent Python du fichier "analysis/types/override.c"
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#include "override.h"


#include <pygobject.h>


#include <analysis/types/override.h>


#include "../type.h"
#include "../../access.h"
#include "../../helpers.h"



/* Crée un nouvel objet Python de type 'OverrideType'. */
static PyObject *py_override_type_new(PyTypeObject *, PyObject *, PyObject *);

/* Fournit le type de base comportant la fonction virtuelle. */
static PyObject *py_override_type_get_base(PyObject *, void *);

/* Fournit les décalages appliquée pour une fonction virtuelle. */
static PyObject *py_override_type_get_offsets(PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de l'objet à instancier.                         *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Crée un nouvel objet Python de type 'OverrideType'.          *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_override_type_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le type de base comportant la fonction virtuelle.    *
*                                                                             *
*  Retour      : Type de base traité.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_override_type_get_base(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GOverrideType *type;                    /* Version GLib du type        */
    GDataType *base;                        /* Base du type                */

    type = G_OVERRIDE_TYPE(pygobject_get(self));

    base = g_override_type_get_base(type);

    result = pygobject_new(G_OBJECT(base));

    g_object_unref(base);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit les décalages appliquée pour une fonction virtuelle. *
*                                                                             *
*  Retour      : Liste des décalages.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_override_type_get_offsets(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GOverrideType *type;                    /* Version GLib du type        */
    call_offset_t off0;                     /* Infos du premier décalage   */
    call_offset_t off1;                     /* Infos du second décalage    */
    bool with_covariant;                    /* Validité du second champ    */
    PyObject *offset;                       /* Transcription intermédiaire */

    type = G_OVERRIDE_TYPE(pygobject_get(self));

    with_covariant = g_override_type_get_offsets(type, &off0, &off1);;

    result = PyTuple_New(with_covariant ? 2 : 1);

    if (off0.virtual)
    {
        offset = PyTuple_New(2);
        PyTuple_SetItem(result, 0, PyLong_FromSsize_t(off0.values[0]));
        PyTuple_SetItem(result, 1, PyLong_FromSsize_t(off0.values[1]));
    }
    else
    {
        offset = PyTuple_New(1);
        PyTuple_SetItem(result, 0, PyLong_FromSsize_t(off0.values[0]));
    }

    PyTuple_SetItem(result, 0, offset);

    if (with_covariant)
    {
        if (off1.virtual)
        {
            offset = PyTuple_New(2);
            PyTuple_SetItem(result, 0, PyLong_FromSsize_t(off1.values[0]));
            PyTuple_SetItem(result, 1, PyLong_FromSsize_t(off1.values[1]));
        }
        else
        {
            offset = PyTuple_New(1);
            PyTuple_SetItem(result, 0, PyLong_FromSsize_t(off1.values[0]));
        }

        PyTuple_SetItem(result, 1, offset);

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

PyTypeObject *get_python_override_type_type(void)
{
    static PyMethodDef py_override_type_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_override_type_getseters[] = {
        {
            "base", py_override_type_get_base, NULL,
            "Provide the base of the override type.", NULL
        },
        {
            "offsets", py_override_type_get_offsets, NULL,
            "Provide the offsets of the override type.", NULL
        },
        { NULL }
    };

    static PyTypeObject py_override_type_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.types.OverrideType",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = "PyChrysalide override type",

        .tp_methods     = py_override_type_methods,
        .tp_getset      = py_override_type_getseters,
        .tp_new         = py_override_type_new

    };

    return &py_override_type_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.....OverrideType'.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_override_type_is_registered(void)
{
    PyTypeObject *type;                     /* Type 'OverrideType'     */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_override_type_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.types");

        dict = PyModule_GetDict(module);

        if (!ensure_python_data_type_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_OVERRIDE_TYPE, type))
            return false;

    }

    return true;

}
