
/* Chrysalide - Outil d'analyse de fichiers binaires
 * project.c - équivalent Python du fichier "analysis/project.c"
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


#include "project.h"


#include <malloc.h>
#include <pygobject.h>


#include <analysis/project.h>


#include "content.h"
#include "loaded.h"
#include "../access.h"
#include "../helpers.h"



/* Crée un nouvel objet Python de type 'StudyProject'. */
static PyObject *py_study_project_new(PyTypeObject *, PyObject *, PyObject *);

/* Procède à l'enregistrement d'un projet donné. */
static PyObject *py_study_project_save(PyObject *, PyObject *);

/* Détermine si un contenu doit être écarté ou conservé. */
static bool filter_loadable_content_with_python(GLoadedContent *, PyObject *);

/* Assure l'intégration de contenus binaires dans un projet. */
static PyObject *py_study_project_discover_binary_content(PyObject *, PyObject *);

/* Attache un contenu donné à un projet donné. */
static PyObject *py_study_project_attach_content(PyObject *, PyObject *);

/* Fournit l'ensemble des contenus associés à un projet. */
static PyObject *py_study_project_get_contents(PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de l'objet à instancier.                         *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Crée un nouvel objet Python de type 'StudyProject'.          *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_study_project_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Instance à retourner        */
    const char *filename;                   /* Destination de la sauvegarde*/
    int cache;                              /* Préparation de rendu ?      */
    int ret;                                /* Bilan de lecture des args.  */
    GStudyProject *project;                 /* Version GLib du projet      */

    filename = NULL;
    cache = 0;

    ret = PyArg_ParseTuple(args, "|sp", &filename, &cache);
    if (!ret) return NULL;

    if (filename != NULL)
        project = g_study_project_open(filename, cache);
    else
        project = g_study_project_new();

    result = pygobject_new(G_OBJECT(project));

    if (project != NULL)
        g_object_unref(project);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = projet d'étude à manipuler.                           *
*                args = arguments accompagnant l'appel.                       *
*                                                                             *
*  Description : Procède à l'enregistrement d'un projet donné.                *
*                                                                             *
*  Retour      : Py_True si l'enregistrement s'est déroule sans encombre.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_study_project_save(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GStudyProject *project;                 /* Version GLib du format      */
    const char *filename;                   /* Destination de la sauvegarde*/
    int ret;                                /* Bilan de lecture des args.  */
    bool status;                            /* Bilan de l'opération        */

    project = G_STUDY_PROJECT(pygobject_get(self));

    ret = PyArg_ParseTuple(args, "s", &filename);
    if (!ret) return NULL;

    status = g_study_project_save(project, filename);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content  = contenu chargeable à étudier ou NULL à la fin.    *
*                callable = procédure de filtre en Python.                    *
*                                                                             *
*  Description : Détermine si un contenu doit être écarté ou conservé.        *
*                                                                             *
*  Retour      : true si le contenu doit être conservé, false sinon.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool filter_loadable_content_with_python(GLoadedContent *content, PyObject *callable)
{
    bool result;                            /* Bilan à retourner           */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *arg;                          /* Argument à fournir au filtre*/
    PyObject *status;                       /* Bilan de l'analyse          */

    gstate = PyGILState_Ensure();

    if (content == NULL)
    {
        Py_DECREF(callable);
        result = false;
    }

    else
    {
        arg = pygobject_new(G_OBJECT(content));

        status = PyObject_CallFunctionObjArgs(callable, arg, NULL);

        if (PyErr_Occurred())
            PyErr_Print();

        result = status == NULL || status == Py_False || status == Py_None ? false : true;
        Py_XDECREF(status);

        Py_DECREF(arg);

    }

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = projet d'étude à manipuler.                           *
*                args = arguments accompagnant l'appel.                       *
*                                                                             *
*  Description : Assure l'intégration de contenus binaires dans un projet.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_study_project_discover_binary_content(PyObject *self, PyObject *args)
{
    GBinContent *content;                   /* Instance de contenu binaire */
    int cache;                              /* Préparation de rendu ?      */
    PyObject *callable;                     /* Filtre de contenus éventuel */
    int ret;                                /* Bilan de lecture des args.  */
    GStudyProject *project;                 /* Version GLib du format      */

    cache = 0;
    callable = NULL;

    ret = PyArg_ParseTuple(args, "O&|pO&",
                           convert_to_binary_content, &content,
                           &cache,
                           convert_to_callable, &callable);
    if (!ret) return NULL;

    project = G_STUDY_PROJECT(pygobject_get(self));

    if (callable != NULL)
    {
        Py_INCREF(callable);

        g_study_project_discover_binary_content(project, content, cache,
                                                (filter_loadable_cb)filter_loadable_content_with_python,
                                                callable);

    }

    else
        g_study_project_discover_binary_content(project, content, cache, NULL, NULL);

    Py_RETURN_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = projet d'étude à manipuler.                           *
*                args = arguments accompagnant l'appel.                       *
*                                                                             *
*  Description : Attache un contenu donné à un projet donné.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_study_project_attach_content(PyObject *self, PyObject *args)
{
    GLoadedContent *content;                /* Instance GLib correspondante*/
    int ret;                                /* Bilan de lecture des args.  */
    GStudyProject *project;                 /* Version GLib du format      */

    ret = PyArg_ParseTuple(args, "O&", convert_to_loaded_content, &content);
    if (!ret) return NULL;

    project = G_STUDY_PROJECT(pygobject_get(self));

    g_study_project_attach_content(project, content);

    Py_RETURN_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit l'ensemble des contenus associés à un projet.        *
*                                                                             *
*  Retour      : Liste de contenus chargés.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_study_project_get_contents(PyObject *self, void *closure)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    GStudyProject *project;                 /* Version GLib du format      */
    size_t count;                           /* Nombre de contenus présents */
    GLoadedContent **contents;              /* Liste de contenus chargés   */
    size_t i;                               /* Boucle de parcours          */

    project = G_STUDY_PROJECT(pygobject_get(self));

    contents = g_study_project_get_contents(project, &count);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
        PyTuple_SetItem(result, i, pygobject_new(G_OBJECT(contents[i])));

        g_object_unref(G_OBJECT(contents[i]));

    }

    if (contents != NULL)
        free(contents);

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

PyTypeObject *get_python_study_project_type(void)
{
    static PyMethodDef py_study_project_methods[] = {
        {
            "save", py_study_project_save,
            METH_VARARGS,
            "save($self, filename, /)\n--\n\nSave the project into a given file."
        },
        {
            "discover", py_study_project_discover_binary_content,
            METH_VARARGS,
            "discover($self, content, cache, filter/)\n--\n\nExplore a new binary content for the project."
        },
        {
            "attach", py_study_project_attach_content,
            METH_VARARGS,
            "attach($self, loaded, /)\n--\n\nAdd a loaded content to the project."
        },
        { NULL }
    };

    static PyGetSetDef py_study_project_getseters[] = {
        {
            "contents", py_study_project_get_contents, NULL,
            "List of all loaded contents for the project.", NULL
        },

        { NULL }
    };

    static PyTypeObject py_study_project_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.StudyProject",

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = "PyChrysalide study project",

        .tp_methods     = py_study_project_methods,
        .tp_getset      = py_study_project_getseters,
        .tp_new         = py_study_project_new

    };

    return &py_study_project_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.analysis.StudyProject'.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_study_project_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'StudyProject'  */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_study_project_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_STUDY_PROJECT, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en projet d'étude.                        *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_study_project(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_study_project_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to study project");
            break;

        case 1:
            *((GStudyProject **)dst) = G_STUDY_PROJECT(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
