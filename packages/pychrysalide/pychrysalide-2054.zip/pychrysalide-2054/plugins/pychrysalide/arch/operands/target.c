
/* Chrysalide - Outil d'analyse de fichiers binaires
 * target.c - équivalent Python du fichier "arch/operands/target.c"
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


#include "target.h"


#include <pygobject.h>


#include <i18n.h>
#include <arch/operands/target-int.h>
#include <plugins/dt.h>


#include "targetable.h"
#include "../operand.h"
#include "../../access.h"
#include "../../helpers.h"
#include "../../analysis/constants.h"
#include "../../analysis/content.h"
#include "../../arch/vmpa.h"
#include "../../format/format.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Accompagne la création d'une instance dérivée en Python. */
static PyObject *py_target_operand_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise la classe des descriptions de fichier binaire. */
static void py_target_operand_init_gclass(GTargetOperandClass *, gpointer);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_target_operand_init(PyObject *, PyObject *, PyObject *);



/* ------------------ OPERANDES CONSTITUANT DE PURS INTERMEDIAIRES ------------------ */


/* Tente une résolution de symbole. */
static PyObject *py_target_operand_resolve(PyObject *, PyObject *);

/* Renseigne la taille de la valeur indiquée à la construction. */
static PyObject *py_target_operand_get_size(PyObject *, void *);

/* Fournit les indications concernant le symbole associé. */
static PyObject *py_target_operand_get_symbol(PyObject *, void *);



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

static PyObject *py_target_operand_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

    /* Validations diverses */

    base = get_python_target_operand_type();

    if (type == base)
        goto simple_way;

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_TARGET_OPERAND, type->tp_name,
                               (GClassInitFunc)py_target_operand_init_gclass, NULL, NULL);

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

static void py_target_operand_init_gclass(GTargetOperandClass *class, gpointer unused)
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

static int py_target_operand_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    MemoryDataSize size;                    /* Taille des adresses mémoire */
    vmpa2t *addr;                           /* Emplacement de symbole      */
    int ret;                                /* Bilan de lecture des args.  */
    GTargetOperand *operand;                /* Opérande à manipuler        */
    tarop_extra_data_t *extra;              /* Données insérées à modifier */

#define TARGET_OPERAND_DOC                                                  \
    "The TargetOperand object translates immediate values as symbols.\n"    \
    "\n"                                                                    \
    "Instances can be created using the following constructor:\n"           \
    "\n"                                                                    \
    "    TargetOperand(size, addr)"                                         \
    "\n"                                                                    \
    "Where size is a pychrysalide.analysis.BinContent.MemoryDataSize value" \
    " describing the size of memory addresses and addr is the location of"  \
    " a symbol to target, as a pychrysalide.arch.vmpa value."

    /* Récupération des paramètres */

    ret = PyArg_ParseTuple(args, "O&O&", convert_to_memory_data_size, &size, convert_any_to_vmpa, &addr);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    operand = G_TARGET_OPERAND(pygobject_get(self));

    extra = GET_TARGET_OP_EXTRA(operand);

    extra->size = size;

    copy_vmpa(&operand->addr, addr);

    clean_vmpa_arg(addr);

    return 0;

}



/* ---------------------------------------------------------------------------------- */
/*                    OPERANDES CONSTITUANT DE PURS INTERMEDIAIRES                    */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self = serveur à manipuler.                                  *
*                args = arguments d'appel non utilisés ici.                   *
*                                                                             *
*  Description : Tente une résolution de symbole.                             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_target_operand_resolve(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    GBinFormat *format;                     /* Format de binaire reconnu   */
    int strict;                             /* Perfection attendue ?       */
    int ret;                                /* Bilan de lecture des args.  */
    GTargetOperand *operand;                /* Version GLib de l'opérande  */
    bool status;                            /* Bilan de l'opération        */

#define TARGET_OPERAND_RESOLVE_METHOD PYTHON_METHOD_DEF             \
(                                                                   \
    resolve, "$self, format, strict, /",                            \
    METH_VARARGS, py_target_operand,                                \
    "Try to resolve the value carried by the operand as the"        \
    " address of an existing symbol.\n"                             \
    "\n"                                                            \
    "The provided format has to be a pychrysalide.format.BinFormat" \
    " instance and the *strict* argument defines if an offset is"   \
    " allowed between the value and the symbol's address.\n"        \
    "\n"                                                            \
    "The result is True if the resolution is successful, False"     \
    " otherwise."                                                   \
)

    ret = PyArg_ParseTuple(args, "O&p", convert_to_binary_format, &format, &strict);
    if (!ret) return NULL;

    operand = G_TARGET_OPERAND(pygobject_get(self));

    status = g_target_operand_resolve(operand, format, strict);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Renseigne la taille de la valeur indiquée à la construction. *
*                                                                             *
*  Retour      : Taille de la valeur représentée en mémoire.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_target_operand_get_size(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    GTargetOperand *operand;                /* Version GLib de l'opérande  */
    MemoryDataSize size;                    /* Taille à transmettre        */

#define TARGET_OPERAND_SIZE_ATTRIB PYTHON_GET_DEF_FULL                          \
(                                                                               \
    size, py_target_operand,                                                    \
    "Provide the size of the value carried by the operand.\n"                   \
    "\n"                                                                        \
    "The result is a pychrysalide.analysis.BinContent.MemoryDataSize value."    \
)

    operand = G_TARGET_OPERAND(pygobject_get(self));

    size = g_target_operand_get_size(operand);

    result = cast_with_constants_group_from_type(get_python_binary_content_type(), "MemoryDataSize", size);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit les indications concernant le symbole associé.       *
*                                                                             *
*  Retour      : Symbole résolu ou NULL si aucun.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_target_operand_get_symbol(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    GTargetOperand *operand;                /* Version GLib de l'opérande  */
    GBinSymbol *symbol;                     /* Symbole attaché à l'opérande*/
    phys_t diff;                            /* Décalage avec la base       */

#define TARGET_OPERAND_SYMBOL_ATTRIB PYTHON_GET_DEF_FULL        \
(                                                               \
    symbol, py_target_operand,                                  \
    "Give the resolved symbol linked to the operand.\n"         \
    "\n"                                                        \
    "The result is a pychrysalide.format.BinSymbol instance"    \
    " or None."                                                 \
)

    operand = G_TARGET_OPERAND(pygobject_get(self));

    symbol = g_target_operand_get_symbol(operand, &diff);

    result = pygobject_new(G_OBJECT(symbol));
    g_object_unref(symbol);

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

PyTypeObject *get_python_target_operand_type(void)
{
    static PyMethodDef py_target_operand_methods[] = {
        TARGET_OPERAND_RESOLVE_METHOD,
        { NULL }
    };

    static PyGetSetDef py_target_operand_getseters[] = {
        TARGET_OPERAND_SIZE_ATTRIB,
        TARGET_OPERAND_SYMBOL_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_target_operand_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.arch.operands.TargetOperand",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = TARGET_OPERAND_DOC,

        .tp_methods     = py_target_operand_methods,
        .tp_getset      = py_target_operand_getseters,

        .tp_init        = py_target_operand_init,
        .tp_new         = py_target_operand_new,

    };

    return &py_target_operand_type;

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

bool ensure_python_target_operand_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'ArchOperand'   */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_target_operand_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.arch.operands");

        dict = PyModule_GetDict(module);

        if (!ensure_python_arch_operand_is_registered())
            return false;

        if (!ensure_python_targetable_operand_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_TARGET_OPERAND, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en opérande ciblant idéalement un symbole.*
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_target_operand(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_target_operand_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to target operand");
            break;

        case 1:
            *((GTargetOperand **)dst) = G_TARGET_OPERAND(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
