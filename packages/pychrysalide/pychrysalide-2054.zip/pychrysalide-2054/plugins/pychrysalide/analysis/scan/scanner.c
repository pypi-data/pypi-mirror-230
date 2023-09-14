
/* Chrysalide - Outil d'analyse de fichiers binaires
 * scanner.c - équivalent Python du fichier "analysis/scan/scanner.c"
 *
 * Copyright (C) 2022 Cyrille Bagard
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


#include "scanner.h"


#include <malloc.h>
#include <pygobject.h>


#include <i18n.h>
#include <analysis/content.h>
#include <analysis/scan/context.h>
#include <analysis/scan/scanner-int.h>


#include "context.h"
#include "options.h"
#include "../content.h"
#include "../../access.h"
#include "../../helpers.h"



CREATE_DYN_CONSTRUCTOR(content_scanner, G_TYPE_CONTENT_SCANNER);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_content_scanner_init(PyObject *, PyObject *, PyObject *);

/* Lance une analyse d'un contenu binaire. */
static PyObject *py_content_scanner_analyze(PyObject *, PyObject *);

/* Convertit un gestionnaire de recherches en JSON. */
static PyObject *py_content_scanner_convert_to_json(PyObject *, PyObject *);

/* Indique le chemin d'un éventuel fichier de source. */
static PyObject *py_content_scanner_get_filename(PyObject *, void *);



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

static int py_content_scanner_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    const char *text;                       /* Contenu de règles à traiter */
    const char *filename;                   /* Fichier de définitions      */
    int ret;                                /* Bilan de lecture des args.  */
    GContentScanner *scanner;               /* Création GLib à transmettre */

    static char *kwlist[] = { "text", "filename", NULL };

#define CONTENT_SCANNER_DOC                                         \
    "A ContentScanner object provides support for rules processing" \
    " against binary contents.\n"                                   \
    "\n"                                                            \
    "Instances can be created using one of the following"           \
    " constructors:\n"                                              \
    "\n"                                                            \
    "    ContentScanner(text=str)"                                  \
    "\n"                                                            \
    "    ContentScanner(filename=str)"                              \
    "\n"                                                            \
    "Where *text* is a string for the rules definitions and"        \
    " *filename* an alternative string for a path pointing to a"    \
    " definition file."

    /* Récupération des paramètres */

    text = NULL;
    filename = NULL;

    ret = PyArg_ParseTupleAndKeywords(args, kwds, "|ss", kwlist, &text, &filename);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    scanner = G_CONTENT_SCANNER(pygobject_get(self));

    if (text != NULL)
    {
        if (!g_content_scanner_create_from_text(scanner, text))
        {
            PyErr_SetString(PyExc_ValueError, _("Unable to create content scanner."));
            return -1;
        }

    }

    else if (filename != NULL)
    {
        if (!g_content_scanner_create_from_file(scanner, filename))
        {
            PyErr_SetString(PyExc_ValueError, _("Unable to create content scanner."));
            return -1;
        }

    }

    else
    {
        PyErr_SetString(PyExc_ValueError, _("Unable to create empty content scanner."));
        return -1;
    }

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un format.                        *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Lance une analyse d'un contenu binaire.                      *
*                                                                             *
*  Retour      : Contexte de suivi pour l'analyse menée.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_content_scanner_analyze(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Contexte de suivi à renvoyer*/
    GScanOptions *options;                  /* Paramètres d'analyse        */
    GBinContent *content;                   /* Contenu binaire à traiter   */
    int ret;                                /* Bilan de lecture des args.  */
    GContentScanner *scanner;               /* Encadrement de recherche    */
    GScanContext *context;                  /* Contexte de suivi           */

#define CONTENT_SCANNER_ANALYZE_METHOD PYTHON_METHOD_DEF            \
(                                                                   \
    analyze, "$self, options, content, /",                          \
    METH_VARARGS, py_content_scanner,                               \
    "Run a scan against a binary content.\n"                        \
    "\n"                                                            \
    "The *content* argument is a pychrysalide.analysis.BinContent"  \
    " object pointing to data to analyze.\n"                        \
    "\n"                                                            \
    "The method returns a pychrysalide.analysis.scan.ScanContext"   \
    " object tracking all the scan results."                        \
)

    ret = PyArg_ParseTuple(args, "O&O&", convert_to_scan_options, &options, convert_to_binary_content, &content);
    if (!ret) return NULL;

    scanner = G_CONTENT_SCANNER(pygobject_get(self));

    context = g_content_scanner_analyze(scanner, options, content);

    result = pygobject_new(G_OBJECT(context));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un format.                        *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Convertit un gestionnaire de recherches en texte.            *
*                                                                             *
*  Retour      : Données textuelles ou None en cas d'erreur.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_content_scanner_convert_to_text(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Contexte de suivi à renvoyer*/
    GScanContext *context;                  /* Contexte d'analyse          */
    int ret;                                /* Bilan de lecture des args.  */
    GContentScanner *scanner;               /* Encadrement de recherche    */
    char *out;                              /* Données en sortie           */

#define CONTENT_SCANNER_CONVERT_TO_TEXT_METHOD PYTHON_METHOD_DEF            \
(                                                                           \
    convert_to_text, "$self, context, /",                                   \
    METH_VARARGS, py_content_scanner,                                       \
    "Output a scan results as text.\n"                                      \
    "\n"                                                                    \
    "The *context* argument is a pychrysalide.analysis.scan.ScanContext"    \
    " instance provided by a previous call to *self.analyze()*. This"       \
    " context stores all the scan results.\n"                               \
    "\n"                                                                    \
    "The method returns a string value, or *None* in case of failure."      \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_scan_context, &context);
    if (!ret) return NULL;

    scanner = G_CONTENT_SCANNER(pygobject_get(self));

    out = g_content_scanner_convert_to_text(scanner, context);

    if (out != NULL)
    {
        result = PyUnicode_FromString(out);
        free(out);
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
*  Paramètres  : self = classe représentant un format.                        *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Convertit un gestionnaire de recherches en JSON.             *
*                                                                             *
*  Retour      : Données textuelles au format JSON ou None en cas d'erreur.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_content_scanner_convert_to_json(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Contexte de suivi à renvoyer*/
    GScanContext *context;                  /* Contexte d'analyse          */
    int ret;                                /* Bilan de lecture des args.  */
    GContentScanner *scanner;               /* Encadrement de recherche    */
    char *out;                              /* Données en sortie           */

#define CONTENT_SCANNER_CONVERT_TO_JSON_METHOD PYTHON_METHOD_DEF            \
(                                                                           \
    convert_to_json, "$self, context, /",                                   \
    METH_VARARGS, py_content_scanner,                                       \
    "Output a scan results as JSON data.\n"                                 \
    "\n"                                                                    \
    "The *context* argument is a pychrysalide.analysis.scan.ScanContext"    \
    " instance provided by a previous call to *self.analyze()*. This"       \
    " context stores all the scan results.\n"                               \
    "\n"                                                                    \
    "The method returns JSON data as a string value, or *None* in case"     \
    " of failure."                                                          \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_scan_context, &context);
    if (!ret) return NULL;

    scanner = G_CONTENT_SCANNER(pygobject_get(self));

    out = g_content_scanner_convert_to_json(scanner, context);

    if (out != NULL)
    {
        result = PyUnicode_FromString(out);
        free(out);
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
*  Description : Indique le chemin d'un éventuel fichier de source.           *
*                                                                             *
*  Retour      : Chemin d'un éventuel fichier de définitions ou NULL.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_content_scanner_get_filename(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GContentScanner *scanner;               /* Analyseur à consulter       */
    const char *filename;                   /* Chemin d'accès à transmettre*/

#define CONTENT_SCANNER_FILENAME_ATTRIB PYTHON_GET_DEF_FULL     \
(                                                               \
    filename, py_content_scanner,                               \
    "Provide the access path to the source file of the rules'"  \
    " definition, or *None* if these rules have not been loaded"\
    " from memory."                                             \
)

    scanner = G_CONTENT_SCANNER(pygobject_get(self));

    filename = g_content_scanner_get_filename(scanner);

    if (filename != NULL)
        result = PyUnicode_FromString(filename);

    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

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

PyTypeObject *get_python_content_scanner_type(void)
{
    static PyMethodDef py_content_scanner_methods[] = {
        CONTENT_SCANNER_ANALYZE_METHOD,
        CONTENT_SCANNER_CONVERT_TO_TEXT_METHOD,
        CONTENT_SCANNER_CONVERT_TO_JSON_METHOD,
        { NULL }
    };

    static PyGetSetDef py_content_scanner_getseters[] = {
        CONTENT_SCANNER_FILENAME_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_content_scanner_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.scan.ContentScanner",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = CONTENT_SCANNER_DOC,

        .tp_methods     = py_content_scanner_methods,
        .tp_getset      = py_content_scanner_getseters,

        .tp_init        = py_content_scanner_init,
        .tp_new         = py_content_scanner_new,

    };

    return &py_content_scanner_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide...scan.ContentScanner. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_content_scanner_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'ContentScanner'*/
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_content_scanner_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.scan");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_CONTENT_SCANNER, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en scanner de contenus binaires.          *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_content_scanner(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_content_scanner_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to content scanner");
            break;

        case 1:
            *((GContentScanner **)dst) = G_CONTENT_SCANNER(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
