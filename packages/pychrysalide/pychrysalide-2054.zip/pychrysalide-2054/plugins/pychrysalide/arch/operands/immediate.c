
/* Chrysalide - Outil d'analyse de fichiers binaires
 * immediate.c - équivalent Python du fichier "arch/operands/immediate.h"
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


#include "immediate.h"


#include <assert.h>
#include <pygobject.h>


#include <i18n.h>


#include <arch/operands/immediate.h>


#include "constants.h"
#include "rename.h"
#include "targetable.h"
#include "../operand.h"
#include "../../access.h"
#include "../../helpers.h"
#include "../../analysis/content.h"
#include "../../glibext/bufferline.h"



/* Crée un nouvel objet Python de type 'ImmOperand'. */
static PyObject *py_imm_operand_new(PyTypeObject *, PyObject *, PyObject *);

/* Compare un opérande avec un autre. */
static PyObject *py_imm_operand___cmp__(PyObject *, PyObject *);

/* Traduit un opérande en version humainement lisible. */
static PyObject *py_imm_operand__print(PyObject *, PyObject *);

/* Renseigne la taille de la valeur indiquée à la construction. */
static PyObject *py_imm_operand_get_size(PyObject *, void *);

/* Fournit la valeur portée par une opérande numérique. */
static PyObject *py_imm_operand_get_value(PyObject *, void *);

/* Indique le format textuel par défaut de la valeur. */
static PyObject *py_imm_operand_get_default_display(PyObject *, void *);

/* Définit le format textuel par défaut de la valeur. */
static int py_imm_operand_set_default_display(PyObject *, PyObject *, void *);

/* Indique la grande ligne du format textuel de la valeur. */
static PyObject *py_imm_operand_get_display(PyObject *, void *);

/* Définit la grande ligne du format textuel de la valeur. */
static int py_imm_operand_set_display(PyObject *, PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de l'objet à instancier.                         *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Crée un nouvel objet Python de type 'ImmOperand'.            *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_imm_operand_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Instance à retourner        */
    unsigned int raw_size;                  /* Taille obtenue de Python    */
    unsigned long long value;               /* Valeur brute à représenter  */
    int ret;                                /* Bilan de lecture des args.  */
    MemoryDataSize size;                    /* Taille des données finale   */
    GArchOperand *operand;                  /* Création GLib à transmettre */

#define IMM_OPERAND_DOC                                                 \
    "The ImmOperand deals with immediate value as operand."             \
    "\n"                                                                \
    "There are several ways to display these values in a disassembly,"  \
    " the operand handles that.\n"                                      \
    "\n"                                                                \
    "Instances can be created using the following constructor:\n"       \
    "\n"                                                                \
    "    ImmOperand(size, value)"                                       \
    "\n"                                                                \
    "Where size specifies the original size of the provided value, as"  \
    " a pychrysalide.analysis.BinContent.MemoryDataSize."

    ret = PyArg_ParseTuple(args, "IK", &raw_size, &value);
    if (!ret) return NULL;

    size = raw_size;

    if (size != MDS_UNDEFINED
        && !(MDS_4_BITS_UNSIGNED <= size && size <= MDS_64_BITS_UNSIGNED)
        && !(MDS_4_BITS_SIGNED <= size && size <= MDS_64_BITS_SIGNED))
    {
        PyErr_SetString(PyExc_ValueError, _("Invalid size to build an immediate operand"));
        return NULL;
    }

    operand = g_imm_operand_new_from_value(size, value);

    result = pygobject_new(G_OBJECT(operand));

    g_object_unref(operand);

    return (PyObject *)result;

}


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

static PyObject *py_imm_operand___cmp__(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    GImmOperand *other;                     /* Autre opérande à manipuler  */
    int ret;                                /* Bilan de lecture des args.  */
    GImmOperand *operand;                   /* Elément à manipuler         */
    int status;                             /* Bilan de comparaison        */

#define IMM_OPERAND_CMP_METHOD PYTHON_METHOD_DEF                    \
(                                                                   \
    __cmp__, "$self, other, /",                                     \
    METH_VARARGS, py_imm_operand,                                   \
    "Implementation of the required method used to compare the"     \
    " operand with another one. This second object is always"       \
    " an pychrysalide.arch.ImmOperand instance.\n"                  \
    "\n"                                                            \
    "See the parent class for more information about this method."  \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_imm_operand, &other);
    if (!ret) return NULL;

    operand = G_IMM_OPERAND(pygobject_get(self));

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

static PyObject *py_imm_operand__print(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    GBufferLine *line;                      /* Ligne fournie à peupler     */
    int ret;                                /* Bilan de lecture des args.  */
    GImmOperand *operand;                   /* Elément à manipuler         */

#define IMM_OPERAND_PRINT_METHOD PYTHON_METHOD_DEF                      \
(                                                                       \
    _print, "$self, line, /",                                           \
    METH_VARARGS, py_imm_operand,                                       \
    "Implementation of the required method used to print the operand"   \
    " into a rendering line, which is a provided"                       \
    " pychrysalide.glibext.BufferLine instance.\n"                      \
    "\n"                                                                \
    "See the parent class for more information about this method."      \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_buffer_line, &line);
    if (!ret) return NULL;

    operand = G_IMM_OPERAND(pygobject_get(self));

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
*  Description : Renseigne la taille de la valeur indiquée à la construction. *
*                                                                             *
*  Retour      : Taille de la valeur représentée en mémoire.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_imm_operand_get_size(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    GImmOperand *operand;                   /* Version GLib de l'opérande  */
    MemoryDataSize size;                    /* Type de donnée représentée  */

#define IMM_OPERAND_SIZE_ATTRIB PYTHON_GET_DEF_FULL                 \
(                                                                   \
    size, py_imm_operand,                                           \
    "Get or set the size of the value contained in the operand."    \
    "\n"                                                            \
    "The property is a value of type"                               \
    " pychrysalide.analysis.BinContent.MemoryDataSize."             \
)

    operand = G_IMM_OPERAND(pygobject_get(self));
    size = g_imm_operand_get_size(operand);

    result = cast_with_constants_group_from_type(get_python_binary_content_type(), "MemoryDataSize", size);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la valeur portée par une opérande numérique.         *
*                                                                             *
*  Retour      : Valeur contenue dans l'opérande, ou None en cas de soucis.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_imm_operand_get_value(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    GImmOperand *operand;                   /* Version GLib de l'opérande  */
    MemoryDataSize size;                    /* Type de donnée représentée  */
    uint8_t uval8;                          /* Valeur sur 8 bits           */
    uint16_t uval16;                        /* Valeur sur 16 bits          */
    uint32_t uval32;                        /* Valeur sur 32 bits          */
    uint64_t uval64;                        /* Valeur sur 64 bits          */
    int8_t sval8;                           /* Valeur sur 8 bits           */
    int16_t sval16;                         /* Valeur sur 16 bits          */
    int32_t sval32;                         /* Valeur sur 32 bits          */
    int64_t sval64;                         /* Valeur sur 64 bits          */

#define IMM_OPERAND_VALUE_ATTRIB PYTHON_GET_DEF_FULL    \
(                                                       \
    value, py_imm_operand,                              \
    "Value of the immediate operand, as an integer."    \
)

    operand = G_IMM_OPERAND(pygobject_get(self));

    size = g_imm_operand_get_size(operand);

    switch (size)
    {
        /* Pour GCC... */
        case MDS_UNDEFINED:
            result = Py_None;
            Py_INCREF(result);
            break;
        case MDS_4_BITS_UNSIGNED:
        case MDS_8_BITS_UNSIGNED:
            g_imm_operand_get_value(operand, size, &uval8);
            result = PyLong_FromUnsignedLong(uval8);
            break;
        case MDS_16_BITS_UNSIGNED:
            g_imm_operand_get_value(operand, size, &uval16);
            result = PyLong_FromUnsignedLong(uval16);
            break;
        case MDS_32_BITS_UNSIGNED:
            g_imm_operand_get_value(operand, size, &uval32);
            result = PyLong_FromUnsignedLong(uval32);
            break;
        case MDS_64_BITS_UNSIGNED:
            g_imm_operand_get_value(operand, size, &uval64);
            result = PyLong_FromUnsignedLongLong(uval64);
            break;
        case MDS_4_BITS_SIGNED:
        case MDS_8_BITS_SIGNED:
            g_imm_operand_get_value(operand, size, &sval8);
            result = PyLong_FromLong(sval8);
            break;
        case MDS_16_BITS_SIGNED:
            g_imm_operand_get_value(operand, size, &sval16);
            result = PyLong_FromLong(sval16);
            break;
        case MDS_32_BITS_SIGNED:
            g_imm_operand_get_value(operand, size, &sval32);
            result = PyLong_FromLong(sval32);
            break;
        case MDS_64_BITS_SIGNED:
            g_imm_operand_get_value(operand, size, &sval64);
            result = PyLong_FromLongLong(sval64);
            break;

        /* Pour GCC... */
        default:
            assert(false);
            result = Py_None;
            Py_INCREF(result);
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique le format textuel par défaut de la valeur.           *
*                                                                             *
*  Retour      : Format global d'un affichage de valeur.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_imm_operand_get_default_display(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    GImmOperand *operand;                   /* Version GLib de l'opérande  */
    ImmOperandDisplay display;              /* Type d'affichage courant    */

#define IMM_OPERAND_DEFAULT_DISPLAY_ATTRIB PYTHON_GETSET_DEF_FULL       \
(                                                                       \
    default_display, py_imm_operand,                                    \
    "Define of the immediate operand default textual representation."   \
    "\n"                                                                \
    "The property is a value of type"                                   \
    " pychrysalide.arch.operands.ImmOperand.ImmOperandDisplay."         \
)

    operand = G_IMM_OPERAND(pygobject_get(self));
    display = g_imm_operand_get_default_display(operand);

    result = cast_with_constants_group_from_type(get_python_imm_operand_type(), "ImmOperandDisplay", display);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Définit le format textuel par défaut de la valeur.           *
*                                                                             *
*  Retour      : Bilan de l'opération pour Python.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_imm_operand_set_default_display(PyObject *self, PyObject *value, void *closure)
{
    ImmOperandDisplay display;              /* Type d'affichage demandé    */
    GImmOperand *operand;                   /* Version GLib de l'opérande  */

    if (!PyLong_Check(value))
    {
        PyErr_SetString(PyExc_TypeError, _("Invalid display type"));
        return -1;
    }

    display = PyLong_AsUnsignedLong(value);

    if (!(IOD_BIN <= display && display <= IOD_CHAR))
    {
        PyErr_SetString(PyExc_TypeError, _("Invalid display type"));
        return -1;
    }

    operand = G_IMM_OPERAND(pygobject_get(self));

    g_imm_operand_set_default_display(operand, display);

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique la grande ligne du format textuel de la valeur.      *
*                                                                             *
*  Retour      : Format global d'un affichage de valeur.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_imm_operand_get_display(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    GImmOperand *operand;                   /* Version GLib de l'opérande  */
    ImmOperandDisplay display;              /* Type d'affichage courant    */

#define IMM_OPERAND_DISPLAY_ATTRIB PYTHON_GETSET_DEF_FULL               \
(                                                                       \
    display, py_imm_operand,                                            \
    "Define of the immediate operand current textual representation."   \
    "\n"                                                                \
    "The property is a value of type"                                   \
    " pychrysalide.arch.operands.ImmOperand.ImmOperandDisplay."         \
)

    operand = G_IMM_OPERAND(pygobject_get(self));
    display = g_imm_operand_get_display(operand);

    result = cast_with_constants_group_from_type(get_python_imm_operand_type(), "ImmOperandDisplay", display);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Définit la grande ligne du format textuel de la valeur.      *
*                                                                             *
*  Retour      : Bilan de l'opération pour Python.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_imm_operand_set_display(PyObject *self, PyObject *value, void *closure)
{
    ImmOperandDisplay display;              /* Type d'affichage demandé    */
    GImmOperand *operand;                   /* Version GLib de l'opérande  */

    if (!PyLong_Check(value))
    {
        PyErr_SetString(PyExc_TypeError, _("Invalid display type"));
        return -1;
    }

    display = PyLong_AsUnsignedLong(value);

    if (!(IOD_BIN <= display && display <= IOD_CHAR))
    {
        PyErr_SetString(PyExc_TypeError, _("Invalid display type"));
        return -1;
    }

    operand = G_IMM_OPERAND(pygobject_get(self));

    g_imm_operand_set_display(operand, display);

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

PyTypeObject *get_python_imm_operand_type(void)
{
    static PyMethodDef py_imm_operand_methods[] = {
        IMM_OPERAND_CMP_METHOD,
        IMM_OPERAND_PRINT_METHOD,
        { NULL }
    };

    static PyGetSetDef py_imm_operand_getseters[] = {
        IMM_OPERAND_SIZE_ATTRIB,
        IMM_OPERAND_VALUE_ATTRIB,
        IMM_OPERAND_DEFAULT_DISPLAY_ATTRIB,
        IMM_OPERAND_DISPLAY_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_imm_operand_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.arch.operands.ImmOperand",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = IMM_OPERAND_DOC,

        .tp_methods     = py_imm_operand_methods,
        .tp_getset      = py_imm_operand_getseters,
        .tp_new         = py_imm_operand_new

    };

    return &py_imm_operand_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.arch.ImmOperand'.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_imm_operand_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'ImmOperand'    */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_imm_operand_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.arch.operands");

        dict = PyModule_GetDict(module);

        if (!ensure_python_arch_operand_is_registered())
            return false;

        if (!ensure_python_targetable_operand_is_registered())
            return false;

        if (!ensure_python_renameable_operand_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_IMM_OPERAND, type))
            return false;

        if (!define_imm_operand_constants(type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en opérande de valeur immédiate.          *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_imm_operand(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_imm_operand_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to immediate operand");
            break;

        case 1:
            *((GImmOperand **)dst) = G_IMM_OPERAND(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
