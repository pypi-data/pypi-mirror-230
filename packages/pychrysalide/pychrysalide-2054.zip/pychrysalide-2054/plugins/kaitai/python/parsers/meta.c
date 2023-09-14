
/* Chrysalide - Outil d'analyse de fichiers binaires
 * meta.h - équivalent Python du fichier "plugins/kaitai/parsers/meta.h"
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


#include "meta.h"


#include <pygobject.h>


#include <i18n.h>
#include <plugins/pychrysalide/access.h>
#include <plugins/pychrysalide/helpers.h>
#include <plugins/pychrysalide/analysis/content.h>
#include <plugins/yaml/python/node.h>


#include "../../parsers/meta-int.h"



CREATE_DYN_CONSTRUCTOR(kaitai_meta, G_TYPE_KAITAI_META);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_kaitai_meta_init(PyObject *, PyObject *, PyObject *);

/* Fournit l'identifié associé à une définiton Kaitai. */
static PyObject *py_kaitai_meta_get_id(PyObject *, void *);

/* Fournit la désignation humaine d'une définiton Kaitai. */
static PyObject *py_kaitai_meta_get_title(PyObject *, void *);



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

static int py_kaitai_meta_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    GYamlNode *parent;                      /* Noeud Yaml de l'attribut    */
    int ret;                                /* Bilan de lecture des args.  */
    GKaitaiMeta *kmeta;                 /* Création GLib à transmettre */

#define KAITAI_META_DOC                                                         \
    "The KaitaiMeta class stores general information about a Kaitai definition,"\
    " such as required imports or the default endianness for reading values.\n" \
    "\n"                                                                        \
    "Instances can be created using the following constructor:\n"               \
    "\n"                                                                        \
    "    KaitaiMeta(parent)"                                                    \
    "\n"                                                                        \
    "Where *parent* is a pychrysalide.plugins.yaml.YamlNode instance pointing"  \
    " to Yaml data to load.\n"                                                  \
    "\n"                                                                        \
    "The class is the Python bindings for a C implementation of the MetaSpec"   \
    " structure described at https://doc.kaitai.io/ksy_diagram.html."

    /* Récupération des paramètres */

    ret = PyArg_ParseTuple(args, "O&", convert_to_yaml_node, &parent);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    kmeta = G_KAITAI_META(pygobject_get(self));

    if (!g_kaitai_meta_create(kmeta, parent))
    {
        PyErr_SetString(PyExc_ValueError, _("Unable to create Kaitai global description."));
        return -1;
    }

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit l'identifié associé à une définiton Kaitai.          *
*                                                                             *
*  Retour      : Identifiant de définition complète ou None.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_kaitai_meta_get_id(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GKaitaiMeta *meta;                      /* Version native de l'objet   */
    const char *id;                         /* Valeur à transmettre        */

#define KAITAI_META_ID_ATTRIB PYTHON_GET_DEF_FULL       \
(                                                       \
    id, py_kaitai_meta,                                 \
    "Identifier for the Kaitai definition, as a string" \
    " value or *None* if any."                          \
)

    meta = G_KAITAI_META(pygobject_get(self));

    id = g_kaitai_meta_get_id(meta);

    if (id != NULL)
        result = PyUnicode_FromString(id);

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
*  Description : Fournit la désignation humaine d'une définiton Kaitai.       *
*                                                                             *
*  Retour      : Intitulé de définition OU None.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_kaitai_meta_get_title(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GKaitaiMeta *meta;                      /* Version native de l'objet   */
    const char *title;                      /* Valeur à transmettre        */

#define KAITAI_META_TITLE_ATTRIB PYTHON_GET_DEF_FULL        \
(                                                           \
    title, py_kaitai_meta,                                  \
    "Humain description for the Kaitai definition, as a"    \
    " string value or *None* if any."                       \
)

    meta = G_KAITAI_META(pygobject_get(self));

    title = g_kaitai_meta_get_title(meta);

    if (title != NULL)
        result = PyUnicode_FromString(title);

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
*  Description : Fournit la désignation humaine d'une définiton Kaitai.       *
*                                                                             *
*  Retour      : Intitulé de définition OU None.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_kaitai_meta_get_endian(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GKaitaiMeta *meta;                      /* Version native de l'objet   */
    SourceEndian endian;                    /* Valeur à transmettre        */

#define KAITAI_META_ENDIAN_ATTRIB PYTHON_GET_DEF_FULL       \
(                                                           \
    endian, py_kaitai_meta,                                 \
    "Default endianness for the Kaitai definition, as a"    \
    " pychrysalide.analysis.BinContent.SourceEndian value." \
)

    meta = G_KAITAI_META(pygobject_get(self));

    endian = g_kaitai_meta_get_endian(meta);

    result = cast_with_constants_group_from_type(get_python_binary_content_type(), "SourceEndian", endian);

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

PyTypeObject *get_python_kaitai_meta_type(void)
{
    static PyMethodDef py_kaitai_meta_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_kaitai_meta_getseters[] = {
        KAITAI_META_ID_ATTRIB,
        KAITAI_META_TITLE_ATTRIB,
        KAITAI_META_ENDIAN_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_kaitai_meta_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.plugins.kaitai.parsers.KaitaiMeta",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = KAITAI_META_DOC,

        .tp_methods     = py_kaitai_meta_methods,
        .tp_getset      = py_kaitai_meta_getseters,

        .tp_init        = py_kaitai_meta_init,
        .tp_new         = py_kaitai_meta_new

    };

    return &py_kaitai_meta_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.plugins...KaitaiMeta.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_kaitai_meta_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'KaitaiMeta'    */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_kaitai_meta_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.plugins.kaitai.parsers");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_KAITAI_META, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en description globale Kaitai.            *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_kaitai_meta(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_kaitai_meta_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to Kaitai global description");
            break;

        case 1:
            *((GKaitaiMeta **)dst) = G_KAITAI_META(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
