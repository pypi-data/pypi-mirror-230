
/* Chrysalide - Outil d'analyse de fichiers binaires
 * binary.c - équivalent Python du fichier "analysis/binary.h"
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


#include "binary.h"


#include <malloc.h>
#include <pygobject.h>


#include <i18n.h>


#include <analysis/binary.h>


#include "loaded.h"
#include "../access.h"
#include "../helpers.h"
#include "../format/executable.h"
#include "db/item.h"



/* Crée un nouvel objet Python de type 'LoadedBinary'. */
static PyObject *py_loaded_binary_new(PyTypeObject *, PyObject *, PyObject *);

/* Fournit un client assurant la liaison avec un serveur. */
static PyObject *py_loaded_binary_get_client(PyObject *, PyObject *);

/* Trouve une collection assurant une fonctionnalité donnée. */
static PyObject *py_loaded_binary_find_collection(PyObject *, PyObject *);

/* Demande l'intégration d'une modification dans une collection. */
static PyObject *py_loaded_binary_add_to_collection(PyObject *, PyObject *);

/* Active les éléments en amont d'un horodatage donné. */
static PyObject *py_loaded_binary_set_last_active(PyObject *, PyObject *);

/* Fournit l'ensemble des collections utilisées par un binaire. */
static PyObject *py_loaded_binary_get_collections(PyObject *, void *);

/* Fournit le format de fichier reconnu dans le contenu binaire. */
static PyObject *py_loaded_binary_get_format(PyObject *, void *);

/* Fournit le processeur de l'architecture liée au binaire. */
static PyObject *py_loaded_binary_get_processor(PyObject *, void *);

/* Fournit le tampon associé au contenu assembleur d'un binaire. */
static PyObject *py_loaded_binary_get_disassembly_cache(PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de l'objet à instancier.                         *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Crée un nouvel objet Python de type 'LoadedBinary'.          *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_loaded_binary_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Instance à retourner        */
    GExeFormat *format;                     /* Instance GLib correspondante*/
    int ret;                                /* Bilan de lecture des args.  */
    GLoadedContent *binary;                 /* Version GLib du binaire     */

    ret = PyArg_ParseTuple(args, "O&", convert_to_executable_format, &format);
    if (!ret) return NULL;

    g_object_ref(G_OBJECT(format));
    binary = g_loaded_binary_new(format);

    result = pygobject_new(G_OBJECT(binary));

    g_object_unref(binary);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet représentant un binaire chargé.                 *
*                args = arguments fournis pour l'opération.                   *
*                                                                             *
*  Description : Fournit un client assurant la liaison avec un serveur.       *
*                                                                             *
*  Retour      : Client connecté ou None.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_loaded_binary_get_client(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    GLoadedBinary *binary;                  /* Binaire en cours d'analyse  */
    GAnalystClient *client;                 /* Eventuel client en place    */

#define LOADED_BINARY_GET_CLIENT_METHOD PYTHON_METHOD_DEF               \
(                                                                       \
    get_client, "$self",                                                \
    METH_NOARGS, py_loaded_binary,                                      \
    "Provide the client connected to an internal or remote server"      \
    " if defined, or return None otherwise.\n"                          \
    "\n"                                                                \
    "The returned object is a pychrysalide.analysis.db.AnalystClient"   \
    " instance or *None*."                                              \
)

    binary = G_LOADED_BINARY(pygobject_get(self));

    client = g_loaded_binary_get_client(binary);

    if (client != NULL)
    {
        result = pygobject_new(G_OBJECT(client));
        g_object_unref(G_OBJECT(client));
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
*  Paramètres  : self = objet représentant un binaire chargé.                 *
*                args = arguments fournis pour l'opération.                   *
*                                                                             *
*  Description : Trouve une collection assurant une fonctionnalité donnée.    *
*                                                                             *
*  Retour      : Collection trouvée ou None.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_loaded_binary_find_collection(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    unsigned int feature;                   /* Fonctionnalité recherchée   */
    int ret;                                /* Bilan de lecture des args.  */
    GLoadedBinary *binary;                  /* Binaire en cours d'analyse  */
    GDbCollection *found;                   /* Collection trouvée          */

#define LOADED_BINARY_FIND_COLLECTION_METHOD PYTHON_METHOD_DEF                      \
(                                                                                   \
    find_collection, "$self, feature, /",                                           \
    METH_VARARGS, py_loaded_binary,                                                 \
    "Provide the collection managing a given database feature."                     \
    "\n"                                                                            \
    "The feature is a value of type pychrysalide.analysis.db.DbItem.DbItemFlags."   \
)

    ret = PyArg_ParseTuple(args, "I", &feature);
    if (!ret) return NULL;

    binary = G_LOADED_BINARY(pygobject_get(self));

    found = g_loaded_binary_find_collection(binary, feature);

    if (found != NULL)
    {
        result = pygobject_new(G_OBJECT(found));
        g_object_unref(G_OBJECT(found));
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
*  Paramètres  : self = objet représentant un binaire chargé.                 *
*                args = arguments fournis pour l'opération.                   *
*                                                                             *
*  Description : Demande l'intégration d'une modification dans une collection.*
*                                                                             *
*  Retour      : Bilan partiel de l'opération demandée.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_loaded_binary_add_to_collection(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    GDbItem *item;                          /* Elément à intégrer          */
    int ret;                                /* Bilan de lecture des args.  */
    GLoadedBinary *binary;                  /* Binaire en cours d'analyse  */
    bool status;                            /* Bilan de l'opération        */

#define LOADED_BINARY_ADD_TO_COLLECTION_METHOD PYTHON_METHOD_DEF            \
(                                                                           \
    add_to_collection, "$self, item, /",                                    \
    METH_VARARGS, py_loaded_binary,                                         \
    "Ask a server to include the given item into the update database."      \
    "\n"                                                                    \
    "The server type (internal or remote) depends on the collection type"   \
    " linked to the item and the user configuration."                       \
    "\n"                                                                    \
    "The item has to be a subclass of pychrysalide.analysis.db.DbItem."     \
    "\n"                                                                    \
    "The method returns True if the item has been successfully forwarded"   \
    " to a server, False otherwise."                                        \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_db_item, &item);
    if (!ret) return NULL;

    binary = G_LOADED_BINARY(pygobject_get(self));

    g_object_ref(G_OBJECT(item));

    status = g_loaded_binary_add_to_collection(binary, item);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = binaire chargé à manipuler.                           *
*                args = arguments d'appel à consulter.                        *
*                                                                             *
*  Description : Active les éléments en amont d'un horodatage donné.          *
*                                                                             *
*  Retour      : True si la commande a bien été envoyée, False sinon.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_loaded_binary_set_last_active(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    unsigned long long timestamp;           /* Horodatage de limite        */
    int ret;                                /* Bilan de lecture des args.  */
    GLoadedBinary *binary;                  /* Binaire en cours d'analyse  */
    bool status;                            /* Bilan de l'opération        */

#define LOADED_BINARY_SET_LAST_ACTIVE_METHOD PYTHON_METHOD_DEF          \
(                                                                       \
    set_last_active, "$self, timestamp, /",                             \
    METH_VARARGS, py_loaded_binary,                                     \
    "Define the timestamp of the last active item in the collection"    \
    " and returns the status of the request transmission."              \
)

    ret = PyArg_ParseTuple(args, "K", &timestamp);
    if (!ret) return NULL;

    binary = G_LOADED_BINARY(pygobject_get(self));

    status = g_loaded_binary_set_last_active(binary, timestamp);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit l'ensemble des collections utilisées par un binaire. *
*                                                                             *
*  Retour      : Liste de collections en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_loaded_binary_get_collections(PyObject *self, void *closure)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    GLoadedBinary *binary;                  /* Version native              */
    size_t count;                           /* Quantité de collections     */
    GDbCollection **collections;            /* Ensemble de collections     */
    size_t i;                               /* Boucle de parcours          */

#define LOADED_BINARY_COLLECTIONS_ATTRIB PYTHON_GET_DEF_FULL            \
(                                                                       \
    collections, py_loaded_binary,                                      \
    "List of all collections of database items linked to the binary."   \
)

    binary = G_LOADED_BINARY(pygobject_get(self));

    collections = g_loaded_binary_get_collections(binary, &count);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
        PyTuple_SetItem(result, i, pygobject_new(G_OBJECT(collections[i])));
        g_object_unref(G_OBJECT(collections[i]));
    }

    if (collections != NULL)
        free(collections);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le format de fichier reconnu dans le contenu binaire.*
*                                                                             *
*  Retour      : Instance du format reconnu.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_loaded_binary_get_format(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    GLoadedBinary *binary;                  /* Binaire en cours d'analyse  */
    GExeFormat *format;                     /* Format du binaire lié       */

    binary = G_LOADED_BINARY(pygobject_get(self));
    format = g_loaded_binary_get_format(binary);

    result = pygobject_new(G_OBJECT(format));

    g_object_unref(G_OBJECT(format));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le processeur de l'architecture liée au binaire.     *
*                                                                             *
*  Retour      : Instance du processeur associé.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_loaded_binary_get_processor(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    GLoadedBinary *binary;                  /* Binaire en cours d'analyse  */
    GArchProcessor *proc;                   /* Architecture visée          */

    binary = G_LOADED_BINARY(pygobject_get(self));
    proc = g_loaded_binary_get_processor(binary);

    if (proc != NULL)
    {
        result = pygobject_new(G_OBJECT(proc));
        g_object_unref(G_OBJECT(proc));
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
*  Paramètres  : self    = classe représentant une instruction.               *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Fournit le tampon associé au contenu assembleur d'un binaire.*
*                                                                             *
*  Retour      : Valeur associée à la propriété consultée.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_loaded_binary_get_disassembly_cache(PyObject *self, void *closure)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    GLoadedBinary *binary;                  /* Version native              */
    GBufferCache *cache;                    /* Tampon à récupérer          */

#define LOADED_BINARY_DISASSEMBLY_CACHE_ATTRIB PYTHON_GET_DEF_FULL      \
(                                                                       \
    disassembly_cache, py_loaded_binary,                                \
    "Give access to the disassembly graphical cache, which is a"        \
    " pychrysalide.glibext.BufferCache instance or None.\n"             \
    "\n"                                                                \
    "In graphical mode, the cache is built by default. Otherwise, the"  \
    " build depends on the *cache* argument provided at the analysis"   \
    " call (please refer to the pychrysalide.analysis.LoadedContent"    \
    " interface for more information about this kind of call)."         \
)

    binary = G_LOADED_BINARY(pygobject_get(self));
    cache = g_loaded_binary_get_disassembly_cache(binary);

    if (cache != NULL)
    {
        result = pygobject_new(G_OBJECT(cache));
        g_object_unref(G_OBJECT(cache));
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

PyTypeObject *get_python_loaded_binary_type(void)
{
    static PyMethodDef py_loaded_binary_methods[] = {
        LOADED_BINARY_GET_CLIENT_METHOD,
        LOADED_BINARY_FIND_COLLECTION_METHOD,
        LOADED_BINARY_ADD_TO_COLLECTION_METHOD,
        LOADED_BINARY_SET_LAST_ACTIVE_METHOD,
        { NULL }
    };

    static PyGetSetDef py_loaded_binary_getseters[] = {
        LOADED_BINARY_COLLECTIONS_ATTRIB,
        {
            "format", py_loaded_binary_get_format, NULL,
            "File format recognized in the binary content.", NULL
        },
        {
            "processor", py_loaded_binary_get_processor, NULL,
            "Handler for the current binary processor.", NULL
        },
        LOADED_BINARY_DISASSEMBLY_CACHE_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_loaded_binary_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.LoadedBinary",

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = "PyChrysalide loaded binary",

        .tp_methods     = py_loaded_binary_methods,
        .tp_getset      = py_loaded_binary_getseters,
        .tp_new         = py_loaded_binary_new

    };

    return &py_loaded_binary_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.analysis.LoadedBinary'.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_loaded_binary_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'LoadedBinary'  */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_loaded_binary_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis");

        dict = PyModule_GetDict(module);

        if (!ensure_python_loaded_content_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_LOADED_BINARY, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en ensemble de binaire chargé.            *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_loaded_binary(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_loaded_binary_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to loaded binary");
            break;

        case 1:
            *((GLoadedBinary **)dst) = G_LOADED_BINARY(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
