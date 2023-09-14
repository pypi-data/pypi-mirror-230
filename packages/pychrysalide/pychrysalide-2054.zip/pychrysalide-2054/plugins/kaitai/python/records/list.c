
/* Chrysalide - Outil d'analyse de fichiers binaires
 * list.h - équivalent Python du fichier "plugins/kaitai/parsers/list.h"
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


#include "list.h"


#include <pygobject.h>
#include <string.h>


#include <i18n.h>
#include <plugins/pychrysalide/access.h>
#include <plugins/pychrysalide/helpers.h>
#include <plugins/pychrysalide/analysis/content.h>
#include <plugins/pychrysalide/arch/vmpa.h>
#include <plugins/yaml/python/node.h>


#include "../record.h"
#include "../parsers/attribute.h"
#include "../../records/list-int.h"



CREATE_DYN_CONSTRUCTOR(record_list, G_TYPE_RECORD_LIST);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_record_list_init(PyObject *, PyObject *, PyObject *);

/* Dénombre le nombre de correspondances enregistrées. */
static Py_ssize_t py_record_list_sq_length(PyObject *);

/* Fournit un élément ciblé dans la liste de correspondances. */
static PyObject *py_record_list_sq_item(PyObject *, Py_ssize_t);



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

static int py_record_list_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    int result;                             /* Bilan à retourner           */
    GKaitaiAttribute *attrib;               /* Attribut défini créateur    */
    GBinContent *content;                   /* Contenu binaire analysé     */
    vmpa2t *addr;                           /* Adresse de symbole à ajouter*/
    int ret;                                /* Bilan de lecture des args.  */
    GRecordList *list;                      /* Création GLib à transmettre */

#define RECORD_LIST_DOC                                                         \
    "The RecordList class collects a list of parsed attributes with their"      \
    " relative values. Each of theses Kaitai attributes can be accessed as"     \
    " subscriptable Python attribute.\n"                                        \
    "\n"                                                                        \
    "Instances can be created using the following constructor:\n"               \
    "\n"                                                                        \
    "    RecordList(content, attrib)"                                           \
    "\n"                                                                        \
    "Where the *attrib* argument refers to the"                                 \
    " pychrysalide.plugins.kaitai.parsers.KaitaiAttribute instance used to"     \
    " create each record contained by the list and *content* points to a"       \
    " pychrysalide.analysis.BinContent instance."

    result = 0;

    /* Récupération des paramètres */

    ret = PyArg_ParseTuple(args, "O&O&",
                           convert_to_kaitai_attribute, &attrib,
                           convert_to_binary_content, &content,
                           convert_any_to_vmpa, &addr);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1)
    {
        result = -1;
        goto exit;
    }

    /* Eléments de base */

    list = G_RECORD_LIST(pygobject_get(self));

    if (!g_record_list_create(list, attrib, content, addr))
    {
        PyErr_SetString(PyExc_ValueError, _("Unable to create record list."));
        result = -1;
        goto exit;
    }

 exit:

    clean_vmpa_arg(addr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = instance Python manipulée.                            *
*                                                                             *
*  Description : Dénombre le nombre de correspondances enregistrées.          *
*                                                                             *
*  Retour      : Taille de la liste représentée.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static Py_ssize_t py_record_list_sq_length(PyObject *self)
{
    Py_ssize_t result;                      /* Quantité à retourner        */
    GRecordList *list;                      /* Version native de l'objet   */

    list = G_RECORD_LIST(pygobject_get(self));

    result = g_record_list_count_records(list);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = structure C convertie en Python.                      *
*                index = indice de la correspondance visée.                   *
*                                                                             *
*  Description : Fournit un élément ciblé dans la liste de correspondances.   *
*                                                                             *
*  Retour      : Instance de correspondance particulière, voire None.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_record_list_sq_item(PyObject *self, Py_ssize_t index)
{
    PyObject *result;                       /* Instance à retourner        */
    GRecordList *list;                      /* Version native de l'objet   */
    GMatchRecord *record;                   /* Correspondance retrouvée    */

    list = G_RECORD_LIST(pygobject_get(self));

    record = g_record_list_get_record(list, index);

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
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Fournit un accès à une définition de type à diffuser.        *
*                                                                             *
*  Retour      : Définition d'objet pour Python.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyTypeObject *get_python_record_list_type(void)
{
    static PySequenceMethods py_record_list_sequence_methods = {

        .sq_length = py_record_list_sq_length,
        .sq_item   = py_record_list_sq_item,

    };

    static PyMethodDef py_record_list_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_record_list_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_record_list_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.plugins.kaitai.records.RecordList",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_as_sequence = &py_record_list_sequence_methods,

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = RECORD_LIST_DOC,

        .tp_methods     = py_record_list_methods,
        .tp_getset      = py_record_list_getseters,

        .tp_init        = py_record_list_init,
        .tp_new         = py_record_list_new,

    };

    return &py_record_list_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide....records.RecordList. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_record_list_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'RecordList'    */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_record_list_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.plugins.kaitai.records");

        dict = PyModule_GetDict(module);

        if (!ensure_python_match_record_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_RECORD_LIST, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en correspondance attribut/binaire.       *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_record_list(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_record_list_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to record list");
            break;

        case 1:
            *((GRecordList **)dst) = G_RECORD_LIST(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
