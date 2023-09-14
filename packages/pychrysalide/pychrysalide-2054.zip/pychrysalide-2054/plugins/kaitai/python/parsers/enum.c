
/* Chrysalide - Outil d'analyse de fichiers binaires
 * enum.h - équivalent Python du fichier "plugins/kaitai/parsers/enum.h"
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


#include "enum.h"


#include <assert.h>
#include <pygobject.h>


#include <i18n.h>
#include <plugins/pychrysalide/access.h>
#include <plugins/pychrysalide/helpers.h>
#include <plugins/yaml/python/node.h>


#include "../../parsers/enum-int.h"



CREATE_DYN_CONSTRUCTOR(kaitai_enum, G_TYPE_KAITAI_ENUM);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_kaitai_enum_init(PyObject *, PyObject *, PyObject *);

/* Traduit une étiquette brute en constante d'énumération. */
static PyObject *py_kaitai_enum_find_value(PyObject *, PyObject *);

/* Traduit une constante d'énumération en étiquette brute. */
static PyObject *py_kaitai_enum_find_label(PyObject *, PyObject *);

/* Traduit une constante d'énumération en documentation. */
static PyObject *py_kaitai_enum_find_documentation(PyObject *, PyObject *);

/* Fournit le nom principal d'une énumération. */
static PyObject *py_kaitai_enum_get_name(PyObject *, void *);



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

static int py_kaitai_enum_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    GYamlNode *parent;                      /* Noeud Yaml de l'attribut    */
    int ret;                                /* Bilan de lecture des args.  */
    GKaitaiEnum *kenum;                 /* Création GLib à transmettre */

#define KAITAI_ENUM_DOC                                                         \
    "The KaitaiEnum class maps integer constants to symbolic names using"       \
    " Kaitai definitions.\n"                                                    \
    "\n"                                                                        \
    "Instances can be created using the following constructor:\n"               \
    "\n"                                                                        \
    "    KaitaiEnum(parent)"                                                    \
    "\n"                                                                        \
    "Where *parent* is a pychrysalide.plugins.yaml.YamlNode instance pointing"  \
    " to Yaml data to load.\n"                                                  \
    "\n"                                                                        \
    "The class is the Python bindings for a C implementation of the EnumSpec"   \
    " structure described at https://doc.kaitai.io/ksy_diagram.html."

    /* Récupération des paramètres */

    ret = PyArg_ParseTuple(args, "O&", convert_to_yaml_node, &parent);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    kenum = G_KAITAI_ENUM(pygobject_get(self));

    if (!g_kaitai_enum_create(kenum, parent))
    {
        PyErr_SetString(PyExc_ValueError, _("Unable to create Kaitai enumeration."));
        return -1;
    }

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = instance de l'énumération Kaitai à manipuler.         *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Traduit une étiquette brute en constante d'énumération.      *
*                                                                             *
*  Retour      : Valeur retrouvée ou None en cas d'échec.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_kaitai_enum_find_value(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    const char *label;                      /* Etiquette à rechercher      */
    int ret;                                /* Bilan de lecture des args.  */
    GKaitaiEnum *kenum;                     /* Enumération Kaitai courante */
    sized_string_t cstr;                    /* CHaîne avec sa longueur     */
    bool status;                            /* Bilan de la conversion      */
    resolved_value_t value;                 /* valeur à transformer        */

#define KAITAI_ENUM_FIND_VALUE_METHOD PYTHON_METHOD_DEF                     \
(                                                                           \
    find_value, "$self, label",                                             \
    METH_VARARGS, py_kaitai_enum,                                           \
    "Translate a given enumeration label into its relative value.\n"        \
    "\n"                                                                    \
    "The *label* argument is expected to be a string.\n"                    \
    "\n"                                                                    \
    "The result is an integer or *None* in case of resolution failure."     \
)

    ret = PyArg_ParseTuple(args, "s", &label);
    if (!ret) return NULL;

    kenum = G_KAITAI_ENUM(pygobject_get(self));

    cstr.data = (char *)label;
    cstr.len = strlen(label);

    status = g_kaitai_enum_find_value(kenum, &cstr, &value);

    if (status)
    {
        if (value.type == GVT_UNSIGNED_INTEGER)
            result = PyLong_FromUnsignedLongLong(value.unsigned_integer);
        else
        {
            assert(value.type == GVT_SIGNED_INTEGER);
            result = PyLong_FromLongLong(value.signed_integer);
        }
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
*  Paramètres  : self = instance de l'énumération Kaitai à manipuler.         *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Traduit une constante d'énumération en étiquette brute.      *
*                                                                             *
*  Retour      : Désignation ou None en cas d'échec.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_kaitai_enum_find_label(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    int prefix;                             /* Préfixe attendu ?           */
    resolved_value_t value;                 /* valeur à transformer        */
    int ret;                                /* Bilan de lecture des args.  */
    GKaitaiEnum *kenum;                     /* Enumération Kaitai courante */
    char *label;                            /* Etiquette reconstruite      */

#define KAITAI_ENUM_FIND_LABEL_METHOD PYTHON_METHOD_DEF                     \
(                                                                           \
    find_label, "$self, value, / , prefix=False",                           \
    METH_VARARGS, py_kaitai_enum,                                           \
    "Provide the label linked to a constant value within the current"       \
    " enumeration.\n"                                                       \
    "\n"                                                                    \
    "The *value* is a simple integer, and *prefix* is a boolean indicating" \
    " if the result has to integrate the enumeration name as a prefix.\n"   \
    "\n"                                                                    \
    "The result is a string or *None* in case of resolution failure."       \
)

    prefix = 0;

    ret = PyArg_ParseTuple(args, "K|p", &value.unsigned_integer, prefix);
    if (!ret) return NULL;

    kenum = G_KAITAI_ENUM(pygobject_get(self));

    value.type = GVT_UNSIGNED_INTEGER;
    label = g_kaitai_enum_find_label(kenum, &value, prefix);

    if (label != NULL)
    {
        result = PyUnicode_FromString(label);
        free(label);
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
*  Paramètres  : self = instance de l'énumération Kaitai à manipuler.         *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Traduit une constante d'énumération en documentation.        *
*                                                                             *
*  Retour      : Documentation associée à la valeur indiquée ou None.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_kaitai_enum_find_documentation(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    resolved_value_t value;                 /* valeur à transformer        */
    int ret;                                /* Bilan de lecture des args.  */
    GKaitaiEnum *kenum;                     /* Enumération Kaitai courante */
    char *doc;                              /* Documentation obtenue       */

#define KAITAI_ENUM_FIND_DOCUMENTATION_METHOD PYTHON_METHOD_DEF             \
(                                                                           \
    find_documentation, "$self, value",                                     \
    METH_VARARGS, py_kaitai_enum,                                           \
    "Provide the optional documentation linked to a constant value within"  \
    " the current enumeration.\n"                                           \
    "\n"                                                                    \
    "The *value* is a simple integer.\n"                                    \
    "\n"                                                                    \
    "The result is a string or *None* if no documentation is registered"    \
    " for the provided value."                                              \
)

    ret = PyArg_ParseTuple(args, "K", &value.unsigned_integer);
    if (!ret) return NULL;

    kenum = G_KAITAI_ENUM(pygobject_get(self));

    value.type = GVT_UNSIGNED_INTEGER;
    doc = g_kaitai_enum_find_documentation(kenum, &value);

    if (doc != NULL)
    {
        result = PyUnicode_FromString(doc);
        free(doc);
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
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le nom principal d'une énumération.                  *
*                                                                             *
*  Retour      : Désignation de l'énumération.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_kaitai_enum_get_name(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GKaitaiEnum *kenum;                     /* Version native de l'objet   */
    const char *name;                       /* Valeur à transmettre        */

#define KAITAI_ENUM_NAME_ATTRIB PYTHON_GET_DEF_FULL     \
(                                                       \
    name, py_kaitai_enum,                               \
    "Name of the enumeration group, as a string value." \
)

    kenum = G_KAITAI_ENUM(pygobject_get(self));

    name = g_kaitai_enum_get_name(kenum);

    result = PyUnicode_FromString(name);

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

PyTypeObject *get_python_kaitai_enum_type(void)
{
    static PyMethodDef py_kaitai_enum_methods[] = {
        KAITAI_ENUM_FIND_VALUE_METHOD,
        KAITAI_ENUM_FIND_LABEL_METHOD,
        KAITAI_ENUM_FIND_DOCUMENTATION_METHOD,
        { NULL }
    };

    static PyGetSetDef py_kaitai_enum_getseters[] = {
        KAITAI_ENUM_NAME_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_kaitai_enum_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.plugins.kaitai.parsers.KaitaiEnum",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = KAITAI_ENUM_DOC,

        .tp_methods     = py_kaitai_enum_methods,
        .tp_getset      = py_kaitai_enum_getseters,

        .tp_init        = py_kaitai_enum_init,
        .tp_new         = py_kaitai_enum_new

    };

    return &py_kaitai_enum_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.plugins...KaitaiEnum.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_kaitai_enum_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'KaitaiEnum'    */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_kaitai_enum_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.plugins.kaitai.parsers");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_KAITAI_ENUM, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en ensemble d'énumérations Kaitai.        *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_kaitai_enum(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_kaitai_enum_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to Kaitai enumeration");
            break;

        case 1:
            *((GKaitaiEnum **)dst) = G_KAITAI_ENUM(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
