
/* Chrysalide - Outil d'analyse de fichiers binaires
 * container.c - équivalent Python du fichier "analysis/storage/container.h"
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


#include "container.h"


#include <pygobject.h>


#include <analysis/storage/container-int.h>


#include "../../access.h"
#include "../../helpers.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Procède à l'initialisation de l'interface de génération. */
static void py_cache_container_interface_init(GCacheContainerIface *, gpointer *);

/* Contrôle l'accès au contenu d'un conteneur. */
static void py_cache_container_lock_unlock_wrapper(GCacheContainer *, bool);

/* Indique si le contenu d'un conteneur peut être mis en cache. */
static bool py_cache_container_can_store_wrapper(GCacheContainer *);



/* ------------------------- CONNEXION AVEC L'API DE PYTHON ------------------------- */


/* Contrôle l'accès au contenu d'un conteneur. */
static bool py_cache_container_lock_unlock(PyObject *, PyObject *);

/* Indique si le contenu d'un conteneur peut être mis en cache. */
static bool py_cache_container_can_store(PyObject *, PyObject *);



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

static void py_cache_container_interface_init(GCacheContainerIface *iface, gpointer *unused)
{

#define CACHE_CONTAINER_DOC                                                 \
    "CacheContainer defines an interface for objects with content allowed"  \
    " to get cached.\n"                                                     \
    "\n"                                                                    \
    "A typical class declaration for a new implementation looks like:\n"    \
    "\n"                                                                    \
    "    class NewImplem(GObject.Object, CacheContainer):\n"                \
    "        ...\n"                                                         \
    "\n"                                                                    \
    "The following methods have to be defined for new implementations:\n"   \
    "* pychrysalide.analysis.storage.CacheContainer._lock_unlock();\n"      \
    "* pychrysalide.analysis.storage.CacheContainer._can_store();\n"

    iface->lock_unlock = py_cache_container_lock_unlock_wrapper;
    iface->can_store = py_cache_container_can_store_wrapper;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : container = conteneur à manipuler.                           *
*                lock      = indique une demande de verrou.                   *
*                                                                             *
*  Description : Contrôle l'accès au contenu d'un conteneur.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_cache_container_lock_unlock_wrapper(GCacheContainer *container, bool lock)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *lock_obj;                     /* Objet Python à emmployer    */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */

#define CACHE_CONTAINER_LOCK_UNLOCK_WRAPPER PYTHON_WRAPPER_DEF              \
(                                                                           \
    _lock_unlock, "$self, lock, /",                                         \
    METH_VARARGS,                                                           \
    "Abstract method used to lock or to unlock access to cache container"   \
    " internals.\n"                                                         \
    "\n"                                                                    \
    "The content of such a cache can then be accessed safely, without the"  \
    " fear of race condition while processing.\n"                           \
    "\n"                                                                    \
    "The *lock* argument is a boolean value indicating the state to"        \
    " achieve."                                                             \
)

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(container));

    if (has_python_method(pyobj, "_lock_unlock"))
    {
        lock_obj = lock ? Py_True : Py_False;
        Py_INCREF(lock_obj);

        args = PyTuple_New(1);
        PyTuple_SetItem(args, 0, lock_obj);

        pyret = run_python_method(pyobj, "_lock_unlock", args);

        Py_XDECREF(pyret);

        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : container = conteneur à consulter.                           *
*                                                                             *
*  Description : Indique si le contenu d'un conteneur peut être mis en cache. *
*                                                                             *
*  Retour      : Bilan de la consultation.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_cache_container_can_store_wrapper(GCacheContainer *container)
{
    bool result;                            /* Bilan à retourner           */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */

#define CACHE_CONTAINER_CAN_STORE_WRAPPER PYTHON_WRAPPER_DEF            \
(                                                                       \
    _can_store, "$self, /",                                             \
    METH_NOARGS,                                                        \
    "Abstract method used to define if a container can cache its"       \
    " content.\n"                                                       \
    "\n"                                                                \
    "This kind of operation is not wished if the content is currently"  \
    " in use.\n"                                                        \
    "\n"                                                                \
    "The result is a boolean indicating the capacity of safely"         \
    " building a cache."                                                \
)

    result = false;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(container));

    if (has_python_method(pyobj, "_can_store"))
    {
        pyret = run_python_method(pyobj, "_can_store", NULL);

        result = (pyret == Py_True ? true : false);

        Py_XDECREF(pyret);

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
*  Description : Contrôle l'accès au contenu d'un conteneur.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_cache_container_lock_unlock(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    int lock;                               /* Type de demande de verrou   */
    int ret;                                /* Bilan de lecture des args.  */
    GCacheContainer *object;                /* Version native              */

#define CACHE_CONTAINER_LOCK_UNLOCK_METHOD PYTHON_METHOD_DEF                \
(                                                                           \
    lock_unlock, "$self, lock, /",                                          \
    METH_VARARGS, py_cache_container,                                       \
    "Lock or unlock access to cache container internals.\n"                 \
    "\n"                                                                    \
    "The content of such a cache can then be accessed safely, without the"  \
    " fear of race condition while processing.\n"                           \
    "\n"                                                                    \
    "The *lock* argument is a boolean value indicating the state to"        \
    " achieve."                                                             \
)

    ret = PyArg_ParseTuple(args, "p", &lock);
    if (!ret) return NULL;

    object = G_CACHE_CONTAINER(pygobject_get(self));

    g_cache_container_lock_unlock(object, lock);

    result = Py_None;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un générateur à manipuler.        *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Indique si le contenu d'un conteneur peut être mis en cache. *
*                                                                             *
*  Retour      : Bilan de la consultation.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_cache_container_can_store(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    GCacheContainer *object;                /* Version native              */
    bool status;                            /* Bilan de l'opération        */

#define CACHE_CONTAINER_CAN_STORE_METHOD PYTHON_METHOD_DEF              \
(                                                                       \
    can_store, "$self, /",                                              \
    METH_NOARGS, py_cache_container,                                    \
    "Define if a container can cache its content.\n"                    \
    "\n"                                                                \
    "This kind of operation is not wished if the content is currently"  \
    " in use.\n"                                                        \
    "\n"                                                                \
    "The result is a boolean indicating the capacity of safely"         \
    " building a cache."                                                \
)

    object = G_CACHE_CONTAINER(pygobject_get(self));

    status = g_cache_container_can_store(object);

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

PyTypeObject *get_python_cache_container_type(void)
{
    static PyMethodDef py_cache_container_methods[] = {
        CACHE_CONTAINER_LOCK_UNLOCK_WRAPPER,
        CACHE_CONTAINER_CAN_STORE_WRAPPER,
        CACHE_CONTAINER_LOCK_UNLOCK_METHOD,
        CACHE_CONTAINER_CAN_STORE_METHOD,
        { NULL }
    };

    static PyGetSetDef py_cache_container_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_cache_container_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.storage.CacheContainer",
        .tp_basicsize   = sizeof(PyObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = CACHE_CONTAINER_DOC,

        .tp_methods     = py_cache_container_methods,
        .tp_getset      = py_cache_container_getseters,

    };

    return &py_cache_container_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide....CacheContainer'.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_cache_container_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'CacheContainer'*/
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    static GInterfaceInfo info = {          /* Paramètres d'inscription    */

        .interface_init = (GInterfaceInitFunc)py_cache_container_interface_init,
        .interface_finalize = NULL,
        .interface_data = NULL,

    };

    type = get_python_cache_container_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.storage");

        dict = PyModule_GetDict(module);

        if (!register_interface_for_pygobject(dict, G_TYPE_CACHE_CONTAINER, type, &info))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en conteneur d'objets entreposables.      *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_cache_container(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_cache_container_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to cache container");
            break;

        case 1:
            *((GCacheContainer **)dst) = G_CACHE_CONTAINER(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
