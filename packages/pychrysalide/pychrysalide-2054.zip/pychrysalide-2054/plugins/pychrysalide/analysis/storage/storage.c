
/* Chrysalide - Outil d'analyse de fichiers binaires
 * storage.c - équivalent Python du fichier "analysis/storage/storage.c"
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


#include "storage.h"


#include <pygobject.h>


#include <analysis/storage/storage-int.h>
#include <plugins/dt.h>


#include "serialize.h"
#include "../../access.h"
#include "../../helpers.h"
#include "../../common/packed.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Accompagne la création d'une instance dérivée en Python. */
static PyObject *py_object_storage_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_object_storage_init(PyObject *, PyObject *, PyObject *);



/* -------------------------- TAMPON POUR CODE DESASSEMBLE -------------------------- */


/* Charge le support d'une conservation d'objets en place. */
static PyObject *py_object_storage_load(PyObject *, PyObject *);

/* Sauvegarde le support d'une conservation d'objets en place. */
static PyObject *py_object_storage_store(PyObject *, PyObject *);

/* Charge un objet à partir de données rassemblées. */
static PyObject *py_object_storage_load_object(PyObject *, PyObject *);

/* Charge un objet interne à partir de données rassemblées. */
static PyObject *py_object_storage_unpack_object(PyObject *, PyObject *);

/* Sauvegarde un object sous forme de données rassemblées. */
static PyObject *py_object_storage_store_object(PyObject *, PyObject *);

/* Sauvegarde un object interne sous forme de données. */
static PyObject *py_object_storage_pack_object(PyObject *, PyObject *);



/* ---------------------------------------------------------------------------------- */
/*                          GLUE POUR CREATION DEPUIS PYTHON                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type du nouvel objet à mettre en place.               *
*                args = éventuelle liste d'arguments.                         *
*                kwds = éventuel dictionnaire de valeurs mises à disposition. *
*                                                                             *
*  Description : Accompagne la création d'une instance dérivée en Python.     *
*                                                                             *
*  Retour      : Nouvel objet Python mis en place ou NULL en cas d'échec.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_object_storage_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

    /* Validations diverses */

    base = get_python_object_storage_type();

    if (type == base)
        goto simple_way;

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_OBJECT_STORAGE, type->tp_name, NULL, NULL, NULL);

    if (first_time)
    {
        status = register_class_for_dynamic_pygobject(gtype, type);

        if (!status)
        {
            result = NULL;
            goto exit;
        }

    }

    /* On crée, et on laisse ensuite la main à PyGObject_Type.tp_init() */

 simple_way:

    result = PyType_GenericNew(type, args, kwds);

 exit:

    return result;

}


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

static int py_object_storage_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    const char *hash;                       /* Empreinte de contenu        */
    int ret;                                /* Bilan de lecture des args.  */
    GObjectStorage *storage;                /* Mécanismes natifs           */

#define OBJECT_STORAGE_DOC                                              \
    "The ObjectStorage object manages the generic storage of GLib"      \
    " objects through serialization.\n"                                 \
    "\n"                                                                \
    "Instances can be created using the following constructor:\n"       \
    "\n"                                                                \
    "    ObjectStorage(hash)"                                           \
    "\n"                                                                \
    "Where *hash* should a string built from the checksum of the"       \
    " relative binary content linked to the storage.pychrysalide."

    /* Récupération des paramètres */

    ret = PyArg_ParseTuple(args, "s", &hash);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    storage = G_OBJECT_STORAGE(pygobject_get(self));

    storage->hash = strdup(hash);

    return 0;

}



/* ---------------------------------------------------------------------------------- */
/*                            TAMPON POUR CODE DESASSEMBLE                            */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant une mémorisation de types.        *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Charge le support d'une conservation d'objets en place.      *
*                                                                             *
*  Retour      : Gestionnaire de conservations construit ou None si erreur.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_object_storage_load(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Emplacement à retourner     */
    packed_buffer_t *pbuf;                  /* Tampon de données à employer*/
    int ret;                                /* Bilan de lecture des args.  */
    GObjectStorage *storage;                /* Mécanismes natifs           */

#define OBJECT_STORAGE_LOAD_METHOD PYTHON_METHOD_DEF                    \
(                                                                       \
    load, "pbuf, /",                                                    \
    METH_STATIC | METH_VARARGS, py_object_storage,                      \
    "Construct a new storage from a buffer.\n"                          \
    "\n"                                                                \
    "The *pbuf* has to be an instance of type"                          \
    " pychrysalide.common.PackedBuffer.\n"                              \
    "\n"                                                                \
    "The result is a new pychrysalide.analysis.storage.ObjectStorage"   \
    " object on success, *None* otherwise."                             \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_packed_buffer, &pbuf);
    if (!ret) return NULL;

    storage = g_object_storage_load(pbuf);

    if (storage == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }
    else
    {
        result = pygobject_new(G_OBJECT(storage));
        g_object_unref(G_OBJECT(storage));
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant une mémorisation de types.        *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Sauvegarde le support d'une conservation d'objets en place.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_object_storage_store(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Emplacement à retourner     */
    packed_buffer_t *pbuf;                  /* Tampon de données à employer*/
    int ret;                                /* Bilan de lecture des args.  */
    GObjectStorage *storage;                /* Mécanismes natifs           */
    bool status;                            /* Bilan de l'opération        */

#define OBJECT_STORAGE_STORE_METHOD PYTHON_METHOD_DEF       \
(                                                           \
    store, "$self, pbuf, /",                                \
    METH_VARARGS, py_object_storage,                        \
    "Save a storage into a buffer.\n"                       \
    "\n"                                                    \
    "The *pbuf* has to be an instance of type"              \
    " pychrysalide.common.PackedBuffer.\n"                  \
    "\n"                                                    \
    "The result is *True* on success, *False* otherwise."   \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_packed_buffer, &pbuf);
    if (!ret) return NULL;

    storage = G_OBJECT_STORAGE(pygobject_get(self));

    status = g_object_storage_store(storage, pbuf);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant une mémorisation de types.        *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Charge un objet à partir de données rassemblées.             *
*                                                                             *
*  Retour      : Objet restauré en mémoire ou None en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_object_storage_load_object(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    const char *name;                       /* Désignation de groupe       */
    unsigned long long pos;                 /* Emplacement des données     */
    int ret;                                /* Bilan de lecture des args.  */
    GObjectStorage *storage;                /* Mécanismes natifs           */
    GSerializableObject *object;            /* Objet reconstruit ou NULL   */

#define OBJECT_STORAGE_LOAD_OBJECT_METHOD PYTHON_METHOD_DEF             \
(                                                                       \
    load_object, "$self, name, pos, /",                                 \
    METH_VARARGS, py_object_storage,                                    \
    "Load an object from serialized data.\n"                            \
    "\n"                                                                \
    "The *name* is a string label for the group of target objects and"  \
    " *pos* is an offset into the data stream indicating the start of"  \
    " the data to unserialize.\n"                                       \
    "\n"                                                                \
    "The result is a pychrysalide.analysis.storage.SerializableObject"  \
    " instancet in case of success, or None in case of failure."        \
)

    ret = PyArg_ParseTuple(args, "sK", &name, &pos);
    if (!ret) return NULL;

    storage = G_OBJECT_STORAGE(pygobject_get(self));

    object = g_object_storage_load_object(storage, name, pos);

    if (object != NULL)
        result = pygobject_new(G_OBJECT(object));
    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant une mémorisation de types.        *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Charge un objet interne à partir de données rassemblées.     *
*                                                                             *
*  Retour      : Objet restauré en mémoire ou None en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_object_storage_unpack_object(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    const char *name;                       /* Désignation de groupe       */
    packed_buffer_t *pbuf;                  /* Tampon de données à employer*/
    int ret;                                /* Bilan de lecture des args.  */
    GObjectStorage *storage;                /* Mécanismes natifs           */
    GSerializableObject *object;            /* Objet reconstruit ou NULL   */

#define OBJECT_STORAGE_UNPACK_OBJECT_METHOD PYTHON_METHOD_DEF           \
(                                                                       \
    unpack_object, "$self, name, pbuf, /",                              \
    METH_VARARGS, py_object_storage,                                    \
    "Load an object from a buffer with a location pointing to data.\n"  \
    "\n"                                                                \
    "The *name* is a string label for the group of target objects and"  \
    " *pbuf* has to be a pychrysalide.common.PackedBuffer instance.\n"  \
    "\n"                                                                \
    "The result is a pychrysalide.analysis.storage.SerializableObject"  \
    " instancet in case of success, or None in case of failure."        \
)

    ret = PyArg_ParseTuple(args, "sO&", &name, convert_to_packed_buffer, &pbuf);
    if (!ret) return NULL;

    storage = G_OBJECT_STORAGE(pygobject_get(self));

    object = g_object_storage_unpack_object(storage, name, pbuf);

    if (object != NULL)
        result = pygobject_new(G_OBJECT(object));
    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant une mémorisation de types.        *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Sauvegarde un object sous forme de données rassemblées.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_object_storage_store_object(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Emplacement à retourner     */
    const char *name;                       /* Désignation de groupe       */
    GSerializableObject *object;            /* Objet à traiter             */
    int ret;                                /* Bilan de lecture des args.  */
    GObjectStorage *storage;                /* Mécanismes natifs           */
    off64_t pos;                            /* Emplacement d'enregistrement*/
    bool status;                            /* Bilan de l'opération        */

#define OBJECT_STORAGE_STORE_OBJECT_METHOD PYTHON_METHOD_DEF        \
(                                                                   \
    store_object, "$self, name, object, /",                         \
    METH_VARARGS, py_object_storage,                                \
    "Save an object as serialized data.\n"                          \
    "\n"                                                            \
    "The *name* is a string label for the group of target objects"  \
    " and the processed *object* has to be a"                       \
    " pychrysalide.analysis.storage.SerializableObject instance.\n" \
    "\n"                                                            \
    "The result is the position of the data for stored object,"     \
    " provided as an integer offset, in case of success or None"    \
    " in case of failure."                                          \
)

    ret = PyArg_ParseTuple(args, "sO&", &name, convert_to_serializable_object, &object);
    if (!ret) return NULL;

    storage = G_OBJECT_STORAGE(pygobject_get(self));

    status = g_object_storage_store_object(storage, name, object, &pos);

    if (status)
        result = PyLong_FromUnsignedLongLong((unsigned long long)pos);
    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant une mémorisation de types.        *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Sauvegarde un object interne sous forme de données.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_object_storage_pack_object(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Emplacement à retourner     */
    const char *name;                       /* Désignation de groupe       */
    GSerializableObject *object;            /* Objet à traiter             */
    packed_buffer_t *pbuf;                  /* Tampon de données à employer*/
    int ret;                                /* Bilan de lecture des args.  */
    GObjectStorage *storage;                /* Mécanismes natifs           */
    bool status;                            /* Bilan de l'opération        */

#define OBJECT_STORAGE_PACK_OBJECT_METHOD PYTHON_METHOD_DEF         \
(                                                                   \
    pack_object, "$self, name, object, pbuf/",                      \
    METH_VARARGS, py_object_storage,                                \
    "Save an object as serialized data and store the location of"   \
    " the data intro a buffer.\n"                                   \
    "\n"                                                            \
    "The *name* is a string label for the group of target objects," \
    " the processed *object* has to be a"                           \
    " pychrysalide.analysis.storage.SerializableObject instance"    \
    " and *pbuf* is expected to be a"                               \
    " pychrysalide.common.PackedBuffer instance.\n"                 \
    "\n"                                                            \
    "The status of the operation is returned as a boolean value:"   \
    " *True* for success, *False* for failure."                     \
)

    ret = PyArg_ParseTuple(args, "sO&O&", &name, convert_to_serializable_object, &object,
                           convert_to_packed_buffer, &pbuf);
    if (!ret) return NULL;

    storage = G_OBJECT_STORAGE(pygobject_get(self));

    status = g_object_storage_pack_object(storage, name, object, pbuf);

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

PyTypeObject *get_python_object_storage_type(void)
{
    static PyMethodDef py_object_storage_methods[] = {
        OBJECT_STORAGE_LOAD_METHOD,
        OBJECT_STORAGE_STORE_METHOD,
        OBJECT_STORAGE_LOAD_OBJECT_METHOD,
        OBJECT_STORAGE_UNPACK_OBJECT_METHOD,
        OBJECT_STORAGE_STORE_OBJECT_METHOD,
        OBJECT_STORAGE_PACK_OBJECT_METHOD,
        { NULL }
    };

    static PyGetSetDef py_object_storage_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_object_storage_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.storage.ObjectStorage",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = OBJECT_STORAGE_DOC,

        .tp_methods     = py_object_storage_methods,
        .tp_getset      = py_object_storage_getseters,

        .tp_init        = py_object_storage_init,
        .tp_new         = py_object_storage_new

    };

    return &py_object_storage_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide....ObjectStorage'.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_object_storage_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'ObjectStorage' */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_object_storage_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.storage");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_OBJECT_STORAGE, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en conservateur d'objets.                 *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_object_storage(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_object_storage_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to object storage");
            break;

        case 1:
            *((GObjectStorage **)dst) = G_OBJECT_STORAGE(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en conservateur d'objets ou NULL.         *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_object_storage_or_none(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    if (arg == Py_None)
    {
        *((GTypeMemory **)dst) = NULL;
        result = 1;
    }

    else
        result = convert_to_object_storage(arg, dst);

    return result;

}
