
/* Chrysalide - Outil d'analyse de fichiers binaires
 * format.c - équivalent Python du fichier "format/format.c"
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


#include "format.h"


#include <pygobject.h>


#include <i18n.h>
#include <format/format-int.h>
#include <plugins/dt.h>


#include "constants.h"
#include "executable.h"
#include "known.h"
#include "symbol.h"
#include "symiter.h"
#include "../access.h"
#include "../helpers.h"
#include "../analysis/constants.h"
#include "../analysis/content.h"
#include "../arch/vmpa.h"
#include "../arch/constants.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Accompagne la création d'une instance dérivée en Python. */
static PyObject *py_binary_format_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise la classe des descriptions de fichier binaire. */
static void py_binary_format_init_gclass(GBinFormatClass *, gpointer);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_binary_format_init(PyObject *, PyObject *, PyObject *);

/* Indique le boutisme employé par le format binaire analysé. */
static SourceEndian py_binary_format_get_endianness_wrapper(const GBinFormat *);



/* ---------------------------- FORMAT BINAIRE GENERIQUE ---------------------------- */


/* Ajoute une information complémentaire à un format. */
static PyObject *py_binary_format_set_flag(PyObject *, PyObject *);

/* Retire une information complémentaire à un format. */
static PyObject *py_binary_format_unset_flag(PyObject *, PyObject *);

/* Détermine si un format possède un fanion particulier. */
static PyObject *py_binary_format_has_flag(PyObject *, PyObject *);

/* Enregistre une adresse comme début d'une zone de code. */
static PyObject *py_binary_format_register_code_point(PyObject *, PyObject *);

/* Ajoute un symbole à la collection du format binaire. */
static PyObject *py_binary_format_add_symbol(PyObject *, PyObject *);

/* Retire un symbole de la collection du format binaire. */
static PyObject *py_binary_format_remove_symbol(PyObject *, PyObject *);

/* Recherche le symbole correspondant à une étiquette. */
static PyObject *py_binary_format_find_symbol_by_label(PyObject *, PyObject *);

/* Recherche le symbole suivant celui lié à une adresse. */
static PyObject *py_binary_format_find_symbol_at(PyObject *, PyObject *);

/* Recherche le symbole suivant celui lié à une adresse. */
static PyObject *py_binary_format_find_next_symbol_at(PyObject *, PyObject *);

/* Recherche le symbole correspondant à une adresse. */
static PyObject *py_binary_format_resolve_symbol(PyObject *, PyObject *);

/* Fournit les particularités du format. */
static PyObject *py_binary_format_get_flags(PyObject *, void *);

/* Indique le boutisme employé par le format binaire analysé. */
static PyObject *py_binary_format_get_endianness(PyObject *, void *);

/* Fournit la liste de tous les symboles détectés. */
static PyObject *py_binary_format_get_symbols(PyObject *, void *);



/* ------------------ CONSERVATION DES SOUCIS DURANT LE CHARGEMENT ------------------ */


/* Etend la liste des soucis détectés avec de nouvelles infos. */
static PyObject *py_binary_format_add_error(PyObject *, PyObject *);

/* Fournit les éléments concernant tous les soucis détectés. */
static PyObject *py_binary_format_get_errors(PyObject *, void *);



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

static PyObject *py_binary_format_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

    /* Validations diverses */

    base = get_python_known_format_type();

    if (type == base)
    {
        result = NULL;
        PyErr_Format(PyExc_RuntimeError, _("%s is an abstract class"), type->tp_name);
        goto exit;
    }

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_BIN_FORMAT, type->tp_name,
                               (GClassInitFunc)py_binary_format_init_gclass, NULL, NULL);

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
*  Description : Initialise la classe générique des processeurs.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_binary_format_init_gclass(GBinFormatClass *class, gpointer unused)
{
    class->get_endian = py_binary_format_get_endianness_wrapper;

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

static int py_binary_format_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    int ret;                                /* Bilan de lecture des args.  */

#define BINARY_FORMAT_DOC                                               \
    "The BinFormat class is the major poart of binary format support."  \
    " It is the core class used by loading most of the binary files.\n" \
    "\n"                                                                \
    "One item has to be defined as class attribute in the final"        \
    " class:\n"                                                         \
    "* *_endianness*: a pychrysalide.analysis.BinContent.SourceEndian"  \
    " value indicating the endianness of the format.\n"                 \
    "\n"                                                                \
    "Calls to the *__init__* constructor of this abstract object expect"\
    " no particular argument."

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description du format connu à consulter.            *
*                                                                             *
*  Description : Indique le boutisme employé par le format binaire analysé.   *
*                                                                             *
*  Retour      : Boutisme associé au format.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static SourceEndian py_binary_format_get_endianness_wrapper(const GBinFormat *format)
{
    SourceEndian result;                    /* Boutisme à retourner        */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Valeur retournée            */
    int ret;                                /* Bilan d'une conversion      */

    result = SRE_LITTLE;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(format));

    if (PyObject_HasAttrString(pyobj, "_endianness"))
    {
        pyret = PyObject_GetAttrString(pyobj, "_endianness");

        if (pyret != NULL)
        {
            ret = convert_to_source_endian(pyret, &result);

            if (ret != 1)
                result = SRE_LITTLE;

            Py_DECREF(pyret);

        }

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/* ---------------------------------------------------------------------------------- */
/*                              FORMAT BINAIRE GENERIQUE                              */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self = serveur à manipuler.                                  *
*                args = arguments d'appel non utilisés ici.                   *
*                                                                             *
*  Description : Ajoute une information complémentaire à un format.           *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_format_set_flag(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    unsigned int flag;                      /* Propriété à traiter         */
    int ret;                                /* Bilan de lecture des args.  */
    GBinFormat *format;                     /* Elément à manipuler         */
    bool status;                            /* Bilan de l'opération        */

#define BINARY_FORMAT_SET_FLAG_METHOD PYTHON_METHOD_DEF             \
(                                                                   \
    set_flag, "$self, flag, /",                                     \
    METH_VARARGS, py_binary_format,                                 \
    "Add a property from a binary format.\n"                        \
    "\n"                                                            \
    "This property is one of the values listed in the"              \
    " of pychrysalide.format.BinFormat.FormatFlag enumeration.\n"   \
    "\n"                                                            \
    "If the flag was not set before the operation, True is"         \
    " returned, else the result is False."                          \
)

    ret = PyArg_ParseTuple(args, "I", &flag);
    if (!ret) return NULL;

    format = G_BIN_FORMAT(pygobject_get(self));

    status = g_binary_format_set_flag(format, flag);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = serveur à manipuler.                                  *
*                args = arguments d'appel non utilisés ici.                   *
*                                                                             *
*  Description : Retire une information complémentaire à un format.           *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_format_unset_flag(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    unsigned int flag;                      /* Propriété à traiter         */
    int ret;                                /* Bilan de lecture des args.  */
    GBinFormat *format;                     /* Elément à manipuler         */
    bool status;                            /* Bilan de l'opération        */

#define BINARY_FORMAT_UNSET_FLAG_METHOD PYTHON_METHOD_DEF           \
(                                                                   \
    unset_flag, "$self, flag, /",                                   \
    METH_VARARGS, py_binary_format,                                 \
    "Remove a property from a binary format.\n"                     \
    "\n"                                                            \
    "This property is one of the values listed in the"              \
    " of pychrysalide.format.BinFormat.FormatFlag enumeration.\n"   \
    "\n"                                                            \
    "If the flag was not set before the operation, False is"        \
    " returned, else the result is True."                           \
)

    ret = PyArg_ParseTuple(args, "I", &flag);
    if (!ret) return NULL;

    format = G_BIN_FORMAT(pygobject_get(self));

    status = g_binary_format_unset_flag(format, flag);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = serveur à manipuler.                                  *
*                args = arguments d'appel non utilisés ici.                   *
*                                                                             *
*  Description : Détermine si un format possède un fanion particulier.        *
*                                                                             *
*  Retour      : Bilan de la détection.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_format_has_flag(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    unsigned int flag;                      /* Propriété à traiter         */
    int ret;                                /* Bilan de lecture des args.  */
    GBinFormat *format;                     /* Elément à manipuler         */
    bool status;                            /* Bilan de l'opération        */

#define BINARY_FORMAT_HAS_FLAG_METHOD PYTHON_METHOD_DEF             \
(                                                                   \
    has_flag, "$self, flag, /",                                     \
    METH_VARARGS, py_binary_format,                                 \
    "Test if a binary format has a given property.\n"               \
    "\n"                                                            \
    "This property is one of the values listed in the"              \
    " of pychrysalide.format.BinFormat.FormatFlag enumeration.\n"   \
    "\n"                                                            \
    "The result is a boolean value."                                \
)

    ret = PyArg_ParseTuple(args, "I", &flag);
    if (!ret) return NULL;

    format = G_BIN_FORMAT(pygobject_get(self));

    status = g_binary_format_has_flag(format, flag);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un format.                        *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Enregistre une adresse comme début d'une zone de code.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_format_register_code_point(PyObject *self, PyObject *args)
{
    unsigned long long pt;                  /* Adresse virtuelle du point  */
    DisassPriorityLevel level;              /* Nature du point fourni      */
    int ret;                                /* Bilan de lecture des args.  */
    GBinFormat *format;                     /* Format de binaire manipulé  */

#define BINARY_FORMAT_REGISTER_CODE_POINT_METHOD PYTHON_METHOD_DEF  \
(                                                                   \
    register_code_point, "$self, point, level, /",                  \
    METH_VARARGS, py_binary_format,                                 \
    "Register a virtual address as entry point or basic point.\n"   \
    "\n"                                                            \
    "The point is an integer value for the virtual memory location" \
    " of the new (entry) point. The type of this entry has to be a" \
    " pychrysalide.arch.ProcContext.DisassPriorityLevel value."     \
)

    ret = PyArg_ParseTuple(args, "kO&", &pt, convert_to_disass_priority_level, &level);
    if (!ret) return NULL;

    format = G_BIN_FORMAT(pygobject_get(self));

    g_binary_format_register_code_point(format, pt, level);

    Py_RETURN_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un format.                        *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Ajoute un symbole à la collection du format binaire.         *
*                                                                             *
*  Retour      : True si le symbole était bien localisé et a été inséré.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_format_add_symbol(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Valeur à retourner          */
    GBinSymbol *symbol;                     /* Enventuel symbole trouvé    */
    int ret;                                /* Bilan de lecture des args.  */
    GBinFormat *format;                     /* Format de binaire manipulé  */
    bool added;                             /* Bilan de l'appel interne    */

#define BINARY_FORMAT_ADD_SYMBOL_METHOD PYTHON_METHOD_DEF               \
(                                                                       \
    add_symbol, "$self, symbol, /",                                     \
    METH_VARARGS, py_binary_format,                                     \
    "Register a new symbol for the format.\n"                           \
    "\n"                                                                \
    "The symbol has to be a pychrysalide.format.BinSymbol instance."    \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_binary_symbol, &symbol);
    if (!ret) return NULL;

    format = G_BIN_FORMAT(pygobject_get(self));

    g_object_ref(G_OBJECT(symbol));
    added = g_binary_format_add_symbol(format, symbol);

    result = added ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un format.                        *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Retire un symbole de la collection du format binaire.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_format_remove_symbol(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Valeur à retourner          */
    GBinSymbol *symbol;                     /* Enventuel symbole trouvé    */
    int ret;                                /* Bilan de lecture des args.  */
    GBinFormat *format;                     /* Format de binaire manipulé  */

#define BINARY_FORMAT_REMOVE_SYMBOL_METHOD PYTHON_METHOD_DEF            \
(                                                                       \
    remove_symbol, "$self, symbol, /",                                  \
    METH_VARARGS, py_binary_format,                                     \
    "Unregister a symbol from the format.\n"                            \
    "\n"                                                                \
    "The symbol has to be a pychrysalide.format.BinSymbol instance."    \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_binary_symbol, &symbol);
    if (!ret) return NULL;

    format = G_BIN_FORMAT(pygobject_get(self));

    g_binary_format_remove_symbol(format, symbol);

    result = Py_None;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un binaire.                       *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Recherche le symbole correspondant à une étiquette.          *
*                                                                             *
*  Retour      : Symbol trouvé si l'opération a été un succès, None sinon.    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_format_find_symbol_by_label(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Valeur à retourner          */
    const char *label;                      /* Etiquette à retrouver       */
    int ret;                                /* Bilan de lecture des args.  */
    GBinFormat *format;                     /* Format de binaire manipulé  */
    GBinSymbol *symbol;                     /* Enventuel symbole trouvé    */
    bool found;                             /* Bilan de la recherche       */

#define BINARY_FORMAT_FIND_SYMBOL_BY_LABEL_METHOD PYTHON_METHOD_DEF     \
(                                                                       \
    find_symbol_by_label, "$self, label, /",                            \
    METH_VARARGS, py_binary_format,                                     \
    "Find the symbol with a given label, provided as a string.\n"       \
    "\n"                                                                \
    "The result is a pychrysalide.format.BinSymbol instance, or None"   \
    " if no symbol was found."                                          \
)

    ret = PyArg_ParseTuple(args, "s", &label);
    if (!ret) return NULL;

    format = G_BIN_FORMAT(pygobject_get(self));

    found = g_binary_format_find_symbol_by_label(format, label, &symbol);

    if (found)
    {
        result = pygobject_new(G_OBJECT(symbol));
        g_object_unref(G_OBJECT(symbol));
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
*  Paramètres  : self = classe représentant un binaire.                       *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Recherche le symbole suivant celui lié à une adresse.        *
*                                                                             *
*  Retour      : Symbol trouvé si l'opération a été un succès, None sinon.    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_format_find_symbol_at(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Valeur à retourner          */
    GBinFormat *format;                     /* Format de binaire manipulé  */
    exe_cv_info_t conv;                     /* Informations de conversion  */
    int ret;                                /* Bilan de lecture des args.  */
    GBinSymbol *symbol;                     /* Enventuel symbole trouvé    */
    bool found;                             /* Bilan de la recherche       */

#define BINARY_FORMAT_FIND_SYMBOL_AT_METHOD PYTHON_METHOD_DEF       \
(                                                                   \
    find_symbol_at, "$self, addr, /",                               \
    METH_VARARGS, py_binary_format,                                 \
    "Find the symbol located at a given address, provided as a"     \
    " pychrysalide.arch.vmpa instance.\n"                           \
    "\n"                                                            \
    "The result is a pychrysalide.format.BinSymbol instance, or"    \
    " None if no symbol was found."                                 \
)

    format = G_BIN_FORMAT(pygobject_get(self));

    conv.format = G_IS_EXE_FORMAT(format) ? G_EXE_FORMAT(format) : NULL;

    ret = PyArg_ParseTuple(args, "O&", convert_to_vmpa_using_executable, &conv);
    if (!ret) return NULL;

    found = g_binary_format_find_symbol_at(format, conv.vmpa, &symbol);

    if (found)
    {
        result = pygobject_new(G_OBJECT(symbol));
        g_object_unref(G_OBJECT(symbol));
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
*  Paramètres  : self = classe représentant un binaire.                       *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Recherche le symbole suivant celui lié à une adresse.        *
*                                                                             *
*  Retour      : Symbol trouvé si l'opération a été un succès, None sinon.    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_format_find_next_symbol_at(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Valeur à retourner          */
    GBinFormat *format;                     /* Format de binaire manipulé  */
    exe_cv_info_t conv;                     /* Informations de conversion  */
    int ret;                                /* Bilan de lecture des args.  */
    GBinSymbol *symbol;                     /* Enventuel symbole trouvé    */
    bool found;                             /* Bilan de la recherche       */

#define BINARY_FORMAT_FIND_NEXT_SYMBOL_AT_METHOD PYTHON_METHOD_DEF  \
(                                                                   \
    find_next_symbol_at, "$self, addr, /",                          \
    METH_VARARGS, py_binary_format,                                 \
    "Find the symbol next to the one found at a given address,"     \
    " provided as a pychrysalide.arch.vmpa instance.\n"             \
    "\n"                                                            \
    "The result is a pychrysalide.format.BinSymbol instance, or"    \
    " None if no symbol was found."                                 \
)

    format = G_BIN_FORMAT(pygobject_get(self));

    conv.format = G_IS_EXE_FORMAT(format) ? G_EXE_FORMAT(format) : NULL;

    ret = PyArg_ParseTuple(args, "O&", convert_to_vmpa_using_executable, &conv);
    if (!ret) return NULL;

    found = g_binary_format_find_next_symbol_at(format, conv.vmpa, &symbol);

    if (found)
    {
        result = pygobject_new(G_OBJECT(symbol));
        g_object_unref(G_OBJECT(symbol));
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
*  Paramètres  : self = classe représentant un format binaire.                *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Recherche le symbole correspondant à une adresse.            *
*                                                                             *
*  Retour      : Tuple (nom, décalage) ou Py_None.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_format_resolve_symbol(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Valeur à retourner          */
    GBinFormat *format;                     /* Format de binaire manipulé  */
    exe_cv_info_t conv;                     /* Informations de conversion  */
    int strict;                             /* Tolérance acceptée          */
    int ret;                                /* Bilan de lecture des args.  */
    GBinSymbol *symbol;                     /* Enventuel symbole trouvé    */
    phys_t diff;                            /* Décalage éventuel mesuré    */
    bool found;                             /* Bilan de la recherche       */

#define BINARY_FORMAT_RESOLVE_SYMBOL_METHOD PYTHON_METHOD_DEF       \
(                                                                   \
    resolve_symbol, "$self, addr, strict, /",                       \
    METH_VARARGS, py_binary_format,                                 \
    "Search for a position inside a symbol by a given address.\n"   \
    "\n"                                                            \
    "The result is a couple of (pychrysalide.format.BinSymbol,"     \
    " offset) values, or None if no symbol was found. The offset"   \
    " is the distance between the start location of the symbol and" \
    " the location provided as argument.\n"                         \
    "\n"                                                            \
    "If the search is run in strict mode, then the offset is"       \
    " always 0 upon success."                                       \
)

    format = G_BIN_FORMAT(pygobject_get(self));

    conv.format = G_IS_EXE_FORMAT(format) ? G_EXE_FORMAT(format) : NULL;

    ret = PyArg_ParseTuple(args, "O&p", convert_to_vmpa_using_executable, &conv, &strict);
    if (!ret) return NULL;

    found = g_binary_format_resolve_symbol(format, conv.vmpa, strict, &symbol, &diff);

    if (found)
    {
        result = PyTuple_New(2);
        PyTuple_SetItem(result, 0, pygobject_new(G_OBJECT(symbol)));
        PyTuple_SetItem(result, 1, PyLong_FromUnsignedLongLong(diff));

        g_object_unref(G_OBJECT(symbol));

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
*  Description : Fournit les particularités du format.                        *
*                                                                             *
*  Retour      : Somme de tous les fanions associés au format.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_format_get_flags(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GBinFormat *format;                     /* Elément à consulter         */
    FormatFlag flags;                       /* Indications complémentaires */

#define BINARY_FORMAT_FLAGS_ATTRIB PYTHON_GET_DEF_FULL          \
(                                                               \
    flags, py_binary_format,                                    \
    "Provide all the flags set for a format. The return value"  \
    " is of type pychrysalide.format.BinFormat.FormatFlag."     \
)

    format = G_BIN_FORMAT(pygobject_get(self));
    flags = g_binary_format_get_flags(format);

    result = cast_with_constants_group_from_type(get_python_binary_format_type(), "FormatFlag", flags);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique le boutisme employé par le format binaire analysé.   *
*                                                                             *
*  Retour      : Boutisme associé au format.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_format_get_endianness(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GBinFormat *format;                     /* Elément à consulter         */
    SourceEndian endianness;                /* Boutisme du format          */

#define BINARY_FORMAT_ENDIANNESS_ATTRIB PYTHON_GET_DEF_FULL     \
(                                                               \
    endianness, py_binary_format,                               \
    "Endianness of the format. The return value is of type"     \
    " pychrysalide.analysis.BinContent.SourceEndian."           \
)

    format = G_BIN_FORMAT(pygobject_get(self));
    endianness = g_binary_format_get_endianness(format);

    result = cast_with_constants_group_from_type(get_python_binary_content_type(), "SourceEndian", endianness);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = classe représentant un format binaire.             *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Fournit la liste de tous les symboles détectés.              *
*                                                                             *
*  Retour      : Tableau créé ou NULL si aucun symbole trouvé.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_format_get_symbols(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    PyTypeObject *iterator_type;            /* Type Python de l'itérateur  */
    PyObject *args;                         /* Liste des arguments d'appel */

#define BINARY_FORMAT_SYMBOLS_ATTRIB PYTHON_GET_DEF_FULL            \
(                                                                   \
    symbols, py_binary_format,                                      \
    "Iterable list of all symbols found in the binary format.\n"    \
    "\n"                                                            \
    "The returned iterator is a pychrysalide.format.SymIterator"    \
    " instance and remains valid until the list from the format"    \
    " does not change."                                             \
)

    iterator_type = get_python_sym_iterator_type();

    args = Py_BuildValue("On", self, 0);

    result = PyObject_CallObject((PyObject *)iterator_type, args);

    Py_DECREF(args);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                    CONSERVATION DES SOUCIS DURANT LE CHARGEMENT                    */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self = architecture concernée par la procédure.              *
*                args = instruction représentant le point de départ.          *
*                                                                             *
*  Description : Etend la liste des soucis détectés avec de nouvelles infos.  *
*                                                                             *
*  Retour      : None.                                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_format_add_error(PyObject *self, PyObject *args)
{
    BinaryFormatError type;                 /* Type d'erreur détectée      */
    vmpa2t *addr;                           /* Position d'une erreur       */
    const char *desc;                       /* Description d'une erreur    */
    int ret;                                /* Bilan de lecture des args.  */
    GBinFormat *format;                     /* Format binaire manipulé     */

#define BINARY_FORMAT_ADD_ERROR_METHOD PYTHON_METHOD_DEF            \
(                                                                   \
    add_error, "$self, type, addr, desc, /",                        \
    METH_VARARGS, py_binary_format,                                 \
    "Extend the list of detected errors linked to the format.\n"    \
    "\n"                                                            \
    "The type of error has to be one of the"                        \
    " pychrysalide.format.BinFormat.BinaryFormatError flags. The"   \
    " location of the error is a pychrysalide.arch.vmpa instance"   \
    " and a one-line description should give some details about"    \
    " what has failed."                                             \
)

    ret = PyArg_ParseTuple(args, "O&O&s", convert_to_binary_format_error, &type, convert_any_to_vmpa, &addr, &desc);
    if (!ret) return NULL;

    format = G_BIN_FORMAT(pygobject_get(self));

    g_binary_format_add_error(format, type, addr, desc);

    clean_vmpa_arg(addr);

    Py_RETURN_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit les éléments concernant tous les soucis détectés.    *
*                                                                             *
*  Retour      : Liste des erreurs relevées au niveau de l'assembleur.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_format_get_errors(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    GBinFormat *format;                     /* Format binaire manipulé     */
    size_t count;                           /* Nombre d'éléments à traiter */
    size_t i;                               /* Boucle de parcours          */
#ifndef NDEBUG
    bool status;                            /* Bilan d'un appel            */
#endif
    BinaryFormatError type;                 /* Type d'erreur détectée      */
    vmpa2t addr;                            /* Position d'une erreur       */
    char *desc;                             /* Description d'une erreur    */
    PyObject *py_type;                      /* Version Python du type      */
    PyObject *error;                        /* Nouvelle erreur à rajouter  */

#define BINARY_FORMAT_ERRORS_ATTRIB PYTHON_GET_DEF_FULL                             \
(                                                                                   \
    errors, py_binary_format,                                                       \
    "List of all detected errors which occurred while loading the binary.\n"        \
    "\n"                                                                            \
    "The result is a tuple of (pychrysalide.format.BinFormat.BinaryFormatError,"    \
    " pychrysalide.arch.vmpa, string) values, providing a location and a"           \
    " description for each error."                                                  \
)

    format = G_BIN_FORMAT(pygobject_get(self));

    g_binary_format_lock_errors(format);

    count = g_binary_format_count_errors(format);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
#ifndef NDEBUG
        status = g_binary_format_get_error(format, i, &type, &addr, &desc);
        assert(status);
#else
        g_binary_format_get_error(format, i, &type, &addr, &desc);
#endif

        py_type = cast_with_constants_group_from_type(get_python_binary_format_type(), "BinaryFormatError", type);
        error = Py_BuildValue("OO&s", py_type, build_from_internal_vmpa, &addr, desc);
        Py_DECREF(py_type);

        PyTuple_SetItem(result, i, error);

    }

    g_binary_format_unlock_errors(format);

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

PyTypeObject *get_python_binary_format_type(void)
{
    static PyMethodDef py_bin_format_methods[] = {
        BINARY_FORMAT_SET_FLAG_METHOD,
        BINARY_FORMAT_UNSET_FLAG_METHOD,
        BINARY_FORMAT_HAS_FLAG_METHOD,
        BINARY_FORMAT_REGISTER_CODE_POINT_METHOD,
        BINARY_FORMAT_ADD_SYMBOL_METHOD,
        BINARY_FORMAT_REMOVE_SYMBOL_METHOD,
        BINARY_FORMAT_FIND_SYMBOL_BY_LABEL_METHOD,
        BINARY_FORMAT_FIND_SYMBOL_AT_METHOD,
        BINARY_FORMAT_FIND_NEXT_SYMBOL_AT_METHOD,
        BINARY_FORMAT_RESOLVE_SYMBOL_METHOD,
        BINARY_FORMAT_ADD_ERROR_METHOD,
        { NULL }
    };

    static PyGetSetDef py_bin_format_getseters[] = {
        BINARY_FORMAT_FLAGS_ATTRIB,
        BINARY_FORMAT_ENDIANNESS_ATTRIB,
        BINARY_FORMAT_SYMBOLS_ATTRIB,
        BINARY_FORMAT_ERRORS_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_bin_format_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.format.BinFormat",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_IS_ABSTRACT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = BINARY_FORMAT_DOC,

        .tp_methods     = py_bin_format_methods,
        .tp_getset      = py_bin_format_getseters,

        .tp_init        = py_binary_format_init,
        .tp_new         = py_binary_format_new,

    };

    return &py_bin_format_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.format.BinFormat'.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_binary_format_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'BinFormat'     */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_binary_format_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.format");

        dict = PyModule_GetDict(module);

        if (!ensure_python_known_format_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_BIN_FORMAT, type))
            return false;

        if (!define_binary_format_constants(type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en format de binaire.                     *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_binary_format(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_binary_format_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to binary format");
            break;

        case 1:
            *((GBinFormat **)dst) = G_BIN_FORMAT(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
