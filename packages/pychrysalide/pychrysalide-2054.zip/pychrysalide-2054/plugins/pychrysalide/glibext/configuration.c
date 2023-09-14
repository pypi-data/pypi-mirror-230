
/* Chrysalide - Outil d'analyse de fichiers binaires
 * configuration.c - prototypes pour l'équivalent Python du fichier "glibext/configuration.c"
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


#include "configuration.h"


#include <pygobject.h>


#include <glibext/configuration-int.h>
#include <plugins/dt.h>


#include "constants.h"
#include "../access.h"
#include "../helpers.h"



/* ---------------------------- ELEMENT DE CONFIGURATION ---------------------------- */


/* Crée un nouvel objet Python de type 'ConfigParam'. */
static PyObject *py_config_param_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_config_param_init(PyObject *, PyObject *, PyObject *);

/* Efface toute valeur courante d'un paramètre de configuration. */
static PyObject *py_config_param_make_empty(PyObject *, PyObject *);

/* Réinitialise la valeur d'un paramètre de configuration. */
static PyObject *py_config_param_reset(PyObject *, PyObject *);

/* Indique le chemin d'accès utilisé pour un paramètre. */
static PyObject *py_config_param_get_path(PyObject *, void *);

/* Indique le type de valeur utilisée par un paramètre. */
static PyObject *py_config_param_get_type(PyObject *, void *);

/* Indique le statut d'une valeur utilisée par un paramètre. */
static PyObject *py_config_param_get_state(PyObject *, void *);

/* Indique la valeur courante d'un paramètre de configuration. */
static PyObject *py_config_param_get_value(PyObject *, void *);

/* Modifie la valeur courante d'un paramètre de configuration. */
static int py_config_param_set_value(PyObject *, PyObject *, void *);



/* ----------------------------- PARCOURS DE PARAMETRES ----------------------------- */


/* Parcours des éléments de configuration */
typedef struct _pyConfigParamIterator
{
    PyObject_HEAD                           /* A laisser en premier        */

    GGenConfig *config;                     /* Configuration à parcourir   */
    GList *params;                          /* Liste de paramètres         */

    GList *last;                            /* Dernier élément retourné    */

} pyConfigParamIterator;


/* Prend acte d'un compteur de référence à 0. */
static void py_config_param_iterator_dealloc(PyObject *);

/* Fournit un itérateur pour paramètres de configuration. */
static PyObject *py_config_param_iterator_next(PyObject *);

/* Initialise un objet Python de type 'ConfigParamIterator'. */
static int py_config_param_iterator_init(PyObject *, PyObject *, PyObject *);



/* ----------------------- GESTION GENERIQUE DE CONFIGURATION ----------------------- */


/* Accompagne la création d'une instance dérivée en Python. */
static PyObject *py_generic_config_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_generic_config_init(PyObject *, PyObject *, PyObject *);

/* Met à disposition un encadrement des accès aux paramètres. */
static PyObject *py_generic_config_lock_unlock(PyObject *, PyObject *);

/* Lit la configuration depuis un fichier. */
static PyObject *py_generic_config_read(PyObject *, PyObject *);

/* Ecrit la configuration dans un fichier. */
static PyObject *py_generic_config_write(PyObject *, PyObject *);

/* Retrouve un élément de configuration par son chemin. */
static PyObject *py_generic_config_search(PyObject *, PyObject *);

/* Ajoute un paramètre à une configuration. */
static PyObject *py_generic_config_add(PyObject *, PyObject *);

/* Retire un paramètre d'une configuration. */
static PyObject *py_generic_config_delete(PyObject *, PyObject *);

/* Indique le fichier utilisé pour l'enregistrement XML. */
static PyObject *py_generic_config_get_filename(PyObject *, void *);

/* Renvoie la liste des paramètres de configuration. */
static PyObject *py_generic_config_get_params(PyObject *, void *);



/* ---------------------------------------------------------------------------------- */
/*                              ELEMENT DE CONFIGURATION                              */
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

static PyObject *py_config_param_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

    /* Validations diverses */

    base = get_python_config_param_type();

    if (type == base)
        goto simple_way;

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_CFG_PARAM, type->tp_name, NULL, NULL, NULL);

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

static int py_config_param_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    const char *path;                       /* Accès au paramètre          */
    ConfigParamType ptype;                  /* Type de paramètre           */
    PyObject *py_value;                     /* Valeur par défaut éventuelle*/
    int ret;                                /* Bilan de lecture des args.  */
    bool valid;                             /* Validité des transmissions  */
    param_value value;                      /* Valeur de paramètre         */
    GCfgParam *param;                       /* Paramètre mis en place      */

#define CONFIG_PARAM_DOC                                                        \
    "ConfigParam holds a configuration parameter with its default and current"  \
    " values.\n"                                                                \
    "\n"                                                                        \
    "Parameters are aimed to join a pychrysalide.glibext.GenConfig instance.\n" \
    "\n"                                                                        \
    "Instances can be created using the following constructor:\n"               \
    "\n"                                                                        \
    "    ConfigParam(path, type, value=None)"                                   \
    "\n"                                                                        \
    "Where *path* is dot separated string items serving as a parameter key,"    \
    " *type* is a pychrysalide.glibext.ConfigParam.ConfigParamType value and"   \
    " *value* is an optional default value if the parameter initial value"      \
    " has not to be empty."

    /* Récupération des paramètres */

    py_value = NULL;

    ret = PyArg_ParseTuple(args, "sO&|O", &path, convert_to_config_param_type, &ptype, &py_value);
    if (!ret) return -1;

    if (py_value != NULL && py_value != Py_None)
    {
        switch (ptype)
        {
            case CPT_BOOLEAN:
                valid = PyBool_Check(py_value);
                if (valid)
                    value.boolean = (bool)(py_value == Py_True);
                break;

            case CPT_INTEGER:
                valid = PyLong_Check(py_value);
                if (valid)
                    value.integer = (int)PyLong_AsLong(py_value);
                break;

            case CPT_ULONG:
                valid = PyLong_Check(py_value);
                if (valid)
                    value.ulong = (unsigned long)PyLong_AsUnsignedLong(py_value);
                break;

            case CPT_STRING:
                valid = PyUnicode_Check(py_value);
                if (valid)
                    value.string = PyUnicode_DATA(py_value);
                break;

            case CPT_COLOR:
                valid = (convert_to_gdk_rgba(py_value, &value.color) == 1);
                break;

            default:
                assert(false);
                valid = false;
                break;

        }

        if (!valid)
        {
            PyErr_SetString(PyExc_TypeError, "invalid value for the specified parameter type");
            return -1;
        }

    }

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    param = G_CFG_PARAM(pygobject_get(self));

    if (py_value == NULL || py_value == Py_None)
        g_config_param_build_empty(param, path, ptype);

    else
        g_config_param_build(param, path, ptype, &value);

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = paramètre de configuration à manipuler.               *
*                args = non utilisé ici.                                      *
*                                                                             *
*  Description : Efface toute valeur courante d'un paramètre de configuration.*
*                                                                             *
*  Retour      : None.                                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_config_param_make_empty(PyObject *self, PyObject *args)
{
    GCfgParam *param;                       /* Paramètre visé par l'opérat°*/

#define CONFIG_PARAM_MAKE_EMPTY_METHOD PYTHON_METHOD_DEF        \
(                                                               \
    make_empty, "$self, /",                                     \
    METH_NOARGS, py_config_param,                               \
    "Unset the value of the current parameter."                 \
)

    param = G_CFG_PARAM(pygobject_get(self));

    g_config_param_make_empty(param);

    Py_RETURN_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = paramètre de configuration à manipuler.               *
*                args = non utilisé ici.                                      *
*                                                                             *
*  Description : Réinitialise la valeur d'un paramètre de configuration.      *
*                                                                             *
*  Retour      : None.                                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_config_param_reset(PyObject *self, PyObject *args)
{
    GCfgParam *param;                       /* Paramètre visé par l'opérat°*/

#define CONFIG_PARAM_RESET_METHOD PYTHON_METHOD_DEF \
(                                                   \
    reset, "$self, /",                              \
    METH_NOARGS, py_config_param,                   \
    "Reset the content of the current parameter."   \
)

    param = G_CFG_PARAM(pygobject_get(self));

    g_config_param_reset(param);

    Py_RETURN_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = paramètre de configuration à manipuler.               *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique le chemin d'accès utilisé pour un paramètre.         *
*                                                                             *
*  Retour      : Chemin d'accès en Python.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_config_param_get_path(PyObject *self, void *closure)
{
    GCfgParam *param;                       /* Paramètre visé par l'opérat°*/
    const char *path;                       /* Chemin d'accès à diffuser   */

#define CONFIG_PARAM_PATH_ATTRIB PYTHON_GET_DEF_FULL    \
(                                                       \
    path, py_config_param,                              \
    "Dot separated string items used as key for a"      \
    " configuration parameter."                         \
)

    param = G_CFG_PARAM(pygobject_get(self));
    path = g_config_param_get_path(param);

    return PyUnicode_FromString(path);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = paramètre de configuration à manipuler.               *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique le type de valeur utilisée par un paramètre.         *
*                                                                             *
*  Retour      : Type en Python.                                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_config_param_get_type(PyObject *self, void *closure)
{
    PyObject *result;                       /* Type de paramètre à renvoyer*/
    GCfgParam *param;                       /* Paramètre visé par l'opérat°*/
    ConfigParamType type;                   /* Type de paramètre           */

#define CONFIG_PARAM_TYPE_ATTRIB PYTHON_GET_DEF_FULL            \
(                                                               \
    type, py_config_param,                                      \
    "Type of value provided by a configuration parameter.\n"    \
    "\n"                                                        \
    "The attribute carries a"                                   \
    " pychrysalide.glibext.ConfigParam.ConfigParamType value."  \
)

    param = G_CFG_PARAM(pygobject_get(self));
    type = g_config_param_get_ptype(param);

    result = cast_with_constants_group_from_type(get_python_config_param_type(), "ConfigParamType", type);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = paramètre de configuration à manipuler.               *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique le statut d'une valeur utilisée par un paramètre.    *
*                                                                             *
*  Retour      : Etat en Python.                                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_config_param_get_state(PyObject *self, void *closure)
{
    PyObject *result;                       /* Etat à retourner            */
    GCfgParam *param;                       /* Paramètre visé par l'opérat°*/
    ConfigParamState state;                 /* Statut de paramètre         */

#define CONFIG_PARAM_STATE_ATTRIB PYTHON_GET_DEF_FULL           \
(                                                               \
    state, py_config_param,                                     \
    "State of a configuration parameter.\n"                     \
    "\n"                                                        \
    "The attribute carries a"                                   \
    " pychrysalide.glibext.ConfigParam.ConfigParamState value." \
)

    param = G_CFG_PARAM(pygobject_get(self));
    state = g_config_param_get_state(param);

    result = cast_with_constants_group_from_type(get_python_config_param_type(), "ConfigParamState", state);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = paramètre de configuration à manipuler.               *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique la valeur courante d'un paramètre de configuration.  *
*                                                                             *
*  Retour      : Etat en Python.                                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_config_param_get_value(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GCfgParam *param;                       /* Paramètre visé par l'opérat°*/
    ConfigParamType type;                   /* Type de paramètre manipulé  */
    param_value value;                      /* Valeur de paramètre         */

#define CONFIG_PARAM_VALUE_ATTRIB PYTHON_GETSET_DEF_FULL        \
(                                                               \
    value, py_config_param,                                     \
    "Value of a configuration parameter.\n"                     \
    "\n"                                                        \
    "The type of the value carried by the attribute depends on" \
    " pychrysalide.glibext.ConfigParam.type value."             \
)

    param = G_CFG_PARAM(pygobject_get(self));

    type = g_config_param_get_ptype(param);

    g_config_param_get_value(param, &value);

    switch (type)
    {
        case CPT_BOOLEAN:
            result = (value.boolean ? Py_True : Py_False);
            Py_INCREF(result);
            break;

        case CPT_INTEGER:
            result = PyLong_FromLong(value.integer);
            break;

        case CPT_ULONG:
            result = PyLong_FromUnsignedLong(value.ulong);
            break;

        case CPT_STRING:
            if (value.string != NULL)
                result = PyUnicode_FromString(value.string);
            else
            {
                result = Py_None;
                Py_INCREF(result);
            }
            break;

        case CPT_COLOR:
            result = create_gdk_rgba(&value.color);
            break;

        default:
            result = NULL;
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = paramètre de configuration à manipuler.            *
*                value   = nouvelle valeur à convertir et définir.            *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Modifie la valeur courante d'un paramètre de configuration.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_config_param_set_value(PyObject *self, PyObject *value, void *closure)
{
    int result;                             /* Conclusion à remonter       */
    GCfgParam *param;                       /* Paramètre visé par l'opérat°*/
    ConfigParamType type;                   /* Type de paramètre manipulé  */
    param_value pvalue;                     /* Valeur de paramètre         */

    result = -1;

    param = G_CFG_PARAM(pygobject_get(self));

    if (value == Py_None)
    {
        g_config_param_make_empty(param);
        result = 0;
    }

    else
    {
        type = g_config_param_get_ptype(param);

        switch (type)
        {
            case CPT_BOOLEAN:
                if (PyBool_Check(value))
                {
                    pvalue.integer = (value == Py_True);
                    g_config_param_set_value(param, pvalue.integer);
                    result = 0;
                }
                break;

            case CPT_INTEGER:
                if (PyLong_Check(value))
                {
                    pvalue.integer = PyLong_AsLong(value);
                    g_config_param_set_value(param, pvalue.integer);
                    result = 0;
                }
                break;

            case CPT_ULONG:
                if (PyLong_Check(value))
                {
                    pvalue.ulong = PyLong_AsUnsignedLong(value);
                    g_config_param_set_value(param, pvalue.ulong);
                    result = 0;
                }
                break;

            case CPT_STRING:
                if (PyUnicode_Check(value))
                {
                    pvalue.string = PyUnicode_DATA(value);
                    g_config_param_set_value(param, pvalue.string);
                    result = 0;
                }
                break;

            case CPT_COLOR:
                if (convert_to_gdk_rgba(value, &pvalue.color) == 1)
                {
                    g_config_param_set_value(param, &pvalue.color);
                    result = 0;
                }
                break;

            default:
                assert(false);
                break;

        }

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

PyTypeObject *get_python_config_param_type(void)
{
    static PyMethodDef py_config_param_methods[] = {
        CONFIG_PARAM_MAKE_EMPTY_METHOD,
        CONFIG_PARAM_RESET_METHOD,
        { NULL }
    };

    static PyGetSetDef py_config_param_getseters[] = {
        CONFIG_PARAM_PATH_ATTRIB,
        CONFIG_PARAM_TYPE_ATTRIB,
        CONFIG_PARAM_STATE_ATTRIB,
        CONFIG_PARAM_VALUE_ATTRIB,
        CONFIG_PARAM_VALUE_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_config_param_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.glibext.ConfigParam",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = CONFIG_PARAM_DOC,

        .tp_methods     = py_config_param_methods,
        .tp_getset      = py_config_param_getseters,

        .tp_init        = py_config_param_init,
        .tp_new         = py_config_param_new

    };

    return &py_config_param_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.glibext.ConfigParam'.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_config_param_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'ConfigParam'   */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_config_param_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.glibext");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_CFG_PARAM, type))
            return false;

        if (!define_config_param_constants(type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en paramètre de configuration.            *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_config_param(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_config_param_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to configuration parameter");
            break;

        case 1:
            *((GCfgParam **)dst) = G_CFG_PARAM(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                               PARCOURS DE PARAMETRES                               */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self = instance Python à libérer de la mémoire.              *
*                                                                             *
*  Description : Prend acte d'un compteur de référence à 0.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_config_param_iterator_dealloc(PyObject *self)
{
    pyConfigParamIterator *iterator;        /* Références pour le parcours */

    /**
     * Il aurait été sans doute mieux de reposer ici sur .tp_finalize,
     * mais cela semble impliquer de mettre en place tous les mécanismes de GC...
     *
     * cf. https://docs.python.org/3/extending/newtypes.html#finalization-and-de-allocation
     */

    iterator = (pyConfigParamIterator *)self;

    g_generic_config_runlock(iterator->config);
    g_object_unref(G_OBJECT(iterator->config));

    Py_TYPE(self)->tp_free((PyObject *)self);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = itérateur à manipuler.                                *
*                                                                             *
*  Description : Fournit un itérateur pour paramètres de configuration.       *
*                                                                             *
*  Retour      : Instance Python prête à emploi.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_config_param_iterator_next(PyObject *self)
{
    PyObject *result;                       /* Instance à retourner        */
    pyConfigParamIterator *iterator;        /* Références pour le parcours */
    GList *item;                            /* Nouvel élément courant      */

    iterator = (pyConfigParamIterator *)self;

    if (iterator->last == NULL) item = iterator->params;
    else item = g_list_next(iterator->last);

    iterator->last = item;

    if (item != NULL)
        result = pygobject_new(G_OBJECT(item->data));

    else
    {
        PyErr_SetNone(PyExc_StopIteration);
        result = NULL;
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet instancié à initialiser.                        *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Initialise un objet Python de type 'ConfigParamIterator'.    *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_config_param_iterator_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    GGenConfig *config;                     /* Configuration format natif  */
    int ret;                                /* Bilan de lecture des args.  */
    pyConfigParamIterator *iterator;        /* Références pour le parcours */

#define CONFIG_PARAM_ITERATOR_DOC                                           \
    "ConfigParamIterator is an iterator for configuration parameters.\n"    \
    "\n"                                                                    \
    "This kind of iterator is provided by the"                              \
    " pychrysalide.glibext.GenConfig.params attribute."

    ret = PyArg_ParseTuple(args, "O&", convert_to_generic_config, &config);
    if (!ret) return -1;

    iterator = (pyConfigParamIterator *)self;

    iterator->config = config;
    g_object_ref(G_OBJECT(iterator->config));

    g_generic_config_rlock(iterator->config);

    iterator->params = g_generic_config_list_params(iterator->config);

    iterator->last = NULL;

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

PyTypeObject *get_python_config_param_iterator_type(void)
{
    static PyTypeObject py_config_param_iterator_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.glibext.ConfigParamIterator",
        .tp_basicsize   = sizeof(pyConfigParamIterator),

        .tp_dealloc     = py_config_param_iterator_dealloc,

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = CONFIG_PARAM_ITERATOR_DOC,

        .tp_iter        = PyObject_SelfIter,
        .tp_iternext    = py_config_param_iterator_next,

        .tp_init        = py_config_param_iterator_init,

        .tp_new         = PyType_GenericNew,

    };

    return &py_config_param_iterator_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide...ConfigParamIterator'.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_config_param_iterator_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'Cnf...Iter'    */
    PyObject *module;                       /* Module à recompléter        */

    type = get_python_config_param_iterator_type();

    type->tp_base = &PyBaseObject_Type;

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.glibext");

        if (PyType_Ready(type) != 0)
            return false;

        if (!register_python_module_object(module, type))
            return false;

    }

    return true;

}



/* ---------------------------------------------------------------------------------- */
/*                         GESTION GENERIQUE DE CONFIGURATION                         */
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

static PyObject *py_generic_config_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

    /* Validations diverses */

    base = get_python_generic_config_type();

    if (type == base)
        goto simple_way;

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_GEN_CONFIG, type->tp_name, NULL, NULL, NULL);

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

static int py_generic_config_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    const char *name;                       /* Désignation de configuration*/
    int ret;                                /* Bilan de lecture des args.  */
    GGenConfig *config;                     /* Configuration en place      */

#define GENERIC_CONFIG_DOC                                                  \
    "The GenConfig class defines a generic way to load, provide and store"  \
    " configuration items. Each of these items is handled with a"           \
    " pychrysalide.glibext.ConfigParam object.\n"                           \
    "\n"                                                                    \
    "Instances can be created using the following constructor:\n"           \
    "\n"                                                                    \
    "    GenConfig(name=None)"                                              \
    "\n"                                                                    \
    "Where *name* is a suitable storage filename for the configuration. If" \
    " no *name* is defined, the configuration is expected to be"            \
    " memory-only resident."

    /* Récupération des paramètres */

    name = NULL;

    ret = PyArg_ParseTuple(args, "|s", &name);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    config = G_GEN_CONFIG(pygobject_get(self));

    if (name != NULL)
        g_generic_config_build(config, name);

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = configuration à manipuler.                            *
*                args = paramètres liés à l'appel.                            *
*                                                                             *
*  Description : Met à disposition un encadrement des accès aux paramètres.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_generic_config_lock_unlock(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    bool write;                             /* Accès en lecture / écriture */
    bool lock;                              /* Pose ou retrait du verrou ? */
    int ret;                                /* Bilan de lecture des args.  */
    GGenConfig *config;                     /* Version GLib de la config.  */

#define GENERIC_CONFIG_LOCK_UNLOCK_METHOD PYTHON_METHOD_DEF     \
(                                                               \
    lock_unlock, "$self, write, lock",                          \
    METH_VARARGS, py_generic_config,                            \
    "Lock or unlock access to the configuration internals.\n"   \
    "\n"                                                        \
    "The *write* argument states if the operation targets read" \
    " or write accesses, and the *lock* value defines the"      \
    " state to achieve.\n"                                      \
    "\n"                                                        \
    "Both arguments are boolean values."                        \
)

    ret = PyArg_ParseTuple(args, "pp", &write, &lock);
    if (!ret) return NULL;

    config = G_GEN_CONFIG(pygobject_get(self));

    g_generic_config_lock_unlock(config, write, lock);

    result = Py_None;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = configuration à manipuler.                            *
*                args = non utilisé ici.                                      *
*                                                                             *
*  Description : Lit la configuration depuis un fichier.                      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_generic_config_read(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GGenConfig *config;                     /* Version GLib de la config.  */
    bool status;                            /* Bilan de l'opération        */

#define GENERIC_CONFIG_READ_METHOD PYTHON_METHOD_DEF            \
(                                                               \
    read, "$self, /",                                           \
    METH_NOARGS, py_generic_config,                             \
    "Read the configuration from its relative XML file.\n"      \
    "\n"                                                        \
    "The returned value is True if the operation terminated"    \
    " with success, or False in case of failure."               \
)

    config = G_GEN_CONFIG(pygobject_get(self));

    status = g_generic_config_read(config);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = configuration à manipuler.                            *
*                args = non utilisé ici.                                      *
*                                                                             *
*  Description : Ecrit la configuration dans un fichier.                      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_generic_config_write(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GGenConfig *config;                     /* Version GLib de la config.  */
    bool status;                            /* Bilan de l'opération        */

#define GENERIC_CONFIG_WRITE_METHOD PYTHON_METHOD_DEF           \
(                                                               \
    write, "$self, /",                                          \
    METH_NOARGS, py_generic_config,                             \
    "Write the configuration to its relative XML file.\n"       \
    "\n"                                                        \
    "The returned value is True if the operation terminated"    \
    " with success, or False in case of failure."               \
)

    config = G_GEN_CONFIG(pygobject_get(self));

    status = g_generic_config_write(config);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = configuration à manipuler.                            *
*                args = indication sur l'élément à retrouver.                 *
*                                                                             *
*  Description : Retrouve un élément de configuration par son chemin.         *
*                                                                             *
*  Retour      : Elément trouvé ou NULL en cas d'échec.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_generic_config_search(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    int lock;                               /* Ordre de pose de verrou     */
    const char *path;                       /* Chemin d'accès du paramètre */
    int ret;                                /* Bilan de lecture des args.  */
    GGenConfig *config;                     /* Version GLib de la config.  */
    GCfgParam *param;                       /* Paramètre trouvé ou NULL    */

#define GENERIC_CONFIG_SEARCH_METHOD PYTHON_METHOD_DEF                      \
(                                                                           \
    search, "$self, path, /, lock=True",                                    \
    METH_VARARGS, py_generic_config,                                        \
    "Look for a given configuration parameter.\n"                           \
    "\n"                                                                    \
    "The *path* argument is a string used as key pointing to a parameter."  \
    " The *lock* boolean value is an optional order handling the way"       \
    " configuration parameters are accessed.\n"                             \
    "\n"                                                                    \
    "The configuration has to be locked while accessing its content. This"  \
    " lock can be managed with the *lock* argument of this function or"     \
    " thanks to the pychrysalide.glibext.GenConfig.lock_unlock method().\n" \
    "\n"                                                                    \
    "The returned value is a pychrysalide.glibext.ConfigParam instance in"  \
    " case of success or None if the parameter is not found."               \
)

    lock = 1;

    ret = PyArg_ParseTuple(args, "s|p", &path, &lock);
    if (!ret) return NULL;

    config = G_GEN_CONFIG(pygobject_get(self));

    param = _g_generic_config_search(config, path, lock);

    if (param == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }
    else
    {
        result = pygobject_new(G_OBJECT(param));
        g_object_unref(G_OBJECT(param));
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = configuration à manipuler.                            *
*                args = indication sur l'élément à retrouver.                 *
*                                                                             *
*  Description : Ajoute un paramètre à une configuration.                     *
*                                                                             *
*  Retour      : Elément ajouté ou NULL en cas d'échec.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_generic_config_add(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    int lock;                               /* Ordre de pose de verrou     */
    GCfgParam *param;                       /* Paramètre GLib transmis     */
    int ret;                                /* Bilan de lecture des args.  */
    GGenConfig *config;                     /* Version GLib de la config.  */
    bool status;                            /* Bilan de l'opération        */

#define GENERIC_CONFIG_ADD_METHOD PYTHON_METHOD_DEF                         \
(                                                                           \
    add, "$self, param, /, lock=True",                                      \
    METH_VARARGS, py_generic_config,                                        \
    "Add an existing parameter to a configuration.\n"                       \
    "\n"                                                                    \
    "The *param* argument has to be a pychrysalide.glibext.ConfigParam"     \
    " instance. The *lock* boolean value is an optional order handling"     \
    " the way configuration parameters are accessed.\n"                     \
    "\n"                                                                    \
    "The configuration has to be locked while accessing its content. This"  \
    " lock can be managed with the *lock* argument of this function or"     \
    " thanks to the pychrysalide.glibext.GenConfig.lock_unlock method().\n" \
    "\n"                                                                    \
    "The returned value is a pychrysalide.glibext.ConfigParam instance in"  \
    " case of success or None if the parameter already exists in the"       \
    " configuration."                                                       \
)

    lock = 1;

    ret = PyArg_ParseTuple(args, "O&|p", convert_to_config_param, &param, &lock);
    if (!ret) return NULL;

    config = G_GEN_CONFIG(pygobject_get(self));

    status = _g_generic_config_add_param(config, param, lock);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = configuration à manipuler.                            *
*                args = indication sur l'élément à retrouver.                 *
*                                                                             *
*  Description : Retire un paramètre d'une configuration.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_generic_config_delete(PyObject *self, PyObject *args)
{
    const char *path;                       /* Chemin d'accès du paramètre */
    int ret;                                /* Bilan de lecture des args.  */
    GGenConfig *config;                     /* Version GLib de la config.  */

#define GENERIC_CONFIG_DELETE_METHOD PYTHON_METHOD_DEF                      \
(                                                                           \
    delete, "$self, path",                                                  \
    METH_VARARGS, py_generic_config,                                        \
    "Delete an existing parameter from a configuration.\n"                  \
    "\n"                                                                    \
    "The *path* argument is a string used as key pointing to the parameter" \
    " to process."                                                          \
)

    ret = PyArg_ParseTuple(args, "s", &path);
    if (!ret) return NULL;

    config = G_GEN_CONFIG(pygobject_get(self));

    g_generic_config_delete_param(config, path);

    Py_RETURN_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = NULL car méthode statique.                         *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique le fichier utilisé pour l'enregistrement XML.        *
*                                                                             *
*  Retour      : Chemin d'accès, potentiellement non existant.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_generic_config_get_filename(PyObject *self, void *closure)
{
    PyObject *result;                       /* Chemin à retourner          */
    GGenConfig *config;                     /* Version GLib de la config.  */
    const char *filename;                   /* Chemin d'accès au fichier   */

#define GENERIC_CONFIG_FILENAME_ATTRIB PYTHON_GET_DEF_FULL      \
(                                                               \
    filename, py_generic_config,                                \
    "Path to the file used as storage backend for the"          \
    " configuration.\n"                                         \
    "\n"                                                        \
    "The result is a string pointing to a file which may not"   \
    " (yet) exist or None if not defined."                      \
)

    config = G_GEN_CONFIG(pygobject_get(self));

    filename = g_generic_config_get_filename(config);

    if (filename == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }

    else
        result = PyUnicode_FromString(filename);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = NULL car méthode statique.                         *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Renvoie la liste des paramètres de configuration.            *
*                                                                             *
*  Retour      : Liste d'éléments à parcourir.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_generic_config_get_params(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance à retourner        */
    PyTypeObject *iterator_type;            /* Type Python de l'itérateur  */
    PyObject *args_list;                    /* Arguments de mise en place  */

#define GENERIC_CONFIG_PARAMS_ATTRIB PYTHON_GET_DEF_FULL        \
(                                                               \
    params, py_generic_config,                                  \
    "List of all registered configuration parameters.\n"        \
    "\n"                                                        \
    "The result is a pychrysalide.glibext.ConfigParamIterator"  \
    " over pychrysalide.glibext.ConfigParam instances."         \
)

    iterator_type = get_python_config_param_iterator_type();

    Py_INCREF(self);

    args_list = Py_BuildValue("(O)", self);
    result = PyObject_CallObject((PyObject *)iterator_type, args_list);

    Py_DECREF(args_list);

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

PyTypeObject *get_python_generic_config_type(void)
{
    static PyMethodDef py_generic_config_methods[] = {
        GENERIC_CONFIG_LOCK_UNLOCK_METHOD,
        GENERIC_CONFIG_READ_METHOD,
        GENERIC_CONFIG_WRITE_METHOD,
        GENERIC_CONFIG_SEARCH_METHOD,
        GENERIC_CONFIG_ADD_METHOD,
        GENERIC_CONFIG_DELETE_METHOD,
        { NULL }
    };

    static PyGetSetDef py_generic_config_getseters[] = {
        GENERIC_CONFIG_FILENAME_ATTRIB,
        GENERIC_CONFIG_PARAMS_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_generic_config_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.glibext.GenConfig",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = GENERIC_CONFIG_DOC,

        .tp_methods     = py_generic_config_methods,
        .tp_getset      = py_generic_config_getseters,

        .tp_init        = py_generic_config_init,
        .tp_new         = py_generic_config_new

    };

    return &py_generic_config_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.glibext.GenConfig'.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_generic_config_is_registered(void)
{
    PyTypeObject *type;   /* Type Python 'GenConfig'     */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_generic_config_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.glibext");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_GEN_CONFIG, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en configuration générique.               *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_generic_config(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_generic_config_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to generic configuration");
            break;

        case 1:
            *((GGenConfig **)dst) = G_GEN_CONFIG(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
