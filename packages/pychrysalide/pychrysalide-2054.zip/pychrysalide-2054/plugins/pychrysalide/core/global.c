
/* Chrysalide - Outil d'analyse de fichiers binaires
 * global.c - équivalent Python du fichier "core/global.c"
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


#include "global.h"


#include <pygobject.h>


#include <core/global.h>


#include "../access.h"
#include "../helpers.h"
#include "../analysis/project.h"



/* Indique le mode d'exécution courant du programme. */
static PyObject *py_global_is_batch_mode(PyObject *, PyObject *);

/* Fournit l'adresse de l'explorateur de contenus courant. */
static PyObject *py_global_get_content_explorer(PyObject *, PyObject *);

/* Fournit l'adresse du résolveur de contenus courant. */
static PyObject *py_global_get_content_resolver(PyObject *, PyObject *);

/* Fournit l'adresse du projet courant. */
static PyObject *py_global_get_current_project(PyObject *, PyObject *);

/* Définit l'adresse du projet courant. */
static PyObject *py_global_set_current_project(PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = non utilisé ici.                                      *
*                                                                             *
*  Description : Indique le mode d'exécution courant du programme.            *
*                                                                             *
*  Retour      : True si le fonctionnement est sans interface.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_global_is_batch_mode(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance Python à retourner */
    bool status;                            /* Bilan de consultation       */

#define GLOBAL_IS_BATCH_MODE_METHOD PYTHON_METHOD_DEF               \
(                                                                   \
    is_batch_mode, "",                                              \
    METH_NOARGS, py_global,                                         \
    "Tell if Chrysalide is started in batch mode or with a GUI."    \
)

    status = is_batch_mode();

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = non utilisé ici.                                      *
*                                                                             *
*  Description : Fournit l'adresse de l'explorateur de contenus courant.      *
*                                                                             *
*  Retour      : Adresse de l'explorateur global ou None si aucun (!).        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_global_get_content_explorer(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance Python à retourner */
    GContentExplorer *explorer;             /* Gestionnaire natif récupéré */

#define GLOBAL_GET_CONTENT_EXPLORER_METHOD PYTHON_METHOD_DEF            \
(                                                                       \
    get_content_explorer, "",                                           \
    METH_NOARGS, py_global,                                             \
    "Get the global exploration manager discovering contents."          \
    "\n"                                                                \
    "The returned object is a pychrysalide.analysis.ContentExplorer"    \
    " instance used as singleton."                                      \
)

    explorer = get_current_content_explorer();

    if (explorer != NULL)
    {
        result = pygobject_new(G_OBJECT(explorer));
        g_object_unref(G_OBJECT(explorer));
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
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = non utilisé ici.                                      *
*                                                                             *
*  Description : Fournit l'adresse du résolveur de contenus courant.          *
*                                                                             *
*  Retour      : Adresse du résolveur global ou None si aucun (!).            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_global_get_content_resolver(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance Python à retourner */
    GContentResolver *resolver;             /* Gestionnaire natif récupéré */

#define GLOBAL_GET_CONTENT_RESOLVER_METHOD PYTHON_METHOD_DEF            \
(                                                                       \
    get_content_resolver, "",                                           \
    METH_NOARGS, py_global,                                             \
    "Get the global resolution manager translating binary contents"     \
    " into loaded contents."                                            \
    "\n"                                                                \
    "The returned object is a pychrysalide.analysis.ContentResolver"    \
    " instance used as singleton."                                      \
)

    resolver = get_current_content_resolver();

    if (resolver != NULL)
    {
        result = pygobject_new(G_OBJECT(resolver));
        g_object_unref(G_OBJECT(resolver));
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
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = non utilisé ici.                                      *
*                                                                             *
*  Description : Fournit l'adresse de l'espace de noms principal pour ROST.   *
*                                                                             *
*  Retour      : Espace de noms racine de ROST ou NULL si aucun (!).          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_global_get_rost_root_namespace(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance Python à retourner */
    GScanNamespace *root_ns;                /* Espace de noms ROST racine  */

#define GLOBAL_GET_ROST_ROOT_NAMESPACE_METHOD PYTHON_METHOD_DEF         \
(                                                                       \
    get_rost_root_namespace, "",                                        \
    METH_NOARGS, py_global,                                             \
    "Get the root namespace for ROST."                                  \
    "\n"                                                                \
    "The returned object is a pychrysalide.analysis.scan.ScanNamespace" \
    " instance used as singleton; it should not be *None*."             \
)

    root_ns = get_rost_root_namespace();

    if (root_ns != NULL)
    {
        result = pygobject_new(G_OBJECT(root_ns));
        g_object_unref(G_OBJECT(root_ns));
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
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = non utilisé ici.                                      *
*                                                                             *
*  Description : Fournit l'adresse du projet courant.                         *
*                                                                             *
*  Retour      : Adresse du résolveur global ou None si aucun.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_global_get_current_project(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance Python à retourner */
    GStudyProject *project;                 /* Projet courant récupéré     */

#define GLOBAL_GET_CURRENT_PROJECT_METHOD PYTHON_METHOD_DEF         \
(                                                                   \
    get_current_project, "",                                        \
    METH_NOARGS, py_global,                                         \
    "Get the current global project."                               \
    "\n"                                                            \
    "The returned object is an instance of type"                    \
    " pychrysalide.analysis.StudyProject."                          \
)

    project = get_current_project();

    if (project != NULL)
    {
        result = pygobject_new(G_OBJECT(project));
        g_object_unref(G_OBJECT(project));
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
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = valeur fournie à intégrer ou prendre en compte.       *
*                                                                             *
*  Description : Définit l'adresse du projet courant.                         *
*                                                                             *
*  Retour      : Bilan de l'opération pour Python.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_global_set_current_project(PyObject *self, PyObject *args)
{
    GStudyProject *project;                 /* Version GLib du projet      */
    int ret;                                /* Bilan de lecture des args.  */

#define GLOBAL_SET_CURRENT_PROJECT_METHOD PYTHON_METHOD_DEF         \
(                                                                   \
    set_current_project, "project",                                 \
    METH_VARARGS, py_global,                                        \
    "Set the current global project."                               \
    "\n"                                                            \
    "The provided project has to be an instance (or a subclass)"    \
    " of pychrysalide.analysis.StudyProject."                       \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_study_project, &project);
    if (!ret) return NULL;

    g_object_ref(G_OBJECT(project));

    set_current_project(project);

    Py_RETURN_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Définit une extension du module 'core' à compléter.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool populate_core_module_with_global(void)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Module à recompléter        */

    static PyMethodDef py_global_methods[] = {
        GLOBAL_IS_BATCH_MODE_METHOD,
        GLOBAL_GET_CONTENT_EXPLORER_METHOD,
        GLOBAL_GET_CONTENT_RESOLVER_METHOD,
        GLOBAL_GET_ROST_ROOT_NAMESPACE_METHOD,
        GLOBAL_GET_CURRENT_PROJECT_METHOD,
        GLOBAL_SET_CURRENT_PROJECT_METHOD,
        { NULL }
    };

    module = get_access_to_python_module("pychrysalide.core");

    result = register_python_module_methods(module, py_global_methods);

    return result;

}
