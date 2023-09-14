
/* Chrysalide - Outil d'analyse de fichiers binaires
 * template.c - équivalent Python du fichier "analysis/types/template.c"
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


#include "template.h"


#include <pygobject.h>
#include <string.h>


#include <i18n.h>
#include <analysis/types/template.h>


#include "../type.h"
#include "../../access.h"
#include "../../helpers.h"



/* Crée un nouvel objet Python de type 'TemplateType'. */
static PyObject *py_template_type_new(PyTypeObject *, PyObject *, PyObject *);

/* Ajoute un paramètre à un gabarit. */
static PyObject *py_template_type_add_param(PyObject *, PyObject *);

/* Indique la désignation principale du type. */
static PyObject *py_template_type_get_name(PyObject *, void *);

/* Précise la désignation principale du type. */
static int py_template_type_set_name(PyObject *, PyObject *, void *);

/* Fournit les arguments du gabarit. */
static PyObject *py_template_type_get_params(PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de l'objet à instancier.                         *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Crée un nouvel objet Python de type 'TemplateType'.          *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_template_type_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Instance à retourner        */
    GDataType *dtype;                       /* Version GLib du type        */

#define TEMPLATE_TYPE_DOC                                                   \
    "The TemplateType class declares an empty template type.\n"             \
    "\n"                                                                    \
    "Instances can be created using the following constructor:\n"           \
    "\n"                                                                    \
    "    TemplateType()"                                                    \
    "\n"                                                                    \
    "Name and template parameters have then to be filled in the created"    \
    " declaration with the relevant methods or properties."

    dtype = g_template_type_new();
    result = pygobject_new(G_OBJECT(dtype));
    g_object_unref(dtype);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = projet d'étude à manipuler.                           *
*                args = arguments accompagnant l'appel.                       *
*                                                                             *
*  Description : Ajoute un paramètre à un gabarit.                            *
*                                                                             *
*  Retour      : Py_None.                                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_template_type_add_param(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Absence de retour Python    */
    GDataType *param;                       /* Version GLib du type        */
    int ret;                                /* Bilan de lecture des args.  */
    GTemplateType *type;                    /* Version GLib du type        */

#define TEMPLATE_TYPE_ADD_PARAM_METHOD PYTHON_METHOD_DEF                \
(                                                                       \
    add_param, "$self, param, /",                                       \
    METH_VARARGS, py_template_type,                                     \
    "Add an extra parameter to the template type.\n"                    \
    "\n"                                                                \
    "This extra parameter has to be a pychrysalide.analysis.DataType"   \
    " instance."                                                        \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_data_type, &param);
    if (!ret) return NULL;

    type = G_TEMPLATE_TYPE(pygobject_get(self));

    g_template_type_add_param(type, param);

    result = Py_None;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique la désignation principale du type.                   *
*                                                                             *
*  Retour      : Désignation humaine du type.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_template_type_get_name(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GTemplateType *type;                    /* Version GLib du type        */
    const char *name;                       /* Désignation humaine         */

#define TEMPLATE_TYPE_NAME_ATTRIB PYTHON_GETSET_DEF_FULL    \
(                                                           \
    name, py_template_type,                                 \
    "Name of the template type.\n"                          \
    "\n"                                                    \
    "This property is a simple string, or None is the"      \
    " template type has no name."                           \
)

    type = G_TEMPLATE_TYPE(pygobject_get(self));

    name = g_template_type_get_name(type);

    if (name == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }
    else
        result = PyUnicode_FromString(name);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Précise la désignation principale du type.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_template_type_set_name(PyObject *self, PyObject *value, void *closure)
{
    GTemplateType *type;                       /* Version GLib du type        */

    if (!PyUnicode_Check(value))
    {
        PyErr_SetString(PyExc_TypeError, _("The attribute value must be a string."));
        return -1;
    }

    type = G_TEMPLATE_TYPE(pygobject_get(self));

    g_template_type_set_name(type, PyUnicode_DATA(value));

    return 0;

}



/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit les arguments du gabarit.                            *
*                                                                             *
*  Retour      : Liste de types de paramètres.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_template_type_get_params(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GTemplateType *type;                    /* Version GLib du type        */
    size_t count;                           /* Nombre de paramètres        */
    size_t i;                               /* Boucle de parcours          */
    GDataType *param;                       /* Paramètre du gabarit        */

#define TEMPLATE_TYPE_PARAMS_ATTRIB PYTHON_GET_DEF_FULL                 \
(                                                                       \
    params, py_template_type,                                           \
    "List of all parameters of the template type.\n"                    \
    "\n"                                                                \
    "The returned value is a tuple of pychrysalide.analysis.DataType"   \
    " instances."                                                       \
)

    type = G_TEMPLATE_TYPE(pygobject_get(self));

    count = g_template_type_count_params(type);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
        param = g_template_type_get_param(type, i);

        PyTuple_SetItem(result, i, pygobject_new(G_OBJECT(param)));

        g_object_unref(param);

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

PyTypeObject *get_python_template_type_type(void)
{
    static PyMethodDef py_template_type_methods[] = {
        TEMPLATE_TYPE_ADD_PARAM_METHOD,
        { NULL }
    };

    static PyGetSetDef py_template_type_getseters[] = {
        TEMPLATE_TYPE_NAME_ATTRIB,
        TEMPLATE_TYPE_PARAMS_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_template_type_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.types.TemplateType",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = TEMPLATE_TYPE_DOC,

        .tp_methods     = py_template_type_methods,
        .tp_getset      = py_template_type_getseters,
        .tp_new         = py_template_type_new

    };

    return &py_template_type_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.....TemplateType'.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_template_type_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'TemplateType'  */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_template_type_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.types");

        dict = PyModule_GetDict(module);

        if (!ensure_python_data_type_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_TEMPLATE_TYPE, type))
            return false;

    }

    return true;

}
