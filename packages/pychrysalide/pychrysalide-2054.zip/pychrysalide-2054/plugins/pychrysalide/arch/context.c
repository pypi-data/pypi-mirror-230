
/* Chrysalide - Outil d'analyse de fichiers binaires
 * context.c - équivalent Python du fichier "arch/context.c"
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#include "context.h"


#include <assert.h>
#include <pygobject.h>


#include <i18n.h>
#include <arch/context-int.h>
#include <plugins/dt.h>


#include "constants.h"
#include "../access.h"
#include "../helpers.h"
#include "../analysis/db/item.h"
#include "../arch/vmpa.h"
#include "../format/preload.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Accompagne la création d'une instance dérivée en Python. */
static PyObject *py_proc_context_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise la classe des contextes de processeur. */
static void py_proc_context_init_gclass(GProcContextClass *, gpointer);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_proc_context_init(PyObject *, PyObject *, PyObject *);

/* Ajoute une adresse virtuelle comme point de départ de code. */
static void py_proc_context_push_drop_point_wrapper(GProcContext *, DisassPriorityLevel, virt_t, va_list);



/* ----------------------------- DEFINITION DE CONTEXTE ----------------------------- */


/* Ajoute une adresse virtuelle comme point de départ de code. */
static PyObject *py_proc_context_push_drop_point(PyObject *, PyObject *);

/* Empile une adresse de nouveau symbole à prendre en compte. */
static PyObject *py_proc_context_push_new_symbol_at(PyObject *, PyObject *);

/* Note la mise en place d'un élément pendant le désassemblage. */
static PyObject *py_proc_context_add_db_item(PyObject *, PyObject *);



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

static PyObject *py_proc_context_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

    /* Validations diverses */

    base = get_python_proc_context_type();

    if (type == base)
    {
        result = NULL;
        PyErr_Format(PyExc_RuntimeError, _("%s is an abstract class"), type->tp_name);
        goto exit;
    }

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_PROC_CONTEXT, type->tp_name,
                               (GClassInitFunc)py_proc_context_init_gclass, NULL, NULL);

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
*  Description : Initialise la classe des contextes de processeur.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_proc_context_init_gclass(GProcContextClass *class, gpointer unused)
{
	class->push_point = py_proc_context_push_drop_point_wrapper;

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

static int py_proc_context_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    int ret;                                /* Bilan d'initialisation      */

#define PROC_CONTEXT_DOC                                                \
    "The ProcContext object is a disassembling companion for"           \
    " architecture processors and is usually provided by the"           \
    " pychrysalide.arch.ArchProcessor.get_context() method.\n"          \
    "\n"                                                                \
    "So each kind of processor should have its dedicated context.\n"    \
    "\n"                                                                \
    "The role of a ProcContext instance is to collect on demand next"   \
    " points to process during a disassembling operation.\n"            \
    "\n"                                                                \
    "The following method may be defined for new classes:\n"            \
    "* pychrysalide.arch.ProcContext._push_drop_point();\n"             \
    "\n"                                                                \
    "Calls to the *__init__* constructor of this abstract object expect"\
    " no particular argument."

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ctx   = contexte de désassemblage à compléter.               *
*                level = indication de priorité et d'origine de l'adresse.    *
*                addr  = adresse d'un nouveau point de départ à traiter.      *
*                ap    = éventuelles informations complémentaires.            *
*                                                                             *
*  Description : Ajoute une adresse virtuelle comme point de départ de code.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_proc_context_push_drop_point_wrapper(GProcContext *ctx, DisassPriorityLevel level, virt_t addr, va_list ap)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pylevel;                      /* Priorité en objet Python    */
    PyObject *pyextra;                      /* Argument complémentaire ?   */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan de consultation       */
    GProcContextClass *class;               /* Classe parente de l'instance*/

#define PROC_CONTEXT_PUSH_DROP_POINT_WRAPPER PYTHON_WRAPPER_DEF     \
(                                                                   \
    _push_drop_point, "$self, level, addr, /, extra=None",          \
    METH_VARARGS,                                                   \
    "Abstract method used to inject a new virtual address to"       \
    " disassemble during the disassembling process.\n"              \
    "\n"                                                            \
    "The priority of this point is given by the"                    \
    " pychrysalide.arch.ProcContext.DisassPriorityLevel value."     \
    " Extra information may also be provided, as a Python object."  \
    "\n"                                                            \
    "If this method is not defined, the default behavior is to"     \
    " inject the point without any further treatment, as if"        \
    " *extra* does not carry any valuable information."             \
)

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(ctx));

    if (has_python_method(pyobj, "_push_drop_point"))
    {
        pylevel = cast_with_constants_group_from_type(get_python_proc_context_type(), "DisassPriorityLevel", level);
        pyextra = va_arg(ap, PyObject *);

        if (pyextra == NULL)
            pyextra = Py_None;

        Py_INCREF(pyextra);

        args = PyTuple_New(3);
        PyTuple_SetItem(args, 0, pylevel);
        PyTuple_SetItem(args, 1, PyLong_FromUnsignedLongLong(addr));
        PyTuple_SetItem(args, 2, pyextra);

        pyret = run_python_method(pyobj, "_push_drop_point", args);

        Py_XDECREF(pyret);

        Py_DECREF(args);

    }

    else
    {
        class = G_PROC_CONTEXT_CLASS(g_type_class_peek_parent(G_OBJECT_GET_CLASS(G_OBJECT(ctx))));

        assert(class->push_point != NULL);
        class->push_point(ctx, level, addr, ap);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

}



/* ---------------------------------------------------------------------------------- */
/*                               DEFINITION DE CONTEXTE                               */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet représentant un contexte de désasssemblage.     *
*                args = arguments fournis pour l'opération.                   *
*                                                                             *
*  Description : Ajoute une adresse virtuelle comme point de départ de code.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_proc_context_push_drop_point(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    DisassPriorityLevel level;              /* Niveau de priorité          */
    unsigned long long addr;                /* Adresse virtuelle à traiter */
    PyObject *extra;                        /* Eventuel complément d'info. */
    int ret;                                /* Bilan de lecture des args.  */
    GProcContext *ctx;                      /* Contexte de désassemble     */

#define PROC_CONTEXT_PUSH_DROP_POINT_METHOD PYTHON_METHOD_DEF       \
(                                                                   \
    push_drop_point, "$self, level, addr, /, extra=None",           \
    METH_VARARGS, py_proc_context,                                  \
    "Inject a new virtual address to disassemble during the"        \
    " disassembling process.\n"                                     \
    "\n"                                                            \
    "The priority of this point is given by the"                    \
    " pychrysalide.arch.ProcContext.DisassPriorityLevel value."     \
    " Extra information may also be provided, as a Python object."  \
)

    extra = Py_None;

    ret = PyArg_ParseTuple(args, "O&K|O", convert_to_disass_priority_level, &level, &addr, &extra);
    if (!ret) return NULL;

    ctx = G_PROC_CONTEXT(pygobject_get(self));

    g_proc_context_push_drop_point(ctx, level, addr, extra);

    result = Py_None;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet représentant un contexte de désasssemblage.     *
*                args = arguments fournis pour l'opération.                   *
*                                                                             *
*  Description : Empile une adresse de nouveau symbole à prendre en compte.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_proc_context_push_new_symbol_at(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    vmpa2t *addr;                           /* Adresse de symbole à ajouter*/
    int ret;                                /* Bilan de lecture des args.  */
    GProcContext *ctx;                      /* Contexte de désassemble     */

#define PROC_CONTEXT_PUSH_NEW_SYMBOL_AT_METHOD PYTHON_METHOD_DEF        \
(                                                                       \
    push_new_symbol_at, "$self, addr",                                  \
    METH_VARARGS, py_proc_context,                                      \
    "Collect the location of a symbol for the disassembling process.\n" \
    "\n"                                                                \
    "This location must be able to get converted into"                  \
    " a pychrysalide.arch.vmpa instance."                               \
)

    ret = PyArg_ParseTuple(args, "O&", convert_any_to_vmpa, &addr);
    if (!ret) return NULL;

    ctx = G_PROC_CONTEXT(pygobject_get(self));

    g_proc_context_push_new_symbol_at(ctx, addr);

    clean_vmpa_arg(addr);

    result = Py_None;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet représentant un contexte de désasssemblage.     *
*                args = arguments fournis pour l'opération.                   *
*                                                                             *
*  Description : Note la mise en place d'un élément pendant le désassemblage. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_proc_context_add_db_item(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    GDbItem *item;                          /* Elément à ajouter           */
    int ret;                                /* Bilan de lecture des args.  */
    GProcContext *ctx;                      /* Contexte de désassemble     */

#define PROC_CONTEXT_ADD_DB_ITEM_METHOD PYTHON_METHOD_DEF               \
(                                                                       \
    add_db_item, "$self, item",                                         \
    METH_VARARGS, py_proc_context,                                      \
    "Collect an extra item to include in the final disassembled"        \
    " content.\n"                                                       \
    "\n"                                                                \
    "The item to consider has to be a pychrysalide.analysis.db.DbItem"  \
    " instance."                                                        \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_db_item, &item);
    if (!ret) return NULL;

    ctx = G_PROC_CONTEXT(pygobject_get(self));

    g_proc_context_add_db_item(ctx, item);

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

PyTypeObject *get_python_proc_context_type(void)
{
    static PyMethodDef py_proc_context_methods[] = {
        PROC_CONTEXT_PUSH_DROP_POINT_WRAPPER,
        PROC_CONTEXT_PUSH_DROP_POINT_METHOD,
        PROC_CONTEXT_PUSH_NEW_SYMBOL_AT_METHOD,
        PROC_CONTEXT_ADD_DB_ITEM_METHOD,
        { NULL }
    };

    static PyGetSetDef py_proc_context_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_proc_context_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.arch.ProcContext",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_IS_ABSTRACT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = PROC_CONTEXT_DOC,

        .tp_methods     = py_proc_context_methods,
        .tp_getset      = py_proc_context_getseters,

        .tp_init        = py_proc_context_init,
        .tp_new         = py_proc_context_new,

    };

    return &py_proc_context_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.arch.ArchContext'.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_proc_context_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'ArchContext'   */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_proc_context_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.arch");

        dict = PyModule_GetDict(module);

        if (!ensure_python_preload_info_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_PROC_CONTEXT, type))
            return false;

        if (!define_proc_context_constants(type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en contexte de désassemblage.             *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_proc_context(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_proc_context_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to disassembly context");
            break;

        case 1:
            *((GProcContext **)dst) = G_PROC_CONTEXT(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
