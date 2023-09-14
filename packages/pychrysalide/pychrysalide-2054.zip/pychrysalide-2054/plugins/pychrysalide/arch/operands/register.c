
/* Chrysalide - Outil d'analyse de fichiers binaires
 * register.c - équivalent Python du fichier "arch/operands/register.c"
 *
 * Copyright (C) 2019-2020 Cyrille Bagard
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


#include <pygobject.h>


#include <i18n.h>
#include <arch/operands/register-int.h>
#include <plugins/dt.h>


#include "../operand.h"
#include "../register.h"
#include "../../access.h"
#include "../../helpers.h"
#include "../../glibext/bufferline.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Accompagne la création d'une instance dérivée en Python. */
static PyObject *py_register_operand_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise la classe des descriptions de fichier binaire. */
static void py_register_operand_init_gclass(GRegisterOperandClass *, gpointer);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_register_operand_init(PyObject *, PyObject *, PyObject *);



/* ------------------------- REGISTRE SOUS FORME D'OPERANDE ------------------------- */


/* Compare un opérande avec un autre. */
static PyObject *py_register_operand___cmp__(PyObject *, PyObject *);

/* Traduit un opérande en version humainement lisible. */
static PyObject *py_register_operand__print(PyObject *, PyObject *);

/* Fournit le registre associé à l'opérande. */
static PyObject *py_register_operand_get_register(PyObject *, void *);



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

static PyObject *py_register_operand_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

    /* Validations diverses */

    base = get_python_register_operand_type();

    if (type == base)
        goto simple_way;

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_REGISTER_OPERAND, type->tp_name,
                               (GClassInitFunc)py_register_operand_init_gclass, NULL, NULL);

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
*  Paramètres  : class  = classe à initialiser.                               *
*                unused = données non utilisées ici.                          *
*                                                                             *
*  Description : Initialise la classe des descriptions de fichier binaire.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_register_operand_init_gclass(GRegisterOperandClass *class, gpointer unused)
{

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

static int py_register_operand_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    GArchRegister *reg;                     /* Registre brut transmis      */
    int ret;                                /* Bilan de lecture des args.  */
    GRegisterOperand *operand;              /* Opérande à manipuler        */

#define REGISTER_OPERAND_DOC                                                \
    "The RegisterOperand object handles an operand carrying an"             \
    " architecture register.\n"                                             \
    "\n"                                                                    \
    "Instances can be created using the following constructor:\n"           \
    "\n"                                                                    \
    "    RegisterOperand(reg)"                                              \
    "\n"                                                                    \
    "Where reg is an architecture register defined from a subclass of"      \
    " pychrysalide.arch.ArchRegister."

    /* Récupération des paramètres */

    ret = PyArg_ParseTuple(args, "O&", convert_to_arch_register, &reg);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    operand = G_REGISTER_OPERAND(pygobject_get(self));

    g_object_ref(G_OBJECT(reg));
    operand->reg = reg;

    return 0;

}



/* ---------------------------------------------------------------------------------- */
/*                           REGISTRE SOUS FORME D'OPERANDE                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self = serveur à manipuler.                                  *
*                args = arguments associés à l'appel.                         *
*                                                                             *
*  Description : Compare un opérande avec un autre.                           *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_register_operand___cmp__(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    GRegisterOperand *other;                /* Autre opérande à manipuler  */
    int ret;                                /* Bilan de lecture des args.  */
    GRegisterOperand *operand;              /* Elément à manipuler         */
    int status;                             /* Bilan de comparaison        */

#define REGISTER_OPERAND_CMP_METHOD PYTHON_METHOD_DEF               \
(                                                                   \
    __cmp__, "$self, other, /",                                     \
    METH_VARARGS, py_register_operand,                              \
    "Implementation of the required method used to compare the"     \
    " operand with another one. This second object is always"       \
    " a pychrysalide.arch.RegisterOperand instance.\n"              \
    "\n"                                                            \
    "See the parent class for more information about this method."  \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_register_operand, &other);
    if (!ret) return NULL;

    operand = G_REGISTER_OPERAND(pygobject_get(self));

    status = g_arch_operand_compare(G_ARCH_OPERAND(operand), G_ARCH_OPERAND(other));

    result = PyLong_FromLong(status);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = serveur à manipuler.                                  *
*                args = arguments associés à l'appel.                         *
*                                                                             *
*  Description : Traduit un opérande en version humainement lisible.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_register_operand__print(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    GBufferLine *line;                      /* Ligne fournie à peupler     */
    int ret;                                /* Bilan de lecture des args.  */
    GRegisterOperand *operand;              /* Elément à manipuler         */

#define REGISTER_OPERAND_PRINT_METHOD PYTHON_METHOD_DEF                 \
(                                                                       \
    _print, "$self, line, /",                                           \
    METH_VARARGS, py_register_operand,                                  \
    "Implementation of the required method used to print the operand"   \
    " into a rendering line, which is a provided"                       \
    " pychrysalide.glibext.BufferLine instance.\n"                      \
    "\n"                                                                \
    "See the parent class for more information about this method."      \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_buffer_line, &line);
    if (!ret) return NULL;

    operand = G_REGISTER_OPERAND(pygobject_get(self));

    g_arch_operand_print(G_ARCH_OPERAND(operand), line);

    result = Py_None;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le registre associé à l'opérande.                    *
*                                                                             *
*  Retour      : Représentation interne du registre.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_register_operand_get_register(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    GRegisterOperand *operand;              /* Version GLib de l'opérande  */
    GArchRegister *reg;                     /* Registre lié à l'opérande   */

#define REGISTER_OPERAND_REGISTER_ATTRIB PYTHON_GET_DEF_FULL    \
(                                                               \
    register, py_register_operand,                              \
    "Provide the register used by the operand, as an"           \
    " instance of type pychrysalide.arch.ArchRegister."         \
)

    operand = G_REGISTER_OPERAND(pygobject_get(self));

    reg = g_register_operand_get_register(operand);

    if (reg == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }

    else
    {
        result = pygobject_new(G_OBJECT(reg));
        g_object_unref(reg);
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

PyTypeObject *get_python_register_operand_type(void)
{
    static PyMethodDef py_register_operand_methods[] = {
        REGISTER_OPERAND_CMP_METHOD,
        REGISTER_OPERAND_PRINT_METHOD,
        { NULL }
    };

    static PyGetSetDef py_register_operand_getseters[] = {
        REGISTER_OPERAND_REGISTER_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_register_operand_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.arch.operands.RegisterOperand",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = REGISTER_OPERAND_DOC,

        .tp_methods     = py_register_operand_methods,
        .tp_getset      = py_register_operand_getseters,

        .tp_init        = py_register_operand_init,
        .tp_new         = py_register_operand_new,

    };

    return &py_register_operand_type;

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

bool ensure_python_register_operand_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'ArchOperand'   */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_register_operand_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.arch.operands");

        dict = PyModule_GetDict(module);

        if (!ensure_python_arch_operand_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_REGISTER_OPERAND, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en opérande de registre.                  *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_register_operand(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_register_operand_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to register operand");
            break;

        case 1:
            *((GRegisterOperand **)dst) = G_REGISTER_OPERAND(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
