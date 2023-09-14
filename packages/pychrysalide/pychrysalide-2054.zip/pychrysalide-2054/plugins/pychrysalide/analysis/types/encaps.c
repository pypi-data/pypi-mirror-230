
/* Chrysalide - Outil d'analyse de fichiers binaires
 * encaps.c - équivalent Python du fichier "analysis/types/encaps.c"
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


#include "encaps.h"


#include <pygobject.h>


#include <analysis/types/encaps.h>


#include "constants.h"
#include "../type.h"
#include "../../access.h"
#include "../../helpers.h"



/* Crée un nouvel objet Python de type 'EncapsulatedType'. */
static PyObject *py_encapsulated_type_new(PyTypeObject *, PyObject *, PyObject *);

/* Fournit le type encapsulée dans le type. */
static PyObject *py_encapsulated_type_get_item(PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de l'objet à instancier.                         *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Crée un nouvel objet Python de type 'EncapsulatedType'.      *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_encapsulated_type_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Instance à retourner        */
    EncapsulationType encapsulation;        /* Type d'encapsulation        */
    GDataType *encapsulated;                /* Type encapsulé              */
    int ret;                                /* Bilan de lecture des args.  */
    GDataType *dtype;                       /* Version GLib du type        */

    ret = PyArg_ParseTuple(args, "kO&", &encapsulation, convert_to_data_type, &encapsulated);
    if (!ret) return NULL;

    dtype = g_encapsulated_type_new(encapsulation, encapsulated);
    result = pygobject_new(G_OBJECT(dtype));
    g_object_unref(dtype);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le type d'encapsulation gérée par le type.           *
*                                                                             *
*  Retour      : Type d'encapsulation gérée.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_encapsulated_type_get_etype(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GEncapsulatedType *type;                /* Version GLib du type        */
    EncapsulationType encapsulation;        /* Type d'encapsulation        */

    type = G_ENCAPSULATED_TYPE(pygobject_get(self));

    encapsulation = g_encapsulated_type_get_etype(type);

    result = PyLong_FromUnsignedLong(encapsulation);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le type encapsulée dans le type.                     *
*                                                                             *
*  Retour      : Sous-type encapsulé dans le type.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_encapsulated_type_get_item(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GEncapsulatedType *type;                /* Version GLib du type        */
    GDataType *encapsulated;                /* Type encapsulé              */

    type = G_ENCAPSULATED_TYPE(pygobject_get(self));

    encapsulated = g_encapsulated_type_get_item(type);

    result = pygobject_new(G_OBJECT(encapsulated));

    g_object_unref(encapsulated);

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

PyTypeObject *get_python_encapsulated_type_type(void)
{
    static PyMethodDef py_encapsulated_type_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_encapsulated_type_getseters[] = {
        {
            "etype", py_encapsulated_type_get_etype, NULL,
            "Provide the encapsultion type.", NULL
        },
        {
            "item", py_encapsulated_type_get_item, NULL,
            "Provide the encapsulted type.", NULL
        },
        { NULL }
    };

    static PyTypeObject py_encapsulated_type_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.types.EncapsulatedType",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = "PyChrysalide encapsulated type",

        .tp_methods     = py_encapsulated_type_methods,
        .tp_getset      = py_encapsulated_type_getseters,
        .tp_new         = py_encapsulated_type_new

    };

    return &py_encapsulated_type_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.....EncapsulatedType'. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_encapsulated_type_is_registered(void)
{
    PyTypeObject *type;                     /* Type 'EncapsulatedType'     */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_encapsulated_type_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.types");

        dict = PyModule_GetDict(module);

        if (!ensure_python_data_type_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_ENCAPSULATED_TYPE, type))
            return false;

        if (!define_encapsulated_type_constants(type))
            return false;

    }

    return true;

}
