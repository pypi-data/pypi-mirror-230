
/* Chrysalide - Outil d'analyse de fichiers binaires
 * named.c - équivalent Python du fichier "glibext/named.h"
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


#include "named.h"


#include <pygobject.h>
#include <string.h>


#include <glibext/named-int.h>


#include "../access.h"
#include "../helpers.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Procède à l'initialisation de l'interface de génération. */
static void py_named_widget_interface_init(GNamedWidgetIface *, gpointer *);

/* Fournit le désignation associée à un composant nommé. */
static char *py_named_widget_get_name_wrapper(const GNamedWidget *, bool);

/* Fournit le composant associé à un composant nommé. */
static GtkWidget *py_named_widget_get_widget_wrapper(const GNamedWidget *);



/* ------------------------- CONNEXION AVEC L'API DE PYTHON ------------------------- */


/* Fournit le désignation associée à un composant nommé. */
static PyObject *py_named_widget_get_name(PyObject *, void *);

/* Fournit le désignation associée à un composant nommé. */
static PyObject *py_named_widget_get_long_name(PyObject *, void *);

/* Fournit le composant associé à un composant nommé. */
static PyObject *py_named_widget_get_widget(PyObject *, void *);



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

static void py_named_widget_interface_init(GNamedWidgetIface *iface, gpointer *unused)
{

#define NAMED_WIDGET_DOC                                                    \
    "NamedWidget is an interface linking GTK widget to short and long"      \
    " descriptions. Such interface is mainly used when inserting widgets"   \
    " into the main window as panels.\n"                                    \
    "\n"                                                                    \
    "A typical class declaration for a new implementation looks like:\n"    \
    "\n"                                                                    \
    "    class NewImplem(GObject.Object, NamedWidget):\n"                   \
    "        ...\n"                                                         \
    "\n"                                                                    \
    "Several items have to be defined as class attributes in the final"     \
    " class:\n"                                                             \
    "* pychrysalide.glibext.NamedWidget._name;\n"                           \
    "* pychrysalide.glibext.NamedWidget._long_name;\n"                      \
    "* pychrysalide.glibext.NamedWidget._widget;\n"

    iface->get_name = py_named_widget_get_name_wrapper;
    iface->get_widget = py_named_widget_get_widget_wrapper;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant nommé à consulter.                        *
*                lname  = précise s'il s'agit d'une version longue ou non.    *
*                                                                             *
*  Description : Fournit le désignation associée à un composant nommé.        *
*                                                                             *
*  Retour      : Description courante.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *py_named_widget_get_name_wrapper(const GNamedWidget *widget, bool lname)
{
    char *result;                           /* Désignation à retourner     */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyname;                       /* Nom en objet Python         */
    int ret;                                /* Bilan d'une conversion      */

#define NAMED_WIDGET_NAME_ATTRIB_WRAPPER PYTHON_GETTER_WRAPPER_DEF      \
(                                                                       \
    _name,                                                              \
    "Provide the short name used to describe a named widget.\n"         \
    "\n"                                                                \
    "The result has to be a string."                                    \
)

#define NAMED_WIDGET_LONG_NAME_ATTRIB_WRAPPER PYTHON_GETTER_WRAPPER_DEF \
(                                                                       \
    _long_name,                                                         \
    "Provide the long name used to describe a named widget.\n"          \
    "\n"                                                                \
    "The result has to be a string."                                    \
)

    result = NULL;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(widget));

    if (PyObject_HasAttrString(pyobj, lname ? "_name" : "_long_name"))
    {
        pyname = PyObject_GetAttrString(pyobj, lname ? "_name" : "_long_name");

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
*  Paramètres  : widget = composant nommé à consulter.                        *
*                                                                             *
*  Description : Fournit le composant associé à un composant nommé.           *
*                                                                             *
*  Retour      : Composant graphique GTK.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GtkWidget *py_named_widget_get_widget_wrapper(const GNamedWidget *widget)
{
    GtkWidget *result;                      /* Composant GTK à renvoyer    */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pywidget;                     /* Composant en objet Python   */
    PyObject *gtk_mod;                      /* Module Python Gtk           */
    PyObject *type;                         /* Module "GtkWidget"          */
    int ret;                                /* Bilan d'une conversion      */

#define NAMED_WIDGET_WIDGET_ATTRIB_WRAPPER PYTHON_GETTER_WRAPPER_DEF    \
(                                                                       \
    _widget,                                                            \
    "Provide the internal widget usable for a named widget.\n"          \
    "\n"                                                                \
    "The result has to be a GTK.Widget instance."                       \
)

    result = NULL;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(widget));

    if (PyObject_HasAttrString(pyobj, "_widget"))
    {
        pywidget = PyObject_GetAttrString(pyobj, "_widget");

        if (pywidget != NULL)
        {
            gtk_mod = PyImport_ImportModule("gi.repository.Gtk");

            if (gtk_mod == NULL)
            {
                PyErr_SetString(PyExc_TypeError, "unable to find the Gtk Python module");
                goto exit;
            }

            type = PyObject_GetAttrString(gtk_mod, "Widget");

            Py_DECREF(gtk_mod);

            ret = PyObject_TypeCheck(pywidget, (PyTypeObject *)type);

            Py_DECREF(type);

            if (ret)
                result = GTK_WIDGET(pygobject_get(pywidget));

            Py_DECREF(pywidget);

        }

    }

 exit:

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                           CONNEXION AVEC L'API DE PYTHON                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = classe représentant un composant nommé à manipuler.*
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le désignation associée à un composant nommé.        *
*                                                                             *
*  Retour      : Description courante.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_named_widget_get_name(PyObject *self, void *closure)
{
    PyObject *result;                       /* Décompte à retourner        */
    GNamedWidget *widget;                   /* Version native              */
    char *name;                             /* Désignation à convertir     */

#define NAMED_WIDGET_NAME_ATTRIB PYTHON_GET_DEF_FULL    \
(                                                       \
    name, py_named_widget,                              \
    "Short name used to describe a named widget.\n"     \
    "\n"                                                \
    "The result has to be a string."                    \
)

    widget = G_NAMED_WIDGET(pygobject_get(self));

    name = g_named_widget_get_name(widget, false);

    if (name == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }
    else
    {
        result = PyUnicode_FromString(name);
        free(name);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = classe représentant un composant nommé à manipuler.*
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le désignation associée à un composant nommé.        *
*                                                                             *
*  Retour      : Description courante.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_named_widget_get_long_name(PyObject *self, void *closure)
{
    PyObject *result;                       /* Décompte à retourner        */
    GNamedWidget *widget;                   /* Version native              */
    char *name;                             /* Désignation à convertir     */

#define NAMED_WIDGET_LONG_NAME_ATTRIB PYTHON_GET_DEF_FULL   \
(                                                           \
    long_name, py_named_widget,                             \
    "Long name used to describe a named widget.\n"          \
    "\n"                                                    \
    "The result has to be a string."                        \
)

    widget = G_NAMED_WIDGET(pygobject_get(self));

    name = g_named_widget_get_name(widget, true);

    if (name == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }
    else
    {
        result = PyUnicode_FromString(name);
        free(name);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = classe représentant un composant nommé à manipuler.*
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le composant associé à un composant nommé.           *
*                                                                             *
*  Retour      : Composant graphique GTK.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_named_widget_get_widget(PyObject *self, void *closure)
{
    PyObject *result;                       /* Décompte à retourner        */
    GNamedWidget *widget;                   /* Version native              */
    GtkWidget *instance;                    /* Composant interne natif     */

#define NAMED_WIDGET_WIDGET_ATTRIB PYTHON_GET_DEF_FULL  \
(                                                       \
    widget, py_named_widget,                            \
    "Internal widget usable for a named widget.\n"      \
    "\n"                                                \
    "The result has to be a GTK *widget*."              \
)

    widget = G_NAMED_WIDGET(pygobject_get(self));

    instance = g_named_widget_get_widget(widget);

    result = pygobject_new(G_OBJECT(instance));

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

PyTypeObject *get_python_named_widget_type(void)
{
    static PyMethodDef py_named_widget_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_named_widget_getseters[] = {
        NAMED_WIDGET_NAME_ATTRIB_WRAPPER,
        NAMED_WIDGET_LONG_NAME_ATTRIB_WRAPPER,
        NAMED_WIDGET_WIDGET_ATTRIB_WRAPPER,
        NAMED_WIDGET_NAME_ATTRIB,
        NAMED_WIDGET_LONG_NAME_ATTRIB,
        NAMED_WIDGET_WIDGET_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_named_widget_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.glibext.NamedWidget",
        .tp_basicsize   = sizeof(PyObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = NAMED_WIDGET_DOC,

        .tp_methods     = py_named_widget_methods,
        .tp_getset      = py_named_widget_getseters,

    };

    return &py_named_widget_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.glibext.NamedWidget'.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_named_widget_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'NamedWidget'   */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    static GInterfaceInfo info = {          /* Paramètres d'inscription    */

        .interface_init = (GInterfaceInitFunc)py_named_widget_interface_init,
        .interface_finalize = NULL,
        .interface_data = NULL,

    };

    type = get_python_named_widget_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.glibext");

        dict = PyModule_GetDict(module);

        if (!register_interface_for_pygobject(dict, G_TYPE_NAMED_WIDGET, type, &info))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en composant nommé.                       *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_named_widget(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_named_widget_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to named widget");
            break;

        case 1:
            *((GNamedWidget **)dst) = G_NAMED_WIDGET(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
