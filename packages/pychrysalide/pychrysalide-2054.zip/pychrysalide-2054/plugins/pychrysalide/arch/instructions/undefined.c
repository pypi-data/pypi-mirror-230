
/* Chrysalide - Outil d'analyse de fichiers binaires
 * undefined.c - équivalent Python du fichier "arch/instructions/undefined.h"
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


#include "undefined.h"


#include <pygobject.h>


#include <i18n.h>
#include <arch/instructions/undefined-int.h>
#include <plugins/dt.h>


#include "constants.h"
#include "../instruction.h"
#include "../../access.h"
#include "../../helpers.h"



/* Accompagne la création d'une instance dérivée en Python. */
static PyObject *py_undef_instruction_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_undef_instruction_init(PyObject *, PyObject *, PyObject *);

/* Indique le type de conséquences réél de l'instruction. */
static PyObject *py_undef_instruction_get_behavior(PyObject *, void *);



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

static PyObject *py_undef_instruction_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

    /* Validations diverses */

    base = get_python_undefined_instruction_type();

    if (type == base)
        goto simple_way;

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_UNDEF_INSTRUCTION, type->tp_name, NULL, NULL, NULL);

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

static int py_undef_instruction_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    unsigned long behavior;                 /* Conséquence pour l'instruct°*/
    int ret;                                /* Bilan de lecture des args.  */
    GUndefInstruction *instr;               /* Instruction à manipuler     */
    undef_extra_data_t *extra;              /* Données insérées à modifier */

    static char *kwlist[] = { "behavior", NULL };

#define UNDEF_INSTRUCTION_DOC                                                   \
    "UndefInstruction represents all kinds of instructions which are"           \
    " officially not part of a runnable instruction set.\n"                     \
    "\n"                                                                        \
    "Instances can be created using the following constructor:\n"               \
    "\n"                                                                        \
    "    UndefInstruction(behavior)"                                            \
    "\n"                                                                        \
    "Where behavior is a"                                                       \
    " pychrysalide.arch.instructions.UndefInstruction.ExpectedBehavior"         \
    " constant describing the state of the CPU once the instruction is run."

    /* Récupération des paramètres */

    ret = PyArg_ParseTupleAndKeywords(args, kwds, "k", kwlist, &behavior);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    instr = G_UNDEF_INSTRUCTION(pygobject_get(self));

    extra = GET_UNDEF_INSTR_EXTRA(instr);

    extra->behavior = behavior;

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = classe représentant une instruction.               *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Indique le type de conséquences réél de l'instruction.       *
*                                                                             *
*  Retour      : Etat réel du CPU après l'exécution de l'instruction.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_undef_instruction_get_behavior(PyObject *self, void *closure)
{
    PyObject *result;                       /* Conversion à retourner      */
    GUndefInstruction *instr;               /* Version native              */
    InstrExpectedBehavior behavior;         /* Comportement attendu        */

#define UNDEF_INSTRUCTION_BEHAVIOR_ATTRIB PYTHON_GET_DEF_FULL           \
(                                                                       \
    behavior, py_undef_instruction,                                     \
    "Consequence carried by the undefined instruction.\n"               \
    "\n"                                                                \
    "The result is provided as a"                                       \
    " pychrysalide.arch.instructions.UndefInstruction.ExpectedBehavior" \
    " constant."                                                        \
)

    instr = G_UNDEF_INSTRUCTION(pygobject_get(self));
    behavior = g_undef_instruction_get_behavior(instr);

    result = cast_with_constants_group_from_type(get_python_undefined_instruction_type(),
                                                 "ExpectedBehavior", behavior);

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

PyTypeObject *get_python_undefined_instruction_type(void)
{
    static PyMethodDef py_undefined_instruction_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_undefined_instruction_getseters[] = {
        UNDEF_INSTRUCTION_BEHAVIOR_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_undefined_instruction_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.arch.instructions.UndefInstruction",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = UNDEF_INSTRUCTION_DOC,

        .tp_methods     = py_undefined_instruction_methods,
        .tp_getset      = py_undefined_instruction_getseters,

        .tp_init        = py_undef_instruction_init,
        .tp_new         = py_undef_instruction_new,

    };

    return &py_undefined_instruction_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.....UndefInstruction'. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_undefined_instruction_is_registered(void)
{
    PyTypeObject *type;                     /* Type 'UndefinedInstruction' */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_undefined_instruction_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.arch.instructions");

        dict = PyModule_GetDict(module);

        if (!ensure_python_arch_instruction_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_UNDEF_INSTRUCTION, type))
            return false;

        if (!define_undefined_instruction_constants(type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en instruction non définie.               *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_undefined_instruction(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_undefined_instruction_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to undefined instruction");
            break;

        case 1:
            *((GUndefInstruction **)dst) = G_UNDEF_INSTRUCTION(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
