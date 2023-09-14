
/* Chrysalide - Outil d'analyse de fichiers binaires
 * item.c - prototypes pour l'équivalent Python du fichier "gui/item.c"
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


#include "item.h"


#include <malloc.h>
#include <pygobject.h>


#include <gui/item-int.h>


#include "../access.h"
#include "../core.h"
#include "../helpers.h"
#include "../analysis/binary.h"
#include "../gtkext/displaypanel.h"



#define EDITOR_ITEM_DOC                                                         \
    "EditorItem is an abstract class for all items belonging to main interface" \
    " of Chrysalide: panels, menus, aso.\n"                                     \
    "\n"                                                                        \
    "These objets do not offer functions as the pychrysalide.gui.core module"   \
    " is aimed to deal with all editor items at once. Thus such functions are"  \
    " located in this module."                                                  \
    "\n"                                                                        \
    "Several items have to be defined as class attributes in the final"         \
    " class:\n"                                                                 \
    "* *_key*: a string providing a small name used to identify the item;\n"    \
    "* *_widget*: a Gtk.Widget instance for the content to display.\n"          \
    "\n"                                                                        \
    "The following special method can be overridden:\n"                         \
    "* _change_content(self, old, new): get notified about a"                   \
    " pychrysalide.analysis.LoadedContent change.\n"                            \
    "* _change_view(self, old, new): get notified about a"                      \
    " pychrysalide.glibext.LoadedPanel change.\n"                               \
    "* _update_view(self, panel): get notified about a"                         \
    " pychrysalide.glibext.LoadedPanel change.\n"                               \
    "* _track_cursor(self, panel, cursor): get notified when the position of a" \
    " pychrysalide.glibext.LineCursor evolves in a"                             \
    " pychrysalide.glibext.LoadedPanel.\n"                                      \
    "* _focus_cursor(self, content, cursor): place the current caret to a given"\
    " pychrysalide.glibext.LineCursor inside a rendered"                        \
    " pychrysalide.analysis.LoadedContent."



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Fournit le nom interne attribué à l'élément réactif. */
static char *py_editor_item_get_key_wrapper(const GEditorItemClass *);

/* Fournit le composant GTK associé à l'élément réactif. */
static GtkWidget *py_editor_item_get_widget_wrapper(const GEditorItem *);

/* Réagit à un changement de contenu chargé en cours d'analyse. */
static void py_editor_item_change_content_wrapper(GEditorItem *, GLoadedContent *, GLoadedContent *);

/* Réagit à un changement de vue du contenu en cours d'analyse. */
static void py_editor_item_change_view_wrapper(GEditorItem *, GLoadedPanel *, GLoadedPanel *);

/* Réagit à une modification de la vue du contenu analysé. */
static void py_editor_item_update_view_wrapper(GEditorItem *, GLoadedPanel *);

/* Réagit à une modification de la vue du contenu analysé. */
static void py_editor_item_track_cursor_wrapper(GEditorItem *, GLoadedPanel *, const GLineCursor *);

/* Réagit à une modification de la vue du contenu analysé. */
static void py_editor_item_focus_cursor_wrapper(GEditorItem *, GLoadedContent *, const GLineCursor *);



/* -------------------------- FONCTIONNALITES D'UN ELEMENT -------------------------- */


/* Fournit le nom interne attribué à l'élément réactif. */
static PyObject *py_editor_item_get_key(PyObject *, void *);

/* Fournit le composant GTK associé à l'élément réactif. */
static PyObject *py_editor_item_get_widget(PyObject *, void *);



/* ---------------------------------------------------------------------------------- */
/*                          GLUE POUR CREATION DEPUIS PYTHON                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : class  = classe à initialiser.                               *
*                unused = données non utilisées ici.                          *
*                                                                             *
*  Description : Initialise la classe des éléménts pour l'interface graphique.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void py_editor_item_init_gclass(GEditorItemClass *class, gpointer unused)
{
    class->get_key = py_editor_item_get_key_wrapper;
    class->get_widget = py_editor_item_get_widget_wrapper;

    class->change_content = py_editor_item_change_content_wrapper;
    class->change_view = py_editor_item_change_view_wrapper;
    class->update_view = py_editor_item_update_view_wrapper;

    class->track_cursor = py_editor_item_track_cursor_wrapper;
    class->focus_cursor = py_editor_item_focus_cursor_wrapper;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à consulter.                                  *
*                                                                             *
*  Description : Fournit le nom interne attribué à l'élément réactif.         *
*                                                                             *
*  Retour      : Désignation (courte) de l'élément de l'éditeur.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *py_editor_item_get_key_wrapper(const GEditorItemClass *class)
{
    char *result;                           /* Désignation à retourner     */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyTypeObject *pytype;                   /* Classe Python concernée     */
    PyObject *pykey;                        /* Clef en objet Python        */
    int ret;                                /* Bilan d'une conversion      */

#define EDITOR_ITEM_KEY_ATTRIB_WRAPPER PYTHON_GETTER_WRAPPER_DEF    \
(                                                                   \
    _key,                                                           \
    "Provide the internal name to use for the editor item.\n"       \
    "\n"                                                            \
    "The value has to be a string."                                 \
)

    result = NULL;

    gstate = PyGILState_Ensure();

    pytype = pygobject_lookup_class(G_TYPE_FROM_CLASS(class));

    if (PyObject_HasAttrString((PyObject *)pytype, "_key"))
    {
        pykey = PyObject_GetAttrString((PyObject *)pytype, "_key");

        if (pykey != NULL)
        {
            ret = PyUnicode_Check(pykey);

            if (ret)
                result = strdup(PyUnicode_AsUTF8(pykey));

            Py_DECREF(pykey);

        }

    }

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = instance à consulter.                                 *
*                                                                             *
*  Description : Fournit le composant GTK associé à l'élément réactif.        *
*                                                                             *
*  Retour      : Instance de composant graphique chargé.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GtkWidget *py_editor_item_get_widget_wrapper(const GEditorItem *item)
{
    GtkWidget *result;                      /* Composant GTK à renvoyer    */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pywidget;                     /* Composant en objet Python   */
    PyObject *gtk_mod;                      /* Module Python Gtk           */
    PyObject *type;                         /* Module "GtkWidget"          */
    int ret;                                /* Bilan d'une conversion      */

#define EDITOR_ITEM_WIDGET_ATTRIB_WRAPPER PYTHON_GETTER_WRAPPER_DEF     \
(                                                                       \
    _widget,                                                            \
    "Provide the Gtk widget base involved in the editor item.\n"        \
    "\n"                                                                \
    "The value has to be a Gtk.Widget instance."                        \
)

    result = NULL;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(item));

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


/******************************************************************************
*                                                                             *
*  Paramètres  : item = instance à consulter.                                 *
*                old  = ancien contenu chargé analysé.                        *
*                new  = nouveau contenu chargé à analyser.                    *
*                                                                             *
*  Description : Réagit à un changement de contenu chargé en cours d'analyse. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_editor_item_change_content_wrapper(GEditorItem *item, GLoadedContent *old, GLoadedContent *new)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyold;                        /* Conversion ou None          */
    PyObject *pynew;                        /* Conversion ou None          */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Retour de Python            */

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(item));

    if (has_python_method(pyobj, "_change_content"))
    {
        if (old != NULL)
            pyold = pygobject_new(G_OBJECT(old));
        else
        {
            pyold = Py_None;
            Py_INCREF(pyold);
        }

        if (new != NULL)
            pynew = pygobject_new(G_OBJECT(new));
        else
        {
            pynew = Py_None;
            Py_INCREF(pynew);
        }

        args = PyTuple_New(2);
        PyTuple_SetItem(args, 0, pyold);
        PyTuple_SetItem(args, 1, pynew);

        pyret = run_python_method(pyobj, "_change_content", args);

        Py_DECREF(args);
        Py_DECREF(pyret);

    }

    PyGILState_Release(gstate);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = instance à consulter.                                 *
*                old  = ancienne vue du contenu chargé analysé.               *
*                new  = nouvelle vue du contenu chargé analysé.               *
*                                                                             *
*  Description : Réagit à un changement de vue du contenu en cours d'analyse. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_editor_item_change_view_wrapper(GEditorItem *item, GLoadedPanel *old, GLoadedPanel *new)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyold;                        /* Conversion ou None          */
    PyObject *pynew;                        /* Conversion ou None          */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Retour de Python            */

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(item));

    if (has_python_method(pyobj, "_change_view"))
    {
        if (old != NULL)
            pyold = pygobject_new(G_OBJECT(old));
        else
        {
            pyold = Py_None;
            Py_INCREF(pyold);
        }

        if (new != NULL)
            pynew = pygobject_new(G_OBJECT(new));
        else
        {
            pynew = Py_None;
            Py_INCREF(pynew);
        }

        args = PyTuple_New(2);
        PyTuple_SetItem(args, 0, pyold);
        PyTuple_SetItem(args, 1, pynew);

        pyret = run_python_method(pyobj, "_change_view", args);

        Py_DECREF(args);
        Py_DECREF(pyret);

    }

    PyGILState_Release(gstate);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item  = instance à consulter.                                *
*                panel = vue du contenu chargé analysé modifiée.              *
*                                                                             *
*  Description : Réagit à une modification de la vue du contenu analysé.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_editor_item_update_view_wrapper(GEditorItem *item, GLoadedPanel *panel)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Retour de Python            */

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(item));

    if (has_python_method(pyobj, "_update_view"))
    {
        args = PyTuple_New(1);
        PyTuple_SetItem(args, 0, pygobject_new(G_OBJECT(panel)));

        pyret = run_python_method(pyobj, "_update_view", args);

        Py_DECREF(args);
        Py_DECREF(pyret);

    }

    PyGILState_Release(gstate);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item   = instance à consulter.                               *
*                panel  = composant d'affichage parcouru.                     *
*                cursor = nouvel emplacement du curseur courant.              *
*                                                                             *
*  Description : Réagit à une modification de la vue du contenu analysé.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_editor_item_track_cursor_wrapper(GEditorItem *item, GLoadedPanel *panel, const GLineCursor *cursor)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Retour de Python            */

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(item));

    if (has_python_method(pyobj, "_track_cursor"))
    {
        args = PyTuple_New(2);
        PyTuple_SetItem(args, 0, pygobject_new(G_OBJECT(panel)));
        PyTuple_SetItem(args, 1, pygobject_new(G_OBJECT(cursor)));

        pyret = run_python_method(pyobj, "_track_cursor", args);

        Py_DECREF(args);
        Py_DECREF(pyret);

    }

    PyGILState_Release(gstate);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item    = instance à consulter.                              *
*                content = contenu contenant le curseur à représenter.        *
*                cursor  = nouvel emplacement du curseur courant.             *
*                                                                             *
*  Description : Réagit à une modification de la vue du contenu analysé.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_editor_item_focus_cursor_wrapper(GEditorItem *item, GLoadedContent *content, const GLineCursor *cursor)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Retour de Python            */

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(item));

    if (has_python_method(pyobj, "_focus_cursor"))
    {
        args = PyTuple_New(2);
        PyTuple_SetItem(args, 0, pygobject_new(G_OBJECT(content)));
        PyTuple_SetItem(args, 1, pygobject_new(G_OBJECT(cursor)));

        pyret = run_python_method(pyobj, "_focus_cursor", args);

        Py_DECREF(args);
        Py_DECREF(pyret);

    }

    PyGILState_Release(gstate);

}



/* ---------------------------------------------------------------------------------- */
/*                            FONCTIONNALITES D'UN ELEMENT                            */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le nom interne attribué à l'élément réactif.         *
*                                                                             *
*  Retour      : Désignation (courte) de l'élément de l'éditeur.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_editor_item_get_key(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GEditorItem *item;                      /* Elément à consulter         */
    char *key;                              /* Désignation humaine         */

#define EDITOR_ITEM_KEY_ATTRIB PYTHON_GET_DEF_FULL      \
(                                                       \
    key, py_editor_item,                                \
    "Internal string name given to the editor item."    \
)

    item = G_EDITOR_ITEM(pygobject_get(self));
    key = g_editor_item_class_get_key(G_EDITOR_ITEM_GET_CLASS(item));

    if (key != NULL)
    {
        result = PyUnicode_FromString(key);
        free(key);
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
*  Description : Fournit le composant GTK associé à l'élément réactif.        *
*                                                                             *
*  Retour      : Instance de composant graphique chargé.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_editor_item_get_widget(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GEditorItem *item;                      /* Elément à consulter         */
    GtkWidget *widget;                      /* Composant GTK employé       */

#define EDITOR_ITEM_WIDGET_ATTRIB PYTHON_GET_DEF_FULL   \
(                                                       \
    widget, py_editor_item,                             \
    "GTK widget base involed in the editor item."       \
)

    item = G_EDITOR_ITEM(pygobject_get(self));
    widget = g_editor_item_get_widget(item);

    if (widget != NULL)
    {
        result = pygobject_new(G_OBJECT(widget));
        g_object_unref(G_OBJECT(widget));
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
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Fournit un accès à une définition de type à diffuser.        *
*                                                                             *
*  Retour      : Définition d'objet pour Python.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyTypeObject *get_python_editor_item_type(void)
{
    static PyMethodDef py_editor_item_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_editor_item_getseters[] = {
        EDITOR_ITEM_KEY_ATTRIB_WRAPPER,
        EDITOR_ITEM_WIDGET_ATTRIB_WRAPPER,
        EDITOR_ITEM_KEY_ATTRIB,
        EDITOR_ITEM_WIDGET_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_editor_item_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.gui.EditorItem",

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = EDITOR_ITEM_DOC,

        .tp_methods     = py_editor_item_methods,
        .tp_getset      = py_editor_item_getseters,

    };

    return &py_editor_item_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.gui.EditorItem'.       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_editor_item_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'EditorItem'  */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_editor_item_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.gui");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_EDITOR_ITEM, type))
            return false;

    }

    return true;

}
