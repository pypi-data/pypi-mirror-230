
/* Chrysalide - Outil d'analyse de fichiers binaires
 * empty.c - équivalent Python du fichier "plugins/kaitai/parsers/empty.c"
 *
 * Copyright (C) 2023 Cyrille Bagard
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


#include "empty.h"


#include <assert.h>
#include <pygobject.h>


#include <i18n.h>
#include <plugins/pychrysalide/access.h>
#include <plugins/pychrysalide/helpers.h>
#include <plugins/pychrysalide/analysis/content.h>
#include <plugins/pychrysalide/arch/vmpa.h>


#include "../parser.h"
#include "../record.h"
#include "../../records/empty-int.h"



CREATE_DYN_CONSTRUCTOR(record_empty, G_TYPE_RECORD_EMPTY);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_record_empty_init(PyObject *, PyObject *, PyObject *);

/* Produit une absence de valeur pour la correspondance. */
static PyObject *py_record_empty_get_value(PyObject *, void *);



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

static int py_record_empty_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    GKaitaiParser *parser;                  /* Analyseur défini créateur   */
    GBinContent *content;                   /* Contenu binaire manipulé    */
    vmpa2t *pos;                            /* Tête de lecture courante    */
    int ret;                                /* Bilan de lecture des args.  */
    GRecordEmpty *empty;                    /* Création GLib à transmettre */

#define RECORD_EMPTY_DOC                                                        \
    "The RecordEmpty object reflects absolutely no match and should only get"   \
    " in some rare cases.\n"                                                    \
    "\n"                                                                        \
    "Instances can be created using following constructor:\n"                   \
    "\n"                                                                        \
    "    RecordEmpty(parser, content, pos)"                                     \
    "\n"                                                                        \
    "Where *parser* is the creator of the record, as a"                         \
    " pychrysalide.plugins.kaitai.KaitaiParser instance, *content* is a"        \
    " pychrysalide.analysis.BinContent instance providing the processed data"   \
    " and *pos* defines the current reading location, as a"                     \
    " pychrysalide.arch.vmpa value."

    /* Récupération des paramètres */

    ret = PyArg_ParseTuple(args, "O&O&O&",
                           convert_to_kaitai_parser, &parser,
                           convert_to_binary_content, &content,
                           convert_any_to_vmpa, &pos);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    empty = G_RECORD_EMPTY(pygobject_get(self));

    if (!g_record_empty_create(empty, parser, content, pos))
    {
        clean_vmpa_arg(pos);

        PyErr_SetString(PyExc_ValueError, _("Unable to create Kaitai stream."));
        return -1;

    }

    clean_vmpa_arg(pos);

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Produit une absence de valeur pour la correspondance.        *
*                                                                             *
*  Retour      : None.                                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_record_empty_get_value(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */

#define RECORD_EMPTY_VALUE_ATTRIB PYTHON_GET_DEF_FULL   \
(                                                       \
    value, py_record_empty,                             \
    "Always *None*.\n"                                  \
    "\n"                                                \
    "This attribute is only provided to mimic other"    \
    " record types."                                    \
)

    result = Py_None;
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

PyTypeObject *get_python_record_empty_type(void)
{
    static PyMethodDef py_record_empty_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_record_empty_getseters[] = {
        RECORD_EMPTY_VALUE_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_record_empty_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.plugins.kaitai.records.RecordEmpty",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = RECORD_EMPTY_DOC,

        .tp_methods     = py_record_empty_methods,
        .tp_getset      = py_record_empty_getseters,

        .tp_init        = py_record_empty_init,
        .tp_new         = py_record_empty_new,

    };

    return &py_record_empty_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide...records.RecordEmpty. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_record_empty_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'RecordEmpty'   */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_record_empty_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.plugins.kaitai.records");

        dict = PyModule_GetDict(module);

        if (!ensure_python_match_record_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_RECORD_EMPTY, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en zone de correspondance vide.           *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_record_empty(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_record_empty_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to record empty");
            break;

        case 1:
            *((GRecordEmpty **)dst) = G_RECORD_EMPTY(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
