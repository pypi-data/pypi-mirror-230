
/* Chrysalide - Outil d'analyse de fichiers binaires
 * collection.c - équivalent Python du fichier "plugins/yaml/collection.c"
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


#include "collection.h"


#include <pygobject.h>


#include <i18n.h>
#include <plugins/pychrysalide/access.h>
#include <plugins/pychrysalide/helpers.h>


#include "node.h"
#include "../collection-int.h"



CREATE_DYN_CONSTRUCTOR(yaml_collection, G_TYPE_YAML_COLLEC);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_yaml_collection_init(PyObject *, PyObject *, PyObject *);

/* Indique la nature d'une collection YAML. */
static PyObject *py_yaml_collection_is_sequence(PyObject *, void *);

/* Fournit la liste des noeuds intégrés dans une collection. */
static PyObject *py_yaml_collection_get_nodes(PyObject *, void *);



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

static int py_yaml_collection_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    int seq;                                /* Indicateur de type          */
    int ret;                                /* Bilan de lecture des args.  */
    GYamlCollection *collec;                /* Création GLib à transmettre */

#define YAML_COLLECTION_DOC                                                         \
    "YamlCollection handles a collection of YAML nodes.\n"                          \
    "\n"                                                                            \
    "Instances can be created using the following constructor:\n"                   \
    "\n"                                                                            \
    "    YamlCollection(seq=False)\n"                                               \
    "\n"                                                                            \
    "Where *seq* is a boolean value which defines if the collection will be a"      \
    " sequence or a mapping of nodes."

    /* Récupération des paramètres */

    ret = PyArg_ParseTuple(args, "p", &seq);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    collec = G_YAML_COLLEC(pygobject_get(self));

    if (!g_yaml_collection_create(collec, seq))
    {
        PyErr_SetString(PyExc_ValueError, _("Unable to create YAML collection."));
        return -1;

    }

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la liste des noeuds intégrés dans une collection.    *
*                                                                             *
*  Retour      : Enfants d'un noeud issu d'une collection YAML.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_yaml_collection_get_nodes(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GYamlCollection *collec;                /* Version GLib du type        */
    size_t count;                           /* Quantité de noeuds à traiter*/
    GYamlNode **nodes;                      /* Liste des noeuds à la racine*/
    size_t i;                               /* Boucle de parcours          */
#ifndef NDEBUG
    int ret;                                /* Bilan d'une insertion       */
#endif

#define YAML_COLLECTION_NODES_ATTRIB PYTHON_GET_DEF_FULL    \
(                                                           \
    nodes, py_yaml_collection,                              \
    "List of nodes contained in the current collection."    \
)

    collec = G_YAML_COLLEC(pygobject_get(self));

    nodes = g_yaml_collection_get_nodes(collec, &count);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
#ifndef NDEBUG
        ret = PyTuple_SetItem(result, i, pygobject_new(G_OBJECT(nodes[i])));
        assert(ret == 0);
#else
        PyTuple_SetItem(result, i, pygobject_new(G_OBJECT(nodes[i])));
#endif

        g_object_unref(G_OBJECT(nodes[i]));

    }

    free(nodes);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique la nature d'une collection YAML.                     *
*                                                                             *
*  Retour      : Nature de la collection.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_yaml_collection_is_sequence(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GYamlCollection *collec;                /* Version GLib du type        */
    bool status;                            /* Bilan de consultation       */

#define YAML_COLLECTION_IS_SEQUENCE_ATTRIB PYTHON_IS_DEF_FULL           \
(                                                                       \
    sequence, py_yaml_collection,                                       \
    "Nature of the collection: True if the collection is a sequence,"   \
    " False if it is a mapping of \"key: value\" nodes."                \
)

    collec = G_YAML_COLLEC(pygobject_get(self));

    status = g_yaml_collection_is_sequence(collec);

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

PyTypeObject *get_python_yaml_collection_type(void)
{
    static PyMethodDef py_yaml_collection_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_yaml_collection_getseters[] = {
        YAML_COLLECTION_IS_SEQUENCE_ATTRIB,
        YAML_COLLECTION_NODES_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_yaml_collection_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.plugins.yaml.YamlCollection",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = YAML_COLLECTION_DOC,

        .tp_methods     = py_yaml_collection_methods,
        .tp_getset      = py_yaml_collection_getseters,

        .tp_init        = py_yaml_collection_init,
        .tp_new         = py_yaml_collection_new,

    };

    return &py_yaml_collection_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.....YamlCollection.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_yaml_collection_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'YamlCollection'*/
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_yaml_collection_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.plugins.yaml");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_YAML_COLLEC, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en collection de noeuds de format YAML.   *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_yaml_collection(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_yaml_collection_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to YAML collection");
            break;

        case 1:
            *((GYamlCollection **)dst) = G_YAML_COLLEC(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
