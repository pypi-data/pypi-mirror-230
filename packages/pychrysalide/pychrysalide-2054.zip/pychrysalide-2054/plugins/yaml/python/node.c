
/* Chrysalide - Outil d'analyse de fichiers binaires
 * node.c - équivalent Python du fichier "plugins/yaml/node.c"
 *
 * Copyright (C) 2019-2023 Cyrille Bagard
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


#include "node.h"


#include <pygobject.h>


#include <plugins/pychrysalide/access.h>
#include <plugins/pychrysalide/helpers.h>


#include "../node.h"



CREATE_DYN_ABSTRACT_CONSTRUCTOR(yaml_node, G_TYPE_YAML_NODE, NULL);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_yaml_node_init(PyObject *, PyObject *, PyObject *);

/* Recherche le premier noeud correspondant à un chemin. */
static PyObject *py_yaml_node_find_first_by_path(PyObject *, PyObject *);



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

static int py_yaml_node_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    int ret;                                /* Bilan de lecture des args.  */

#define YAML_NODE_DOC                                                                               \
    "YamlNode handles a node in a YAML tree.\n"                                                     \
    "\n"                                                                                            \
    "There are two kinds of node contents defined in the YAML specifications:\n"                    \
    "* pair, implemented by the pychrysalide.plugins.yaml.YamlPair object;\n"                       \
    "* sequence and mapping, implemented by the pychrysalide.plugins.yaml.YamlCollection object."

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = variable non utilisée ici.                            *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Recherche le premier noeud correspondant à un chemin.        *
*                                                                             *
*  Retour      : Noeud avec la correspondance établie ou None si non trouvé.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_yaml_node_find_first_by_path(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    const char *path;                       /* Chemin d'accès à traiter    */
    int ret;                                /* Bilan de lecture des args.  */
    GYamlNode *node;                        /* Version GLib du noeud       */
    GYamlNode *found;                      /* Créations GLib à transmettre*/

#define YAML_NODE_FIND_FIRST_BY_PATH_METHOD PYTHON_METHOD_DEF               \
(                                                                           \
    find_first_by_path, "path",                                             \
    METH_VARARGS, py_yaml_node,                                             \
    "Find the first node related to a path among the node YAML children.\n" \
    "\n"                                                                    \
    "Paths are node keys separated by '/', such as '/my/path/to/node'."     \
    " In case where the path ends with a trailing '/', the operation"       \
    " matches the first next met node.\n"                                   \
    "\n"                                                                    \
    "The *path* argument is expected to be a string value.\n"               \
    "\n"                                                                    \
    "The function returns a pychrysalide.plugins.yaml.YamlNode instance,"   \
    " or *None* if none found."                                             \
)

    ret = PyArg_ParseTuple(args, "s", &path);
    if (!ret) return NULL;

    node = G_YAML_NODE(pygobject_get(self));

    found = g_yaml_node_find_first_by_path(node, path);

    if (found != NULL)
    {
        result = pygobject_new(G_OBJECT(found));
        g_object_unref(G_OBJECT(found));
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
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Fournit un accès à une définition de type à diffuser.        *
*                                                                             *
*  Retour      : Définition d'objet pour Python.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyTypeObject *get_python_yaml_node_type(void)
{
    static PyMethodDef py_yaml_node_methods[] = {
        YAML_NODE_FIND_FIRST_BY_PATH_METHOD,
        { NULL }
    };

    static PyGetSetDef py_yaml_node_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_yaml_node_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.plugins.yaml.YamlNode",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_IS_ABSTRACT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = YAML_NODE_DOC,

        .tp_methods     = py_yaml_node_methods,
        .tp_getset      = py_yaml_node_getseters,

        .tp_init        = py_yaml_node_init,
        .tp_new         = py_yaml_node_new,

    };

    return &py_yaml_node_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.plugins.....YamlNode.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_yaml_node_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'YamlNode'      */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_yaml_node_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.plugins.yaml");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_YAML_NODE, type))
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

int convert_to_yaml_node(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_yaml_node_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to YAML node");
            break;

        case 1:
            *((GYamlNode **)dst) = G_YAML_NODE(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
