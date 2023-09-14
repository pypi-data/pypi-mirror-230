
/* Chrysalide - Outil d'analyse de fichiers binaires
 * instance.h - équivalent Python du fichier "plugins/kaitai/parsers/instance.h"
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


#include "instance.h"


#include <assert.h>
#include <pygobject.h>


#include <i18n.h>
#include <plugins/pychrysalide/access.h>
#include <plugins/pychrysalide/helpers.h>
#include <plugins/yaml/python/node.h>


#include "attribute.h"
#include "../../parsers/instance-int.h"



CREATE_DYN_CONSTRUCTOR(kaitai_instance, G_TYPE_KAITAI_INSTANCE);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_kaitai_instance_init(PyObject *, PyObject *, PyObject *);

/* Indique le nom attribué à une instance Kaitai. */
static PyObject *py_kaitai_instance_get_name(PyObject *, void *);



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

static int py_kaitai_instance_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    GYamlNode *parent;                      /* Noeud Yaml de l'attribut    */
    int ret;                                /* Bilan de lecture des args.  */
    GKaitaiInstance *attrib;               /* Création GLib à transmettre */

#define KAITAI_INSTANCE_DOC                                                     \
    "KaitaiInstance is the class providing support for Kaitai computed"         \
    " values.\n"                                                                \
    "\n"                                                                        \
    "Instances can be created using the following constructor:\n"               \
    "\n"                                                                        \
    "    KaitaiInstance(parent)"                                                \
    "\n"                                                                        \
    "Where *parent* is a pychrysalide.plugins.yaml.YamlNode instance pointing"  \
    " to Yaml data to load.\n"                                                  \
    "\n"                                                                        \
    "The class is the Python bindings for a C implementation of the Instance"   \
    " structure described at https://doc.kaitai.io/ksy_diagram.html."

    /* Récupération des paramètres */

    ret = PyArg_ParseTuple(args, "O&", convert_to_yaml_node, &parent);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    attrib = G_KAITAI_INSTANCE(pygobject_get(self));

    if (!g_kaitai_instance_create(attrib, parent))
    {
        PyErr_SetString(PyExc_ValueError, _("Unable to create Kaitai instance."));
        return -1;
    }

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique le nom attribué à une instance Kaitai.               *
*                                                                             *
*  Retour      : Désignation pointant l'instance.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_kaitai_instance_get_name(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GKaitaiInstance *inst;                  /* Version native de l'instance*/
    const char *name;                       /* Désignation à transmettre   */

#define KAITAI_INSTANCE_NAME_ATTRIB PYTHON_GET_DEF_FULL \
(                                                       \
    name, py_kaitai_instance,                           \
    "Name used by Kaitai to identify the instance"      \
    " among others.\n"                                  \
    "\n"                                                \
    "The returned indentifier is a string value."       \
)

    inst = G_KAITAI_INSTANCE(pygobject_get(self));

    name = g_kaitai_instance_get_name(inst);
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

PyTypeObject *get_python_kaitai_instance_type(void)
{
    static PyMethodDef py_kaitai_instance_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_kaitai_instance_getseters[] = {
        KAITAI_INSTANCE_NAME_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_kaitai_instance_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.plugins.kaitai.parsers.KaitaiInstance",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = KAITAI_INSTANCE_DOC,

        .tp_methods     = py_kaitai_instance_methods,
        .tp_getset      = py_kaitai_instance_getseters,

        .tp_init        = py_kaitai_instance_init,
        .tp_new         = py_kaitai_instance_new,

    };

    return &py_kaitai_instance_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide....KaitaiInstance.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_kaitai_instance_is_registered(void)
{
    PyTypeObject *type;                     /* Type 'KaitaiInstance'      */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_kaitai_instance_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.plugins.kaitai.parsers");

        dict = PyModule_GetDict(module);

        if (!ensure_python_kaitai_attribute_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_KAITAI_INSTANCE, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en instance Kaitai.                       *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_kaitai_instance(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_kaitai_instance_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to Kaitai instance");
            break;

        case 1:
            *((GKaitaiInstance **)dst) = G_KAITAI_INSTANCE(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
