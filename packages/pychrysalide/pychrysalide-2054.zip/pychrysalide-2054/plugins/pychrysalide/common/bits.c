
/* Chrysalide - Outil d'analyse de fichiers binaires
 * bits.c - équivalent Python du fichier "common/bits.c"
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


#include "bits.h"


#include "../access.h"
#include "../helpers.h"



/* Encapsulation d'un champ de bits */
typedef struct _py_bitfield_t
{
    PyObject_HEAD                           /* A laisser en premier        */

    bitfield_t *native;                     /* Champ de bits représenté    */

} py_bitfield_t;



/* Libère de la mémoire un objet Python de type 'bitfield_t'. */
static void py_bitfield_dealloc(py_bitfield_t *);

/* Initialise un objet Python de type 'bitfield_t'. */
static int py_bitfield_init(py_bitfield_t *, PyObject *, PyObject *);

/* Effectue une opération de type 'and' avec le type 'bitfield'. */
static PyObject *py_bitfield_nb_and(PyObject *, PyObject *);

/* Effectue une opération de type 'or' avec le type 'bitfield'. */
static PyObject *py_bitfield_nb_or(PyObject *, PyObject *);

/* Indique la taille de la séquence correspondant à un champ. */
static Py_ssize_t py_bitfield_sequence_length(PyObject *);

/* Fournit un élément de la séquence correspondant à un champ. */
static PyObject *py_bitfield_sequence_item(PyObject *, Py_ssize_t);

/* Effectue une comparaison avec un objet Python 'bitfield'. */
static PyObject *py_bitfield_richcompare(PyObject *, PyObject *, int);

/* Crée une copie d'un champ de bits classique. */
static PyObject *py_bitfield_dup(PyObject *, PyObject *);

/* Redimensionne un champ de bits. */
static PyObject *py_bitfield_resize(PyObject *, PyObject *);

/* Bascule à 0 un champ de bits dans son intégralité. */
static PyObject *py_bitfield_reset_all(PyObject *, PyObject *);

/* Bascule à 1 un champ de bits dans son intégralité. */
static PyObject *py_bitfield_set_all(PyObject *, PyObject *);

/* Bascule à 0 une partie d'un champ de bits. */
static PyObject *py_bitfield_reset(PyObject *, PyObject *);

/* Bascule à 1 une partie d'un champ de bits. */
static PyObject *py_bitfield_set(PyObject *, PyObject *);

/* Réalise une opération OU logique entre deux champs de bits. */
static PyObject *py_bitfield_or_at(PyObject *, PyObject *);

/* Détermine si un bit est à 1 dans un champ de bits. */
static PyObject *py_bitfield_test(PyObject *, PyObject *);

/* Détermine si un ensemble de bits est à 0 dans un champ. */
static PyObject *py_bitfield_test_none(PyObject *, PyObject *);

/* Détermine si un ensemble de bits est à 1 dans un champ. */
static PyObject *py_bitfield_test_all(PyObject *, PyObject *);

/* Teste l'état à 0 de bits selon un masque de bits. */
static PyObject *py_bitfield_test_zeros_with(PyObject *, PyObject *);

/* Teste l'état à 1 de bits selon un masque de bits. */
static PyObject *py_bitfield_test_ones_with(PyObject *, PyObject *);

/* Indique la taille d'un champ de bits donné. */
static PyObject *py_bitfield_get_size(PyObject *, void *);

/* Détermine le nombre de bits à 1 dans un champ. */
static PyObject *py_bitfield_get_popcount(PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = champ de bits à supprimer.                            *
*                                                                             *
*  Description : Libère de la mémoire un objet Python de type 'bitfield_t'.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_bitfield_dealloc(py_bitfield_t *self)
{
    delete_bit_field(self->native);

    Py_TYPE(self)->tp_free((PyObject *)self);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = instance d'objet à initialiser.                       *
*                args = arguments passés pour l'appel.                        *
*                kwds = mots clefs éventuellement fournis en complément.      *
*                                                                             *
*  Description : Initialise un objet Python de type 'bitfield_t'.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_bitfield_init(py_bitfield_t *self, PyObject *args, PyObject *kwds)
{
    int result;                             /* Bilan à retourner           */
    unsigned long length;                   /* Taille du champ à créer     */
    int state;                              /* Initialisation par défaut   */
    int ret;                                /* Bilan de lecture des args.  */

#define BITFIELD_DOC                                                \
    "The BitField object describes a group of bits and provides"    \
    " operations on it.\n"                                          \
    "\n"                                                            \
    "Instances can be created using the following constructor:\n"   \
    "\n"                                                            \
    "    BitField(length, state)"                                   \
    "\n"                                                            \
    "Where *length* is the size of the bitfield and *state*"        \
    " defines the initial state of each bits."                      \

    result = -1;

    ret = PyArg_ParseTuple(args, "kp", &length, &state);
    if (ret == 0) goto exit;

    self->native = create_bit_field(length, state);

    result = 0;

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : o1 = premier élément concerné par l'opération.               *
*                o2 = second élément concerné par l'opération.                *
*                                                                             *
*  Description : Effectue une opération de type 'and' avec le type 'bitfield'.*
*                                                                             *
*  Retour      : Résultat de l'opération.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_bitfield_nb_and(PyObject *o1, PyObject *o2)
{
    PyObject *result;                       /* Résultat à retourner        */
    int ret;                                /* Bilan de compatibilité      */
    py_bitfield_t *bf_1;                    /* Instance à manipuler #1     */
    py_bitfield_t *bf_2;                    /* Instance à manipuler #2     */
    py_bitfield_t *new;                     /* Nouvelle version en place   */

    ret = PyObject_IsInstance(o2, (PyObject *)get_python_bitfield_type());
    if (!ret)
    {
        result = NULL;
        goto pbna_done;
    }

    bf_1 = (py_bitfield_t *)o1;
    bf_2 = (py_bitfield_t *)o2;

    result = build_from_internal_bitfield(bf_1->native);

    new = (py_bitfield_t *)result;

    and_bit_field(new->native, bf_2->native);

 pbna_done:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : o1 = premier élément concerné par l'opération.               *
*                o2 = second élément concerné par l'opération.                *
*                                                                             *
*  Description : Effectue une opération de type 'or' avec le type 'bitfield'. *
*                                                                             *
*  Retour      : Résultat de l'opération.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_bitfield_nb_or(PyObject *o1, PyObject *o2)
{
    PyObject *result;                       /* Résultat à retourner        */
    int ret;                                /* Bilan de compatibilité      */
    py_bitfield_t *bf_1;                    /* Instance à manipuler #1     */
    py_bitfield_t *bf_2;                    /* Instance à manipuler #2     */
    py_bitfield_t *new;                     /* Nouvelle version en place   */

    ret = PyObject_IsInstance(o2, (PyObject *)get_python_bitfield_type());
    if (!ret)
    {
        result = NULL;
        goto pbna_done;
    }

    bf_1 = (py_bitfield_t *)o1;
    bf_2 = (py_bitfield_t *)o2;

    result = build_from_internal_bitfield(bf_1->native);

    new = (py_bitfield_t *)result;

    or_bit_field(new->native, bf_2->native);

 pbna_done:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = champ de bits à consulter.                            *
*                                                                             *
*  Description : Indique la taille de la séquence correspondant à un champ.   *
*                                                                             *
*  Retour      : Taille du champ de bits.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static Py_ssize_t py_bitfield_sequence_length(PyObject *self)
{
    Py_ssize_t result;                      /* Taille à retourner          */
    py_bitfield_t *bf;                      /* Instance à manipuler        */

    bf = (py_bitfield_t *)self;

    result = get_bit_field_size(bf->native);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = champ de bits à consulter.                            *
*                i    = indice de l'élément à retourner.                      *
*                                                                             *
*  Description : Fournit un élément de la séquence correspondant à un champ.  *
*                                                                             *
*  Retour      : Valeur booléenne.                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_bitfield_sequence_item(PyObject *self, Py_ssize_t i)
{
    PyObject *result;                       /* Elément à retourner         */
    py_bitfield_t *bf;                      /* Instance à manipuler        */
    bool state;                             /* Etat du bit ciblé           */

    bf = (py_bitfield_t *)self;

    if (i < 0 || i >= (Py_ssize_t)get_bit_field_size(bf->native))
        result = NULL;

    else
    {
        state = test_in_bit_field(bf->native, i);

        result = state ? Py_True : Py_False;
        Py_INCREF(result);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a  = premier object Python à consulter.                      *
*                b  = second object Python à consulter.                       *
*                op = type de comparaison menée.                              *
*                                                                             *
*  Description : Effectue une comparaison avec un objet Python 'bitfield'.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_bitfield_richcompare(PyObject *a, PyObject *b, int op)
{
    PyObject *result;                       /* Bilan à retourner           */
    int ret;                                /* Bilan de lecture des args.  */
    py_bitfield_t *bf_a;                    /* Instance à manipuler #1     */
    py_bitfield_t *bf_b;                    /* Instance à manipuler #2     */
    int status;                             /* Résultat d'une comparaison  */

    ret = PyObject_IsInstance(b, (PyObject *)get_python_bitfield_type());
    if (!ret)
    {
        result = Py_NotImplemented;
        goto cmp_done;
    }

    bf_a = (py_bitfield_t *)a;
    bf_b = (py_bitfield_t *)b;

    status = compare_bit_fields(bf_a->native, bf_b->native);

    result = status_to_rich_cmp_state(status, op);

 cmp_done:

    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = champ de bits à dupliquer.                            *
*                args = non utilisé ici.                                      *
*                                                                             *
*  Description : Crée une copie d'un champ de bits classique.                 *
*                                                                             *
*  Retour      : Champ de bits mis en place.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_bitfield_dup(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    py_bitfield_t *bf;                      /* Instance à manipuler        */

#define BITFIELD_DUP_METHOD PYTHON_METHOD_DEF                           \
(                                                                       \
    dup, "$self, /",                                                    \
    METH_NOARGS, py_bitfield,                                           \
    "Duplicate a bitfield.\n"                                           \
    "\n"                                                                \
    "The result is a new pychrysalide.common.BitField with the same"    \
    " content."                                                         \
)

    bf = (py_bitfield_t *)self;

    result = build_from_internal_bitfield(bf->native);;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = champ de bits à dupliquer.                            *
*                args = non utilisé ici.                                      *
*                                                                             *
*  Description : Redimensionne un champ de bits.                              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_bitfield_resize(PyObject *self, PyObject *args)
{
    unsigned long length;                   /* Nouvelle taille à respecter */
    int ret;                                /* Bilan de lecture des args.  */
    py_bitfield_t *bf;                      /* Instance à manipuler        */

#define BITFIELD_RESIZE_METHOD PYTHON_METHOD_DEF                        \
(                                                                       \
    resize, "$self, length, /",                                         \
    METH_VARARGS, py_bitfield,                                          \
    "Resize a bitfield and fix its new size to *length*.\n"             \
    "\n"                                                                \
    "The new bits get initialized to the same state used at the"        \
    " bitfield creation."                                               \
)

    ret = PyArg_ParseTuple(args, "k", &length);
    if (!ret) return NULL;

    bf = (py_bitfield_t *)self;

    resize_bit_field(&bf->native, length);

    Py_RETURN_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = champ de bits à modifier.                             *
*                args = non utilisé ici.                                      *
*                                                                             *
*  Description : Bascule à 0 un champ de bits dans son intégralité.           *
*                                                                             *
*  Retour      : Rien (None).                                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_bitfield_reset_all(PyObject *self, PyObject *args)
{
    py_bitfield_t *bf;                      /* Instance à manipuler        */

#define BITFIELD_RESET_ALL_METHOD PYTHON_METHOD_DEF \
(                                                   \
    reset_all, "$self, /",                          \
    METH_NOARGS, py_bitfield,                       \
    "Switch to 0 all bits in a bitfield."           \
)

    bf = (py_bitfield_t *)self;

    reset_all_in_bit_field(bf->native);

    Py_RETURN_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = champ de bits à modifier.                             *
*                args = non utilisé ici.                                      *
*                                                                             *
*  Description : Bascule à 1 un champ de bits dans son intégralité.           *
*                                                                             *
*  Retour      : Rien (None).                                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_bitfield_set_all(PyObject *self, PyObject *args)
{
    py_bitfield_t *bf;                      /* Instance à manipuler        */

#define BITFIELD_SET_ALL_METHOD PYTHON_METHOD_DEF   \
(                                                   \
    set_all, "$self, /",                            \
    METH_NOARGS, py_bitfield,                       \
    "Switch to 1 all bits in a bitfield."           \
)

    bf = (py_bitfield_t *)self;

    set_all_in_bit_field(bf->native);

    Py_RETURN_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = champ de bits à consulter.                            *
*                args = arguments fournis pour la conduite de l'opération.    *
*                                                                             *
*  Description : Bascule à 0 une partie d'un champ de bits.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_bitfield_reset(PyObject *self, PyObject *args)
{
    unsigned long first;                    /* Indice du premier bit testé */
    unsigned long count;                    /* Nombre de bits à analyser   */
    int ret;                                /* Bilan de lecture des args.  */
    py_bitfield_t *bf;                      /* Instance à manipuler        */

#define BITFIELD_RESET_METHOD PYTHON_METHOD_DEF             \
(                                                           \
    reset, "$self, first, count, /",                        \
    METH_VARARGS, py_bitfield,                              \
    "Switch to 0 a part of bits in a bitfield.\n"           \
    "\n"                                                    \
    "The area to process starts at bit *first* and has a"   \
    " size of *count* bits."                                \
)

    ret = PyArg_ParseTuple(args, "kk", &first, &count);
    if (!ret) return NULL;

    bf = (py_bitfield_t *)self;

    reset_in_bit_field(bf->native, first, count);

    Py_RETURN_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = champ de bits à consulter.                            *
*                args = arguments fournis pour la conduite de l'opération.    *
*                                                                             *
*  Description : Bascule à 1 une partie d'un champ de bits.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_bitfield_set(PyObject *self, PyObject *args)
{
    unsigned long first;                    /* Indice du premier bit testé */
    unsigned long count;                    /* Nombre de bits à analyser   */
    int ret;                                /* Bilan de lecture des args.  */
    py_bitfield_t *bf;                      /* Instance à manipuler        */

#define BITFIELD_SET_METHOD PYTHON_METHOD_DEF               \
(                                                           \
    set, "$self, first, count, /",                          \
    METH_VARARGS, py_bitfield,                              \
    "Switch to 1 a part of bits in a bitfield.\n"           \
    "\n"                                                    \
    "The area to process starts at bit *first* and has a"   \
    " size of *count* bits."                                \
)

    ret = PyArg_ParseTuple(args, "kk", &first, &count);
    if (!ret) return NULL;

    bf = (py_bitfield_t *)self;

    set_in_bit_field(bf->native, first, count);

    Py_RETURN_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = champ de bits à consulter.                            *
*                args = arguments fournis pour la conduite de l'opération.    *
*                                                                             *
*  Description : Réalise une opération OU logique entre deux champs de bits.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_bitfield_or_at(PyObject *self, PyObject *args)
{
    bitfield_t *src;                        /* Seconde champ de bits       */
    unsigned long first;                    /* Indice du premier bit testé */
    int ret;                                /* Bilan de lecture des args.  */
    py_bitfield_t *bf;                      /* Instance à manipuler        */

#define BITFIELD_OR_AT_METHOD PYTHON_METHOD_DEF             \
(                                                           \
    or_at, "$self, src, first, /",                          \
    METH_VARARGS, py_bitfield,                              \
    "Perform an OR operation with another bitfield.\n"      \
    "\n"                                                    \
    "The *src* argument is expected to be another"          \
    " pychrysalide.common.BitField instance. The area to"   \
    " process starts at bit *first* from *src*."            \
)

    ret = PyArg_ParseTuple(args, "O&k", convert_to_bitfield, &src, &first);
    if (!ret) return NULL;

    bf = (py_bitfield_t *)self;

    or_bit_field_at(bf->native, src, first);

    Py_RETURN_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = champ de bits à consulter.                            *
*                args = arguments fournis pour la conduite de l'opération.    *
*                                                                             *
*  Description : Détermine si un bit est à 1 dans un champ de bits.           *
*                                                                             *
*  Retour      : true si le bit correspondant est à l'état haut.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_bitfield_test(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à faire remonter      */
    unsigned long n;                        /* Indice du bit à traiter     */
    int ret;                                /* Bilan de lecture des args.  */
    py_bitfield_t *bf;                      /* Instance à manipuler        */
    bool status;                            /* Bilan d'analyse             */

#define BITFIELD_TEST_METHOD PYTHON_METHOD_DEF              \
(                                                           \
    test, "$self, n, /",                                    \
    METH_VARARGS, py_bitfield,                              \
    "Test if a given bit is set in a bitfield.\n"           \
    "\n"                                                    \
    "The result is a boolean value: True if the tested"     \
    " *n* bit is set, False otherwise."                     \
)

    ret = PyArg_ParseTuple(args, "k", &n);
    if (!ret) return NULL;

    bf = (py_bitfield_t *)self;

    status = test_in_bit_field(bf->native, n);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = champ de bits à consulter.                            *
*                args = arguments fournis pour la conduite de l'opération.    *
*                                                                             *
*  Description : Détermine si un ensemble de bits est à 0 dans un champ.      *
*                                                                             *
*  Retour      : True si les bits correspondants sont à l'état bas.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_bitfield_test_none(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à faire remonter      */
    unsigned long first;                    /* Indice du premier bit testé */
    unsigned long count;                    /* Nombre de bits à analyser   */
    int ret;                                /* Bilan de lecture des args.  */
    py_bitfield_t *bf;                      /* Instance à manipuler        */
    bool status;                            /* Bilan d'analyse             */

#define BITFIELD_TEST_NONE_METHOD PYTHON_METHOD_DEF         \
(                                                           \
    test_none, "$self, first, count, /",                    \
    METH_VARARGS, py_bitfield,                              \
    "Test a range of bits against 0.\n"                     \
    "\n"                                                    \
    "The area to process starts at bit *first* and has a"   \
    " size of *count* bits."                                \
    "\n"                                                    \
    "The result is a boolean value: True if all tested"     \
    " bits are unset, False otherwise."                     \
)

    ret = PyArg_ParseTuple(args, "kk", &first, &count);
    if (!ret) return NULL;

    bf = (py_bitfield_t *)self;

    status = test_none_in_bit_field(bf->native, first, count);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = champ de bits à consulter.                            *
*                args = arguments fournis pour la conduite de l'opération.    *
*                                                                             *
*  Description : Détermine si un ensemble de bits est à 1 dans un champ.      *
*                                                                             *
*  Retour      : True si les bits correspondants sont à l'état haut.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_bitfield_test_all(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à faire remonter      */
    unsigned long first;                    /* Indice du premier bit testé */
    unsigned long count;                    /* Nombre de bits à analyser   */
    int ret;                                /* Bilan de lecture des args.  */
    py_bitfield_t *bf;                      /* Instance à manipuler        */
    bool status;                            /* Bilan d'analyse             */

#define BITFIELD_TEST_ALL_METHOD PYTHON_METHOD_DEF          \
(                                                           \
    test_all, "$self, first, count, /",                     \
    METH_VARARGS, py_bitfield,                              \
    "Test a range of bits against 1.\n"                     \
    "\n"                                                    \
    "The area to process starts at bit *first* and has a"   \
    " size of *count* bits."                                \
    "\n"                                                    \
    "The result is a boolean value: True if all tested"     \
    " bits are set, False otherwise."                       \
)

    ret = PyArg_ParseTuple(args, "kk", &first, &count);
    if (!ret) return NULL;

    bf = (py_bitfield_t *)self;

    status = test_all_in_bit_field(bf->native, first, count);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = champ de bits à consulter.                            *
*                args = arguments fournis pour la conduite de l'opération.    *
*                                                                             *
*  Description : Teste l'état à 0 de bits selon un masque de bits.            *
*                                                                             *
*  Retour      : true si les bits visés sont à l'état bas.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_bitfield_test_zeros_with(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à faire remonter      */
    unsigned long first;                    /* Indice du premier bit testé */
    bitfield_t *mask;                       /* Champ de bits natif         */
    int ret;                                /* Bilan de lecture des args.  */
    py_bitfield_t *bf;                      /* Instance à manipuler        */
    bool status;                            /* Bilan d'analyse             */

#define BITFIELD_TEST_ZEROS_WITH_METHOD PYTHON_METHOD_DEF   \
(                                                           \
    test_zeros_with, "$self, first, mask, /",               \
    METH_VARARGS, py_bitfield,                              \
    "Test a range of bits against another bit field.\n"     \
    "\n"                                                    \
    "The area to process starts at bit *first* and the"     \
    " test relies on bits set within the *mask* object.\n"  \
    "\n"                                                    \
    "The result is a boolean value: True if all tested"     \
    " bits are unset, False otherwise."                     \
)

    ret = PyArg_ParseTuple(args, "kO&", &first, convert_to_bitfield, &mask);
    if (!ret) return NULL;

    bf = (py_bitfield_t *)self;

    status = test_zeros_within_bit_field(bf->native, first, mask);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = champ de bits à consulter.                            *
*                args = arguments fournis pour la conduite de l'opération.    *
*                                                                             *
*  Description : Teste l'état à 1 de bits selon un masque de bits.            *
*                                                                             *
*  Retour      : true si les bits visés sont à l'état haut.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_bitfield_test_ones_with(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à faire remonter      */
    unsigned long first;                    /* Indice du premier bit testé */
    bitfield_t *mask;                       /* Champ de bits natif         */
    int ret;                                /* Bilan de lecture des args.  */
    py_bitfield_t *bf;                      /* Instance à manipuler        */
    bool status;                            /* Bilan d'analyse             */

#define BITFIELD_TEST_ONES_WITH_METHOD PYTHON_METHOD_DEF    \
(                                                           \
    test_ones_with, "$self, first, mask, /",                \
    METH_VARARGS, py_bitfield,                              \
    "Test a range of bits against another bit field.\n"     \
    "\n"                                                    \
    "The area to process starts at bit *first* and the"     \
    " test relies on bits set within the *mask* object.\n"  \
    "\n"                                                    \
    "The result is a boolean value: True if all tested"     \
    " bits are set, False otherwise."                       \
)

    ret = PyArg_ParseTuple(args, "kO&", &first, convert_to_bitfield, &mask);
    if (!ret) return NULL;

    bf = (py_bitfield_t *)self;

    status = test_ones_within_bit_field(bf->native, first, mask);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = classe représentant une instruction.               *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Indique la taille d'un champ de bits donné.                  *
*                                                                             *
*  Retour      : Taille du champ de bits.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_bitfield_get_size(PyObject *self, void *closure)
{
    PyObject *result;                       /* Conversion à retourner      */
    py_bitfield_t *bf;                      /* Instance à manipuler        */
    size_t size;                            /* Taille du champs de bits    */

#define BITFIELD_SIZE_ATTRIB PYTHON_GET_DEF_FULL    \
(                                                   \
    size, py_bitfield,                              \
    "Provide the size of the bitfield."             \
)

    bf = (py_bitfield_t *)self;

    size = get_bit_field_size(bf->native);

    result = PyLong_FromSize_t(size);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = classe représentant une instruction.               *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Détermine le nombre de bits à 1 dans un champ.               *
*                                                                             *
*  Retour      : Valeur positive ou nulle.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_bitfield_get_popcount(PyObject *self, void *closure)
{
    PyObject *result;                       /* Conversion à retourner      */
    py_bitfield_t *bf;                      /* Instance à manipuler        */
    size_t count;                           /* Quantité de bits à 1        */

#define BITFIELD_POPCOUNT_ATTRIB PYTHON_GET_DEF_FULL    \
(                                                       \
    popcount, py_bitfield,                              \
    "Get the number of bits set to 1 in the bitfield."  \
)

    bf = (py_bitfield_t *)self;

    count = popcount_for_bit_field(bf->native);

    result = PyLong_FromSize_t(count);

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

PyTypeObject *get_python_bitfield_type(void)
{
    static PyNumberMethods py_bitfield_nb_proto = {
        .nb_and = py_bitfield_nb_and,
        .nb_or  = py_bitfield_nb_or
    };

    static PySequenceMethods py_bitfield_sequence_proto = {
        .sq_length = py_bitfield_sequence_length,
        .sq_item   = py_bitfield_sequence_item
    };

    static PyMethodDef py_bitfield_methods[] = {
        BITFIELD_DUP_METHOD,
        BITFIELD_RESIZE_METHOD,
        BITFIELD_RESET_ALL_METHOD,
        BITFIELD_SET_ALL_METHOD,
        BITFIELD_RESET_METHOD,
        BITFIELD_SET_METHOD,
        BITFIELD_OR_AT_METHOD,
        BITFIELD_TEST_METHOD,
        BITFIELD_TEST_NONE_METHOD,
        BITFIELD_TEST_ALL_METHOD,
        BITFIELD_TEST_ZEROS_WITH_METHOD,
        BITFIELD_TEST_ONES_WITH_METHOD,
        { NULL }
    };

    static PyGetSetDef py_bitfield_getseters[] = {
        BITFIELD_SIZE_ATTRIB,
        BITFIELD_POPCOUNT_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_bitfield_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.common.BitField",
        .tp_basicsize   = sizeof(py_bitfield_t),

        .tp_dealloc     = (destructor)py_bitfield_dealloc,

        .tp_as_number   = &py_bitfield_nb_proto,
        .tp_as_sequence = &py_bitfield_sequence_proto,

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = BITFIELD_DOC,

        .tp_richcompare = py_bitfield_richcompare,

        .tp_methods     = py_bitfield_methods,
        .tp_getset      = py_bitfield_getseters,

        .tp_init        = (initproc)py_bitfield_init,
        .tp_new         = PyType_GenericNew,

    };

    return &py_bitfield_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.common.BitField'.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_bitfield_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python pour 'bitfield' */
    PyObject *module;                       /* Module à recompléter        */

    type = get_python_bitfield_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        if (PyType_Ready(type) != 0)
            return false;

        module = get_access_to_python_module("pychrysalide.common");

        if (!register_python_module_object(module, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en champ de bits.                         *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_bitfield(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_bitfield_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to bit field");
            break;

        case 1:
            *((bitfield_t **)dst) = ((py_bitfield_t *)arg)->native;
            break;

        default:
            assert(false);
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : field = structure interne à copier en objet Python.          *
*                                                                             *
*  Description : Convertit une structure de type 'bitfield_t' en objet Python.*
*                                                                             *
*  Retour      : Object Python résultant de la conversion opérée.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *build_from_internal_bitfield(const bitfield_t *field)
{
    PyObject *result;                       /* Instance à retourner        */
    PyTypeObject *type;                     /* Type à instancier           */
    PyObject *args;                         /* Liste des arguments d'appel */
    py_bitfield_t *bf_obj;                  /* Objet précis instancié      */

    type = get_python_bitfield_type();

    /**
     * Le format "p" n'existe pas pour Py_BuildValue().
     */
    args = Py_BuildValue("kk", 0, 0);

    result = PyObject_CallObject((PyObject *)type, args);

    Py_DECREF(args);

    bf_obj = (py_bitfield_t *)result;

    delete_bit_field(bf_obj->native);

    bf_obj->native = dup_bit_field(field);

    return result;

}
