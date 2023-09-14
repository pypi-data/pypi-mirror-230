
/* Chrysalide - Outil d'analyse de fichiers binaires
 * symbol.c - équivalent Python du fichier "format/symbol.h"
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


#include "symbol.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>
#include <pygobject.h>


#include <i18n.h>


#include <format/symbol-int.h>
#include <plugins/dt.h>


#include "constants.h"
#include "../access.h"
#include "../helpers.h"
#include "../analysis/routine.h"
#include "../analysis/db/items/comment.h"
#include "../analysis/storage/serialize.h"
#include "../arch/instruction.h"
#include "../arch/vmpa.h"
#include "../glibext/linegen.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Accompagne la création d'une instance dérivée en Python. */
static PyObject *py_binary_symbol_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise la classe des symboles d'exécutables. */
static void py_binary_symbol_init_gclass(GBinSymbolClass *, gpointer);

/* Fournit une étiquette pour viser un symbole. */
static char *py_binary_symbol_get_label_wrapper(const GBinSymbol *);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_binary_symbol_init(PyObject *, PyObject *, PyObject *);



/* --------------------- FONCTIONNALITES BASIQUES POUR SYMBOLES --------------------- */


/* Effectue une comparaison avec un objet Python 'BinSymbol'. */
static PyObject *py_binary_symbol_richcompare(PyObject *, PyObject *, int);

/* Ajoute une information complémentaire à un symbole. */
static PyObject *py_binary_symbol_set_flag(PyObject *, PyObject *);

/* Retire une information complémentaire à un symbole. */
static PyObject *py_binary_symbol_unset_flag(PyObject *, PyObject *);

/* Détermine si un symbole possède un fanion particulier. */
static PyObject *py_binary_symbol_has_flag(PyObject *, PyObject *);

/* Fournit l'emplacement où se situe un symbole. */
static PyObject *py_binary_symbol_get_range(PyObject *, void *);

/* Définit la couverture physique / en mémoire d'un symbole. */
static int py_binary_symbol_set_range(PyObject *, PyObject *, void *);

/* Fournit le type du symbole. */
static PyObject *py_binary_symbol_get_stype(PyObject *, void *);

/* Définit le type du symbole. */
static int py_binary_symbol_set_stype(PyObject *, PyObject *, void *);

/* Fournit la visibilité du symbole. */
static PyObject *py_binary_symbol_get_status(PyObject *, void *);

/* Définit la visibilité du symbole. */
static int py_binary_symbol_set_status(PyObject *, PyObject *, void *);

/* Fournit les particularités du symbole. */
static PyObject *py_binary_symbol_get_flags(PyObject *, void *);

/* Fournit le préfixe compatible avec une sortie "nm". */
static PyObject *py_binary_symbol_get_nm_prefix(PyObject *, void *);

/* Fournit un étiquette pour viser un symbole. */
static PyObject *py_binary_symbol_get_label(PyObject *, void *);

/* Définit un autre nom pour le symbole. */
static int py_binary_symbol_set_label(PyObject *, PyObject *, void *);



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

static PyObject *py_binary_symbol_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

    /* Validations diverses */

    base = get_python_binary_symbol_type();

    if (type == base)
        goto simple_way;

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_BIN_SYMBOL, type->tp_name,
                               (GClassInitFunc)py_binary_symbol_init_gclass, NULL, NULL);

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
*  Description : Initialise la classe des symboles d'exécutables.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_binary_symbol_init_gclass(GBinSymbolClass *class, gpointer unused)
{
    class->get_label = py_binary_symbol_get_label_wrapper;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = symbole à venir consulter.                          *
*                                                                             *
*  Description : Fournit une étiquette pour viser un symbole.                 *
*                                                                             *
*  Retour      : Chaîne de caractères renvoyant au symbole.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *py_binary_symbol_get_label_wrapper(const GBinSymbol *symbol)
{
    char *result;                           /* Etiquette à retourner       */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */

#define BINARY_SYMBOL_GET_LABEL_WRAPPER PYTHON_WRAPPER_DEF              \
(                                                                       \
    _get_label, "$self, /",                                             \
    METH_VARARGS,                                                       \
    "Abstract method used to provide the default label for a symbol.\n" \
    "\n"                                                                \
    "The returned value has to be a string."                            \
)

    result = NULL;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(symbol));

    if (has_python_method(pyobj, "_get_label"))
    {
        pyret = run_python_method(pyobj, "_get_label", NULL);
        if (pyret == NULL) goto exit;

        if (PyUnicode_Check(pyret))
            result = strdup(PyUnicode_DATA(pyret));

        Py_DECREF(pyret);

    }

 exit:

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

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

static int py_binary_symbol_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    mrange_t range;                         /* Version native d'un espace  */
    unsigned long stype;                    /* Type prévu pour le  symbole */
    int ret;                                /* Bilan de lecture des args.  */
    GBinSymbol *symbol;                     /* Version GLib du symbole     */

#define BINARY_SYMBOL_DOC                                                       \
    "BinSymbol represents all kinds of symbols, such as strings, routines or"   \
    " objects. If something can be linked to a physical or virtual location,"   \
    " it can be a symbol.\n"                                                    \
    "\n"                                                                        \
    "Instances can be created using the following constructor:\n"               \
    "\n"                                                                        \
    "    BinSymbol(range, stype)"                                               \
    "\n"                                                                        \
    "Where range is a memory space defined by pychrysalide.arch.mrange and"     \
    " stype a pychrysalide.format.BinSymbol.SymbolType value."                  \
    "\n"                                                                        \
    "The following methods have to be defined for new classes:\n"               \
    "* pychrysalide.format.BinSymbol._get_label()."

    /* Récupération des paramètres */

    ret = PyArg_ParseTuple(args, "O&k", convert_any_to_mrange, &range, &stype);
    if (!ret) return -1;

    if (stype >= STP_COUNT)
    {
        PyErr_SetString(PyExc_ValueError, _("Invalid type of symbol."));
        return -1;
    }

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    symbol = G_BIN_SYMBOL(pygobject_get(self));

    g_binary_symbol_set_range(symbol, &range);
    g_binary_symbol_set_stype(symbol, stype);

    return 0;

}



/* ---------------------------------------------------------------------------------- */
/*                       FONCTIONNALITES BASIQUES POUR SYMBOLES                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : a  = premier object Python à consulter.                      *
*                b  = second object Python à consulter.                       *
*                op = type de comparaison menée.                              *
*                                                                             *
*  Description : Effectue une comparaison avec un objet Python 'BinSymbol'.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_symbol_richcompare(PyObject *a, PyObject *b, int op)
{
    PyObject *result;                       /* Bilan à retourner           */
    int ret;                                /* Bilan de lecture des args.  */
    const GBinSymbol *sym_a;                /* Premier élément à traiter   */
    const GBinSymbol *sym_b;                /* Second élément à traiter    */
    int status;                             /* Résultat d'une comparaison  */

    ret = PyObject_IsInstance(b, (PyObject *)get_python_binary_symbol_type());
    if (!ret)
    {
        result = Py_NotImplemented;
        goto cmp_done;
    }

    sym_a = G_BIN_SYMBOL(pygobject_get(a));
    sym_b = G_BIN_SYMBOL(pygobject_get(b));

    status = g_binary_symbol_cmp(&sym_a, &sym_b);

    result = status_to_rich_cmp_state(status, op);

 cmp_done:

    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = serveur à manipuler.                                  *
*                args = arguments d'appel non utilisés ici.                   *
*                                                                             *
*  Description : Ajoute une information complémentaire à un symbole.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_symbol_set_flag(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    unsigned int flag;                      /* Propriété à traiter         */
    int ret;                                /* Bilan de lecture des args.  */
    GBinSymbol *symbol;                     /* Elément à manipuler         */
    bool status;                            /* Bilan de l'opération        */

#define BINARY_SYMBOL_SET_FLAG_METHOD PYTHON_METHOD_DEF             \
(                                                                   \
    set_flag, "$self, flag, /",                                     \
    METH_VARARGS, py_binary_symbol,                                 \
    "Add a property from a binary symbol.\n"                        \
    "\n"                                                            \
    "This property is one of the values listed in the"              \
    " of pychrysalide.format.BinSymbol.SymbolFlag enumeration.\n"   \
    "\n"                                                            \
    "If the flag was not set before the operation, True is"         \
    " returned, else the result is False."                          \
)

    ret = PyArg_ParseTuple(args, "I", &flag);
    if (!ret) return NULL;

    symbol = G_BIN_SYMBOL(pygobject_get(self));

    status = g_binary_symbol_set_flag(symbol, flag);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = serveur à manipuler.                                  *
*                args = arguments d'appel non utilisés ici.                   *
*                                                                             *
*  Description : Retire une information complémentaire à un symbole.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_symbol_unset_flag(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    unsigned int flag;                      /* Propriété à traiter         */
    int ret;                                /* Bilan de lecture des args.  */
    GBinSymbol *symbol;                     /* Elément à manipuler         */
    bool status;                            /* Bilan de l'opération        */

#define BINARY_SYMBOL_UNSET_FLAG_METHOD PYTHON_METHOD_DEF           \
(                                                                   \
    unset_flag, "$self, flag, /",                                   \
    METH_VARARGS, py_binary_symbol,                                 \
    "Remove a property from a binary symbol.\n"                     \
    "\n"                                                            \
    "This property is one of the values listed in the"              \
    " of pychrysalide.format.BinSymbol.SymbolFlag enumeration.\n"   \
    "\n"                                                            \
    "If the flag was not set before the operation, False is"        \
    " returned, else the result is True."                           \
)

    ret = PyArg_ParseTuple(args, "I", &flag);
    if (!ret) return NULL;

    symbol = G_BIN_SYMBOL(pygobject_get(self));

    status = g_binary_symbol_unset_flag(symbol, flag);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = serveur à manipuler.                                  *
*                args = arguments d'appel non utilisés ici.                   *
*                                                                             *
*  Description : Détermine si un symbole possède un fanion particulier.       *
*                                                                             *
*  Retour      : Bilan de la détection.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_symbol_has_flag(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    unsigned int flag;                      /* Propriété à traiter         */
    int ret;                                /* Bilan de lecture des args.  */
    GBinSymbol *symbol;                     /* Elément à manipuler         */
    bool status;                            /* Bilan de l'opération        */

#define BINARY_SYMBOL_HAS_FLAG_METHOD PYTHON_METHOD_DEF             \
(                                                                   \
    has_flag, "$self, flag, /",                                     \
    METH_VARARGS, py_binary_symbol,                                 \
    "Test if a binary symbol has a given property.\n"               \
    "\n"                                                            \
    "This property is one of the values listed in the"              \
    " of pychrysalide.format.BinSymbol.SymbolFlag enumeration.\n"   \
    "\n"                                                            \
    "The result is a boolean value."                                \
)

    ret = PyArg_ParseTuple(args, "I", &flag);
    if (!ret) return NULL;

    symbol = G_BIN_SYMBOL(pygobject_get(self));

    status = g_binary_symbol_has_flag(symbol, flag);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit l'emplacement où se situe un symbole.                *
*                                                                             *
*  Retour      : Zone mémoire couverte par le symbole.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_symbol_get_range(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GBinSymbol *symbol;                     /* Elément à consulter         */
    const mrange_t *range;                  /* Couverture courante         */

#define BINARY_SYMBOL_RANGE_ATTRIB PYTHON_GETSET_DEF_FULL   \
(                                                           \
    range, py_binary_symbol,                                \
    "Memory range covered by the symbol.\n"                 \
    "\n"                                                    \
    "This property is a pychrysalide.arch.mrange instance." \
)

    symbol = G_BIN_SYMBOL(pygobject_get(self));
    range = g_binary_symbol_get_range(symbol);

    result = build_from_internal_mrange(range);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Définit la couverture physique / en mémoire d'un symbole.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_binary_symbol_set_range(PyObject *self, PyObject *value, void *closure)
{
    int ret;                                /* Bilan d'analyse             */
    mrange_t *range;                        /* Espace mémoire à manipuler  */
    GBinSymbol *symbol;                     /* Elément à consulter         */

    ret = PyObject_IsInstance(value, (PyObject *)get_python_mrange_type());
    if (!ret) return -1;

    range = get_internal_mrange(value);

    symbol = G_BIN_SYMBOL(pygobject_get(self));

    g_binary_symbol_set_range(symbol, range);

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le type du symbole.                                  *
*                                                                             *
*  Retour      : Type de symbole représenté.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_symbol_get_stype(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GBinSymbol *symbol;                     /* Elément à consulter         */
    SymbolType type;                        /* Type de symbole représenté  */

#define BINARY_SYMBOL_STYPE_ATTRIB PYTHON_GETSET_DEF_FULL   \
(                                                           \
    stype, py_binary_symbol,                                \
    "Type of the current symbol, as a value of type"        \
    " pychrysalide.format.BinSymbol.SymbolType."            \
)

    symbol = G_BIN_SYMBOL(pygobject_get(self));
    type = g_binary_symbol_get_stype(symbol);

    result = cast_with_constants_group_from_type(get_python_binary_symbol_type(), "SymbolType", type);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Définit le type du symbole.                                  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_binary_symbol_set_stype(PyObject *self, PyObject *value, void *closure)
{
    GBinSymbol *symbol;                     /* Elément à consulter         */
    SymbolType type;                        /* Type de symbole à définir   */

    if (!PyLong_Check(value))
        return -1;

    symbol = G_BIN_SYMBOL(pygobject_get(self));

    type = PyLong_AsUnsignedLong(value);

    g_binary_symbol_set_stype(symbol, type);

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la visibilité du symbole.                            *
*                                                                             *
*  Retour      : Etat de la visibilité du symbole représenté.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_symbol_get_status(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GBinSymbol *symbol;                     /* Elément à consulter         */
    SymbolStatus status;                    /* Visibilité du symbole fourni*/

#define BINARY_SYMBOL_STATUS_ATTRIB PYTHON_GETSET_DEF_FULL      \
(                                                               \
    status, py_binary_symbol,                                   \
    "Status of the symbol's visibility, as a value of type"     \
    " pychrysalide.format.BinSymbol.SymbolStatus."              \
)

    symbol = G_BIN_SYMBOL(pygobject_get(self));
    status = g_binary_symbol_get_status(symbol);

    result = cast_with_constants_group_from_type(get_python_binary_symbol_type(), "SymbolStatus", status);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Définit la visibilité du symbole.                            *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_binary_symbol_set_status(PyObject *self, PyObject *value, void *closure)
{
    GBinSymbol *symbol;                     /* Elément à consulter         */
    SymbolStatus status;                    /* Visibilité à définir        */

    if (!PyLong_Check(value))
        return -1;

    symbol = G_BIN_SYMBOL(pygobject_get(self));

    status = PyLong_AsUnsignedLong(value);

    g_binary_symbol_set_status(symbol, status);

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit les particularités du symbole.                       *
*                                                                             *
*  Retour      : Somme de tous les fanions associés au symbole.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_symbol_get_flags(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GBinSymbol *symbol;                     /* Elément à consulter         */
    SymbolFlag flags;                       /* Indications complémentaires */

#define BINARY_SYMBOL_FLAGS_ATTRIB PYTHON_GET_DEF_FULL          \
(                                                               \
    flags, py_binary_symbol,                                    \
    "Provide all the flags set for a symbol. The return value"  \
    " is of type pychrysalide.format.BinSymbol.SymbolFlag."     \
)

    symbol = G_BIN_SYMBOL(pygobject_get(self));
    flags = g_binary_symbol_get_flags(symbol);

    result = cast_with_constants_group_from_type(get_python_binary_symbol_type(), "SymbolFlag", flags);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le préfixe compatible avec une sortie "nm".          *
*                                                                             *
*  Retour      : Caractère éventuel ou None.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_symbol_get_nm_prefix(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GBinSymbol *symbol;                     /* Elément à consulter         */
    char prefix[2];                         /* Eventuel préfixe "nm"       */
    bool status;                            /* Validité de ce préfixe      */

#define BINARY_SYMBOL_NM_PREFIX_ATTRIB PYTHON_GET_DEF_FULL              \
(                                                                       \
    nm_prefix, py_binary_symbol,                                        \
    "Single-byte string for an optional *nm* prefix, or None if any."   \
)

    symbol = G_BIN_SYMBOL(pygobject_get(self));
    status = g_binary_symbol_get_nm_prefix(symbol, &prefix[0]);

    if (status)
    {
        prefix[1] = '\0';
        result = PyUnicode_FromString(prefix);
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
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit un étiquette pour viser un symbole.                  *
*                                                                             *
*  Retour      : Chaîne de caractères renvoyant au symbole.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_symbol_get_label(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GBinSymbol *symbol;                     /* Elément à consulter         */
    char *label;                            /* Désignation courante        */

#define BINARY_SYMBOL_LABEL_ATTRIB PYTHON_GETSET_DEF_FULL                       \
(                                                                               \
    label, py_binary_symbol,                                                    \
    "Label of the symbol, provided by the internal component or by the user."   \
)

    symbol = G_BIN_SYMBOL(pygobject_get(self));
    label = g_binary_symbol_get_label(symbol);

    if (label != NULL)
    {
        result = PyUnicode_FromString(label);
        free(label);
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
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Définit un autre nom pour le symbole.                        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_binary_symbol_set_label(PyObject *self, PyObject *value, void *closure)
{
    const char *alt;                        /* Etiquette alternative       */
    GBinSymbol *symbol;                     /* Elément à consulter         */

    if (value == Py_None)
        alt = NULL;

    else
    {
        if (!PyUnicode_Check(value))
            return -1;

        alt = PyUnicode_DATA(value);

    }

    symbol = G_BIN_SYMBOL(pygobject_get(self));

    g_binary_symbol_set_alt_label(symbol, alt);

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

PyTypeObject *get_python_binary_symbol_type(void)
{
    static PyMethodDef binary_symbol_methods[] = {
        BINARY_SYMBOL_GET_LABEL_WRAPPER,
        BINARY_SYMBOL_SET_FLAG_METHOD,
        BINARY_SYMBOL_UNSET_FLAG_METHOD,
        BINARY_SYMBOL_HAS_FLAG_METHOD,
        { NULL }
    };

    static PyGetSetDef binary_symbol_getseters[] = {
        BINARY_SYMBOL_RANGE_ATTRIB,
        BINARY_SYMBOL_STYPE_ATTRIB,
        BINARY_SYMBOL_STATUS_ATTRIB,
        BINARY_SYMBOL_FLAGS_ATTRIB,
        BINARY_SYMBOL_NM_PREFIX_ATTRIB,
        BINARY_SYMBOL_LABEL_ATTRIB,
        { NULL }
    };

    static PyTypeObject binary_symbol_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.format.BinSymbol",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = BINARY_SYMBOL_DOC,

        .tp_richcompare = py_binary_symbol_richcompare,

        .tp_methods     = binary_symbol_methods,
        .tp_getset      = binary_symbol_getseters,

        .tp_init        = py_binary_symbol_init,
        .tp_new         = py_binary_symbol_new

    };

    return &binary_symbol_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.format.BinSymbol'.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_binary_symbol_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'BinSymbol'     */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_binary_symbol_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.format");

        dict = PyModule_GetDict(module);

        if (!ensure_python_line_generator_is_registered())
            return false;

        if (!ensure_python_serializable_object_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_BIN_SYMBOL, type))
            return false;

        if (!define_binary_symbol_constants(type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en symbole binaire.                       *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_binary_symbol(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_binary_symbol_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to binary symbol");
            break;

        case 1:
            *((GBinSymbol **)dst) = G_BIN_SYMBOL(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
