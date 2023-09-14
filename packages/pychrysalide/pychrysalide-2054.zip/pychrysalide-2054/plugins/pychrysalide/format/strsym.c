
/* Chrysalide - Outil d'analyse de fichiers binaires
 * strsym.c - équivalent Python du fichier "format/strsym.h"
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


#include "strsym.h"


#include <malloc.h>
#include <pygobject.h>


#include <i18n.h>


#include <format/strsym.h>
#include <plugins/dt.h>


#include "constants.h"
#include "known.h"
#include "symbol.h"
#include "../access.h"
#include "../helpers.h"
#include "../arch/vmpa.h"
#include "../arch/operands/feeder.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Accompagne la création d'une instance dérivée en Python. */
static PyObject *py_string_symbol_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_string_symbol_init(PyObject *, PyObject *, PyObject *);



/* ----------------------- VITRINE POUR CHAINES DE CARACTERES ----------------------- */


/* Indique si une chaîne de caractères est liée au format. */
static PyObject *py_string_symbol_get_structural(PyObject *, void *);

/* Définit si une chaîne de caractères est liée au format. */
static int py_string_symbol_set_structural(PyObject *, PyObject *, void *);

/* Fournit l'encodage d'une chaîne de caractères. */
static PyObject *py_string_symbol_get_encoding(PyObject *, void *);

/* Fournit la chaîne brute de caractères du symbole. */
static PyObject *py_string_symbol_get_raw(PyObject *, void *);

/* Fournit la chaîne de caractères du symbole. */
static PyObject *py_string_symbol_get_utf8(PyObject *, void *);



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

static PyObject *py_string_symbol_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

    /* Validations diverses */

    base = get_python_string_symbol_type();

    if (type == base)
        goto simple_way;

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_STR_SYMBOL, type->tp_name, NULL, NULL, NULL);

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

static int py_string_symbol_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    StringEncodingType encoding;            /* Encodage spécifié           */
    GKnownFormat *format;                   /* Format au contenu à relire  */
    mrange_t range;                         /* Version native d'un espace  */
    const char *string;                     /* Chaîne de caractères soumise*/
    vmpa2t *addr;                           /* Emplacement de chaîne       */
    int ret;                                /* Bilan de lecture des args.  */
    GStrSymbol *symbol;                     /* Version GLib du symbole     */

    static char *kwlist[] = { "encoding", "format", "range", "string", "addr", NULL };

#define STRING_SYMBOL_DOC                                                       \
    "StrSymbol is a special symbol object dedicated to strings.\n"              \
    "\n"                                                                        \
    "Instances can be created using one of the following constructors:\n"       \
    "\n"                                                                        \
    "    StrSymbol(encoding, format=pychrysalide.format.KnownFormat,"          \
    " range=pychrysalide.arch.mrange)"                                          \
    "\n"                                                                        \
    "    StrSymbol(encoding, string=string, addr=pychrysalide.arch.vmpa)"       \
    "\n"                                                                        \
    "The first constructor is aimed to be used for read-only strings available" \
    " from the raw data of the analyzed binary. The format provides the raw"    \
    " content, and the memory range specifies the location of the string.\n"    \
    "\n"                                                                        \
    "The second constructor is useful for strings which can not be extracted"   \
    " directly from the original content, such as obfuscted strings. A dynamic" \
    " string is then provided here, and the start point of this string has to"  \
    " be provided.\n"                                                           \
    "\n"                                                                        \
    "In both cases, the encoding remains the first argument, as a"              \
    " pychrysalide.format.StrSymbol.StringEncodingType value."

    /* Récupération des paramètres */

    format = NULL;
    string = NULL;
    addr = NULL;

    ret = PyArg_ParseTupleAndKeywords(args, kwds, "O&|O&O&sO&", kwlist,
                                      convert_to_string_encoding_type, &encoding,
                                      convert_to_known_format, &format,
                                      convert_any_to_mrange, &range,
                                      &string, convert_any_to_vmpa, &addr);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    symbol = G_STR_SYMBOL(pygobject_get(self));

    if (format != NULL)
        g_string_symbol_init_read_only(symbol, encoding, format, &range);

    else if (string != NULL && addr != NULL)
    {
        g_string_symbol_init_dynamic(symbol, encoding, string, addr);
        clean_vmpa_arg(addr);
    }

    else
    {
        PyErr_SetString(PyExc_ValueError, _("Invalid argument combination."));

        if (addr != NULL)
            clean_vmpa_arg(addr);

        return -1;

    }

    return 0;

}



/* ---------------------------------------------------------------------------------- */
/*                         VITRINE POUR CHAINES DE CARACTERES                         */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique si une chaîne de caractères est liée au format.      *
*                                                                             *
*  Retour      : Indication sur l'emploi de la chaîne.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_string_symbol_get_structural(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GStrSymbol *symbol;                     /* Elément à consulter         */
    bool status;                            /* Etat à transmettre          */

#define STRING_SYMBOL_STRUCTURAL_ATTRIB PYTHON_GETSET_DEF_FULL                  \
(                                                                               \
    structural, py_string_symbol,                                               \
    "True if the string symbol is linked to the file structure, else False."    \
)

    symbol = G_STR_SYMBOL(pygobject_get(self));

    status = g_string_symbol_is_structural(symbol);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Définit si une chaîne de caractères est liée au format.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_string_symbol_set_structural(PyObject *self, PyObject *value, void *closure)
{
    int ret;                                /* Bilan d'analyse             */
    GStrSymbol *symbol;                     /* Elément à consulter         */

    ret = PyBool_Check(value);
    if (!ret) return -1;

    symbol = G_STR_SYMBOL(pygobject_get(self));

    g_string_symbol_set_structural(symbol, value == Py_True);

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit l'encodage d'une chaîne de caractères.               *
*                                                                             *
*  Retour      : Type d'encodage utilisé.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_string_symbol_get_encoding(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GStrSymbol *symbol;                     /* Elément à consulter         */
    StringEncodingType encoding;            /* Encodage associé à la chaîne*/

#define STRING_SYMBOL_ENCODING_ATTRIB PYTHON_GET_DEF_FULL       \
(                                                               \
    encoding, py_string_symbol,                                 \
    "Encoding of the string, provided as a"                     \
    " pychrysalide.format.StrSymbol.StringEncodingType value."  \
)

    symbol = G_STR_SYMBOL(pygobject_get(self));
    encoding = g_string_symbol_get_encoding(symbol);

    result = cast_with_constants_group_from_type(get_python_string_symbol_type(), "StringEncodingType", encoding);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la chaîne brute de caractères du symbole.            *
*                                                                             *
*  Retour      : Chaîne de caractères d'origine.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_string_symbol_get_raw(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GStrSymbol *symbol;                     /* Elément à consulter         */
    size_t len;                             /* Taille de la chaîne         */
    const char *data;                       /* Données à manipuler         */

#define STRING_SYMBOL_RAW_ATTRIB PYTHON_GET_DEF_FULL    \
(                                                       \
    raw, py_string_symbol,                              \
    "Raw data of the string, provided as bytes."        \
)

    symbol = G_STR_SYMBOL(pygobject_get(self));
    data = g_string_symbol_get_raw(symbol, &len);

    result = PyBytes_FromStringAndSize(data, len);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la chaîne de caractères du symbole.                  *
*                                                                             *
*  Retour      : Chaîne de caractères, à priori en UTF-8.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_string_symbol_get_utf8(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GStrSymbol *symbol;                     /* Elément à consulter         */
    size_t len;                             /* Taille de la chaîne         */
    const char *data;                       /* Données à manipuler         */

#define STRING_SYMBOL_UTF8_ATTRIB PYTHON_GET_DEF_FULL   \
(                                                       \
    utf8, py_string_symbol,                             \
    "String content as UTF-8 data."                     \
)

    symbol = G_STR_SYMBOL(pygobject_get(self));
    data = g_string_symbol_get_utf8(symbol, &len);

    result = PyUnicode_FromStringAndSize(data, len);

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

PyTypeObject *get_python_string_symbol_type(void)
{
    static PyMethodDef py_string_symbol_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_string_symbol_getseters[] = {
        STRING_SYMBOL_STRUCTURAL_ATTRIB,
        STRING_SYMBOL_ENCODING_ATTRIB,
        STRING_SYMBOL_RAW_ATTRIB,
        STRING_SYMBOL_UTF8_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_string_symbol_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.format.StrSymbol",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = STRING_SYMBOL_DOC,

        .tp_methods     = py_string_symbol_methods,
        .tp_getset      = py_string_symbol_getseters,

        .tp_init        = py_string_symbol_init,
        .tp_new         = py_string_symbol_new

    };

    return &py_string_symbol_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.format.StrSymbol'.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_string_symbol_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'StrSymbol'     */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_string_symbol_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.format");

        dict = PyModule_GetDict(module);

        if (!ensure_python_proxy_feeder_is_registered())
            return false;

        if (!ensure_python_binary_symbol_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_STR_SYMBOL, type))
            return false;

        if (!define_string_symbol_constants(type))
            return false;

    }

    return true;

}
