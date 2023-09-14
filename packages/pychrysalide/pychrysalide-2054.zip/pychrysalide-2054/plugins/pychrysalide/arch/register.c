
/* Chrysalide - Outil d'analyse de fichiers binaires
 * register.c - équivalent Python du fichier "arch/register.c"
 *
 * Copyright (C) 2019 Cyrille Bagard
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


#include "register.h"


#include <assert.h>
#include <pygobject.h>


#include <i18n.h>
#include <arch/register-int.h>
#include <plugins/dt.h>


#include "../access.h"
#include "../helpers.h"
#include "../analysis/storage/serialize.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Accompagne la création d'une instance dérivée en Python. */
static PyObject *py_arch_register_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise la classe des registres. */
static void py_arch_register_init_gclass(GArchRegisterClass *, gpointer);

/* Produit une empreinte à partir d'un registre. */
static guint py_arch_register___hash___wrapper(const GArchRegister *);

/* Compare un registre avec un autre. */
static int py_arch_register___cmp___wrapper(const GArchRegister *, const GArchRegister *);

/* Traduit un registre en version humainement lisible. */
static void py_arch_register_print_wrapper(const GArchRegister *, GBufferLine *);

/* Indique si le registre correspond à ebp ou similaire. */
static bool py_arch_register_is_base_pointer_wrapper(const GArchRegister *);

/* Indique si le registre correspond à esp ou similaire. */
static bool py_arch_register_is_stack_pointer_wrapper(const GArchRegister *);



/* ---------------------------- PUR REGISTRE DU MATERIEL ---------------------------- */


/* Effectue une comparaison avec un objet Python 'ArchRegister'. */
static PyObject *py_arch_register_richcompare(PyObject *, PyObject *, int);

/* Indique si le registre correspond à ebp ou similaire. */
static PyObject *py_arch_register_is_base_pointer(PyObject *, void *);

/* Indique si le registre correspond à esp ou similaire. */
static PyObject *py_arch_register_is_stack_pointer(PyObject *, void *);



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

static PyObject *py_arch_register_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de registre    */
    bool status;                            /* Bilan d'un enregistrement   */

#define ARCH_REGISTER_DOC                                               \
    "The ArchRegister object aims to get subclassed to create"          \
    " registers suitable for new architectures.\n"                      \
    "\n"                                                                \
    "Calls to the *__init__* constructor of this abstract object expect"\
    " no particular argument.\n"                                        \
    "\n"                                                                \
    "The following methods have to be defined for new classes:\n"       \
    "* pychrysalide.arch.ArchRegister.__hash__();\n"                    \
    "* pychrysalide.arch.ArchRegister.__cmp__();\n"                     \
    "* pychrysalide.arch.ArchRegister._print();\n"                      \
    "* pychrysalide.arch.ArchRegister._is_base_pointer();\n"            \
    "* pychrysalide.arch.ArchRegister._is_stack_pointer().\n"           \
    "\n"                                                                \
    "Chrysalide creates an internal glue to provide rich comparisons"   \
    " for registers based on the old-style *__cmp__* function."

    /* Validations diverses */

    base = get_python_arch_register_type();

    if (type == base)
    {
        result = NULL;
        PyErr_Format(PyExc_RuntimeError, _("%s is an abstract class"), type->tp_name);
        goto exit;
    }

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_ARCH_REGISTER, type->tp_name,
                               (GClassInitFunc)py_arch_register_init_gclass, NULL, NULL);

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
*  Description : Initialise la classe des registres.                          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_arch_register_init_gclass(GArchRegisterClass *class, gpointer unused)
{
    class->hash = py_arch_register___hash___wrapper;
    class->compare = py_arch_register___cmp___wrapper;
    class->print = py_arch_register_print_wrapper;
    class->is_bp = py_arch_register_is_base_pointer_wrapper;
    class->is_sp = py_arch_register_is_stack_pointer_wrapper;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg = registre visé par la procédure.                        *
*                                                                             *
*  Description : Produit une empreinte à partir d'un registre.                *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static guint py_arch_register___hash___wrapper(const GArchRegister *reg)
{
    guint result;                           /* Empreinte à retourner       */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */

#define ARCH_REGISTER_HASH_WRAPPER PYTHON_WRAPPER_DEF           \
(                                                               \
    __hash__, "$self, /",                                       \
    METH_NOARGS,                                                \
    "Abstract method used to produce a hash of the object. The" \
    " result must be an integer value."                         \
)

    result = 0;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(reg));

    if (has_python_method(pyobj, "__hash__"))
    {
        pyret = run_python_method(pyobj, "__hash__", NULL);

        if (pyret != NULL)
        {
            if (PyLong_Check(pyret))
                result = PyLong_AsUnsignedLong(pyret);

            Py_DECREF(pyret);

        }

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = premier registre à consulter.                            *
*                b = second registre à consulter.                             *
*                                                                             *
*  Description : Compare un registre avec un autre.                           *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_arch_register___cmp___wrapper(const GArchRegister *a, const GArchRegister *b)
{
    int result;                             /* Empreinte à retourner       */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan de consultation       */

#define ARCH_REGISTER_CMP_WRAPPER PYTHON_WRAPPER_DEF            \
(                                                               \
    __cmp__, "$self, other, /",                                 \
    METH_VARARGS,                                               \
    "Abstract method used to compare the register with another" \
    " one. This second object is always an"                     \
    " pychrysalide.arch.ArchRegister instance.\n"               \
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

        Py_DECREF(args);

        Py_XDECREF(pyret);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg = registre visé par la procédure.                        *
*                                                                             *
*  Description : Traduit un registre en version humainement lisible.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_arch_register_print_wrapper(const GArchRegister *reg, GBufferLine *line)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan de consultation       */

#define ARCH_REGISTER_PRINT_WRAPPER PYTHON_WRAPPER_DEF              \
(                                                                   \
    _print, "$self, line, /",                                       \
    METH_VARARGS,                                                   \
    "Abstract method used to print the register into a rendering"   \
    " line, which is a provided pychrysalide.glibext.BufferLine"    \
    " instance."                                                    \
)

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(reg));

    if (has_python_method(pyobj, "_print"))
    {
        args = PyTuple_New(1);
        PyTuple_SetItem(args, 0, pygobject_new(G_OBJECT(line)));

        pyret = run_python_method(pyobj, "_print", args);

        Py_DECREF(args);

        Py_XDECREF(pyret);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg = registre visé par la procédure.                        *
*                                                                             *
*  Description : Indique si le registre correspond à ebp ou similaire.        *
*                                                                             *
*  Retour      : true si la correspondance est avérée, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_arch_register_is_base_pointer_wrapper(const GArchRegister *reg)
{
    bool result;                            /* Bilan à renvoyer            */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */

#define ARCH_REGISTER_IS_BASE_POINTER_WRAPPER PYTHON_WRAPPER_DEF    \
(                                                                   \
    _is_base_pointer, "$self, /",                                   \
    METH_NOARGS,                                                    \
    "Abstract method used to tell if the register is handling a"    \
    " base pointer. The result must be a boolean value."            \
)

    result = false;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(reg));

    if (has_python_method(pyobj, "_is_base_pointer"))
    {
        pyret = run_python_method(pyobj, "_is_base_pointer", NULL);

        if (pyret != NULL)
        {
            result = (pyret == Py_True);

            Py_DECREF(pyret);

        }

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg = registre visé par la procédure.                        *
*                                                                             *
*  Description : Indique si le registre correspond à esp ou similaire.        *
*                                                                             *
*  Retour      : true si la correspondance est avérée, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_arch_register_is_stack_pointer_wrapper(const GArchRegister *reg)
{
    bool result;                            /* Bilan à renvoyer            */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */

#define ARCH_REGISTER_IS_STACK_POINTER_WRAPPER PYTHON_WRAPPER_DEF   \
(                                                                   \
    _is_stack_pointer, "$self, /",                                  \
    METH_NOARGS,                                                    \
    "Abstract method used to tell if the register is handling a"    \
    " stack pointer. The result must be a boolean value."           \
)

    result = false;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(reg));

    if (has_python_method(pyobj, "_is_stack_pointer"))
    {
        pyret = run_python_method(pyobj, "_is_stack_pointer", NULL);

        if (pyret != NULL)
        {
            result = (pyret == Py_True);

            Py_DECREF(pyret);

        }

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                              PUR REGISTRE DU MATERIEL                              */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : a  = premier object Python à consulter.                      *
*                b  = second object Python à consulter.                       *
*                op = type de comparaison menée.                              *
*                                                                             *
*  Description : Effectue une comparaison avec un objet Python 'ArchRegister'.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_arch_register_richcompare(PyObject *a, PyObject *b, int op)
{
    PyObject *result;                       /* Bilan à retourner           */
    int ret;                                /* Bilan de lecture des args.  */
    const GArchRegister *reg_a;             /* Premier élément à traiter   */
    const GArchRegister *reg_b;             /* Second élément à traiter    */
    int status;                             /* Résultat d'une comparaison  */

    ret = PyObject_IsInstance(b, (PyObject *)get_python_arch_register_type());
    if (!ret)
    {
        result = Py_NotImplemented;
        goto cmp_done;
    }

    reg_a = G_ARCH_REGISTER(pygobject_get(a));
    reg_b = G_ARCH_REGISTER(pygobject_get(b));

    status = py_arch_register___cmp___wrapper(reg_a, reg_b);

    result = status_to_rich_cmp_state(status, op);

 cmp_done:

    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique si le registre correspond à ebp ou similaire.        *
*                                                                             *
*  Retour      : True si la correspondance est avérée, False sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_arch_register_is_base_pointer(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    GArchRegister *reg;                     /* Registre visé               */
    bool status;                            /* Bilan de consultation       */

#define ARCH_REGISTER_IS_BASE_POINTER_ATTRIB PYTHON_IS_DEF_FULL     \
(                                                                   \
    base_pointer, py_arch_register,                                 \
    "Tell if the register is a base pointer or not."                \
)

    reg = G_ARCH_REGISTER(pygobject_get(self));

    status = g_arch_register_is_base_pointer(reg);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique si le registre correspond à esp ou similaire.        *
*                                                                             *
*  Retour      : True si la correspondance est avérée, False sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_arch_register_is_stack_pointer(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    GArchRegister *reg;                     /* Registre visé               */
    bool status;                            /* Bilan de consultation       */

#define ARCH_REGISTER_IS_STACK_POINTER_ATTRIB PYTHON_IS_DEF_FULL    \
(                                                                   \
    stack_pointer, py_arch_register,                                \
    "Tell if the register is a stack pointer or not."               \
)

    reg = G_ARCH_REGISTER(pygobject_get(self));

    status = g_arch_register_is_stack_pointer(reg);

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

PyTypeObject *get_python_arch_register_type(void)
{
    static PyMethodDef py_arch_register_methods[] = {
        ARCH_REGISTER_HASH_WRAPPER,
        ARCH_REGISTER_CMP_WRAPPER,
        ARCH_REGISTER_PRINT_WRAPPER,
        ARCH_REGISTER_IS_BASE_POINTER_WRAPPER,
        ARCH_REGISTER_IS_STACK_POINTER_WRAPPER,
        { NULL }
    };

    static PyGetSetDef py_arch_register_getseters[] = {
        ARCH_REGISTER_IS_BASE_POINTER_ATTRIB,
        ARCH_REGISTER_IS_STACK_POINTER_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_arch_register_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.arch.ArchRegister",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_IS_ABSTRACT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = ARCH_REGISTER_DOC,

        .tp_richcompare = py_arch_register_richcompare,

        .tp_methods     = py_arch_register_methods,
        .tp_getset      = py_arch_register_getseters,

        .tp_new         = py_arch_register_new,

    };

    return &py_arch_register_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.arch.ArchRegister'.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_arch_register_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'ArchRegister'  */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_arch_register_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.arch");

        dict = PyModule_GetDict(module);

        if (!ensure_python_serializable_object_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_ARCH_REGISTER, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en registre d'architecture.               *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_arch_register(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_arch_register_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to architecture register");
            break;

        case 1:
            *((GArchRegister **)dst) = G_ARCH_REGISTER(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
