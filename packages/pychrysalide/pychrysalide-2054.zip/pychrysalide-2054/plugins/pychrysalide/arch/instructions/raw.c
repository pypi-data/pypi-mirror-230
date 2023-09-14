
/* Chrysalide - Outil d'analyse de fichiers binaires
 * raw.c - équivalent Python du fichier "arch/instructions/raw.h"
 *
 * Copyright (C) 2018-2020 Cyrille Bagard
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


#include "raw.h"


#include <pygobject.h>


#include <i18n.h>
#include <arch/instructions/raw.h>
#include <plugins/dt.h>


#include "constants.h"
#include "../instruction.h"
#include "../vmpa.h"
#include "../../access.h"
#include "../../helpers.h"
#include "../../analysis/content.h"



/* Accompagne la création d'une instance dérivée en Python. */
static PyObject *py_raw_instruction_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_raw_instruction_init(PyObject *, PyObject *, PyObject *);

/* Indique si le contenu de l'instruction est du bourrage. */
static PyObject *py_raw_instruction_get_padding(PyObject *, void *);

/* Marque l'instruction comme ne contenant que du bourrage. */
static int py_raw_instruction_set_padding(PyObject *, PyObject *, void *);

/* Indique si le contenu de l'instruction est un texte. */
static PyObject *py_raw_instruction_get_string(PyObject *, void *);

/* Marque l'instruction comme contenant une chaîne de texte. */
static int py_raw_instruction_set_string(PyObject *, PyObject *, void *);



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

static PyObject *py_raw_instruction_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

    /* Validations diverses */

    base = get_python_raw_instruction_type();

    if (type == base)
        goto simple_way;

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_RAW_INSTRUCTION, type->tp_name, NULL, NULL, NULL);

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

static int py_raw_instruction_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    int result;                             /* Bilan à retourner           */
    vmpa2t *addr;                           /* Texte de lecture            */
    unsigned long mem_size;                 /* Taille de portion brute     */
    unsigned long long value;               /* Valeur brute à considérer   */
    GBinContent *content;                   /* Contenu à lire au besoin    */
    unsigned long count;                    /* Nombre d'éléments à lister  */
    unsigned int endian;                    /* Type de boutisme impliqué   */
    int ret;                                /* Bilan de lecture des args.  */
    GArchInstruction *fake;                 /* Instruction à copier        */
    GArchInstruction *instr;                /* Instruction à manipuler     */
    size_t op_count;                        /* Nombre d'opérande à copier  */
    size_t i;                               /* Boucle de parcours          */
    GArchOperand *op;                       /* Opérande à transférer       */

    static char *kwlist[] = { "addr", "mem_size", "value", "content", "count", "endian", NULL };

#define RAW_INSTRUCTION_DOC                                                     \
    "The RawInstruction object handles data which is not (yet?) disassembled"   \
    " as code in a binary.\n"                                                   \
    "\n"                                                                        \
    "Raw values pointed by this kind of instruction can be immediate values"    \
    " or strings.\n"                                                            \
    "\n"                                                                        \
    "Instances can be created using one of the following constructors:\n"       \
    "\n"                                                                        \
    "    RawInstruction(addr, size, value=int)\n"                               \
    "    RawInstruction(addr, size, content=object, count=int, endian=int)"     \
    "\n"                                                                        \
    "Where addr is always a location defined by a pychrysalide.arch.vmpa"       \
    " object and size is a pychrysalide.analysis.BinContent.MemoryDataSize"     \
    " constant defining the size of the read immediate value(s).\n"             \
    "\n"                                                                        \
    "In the first case, value is used to build an immediate operand for the"    \
    " instruction.\n"                                                           \
    "\n"                                                                        \
    "In the second case, content is a pychrysalide.analysis.BinContent"         \
    " instance, count states how many items belong to the array and endian"     \
    " is a pychrysalide.analysis.BinContent.SourceEndian constant defining"     \
    " the byte order used to read values."

    result = -1;

    /* Récupération des paramètres */

    value = 0;
    content = NULL;
    count = 0;
    endian = 0;

    ret = PyArg_ParseTupleAndKeywords(args, kwds, "O&k|KO&kI", kwlist,
                                      convert_any_to_vmpa, &addr, &mem_size,
                                      &value, convert_to_binary_content, &content, &count, &endian);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) goto clean_exit;

    /* Eléments de base */

    if (content != NULL)
        fake = g_raw_instruction_new_array(content, mem_size, count, addr, endian);
    else
        fake = g_raw_instruction_new_from_value(addr, mem_size, value);

    if (fake == NULL)
    {
        PyErr_SetString(PyExc_ValueError, _("Unable to build the object with the given parameters."));
        goto clean_exit;
    }

    instr = G_ARCH_INSTRUCTION(pygobject_get(self));

    g_arch_instruction_lock_operands(fake);

    op_count = _g_arch_instruction_count_operands(fake);

    for (i = 0; i < op_count; i++)
    {
        op = _g_arch_instruction_get_operand(fake, i);
        g_arch_instruction_attach_extra_operand(instr, op);
    }

    g_arch_instruction_unlock_operands(fake);

    g_arch_instruction_set_range(instr, g_arch_instruction_get_range(fake));

    g_object_unref(G_OBJECT(fake));

    result = 0;

 clean_exit:

    clean_vmpa_arg(addr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = classe représentant une instruction.               *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Indique si le contenu de l'instruction est du bourrage.      *
*                                                                             *
*  Retour      : Valeur associée à la propriété consultée.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_raw_instruction_get_padding(PyObject *self, void *closure)
{
    PyObject *result;                       /* Conversion à retourner      */
    GRawInstruction *instr;                 /* Version native              */
    bool state;                             /* Etat courant à consulter    */

#define RAW_INSTRUCTION_PADDING_ATTRIB PYTHON_GETSET_DEF_FULL   \
(                                                               \
    padding, py_raw_instruction,                                \
    "Report if the instruction is seen as padding."             \
)

    instr = G_RAW_INSTRUCTION(pygobject_get(self));

    state = g_raw_instruction_is_padding(instr);

    result = state ? Py_True : Py_False;
    Py_INCREF(result);


    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Marque l'instruction comme ne contenant que du bourrage.     *
*                                                                             *
*  Retour      : Bilan de l'opération pour Python.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_raw_instruction_set_padding(PyObject *self, PyObject *value, void *closure)
{
    bool state;                             /* Nouvel état à définir       */
    GRawInstruction *instr;                 /* Version native              */

    if (value != Py_True && value != Py_False)
        return -1;

    state = (value == Py_True);

    instr = G_RAW_INSTRUCTION(pygobject_get(self));

    g_raw_instruction_mark_as_padding(instr, state);

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = classe représentant une instruction.               *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Indique si le contenu de l'instruction est un texte.         *
*                                                                             *
*  Retour      : Valeur associée à la propriété consultée.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_raw_instruction_get_string(PyObject *self, void *closure)
{
    PyObject *result;                       /* Conversion à retourner      */
    GRawInstruction *instr;                 /* Version native              */
    bool state;                             /* Etat courant à consulter    */

#define RAW_INSTRUCTION_STRING_ATTRIB PYTHON_GETSET_DEF_FULL    \
(                                                               \
    string, py_raw_instruction,                                 \
    "Report if the instruction is seen as a string."            \
)

    instr = G_RAW_INSTRUCTION(pygobject_get(self));

    state = g_raw_instruction_is_string(instr);

    result = state ? Py_True : Py_False;
    Py_INCREF(result);


    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Marque l'instruction comme contenant une chaîne de texte.    *
*                                                                             *
*  Retour      : Bilan de l'opération pour Python.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_raw_instruction_set_string(PyObject *self, PyObject *value, void *closure)
{
    bool state;                             /* Nouvel état à définir       */
    GRawInstruction *instr;                 /* Version native              */

    if (value != Py_True && value != Py_False)
        return -1;

    state = (value == Py_True);

    instr = G_RAW_INSTRUCTION(pygobject_get(self));

    g_raw_instruction_mark_as_string(instr, state);

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

PyTypeObject *get_python_raw_instruction_type(void)
{
    static PyMethodDef py_raw_instruction_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_raw_instruction_getseters[] = {
        RAW_INSTRUCTION_PADDING_ATTRIB,
        RAW_INSTRUCTION_STRING_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_raw_instruction_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.arch.instructions.RawInstruction",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = RAW_INSTRUCTION_DOC,

        .tp_methods     = py_raw_instruction_methods,
        .tp_getset      = py_raw_instruction_getseters,

        .tp_init        = py_raw_instruction_init,
        .tp_new         = py_raw_instruction_new,

    };

    return &py_raw_instruction_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.arch...RawInstruction'.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_raw_instruction_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'RawInstruction'*/
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_raw_instruction_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.arch.instructions");

        dict = PyModule_GetDict(module);

        if (!ensure_python_arch_instruction_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_RAW_INSTRUCTION, type))
            return false;

        if (!define_raw_instruction_constants(type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en instruction brute.                     *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_raw_instruction(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_raw_instruction_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to raw instruction");
            break;

        case 1:
            *((GRawInstruction **)dst) = G_RAW_INSTRUCTION(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
