
/* Chrysalide - Outil d'analyse de fichiers binaires
 * cache.c - équivalent Python du fichier "analysis/storage/cache.c"
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


#include "cache.h"


#include <pygobject.h>


#include <analysis/storage/cache-int.h>
#include <plugins/dt.h>


#include "container.h"
#include "../loaded.h"
#include "../../access.h"
#include "../../helpers.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Accompagne la création d'une instance dérivée en Python. */
static PyObject *py_object_cache_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_object_cache_init(PyObject *, PyObject *, PyObject *);



/* -------------------------- TAMPON POUR CODE DESASSEMBLE -------------------------- */


/* Introduit un contenu dans un cache d'objets. */
static PyObject *py_object_cache_add(PyObject *, PyObject *);



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

static PyObject *py_object_cache_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

    /* Validations diverses */

    base = get_python_object_cache_type();

    if (type == base)
        goto simple_way;

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_OBJECT_CACHE, type->tp_name, NULL, NULL, NULL);

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

static int py_object_cache_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    GLoadedContent *loaded;                 /* Contenu chargé et traité    */
    int ret;                                /* Bilan de lecture des args.  */
    GObjectCache *cache;                /* Mécanismes natifs           */

#define OBJECT_CACHE_DOC                                                \
    "The ObjectCache object manages a cache built for reducing the"     \
    " overall memory footprint by releasing partial content of"         \
    " pychrysalide.analysis.storage.CacheContainer objects.\n"          \
    "\n"                                                                \
    "Disassembled instructions are the typical objects targeted by"     \
    " this feature, through serialization.\n"                           \
    "\n"                                                                \
    "Instances can be created using the following constructor:\n"       \
    "\n"                                                                \
    "    ObjectCache(loaded)"                                           \
    "\n"                                                                \
    "Where *loaded* is a pychrysalide.analysis.LoadedContent instance"  \
    " linked to the processed objects."

    /* Récupération des paramètres */

    ret = PyArg_ParseTuple(args, "O&", convert_to_loaded_content, &loaded);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    cache = G_OBJECT_CACHE(pygobject_get(self));

    if (!g_object_cache_open_for(cache, loaded))
        return -1;

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
*  Description : Introduit un contenu dans un cache d'objets.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_object_cache_add(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    GCacheContainer *container;             /* Conteneur à intégrer        */
    int ret;                                /* Bilan de lecture des args.  */
    GObjectCache *cache;                    /* Cache en version native     */

#define OBJECT_CACHE_ADD_METHOD PYTHON_METHOD_DEF               \
(                                                               \
    add, "$self, container, /",                                 \
    METH_VARARGS, py_object_cache,                              \
    "Introduce a new content to the object cache system.\n"     \
    "\n"                                                        \
    "The *container* object must implement the"                 \
    " pychrysalide.analysis.storage.CacheContainer interface."  \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_cache_container, &container);
    if (!ret) return NULL;

    cache = G_OBJECT_CACHE(pygobject_get(self));

    g_object_cache_add(cache, container);

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

PyTypeObject *get_python_object_cache_type(void)
{
    static PyMethodDef py_object_cache_methods[] = {
        OBJECT_CACHE_ADD_METHOD,
        { NULL }
    };

    static PyGetSetDef py_object_cache_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_object_cache_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.cache.ObjectCache",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = OBJECT_CACHE_DOC,

        .tp_methods     = py_object_cache_methods,
        .tp_getset      = py_object_cache_getseters,

        .tp_init        = py_object_cache_init,
        .tp_new         = py_object_cache_new

    };

    return &py_object_cache_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide....ObjectCache'.       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_object_cache_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'ObjectCache'   */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_object_cache_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.storage");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_OBJECT_CACHE, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en cache d'objets.                        *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_object_cache(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_object_cache_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to object cache");
            break;

        case 1:
            *((GObjectCache **)dst) = G_OBJECT_CACHE(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
