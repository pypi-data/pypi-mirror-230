
/* Chrysalide - Outil d'analyse de fichiers binaires
 * type.h - équivalent Python du fichier "plugins/kaitai/parsers/type.h"
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


#include "type.h"


#include <assert.h>
#include <pygobject.h>


#include <i18n.h>
#include <plugins/pychrysalide/access.h>
#include <plugins/pychrysalide/helpers.h>
#include <plugins/yaml/python/node.h>


#include "struct.h"
#include "../../parsers/type-int.h"



CREATE_DYN_CONSTRUCTOR(kaitai_type, G_TYPE_KAITAI_TYPE);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_kaitai_type_init(PyObject *, PyObject *, PyObject *);

/* Indique le nom de scène du type représenté. */
static PyObject *py_kaitai_type_get_name(PyObject *, void *);



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

static int py_kaitai_type_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    GYamlNode *parent;                      /* Noeud Yaml de l'attribut    */
    int ret;                                /* Bilan de lecture des args.  */
    GKaitaiType *attrib;               /* Création GLib à transmettre */

#define KAITAI_TYPE_DOC                                                         \
    "The KaitaiType class provides support for user-defined type used in"       \
    " Kaitai definitions.\n"                                                    \
    "\n"                                                                        \
    "Instances can be created using the following constructor:\n"               \
    "\n"                                                                        \
    "    KaitaiType(parent)"                                                    \
    "\n"                                                                        \
    "Where *parent* is a pychrysalide.plugins.yaml.YamlNode instance pointing"  \
    " to Yaml data to load.\n"                                                  \
    "\n"                                                                        \
    "The class is the Python bindings for a C implementation of the TypesSpec"  \
    " structure described at https://doc.kaitai.io/ksy_diagram.html."

    /* Récupération des paramètres */

    ret = PyArg_ParseTuple(args, "O&", convert_to_yaml_node, &parent);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    attrib = G_KAITAI_TYPE(pygobject_get(self));

    if (!g_kaitai_type_create(attrib, parent))
    {
        PyErr_SetString(PyExc_ValueError, _("Unable to create Kaitai type."));
        return -1;
    }

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique le nom de scène du type représenté.                  *
*                                                                             *
*  Retour      : Désignation humaine.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_kaitai_type_get_name(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GKaitaiType *type;                      /* Version native du type      */
    const char *name;                       /* Désignation à transmettre   */

#define KAITAI_TYPE_NAME_ATTRIB PYTHON_GET_DEF_FULL         \
(                                                           \
    name, py_kaitai_type,                                   \
    "Name of the user-defined type, provided as a unique"   \
    " string value."                                        \
)

    type = G_KAITAI_TYPE(pygobject_get(self));

    name = g_kaitai_type_get_name(type);
    assert(name != NULL);

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

PyTypeObject *get_python_kaitai_type_type(void)
{
    static PyMethodDef py_kaitai_type_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_kaitai_type_getseters[] = {
        KAITAI_TYPE_NAME_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_kaitai_type_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.plugins.kaitai.parsers.KaitaiType",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = KAITAI_TYPE_DOC,

        .tp_methods     = py_kaitai_type_methods,
        .tp_getset      = py_kaitai_type_getseters,

        .tp_init        = py_kaitai_type_init,
        .tp_new         = py_kaitai_type_new,

    };

    return &py_kaitai_type_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide....parsers.KaitaiType. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_kaitai_type_is_registered(void)
{
    PyTypeObject *type;                     /* Type 'KaitaiType'           */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_kaitai_type_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.plugins.kaitai.parsers");

        dict = PyModule_GetDict(module);

        if (!ensure_python_kaitai_structure_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_KAITAI_TYPE, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en type particulier pour Kaitai.          *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_kaitai_type(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_kaitai_type_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to Kaitai type");
            break;

        case 1:
            *((GKaitaiType **)dst) = G_KAITAI_TYPE(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
