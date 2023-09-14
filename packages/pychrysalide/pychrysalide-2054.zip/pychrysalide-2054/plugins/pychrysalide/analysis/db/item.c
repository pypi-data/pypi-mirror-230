
/* Chrysalide - Outil d'analyse de fichiers binaires
 * item.c - équivalent Python du fichier "analysis/db/item.c"
 *
 * Copyright (C) 2018-2020 Cyrille Bagard
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


#include <malloc.h>
#include <pygobject.h>


#include <i18n.h>
#include <analysis/db/item.h>


#include "constants.h"
#include "../../access.h"
#include "../../helpers.h"



/* Ajoute une propriété à un élément de base de données. */
static PyObject *py_db_item_add_flag(PyObject *, PyObject *);

/* Retire une propriété à un élément de base de données. */
static PyObject *py_db_item_remove_flag(PyObject *, PyObject *);

/* Décrit l'élément de collection en place. */
static PyObject *py_db_item_get_label(PyObject *, void *);

/* Fournit l'horodatage associé à l'élément de collection. */
static PyObject *py_db_item_get_timestamp(PyObject *, void *);

/* Indique les propriétés particulières appliquées à l'élément. */
static PyObject *py_db_item_get_flags(PyObject *, void *);

/* Applique un ensemble de propriétés à un élément. */
static int py_db_item_set_flags(PyObject *, PyObject *, void *);



#define DB_ITEM_DOC                                                         \
    "DbItem handles all kinds of updates applied to the disassebled code."  \
    "\n"                                                                    \
    "These items are managed using a client/server model."                  \
    "\n"                                                                    \
    "See the pychrysalide.analysis.db.items package for a full list of"     \
    " existing items."



/******************************************************************************
*                                                                             *
*  Paramètres  : self = serveur à manipuler.                                  *
*                args = arguments d'appel non utilisés ici.                   *
*                                                                             *
*  Description : Ajoute une propriété à un élément de base de données.        *
*                                                                             *
*  Retour      : None.                                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_db_item_add_flag(PyObject *self, PyObject *args)
{
    unsigned int flag;                      /* Propriété à traiter         */
    int ret;                                /* Bilan de lecture des args.  */
    GDbItem *item;                          /* Elément à manipuler         */

#define DB_ITEM_ADD_FLAG_METHOD PYTHON_METHOD_DEF                   \
(                                                                   \
    add_flag, "$self, flag, /",                                     \
    METH_VARARGS, py_db_item,                                       \
    "Add a property to a database item."                            \
    "\n"                                                            \
    "This property is one of the values listed in the"              \
    " of pychrysalide.analysis.db.DbItem.DbItemFlags enumeration."  \
)

    ret = PyArg_ParseTuple(args, "I", &flag);
    if (!ret) return NULL;

    item = G_DB_ITEM(pygobject_get(self));

    g_db_item_add_flag(item, flag);

    Py_RETURN_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = serveur à manipuler.                                  *
*                args = arguments d'appel non utilisés ici.                   *
*                                                                             *
*  Description : Retire une propriété à un élément de base de données.        *
*                                                                             *
*  Retour      : None.                                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_db_item_remove_flag(PyObject *self, PyObject *args)
{
    unsigned int flag;                      /* Propriété à traiter         */
    int ret;                                /* Bilan de lecture des args.  */
    GDbItem *item;                          /* Elément à manipuler         */

#define DB_ITEM_REMOVE_FLAG_METHOD PYTHON_METHOD_DEF                \
(                                                                   \
    remove_flag, "$self, flag, /",                                  \
    METH_VARARGS, py_db_item,                                       \
    "Remove a property from a database item."                       \
    "\n"                                                            \
    "This property is one of the values listed in the"              \
    " of pychrysalide.analysis.db.DbItem.DbItemFlags enumeration."  \
)

    ret = PyArg_ParseTuple(args, "I", &flag);
    if (!ret) return NULL;

    item = G_DB_ITEM(pygobject_get(self));

    g_db_item_remove_flag(item, flag);

    Py_RETURN_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Décrit l'élément de collection en place.                     *
*                                                                             *
*  Retour      : Chaîne de caractère correspondante.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_db_item_get_label(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GDbItem *item;                          /* Elément à consulter         */
    char *label;                            /* Etiquette de représentation */

#define DB_ITEM_LABEL_ATTRIB PYTHON_GET_DEF_FULL            \
(                                                           \
    label, py_db_item,                                      \
    "String describing the effect of the database item."    \
)

    item = G_DB_ITEM(pygobject_get(self));

    label = g_db_item_get_label(item);

    result = PyUnicode_FromString(label);

    free(label);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit l'horodatage associé à l'élément de collection.      *
*                                                                             *
*  Retour      : Date de création de l'élément.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_db_item_get_timestamp(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GDbItem *item;                          /* Elément à consulter         */
    timestamp_t timestamp;                  /* Horodatage de l'élément     */

#define DB_ITEM_TIMESTAMP_ATTRIB PYTHON_GET_DEF_FULL    \
(                                                       \
    timestamp, py_db_item,                              \
    "Timestamp of the item creation."                   \
)

    item = G_DB_ITEM(pygobject_get(self));

    timestamp = g_db_item_get_timestamp(item);

    result = PyLong_FromUnsignedLongLong(timestamp);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique les propriétés particulières appliquées à l'élément. *
*                                                                             *
*  Retour      : Propriétés actives de l'élément.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_db_item_get_flags(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GDbItem *item;                          /* Elément à consulter         */
    DbItemFlags flags;                      /* Propriétés de l'élément     */

#define DB_ITEM_FLAGS_ATTRIB PYTHON_GETSET_DEF_FULL             \
(                                                               \
    flags, py_db_item,                                          \
    "Properties of the database item, provided as a mask"       \
    " of pychrysalide.analysis.db.DbItem.DbItemFlags values."   \
)

    item = G_DB_ITEM(pygobject_get(self));

    flags = g_db_item_get_flags(item);

    result = cast_with_constants_group_from_type(get_python_db_item_type(), "DbItemFlags", flags);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Applique un ensemble de propriétés à un élément.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_db_item_set_flags(PyObject *self, PyObject *value, void *closure)
{
    GDbItem *item;                          /* Elément à consulter         */
    DbItemFlags flags;                      /* Propriétés d'élément        */

    if (!PyLong_Check(value))
        return -1;

    item = G_DB_ITEM(pygobject_get(self));

    flags = PyLong_AsUnsignedLong(value);

    g_db_item_set_flags(item, flags);

    return 0;

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

PyTypeObject *get_python_db_item_type(void)
{
    static PyMethodDef py_db_item_methods[] = {
        DB_ITEM_ADD_FLAG_METHOD,
        DB_ITEM_REMOVE_FLAG_METHOD,
        { NULL }
    };

    static PyGetSetDef py_db_item_getseters[] = {
        DB_ITEM_LABEL_ATTRIB,
        DB_ITEM_TIMESTAMP_ATTRIB,
        DB_ITEM_FLAGS_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_db_item_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.db.DbItem",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = DB_ITEM_DOC,

        .tp_methods     = py_db_item_methods,
        .tp_getset      = py_db_item_getseters,

    };

    return &py_db_item_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide....db.items.DbItem'.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_db_item_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'DbItem'        */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_db_item_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.db");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_DB_ITEM, type))
            return false;

        if (!define_db_protocol_constants(type))
            return false;

        if (!define_db_item_constants(type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en élément pour base de données.          *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_db_item(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_db_item_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to database item");
            break;

        case 1:
            *((GDbItem **)dst) = G_DB_ITEM(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
