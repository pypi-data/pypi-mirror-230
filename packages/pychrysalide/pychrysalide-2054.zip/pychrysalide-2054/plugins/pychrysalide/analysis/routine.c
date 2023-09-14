
/* Chrysalide - Outil d'analyse de fichiers binaires
 * routine.c - équivalent Python du fichier "analysis/routine.c"
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


#include "routine.h"


#include <string.h>
#include <pygobject.h>


#include <i18n.h>


#include <analysis/block.h>
#include <analysis/routine.h>


#include "block.h"
#include "type.h"
#include "../access.h"
#include "../helpers.h"
#include "../format/symbol.h"



/* Décrit la routine fournie sous forme de caractères. */
static PyObject *py_binary_routine_to_str(PyObject *);

/* Crée un nouvel objet Python de type 'BinRoutine'. */
static PyObject *py_binary_routine_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_binary_routine_init(PyObject *, PyObject *, PyObject *);

/* Fournit le groupe d'appartenance d'une routine donnée. */
static PyObject *py_binary_routine_get_namespace(PyObject *, void *);

/* Définit le groupe d'appartenance d'une routine donnée. */
static int py_binary_routine_set_namespace(PyObject *, PyObject *, void *);

/* Fournit le nom humain d'une routine. */
static PyObject *py_binary_routine_get_name(PyObject *, void *);

/* Définit le nom humain d'une routine. */
static int py_binary_routine_set_name(PyObject *, PyObject *, void *);

/* Fournit le type construisant le nom humain d'une routine. */
static PyObject *py_binary_routine_get_typed_name(PyObject *, void *);

/* Définit de façon indirecte le nom humain d'une routine. */
static int py_binary_routine_set_typed_name(PyObject *, PyObject *, void *);

/* Fournit le type de retour d'une routine. */
static PyObject *py_binary_routine_get_return_type(PyObject *, void *);

/* Définit le type de retour d'une routine. */
static int py_binary_routine_set_return_type(PyObject *, PyObject *, void *);

/* Fournit la liste des arguments associés à la routine. */
static PyObject *py_binary_routine_get_args(PyObject *, void *);

/* Fournit les blocs basiques de la routine. */
static PyObject *py_binary_routine_get_basic_blocks(PyObject *, void *);

/* Définit les blocs basiques de la routine. */
static int py_binary_routine_set_basic_blocks(PyObject *, PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = instance d'une routine version Python à traiter.      *
*                                                                             *
*  Description : Décrit la routine fournie sous forme de caractères.          *
*                                                                             *
*  Retour      : Chaîne de caractère construite pour l'occasion.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_routine_to_str(PyObject *self)
{
    PyObject *result;                       /* Représentation à retourner  */
    GBinRoutine *routine;                   /* Version native de l'objet   */
    char *desc;                             /* Description du type         */

    routine = G_BIN_ROUTINE(pygobject_get(self));

    desc = g_binary_routine_to_string(routine, true);

    result = PyUnicode_FromString(desc);

    free(desc);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de l'objet à instancier.                         *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Crée un nouvel objet Python de type 'BinaryRoutine'.         *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_routine_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Création à retourner        */

    result = pygobject_new(G_OBJECT(g_binary_routine_new()));

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

static int py_binary_routine_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    int result;                             /* Bilan à retourner           */

    /**
     * Si cette fonction n'est pas définie, l'initialisation de l'instance
     * se réalise via py_binary_symbol_init(), et l'interface attend là
     * des arguments...
     */

#define BINARY_ROUTINE_DOC                                                      \
    "BinRoutine is an object for a function in a binary.\n"                     \
    "\n"                                                                        \
    "Instances can be created using the following constructor:\n"               \
    "\n"                                                                        \
    "    BinRoutine()"                                                          \
    "\n"                                                                        \
    "As routines can be built from demangling, with no information other than"  \
    " a name at first glance, the usual process is to create a routine object"  \
    " and to define its core properties (namely a location range and a symbol"  \
    " type) after this operation."

    result = 0;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le groupe d'appartenance d'une routine donnée.       *
*                                                                             *
*  Retour      : Eventuelle instance d'appartenance ou None.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_routine_get_namespace(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GBinRoutine *routine;                   /* Elément à consulter         */
    GDataType *ns;                          /* Espace de noms              */

#define BINARY_ROUTINE_NAMESPACE_ATTRIB PYTHON_GETSET_DEF_FULL      \
(                                                                   \
    namespace, py_binary_routine,                                   \
    "Namespace of the routine, provided as a"                       \
    " pychrysalide.analysis.DataType instance, or None if any."     \
)

    routine = G_BIN_ROUTINE(pygobject_get(self));
    ns = g_binary_routine_get_namespace(routine);

    if (ns != NULL)
    {
        result = pygobject_new(G_OBJECT(ns));
        g_object_unref(G_OBJECT(ns));
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
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Définit le groupe d'appartenance d'une routine donnée.       *
*                                                                             *
*  Retour      : Bilan de l'opération pour Python.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_binary_routine_set_namespace(PyObject *self, PyObject *value, void *closure)
{
    GBinRoutine *routine;                   /* Elément à traiter           */
    GDataType *ns;                          /* Espace de noms              */
    char *sep;                              /* Séparateur des espaces      */

    if ((!PyTuple_Check(value) || (PyTuple_Check(value) && PyTuple_Size(value) != 2)) && value != Py_None)
    {
        PyErr_SetString(PyExc_TypeError,
                        _("The attribute value must be a tuple with GDataType and a separator or None."));
        return -1;
    }

    routine = G_BIN_ROUTINE(pygobject_get(self));

    if (value == Py_None)
        g_binary_routine_set_namespace(routine, NULL, NULL);

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
        sep = strdup(PyUnicode_DATA(pygobject_get(PyTuple_GetItem(value, 1))));

        g_object_ref(G_OBJECT(ns));
        g_binary_routine_set_namespace(routine, ns, sep);

    }

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le nom humain d'une routine.                         *
*                                                                             *
*  Retour      : Désignation humainement lisible ou None si non définie.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_routine_get_name(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GBinRoutine *routine;                   /* Elément à consulter         */
    const char *name;                       /* Désignation courante        */

#define BINARY_ROUTINE_NAME_ATTRIB PYTHON_GETSET_DEF_FULL       \
(                                                               \
    name, py_binary_routine,                                    \
    "String for the raw name of the routine or None if any."    \
)

    routine = G_BIN_ROUTINE(pygobject_get(self));
    name = g_binary_routine_get_name(routine);

    if (name != NULL)
        result = PyUnicode_FromString(name);

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
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Définit le nom humain d'une routine.                         *
*                                                                             *
*  Retour      : Bilan de l'opération pour Python.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_binary_routine_set_name(PyObject *self, PyObject *value, void *closure)
{
    GBinRoutine *routine;                   /* Elément à consulter         */

    if (!PyUnicode_Check(value) && value != Py_None)
    {
        PyErr_SetString(PyExc_TypeError, _("The attribute value must be a string or None."));
        return -1;
    }

    routine = G_BIN_ROUTINE(pygobject_get(self));

    if (value == Py_None)
        g_binary_routine_set_name(routine, NULL);
    else
        g_binary_routine_set_name(routine, strdup(PyUnicode_DATA(value)));

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le type construisant le nom humain d'une routine.    *
*                                                                             *
*  Retour      : Eventuel type à l'origine du nom ou None.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_routine_get_typed_name(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GBinRoutine *routine;                   /* Elément à consulter         */
    GDataType *name;                        /* Type de nom                 */

#define BINARY_ROUTINE_TYPED_NAME_ATTRIB PYTHON_GETSET_DEF_FULL         \
(                                                                       \
    typed_name, py_binary_routine,                                      \
    "Typed name of the routine, provided as a"                          \
    " pychrysalide.analysis.DataType instance, or None if any.\n"       \
    "\n"                                                                \
    "When a routine is built from a demangling operation, its final"    \
    " name carries some type information. This kind of information can" \
    " be retrived thanks to this attribute."                            \
)

    routine = G_BIN_ROUTINE(pygobject_get(self));
    name = g_binary_routine_get_typed_name(routine);

    if (name != NULL)
    {
        result = pygobject_new(G_OBJECT(name));
        g_object_unref(G_OBJECT(name));
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
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Définit de façon indirecte le nom humain d'une routine.      *
*                                                                             *
*  Retour      : Bilan de l'opération pour Python.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_binary_routine_set_typed_name(PyObject *self, PyObject *value, void *closure)
{
    GBinRoutine *routine;                   /* Elément à traiter           */
    GDataType *name;                        /* Type de nom                 */

    if (!PyObject_IsInstance(value, (PyObject *)get_python_data_type_type()) && value != Py_None)
    {
        PyErr_SetString(PyExc_TypeError, _("The attribute value must be a GDataType or None."));
        return -1;
    }

    routine = G_BIN_ROUTINE(pygobject_get(self));

    if (value == Py_None)
        g_binary_routine_set_return_type(routine, NULL);

    else
    {
        name = G_DATA_TYPE(pygobject_get(value));

        g_object_ref(G_OBJECT(name));
        g_binary_routine_set_typed_name(routine, name);

    }

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le type de retour d'une routine.                     *
*                                                                             *
*  Retour      : Indication sur le type de retour en place.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_routine_get_return_type(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GBinRoutine *routine;                   /* Elément à consulter         */
    GDataType *ret;                         /* Type de retour              */

#define BINARY_ROUTINE_RETURN_TYPE_ATTRIB PYTHON_GETSET_DEF_FULL    \
(                                                                   \
    return_type, py_binary_routine,                                 \
    "Return of the routine, provided as a"                          \
    " pychrysalide.analysis.DataType instance, or None if any."     \
)

    routine = G_BIN_ROUTINE(pygobject_get(self));
    ret = g_binary_routine_get_return_type(routine);

    if (ret != NULL)
    {
        result = pygobject_new(G_OBJECT(ret));
        g_object_unref(G_OBJECT(ret));
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
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Définit le type de retour d'une routine.                     *
*                                                                             *
*  Retour      : Bilan de l'opération pour Python.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_binary_routine_set_return_type(PyObject *self, PyObject *value, void *closure)
{
    GBinRoutine *routine;                   /* Elément à traiter           */
    GDataType *ret;                         /* Type de retour              */

    if (!PyObject_IsInstance(value, (PyObject *)get_python_data_type_type()) && value != Py_None)
    {
        PyErr_SetString(PyExc_TypeError, _("The attribute value must be a GDataType or None."));
        return -1;
    }

    routine = G_BIN_ROUTINE(pygobject_get(self));

    if (value == Py_None)
        g_binary_routine_set_return_type(routine, NULL);

    else
    {
        ret = G_DATA_TYPE(pygobject_get(value));

        g_object_ref(G_OBJECT(ret));
        g_binary_routine_set_return_type(routine, ret);

    }

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = classe représentant une routine binaire.           *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Fournit la liste des arguments associés à la routine.        *
*                                                                             *
*  Retour      : Ensemble de blocs déterminés via les instructions.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_routine_get_args(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GBinRoutine *routine;                   /* Version native              */
    size_t count;                           /* Nombre de paramètres        */
    size_t i;                               /* Boucle de parcours          */
    GBinVariable *arg;                      /* Argument à transcrire       */

#define BINARY_ROUTINE_ARGS_ATTRIB PYTHON_GET_DEF_FULL      \
(                                                           \
    args, py_binary_routine,                                \
    "Arguments for the routine, provided as a tuple of"     \
    " pychrysalide.analysis.BinVariable instances."         \
)

    routine = G_BIN_ROUTINE(pygobject_get(self));

    count = g_binary_routine_get_args_count(routine);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
        arg = g_binary_routine_get_arg(routine, i);

        PyTuple_SetItem(result, i, pygobject_new(G_OBJECT(arg)));

        g_object_unref(arg);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = classe représentant une routine binaire.           *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Fournit les blocs basiques de la routine.                    *
*                                                                             *
*  Retour      : Ensemble de blocs déterminés via les instructions.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_routine_get_basic_blocks(PyObject *self, void *closure)
{
    PyObject *result;                       /* Eléments à retourner        */
    GBinRoutine *routine;                   /* Version native              */
    GBlockList *blocks;                     /* Blocs basiques de routine   */

#define BINARY_ROUTINE_BASIC_BLOCKS_ATTRIB PYTHON_GETSET_DEF_FULL           \
(                                                                           \
    basic_blocks, py_binary_routine,                                        \
    "Basic blocks for the routine.\n"                                       \
    "\n"                                                                    \
    "This list is managed by a pychrysalide.analysis.BlockList instance."   \
)

    routine = G_BIN_ROUTINE(pygobject_get(self));
    blocks = g_binary_routine_get_basic_blocks(routine);

    result = pygobject_new(G_OBJECT(blocks));

    g_object_unref(G_OBJECT(blocks));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Définit les blocs basiques de la routine.                    *
*                                                                             *
*  Retour      : Bilan de l'opération pour Python.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_binary_routine_set_basic_blocks(PyObject *self, PyObject *value, void *closure)
{
    GBinRoutine *routine;                   /* Elément à consulter         */
    int ret;                                /* Bilan de lecture des args.  */
    GBlockList *blocks;                     /* Blocs basiques à intégrer   */

    ret = PyObject_IsInstance(value, (PyObject *)get_python_block_list_type());
    if (!ret) return -1;

    routine = G_BIN_ROUTINE(pygobject_get(self));
    blocks = G_BLOCK_LIST(pygobject_get(value));

    g_binary_routine_set_basic_blocks(routine, blocks);

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

PyTypeObject *get_python_binary_routine_type(void)
{
    static PyMethodDef py_binary_routine_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_binary_routine_getseters[] = {
        BINARY_ROUTINE_NAMESPACE_ATTRIB,
        BINARY_ROUTINE_NAME_ATTRIB,
        BINARY_ROUTINE_TYPED_NAME_ATTRIB,
        BINARY_ROUTINE_RETURN_TYPE_ATTRIB,
        BINARY_ROUTINE_ARGS_ATTRIB,
        BINARY_ROUTINE_BASIC_BLOCKS_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_binary_routine_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.BinRoutine",

        .tp_str         = py_binary_routine_to_str,

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = BINARY_ROUTINE_DOC,

        .tp_methods     = py_binary_routine_methods,
        .tp_getset      = py_binary_routine_getseters,

        .tp_init        = py_binary_routine_init,
        .tp_new         = py_binary_routine_new

    };

    return &py_binary_routine_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.analysis.BinRoutine'.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_binary_routine_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'BinRoutine'    */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_binary_routine_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis");

        dict = PyModule_GetDict(module);

        if (!ensure_python_binary_symbol_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_BIN_ROUTINE, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en routine de binaire.                    *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_binary_routine(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_binary_routine_type());

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
            *((GBinRoutine **)dst) = G_BIN_ROUTINE(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
