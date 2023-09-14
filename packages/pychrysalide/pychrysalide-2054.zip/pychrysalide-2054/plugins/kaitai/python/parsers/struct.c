
/* Chrysalide - Outil d'analyse de fichiers binaires
 * struct.h - équivalent Python du fichier "plugins/kaitai/struct.h"
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


#include "struct.h"


#include <pygobject.h>


#include <i18n.h>
#include <plugins/pychrysalide/access.h>
#include <plugins/pychrysalide/helpers.h>
#include <plugins/pychrysalide/analysis/content.h>


#include "../parser.h"
#include "../../parsers/struct-int.h"



CREATE_DYN_CONSTRUCTOR(kaitai_structure, G_TYPE_KAITAI_STRUCT);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_kaitai_structure_init(PyObject *, PyObject *, PyObject *);

/* Parcourt un contenu binaire selon une description Kaitai. */
static PyObject *py_kaitai_structure_parse(PyObject *, PyObject *);

/* Fournit la désignation humaine d'une définiton Kaitai. */
static PyObject *py_kaitai_structure_get_meta(PyObject *, void *);



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

static int py_kaitai_structure_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    const char *text;                       /* Contenu de règles à traiter */
    const char *filename;                   /* Fichier de définitions      */
    int ret;                                /* Bilan de lecture des args.  */
    GKaitaiStruct *kstruct;                 /* Création GLib à transmettre */

    static char *kwlist[] = { "text", "filename", NULL };

#define KAITAI_STRUCT_DOC                                                       \
    "KaitaiStruct is the class providing support for parsing binary contents"   \
    " using a special declarative language."                                    \
    "\n"                                                                        \
    "Instances can be created using one of the following constructors:\n"       \
    "\n"                                                                        \
    "    KaitaiStruct(text=str)"                                                \
    "\n"                                                                        \
    "    KaitaiStruct(filename=str)"                                            \
    "\n"                                                                        \
    "Where *text* is a string containg a markup content to parse; the"          \
    " *filename* argument is an alternative string for a path pointing to the"  \
    " same kind of content. This path can be a real filename or a resource"     \
    " URI."                                                                     \
    "\n"                                                                        \
    "It is the Python bindings for a C implementation of the specifications"    \
    " described at http://kaitai.io/."

    /* Récupération des paramètres */

    text = NULL;
    filename = NULL;

    ret = PyArg_ParseTupleAndKeywords(args, kwds, "|ss", kwlist, &text, &filename);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    kstruct = G_KAITAI_STRUCT(pygobject_get(self));

    if (text != NULL)
    {
        if (!g_kaitai_structure_create_from_text(kstruct, text))
        {
            PyErr_SetString(PyExc_ValueError, _("Unable to create Kaitai structure."));
            return -1;
        }

    }

    else if (filename != NULL)
    {
        if (!g_kaitai_structure_create_from_file(kstruct, filename))
        {
            PyErr_SetString(PyExc_ValueError, _("Unable to create Kaitai structure."));
            return -1;
        }

    }

    else
    {
        PyErr_SetString(PyExc_ValueError, _("Unable to create empty Kaitai structure."));
        return -1;
    }

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = instance de l'interpréteur Kaitai à manipuler.        *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Parcourt un contenu binaire selon une description Kaitai.    *
*                                                                             *
*  Retour      : Arborescence d'éléments rencontrés selon les spécifications. *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_kaitai_structure_parse(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinContent *content;                   /* Contenu binaire à traiter   */
    int ret;                                /* Bilan de lecture des args.  */
    GKaitaiStruct *kstruct;                 /* Interpréteur Kaitai courant */
    GMatchRecord *record;                   /* Ensemble de correspondances */

#define KAITAI_STRUCTURE_PARSE_METHOD PYTHON_METHOD_DEF                     \
(                                                                           \
    parse, "$self, content",                                                \
    METH_VARARGS, py_kaitai_structure,                                      \
    "Parse a binary content with the loaded specifications."                \
    "\n"                                                                    \
    "The content has to be a pychrysalide.analysis.BinContent instance.\n"  \
    "\n"                                                                    \
    "The result is *None* if the parsing failed, or a"                      \
    " pychrysalide.plugins.kaitai.MatchRecord object for each attribute"    \
    " met."                                                                 \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_binary_content, &content);
    if (!ret) return NULL;

    kstruct = G_KAITAI_STRUCT(pygobject_get(self));

    record = g_kaitai_structure_parse(kstruct, content);

    if (record != NULL)
    {
        result = pygobject_new(G_OBJECT(record));
        g_object_unref(G_OBJECT(record));
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
*  Description : Fournit la désignation humaine d'une définiton Kaitai.       *
*                                                                             *
*  Retour      : Intitulé de définition OU None.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_kaitai_structure_get_meta(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GKaitaiStruct *kstruct;                 /* Version native de l'objet   */
    GKaitaiMeta *meta;                      /* Informations à transmettre  */

#define KAITAI_STRUCTURE_META_ATTRIB PYTHON_GET_DEF_FULL            \
(                                                                   \
    meta, py_kaitai_structure,                                      \
    "Global description provided for the Kaitai definition, as a"   \
    " pychrysalide.plugins.kaitai.parsers.KaitaiMeta instance."     \
)

    kstruct = G_KAITAI_STRUCT(pygobject_get(self));

    meta = g_kaitai_structure_get_meta(kstruct);

    if (meta != NULL)
    {
        result = pygobject_new(G_OBJECT(meta));
        g_object_unref(G_OBJECT(meta));
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

PyTypeObject *get_python_kaitai_structure_type(void)
{
    static PyMethodDef py_kaitai_structure_methods[] = {
        KAITAI_STRUCTURE_PARSE_METHOD,
        { NULL }
    };

    static PyGetSetDef py_kaitai_structure_getseters[] = {
        KAITAI_STRUCTURE_META_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_kaitai_structure_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.plugins.kaitai.parsers.KaitaiStruct",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = KAITAI_STRUCT_DOC,

        .tp_methods     = py_kaitai_structure_methods,
        .tp_getset      = py_kaitai_structure_getseters,

        .tp_init        = py_kaitai_structure_init,
        .tp_new         = py_kaitai_structure_new

    };

    return &py_kaitai_structure_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.plugins...KaitaiStruct.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_kaitai_structure_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'KaitaiStruct'  */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_kaitai_structure_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.plugins.kaitai.parsers");

        dict = PyModule_GetDict(module);

        if (!ensure_python_kaitai_parser_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_KAITAI_STRUCT, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en structure de données Kaitai.           *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_kaitai_structure(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_kaitai_structure_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to Kaitai structure");
            break;

        case 1:
            *((GKaitaiStruct **)dst) = G_KAITAI_STRUCT(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
