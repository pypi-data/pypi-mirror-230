
/* Chrysalide - Outil d'analyse de fichiers binaires
 * strenum.c - mise à disposition de constantes pointant des chaînes de caractères
 *
 * Copyright (C) 2020 Cyrille Bagard
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


#include "strenum.h"


#include <stddef.h>
#include <string.h>
#include <structmember.h>


#include "access.h"
#include "helpers.h"



/* Objet à vocation abstraite */
typedef struct _PyStringEnum
{
    PyDictObject base;                      /* A laisser en premier        */

    char *grp_doc;                          /* Documentation d'instance    */

    int val;

} PyStringEnum;


/* Initialise un objet Python de type 'StringEnum'. */
static int py_string_enum_init(PyStringEnum *, PyObject *, PyObject *);

/* Accompagne la suppression complète d'un objet 'StringEnum'. */
static void py_string_enum_finalize(PyStringEnum *);

/* Assure l'encadrement des accès aux champs d'une structure. */
static PyObject *py_string_enum_getattr(PyObject *, char *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = instance d'objet à initialiser.                       *
*                args = arguments passés pour l'appel.                        *
*                kwds = mots clefs éventuellement fournis en complément.      *
*                                                                             *
*  Description : Initialise un objet Python de type 'StringEnum'.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_string_enum_init(PyStringEnum *self, PyObject *args, PyObject *kwds)
{
    int result;                             /* Bilan à retourner           */
    char *doc;                              /* Documentation de l'instance */
    int ret;                                /* Bilan de lecture des args.  */

#define STRING_ENUM_DOC                                             \
    "StringEnum provides dictionaries collecting string constants." \
    "\n"                                                            \
    "Such constants are mainly used as keywords for accessing"      \
    " configuration parameters."

    result = -1;

    doc = NULL;

    ret = PyArg_ParseTuple(args, "|s", &doc);
    if (!ret) goto exit;

    if (doc != NULL)
        self->grp_doc = strdup(doc);

    result = 0;

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = instance d'objet à traiter.                           *
*                                                                             *
*  Description : Accompagne la suppression complète d'un objet 'StringEnum'.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_string_enum_finalize(PyStringEnum *self)
{
    if (self->grp_doc != NULL)
        free(self->grp_doc);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = structure C convertie en Python.                      *
*                name = nom du champ auquel un accès est demandé.             *
*                                                                             *
*  Description : Assure l'encadrement des accès aux champs d'une structure.   *
*                                                                             *
*  Retour      : Valeur du champ demandé.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_string_enum_getattr(PyObject *self, char *name)
{
    PyObject *result;                       /* Elément à retourner         */
    PyObject *w;                            /* Conversion du nom de champ  */
    PyTypeObject *tp;                       /* Type de l'objet manipulé    */

    result = PyDict_GetItemString(self, name);

    if (result != NULL)
        Py_INCREF(result);

    else
    {
        w = PyUnicode_InternFromString(name);
        if (w == NULL) return NULL;

        tp = Py_TYPE(self);

        if (tp->tp_base->tp_getattro != NULL)
            result = tp->tp_base->tp_getattro(self, w);

        Py_DECREF(w);

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

PyTypeObject *get_python_string_enum_type(void)
{
    static PyMethodDef py_string_enum_methods[] = {
        { NULL }
    };

    static PyMemberDef py_string_enum_members[] = {
        {
            "__grp_doc__", T_STRING, offsetof(PyStringEnum, grp_doc), READONLY,
            "Specialized documentation for an instance of the object."
        },
        { NULL }
    };

    static PyGetSetDef py_string_enum_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_string_enum_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.StringEnum",
        .tp_basicsize   = sizeof(PyStringEnum),

        .tp_getattr     = py_string_enum_getattr,

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE \
                          | Py_TPFLAGS_DICT_SUBCLASS | Py_TPFLAGS_HAVE_FINALIZE,

        .tp_doc         = STRING_ENUM_DOC,

        .tp_methods     = py_string_enum_methods,
        .tp_members     = py_string_enum_members,
        .tp_getset      = py_string_enum_getseters,
        .tp_base        = &PyDict_Type,

        .tp_init        = (initproc)py_string_enum_init,

        .tp_finalize    = (destructor)py_string_enum_finalize,

    };

    return &py_string_enum_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.PyStringEnum'.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_string_enum_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'StringEnum'    */
    PyObject *module;                       /* Module à recompléter        */

    type = get_python_string_enum_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide");

        if (PyType_Ready(type) != 0)
            return false;

        if (!register_python_module_object(module, type))
            return false;

    }

    return true;

}
