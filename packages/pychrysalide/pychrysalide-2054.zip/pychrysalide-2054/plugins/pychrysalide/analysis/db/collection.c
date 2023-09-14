
/* Chrysalide - Outil d'analyse de fichiers binaires
 * collection.c - équivalent Python du fichier "analysis/db/collection.c"
 *
 * Copyright (C) 2018-2019 Cyrille Bagard
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
#include <analysis/db/collection.h>


#include "../../access.h"
#include "../../helpers.h"



/* Renvoie la liste des éléments rassemblés. */
static PyObject *py_db_collection_get_items(PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Renvoie la liste des éléments rassemblés.                    *
*                                                                             *
*  Retour      : Liste d'éléments à parcourir.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_db_collection_get_items(PyObject *self, void *closure)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    GDbCollection *collec;                  /* Version native              */
    size_t count;                           /* Décompte des éléments       */
    GDbItem **items;                        /* Eléments déjà en place      */
    size_t i;                               /* Boucle de parcours          */

#define DB_COLLECTION_ITEMS_ATTRIB PYTHON_GET_DEF_FULL      \
(                                                           \
    items, py_db_collection,                                \
    "List of all items contained in the collection."        \
    "\n"                                                    \
    "These items can currently be applied or not."          \
)

    collec = G_DB_COLLECTION(pygobject_get(self));

    g_db_collection_rlock(collec);

    items = g_db_collection_get_items(G_DB_COLLECTION(collec), &count);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
        PyTuple_SetItem(result, i, pygobject_new(G_OBJECT(items[i])));
        g_object_unref(G_OBJECT(items[i]));
    }

    if (items != NULL)
        free(items);

    g_db_collection_runlock(collec);

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

PyTypeObject *get_python_db_collection_type(void)
{
    static PyMethodDef py_db_collection_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_db_collection_getseters[] = {
        DB_COLLECTION_ITEMS_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_db_collection_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.db.DbCollection",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = "PyChrysalide collection for DataBase collection",

        .tp_methods     = py_db_collection_methods,
        .tp_getset      = py_db_collection_getseters,

    };

    return &py_db_collection_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide....db.DbCollection'.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_db_collection_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'DbCollection'  */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_db_collection_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.db");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_DB_COLLECTION, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en collection de traitements sur binaire. *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_db_collection(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_db_collection_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to DB collection");
            break;

        case 1:
            *((GDbCollection **)dst) = G_DB_COLLECTION(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
