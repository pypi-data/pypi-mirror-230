
/* Chrysalide - Outil d'analyse de fichiers binaires
 * context.c - équivalent Python du fichier "analysis/scan/context.c"
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


#include "context.h"


#include <pygobject.h>


#include <i18n.h>
#include <analysis/content.h>
#include <analysis/scan/context-int.h>
#include <analysis/scan/expr.h>
#include <plugins/pychrysalide/access.h>
#include <plugins/pychrysalide/helpers.h>
#include <plugins/pychrysalide/analysis/content.h>
#include <plugins/pychrysalide/analysis/scan/expr.h>



CREATE_DYN_CONSTRUCTOR(scan_context, G_TYPE_SCAN_CONTEXT);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_scan_context_init(PyObject *, PyObject *, PyObject *);

/* Note que la phase d'analyse de contenu est terminée. */
static PyObject *py_scan_context_mark_scan_as_done(PyObject *, PyObject *);

/* Indique si une correspondance globale a pu être établie. */
static PyObject *py_scan_context_has_match_for_rule(PyObject *, PyObject *);

/* Indique si la phase d'analyse de contenu est terminée. */
static PyObject *py_scan_context_is_scan_done(PyObject *, void *);



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

static int py_scan_context_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    int ret;                                /* Bilan de lecture des args.  */

#define SCAN_CONTEXT_DOC                                            \
    "A ScanContext object tracks results of a run analysis process" \
    " against binary contents.\n"                                   \
    "\n"                                                            \
    "Instances can be created using the following constructor:\n"   \
    "\n"                                                            \
    "    ScanContext()"

    /* Récupération des paramètres */

    ret = PyArg_ParseTuple(args, "");
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un format.                        *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Note que la phase d'analyse de contenu est terminée.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_scan_context_mark_scan_as_done(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Contexte de suivi à renvoyer*/
    GScanContext *context;                  /* Contexte de suivi d'analyse */

#define SCAN_CONTEXT_MARK_SCAN_AS_DONE_METHOD PYTHON_METHOD_DEF \
(                                                               \
    mark_scan_as_done, "$self",                                 \
    METH_NOARGS, py_scan_context,                               \
    "Note that the analysis operations are finished."           \
)

    context = G_SCAN_CONTEXT(pygobject_get(self));

    g_scan_context_mark_scan_as_done(context);

    result = Py_None;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un format.                        *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Indique si une correspondance globale a pu être établie.     *
*                                                                             *
*  Retour      : Bilan final d'une analyse (False par défaut).                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_scan_context_has_match_for_rule(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Contexte de suivi à renvoyer*/
    const char *name;                       /* Désignation de règle        */
    int ret;                                /* Bilan de lecture des args.  */
    GScanContext *context;                  /* Contexte de suivi d'analyse */
    bool matched;                           /* Bilan d'analyse à renvoyer  */

#define SCAN_CONTEXT_HAS_MATCH_FOR_RULE_METHOD PYTHON_METHOD_DEF    \
(                                                                   \
    has_match_for_rule, "$self, name, /",                           \
    METH_VARARGS, py_scan_context,                                  \
    "Provide the match status for a given scan rule.\n"             \
    "\n"                                                            \
    "The *name* argument points to the registered rule to query.\n" \
    "\n"                                                            \
    "The method returns the scan final status as a boolean: *True*" \
    " in case of match, *False* otherwise."                         \
)

    ret = PyArg_ParseTuple(args, "s", &name);
    if (!ret) return NULL;

    context = G_SCAN_CONTEXT(pygobject_get(self));

    matched = g_scan_context_has_match_for_rule(context, name);

    result = matched ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique si la phase d'analyse de contenu est terminée.       *
*                                                                             *
*  Retour      : True si la phase de scan est terminée, False sinon.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_scan_context_is_scan_done(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    GScanContext *context;                  /* Contexte de suivi d'analyse */
    bool status;                            /* Bilan de consultation       */

#define SCAN_CONTEXT_IS_SCAN_DONE_ATTRIB PYTHON_IS_DEF_FULL     \
(                                                               \
    scan_done, py_scan_context,                                 \
    "Tell if the analysis operations are finished.\n"           \
    "\n"                                                        \
    "The result is a boolean: *True* if the scan is marked as"  \
    " done, *False* otherwise."                                 \
)

    context = G_SCAN_CONTEXT(pygobject_get(self));

    status = g_scan_context_is_scan_done(context);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

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

PyTypeObject *get_python_scan_context_type(void)
{
    static PyMethodDef py_scan_context_methods[] = {
        SCAN_CONTEXT_MARK_SCAN_AS_DONE_METHOD,
        SCAN_CONTEXT_HAS_MATCH_FOR_RULE_METHOD,
        { NULL }
    };

    static PyGetSetDef py_scan_context_getseters[] = {
        SCAN_CONTEXT_IS_SCAN_DONE_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_scan_context_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.scan.ScanContext",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = SCAN_CONTEXT_DOC,

        .tp_methods     = py_scan_context_methods,
        .tp_getset      = py_scan_context_getseters,

        .tp_init        = py_scan_context_init,
        .tp_new         = py_scan_context_new,

    };

    return &py_scan_context_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.....scan.ScanContext.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_scan_context_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'ScanContext'   */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_scan_context_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.scan");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_SCAN_CONTEXT, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en contexte de suivi d'analyse.           *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_scan_context(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_scan_context_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to scan context");
            break;

        case 1:
            *((GScanContext **)dst) = G_SCAN_CONTEXT(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
