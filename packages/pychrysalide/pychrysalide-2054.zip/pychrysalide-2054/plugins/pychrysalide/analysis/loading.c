
/* Chrysalide - Outil d'analyse de fichiers binaires
 * loading.c - équivalent Python du fichier "analysis/loading.c"
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


#include "loading.h"


#include <pygobject.h>


#include <analysis/loading.h>


#include "content.h"
#include "loaded.h"
#include "../access.h"
#include "../helpers.h"



/* --------------------- EXPLORATION NON BLOQUANTE DES CONTENUS --------------------- */


/* Ajoute un nouveau contenu découvert au crédit d'un groupe. */
static PyObject *py_content_explorer_populate_group(PyObject *, PyObject *);



/* ------------------- RESOLUTION DE CONTENUS BINAIRES EN CHARGES ------------------- */


/* Intègre un contenu chargé dans les résultats. */
static PyObject *py_content_resolver_add_detected(PyObject *, PyObject *);



/* ---------------------------------------------------------------------------------- */
/*                       EXPLORATION NON BLOQUANTE DES CONTENUS                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un binaire.                       *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Ajoute un nouveau contenu découvert au crédit d'un groupe.   *
*                                                                             *
*  Retour      : None.                                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_content_explorer_populate_group(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Valeur à retourner          */
    unsigned long long wid;                 /* Identifiant de groupe       */
    GBinContent *content;                   /* Contenu nouveau au final    */
    int ret;                                /* Bilan de lecture des args.  */
    GContentExplorer *explorer;             /* Explorateur à manipuler     */

    ret = PyArg_ParseTuple(args, "KO&", &wid, convert_to_binary_content, &content);
    if (!ret) return NULL;

    explorer = G_CONTENT_EXPLORER(pygobject_get(self));

    g_content_explorer_populate_group(explorer, wid, content);

    result = Py_None;
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

PyTypeObject *get_python_content_explorer_type(void)
{
    static PyMethodDef py_content_explorer_methods[] = {
        {
            "populate_group", py_content_explorer_populate_group,
            METH_VARARGS,
            "populate_group($self, wid, content, /)\n--\n\nPush a new binary content into the list to explore."
        },
        { NULL }
    };

    static PyGetSetDef py_content_explorer_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_content_explorer_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.ContentExplorer",

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = "PyChrysalide content explorer",

        .tp_methods     = py_content_explorer_methods,
        .tp_getset      = py_content_explorer_getseters

    };

    return &py_content_explorer_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide...ContentExplorer'.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_content_explorer_is_registered(void)
{
    PyTypeObject *type;                     /* Type 'ContentExplorer'      */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_content_explorer_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_CONTENT_EXPLORER, type))
            return false;

    }

    return true;

}



/* ---------------------------------------------------------------------------------- */
/*                     RESOLUTION DE CONTENUS BINAIRES EN CHARGES                     */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un binaire.                       *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Intègre un contenu chargé dans les résultats.                *
*                                                                             *
*  Retour      : None.                                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_content_resolver_add_detected(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Valeur à retourner          */
    unsigned long long wid;                 /* Identifiant de groupe       */
    GLoadedContent *loaded;                 /* Contenu chargé au final     */
    int ret;                                /* Bilan de lecture des args.  */
    GContentResolver *resolver;             /* Résolveur à manipuler       */

    ret = PyArg_ParseTuple(args, "KO&", &wid, convert_to_loaded_content, &loaded);
    if (!ret) return NULL;

    resolver = G_CONTENT_RESOLVER(pygobject_get(self));

    g_content_resolver_add_detected(resolver, wid, loaded);

    result = Py_None;
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

PyTypeObject *get_python_content_resolver_type(void)
{
    static PyMethodDef py_content_resolver_methods[] = {

        {
            "add_detected", py_content_resolver_add_detected,
            METH_VARARGS,
            "add_detected($self, wid, loaded, /)\n--\n\nAdd a binary content as loaded content ready to get analyzed."
        },
        { NULL }
    };

    static PyGetSetDef py_content_resolver_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_content_resolver_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.ContentResolver",

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = "PyChrysalide content resolver",

        .tp_methods     = py_content_resolver_methods,
        .tp_getset      = py_content_resolver_getseters

    };

    return &py_content_resolver_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide...ContentResolver'.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_content_resolver_is_registered(void)
{
    PyTypeObject *type;                     /* Type 'ContentResolver'      */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_content_resolver_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_CONTENT_RESOLVER, type))
            return false;

    }

    return true;

}
