
/* Chrysalide - Outil d'analyse de fichiers binaires
 * serialize.c - équivalent Python du fichier "analysis/storage/serialize.h"
 *
 * Copyright (C) 2020 Cyrille Bagard
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


#include "serialize.h"


#include <pygobject.h>


#include <analysis/storage/serialize-int.h>


#include "storage.h"
#include "../../access.h"
#include "../../helpers.h"
#include "../../common/packed.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Procède à l'initialisation de l'interface de génération. */
static void py_serializable_object_interface_init(GSerializableObjectIface *, gpointer *);

/* Charge un objet depuis une mémoire tampon. */
static bool py_serializable_object_load_wrapper(GSerializableObject *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un objet dans une mémoire tampon. */
static bool py_serializable_object_store_wrapper(const GSerializableObject *, GObjectStorage *, packed_buffer_t *);



/* ------------------------- CONNEXION AVEC L'API DE PYTHON ------------------------- */


/* Charge un objet depuis une mémoire tampon. */
static bool py_serializable_object_load(PyObject *, PyObject *);

/* Sauvegarde un objet dans une mémoire tampon. */
static bool py_serializable_object_store(PyObject *, PyObject *);



/* ---------------------------------------------------------------------------------- */
/*                          GLUE POUR CREATION DEPUIS PYTHON                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : iface  = interface GLib à initialiser.                       *
*                unused = adresse non utilisée ici.                           *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de génération.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_serializable_object_interface_init(GSerializableObjectIface *iface, gpointer *unused)
{

#define SERIALIZABLE_OBJECT_DOC                                             \
    "SerializableObject defines an interface used to store and load"        \
    " objects to and from a data buffer.\n"                                 \
    "\n"                                                                    \
    "A typical class declaration for a new implementation looks like:\n"    \
    "\n"                                                                    \
    "    class NewImplem(GObject.Object, SerializableObject):\n"            \
    "        ...\n"                                                         \
    "\n"                                                                    \
    "The following methods have to be defined for new implementations:\n"   \
    "* pychrysalide.analysis.storage.SerializableObject._load();\n"         \
    "* pychrysalide.analysis.storage.SerializableObject._store();\n"

    iface->load = py_serializable_object_load_wrapper;
    iface->store = py_serializable_object_store_wrapper;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : object  = instruction d'assemblage à consulter.              *
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à remplir.                             *
*                                                                             *
*  Description : Charge un objet depuis une mémoire tampon.                   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_serializable_object_load_wrapper(GSerializableObject *object, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *storage_obj;                  /* Objet Python à emmployer    */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */

#define SERIALIZABLE_OBJECT_LOAD_WRAPPER PYTHON_WRAPPER_DEF                     \
(                                                                               \
    _load, "$self, storage, pbuf, /",                                           \
    METH_VARARGS,                                                               \
    "Abstract method used to load an object definition from buffered data.\n"   \
    "\n"                                                                        \
    "The *storage* is a pychrysalide.analysis.storage.ObjectStorage instance"   \
    " provided to store inner objects, if relevant, or None. The *pbuf*"        \
    " argument points to a pychrysalide.common.PackedBuffer object containing"  \
    " the data to process.\n"                                                   \
    "\n"                                                                        \
    "The result is a boolean indicating the status of the operation."           \
)

    result = false;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(object));

    if (has_python_method(pyobj, "_load"))
    {
        if (storage == NULL)
        {
            storage_obj = Py_None;
            Py_INCREF(storage_obj);
        }
        else
            storage_obj = pygobject_new(G_OBJECT(storage));

        args = PyTuple_New(2);
        PyTuple_SetItem(args, 0, storage_obj);
        PyTuple_SetItem(args, 1, build_from_internal_packed_buffer(pbuf));

        pyret = run_python_method(pyobj, "_load", args);

        result = (pyret == Py_True ? true : false);

        Py_XDECREF(pyret);

        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : object  = instruction d'assemblage à consulter.              *
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à remplir.                             *
*                                                                             *
*  Description : Sauvegarde un objet dans une mémoire tampon.                 *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_serializable_object_store_wrapper(const GSerializableObject *object, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *storage_obj;                  /* Objet Python à emmployer    */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */

#define SERIALIZABLE_OBJECT_STORE_WRAPPER PYTHON_WRAPPER_DEF                    \
(                                                                               \
    _store, "$self, storage, pbuf, /",                                          \
    METH_VARARGS,                                                               \
    "Abstract method used to store an object definition into buffered data.\n"  \
    "\n"                                                                        \
    "The *storage* is a pychrysalide.analysis.storage.ObjectStorage instance"   \
    " provided to store inner objects, if relevant, or None. The *pbuf*"        \
    " argument points to a pychrysalide.common.PackedBuffer object containing"  \
    " the data to process.\n"                                                   \
    "\n"                                                                        \
    "The result is a boolean indicating the status of the operation."           \
)

    result = false;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(object));

    if (has_python_method(pyobj, "_store"))
    {
        if (storage == NULL)
        {
            storage_obj = Py_None;
            Py_INCREF(storage_obj);
        }
        else
            storage_obj = pygobject_new(G_OBJECT(storage));

        args = PyTuple_New(2);
        PyTuple_SetItem(args, 0, storage_obj);
        PyTuple_SetItem(args, 1, build_from_internal_packed_buffer(pbuf));

        pyret = run_python_method(pyobj, "_store", args);

        result = (pyret == Py_True ? true : false);

        Py_XDECREF(pyret);

        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                           CONNEXION AVEC L'API DE PYTHON                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un générateur à manipuler.        *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Charge un objet depuis une mémoire tampon.                   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_serializable_object_load(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    GObjectStorage *storage;                /* Conservateur à manipuler    */
    packed_buffer_t *pbuf;                  /* Tampon de données à employer*/
    int ret;                                /* Bilan de lecture des args.  */
    GSerializableObject *object;            /* Version native              */
    bool status;                            /* Bilan de l'opération        */

#define SERIALIZABLE_OBJECT_LOAD_METHOD PYTHON_METHOD_DEF                       \
(                                                                               \
    load, "$self, storage, pbuf, /",                                            \
    METH_VARARGS, py_serializable_object,                                       \
    "Load an object definition from buffered data.\n"                           \
    "\n"                                                                        \
    "The *storage* is a pychrysalide.analysis.storage.ObjectStorage instance"   \
    " provided to store inner objects, if relevant, or None. The *pbuf*"        \
    " argument points to a pychrysalide.common.PackedBuffer object containing"  \
    " the data to process.\n"                                                   \
    "\n"                                                                        \
    "The result is a boolean indicating the status of the operation."           \
)

    ret = PyArg_ParseTuple(args, "O&O&", convert_to_object_storage_or_none, &storage,
                           convert_to_packed_buffer, &pbuf);
    if (!ret) return NULL;

    object = G_SERIALIZABLE_OBJECT(pygobject_get(self));

    status = g_serializable_object_load(object, storage, pbuf);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un générateur à manipuler.        *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Sauvegarde un objet dans une mémoire tampon.                 *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_serializable_object_store(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    GObjectStorage *storage;                /* Conservateur à manipuler    */
    packed_buffer_t *pbuf;                  /* Tampon de données à employer*/
    int ret;                                /* Bilan de lecture des args.  */
    GSerializableObject *object;            /* Version native              */
    bool status;                            /* Bilan de l'opération        */

#define SERIALIZABLE_OBJECT_STORE_METHOD PYTHON_METHOD_DEF                      \
(                                                                               \
    store, "$self, storage, pbuf, /",                                           \
    METH_VARARGS, py_serializable_object,                                       \
    "Store an object definition into buffered data.\n"                          \
    "\n"                                                                        \
    "The *storage* is a pychrysalide.analysis.storage.ObjectStorage instance"   \
    " provided to store inner objects, if relevant, or None. The *pbuf*"        \
    " argument points to a pychrysalide.common.PackedBuffer object containing"  \
    " the data to process.\n"                                                   \
    "\n"                                                                        \
    "The result is a boolean indicating the status of the operation."           \
)

    ret = PyArg_ParseTuple(args, "O&O&", convert_to_object_storage_or_none, &storage,
                           convert_to_packed_buffer, &pbuf);
    if (!ret) return NULL;

    object = G_SERIALIZABLE_OBJECT(pygobject_get(self));

    status = g_serializable_object_store(object, storage, pbuf);

    result = status ? Py_True : Py_False;
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

PyTypeObject *get_python_serializable_object_type(void)
{
    static PyMethodDef py_serializable_object_methods[] = {
        SERIALIZABLE_OBJECT_LOAD_WRAPPER,
        SERIALIZABLE_OBJECT_STORE_WRAPPER,
        SERIALIZABLE_OBJECT_LOAD_METHOD,
        SERIALIZABLE_OBJECT_STORE_METHOD,
        { NULL }
    };

    static PyGetSetDef py_serializable_object_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_serializable_object_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.storage.SerializableObject",
        .tp_basicsize   = sizeof(PyObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = SERIALIZABLE_OBJECT_DOC,

        .tp_methods     = py_serializable_object_methods,
        .tp_getset      = py_serializable_object_getseters,

    };

    return &py_serializable_object_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide....SerializableObject'.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_serializable_object_is_registered(void)
{
    PyTypeObject *type;                     /* Type 'SerializableObject'   */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    static GInterfaceInfo info = {          /* Paramètres d'inscription    */

        .interface_init = (GInterfaceInitFunc)py_serializable_object_interface_init,
        .interface_finalize = NULL,
        .interface_data = NULL,

    };

    type = get_python_serializable_object_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.storage");

        dict = PyModule_GetDict(module);

        if (!register_interface_for_pygobject(dict, G_TYPE_SERIALIZABLE_OBJECT, type, &info))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en objet adapté à une mise en cache.      *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_serializable_object(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_serializable_object_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to serializable object");
            break;

        case 1:
            *((GSerializableObject **)dst) = G_SERIALIZABLE_OBJECT(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
