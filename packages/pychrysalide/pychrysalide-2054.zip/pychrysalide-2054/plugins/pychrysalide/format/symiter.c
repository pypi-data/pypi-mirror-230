
/* Chrysalide - Outil d'analyse de fichiers binaires
 * symiter.c - équivalent Python du fichier "format/symiter.c"
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


#include "symiter.h"


#include <pygobject.h>


#include <format/symiter.h>


#include "format.h"
#include "../access.h"
#include "../helpers.h"



#define SYM_ITERATOR_DOC                                                \
    "Iterator for Chrysalide symbols registered in a given format.\n"   \
    "\n"                                                                \
    "This iterator is built when accessing to the"                      \
    " pychrysalide.format.BinFormat.symbols field."


/* Transcription d'un itérateur en Python */
typedef struct _PySymIterator
{
    PyObject_HEAD;                          /* A laisser en premier        */

    sym_iter_t *native;                     /* Version native de l'objet   */
    bool first_time;                        /* Premier élément retourné ?  */

} PySymIterator;


/* Libère de la mémoire un itérateur sur des symboles. */
static void py_sym_iterator_dealloc(PySymIterator *);

/* Fournit le symbole qui en suit un autr. */
static PyObject *py_sym_iterator_next(PySymIterator *);

/* Initialise un nouvel itérateur. */
static int py_sym_iterator_init(PySymIterator *, PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = itérateur à supprimer.                                *
*                                                                             *
*  Description : Libère de la mémoire un itérateur sur des symboles.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_sym_iterator_dealloc(PySymIterator *self)
{
    delete_symbol_iterator(self->native);

    Py_TYPE(self)->tp_free((PyObject *)self);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = itérateur à manipuler.                                *
*                                                                             *
*  Description : Fournit le symbole qui en suit un autre.                     *
*                                                                             *
*  Retour      : Symbole suivant trouvé, ou NULL.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_sym_iterator_next(PySymIterator *self)
{
    PyObject *result;                       /* Résultat à retourner        */
    GBinSymbol *next;                       /* Symbole suivant             */

    if (self->first_time)
    {
        next = get_symbol_iterator_current(self->native);
        self->first_time = false;
    }

    else
        next = get_symbol_iterator_next(self->native);

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

static int py_sym_iterator_init(PySymIterator *self, PyObject *args, PyObject *kwds)
{
    int result;                             /* Bilan à retourner           */
    PyObject *fmt_obj;                      /* Format version Python       */
    unsigned long index;                    /* Indice de premier symbole   */
    int ret;                                /* Bilan de lecture des args.  */
    GBinFormat *format;                     /* Version native du format    */

    result = -1;

    ret = PyArg_ParseTuple(args, "Ok", &fmt_obj, &index);
    if (ret == 0) goto psii_exit;

    ret = PyObject_IsInstance(fmt_obj, (PyObject *)get_python_binary_format_type());
    if (!ret) goto psii_exit;

    format = G_BIN_FORMAT(pygobject_get(fmt_obj));

    self->native = create_symbol_iterator(format, index);
    self->first_time = true;

    result = 0;

 psii_exit:

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

PyTypeObject *get_python_sym_iterator_type(void)
{
    static PyTypeObject py_sym_iterator_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.format.SymIterator",
        .tp_basicsize   = sizeof(PySymIterator),

        .tp_dealloc     = (destructor)py_sym_iterator_dealloc,

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = SYM_ITERATOR_DOC,

        .tp_iter        = PyObject_SelfIter,
        .tp_iternext    = (iternextfunc)py_sym_iterator_next,

        .tp_init        = (initproc)py_sym_iterator_init,
        .tp_new         = PyType_GenericNew,

    };

    return &py_sym_iterator_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.format.SymIterator'.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_sym_iterator_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'SymIterator'   */
    PyObject *module;                       /* Module à recompléter        */

    type = get_python_sym_iterator_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        if (PyType_Ready(type) < 0)
            return false;

        module = get_access_to_python_module("pychrysalide.format");

        if (!register_python_module_object(module, type))
            return false;

    }

    return true;

}
