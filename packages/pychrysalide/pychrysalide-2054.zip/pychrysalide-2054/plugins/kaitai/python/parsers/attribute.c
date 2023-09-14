
/* Chrysalide - Outil d'analyse de fichiers binaires
 * attribute.h - équivalent Python du fichier "plugins/kaitai/parsers/attribute.h"
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


#include "attribute.h"


#include <assert.h>
#include <pygobject.h>


#include <i18n.h>
#include <plugins/pychrysalide/access.h>
#include <plugins/pychrysalide/helpers.h>
#include <plugins/yaml/python/node.h>


#include "../parser.h"
#include "../../parsers/attribute-int.h"



CREATE_DYN_CONSTRUCTOR(kaitai_attribute, G_TYPE_KAITAI_ATTRIBUTE);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_kaitai_attribute_init(PyObject *, PyObject *, PyObject *);

/* Indique la désignation brute d'un identifiant Kaitai. */
static PyObject *py_kaitai_attribute_get_raw_id(PyObject *, void *);

/* Indique la désignation originelle d'un identifiant Kaitai. */
static PyObject *py_kaitai_attribute_get_original_id(PyObject *, void *);

/* Fournit une éventuelle documentation concernant l'attribut. */
static PyObject *py_kaitai_attribute_get_doc(PyObject *, void *);

/* Détermine si l'attribue porte une valeur entière signée. */
static PyObject *py_kaitai_attribute_get_handle_signed_integer(PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet à initialiser (théoriquement).                  *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Initialise une instance sur la base du dérivé de GObject.    *
*                                                                             *
*  Retour      : 0.                                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_kaitai_attribute_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    GYamlNode *parent;                      /* Noeud Yaml de l'attribut    */
    int ret;                                /* Bilan de lecture des args.  */
    GKaitaiAttribute *attrib;               /* Création GLib à transmettre */

#define KAITAI_ATTRIBUTE_DOC                                                    \
    "KaitaiAttribute is the class providing support for parsing binary"         \
    " contents using a special declarative language."                           \
    "\n"                                                                        \
    "Instances can be created using the following constructor:\n"               \
    "\n"                                                                        \
    "    KaitaiAttribute(parent)"                                               \
    "\n"                                                                        \
    "Where *parent* is a pychrysalide.plugins.yaml.YamlNode instance pointing"  \
    " to Yaml data to load.\n"                                                  \
    "\n"                                                                        \
    "The class is the Python bindings for a C implementation of the Attribute"  \
    " structure described at https://doc.kaitai.io/ksy_diagram.html."

    /* Récupération des paramètres */

    ret = PyArg_ParseTuple(args, "O&", convert_to_yaml_node, &parent);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    attrib = G_KAITAI_ATTRIBUTE(pygobject_get(self));

    if (!g_kaitai_attribute_create(attrib, parent, true))
    {
        PyErr_SetString(PyExc_ValueError, _("Unable to create Kaitai attribute."));
        return -1;
    }

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique la désignation brute d'un identifiant Kaitai.        *
*                                                                             *
*  Retour      : Valeur brute de l'identifiant.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_kaitai_attribute_get_raw_id(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GKaitaiAttribute *attrib;               /* Version native de l'attribut*/
    const char *value;                      /* Valeur à transmettre        */

#define KAITAI_ATTRIBUTE_RAW_ID_ATTRIB PYTHON_GET_DEF_FULL  \
(                                                           \
    raw_id, py_kaitai_attribute,                            \
    "Raw value used by Kaitai to identify one attribute"    \
    " among others.\n"                                      \
    "\n"                                                    \
    "The returned indentifier is a string value."           \
)

    attrib = G_KAITAI_ATTRIBUTE(pygobject_get(self));

    value = g_kaitai_attribute_get_raw_id(attrib);
    assert(value != NULL);

    result = PyUnicode_FromString(value);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique la désignation originelle d'un identifiant Kaitai.   *
*                                                                             *
*  Retour      : Valeur originelle de l'identifiant.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_kaitai_attribute_get_original_id(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GKaitaiAttribute *attrib;               /* Version native de l'attribut*/
    const char *value;                      /* Valeur à transmettre        */

#define KAITAI_ATTRIBUTE_ORIGINAL_ID_ATTRIB PYTHON_GET_DEF_FULL     \
(                                                                   \
    original_id, py_kaitai_attribute,                               \
    "Optional alternative identifier for the attribute, as seen in" \
    " the original specifications.\n"                               \
    "\n"                                                            \
    "The returned value is a string or *None*."                     \
)

    attrib = G_KAITAI_ATTRIBUTE(pygobject_get(self));

    value = g_kaitai_attribute_get_original_id(attrib);

    if (value == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }
    else
        result = PyUnicode_FromString(value);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit une éventuelle documentation concernant l'attribut.  *
*                                                                             *
*  Retour      : Description enregistrée ou None si absente.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_kaitai_attribute_get_doc(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GKaitaiAttribute *attrib;               /* Version native de l'attribut*/
    const char *doc;                        /* Documentation à transmettre */

#define KAITAI_ATTRIBUTE_DOC_ATTRIB PYTHON_GET_DEF_FULL     \
(                                                           \
    doc, py_kaitai_attribute,                               \
    "Optional documentation for the attribute.\n"           \
    "\n"                                                    \
    "The returned value is a string or *None*."             \
)

    attrib = G_KAITAI_ATTRIBUTE(pygobject_get(self));

    doc = g_kaitai_attribute_get_doc(attrib);

    if (doc == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }
    else
        result = PyUnicode_FromString(doc);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Détermine si l'attribue porte une valeur entière signée.     *
*                                                                             *
*  Retour      : Bilan de la consultation : True si un entier signé est visé. *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_kaitai_attribute_get_handle_signed_integer(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GKaitaiAttribute *attrib;               /* Version native de l'attribut*/
    bool status;                            /* Bilan d'une consultation    */ 

#define KAITAI_ATTRIBUTE_HANDLE_SIGNED_INTEGER_ATTRIB PYTHON_GET_DEF_FULL   \
(                                                                           \
    handle_signed_integer, py_kaitai_attribute,                             \
    "Sign of the carried integer value, if any: positive or negative?\n"    \
    "\n"                                                                    \
    "This status is provided as a boolean value."                           \
)

    attrib = G_KAITAI_ATTRIBUTE(pygobject_get(self));

    status = g_kaitai_attribute_handle_signed_integer(attrib);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

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

PyTypeObject *get_python_kaitai_attribute_type(void)
{
    static PyMethodDef py_kaitai_attribute_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_kaitai_attribute_getseters[] = {
        KAITAI_ATTRIBUTE_RAW_ID_ATTRIB,
        KAITAI_ATTRIBUTE_ORIGINAL_ID_ATTRIB,
        KAITAI_ATTRIBUTE_DOC_ATTRIB,
        KAITAI_ATTRIBUTE_HANDLE_SIGNED_INTEGER_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_kaitai_attribute_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.plugins.kaitai.parsers.KaitaiAttribute",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = KAITAI_ATTRIBUTE_DOC,

        .tp_methods     = py_kaitai_attribute_methods,
        .tp_getset      = py_kaitai_attribute_getseters,

        .tp_init        = py_kaitai_attribute_init,
        .tp_new         = py_kaitai_attribute_new,

    };

    return &py_kaitai_attribute_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide....KaitaiAttribute.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_kaitai_attribute_is_registered(void)
{
    PyTypeObject *type;                     /* Type 'KaitaiAttribute'      */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_kaitai_attribute_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.plugins.kaitai.parsers");

        dict = PyModule_GetDict(module);

        if (!ensure_python_kaitai_parser_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_KAITAI_ATTRIBUTE, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en attribut de données Kaitai.            *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_kaitai_attribute(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_kaitai_attribute_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to Kaitai attribute");
            break;

        case 1:
            *((GKaitaiAttribute **)dst) = G_KAITAI_ATTRIBUTE(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
