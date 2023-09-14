
/* Chrysalide - Outil d'analyse de fichiers binaires
 * operand.c - équivalent Python du fichier "arch/operand.h"
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


#include "operand.h"


#include <pygobject.h>


#include <i18n.h>
#include <arch/operand-int.h>
#include <plugins/dt.h>


#include "../access.h"
#include "../helpers.h"
#include "../glibext/singleton.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Accompagne la création d'une instance dérivée en Python. */
static PyObject *py_arch_operand_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise la classe générique des opérandes. */
static void py_arch_operand_init_gclass(GArchOperandClass *, gpointer);

/* Compare un opérande avec un autre. */
static int py_arch_operand___cmp___wrapper(const GArchOperand *, const GArchOperand *, bool);

/* Détermine le chemin conduisant à un opérande interne. */
static char *py_arch_operand_find_inner_operand_path_wrapper(const GArchOperand *, const GArchOperand *);

/* Obtient l'opérande correspondant à un chemin donné. */
static GArchOperand *py_arch_operand_get_inner_operand_from_path_wrapper(const GArchOperand *, const char *);

/* Traduit un opérande en version humainement lisible. */
static void py_arch_operand_print_wrapper(const GArchOperand *, GBufferLine *);

#ifdef INCLUDE_GTK_SUPPORT

/* Construit un petit résumé concis de l'opérande. */
static char *py_arch_operand_build_tooltip_wrapper(const GArchOperand *, const GLoadedBinary *);

#endif



/* ------------------------ DEFINITION D'OPERANDE QUELCONQUE ------------------------ */


/* Effectue une comparaison avec un objet Python 'ArchOperand'. */
static PyObject *py_arch_operand_richcompare(PyObject *, PyObject *, int);

/* Détermine le chemin conduisant à un opérande interne. */
static PyObject *py_arch_operand_find_inner_operand_path(PyObject *, PyObject *);

/* Obtient l'opérande correspondant à un chemin donné. */
static PyObject *py_arch_operand_get_inner_operand_from_path(PyObject *, PyObject *);



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

static PyObject *py_arch_operand_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

#define ARCH_OPERAND_DOC                                                \
    "The ArchOperand object aims to get subclassed to create"           \
    " operands of any kind for new architectures.\n"                    \
    "\n"                                                                \
    "Calls to the *__init__* constructor of this abstract object expect"\
    " no particular argument.\n"                                        \
    "\n"                                                                \
    "The following methods have to be defined for new classes:\n"       \
    "* pychrysalide.arch.ArchRegister.__cmp__();\n"                     \
    "* pychrysalide.arch.ArchRegister._print();\n"                      \
    "* pychrysalide.arch.ArchRegister._build_tooltip().\n"              \
    "\n"                                                                \
    "Some extra method definitions are optional for new classes:\n"     \
    "* pychrysalide.arch.ArchRegister._find_inner_operand_path();\n"    \
    "* pychrysalide.arch.ArchRegister._get_inner_operand_from_path().\n"\
    "\n"                                                                \
    "Chrysalide creates an internal glue to provide rich comparisons"   \
    " for operands based on the old-style *__cmp__* function."

    /* Validations diverses */

    base = get_python_arch_operand_type();

    if (type == base)
    {
        result = NULL;
        PyErr_Format(PyExc_RuntimeError, _("%s is an abstract class"), type->tp_name);
        goto exit;
    }

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_ARCH_OPERAND, type->tp_name,
                               (GClassInitFunc)py_arch_operand_init_gclass, NULL, NULL);

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
*  Description : Initialise la classe générique des opérandes.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_arch_operand_init_gclass(GArchOperandClass *class, gpointer unused)
{
    class->compare = py_arch_operand___cmp___wrapper;
    class->find_inner = py_arch_operand_find_inner_operand_path_wrapper;
    class->get_inner = py_arch_operand_get_inner_operand_from_path_wrapper;

    class->print = py_arch_operand_print_wrapper;
#ifdef INCLUDE_GTK_SUPPORT
    class->build_tooltip = py_arch_operand_build_tooltip_wrapper;
#endif

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a    = premier opérande à consulter.                         *
*                b    = second opérande à consulter.                          *
*                lock = précise le besoin en verrouillage.                    *
*                                                                             *
*  Description : Compare un opérande avec un autre.                           *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_arch_operand___cmp___wrapper(const GArchOperand *a, const GArchOperand *b, bool lock)
{
    int result;                             /* Empreinte à retourner       */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan de consultation       */

#define ARCH_OPERAND_CMP_WRAPPER PYTHON_WRAPPER_DEF             \
(                                                               \
    __cmp__, "$self, other, /",                                 \
    METH_VARARGS,                                               \
    "Abstract method used to compare the operand with another"  \
    " one. This second object is always an"                     \
    " pychrysalide.arch.ArchOperand instance.\n"                \
    "\n"                                                        \
    " This is the Python old-style comparison method, but"      \
    " Chrysalide provides a glue to automatically build a rich" \
    " version of this function."                                \
)

    result = 0;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(a));

    if (has_python_method(pyobj, "__cmp__"))
    {
        args = PyTuple_New(1);
        PyTuple_SetItem(args, 0, pygobject_new(G_OBJECT(b)));

        pyret = run_python_method(pyobj, "__cmp__", args);

        if (pyret != NULL)
        {
            if (PyLong_Check(pyret))
                result = PyLong_AsLong(pyret);
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
*  Paramètres  : operand = opérande à consulter.                              *
*                target  = instruction à venir retrouver.                     *
*                                                                             *
*  Description : Détermine le chemin conduisant à un opérande interne.        *
*                                                                             *
*  Retour      : Chemin d'accès à l'opérande ou NULL en cas d'absence.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *py_arch_operand_find_inner_operand_path_wrapper(const GArchOperand *operand, const GArchOperand *target)
{
    char *result;                           /* Chemin à retourner          */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan de consultation       */

#define ARCH_OPERAND_FIND_INNER_OPERAND_PATH_WRAPPER PYTHON_WRAPPER_DEF     \
(                                                                           \
    _find_inner_operand_path, "$self, target, /",                           \
    METH_VARARGS,                                                           \
    "Abstract method used to compute the path leading to an inner"          \
    " operand.\n"                                                           \
    "\n"                                                                    \
    "The *target* has to be an instance of pychrysalide.arch.ArchOperand"   \
    " included in the operand.\n"                                           \
    "\n"                                                                    \
    "The result is a string of the form 'n[:n:n:n]', where n is an"         \
    " internal index, or None if the *target* is not found. This kind of"   \
    " path is aimed to be built for the"                                    \
    " pychrysalide.arch.ArchInstruction.find_operand_path() function."      \
)

    result = NULL;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(operand));

    if (has_python_method(pyobj, "_find_inner_operand_path"))
    {
        args = PyTuple_New(1);
        PyTuple_SetItem(args, 0, pygobject_new(G_OBJECT(target)));

        pyret = run_python_method(pyobj, "_find_inner_operand_path", args);

        if (pyret != NULL)
        {
            if (PyUnicode_Check(pyret))
                result = strdup(PyUnicode_AsUTF8(pyret));
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
*  Paramètres  : operand = opérande à consulter.                              *
*                path  = chemin d'accès à un opérande à retrouver.            *
*                                                                             *
*  Description : Obtient l'opérande correspondant à un chemin donné.          *
*                                                                             *
*  Retour      : Opérande trouvé ou NULL en cas d'échec.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchOperand *py_arch_operand_get_inner_operand_from_path_wrapper(const GArchOperand *operand, const char *path)
{
    GArchOperand *result;                   /* Opérande trouvée à renvoyer */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan de consultation       */

#define ARCH_OPERAND_GET_INNER_OPERAND_FROM_PATH_WRAPPER PYTHON_WRAPPER_DEF \
(                                                                           \
    _get_inner_operand_from_path, "$self, path, /",                         \
    METH_VARARGS,                                                           \
    "Abstract method used to retrieve an inner operand by its path.\n"      \
    "\n"                                                                    \
    "This *path* is a string of the form 'n[:n:n:n]', where n is an"        \
    " internal index. Such a path is usually built by the"                  \
    " pychrysalide.arch.ArchInstruction.find_operand_path() function.\n"    \
    "\n"                                                                    \
    "The result is an pychrysalide.arch.ArchOperand instance, or"           \
    " None if no operand was found."                                        \
)

    result = NULL;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(operand));

    if (has_python_method(pyobj, "_get_inner_operand_from_path"))
    {
        args = PyTuple_New(1);
        PyTuple_SetItem(args, 0, PyUnicode_FromString(path));

        pyret = run_python_method(pyobj, "_get_inner_operand_from_path", args);

        if (pyret != NULL)
        {
            if (PyObject_TypeCheck(pyret, get_python_arch_operand_type()))
            {
                result = G_ARCH_OPERAND(pygobject_get(pyret));
                g_object_ref(G_OBJECT(result));
            }

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
*  Paramètres  : operand = registre visé par la procédure.                    *
*                                                                             *
*  Description : Traduit un opérande en version humainement lisible.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_arch_operand_print_wrapper(const GArchOperand *operand, GBufferLine *line)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan de consultation       */

#define ARCH_OPERAND_PRINT_WRAPPER PYTHON_WRAPPER_DEF               \
(                                                                   \
    _print, "$self, line, /",                                       \
    METH_VARARGS,                                                   \
    "Abstract method used to print the operand into a rendering"    \
    " line, which is a provided pychrysalide.glibext.BufferLine"    \
    " instance."                                                    \
)

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(operand));

    if (has_python_method(pyobj, "_print"))
    {
        args = PyTuple_New(1);
        PyTuple_SetItem(args, 0, pygobject_new(G_OBJECT(line)));

        pyret = run_python_method(pyobj, "_print", args);

        Py_XDECREF(pyret);

        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

}


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à consulter.                              *
*                binary  = informations relatives au binaire chargé.          *
*                                                                             *
*  Description : Construit un petit résumé concis de l'opérande.              *
*                                                                             *
*  Retour      : Chaîne de caractères à libérer après usage ou NULL.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *py_arch_operand_build_tooltip_wrapper(const GArchOperand *operand, const GLoadedBinary *binary)
{
    char *result;                           /* Description à retourner     */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan de consultation       */

#define ARCH_OPERAND_BUILD_TOOLTIP_WRAPPER PYTHON_WRAPPER_DEF       \
(                                                                   \
    _build_tooltip, "$self, line, /",                               \
    METH_VARARGS,                                                   \
    "Abstract method used to build a tooltip text shown when the"   \
    " mouse is over the operand.\n"                                 \
    "\n"                                                            \
    "A pychrysalide.analysis.LoadedBinary instance is provided in"  \
    " case of need."                                                \
)

    result = NULL;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(operand));

    if (has_python_method(pyobj, "_build_tooltip"))
    {
        args = PyTuple_New(1);
        PyTuple_SetItem(args, 0, pygobject_new(G_OBJECT(binary)));

        pyret = run_python_method(pyobj, "_build_tooltip", args);

        if (pyret != NULL)
        {
            if (PyUnicode_Check(pyret))
                result = strdup(PyUnicode_AsUTF8(pyret));
        }

        Py_XDECREF(pyret);

        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


#endif



/* ---------------------------------------------------------------------------------- */
/*                          DEFINITION D'OPERANDE QUELCONQUE                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : a  = premier object Python à consulter.                      *
*                b  = second object Python à consulter.                       *
*                op = type de comparaison menée.                              *
*                                                                             *
*  Description : Effectue une comparaison avec un objet Python 'ArchOperand'. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_arch_operand_richcompare(PyObject *a, PyObject *b, int op)
{
    PyObject *result;                       /* Bilan à retourner           */
    int ret;                                /* Bilan de lecture des args.  */
    const GArchOperand *reg_a;              /* Premier élément à traiter   */
    const GArchOperand *reg_b;              /* Second élément à traiter    */
    int status;                             /* Résultat d'une comparaison  */

    ret = PyObject_IsInstance(b, (PyObject *)get_python_arch_operand_type());
    if (!ret)
    {
        result = Py_NotImplemented;
        goto cmp_done;
    }

    reg_a = G_ARCH_OPERAND(pygobject_get(a));
    reg_b = G_ARCH_OPERAND(pygobject_get(b));

    status = py_arch_operand___cmp___wrapper(reg_a, reg_b, true);

    result = status_to_rich_cmp_state(status, op);

 cmp_done:

    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = architecture concernée par la procédure.              *
*                args = instruction représentant le point de départ.          *
*                                                                             *
*  Description : Détermine le chemin conduisant à un opérande interne.        *
*                                                                             *
*  Retour      : Chemin d'accès à l'opérande ou None en cas d'absence.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_arch_operand_find_inner_operand_path(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Chemin à retourner          */
    GArchOperand *target;                   /* Opérande ciblé par l'action */
    int ret;                                /* Bilan de lecture des args.  */
    GArchOperand *operand;                  /* Opérande manipulé           */
    char *path;                             /* Chemin déterminé            */

#define ARCH_OPERAND_FIND_INNER_OPERAND_PATH_METHOD PYTHON_METHOD_DEF       \
(                                                                           \
    find_inner_operand_path, "$self, target, /",                            \
    METH_VARARGS, py_arch_operand,                                          \
    "Compute the path leading to an inner operand.\n"                       \
    "\n"                                                                    \
    "The *target* has to be an instance of pychrysalide.arch.ArchOperand"   \
    " included in the operand.\n"                                           \
    "\n"                                                                    \
    "The result is a string of the form 'n[:n:n:n]', where n is an"         \
    " internal index, or None if the *target* is not found. This kind of"   \
    " path is aimed to be built for the"                                    \
    " pychrysalide.arch.ArchInstruction.find_operand_path() function."      \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_arch_operand, &target);
    if (!ret) return NULL;

    operand = G_ARCH_OPERAND(pygobject_get(self));

    path = g_arch_operand_find_inner_operand_path(operand, target);

    if (path != NULL)
    {
        result = PyUnicode_FromString(path);
        free(path);
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
*  Paramètres  : self = architecture concernée par la procédure.              *
*                args = instruction représentant le point de départ.          *
*                                                                             *
*  Description : Obtient l'opérande correspondant à un chemin donné.          *
*                                                                             *
*  Retour      : Opérande trouvé ou None en cas d'échec.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_arch_operand_get_inner_operand_from_path(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Trouvaille à retourner      */
    const char *path;                       /* Chemin à parcourir          */
    int ret;                                /* Bilan de lecture des args.  */
    GArchOperand *operand;                  /* Opérande manipulé           */
    GArchOperand *op;                       /* Opérande retrouvé           */

#define ARCH_OPERAND_GET_INNER_OPERAND_FROM_PATH_METHOD PYTHON_METHOD_DEF   \
(                                                                           \
    get_inner_operand_from_path, "$self, path, /",                          \
    METH_VARARGS, py_arch_operand,                                          \
    "Retrieve an inner operand by its path.\n"                              \
    "\n"                                                                    \
    "This *path* is a string of the form 'n[:n:n:n]', where n is an"        \
    " internal index. Such a path is usually built by the"                  \
    " pychrysalide.arch.ArchInstruction.find_operand_path() function.\n"    \
    "\n"                                                                    \
    "The result is an pychrysalide.arch.ArchOperand instance, or"           \
    " None if no operand was found."                                        \
)

    ret = PyArg_ParseTuple(args, "s", &path);
    if (!ret) return NULL;

    operand = G_ARCH_OPERAND(pygobject_get(self));

    op = g_arch_operand_get_inner_operand_from_path(operand, path);

    if (op != NULL)
    {
        result = pygobject_new(G_OBJECT(op));
        g_object_unref(G_OBJECT(op));
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
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Fournit un accès à une définition de type à diffuser.        *
*                                                                             *
*  Retour      : Définition d'objet pour Python.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyTypeObject *get_python_arch_operand_type(void)
{
    static PyMethodDef py_arch_operand_methods[] = {
        ARCH_OPERAND_CMP_WRAPPER,
        ARCH_OPERAND_FIND_INNER_OPERAND_PATH_WRAPPER,
        ARCH_OPERAND_GET_INNER_OPERAND_FROM_PATH_WRAPPER,
        ARCH_OPERAND_PRINT_WRAPPER,
#ifdef INCLUDE_GTK_SUPPORT
        ARCH_OPERAND_BUILD_TOOLTIP_WRAPPER,
#endif
        ARCH_OPERAND_FIND_INNER_OPERAND_PATH_METHOD,
        ARCH_OPERAND_GET_INNER_OPERAND_FROM_PATH_METHOD,
        { NULL }
    };

    static PyGetSetDef py_arch_operand_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_arch_operand_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.arch.ArchOperand",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_IS_ABSTRACT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = ARCH_OPERAND_DOC,

        .tp_richcompare = py_arch_operand_richcompare,

        .tp_methods     = py_arch_operand_methods,
        .tp_getset      = py_arch_operand_getseters,

        .tp_new         = py_arch_operand_new,

    };

    return &py_arch_operand_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.arch.ArchOperand'.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_arch_operand_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'ArchOperand'   */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_arch_operand_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.arch");

        dict = PyModule_GetDict(module);

        if (!ensure_python_singleton_candidate_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_ARCH_OPERAND, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en opérande d'architecture.               *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_arch_operand(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_arch_operand_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to arch operand");
            break;

        case 1:
            *((GArchOperand **)dst) = G_ARCH_OPERAND(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
