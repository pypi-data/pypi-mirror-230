
/* Chrysalide - Outil d'analyse de fichiers binaires
 * tpmem.c - équivalent Python du fichier "analysis/storage/tpmem.c"
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


#include "tpmem.h"


#include <pygobject.h>


#include <analysis/storage/tpmem.h>
#include <plugins/dt.h>


#include "../../access.h"
#include "../../helpers.h"
#include "../../common/packed.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Accompagne la création d'une instance dérivée en Python. */
static PyObject *py_type_memory_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_type_memory_init(PyObject *, PyObject *, PyObject *);



/* -------------------------- TAMPON POUR CODE DESASSEMBLE -------------------------- */


/* Apprend tous les types mémorisés dans un tampon. */
static PyObject *py_type_memory_load_types(PyObject *, PyObject *);

/* Crée une nouvelle instance d'objet à partir de son type. */
static PyObject *py_type_memory_create_object(PyObject *, PyObject *);

/* Sauvegarde le type d'un objet instancié. */
static PyObject *py_type_memory_store_object_gtype(PyObject *, PyObject *);

/* Enregistre tous les types mémorisés dans un tampon. */
static PyObject *py_type_memory_store_types(PyObject *, PyObject *);



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

static PyObject *py_type_memory_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

    /* Validations diverses */

    base = get_python_type_memory_type();

    if (type == base)
        goto simple_way;

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_TYPE_MEMORY, type->tp_name, NULL, NULL, NULL);

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

static int py_type_memory_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    int ret;                                /* Bilan de lecture des args.  */

#define TYPE_MEMORY_DOC                                             \
    "The TypeMemory remembers all the types of objects involved in" \
    " a serialization process.\n"                                   \
    "\n"                                                            \
    "Instances can be created using the following constructor:\n"   \
    "\n"                                                            \
    "    TypeMemory()"                                              \

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

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
*  Description : Apprend tous les types mémorisés dans un tampon.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_type_memory_load_types(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    packed_buffer_t *pbuf;                  /* Tampon à consulter          */
    int ret;                                /* Bilan de lecture des args.  */
    GTypeMemory *tpmem;                     /* Mémorisation native         */
    bool status;                            /* Bilan de l'opération        */

#define TYPE_MEMORY_LOAD_TYPES_METHOD PYTHON_METHOD_DEF         \
(                                                               \
    load_types, "$self, pbuf",                                  \
    METH_VARARGS, py_type_memory,                               \
    "Read types from a buffer.\n"                               \
    "\n"                                                        \
    "This operation is usually handled internally by the"       \
    " Chrysalide's core.\n"                                     \
    "\n"                                                        \
    "The *pbuf* parameter is a pychrysalide.common.PackedBuffer"\
    " instance providing buffered data to read."                \
    "\n"                                                        \
    "The result is a boolean value indicating the status of"    \
    " the operation: True for success, False for failure."      \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_packed_buffer, &pbuf);
    if (!ret) return NULL;

    tpmem = G_TYPE_MEMORY(pygobject_get(self));

    status = g_type_memory_load_types(tpmem, pbuf);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant une mémorisation de types.        *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Crée une nouvelle instance d'objet à partir de son type.     *
*                                                                             *
*  Retour      : Instance issue de l'opération ou NULL.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_type_memory_create_object(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    packed_buffer_t *pbuf;                  /* Tampon à consulter          */
    int ret;                                /* Bilan de lecture des args.  */
    GTypeMemory *tpmem;                     /* Mémorisation native         */
    GObject *obj;                           /* Instance retournée          */

#define TYPE_MEMORY_CREATE_OBJECT_METHOD PYTHON_METHOD_DEF          \
(                                                                   \
    create_object, "$self, pbuf",                                   \
    METH_VARARGS, py_type_memory,                                   \
    "Create a new GLib object from serialized data.\n"              \
    "\n"                                                            \
    "The *pbuf* parameter is a pychrysalide.common.PackedBuffer"    \
    " instance providing buffered data to read."                    \
    "\n"                                                            \
    "The result is a Python object linked to a native GLib"         \
    " object instance."                                             \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_packed_buffer, &pbuf);
    if (!ret) return NULL;

    tpmem = G_TYPE_MEMORY(pygobject_get(self));

    obj = g_type_memory_create_object(tpmem, pbuf);

    result = pygobject_new(obj);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant une mémorisation de types.        *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Sauvegarde le type d'un objet instancié.                     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_type_memory_store_object_gtype(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    GObject *obj;                           /* Instance à traiter          */
    packed_buffer_t *pbuf;                  /* Tampon à consulter          */
    int ret;                                /* Bilan de lecture des args.  */
    GTypeMemory *tpmem;                     /* Mémorisation native         */
    bool status;                            /* Bilan de l'opération        */

#define TYPE_MEMORY_STORE_OBJECT_GTYPE_METHOD PYTHON_METHOD_DEF     \
(                                                                   \
    store_object_gtype, "$self, obj, pbuf",                         \
    METH_VARARGS, py_type_memory,                                   \
    "Create a new GLib object from serialized data.\n"              \
    "\n"                                                            \
    "The *obj* parameter is the Python version of the GObject"      \
    " whose type is to process and the *pbuf* parameter is a"       \
    " pychrysalide.common.PackedBuffer instance providing buffered" \
    " data to extend."                                              \
    "\n"                                                            \
    "The result is a boolean value indicating the status of the"    \
    " operation: True for success, False for failure."              \
)

    ret = PyArg_ParseTuple(args, "O!O&", PyGObject_Type, &obj, convert_to_packed_buffer, &pbuf);
    if (!ret) return NULL;

    tpmem = G_TYPE_MEMORY(pygobject_get(self));

    status = g_type_memory_store_object_gtype(tpmem, obj, pbuf);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant une mémorisation de types.        *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Enregistre tous les types mémorisés dans un tampon.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_type_memory_store_types(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    packed_buffer_t *pbuf;                  /* Tampon à consulter          */
    int ret;                                /* Bilan de lecture des args.  */
    GTypeMemory *tpmem;                     /* Mémorisation native         */
    bool status;                            /* Bilan de l'opération        */

#define TYPE_MEMORY_STORE_TYPES_METHOD PYTHON_METHOD_DEF        \
(                                                               \
    store_types, "$self, pbuf",                                 \
    METH_VARARGS, py_type_memory,                               \
    "Write types into a buffer.\n"                              \
    "\n"                                                        \
    "This operation is usually handled internally by the"       \
    " Chrysalide's core.\n"                                     \
    "\n"                                                        \
    "The *pbuf* parameter is a pychrysalide.common.PackedBuffer"\
    " instance providing buffered data to read."                \
    "\n"                                                        \
    "The result is a boolean value indicating the status of"    \
    " the operation: True for success, False for failure."      \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_packed_buffer, &pbuf);
    if (!ret) return NULL;

    tpmem = G_TYPE_MEMORY(pygobject_get(self));

    status = g_type_memory_store_types(tpmem, pbuf);

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

PyTypeObject *get_python_type_memory_type(void)
{
    static PyMethodDef py_type_memory_methods[] = {
        TYPE_MEMORY_LOAD_TYPES_METHOD,
        TYPE_MEMORY_CREATE_OBJECT_METHOD,
        TYPE_MEMORY_STORE_OBJECT_GTYPE_METHOD,
        TYPE_MEMORY_STORE_TYPES_METHOD,
        { NULL }
    };

    static PyGetSetDef py_type_memory_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_type_memory_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.storage.TypeMemory",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = TYPE_MEMORY_DOC,

        .tp_methods     = py_type_memory_methods,
        .tp_getset      = py_type_memory_getseters,

        .tp_init        = py_type_memory_init,
        .tp_new         = py_type_memory_new

    };

    return &py_type_memory_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.analysis...TypeMemory'.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_type_memory_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'BufferCache'   */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_type_memory_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.storage");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_TYPE_MEMORY, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en mémorisation de types.                 *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_type_memory(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_type_memory_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to buffer cache");
            break;

        case 1:
            *((GTypeMemory **)dst) = G_TYPE_MEMORY(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
