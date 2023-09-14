
/* Chrysalide - Outil d'analyse de fichiers binaires
 * instriter.c - équivalent Python du fichier "arch/instriter.c"
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


#include "instriter.h"


#include <pygobject.h>


#include <i18n.h>
#include <arch/processor.h>


#include "processor.h"
#include "vmpa.h"
#include "../access.h"
#include "../helpers.h"



/* Transcription d'un itérateur en Python */
typedef struct _PyInstrIterator
{
    PyObject_HEAD;                          /* A laisser en premier        */

    instr_iter_t *native;                   /* Version native de l'objet   */
    bool first_time;                        /* Premier élément retourné ?  */

} PyInstrIterator;


/* Libère de la mémoire un itérateur sur des instructions. */
static void py_instr_iterator_dealloc(PyInstrIterator *);

/* Fournit l'instruction qui en suit une autre. */
static PyObject *py_instr_iterator_next(PyInstrIterator *);

/* Limite le parcours des instructions à une zone donnée. */
static PyObject *py_instr_iterator_restrict(PyObject *, PyObject *);

/* Initialise un nouvel itérateur. */
static int py_instr_iterator_init(PyInstrIterator *, PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = itérateur à supprimer.                                *
*                                                                             *
*  Description : Libère de la mémoire un itérateur sur des instructions.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_instr_iterator_dealloc(PyInstrIterator *self)
{
    delete_instruction_iterator(self->native);

    Py_TYPE(self)->tp_free((PyObject *)self);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = itérateur à manipuler.                                *
*                                                                             *
*  Description : Fournit l'instruction qui en suit une autre.                 *
*                                                                             *
*  Retour      : Instruction suivante trouvée, ou NULL.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_instr_iterator_next(PyInstrIterator *self)
{
    PyObject *result;                       /* Résultat à retourner        */
    GArchInstruction *next;                 /* Instruction suivante        */

    if (self->first_time)
    {
        next = get_instruction_iterator_current(self->native);
        self->first_time = false;
    }

    else
        next = get_instruction_iterator_next(self->native);

    if (next != NULL)
    {
        result = pygobject_new(G_OBJECT(next));
        g_object_unref(G_OBJECT(next));
    }

    else
    {
        PyErr_SetNone(PyExc_StopIteration);
        result = NULL;
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = instance d'objet à initialiser.                       *
*                args = arguments passés pour l'appel.                        *
*                kwds = mots clefs éventuellement fournis en complément.      *
*                                                                             *
*  Description : Initialise un nouvel itérateur.                              *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_instr_iterator_init(PyInstrIterator *self, PyObject *args, PyObject *kwds)
{
    int result;                             /* Bilan à retourner           */
    GArchProcessor *proc;                   /* Version native du processeur*/
    PyObject *start;                        /* Position de départ          */
    int ret;                                /* Bilan de lecture des args.  */
    PyTypeObject *py_vmpa_type;             /* Type Python pour 'vmpa'     */
    PY_LONG_LONG index;                     /* Indice de première instruc. */
    int overflow;                           /* Détection d'une grosse val. */

    result = -1;

    ret = PyArg_ParseTuple(args, "O&O", convert_to_arch_processor, &proc, &start);
    if (!ret) goto exit;

    py_vmpa_type = get_python_vmpa_type();

    ret = PyObject_IsInstance(start, (PyObject *)py_vmpa_type);

    /* Si l'argument est une adresse... */
    if (ret == 1)
    {
        self->native = g_arch_processor_get_iter_from_address(proc, get_internal_vmpa(start));
        result = 0;
    }

    /* Si l'argument est un indice... */
    else
    {
        index = PyLong_AsLongLongAndOverflow(start, &overflow);

        if (index == -1 && (overflow == 1 || PyErr_Occurred()))
        {
            PyErr_Clear();
            PyErr_SetString(PyExc_TypeError, _("Unable to cast object as index."));
        }

        else
        {
            self->native = create_instruction_iterator(proc, index);
            result = 0;
        }

    }

    self->first_time = true;

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = itérateur d'instructions à manipuler.                 *
*                args = bornes de l'espace de parcours.                       *
*                                                                             *
*  Description : Limite le parcours des instructions à une zone donnée.       *
*                                                                             *
*  Retour      : Itérateur mis à jour.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_instr_iterator_restrict(PyObject *self, PyObject *args)
{
    mrange_t range;                         /* Espace mémoire fourni       */
    int ret;                                /* Bilan de lecture des args.  */
    PyInstrIterator *iter;                  /* Autre version d'objet       */

    ret = PyArg_ParseTuple(args, "O&", convert_any_to_mrange, &range);
    if (!ret) return NULL;

    iter = (PyInstrIterator *)self;

    restrict_instruction_iterator(iter->native, &range);

    Py_INCREF(self);

    return self;

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

PyTypeObject *get_python_instr_iterator_type(void)
{
    static PyMethodDef py_instr_iterator_methods[] = {
        {
            "restrict", py_instr_iterator_restrict,
            METH_VARARGS,
            "restrict($self, range, /)\n--\n\nLimit the instruction iterator to a memory range."
        },
        { NULL }
    };

    static PyTypeObject py_instr_iterator_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.arch.InstrIterator",
        .tp_basicsize   = sizeof(PyInstrIterator),

        .tp_dealloc     = (destructor)py_instr_iterator_dealloc,

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = "Iterator for Chrysalide instructions loaded in a given processor.",

        .tp_iter        = PyObject_SelfIter,
        .tp_iternext    = (iternextfunc)py_instr_iterator_next,

        .tp_methods     = py_instr_iterator_methods,
        .tp_init        = (initproc)py_instr_iterator_init,
        .tp_new         = PyType_GenericNew,

    };

    return &py_instr_iterator_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.arch.InstrIterator'.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_instr_iterator_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'InstrIterator' */
    PyObject *module;                       /* Module à recompléter        */

    type = get_python_instr_iterator_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        if (PyType_Ready(type) < 0)
            return false;

        module = get_access_to_python_module("pychrysalide.arch");

        if (!register_python_module_object(module, type))
            return false;

    }

    return true;

}
