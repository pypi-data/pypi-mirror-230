
/* Chrysalide - Outil d'analyse de fichiers binaires
 * cattribs.c - équivalent Python du fichier "analysis/cattribs.h"
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


#include "cattribs.h"


#include <pygobject.h>


#include <i18n.h>


#include <analysis/cattribs.h>


#include "../access.h"
#include "../helpers.h"



/* Crée un nouvel objet Python de type 'ContentAttributes'. */
static PyObject *py_content_attributes_new(PyTypeObject *, PyObject *, PyObject *);

/* Fournit l'ensemble des clefs d'un ensemble d'attributs. */
static PyObject *py_content_attributes_subscript(PyObject *, PyObject *);

/* Fournit l'ensemble des clefs d'un ensemble d'attributs. */
static PyObject *py_content_attributes_get_keys(PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de l'objet à instancier.                         *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Crée un nouvel objet Python de type 'ContentAttributes'.     *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_content_attributes_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Instance à retourner        */
    const char *path;                       /* Chemin d'accès à traiter    */
    int ret;                                /* Bilan de lecture des args.  */
    char *filename;                         /* Nom de fichier embarqué     */
    GContentAttributes *attribs;            /* Création GLib à transmettre */
    PyObject *obj;                          /* Objet Python à retourner    */
    PyObject *str;                          /* Chaîne à retourner          */

#define CONTENT_ATTRIBUTES_DOC                                                  \
    "ContentAttributes is a set of values used at binary content loading.\n"    \
    "\n"                                                                        \
    "Such parameters are useful to transmit password for encrypted contents"    \
    " for instance. These parameters can be accessed like dictionary items:\n"  \
    "\n"                                                                        \
    "    password = attributes['password']\n"                                   \
    "    attributes['password'] = 'updated'\n"                                  \
    "\n"                                                                        \
    "Instances can be created using the following constructor:\n"               \
    "\n"                                                                        \
    "    ContentAttributes(path)\n"                                             \
    "\n"                                                                        \
    "Where path is a list of parameters: '[...]&key0=value0&key1=value1...'"    \
    "\n"                                                                        \
    "The constructor returns a tuple containing a ContentAttributes instance"   \
    " and the original targot filename."

    ret = PyArg_ParseTuple(args, "s", &path);
    if (!ret) return NULL;

    attribs = g_content_attributes_new(path, &filename);

    if (attribs != NULL)
    {
        g_object_ref_sink(G_OBJECT(attribs));
        obj = pygobject_new(G_OBJECT(attribs));
        g_object_unref(attribs);
    }
    else
    {
        obj = Py_None;
        Py_INCREF(obj);
    }

    if (filename != NULL)
    {
        str = PyUnicode_FromString(filename);
        free(filename);
    }
    else
    {
        str = Py_None;
        Py_INCREF(str);
    }

    result = PyTuple_New(2);
    PyTuple_SetItem(result, 0, obj);
    PyTuple_SetItem(result, 1, str);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                key  = clef d'accès servant d'indice.                        *
*                                                                             *
*  Description : Fournit l'ensemble des clefs d'un ensemble d'attributs.      *
*                                                                             *
*  Retour      : Valeur associée à la clef trouvée, ou NULL en cas d'échec.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_content_attributes_subscript(PyObject *self, PyObject *key)
{
    PyObject *result;                       /* Valeur à retourner          */
    void *keyval;                           /* Valeur brute de la clef     */
    GContentAttributes *cattribs;           /* Version native              */
    const char *value;                      /* Valeur brute trouvée        */

    result = NULL;

    if (!PyUnicode_Check(key))
        PyErr_SetString(PyExc_TypeError, "key must be a string value");

    else
    {
        keyval = PyUnicode_DATA(key);

        cattribs = G_CONTENT_ATTRIBUTES(pygobject_get(self));

        value = g_content_attributes_get_value(cattribs, keyval);

        if (value == NULL)
            PyErr_SetString(PyExc_KeyError, "attribute value not found for the provided key");

        else
            result = PyUnicode_FromString(value);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit l'ensemble des clefs d'un ensemble d'attributs.      *
*                                                                             *
*  Retour      : Liste de clefs des attributes conservés dans l'ensemble.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_content_attributes_get_keys(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GContentAttributes *cattribs;           /* Version native              */
    size_t count;                           /* Nombre d'éléments à traiter */
    const char **keys;                      /* Clefs des attributs         */
    size_t i;                               /* Boucle de parcours          */

#define CONTENT_ATTRIBUTES_KEYS_ATTRIB PYTHON_GET_DEF_FULL      \
(                                                               \
    keys, py_content_attributes,                                \
    "Keys of all attributes contained in a set of values."      \
)

    cattribs = G_CONTENT_ATTRIBUTES(pygobject_get(self));

    keys = g_content_attributes_get_keys(cattribs, &count);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
        PyTuple_SetItem(result, i, PyUnicode_FromString(keys[i]));

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

PyTypeObject *get_python_content_attributes_type(void)
{
    static PyMappingMethods py_content_attributes_mapping = {
        .mp_length        = NULL,
        .mp_subscript     = py_content_attributes_subscript,
        .mp_ass_subscript = NULL
    };

    static PyMethodDef py_content_attributes_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_content_attributes_getseters[] = {
        CONTENT_ATTRIBUTES_KEYS_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_content_attributes_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.ContentAttributes",

        .tp_as_mapping  = &py_content_attributes_mapping,

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = CONTENT_ATTRIBUTES_DOC,

        .tp_methods     = py_content_attributes_methods,
        .tp_getset      = py_content_attributes_getseters,
        .tp_new         = py_content_attributes_new

    };

    return &py_content_attributes_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.....ContentAttributes'.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_content_attributes_is_registered(void)
{
    PyTypeObject *type;                     /* Type 'ContentAttributes'    */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_content_attributes_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_CONTENT_ATTRIBUTES, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en ensemble d'attributs pour contenu.     *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_content_attributes(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_content_attributes_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to content attributes");
            break;

        case 1:
            *((GContentAttributes **)dst) = G_CONTENT_ATTRIBUTES(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
