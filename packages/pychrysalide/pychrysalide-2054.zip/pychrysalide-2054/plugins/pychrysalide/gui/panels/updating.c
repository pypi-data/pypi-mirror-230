
/* Chrysalide - Outil d'analyse de fichiers binaires
 * updating.c - équivalent Python du fichier "gui/panels/updating.h"
 *
 * Copyright (C) 2020 Cyrille Bagard
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


#include "updating.h"


#include <pygobject.h>


#include <core/queue.h>
#include <gui/panels/updating-int.h>


#include "../../access.h"
#include "../../helpers.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Procède à l'initialisation de l'interface de génération. */
static void py_updatable_panel_interface_init(GUpdatablePanelIface *, gpointer *);

/* Prépare une opération de mise à jour de panneau. */
static bool py_updatable_panel_setup_wrapper(const GUpdatablePanel *, unsigned int, size_t *, void **, char **);

/* Obtient le groupe de travail dédié à une mise à jour. */
static wgroup_id_t py_updatable_panel_get_group_wrapper(const GUpdatablePanel *);

/* Bascule l'affichage d'un panneau avant mise à jour. */
static void py_updatable_panel_introduce_wrapper(const GUpdatablePanel *, unsigned int, void *);

/* Réalise une opération de mise à jour de panneau. */
static void py_updatable_panel_process_wrapper(const GUpdatablePanel *, unsigned int, GtkStatusStack *, activity_id_t, void *);

/* Bascule l'affichage d'un panneau après mise à jour. */
static void py_updatable_panel_conclude_wrapper(GUpdatablePanel *, unsigned int, void *);

/* Supprime les données dynamiques utilisées à la mise à jour. */
static void py_updatable_panel_clean_data_wrapper(const GUpdatablePanel *, unsigned int, void *);



/* ------------------------- CONNEXION AVEC L'API DE PYTHON ------------------------- */


/* Prépare et lance l'actualisation d'un panneau. */
static PyObject *py_updatable_panel_run_update(PyObject *, PyObject *);



/* ---------------------------------------------------------------------------------- */
/*                          GLUE POUR CREATION DEPUIS PYTHON                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : iface  = interface GLib à initialiser.                       *
*                unused = adresse non utilisée ici.                           *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de génération.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_updatable_panel_interface_init(GUpdatablePanelIface *iface, gpointer *unused)
{

#define UPDATABLE_PANEL_DOC                                                 \
    "UpdatablePanel defines an interface as helper for panels updates."     \
    " Panels contents can thus get hidden then restored easily once data"   \
    " is fully processed.\n"                                                \
    "\n"                                                                    \
    "A typical class declaration for a new implementation looks like:\n"    \
    "\n"                                                                    \
    "    class NewImplem(GObject.Object, UpdatablePanel):\n"                \
    "        ...\n"                                                         \
    "\n"                                                                    \
    "The following methods have to be defined for new implementations:\n"   \
    "* pychrysalide.gui.panels.UpdatablePanel._setup();\n"                  \
    "* pychrysalide.gui.panels.UpdatablePanel._introduce();\n"              \
    "* pychrysalide.gui.panels.UpdatablePanel._process();\n"                \
    "* pychrysalide.gui.panels.UpdatablePanel._conclude();\n"               \
    "* pychrysalide.gui.panels.UpdatablePanel._clean_data().\n"             \
    "\n"                                                                    \
    "The following attribute has to be defined for new implementations:\n"  \
    "* pychrysalide.gui.panels.UpdatablePanel._working_group_id.\n"         \

    iface->setup = py_updatable_panel_setup_wrapper;
    iface->get_group = py_updatable_panel_get_group_wrapper;
    iface->introduce = py_updatable_panel_introduce_wrapper;
    iface->process = py_updatable_panel_process_wrapper;
    iface->conclude = py_updatable_panel_conclude_wrapper;
    iface->clean = py_updatable_panel_clean_data_wrapper;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau ciblé par une mise à jour.                   *
*                uid   = identifiant de la phase de traitement.               *
*                count = nombre d'étapes à prévoir dans le traitement. [OUT]  *
*                data  = données sur lesquelles s'appuyer ensuite. [OUT]      *
*                msg   = description du message d'information. [OUT]          *
*                                                                             *
*  Description : Prépare une opération de mise à jour de panneau.             *
*                                                                             *
*  Retour      : Bilan de la préparation.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_updatable_panel_setup_wrapper(const GUpdatablePanel *panel, unsigned int uid, size_t *count, void **data, char **msg)
{
    bool result;                            /* Bilan à retourner           */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan de consultation       */
    PyObject *item;                         /* Elément obtenu              */

#define UPDATABLE_PANEL_SETUP_WRAPPER PYTHON_WRAPPER_DEF                    \
(                                                                           \
    _setup, "$self, uid, /",                                                \
    METH_VARARGS,                                                           \
    "Abstract method used to prepare an update process for a panel.\n"      \
    "\n"                                                                    \
    "The *uid* identifier is an arbitrary number identifying the update"    \
    " process.\n"                                                           \
    "\n"                                                                    \
    "The expected result is a tuple containing three items:\n"              \
    "* the number of items to be processed, in order to synchronize with"   \
    " the progress shown in the status bar;\n"                              \
    "* an optional object used to store final result (or None);\n"          \
    "* a text message to display as the name of the update operation."      \
)

    result = false;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(panel));

    if (has_python_method(pyobj, "_setup"))
    {
        args = PyTuple_New(1);
        PyTuple_SetItem(args, 0, PyLong_FromUnsignedLong(uid));

        pyret = run_python_method(pyobj, "_setup", args);

        if (!PyTuple_Check(pyret) || PyTuple_Size(pyret) != 3)
        {
            PyErr_SetString(PyExc_ValueError, "the provided quantity has to be a tuple with three items");
            goto exit;
        }

        item = PyTuple_GetItem(pyret, 0);
        if (!PyLong_Check(item)) goto exit;

        *count = PyLong_AsUnsignedLongLong(item);

        item = PyTuple_GetItem(pyret, 1);

        Py_INCREF(item);
        *data = item;

        item = PyTuple_GetItem(pyret, 2);
        if (!PyUnicode_Check(item))
        {
            Py_DECREF(item);
            *data = NULL;
            goto exit;
        }

        *msg = strdup(PyUnicode_AsUTF8(item));

        result = true;

    exit:

        Py_XDECREF(pyret);

        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau ciblé par une mise à jour.                   *
*                                                                             *
*  Description : Obtient le groupe de travail dédié à une mise à jour.        *
*                                                                             *
*  Retour      : Identifiant de groupe de travail.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static wgroup_id_t py_updatable_panel_get_group_wrapper(const GUpdatablePanel *panel)
{
    wgroup_id_t result;                     /* Identifiant à retourner     */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyattr;                       /* Attribut de l'objet Python  */
    int ret;                                /* Bilan d'une conversion      */

#define UPDATABLE_PANEL_WORKING_GROUP_ID_ATTRIB_WRAPPER PYTHON_GETTER_WRAPPER_DEF   \
(                                                                                   \
    _working_group_id,                                                              \
    "Identifier of a dedicated working group processing panel update jobs.\n"       \
    "\n"                                                                            \
    "The result has to be an integer."                                              \
)

    result = DEFAULT_WORK_GROUP;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(panel));

    if (PyObject_HasAttrString(pyobj, "_working_group_id"))
    {
        pyattr = PyObject_GetAttrString(pyobj, "_working_group_id");

        if (pyattr != NULL)
        {
            ret = PyLong_Check(pyattr);

            if (ret)
                result = PyLong_AsUnsignedLongLong(pyattr);

            Py_DECREF(pyattr);

        }

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau ciblé par une mise à jour.                   *
*                uid   = identifiant de la phase de traitement.               *
*                data  = données préparées par l'appelant.                    *
*                                                                             *
*  Description : Bascule l'affichage d'un panneau avant mise à jour.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_updatable_panel_introduce_wrapper(const GUpdatablePanel *panel, unsigned int uid, void *data)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pydata;                       /* Données au format Python    */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan de consultation       */

#define UPDATABLE_PANEL_INTRODUCE_WRAPPER PYTHON_WRAPPER_DEF                \
(                                                                           \
    _introduce, "$self, uid, data, /",                                      \
    METH_VARARGS,                                                           \
    "Abstract method used to introduce the update process; display switch"  \
    " is here an option.\n"                                                 \
    "\n"                                                                    \
    "The *uid* identifier is the same identifier provided for a previous"   \
    " call to pychrysalide.gui.panels.UpdatablePanel._setup(), and *data*"  \
    " is an optional object instance."                                      \
)

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(panel));
    pydata = (PyObject *)data;

    if (has_python_method(pyobj, "_introduce"))
    {
        Py_INCREF(pydata);

        args = PyTuple_New(2);
        PyTuple_SetItem(args, 0, PyLong_FromUnsignedLong(uid));
        PyTuple_SetItem(args, 1, pydata);

        pyret = run_python_method(pyobj, "_introduce", args);

        Py_XDECREF(pyret);

        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel  = panneau ciblé par une mise à jour.                  *
*                uid    = identifiant de la phase de traitement.              *
*                status = barre de statut à tenir informée.                   *
*                id     = identifiant pour le suivi de la progression.        *
*                data   = données préparées par l'appelant.                   *
*                                                                             *
*  Description : Réalise une opération de mise à jour de panneau.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_updatable_panel_process_wrapper(const GUpdatablePanel *panel, unsigned int uid, GtkStatusStack *status, activity_id_t id, void *data)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pydata;                       /* Données au format Python    */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan de consultation       */

#define UPDATABLE_PANEL_PROCESS_WRAPPER PYTHON_WRAPPER_DEF                  \
(                                                                           \
    _process, "$self, uid, status, id, data, /",                            \
    METH_VARARGS,                                                           \
    "Abstract method used to perform the computing of data to render.\n"    \
    "\n"                                                                    \
    "The *uid* identifier is the same identifier provided for a previous"   \
    " call to pychrysalide.gui.panels.UpdatablePanel._setup(), *status* is" \
    " a pychrysalide.gtkext.StatusStack instance, *id* refers to the"       \
    " identifier for message display inside the status bar and *data* is"   \
    " an optional object instance.\n"                                       \
    "\n"                                                                    \
    "The method is called from a dedicated processing thread."              \
)

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(panel));
    pydata = (PyObject *)data;

    if (has_python_method(pyobj, "_process"))
    {
        Py_INCREF(pydata);

        args = PyTuple_New(4);
        PyTuple_SetItem(args, 0, PyLong_FromUnsignedLong(uid));
        PyTuple_SetItem(args, 1, pygobject_new(G_OBJECT(status)));
        PyTuple_SetItem(args, 2, PyLong_FromUnsignedLong(id));
        PyTuple_SetItem(args, 3, pydata);

        pyret = run_python_method(pyobj, "_process", args);

        Py_XDECREF(pyret);

        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau ciblé par une mise à jour.                   *
*                uid   = identifiant de la phase de traitement.               *
*                data  = données préparées par l'appelant.                    *
*                                                                             *
*  Description : Bascule l'affichage d'un panneau après mise à jour.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_updatable_panel_conclude_wrapper(GUpdatablePanel *panel, unsigned int uid, void *data)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pydata;                       /* Données au format Python    */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan de consultation       */

#define UPDATABLE_PANEL_CONCLUDE_WRAPPER PYTHON_WRAPPER_DEF                 \
(                                                                           \
    _conclude, "$self, uid, data, /",                                       \
    METH_VARARGS,                                                           \
    "Abstract method used to conclude the update process and to display"    \
    " the computed data.\n"                                                 \
    "\n"                                                                    \
    "The *uid* identifier is the same identifier provided for a previous"   \
    " call to pychrysalide.gui.panels.UpdatablePanel._setup(), and *data*"  \
    " is an optional object instance."                                      \
)

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(panel));
    pydata = (PyObject *)data;

    if (has_python_method(pyobj, "_conclude"))
    {
        Py_INCREF(pydata);

        args = PyTuple_New(2);
        PyTuple_SetItem(args, 0, PyLong_FromUnsignedLong(uid));
        PyTuple_SetItem(args, 1, pydata);

        pyret = run_python_method(pyobj, "_conclude", args);

        Py_XDECREF(pyret);

        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau ciblé par une mise à jour.                   *
*                uid   = identifiant de la phase de traitement.               *
*                data  = données en place à nettoyer avant suppression.       *
*                                                                             *
*  Description : Supprime les données dynamiques utilisées à la mise à jour.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_updatable_panel_clean_data_wrapper(const GUpdatablePanel *panel, unsigned int uid, void *data)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pydata;                       /* Données au format Python    */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan de consultation       */

#define UPDATABLE_PANEL_CLEAN_DATA_WRAPPER PYTHON_WRAPPER_DEF               \
(                                                                           \
    _clean_data, "$self, uid, data, /",                                     \
    METH_VARARGS,                                                           \
    "Abstract method used to delete dynamically generated objects for the"  \
    " panel update.\n"                                                      \
    "\n"                                                                    \
    "The *uid* identifier is the same identifier provided for a previous"   \
    " call to pychrysalide.gui.panels.UpdatablePanel._setup(), and *data*"  \
    " is an optional object instance.\n"                                    \
    "\n"                                                                    \
    "As the user *data* reference counter is decreased automatically after" \
    " this wrapper is called (if existing), there should be no need to"     \
    " define such a wrapper, except if the panel needs some kind of"        \
    " notification at the end of the update or if it still owns a reference"\
    " to this *data*."                                                      \
)

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(panel));
    pydata = (PyObject *)data;

    if (has_python_method(pyobj, "_clean_data"))
    {
        Py_INCREF(pydata);

        args = PyTuple_New(2);
        PyTuple_SetItem(args, 0, PyLong_FromUnsignedLong(uid));
        PyTuple_SetItem(args, 1, pydata);

        pyret = run_python_method(pyobj, "_clean_data", args);

        Py_XDECREF(pyret);

        Py_DECREF(args);

    }

    Py_DECREF(pydata);
    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

}



/* ---------------------------------------------------------------------------------- */
/*                           CONNEXION AVEC L'API DE PYTHON                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self = NULL car méthode statique.                            *
*                args = paramètres à transmettre à l'appel natif.             *
*                                                                             *
*  Description : Prépare et lance l'actualisation d'un panneau.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_updatable_panel_run_update(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Désignation à retourner     */
    unsigned int uid;                       /* Identifiant de mise à jour  */
    int ret;                                /* Bilan de lecture des args.  */
    GUpdatablePanel *panel;                 /* Instance à manipuler        */

#define UPDATABLE_PANEL_RUN_UPDATE_METHOD PYTHON_METHOD_DEF \
(                                                           \
    run_update, "self, uid, /",                             \
    METH_VARARGS, py_updatable_panel,                       \
    "Prepare and run an update for the panel.\n"            \
    "\n"                                                    \
    "The *uid* argument is an arbitrary integer provided"   \
    " as internal identifier for the caller."               \
)

    ret = PyArg_ParseTuple(args, "I", &uid);
    if (!ret) return NULL;

    panel = G_UPDATABLE_PANEL(pygobject_get(self));

    run_panel_update(panel, uid);

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

PyTypeObject *get_python_updatable_panel_type(void)
{
    static PyMethodDef py_updatable_panel_methods[] = {
        UPDATABLE_PANEL_SETUP_WRAPPER,
        UPDATABLE_PANEL_INTRODUCE_WRAPPER,
        UPDATABLE_PANEL_PROCESS_WRAPPER,
        UPDATABLE_PANEL_CONCLUDE_WRAPPER,
        UPDATABLE_PANEL_CLEAN_DATA_WRAPPER,
        UPDATABLE_PANEL_RUN_UPDATE_METHOD,
        { NULL }
    };

    static PyGetSetDef py_updatable_panel_getseters[] = {
        UPDATABLE_PANEL_WORKING_GROUP_ID_ATTRIB_WRAPPER,
        { NULL }
    };

    static PyTypeObject py_updatable_panel_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.gui.panels.UpdatablePanel",
        .tp_basicsize   = sizeof(PyObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = UPDATABLE_PANEL_DOC,

        .tp_methods     = py_updatable_panel_methods,
        .tp_getset      = py_updatable_panel_getseters,

    };

    return &py_updatable_panel_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.gui....UpdatablePanel'.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_updatable_panel_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'LineGenerator' */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    static GInterfaceInfo info = {          /* Paramètres d'inscription    */

        .interface_init = (GInterfaceInitFunc)py_updatable_panel_interface_init,
        .interface_finalize = NULL,
        .interface_data = NULL,

    };

    type = get_python_updatable_panel_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.gui.panels");

        dict = PyModule_GetDict(module);

        if (!register_interface_for_pygobject(dict, G_TYPE_UPDATABLE_PANEL, type, &info))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en mécanisme de mise à jour de panneau.   *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_updatable_panel(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_updatable_panel_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to updatable panel");
            break;

        case 1:
            *((GUpdatablePanel **)dst) = G_UPDATABLE_PANEL(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
