
/* Chrysalide - Outil d'analyse de fichiers binaires
 * type.c - équivalent Python du fichier "analysis/type.c"
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


#include "type.h"


#include <assert.h>
#include <malloc.h>
#include <pygobject.h>


#include <i18n.h>


#include <analysis/type-int.h>
#include <plugins/dt.h>


#include "constants.h"
#include "storage/serialize.h"
#include "../access.h"
#include "../helpers.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Accompagne la création d'une instance dérivée en Python. */
static PyObject *py_data_type_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise la classe des types quelconques. */
static void py_data_type_init_gclass(GDataTypeClass *, gpointer);

/* Calcule une empreinte pour un type de données. */
static guint py_data_type_hash_wrapper(const GDataType *);

/* Crée un copie d'un type existant. */
static GDataType *py_data_type_dup_wrapper(const GDataType *);

/* Décrit le type fourni sous forme de caractères. */
static char *py_data_type_to_string_wrapper(const GDataType *, bool);

/* Indique si le type assure une gestion des espaces de noms. */
static bool py_data_type_handle_namespaces_wrapper(const GDataType *);

/* Indique si le type est un pointeur. */
static bool py_data_type_is_pointer_wrapper(const GDataType *);

/* Indique si le type est une référence. */
static bool py_data_type_is_reference_wrapper(const GDataType *);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_data_type_init(PyObject *, PyObject *, PyObject *);



/* ----------------- FONCTIONNALITES BASIQUES POUR TYPES DE DONNEES ----------------- */


/* Décrit le type fourni sous forme de caractères. */
static PyObject *py_data_type_to_str(PyObject *);

/* Crée un copie d'un type existant. */
static PyObject *py_data_type_dup(PyObject *, PyObject *);

/* Calcule une empreinte pour un type de données. */
static PyObject *py_data_type_get_hash(PyObject *, void *);

/* Fournit le groupe d'appartenance d'un type donné. */
static PyObject *py_data_type_get_namespace(PyObject *, void *);

/* Définit le groupe d'appartenance d'un type donné. */
static int py_data_type_set_namespace(PyObject *, PyObject *, void *);

/* Fournit les qualificatifs associés à une instance de type. */
static PyObject *py_data_type_get_qualifiers(PyObject *, void *);

/* Définit l'ensemble des qualificatifs d'une instance de type. */
static int py_data_type_set_qualifiers(PyObject *, PyObject *, void *);

/* Indique si le type assure une gestion des espaces de noms. */
static PyObject *py_data_type_handle_namespaces(PyObject *, void *);

/* Indique si le type est un pointeur. */
static PyObject *py_data_type_is_pointer(PyObject *, void *);

/* Indique si le type est une référence. */
static PyObject *py_data_type_is_reference(PyObject *, void *);



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

static PyObject *py_data_type_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

    /* Validations diverses */

    base = get_python_data_type_type();

    if (type == base)
    {
        result = NULL;
        PyErr_Format(PyExc_RuntimeError, _("%s is an abstract class"), type->tp_name);
        goto exit;
    }

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_DATA_TYPE, type->tp_name,
                               (GClassInitFunc)py_data_type_init_gclass, NULL, NULL);

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

    result = PyType_GenericNew(type, args, kwds);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class  = classe à initialiser.                               *
*                unused = données non utilisées ici.                          *
*                                                                             *
*  Description : Initialise la classe des types quelconques.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_data_type_init_gclass(GDataTypeClass *class, gpointer unused)
{
    class->hash = py_data_type_hash_wrapper;
    class->dup = py_data_type_dup_wrapper;
    class->to_string = py_data_type_to_string_wrapper;

    class->handle_ns = py_data_type_handle_namespaces_wrapper;
    class->is_pointer = py_data_type_is_pointer_wrapper;
    class->is_reference = py_data_type_is_reference_wrapper;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à consulter.                                     *
*                                                                             *
*  Description : Calcule une empreinte pour un type de données.               *
*                                                                             *
*  Retour      : Valeur arbitraire sur 32 bits, idéalement unique par type.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static guint py_data_type_hash_wrapper(const GDataType *type)
{
    guint result;                           /* Empreinte à renvoyer        */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */

#define DATA_TYPE_HASH_WRAPPER PYTHON_WRAPPER_DEF               \
(                                                               \
    _hash, "$self, /",                                          \
    METH_NOARGS,                                                \
    "Abstract method used to create a hash of the data type.\n" \
    "\n"                                                        \
    "The returned value has to be a 32-bit integer."            \
)

    result = 0;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(type));

    if (has_python_method(pyobj, "_hash"))
    {
        pyret = run_python_method(pyobj, "_hash", NULL);

        if (pyret != NULL)
        {
            if (PyLong_Check(pyret))
                result = PyLong_AsSsize_t(pyret);
        }

        Py_XDECREF(pyret);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à dupliquer.                                     *
*                                                                             *
*  Description : Crée un copie d'un type existant.                            *
*                                                                             *
*  Retour      : Nouvelle instance de type identique à celle fournie.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GDataType *py_data_type_dup_wrapper(const GDataType *type)
{
    GDataType *result;                      /* Copie à retourner           */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */

#define DATA_TYPE_DUP_WRAPPER PYTHON_WRAPPER_DEF                \
(                                                               \
    _dup, "$self, /",                                           \
    METH_NOARGS,                                                \
    "Abstract method used to create a copy of a data type.\n"   \
    "\n"                                                        \
    "The returned value has to be a new instance of the"        \
    " pychrysalide.analysis.DataType class."                    \
)

    result = NULL;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(type));

    if (has_python_method(pyobj, "_dup"))
    {
        pyret = run_python_method(pyobj, "_dup", NULL);

        if (pyret != NULL)
        {
            if (PyObject_TypeCheck(pyret, get_python_data_type_type()))
            {
                result = G_DATA_TYPE(pygobject_get(pyret));
                g_object_ref(G_OBJECT(result));
            }
        }

        Py_XDECREF(pyret);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type    = type à convertir.                                  *
*                include = doit-on inclure les espaces de noms ?              *
*                                                                             *
*  Description : Décrit le type fourni sous forme de caractères.              *
*                                                                             *
*  Retour      : Chaîne à libérer de la mémoire après usage.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *py_data_type_to_string_wrapper(const GDataType *type, bool include)
{
    char *result;                           /* Etiquette à retourner       */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *arg;                          /* Version Python de l'argument*/
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan de consultation       */

#define DATA_TYPE_TO_STRING_WRAPPER PYTHON_WRAPPER_DEF              \
(                                                                   \
    _to_string, "$self, include, /",                                \
    METH_VARARGS,                                                   \
    "Abstract method used to provide the string represention of"    \
    " a data type.\n"                                               \
    "\n"                                                            \
    "The *include* argument defines if the type namespace has to"   \
    " get prepended, if it exists.\n"                               \
    "\n"                                                            \
    "The returned value has to be a string."                        \
)

    result = NULL;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(type));

    if (has_python_method(pyobj, "_to_string"))
    {
        arg = include ? Py_True : Py_False;
        Py_INCREF(arg);

        args = PyTuple_New(1);
        PyTuple_SetItem(args, 0, arg);

        pyret = run_python_method(pyobj, "_to_string", args);

        if (pyret != NULL)
        {
            if (PyUnicode_Check(pyret))
                result = strdup(PyUnicode_DATA(pyret));
        }

        Py_XDECREF(pyret);

        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à consulter.                                     *
*                                                                             *
*  Description : Indique si le type assure une gestion des espaces de noms.   *
*                                                                             *
*  Retour      : Bilan de la consultation.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_data_type_handle_namespaces_wrapper(const GDataType *type)
{
    bool result;                            /* Bilan à retourner           */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */

#define DATA_TYPE_HANDLE_NAMESPACES_WRAPPER PYTHON_TRUE_WRAPPER_DEF     \
(                                                                       \
    _handle_namespaces, "$self, /",                                     \
    METH_NOARGS,                                                        \
    "Abstract method used to state if the type handles namespaces"      \
    " or not.\n"                                                        \
    "\n"                                                                \
    "The return is a boolean value. If this method does not"            \
    " exist, the True value is assumed."                                \
)

    result = true;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(type));

    if (has_python_method(pyobj, "_handle_namespaces"))
    {
        pyret = run_python_method(pyobj, "_handle_namespaces", NULL);

        result = (pyret == Py_True);

        Py_XDECREF(pyret);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à consulter.                                     *
*                                                                             *
*  Description : Indique si le type est un pointeur.                          *
*                                                                             *
*  Retour      : Bilan de la consultation.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_data_type_is_pointer_wrapper(const GDataType *type)
{
    bool result;                            /* Bilan à retourner           */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */

#define DATA_TYPE_IS_POINTER_WRAPPER PYTHON_FALSE_WRAPPER_DEF   \
(                                                               \
    _is_pointer, "$self, /",                                    \
    METH_NOARGS,                                                \
    "Abstract method used to state if the type points to"       \
    " another type or not.\n"                                   \
    "\n"                                                        \
    "The return is a boolean value. If this method does not"    \
    " exist, the False value is assumed."                       \
)

    result = false;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(type));

    if (has_python_method(pyobj, "_is_pointer"))
    {
        pyret = run_python_method(pyobj, "_is_pointer", NULL);

        result = (pyret == Py_True);

        Py_XDECREF(pyret);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type à consulter.                                     *
*                                                                             *
*  Description : Indique si le type est une référence.                        *
*                                                                             *
*  Retour      : Bilan de la consultation.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_data_type_is_reference_wrapper(const GDataType *type)
{
    bool result;                            /* Bilan à retourner           */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */

#define DATA_TYPE_IS_REFERENCE_WRAPPER PYTHON_FALSE_WRAPPER_DEF \
(                                                               \
    _is_reference, "$self, /",                                  \
    METH_NOARGS,                                                \
    "Abstract method used to state if the type refers to"       \
    " another type or not.\n"                                   \
    "\n"                                                        \
    "The return is a boolean value. If this method does not"    \
    " exist, the False value is assumed."                       \
)

    result = false;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(type));

    if (has_python_method(pyobj, "_is_reference"))
    {
        pyret = run_python_method(pyobj, "_is_reference", NULL);

        result = (pyret == Py_True);

        Py_XDECREF(pyret);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

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

static int py_data_type_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    int ret;                                /* Bilan de lecture des args.  */

#define DATA_TYPE_DOC                                                   \
    "The DataType object is the base class for all data types.\n"       \
    "\n"                                                                \
    "Instances can be created using the following constructor:\n"       \
    "\n"                                                                \
    "    DataType()"                                                    \
    "\n"                                                                \
    "The following methods have to be defined for new classes:\n"       \
    "* pychrysalide.analysis.DataType._hash();\n"                       \
    "* pychrysalide.analysis.DataType._dup();\n"                        \
    "* pychrysalide.analysis.DataType._to_string()."                    \
    "\n"                                                                \
    "Some extra method definitions are optional for new classes:\n"     \
    "* pychrysalide.analysis.DataType._handle_namespaces();\n"          \
    "* pychrysalide.analysis.DataType._is_pointer();\n"                 \
    "* pychrysalide.analysis.DataType._is_reference();"                 \

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    return 0;

}



/* ---------------------------------------------------------------------------------- */
/*                   FONCTIONNALITES BASIQUES POUR TYPES DE DONNEES                   */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self = instance d'un type version Python à traiter.          *
*                                                                             *
*  Description : Décrit le type fourni sous forme de caractères.              *
*                                                                             *
*  Retour      : Chaîne de caractère construite pour l'occasion.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_data_type_to_str(PyObject *self)
{
    PyObject *result;                       /* Représentation à retourner  */
    GDataType *type;                        /* Version native de l'objet   */
    char *desc;                             /* Description du type         */

    type = G_DATA_TYPE(pygobject_get(self));

    desc = g_data_type_to_string(type, true);

    result = PyUnicode_FromString(desc);

    free(desc);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = serveur à manipuler.                                  *
*                args = arguments d'appel non utilisés ici.                   *
*                                                                             *
*  Description : Crée un copie d'un type existant.                            *
*                                                                             *
*  Retour      : Nouvelle instance de type identique à celle fournie.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_data_type_dup(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    GDataType *type;                        /* Version native de l'objet   */
    GDataType *copy;                        /* Copie du type obtenue       */

#define DATA_TYPE_DUP_METHOD PYTHON_METHOD_DEF              \
(                                                           \
    dup, "$self, /",                                        \
    METH_NOARGS, py_data_type,                              \
    "Create a copy of a data type.\n"                       \
    "\n"                                                    \
    "The returned value has to be a new instance of the"    \
    " pychrysalide.analysis.DataType class."                \
)

    type = G_DATA_TYPE(pygobject_get(self));

    copy = g_data_type_dup(type);

    if (copy != NULL)
    {
        result = pygobject_new(G_OBJECT(copy));
        g_object_unref(G_OBJECT(copy));
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
*  Description : Calcule une empreinte pour un type de données.               *
*                                                                             *
*  Retour      : Valeur arbitraire sur 32 bits, idéalement unique par type.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_data_type_get_hash(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GDataType *type;                        /* Elément à consulter         */
    guint hash;                             /* Empreinte à transmettre     */

#define DATA_TYPE_HASH_ATTRIB PYTHON_GET_DEF_FULL       \
(                                                       \
    hash, py_data_type,                                 \
    "Hash value for the type, as a 32-bit integer.\n"   \
    "\n"                                                \
    "Each proporty change implies a hash change."       \
)

    type = G_DATA_TYPE(pygobject_get(self));

    hash = g_data_type_hash(type);

    result = PyLong_FromUnsignedLong(hash);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le groupe d'appartenance d'un type donné.            *
*                                                                             *
*  Retour      : Eventuelle instance d'appartenance ou None.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_data_type_get_namespace(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GDataType *type;                        /* Elément à consulter         */
    GDataType *ns;                          /* Espace de noms              */
    char *sep;                              /* Séparateur d'espace         */

#define DATA_TYPE_NAMESPACE_ATTRIB PYTHON_GETSET_DEF_FULL               \
(                                                                       \
    namespace, py_data_type,                                            \
    "Namespace for the type, None if any.\n"                            \
    "\n"                                                                \
    "This property carries a tuple of two values:\n"                    \
    "* a namespace, as a pychrysalide.analysis.DataType.TypeQualifier"  \
    " instance;\n"                                                      \
    "* a namespace separator, as a string."                             \
)

    type = G_DATA_TYPE(pygobject_get(self));

    ns = g_data_type_get_namespace(type);
    sep = g_data_type_get_namespace_separator(type);

    if (ns != NULL && sep != NULL)
    {
        result = PyTuple_New(2);

        PyTuple_SetItem(result, 0, pygobject_new(G_OBJECT(ns)));
        g_object_unref(G_OBJECT(ns));

        PyTuple_SetItem(result, 1, PyUnicode_FromString(sep));
        free(sep);

    }

    else
    {
        assert(ns == NULL && sep == NULL);

        result = Py_None;
        Py_INCREF(result);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Définit le groupe d'appartenance d'un type donné.            *
*                                                                             *
*  Retour      : Bilan de l'opération pour Python.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_data_type_set_namespace(PyObject *self, PyObject *value, void *closure)
{
    GDataType *type;                        /* Elément à traiter           */
    bool status;                            /* Echec de l'inscription      */
    GDataType *ns;                          /* Espace de noms              */
    const char *sep;                        /* Séparateur des espaces      */

    if ((!PyTuple_Check(value) || (PyTuple_Check(value) && PyTuple_Size(value) != 2)) && value != Py_None)
    {
        PyErr_SetString(PyExc_TypeError,
                        _("The attribute value must be a tuple with GDataType and a separator or None."));
        return -1;
    }

    type = G_DATA_TYPE(pygobject_get(self));

    if (value == Py_None)
        status = g_data_type_set_namespace(type, NULL, NULL);

    else
    {
        if (!PyObject_IsInstance(PyTuple_GetItem(value, 0), (PyObject *)get_python_data_type_type()))
        {
            PyErr_SetString(PyExc_TypeError, _("The first tuple item must be a GDataType."));
            return -1;
        }

        if (!PyUnicode_Check(PyTuple_GetItem(value, 1)))
        {
            PyErr_SetString(PyExc_TypeError, _("The second tuple item must be a string."));
            return -1;
        }

        ns = G_DATA_TYPE(pygobject_get(PyTuple_GetItem(value, 0)));
        sep = PyUnicode_DATA(PyTuple_GetItem(value, 1));

        status = g_data_type_set_namespace(type, ns, sep);

    }

    if (!status)
    {
        PyErr_SetString(PyExc_TypeError, _("Failed while registering the type namespace (!)"));
        return -1;
    }

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit les qualificatifs associés à une instance de type.   *
*                                                                             *
*  Retour      : Qualificatifs éventuels.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_data_type_get_qualifiers(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GDataType *type;                        /* Elément à consulter         */
    TypeQualifier qualifiers;               /* Qualificatifs en place      */

#define DATA_TYPE_QUALIFIERS_ATTRIB PYTHON_GETSET_DEF_FULL                          \
(                                                                                   \
    qualifiers, py_data_type,                                                       \
    "Qualifier for the data type, *TypeQualifier.NONE* if any.\n"                   \
    "\n"                                                                            \
    "This property carries a pychrysalide.analysis.DataType.TypeQualifier value."   \
)

    type = G_DATA_TYPE(pygobject_get(self));
    qualifiers = g_data_type_get_qualifiers(type);

    result = cast_with_constants_group_from_type(get_python_data_type_type(), "TypeQualifier", qualifiers);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Définit l'ensemble des qualificatifs d'une instance de type. *
*                                                                             *
*  Retour      : Bilan de l'opération pour Python.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_data_type_set_qualifiers(PyObject *self, PyObject *value, void *closure)
{
    GDataType *type;                        /* Elément à traiter           */
    TypeQualifier qualifiers;               /* Qualificatifs à intégrer    */
    int ret;                                /* Bilan d'une conversion      */

    ret = convert_to_data_type_qualifier(value, &qualifiers);
    if (ret != 1) return -1;

    type = G_DATA_TYPE(pygobject_get(self));

    g_data_type_set_qualifiers(type, qualifiers);

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique si le type assure une gestion des espaces de noms.   *
*                                                                             *
*  Retour      : Bilan de la consultation.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_data_type_handle_namespaces(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GDataType *type;                        /* Elément à consulter         */
    bool status;                            /* Etat à faire suivre         */

#define DATA_TYPE_NAMESPACES_ATTRIB PYTHON_RAWGET_DEF_FULL      \
(                                                               \
    handle_namespaces, py_data_type,                            \
    "True if the type handles namespaces, False otherwise."     \
)

    type = G_DATA_TYPE(pygobject_get(self));

    status = g_data_type_handle_namespaces(type);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique si le type est un pointeur.                          *
*                                                                             *
*  Retour      : Bilan de la consultation.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_data_type_is_pointer(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GDataType *type;                        /* Elément à consulter         */
    bool status;                            /* Etat à faire suivre         */

#define DATA_TYPE_POINTER_ATTRIB PYTHON_IS_DEF_FULL     \
(                                                       \
    pointer, py_data_type,                              \
    "True if the type is a pointer, False otherwise."   \
)

    type = G_DATA_TYPE(pygobject_get(self));

    status = g_data_type_is_pointer(type);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique si le type est une référence.                        *
*                                                                             *
*  Retour      : Bilan de la consultation.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_data_type_is_reference(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GDataType *type;                        /* Elément à consulter         */
    bool status;                            /* Etat à faire suivre         */

#define DATA_TYPE_REFERENCE_ATTRIB PYTHON_IS_DEF_FULL   \
(                                                       \
    reference, py_data_type,                            \
    "True if the type is a reference, False otherwise." \
)

    type = G_DATA_TYPE(pygobject_get(self));

    status = g_data_type_is_reference(type);

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

PyTypeObject *get_python_data_type_type(void)
{
    static PyMethodDef py_data_type_methods[] = {
        DATA_TYPE_HASH_WRAPPER,
        DATA_TYPE_DUP_WRAPPER,
        DATA_TYPE_TO_STRING_WRAPPER,
        DATA_TYPE_HANDLE_NAMESPACES_WRAPPER,
        DATA_TYPE_IS_POINTER_WRAPPER,
        DATA_TYPE_DUP_METHOD,
        { NULL }
    };

    static PyGetSetDef py_data_type_getseters[] = {
        DATA_TYPE_HASH_ATTRIB,
        DATA_TYPE_NAMESPACE_ATTRIB,
        DATA_TYPE_QUALIFIERS_ATTRIB,
        DATA_TYPE_NAMESPACES_ATTRIB,
        DATA_TYPE_POINTER_ATTRIB,
        DATA_TYPE_REFERENCE_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_data_type_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.DataType",

        .tp_str         = py_data_type_to_str,

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = DATA_TYPE_DOC,

        .tp_methods     = py_data_type_methods,
        .tp_getset      = py_data_type_getseters,

        .tp_init        = py_data_type_init,
        .tp_new         = py_data_type_new

    };

    return &py_data_type_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.analysis.DataType'.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_data_type_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'DataType'      */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_data_type_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        if (!ensure_python_serializable_object_is_registered())
            return false;

        module = get_access_to_python_module("pychrysalide.analysis");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_DATA_TYPE, type))
            return false;

        if (!define_analysis_data_type_constants(type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en type de donnée.                        *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_data_type(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_data_type_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to data type");
            break;

        case 1:
            *((GDataType **)dst) = G_DATA_TYPE(pygobject_get(arg));
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
*  Description : Tente de convertir en type de donnée ou NULL.                *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_data_type_or_none(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    if (arg == Py_None)
    {
        *((GDataType **)dst) = NULL;
        result = 1;
    }

    else
        result = convert_to_data_type(arg, dst);

    return result;

}
