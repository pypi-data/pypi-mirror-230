
/* Chrysalide - Outil d'analyse de fichiers binaires
 * rename.c - prototypes pour l'équivalent Python du fichier "arch/operands/rename.c"
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


#include "rename.h"


#include <pygobject.h>


#include <arch/operands/rename-int.h>


#include "../../access.h"
#include "../../helpers.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Procède à l'initialisation de l'interface de renom. */
static void py_renamed_operand_init(GRenamedOperandIface *, gpointer *);

/* Fournit un texte comme représentation alternative d'opérande. */
static char *py_renamed_operand_get_text_wrapper(const GRenamedOperand *);



/* ------------------------ INTERFACE POUR OPERANDE RENOMMEE ------------------------ */


/* Fournit un texte comme représentation alternative d'opérande. */
static PyObject *py_renamed_operand_get_text(PyObject *, void *);



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Procède à l'initialisation de l'interface de renommage. */
static void py_renameable_operand_init(GRenameableOperandIface *, gpointer *);

/* Construit un opérande de représentation alternative. */
static GRenamedOperand *py_renameable_operand_build_wrapper(const GRenameableOperand *, const char *);



/* ----------------------- INTERFACE POUR OPERANDE RENOMMABLE ----------------------- */


/* Construit un opérande de représentation alternative. */
static PyObject *py_renameable_operand_build(PyObject *, PyObject *);



/* ---------------------------------------------------------------------------------- */
/*                          GLUE POUR CREATION DEPUIS PYTHON                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : iface  = interface GLib à initialiser.                       *
*                unused = adresse non utilisée ici.                           *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de renom.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_renamed_operand_init(GRenamedOperandIface *iface, gpointer *unused)
{

#define RENAMED_OPERAND_DOC                                                 \
    "The RenamedOperand interface depicts operands renamed with an"         \
    " alternative text."                                                    \
    "\n"                                                                    \
    "A typical class declaration for a new implementation looks like:\n"    \
    "\n"                                                                    \
    "    class NewImplem(GObject.Object, RenamedOperand):\n"                \
    "        ...\n"                                                         \
    "\n"                                                                    \
    "The following method has to be defined for new implementations:\n"     \
    "* pychrysalide.arch.operands.RenamedOperand._get_text();\n"            \

    iface->get_text = py_renamed_operand_get_text_wrapper;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = operande à consulter.                              *
*                                                                             *
*  Description : Fournit un texte comme représentation alternative d'opérande.*
*                                                                             *
*  Retour      : Chaîne de caractère de représentation alternative.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *py_renamed_operand_get_text_wrapper(const GRenamedOperand *operand)
{
    char *result;                           /* Texte à retourner           */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */
    int ret;                                /* Bilan d'une conversion      */

#define RENAMED_OPERAND_GET_TEXT_WRAPPER PYTHON_WRAPPER_DEF     \
(                                                               \
    _get_text, "$self",                                         \
    METH_NOARGS,                                                \
    "Abstract method used to provide the alternative text for"  \
    " rendering."                                               \
    "\n"                                                        \
    "The result of the call has to be a string."                \
)

    result = NULL;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(operand));

    if (has_python_method(pyobj, "_get_text"))
    {
        pyret = run_python_method(pyobj, "_get_text", NULL);

        if (pyret != NULL)
        {
            ret = PyUnicode_Check(pyret);

            if (ret)
                result = strdup(PyUnicode_AsUTF8(pyret));

            Py_DECREF(pyret);

        }

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                          INTERFACE POUR OPERANDE RENOMMEE                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit un texte comme représentation alternative d'opérande.*
*                                                                             *
*  Retour      : Chaîne de caractère de représentation alternative.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_renamed_operand_get_text(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GRenamedOperand *operand;               /* Elément à consulter         */
    const char *text;                       /* Texte alternatif de rendu   */

#define RENAMED_OPERAND_TEXT_ATTRIB PYTHON_GET_DEF_FULL     \
(                                                           \
    text, py_renamed_operand,                               \
    "Alternative text for the operand rendering."           \
)

    operand = G_RENAMED_OPERAND(pygobject_get(self));
    text = g_renamed_operand_get_text(operand);

    result = PyUnicode_FromString(text);

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

PyTypeObject *get_python_renamed_operand_type(void)
{
    static PyMethodDef py_renamed_operand_methods[] = {
        RENAMED_OPERAND_GET_TEXT_WRAPPER,
        { NULL }
    };

    static PyGetSetDef py_renamed_operand_getseters[] = {
        RENAMED_OPERAND_TEXT_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_renamed_operand_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.arch.operands.RenamedOperand",
        .tp_basicsize   = sizeof(PyObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = RENAMED_OPERAND_DOC,

        .tp_methods     = py_renamed_operand_methods,
        .tp_getset      = py_renamed_operand_getseters

    };

    return &py_renamed_operand_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.....RenamedOperand'.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_renamed_operand_is_registered(void)
{
    PyTypeObject *type;                     /* Type 'RenamedOperand'       */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    static GInterfaceInfo info = {          /* Paramètres d'inscription    */

        .interface_init = (GInterfaceInitFunc)py_renamed_operand_init,
        .interface_finalize = NULL,
        .interface_data = NULL,

    };

    type = get_python_renamed_operand_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.arch.operands");

        dict = PyModule_GetDict(module);

        if (!register_interface_for_pygobject(dict, G_TYPE_RENAMED_OPERAND, type, &info))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en opérande renommé.                      *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_renamed_operand(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_renamed_operand_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to renamed operand");
            break;

        case 1:
            *((GRenamedOperand **)dst) = G_RENAMED_OPERAND(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                          GLUE POUR CREATION DEPUIS PYTHON                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : iface  = interface GLib à initialiser.                       *
*                unused = adresse non utilisée ici.                           *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de renommage.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_renameable_operand_init(GRenameableOperandIface *iface, gpointer *unused)
{

#define RENAMEABLE_OPERAND_DOC                                              \
    "The RenameableOperand interface depicts operands which can get"        \
    " renamed with an alternative text."                                    \
    "\n"                                                                    \
    "A typical class declaration for a new implementation looks like:\n"    \
    "\n"                                                                    \
    "    class NewImplem(GObject.Object, RenameableOperand):\n"             \
    "        ...\n"                                                         \
    "\n"                                                                    \
    "The following method has to be defined for new implementations:\n"     \
    "* pychrysalide.arch.operands.RenameableOperand._build();\n"            \

    iface->build = py_renameable_operand_build_wrapper;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = operande à consulter.                              *
*                text    = texte alternatif de représentation.                *
*                                                                             *
*  Description : Construit un opérande de représentation alternative.         *
*                                                                             *
*  Retour      : Nouvel opérande, en version renommée.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GRenamedOperand *py_renameable_operand_build_wrapper(const GRenameableOperand *operand, const char *text)
{
    GRenamedOperand *result;                /* Instance à retourner        */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan de consultation       */
    int ret;                                /* Bilan d'une conversion      */

#define RENAMEABLE_OPERAND_BUILD_WRAPPER PYTHON_WRAPPER_DEF         \
(                                                                   \
    _build, "$self, text",                                          \
    METH_VARARGS,                                                   \
    "Abstract method used to build a new operand with an"           \
    " alternative text as rendering."                               \
    "\n"                                                            \
    "The result of the call has to be an object implementing the"   \
    " pychrysalide.arch.operands.RenamedOperand interface."         \
)

    result = NULL;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(operand));

    if (has_python_method(pyobj, "_build"))
    {
        args = PyTuple_New(1);
        PyTuple_SetItem(args, 0, PyUnicode_FromString(text));

        pyret = run_python_method(pyobj, "_build", args);

        if (pyret != NULL)
        {
            ret = convert_to_renamed_operand(pyret, &result);

            if (ret == 1)
                g_object_ref(G_OBJECT(result));

            PyErr_Clear();

            Py_DECREF(pyret);

        }

        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                         INTERFACE POUR OPERANDE RENOMMABLE                         */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = argument accompagnant l'appel.                        *
*                                                                             *
*  Description : Construit un opérande de représentation alternative.         *
*                                                                             *
*  Retour      : Nouvel opérande, en version renommée.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_renameable_operand_build(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    const char *text;                       /* Texte alternatif à utiliser */
    int ret;                                /* Bilan de lecture des args.  */
    GRenameableOperand *operand;            /* Instance à manipuler        */
    GRenamedOperand *renamed;               /* Instance nouvelle           */

#define RENAMEABLE_OPERAND_BUILD_METHOD PYTHON_METHOD_DEF           \
(                                                                   \
    build, "$self, text",                                           \
    METH_VARARGS, py_renameable_operand,                            \
    "Build a new operand with an alternative text as rendering."    \
    "\n"                                                            \
    "The result of the call is an object implementing the"          \
    " pychrysalide.arch.operands.RenamedOperand interface."         \
)

    ret = PyArg_ParseTuple(args, "s", &text);
    if (!ret) return NULL;

    operand = G_RENAMEABLE_OPERAND(pygobject_get(self));

    renamed = g_renameable_operand_build(operand, text);

    result = pygobject_new(G_OBJECT(renamed));
    g_object_unref(G_OBJECT(renamed));

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

PyTypeObject *get_python_renameable_operand_type(void)
{
    static PyMethodDef py_renameable_operand_methods[] = {
        RENAMEABLE_OPERAND_BUILD_WRAPPER,
        RENAMEABLE_OPERAND_BUILD_METHOD,
        { NULL }
    };

    static PyGetSetDef py_renameable_operand_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_renameable_operand_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.arch.operands.RenameableOperand",
        .tp_basicsize   = sizeof(PyObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = RENAMEABLE_OPERAND_DOC,

        .tp_methods     = py_renameable_operand_methods,
        .tp_getset      = py_renameable_operand_getseters

    };

    return &py_renameable_operand_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.....RenameableOperand'.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_renameable_operand_is_registered(void)
{
    PyTypeObject *type;                     /* Type 'RenameableOperand'    */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    static GInterfaceInfo info = {          /* Paramètres d'inscription    */

        .interface_init = (GInterfaceInitFunc)py_renameable_operand_init,
        .interface_finalize = NULL,
        .interface_data = NULL,

    };

    type = get_python_renameable_operand_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.arch.operands");

        dict = PyModule_GetDict(module);

        if (!register_interface_for_pygobject(dict, G_TYPE_RENAMEABLE_OPERAND, type, &info))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en opérande renommable.                   *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_renameable_operand(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_renameable_operand_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to renameable operand");
            break;

        case 1:
            *((GRenameableOperand **)dst) = G_RENAMEABLE_OPERAND(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
