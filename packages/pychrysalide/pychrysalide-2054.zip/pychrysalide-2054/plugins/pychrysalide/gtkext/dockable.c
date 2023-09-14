
/* Chrysalide - Outil d'analyse de fichiers binaires
 * dockable.c - équivalent Python du fichier "gtkext/gtkdockable.c"
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


#include "dockable.h"


#include <pygobject.h>


#include <gtkext/gtkdockable-int.h>


#include "../access.h"
#include "../helpers.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Procède à l'initialisation de l'interface d'incrustation. */
static void py_dockable_interface_init(GtkDockableInterface *, gpointer *);

/* Fournit le nom court du composant encapsulable. */
static char *py_dockable_get_name_wrapper(const GtkDockable *);

/* Fournit le nom long du composant encapsulable. */
static char *py_dockable_get_desc_wrapper(const GtkDockable *);

/* Indique si le composant représenté à du contenu à fouiller. */
static bool py_dockable_can_search_wrapper(const GtkDockable *);

/* Fournit le composant graphique intégrable dans un ensemble. */
static GtkWidget *py_dockable_get_widget_wrapper(const GtkDockable *);

/* Applique un nouveau filtre sur un composant intégré. */
static void py_dockable_update_filter_wrapper(GtkDockable *, const char *);



/* ------------------------- CONNEXION AVEC L'API DE PYTHON ------------------------- */


/* Fournit le nom court du composant encapsulable. */
static PyObject *py_dockable_get_name(PyObject *, void *);

/* Fournit le nom long du composant encapsulable. */
static PyObject *py_dockable_get_desc(PyObject *, void *);

/* Indique si le composant représenté à du contenu à fouiller. */
static PyObject *py_dockable_get_can_search(PyObject *, void *);



/* ---------------------------------------------------------------------------------- */
/*                          GLUE POUR CREATION DEPUIS PYTHON                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : iface  = interface GLib à initialiser.                       *
*                unused = adresse non utilisée ici.                           *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface d'incrustation.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_dockable_interface_init(GtkDockableInterface *iface, gpointer *unused)
{

#define DOCKABLE_DOC                                                        \
    "Dockable defines an interface for all Gtk dockable widgets.\n"         \
    "\n"                                                                    \
    "A typical class declaration for a new implementation looks like:\n"    \
    "\n"                                                                    \
    "    class NewImplem(GObject.Object, Dockable):\n"                      \
    "        ...\n"                                                         \
    "\n"                                                                    \
    "\n"                                                                    \
    "Several items have to be defined as class attributes in the final"     \
    " class:\n"                                                             \
    "* *_name*: a string providing a short name for the dockable item;\n"   \
    "* *_desc*: a string for a human readable description of the dockable"  \
    " item;\n"                                                              \
    "* *_can_search*: a boolean value indicating if a search widget is"     \
    " suitable for the dockable item.\n"                                    \
    "\n"                                                                    \
    "The following methods have to be defined for new implementations:\n"   \
    "* pychrysalide.gtkext.Dockable._get_widget();\n"                       \
    "* pychrysalide.gtkext.Dockable._update_filter();\n"                    \

    iface->get_name = py_dockable_get_name_wrapper;
    iface->get_desc = py_dockable_get_desc_wrapper;
    iface->can_search = py_dockable_can_search_wrapper;

    iface->get_widget = py_dockable_get_widget_wrapper;
    iface->update_filtered = py_dockable_update_filter_wrapper;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dockable = instance GTK dont l'interface est à consulter.    *
*                                                                             *
*  Description : Fournit le nom court du composant encapsulable.              *
*                                                                             *
*  Retour      : Désignation humaine pour titre d'onglet ou de fenêtre.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *py_dockable_get_name_wrapper(const GtkDockable *dockable)
{
    char *result;                           /* Désignation à retourner     */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyname;                       /* Désignation en objet Python */
    int ret;                                /* Bilan d'une conversion      */

    result = NULL;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(dockable));

    if (PyObject_HasAttrString(pyobj, "_name"))
    {
        pyname = PyObject_GetAttrString(pyobj, "_name");

        if (pyname != NULL)
        {
            ret = PyUnicode_Check(pyname);

            if (ret)
                result = strdup(PyUnicode_AsUTF8(pyname));

            Py_DECREF(pyname);

        }

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dockable = instance GTK dont l'interface est à consulter.    *
*                                                                             *
*  Description : Fournit le nom long du composant encapsulable.               *
*                                                                             *
*  Retour      : Désignation humaine pour titre d'onglet ou de fenêtre.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *py_dockable_get_desc_wrapper(const GtkDockable *dockable)
{
    char *result;                           /* Description à retourner     */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pydesc;                       /* Description en objet Python */
    int ret;                                /* Bilan d'une conversion      */

    result = NULL;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(dockable));

    if (PyObject_HasAttrString(pyobj, "_desc"))
    {
        pydesc = PyObject_GetAttrString(pyobj, "_desc");

        if (pydesc != NULL)
        {
            ret = PyUnicode_Check(pydesc);

            if (ret)
                result = strdup(PyUnicode_AsUTF8(pydesc));

            Py_DECREF(pydesc);

        }

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dockable = instance GTK dont l'interface est à consulter.    *
*                                                                             *
*  Description : Indique si le composant représenté à du contenu à fouiller.  *
*                                                                             *
*  Retour      : Etat de la capacité.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_dockable_can_search_wrapper(const GtkDockable *dockable)
{
    bool result;                            /* Indication à retourner      */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Retour d'un appel           */
    int ret;                                /* Bilan d'une conversion      */

    result = false;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(dockable));

    if (PyObject_HasAttrString(pyobj, "_can_search"))
    {
        pyret = PyObject_GetAttrString(pyobj, "_can_search");

        if (pyret != NULL)
        {
            ret = PyBool_Check(pyret);

            if (ret)
                result = (pyret == Py_True);

            Py_DECREF(pyret);

        }

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dockable = instance GTK dont l'interface est à consulter.    *
*                                                                             *
*  Description : Fournit le composant graphique intégrable dans un ensemble.  *
*                                                                             *
*  Retour      : Composant graphique prêt à emploi.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GtkWidget *py_dockable_get_widget_wrapper(const GtkDockable *dockable)
{
    GtkWidget *result;                      /* Composant à retourner       */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */
    int ret;                                /* Bilan d'une conversion      */

#define DOCKABLE_GET_WIDGET_WRAPPER PYTHON_WRAPPER_DEF              \
(                                                                   \
    _get_widget, "$self, /",                                        \
    METH_NOARGS,                                                    \
    "Abstract method used to get the widget for a dockable item.\n" \
    "\n"                                                            \
    "The result has to be a Gtk.Widget instance."                   \
)

    result = NULL;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(dockable));

    if (has_python_method(pyobj, "_get_widget"))
    {
        pyret = run_python_method(pyobj, "_get_widget", NULL);

        if (pyret != NULL)
        {
            ret = convert_to_gtk_widget(pyret, &result);

            if (ret == 1)
                g_object_ref(G_OBJECT(result));

            Py_DECREF(pyret);

        }

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dockable = instance GTK dont l'interface est à manipuler.    *
*                filter   = nouveau filtre à appliquer.                       *
*                                                                             *
*  Description : Applique un nouveau filtre sur un composant intégré.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_dockable_update_filter_wrapper(GtkDockable *dockable, const char *filter)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan de consultation       */

#define DOCKABLE_UPDATE_FILTER_WRAPPER PYTHON_WRAPPER_DEF           \
(                                                                   \
    _update_filter, "$self, filter, /",                             \
    METH_VARARGS,                                                   \
    "Abstract method used to update the content of a dockable item" \
    " according to a given filter string."                          \
)

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(dockable));

    if (has_python_method(pyobj, "_update_filter"))
    {
        args = PyTuple_New(1);
        PyTuple_SetItem(args, 0, PyUnicode_FromString(filter));

        pyret = run_python_method(pyobj, "_update_filter", args);

        Py_XDECREF(pyret);

        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

}



/* ---------------------------------------------------------------------------------- */
/*                           CONNEXION AVEC L'API DE PYTHON                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le nom court du composant encapsulable.              *
*                                                                             *
*  Retour      : Désignation humaine pour titre d'onglet ou de fenêtre.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dockable_get_name(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    GtkDockable *dockable;                  /* Version GLib du composant   */
    char *name;                             /* Désignation du composant    */

#define DOCKABLE_NAME_ATTRIB PYTHON_GET_DEF_FULL        \
(                                                       \
    name, py_dockable,                                  \
    "Provide the short name of a dockable item, as"     \
    " a simple string."                                 \
)

    dockable = GTK_DOCKABLE(pygobject_get(self));

    name = gtk_dockable_get_name(dockable);

    if (name != NULL)
    {
        result = PyUnicode_FromString(name);
        free(name);
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
*  Description : Fournit le nom long du composant encapsulable.               *
*                                                                             *
*  Retour      : Désignation humaine pour titre d'onglet ou de fenêtre.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dockable_get_desc(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    GtkDockable *dockable;                  /* Version GLib du composant   */
    char *desc;                             /* Description du composant    */

#define DOCKABLE_DESC_ATTRIB PYTHON_GET_DEF_FULL    \
(                                                   \
    desc, py_dockable,                              \
    "Provide a human readable description of the"   \
    " dockable item, as a string."                  \
)

    dockable = GTK_DOCKABLE(pygobject_get(self));

    desc = gtk_dockable_get_desc(dockable);

    if (desc != NULL)
    {
        result = PyUnicode_FromString(desc);
        free(desc);
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
*  Description : Indique si le composant représenté à du contenu à fouiller.  *
*                                                                             *
*  Retour      : Etat de la capacité.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dockable_get_can_search(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    GtkDockable *dockable;                  /* Version GLib du composant   */
    bool status;                            /* Capacité à faire suivre     */

#define DOCKABLE_CAN_SEARCH_ATTRIB PYTHON_GET_DEF_FULL      \
(                                                           \
    can_search, py_dockable,                                \
    "Status of a search support for the dockable item."     \
)

    dockable = GTK_DOCKABLE(pygobject_get(self));

    status = gtk_dockable_can_search(dockable);

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

PyTypeObject *get_python_dockable_type(void)
{
    static PyMethodDef py_dockable_methods[] = {
        DOCKABLE_GET_WIDGET_WRAPPER,
        DOCKABLE_UPDATE_FILTER_WRAPPER,
        { NULL }
    };

    static PyGetSetDef py_dockable_getseters[] = {
        DOCKABLE_NAME_ATTRIB,
        DOCKABLE_DESC_ATTRIB,
        DOCKABLE_CAN_SEARCH_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_dockable_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.gtkext.Dockable",
        .tp_basicsize   = sizeof(PyObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = DOCKABLE_DOC,

        .tp_methods     = py_dockable_methods,
        .tp_getset      = py_dockable_getseters,

    };

    return &py_dockable_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.gtkext.Dockable'.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_dockable_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'Dockable'      */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    static GInterfaceInfo info = {          /* Paramètres d'inscription    */

        .interface_init = (GInterfaceInitFunc)py_dockable_interface_init,
        .interface_finalize = NULL,
        .interface_data = NULL,

    };

    type = get_python_dockable_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.gtkext");

        dict = PyModule_GetDict(module);

        if (!register_interface_for_pygobject(dict, GTK_TYPE_DOCKABLE, type, &info))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en élément incrustable.                   *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_dockable(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_dockable_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to dockable item");
            break;

        case 1:
            *((GtkDockable **)dst) = GTK_DOCKABLE(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
