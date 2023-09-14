
/* Chrysalide - Outil d'analyse de fichiers binaires
 * pair.c - équivalent Python du fichier "plugins/yaml/pair.c"
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


#include "pair.h"


#include <assert.h>
#include <malloc.h>
#include <pygobject.h>


#include <i18n.h>
#include <plugins/pychrysalide/access.h>
#include <plugins/pychrysalide/helpers.h>


#include "collection.h"
#include "constants.h"
#include "node.h"
#include "../pair-int.h"



CREATE_DYN_CONSTRUCTOR(yaml_pair, G_TYPE_YAML_PAIR);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_yaml_pair_init(PyObject *, PyObject *, PyObject *);

/* Rassemble une éventuelle séquence de valeurs attachées. */
static PyObject *py_yaml_pair_aggregate_value(PyObject *, PyObject *);

/* Fournit la clef représentée dans une paire en YAML. */
static PyObject *py_yaml_pair_get_key(PyObject *, void *);

/* Indique le format d'origine YAML associé à la clef. */
static PyObject *py_yaml_pair_get_key_style(PyObject *, void *);

/* Fournit l'éventuelle valeur d'une paire en YAML. */
static PyObject *py_yaml_pair_get_value(PyObject *, void *);

/* Indique le format d'origine YAML associé à la clef. */
static PyObject *py_yaml_pair_get_value_style(PyObject *, void *);

/* Attache une collection de noeuds YAML à un noeud. */
static int py_yaml_pair_set_children(PyObject *, PyObject *, void *);

/* Fournit une éventuelle collection rattachée à un noeud. */
static PyObject *py_yaml_pair_get_children(PyObject *, void *);



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

static int py_yaml_pair_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    YamlOriginalStyle kstyle;               /* Format d'origine de la clef */
    const char *value;                      /* Eventuelle valeur associée  */
    YamlOriginalStyle vstyle;               /* Format d'origine de la val. */
    const char *key;                        /* Clef associée au noeud      */
    int ret;                                /* Bilan de lecture des args.  */
    GYamlPair *pair;                        /* Création GLib à transmettre */

#define YAML_PAIR_DOC                                                   \
    "YamlPair handles a key/value pair node in a YAML tree.\n"          \
    "\n"                                                                \
    "Instances can be created using the following constructor:\n"       \
    "\n"                                                                \
    "    YamlPair(key, kstyle=PLAIN, value=None, vstyle=PLAIN)\n"       \
    "\n"                                                                \
    "Where *key* defines the name for the YAML node, and *value*"       \
    " provides an optional direct value for the node. The *kstyle* and" \
    " *vstyle* arguements are"                                          \
    " pychrysalide.plugins.yaml.YamlPair.YamlOriginalStyle states"      \
    " linking an original format to the provided relative strings.\n"   \
    "\n"                                                                \
    "The two style are mainly used to aggregate children values into"   \
    " a raw array. The following declarations are indeed equivalent"    \
    " and pychrysalide.plugins.yaml.YamlPair.aggregate_value()"         \
    " build the latter version from the former one:\n"                  \
    "\n"                                                                \
    "a: [ 1, 2, 3 ]\n"                                                  \
    "\n"                                                                \
    "a:\n"                                                              \
    "    - 1\n"                                                         \
    "    - 2\n"                                                         \
    "    - 3"                                                           \

    /* Récupération des paramètres */

    kstyle = YOS_PLAIN;
    value = NULL;
    vstyle = YOS_PLAIN;

    ret = PyArg_ParseTuple(args, "s|O&sO&",
                           &key, convert_to_yaml_pair_original_style, &kstyle,
                           &value, convert_to_yaml_pair_original_style, &vstyle);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    pair = G_YAML_PAIR(pygobject_get(self));

    if (!g_yaml_pair_create(pair, key, kstyle, value, vstyle))
    {
        PyErr_SetString(PyExc_ValueError, _("Unable to create YAML pair."));
        return -1;

    }

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = serveur à manipuler.                                  *
*                args = arguments d'appel non utilisés ici.                   *
*                                                                             *
*  Description : Rassemble une éventuelle séquence de valeurs attachées.      *
*                                                                             *
*  Retour      : Valeur sous forme de chaîne de caractères ou None.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_yaml_pair_aggregate_value(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    GYamlPair *node;                        /* Version GLib du type        */
    char *value;                            /* Chaîne à transmettre        */

#define YAML_PAIR_AGGREGATE_VALUE_METHOD PYTHON_METHOD_DEF  \
(                                                           \
    aggregate_value, "$self, /",                            \
    METH_NOARGS, py_yaml_pair,                              \
    "Provide the value linked to the YAML node, rebuilding" \
    " it from inner sequenced values if necessary and"      \
    " possible."                                            \
    "\n"                                                    \
    "The result is a string value, or *None* if none"       \
    " available."                                           \
)

    node = G_YAML_PAIR(pygobject_get(self));

    value = g_yaml_pair_aggregate_value(node);

    if (value == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }

    else
    {
        result = PyUnicode_FromString(value);
        free(value);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la clef représentée dans une paire en YAML.          *
*                                                                             *
*  Retour      : Clef sous forme de chaîne de caractères.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_yaml_pair_get_key(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GYamlPair *node;                        /* Version GLib du noeud       */
    const char *key;                        /* Chaîne à transmettre        */

#define YAML_PAIR_KEY_ATTRIB PYTHON_GET_DEF_FULL    \
(                                                   \
    key, py_yaml_pair,                              \
    "Key linked to the YAML key/value pair node,"   \
    " as a string value."                           \
)

    node = G_YAML_PAIR(pygobject_get(self));

    key = g_yaml_pair_get_key(node);
    assert(key != NULL);

    result = PyUnicode_FromString(key);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique le format d'origine YAML associé à la clef.          *
*                                                                             *
*  Retour      : Valeur renseignée lors du chargement du noeud.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_yaml_pair_get_key_style(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GYamlPair *node;                        /* Version GLib du noeud       */
    YamlOriginalStyle style;                /* Format à transmettre        */

#define YAML_PAIR_KEY_STYLE_ATTRIB PYTHON_GET_DEF_FULL      \
(                                                           \
    key_style, py_yaml_pair,                                \
    "Original format for the YAML node Key, as a"           \
    " pychrysalide.plugins.yaml.YamlPair.YamlOriginalStyle" \
    " value."                                               \
)

    node = G_YAML_PAIR(pygobject_get(self));

    style = g_yaml_pair_get_key_style(node);

    result = cast_with_constants_group_from_type(get_python_yaml_pair_type(), "YamlOriginalStyle", style);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit l'éventuelle valeur d'une paire en YAML.             *
*                                                                             *
*  Retour      : Valeur sous forme de chaîne de caractères ou None.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_yaml_pair_get_value(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GYamlPair *node;                        /* Version GLib du type        */
    const char *value;                      /* Chaîne à transmettre        */

#define YAML_PAIR_VALUE_ATTRIB PYTHON_GET_DEF_FULL          \
(                                                           \
    value, py_yaml_pair,                                    \
    "Value linked to the YAML key/value pair node, as a"    \
    " string value, or *None* if none defined."             \
)

    node = G_YAML_PAIR(pygobject_get(self));

    value = g_yaml_pair_get_value(node);

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
*  Description : Indique le format d'origine YAML associé à la clef.          *
*                                                                             *
*  Retour      : Valeur renseignée lors du chargement du noeud.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_yaml_pair_get_value_style(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GYamlPair *node;                        /* Version GLib du noeud       */
    YamlOriginalStyle style;                /* Format à transmettre        */

#define YAML_PAIR_VALUE_STYLE_ATTRIB PYTHON_GET_DEF_FULL    \
(                                                           \
    value_style, py_yaml_pair,                              \
    "Original format for the YAML node Value, as a"         \
    " pychrysalide.plugins.yaml.YamlPair.YamlOriginalStyle" \
    " value.\n"                                             \
    "\n"                                                    \
    "Even if there is no value for the node, the default"   \
    " style is returned: *PLAIN*."                          \
)

    node = G_YAML_PAIR(pygobject_get(self));

    style = g_yaml_pair_get_value_style(node);

    result = cast_with_constants_group_from_type(get_python_yaml_pair_type(), "YamlOriginalStyle", style);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = contenu binaire à manipuler.                       *
*                value   = collection de noeuds YAML.                         *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Attache une collection de noeuds YAML à un noeud.            *
*                                                                             *
*  Retour      : Jeu d'attributs liés au contenu courant.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_yaml_pair_set_children(PyObject *self, PyObject *value, void *closure)
{
    int result;                             /* Bilan à renvoyer            */
    GYamlPair *node;                        /* Version GLib du noeud       */
    GYamlCollection *children;              /* Version GLib de la valeur   */

    node = G_YAML_PAIR(pygobject_get(self));

    if (value == Py_None)
    {
        g_yaml_pair_set_children(node, NULL);
        result = 0;
    }

    else
    {
        if (!convert_to_yaml_collection(value, &children))
            result = -1;

        else
        {
            g_yaml_pair_set_children(node, children);
            result = 0;
        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = contenu binaire à manipuler.                       *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Fournit une éventuelle collection rattachée à un noeud.      *
*                                                                             *
*  Retour      : Collection de noeuds YAML ou None.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_yaml_pair_get_children(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance à retourner        */
    GYamlPair *node;                        /* Version GLib du noeud       */
    GYamlCollection *children;              /* Collection à transmettre    */

#define YAML_PAIR_CHILDREN_ATTRIB PYTHON_GETSET_DEF_FULL            \
(                                                                   \
    children, py_yaml_pair,                                         \
    "Provide or define the collection of nodes attached to another" \
    " YAML node. The collection, if defined, is handled as a"       \
    " pychrysalide.plugins.yaml.YamlCollection instance."           \
)

    node = G_YAML_PAIR(pygobject_get(self));

    children = g_yaml_pair_get_children(node);

    if (children == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }

    else
    {
        result = pygobject_new(G_OBJECT(children));
        g_object_unref(children);
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

PyTypeObject *get_python_yaml_pair_type(void)
{
    static PyMethodDef py_yaml_pair_methods[] = {
        YAML_PAIR_AGGREGATE_VALUE_METHOD,
        { NULL }
    };

    static PyGetSetDef py_yaml_pair_getseters[] = {
        YAML_PAIR_KEY_ATTRIB,
        YAML_PAIR_KEY_STYLE_ATTRIB,
        YAML_PAIR_VALUE_ATTRIB,
        YAML_PAIR_VALUE_STYLE_ATTRIB,
        YAML_PAIR_CHILDREN_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_yaml_pair_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.plugins.yaml.YamlPair",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = YAML_PAIR_DOC,

        .tp_methods     = py_yaml_pair_methods,
        .tp_getset      = py_yaml_pair_getseters,

        .tp_init        = py_yaml_pair_init,
        .tp_new         = py_yaml_pair_new,

    };

    return &py_yaml_pair_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.plugins.....YamlPair.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_yaml_pair_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'YamlPair'      */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_yaml_pair_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.plugins.yaml");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_YAML_PAIR, type))
            return false;

        if (!define_yaml_pair_constants(type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en noeud d'arborescence de format YAML.   *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_yaml_pair(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_yaml_pair_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to YAML key/value pair");
            break;

        case 1:
            *((GYamlPair **)dst) = G_YAML_PAIR(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
