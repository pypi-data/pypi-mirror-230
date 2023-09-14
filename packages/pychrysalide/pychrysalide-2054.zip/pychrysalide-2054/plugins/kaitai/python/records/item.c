
/* Chrysalide - Outil d'analyse de fichiers binaires
 * item.h - équivalent Python du fichier "plugins/kaitai/parsers/item.h"
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


#include "item.h"


#include <assert.h>
#include <pygobject.h>


#include <i18n.h>
#include <plugins/pychrysalide/access.h>
#include <plugins/pychrysalide/helpers.h>
#include <plugins/pychrysalide/analysis/content.h>
#include <plugins/pychrysalide/arch/vmpa.h>
#include <plugins/yaml/python/node.h>


#include "../record.h"
#include "../parsers/attribute.h"
#include "../../records/item-int.h"



CREATE_DYN_CONSTRUCTOR(record_item, G_TYPE_RECORD_ITEM);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_record_item_init(PyObject *, PyObject *, PyObject *);

/* Lit la série d'octets d'un élément Kaitai entier représenté. */
static PyObject *py_record_item_get_truncated_bytes(PyObject *, void *);

/* Lit la valeur d'un élément Kaitai entier représenté. */
static PyObject *py_record_item_get_value(PyObject *, void *);



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

static int py_record_item_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    GKaitaiAttribute *attrib;               /* Attribut défini créateur    */
    GBinContent *content;                   /* Contenu binaire analysé     */
    mrange_t range;                         /* Espace couvert              */
    SourceEndian endian;                    /* Boutisme à observer         */
    int ret;                                /* Bilan de lecture des args.  */
    GRecordItem *item;                      /* Création GLib à transmettre */

#define RECORD_ITEM_DOC                                                         \
    "The RecordItem class remembers a match between a described attribute and"  \
    " its concret value read from parsed binary data."                          \
    "\n"                                                                        \
    "Instances can be created using the following constructor:\n"               \
    "\n"                                                                        \
    "    RecordItem(content, range, endian, attrib)"                            \
    "\n"                                                                        \
    "Where the *attrib* arguments refers to a"                                  \
    " pychrysalide.plugins.kaitai.parsers.KaitaiAttribute instance as the"      \
    " creator of the newly created object, *content* points to a"               \
    " pychrysalide.analysis.BinContent instance, *range* is a"                  \
    " pychrysalide.arch.mrange object, *endian* states with a"                  \
    " pychrysalide.analysis.BinContent.SourceEndian hint the endianness used"   \
    " to read integer values."

    /* Récupération des paramètres */

    ret = PyArg_ParseTuple(args, "O&O&O&",
                           convert_to_kaitai_attribute, &attrib,
                           convert_to_binary_content, &content,
                           convert_any_to_mrange, &range,
                           convert_to_binary_content, &endian);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    item = G_RECORD_ITEM(pygobject_get(self));

    if (!g_record_item_create(item, attrib, content, &range, endian))
    {
        PyErr_SetString(PyExc_ValueError, _("Unable to create record item."));
        return -1;
    }

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Lit la série d'octets d'un élément Kaitai entier représenté. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_record_item_get_truncated_bytes(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GRecordItem *item;                      /* Version native de l'élément */
    bool status;                            /* Bilan d'opération           */ 
    bin_t *out;                             /* Données brutes à transmettre*/
    size_t len;                             /* Quantité de ces données     */

#define RECORD_ITEM_TRUNCATED_BYTES_ATTRIB PYTHON_GET_DEF_FULL      \
(                                                                   \
    truncated_bytes, py_record_item,                                \
    "Raw bytes carried by the item (truncated if a separator"       \
    " is defined in the linked attribute), or None if irrelevant"   \
    " regarding to the type of the attribute."                      \
)

    item = G_RECORD_ITEM(pygobject_get(self));

    status = g_record_item_get_truncated_bytes(item, &out, &len);

    if (status)
    {
        result = PyBytes_FromStringAndSize((char *)out, len);
        free(out);
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
*  Description : Lit la valeur d'un élément Kaitai entier représenté.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_record_item_get_value(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GRecordItem *item;                      /* Version native de l'élément */
    resolved_value_t resolved;              /* Valeur sous forme générique */
    bool status;                            /* Bilan d'opération           */

#define RECORD_ITEM_VALUE_ATTRIB PYTHON_GET_DEF_FULL                \
(                                                                   \
    value, py_record_item,                                          \
    "Carried value (as integer, bytes), or None in case of error."  \
)

    result = NULL;

    item = G_RECORD_ITEM(pygobject_get(self));

    status = g_record_item_get_value(item, &resolved);

    if (status)
        switch (resolved.type)
        {
            case GVT_ERROR:
                assert(false);
                PyErr_Format(PyExc_RuntimeError,
                             _("Error got while parsing Kaitai definition should not have been exported!"));
                result = NULL;
                break;

            case GVT_UNSIGNED_INTEGER:
                result = PyLong_FromUnsignedLongLong(resolved.unsigned_integer);
                break;

            case GVT_SIGNED_INTEGER:
                result = PyLong_FromLongLong(resolved.signed_integer);
                break;

            case GVT_FLOAT:
                result = PyFloat_FromDouble(resolved.floating_number);
                break;

            case GVT_BOOLEAN:
                result = resolved.status ? Py_True : Py_False;
                Py_INCREF(result);
                break;

            case GVT_BYTES:
                result = PyBytes_FromStringAndSize(resolved.bytes.data, resolved.bytes.len);
                exit_szstr(&resolved.bytes);
                break;

            case GVT_ARRAY:
                result = pygobject_new(G_OBJECT(resolved.array));
                break;

            case GVT_RECORD:
                result = pygobject_new(G_OBJECT(resolved.record));
                break;

            case GVT_STREAM:
                result = pygobject_new(G_OBJECT(resolved.stream));
                break;

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

PyTypeObject *get_python_record_item_type(void)
{
    static PyMethodDef py_record_item_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_record_item_getseters[] = {
        RECORD_ITEM_TRUNCATED_BYTES_ATTRIB,
        RECORD_ITEM_VALUE_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_record_item_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.plugins.kaitai.records.RecordItem",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = RECORD_ITEM_DOC,

        .tp_methods     = py_record_item_methods,
        .tp_getset      = py_record_item_getseters,

        .tp_init        = py_record_item_init,
        .tp_new         = py_record_item_new,

    };

    return &py_record_item_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide....records.RecordItem. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_record_item_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'RecordItem'    */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_record_item_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.plugins.kaitai.records");

        dict = PyModule_GetDict(module);

        if (!ensure_python_match_record_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_RECORD_ITEM, type))
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

int convert_to_record_item(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_record_item_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to record item");
            break;

        case 1:
            *((GRecordItem **)dst) = G_RECORD_ITEM(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
