
/* Chrysalide - Outil d'analyse de fichiers binaires
 * panel.c - équivalent Python du fichier "gui/panels/panel.c"
 *
 * Copyright (C) 2019-2020 Cyrille Bagard
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


#include "panel.h"


#include <pygobject.h>


#include <i18n.h>
#include <core/params.h>
#include <gui/panel-int.h>
#include <gui/core/panels.h>
#include <plugins/dt.h>


#include "constants.h"
#include "item.h"
#include "../access.h"
#include "../helpers.h"
#include "../glibext/named.h"
#include "../gtkext/dockable.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Accompagne la création d'une instance dérivée en Python. */
static PyObject *py_panel_item_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise la classe des panneaux graphiques de l'éditeur. */
static void py_panel_item_init_gclass(GPanelItemClass *, gpointer);

/* Fournit une indication sur la personnalité du panneau. */
static PanelItemPersonality py_panel_item_class_get_personality_wrapper(const GPanelItemClass *);

/* Fournit une indication d'accroche du panneau au démarrage. */
static bool py_panel_item_class_dock_at_startup_wrapper(const GPanelItemClass *);

/* Détermine si un panneau peut être filtré. */
static bool py_panel_item_class_can_search_wrapper(const GPanelItemClass *);

/* Indique le chemin initial de la localisation d'un panneau. */
static char *py_panel_item_class_get_path_wrapper(const GPanelItemClass *);

/* Indique la définition d'un éventuel raccourci clavier. */
static char *py_panel_item_class_get_key_bindings_wrapper(const GPanelItemClass *);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_panel_item_init(PyObject *self, PyObject *args, PyObject *kwds);



/* -------------------------- FONCTIONNALITES D'UN PANNEAU -------------------------- */


/* Place un panneau dans l'ensemble affiché. */
static PyObject *py_panel_item_dock(PyObject *, PyObject *);

/* Supprime un panneau de l'ensemble affiché. */
static PyObject *py_panel_item_undock(PyObject *, PyObject *);

/* Bascule l'affichage d'un panneau après sa mise à jour. */
static PyObject *py_panel_item_switch_to_updated_content(PyObject *, PyObject *);

/* Bascule l'affichage d'un panneau avant sa mise à jour. */
static PyObject *py_panel_item_switch_to_updating_mask(PyObject *, PyObject *);

/* Fournit une indication sur la personnalité du panneau. */
static PyObject *py_panel_item_get_personality(PyObject *, void *);

/* Fournit une indication d'accroche du panneau au démarrage. */
static PyObject *py_panel_item_get_dock_at_startup(PyObject *, void *);

/*  Définit si le composant repose sur un support de l'éditeur. */
static int py_panel_item_set_dock_at_startup(PyObject *, PyObject *, void *);

/* Détermine si un panneau peut être filtré. */
static PyObject *py_panel_item_can_search(PyObject *, void *);

/* Fournit le chemin d'accès à utiliser pour les encapsulations. */
static PyObject *py_panel_item_get_path(PyObject *, void *);

/* Définit le chemin d'accès à utiliser pour les encapsulations. */
static int py_panel_item_set_path(PyObject *, PyObject *, void *);

/* Indique la définition d'un éventuel raccourci clavier. */
static PyObject *py_panel_item_get_key_bindings(PyObject *, void *);

/* Fournit le chemin d'accès à utiliser pour les encapsulations. */
static PyObject *py_panel_item_get_named_widget(PyObject *, void *);

/* Indique si le composant repose sur un support de l'éditeur. */
static PyObject *py_panel_item_get_docked(PyObject *, void *);



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

static PyObject *py_panel_item_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

    /* Validations diverses */

    base = get_python_panel_item_type();

    if (type == base)
    {
        result = NULL;
        PyErr_Format(PyExc_RuntimeError, _("%s is an abstract class"), type->tp_name);
        goto exit;
    }

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_PANEL_ITEM, type->tp_name,
                               (GClassInitFunc)py_panel_item_init_gclass, NULL, NULL);

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

    result = PyType_GenericNew(type, args, kwds);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class  = classe à initialiser.                               *
*                unused = données non utilisées ici.                          *
*                                                                             *
*  Description : Initialise la classe des panneaux graphiques de l'éditeur.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_panel_item_init_gclass(GPanelItemClass *class, gpointer unused)
{
    py_editor_item_init_gclass(G_EDITOR_ITEM_CLASS(class), NULL);

    class->get_personality = py_panel_item_class_get_personality_wrapper;
    class->dock_at_startup = py_panel_item_class_dock_at_startup_wrapper;
    class->can_search = py_panel_item_class_can_search_wrapper;
    class->get_path = py_panel_item_class_get_path_wrapper;
    class->get_bindings = py_panel_item_class_get_key_bindings_wrapper;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à consulter.                                  *
*                                                                             *
*  Description : Fournit une indication sur la personnalité du panneau.       *
*                                                                             *
*  Retour      : Identifiant lié à la nature du panneau.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PanelItemPersonality py_panel_item_class_get_personality_wrapper(const GPanelItemClass *class)
{
    PanelItemPersonality result;            /* Personnalité à retourner    */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyTypeObject *pytype;                   /* Classe Python concernée     */
    PyObject *value;                        /* Valeur d'attribut en Python */
    int ret;                                /* Bilan d'une conversion      */

#define PANEL_ITEM_PERSONALITY_ATTRIB_WRAPPER PYTHON_GETTER_WRAPPER_DEF     \
(                                                                           \
    _personality,                                                           \
    "Abstract attribute defining the initial rule for handling panel"       \
    " creation.\n"                                                          \
    "\n"                                                                    \
    "The result has to be a pychrysalide.gui.PanelItem.PanelItemPersonality"\
    " value.\n"                                                             \
    "\n"                                                                    \
    "The default value is *PanelItem.PanelItemPersonality.SINGLETON*."      \
)

    result = PIP_SINGLETON;

    gstate = PyGILState_Ensure();

    pytype = pygobject_lookup_class(G_TYPE_FROM_CLASS(class));

    if (PyObject_HasAttrString((PyObject *)pytype, "_personality"))
    {
        value = PyObject_GetAttrString((PyObject *)pytype, "_personality");

        if (value != NULL)
        {
            ret = convert_to_panel_item_personality(value, &result);

            if (ret != 1)
            {
                PyErr_Clear();
                result = PIP_OTHER;
            }

            Py_DECREF(value);

        }

    }

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à consulter.                                  *
*                                                                             *
*  Description : Fournit une indication d'accroche du panneau au démarrage.   *
*                                                                             *
*  Retour      : true si le panneau doit être affiché de prime abord.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_panel_item_class_dock_at_startup_wrapper(const GPanelItemClass *class)
{
    bool result;                            /* Statut à retourner          */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyTypeObject *pytype;                   /* Classe Python concernée     */
    PyObject *value;                        /* Valeur d'attribut en Python */
    int ret;                                /* Bilan d'une conversion      */

#define PANEL_ITEM_DOCK_AT_STARTUP_ATTRIB_WRAPPER PYTHON_GETTER_WRAPPER_DEF \
(                                                                           \
    _dock_at_startup,                                                       \
    "Abstract attribute defining if the panel should get docked"            \
    " automatically at startup.\n"                                          \
    "\n"                                                                    \
    "The value has to be a boolean value: *True* or *False*.\n"             \
    "\n"                                                                    \
    "The default value is *True*."                                          \
)

    result = true;

    gstate = PyGILState_Ensure();

    pytype = pygobject_lookup_class(G_TYPE_FROM_CLASS(class));

    if (PyObject_HasAttrString((PyObject *)pytype, "_dock_at_startup"))
    {
        value = PyObject_GetAttrString((PyObject *)pytype, "_dock_at_startup");

        if (value != NULL)
        {
            ret = PyBool_Check(value);

            if (ret)
                result = (value == Py_True);

            Py_DECREF(value);

        }

    }

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à consulter.                                  *
*                                                                             *
*  Description : Détermine si un panneau peut être filtré.                    *
*                                                                             *
*  Retour      : Bilan de la consultation.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_panel_item_class_can_search_wrapper(const GPanelItemClass *class)
{
    bool result;                            /* Statut à retourner          */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyTypeObject *pytype;                   /* Classe Python concernée     */
    PyObject *value;                        /* Valeur d'attribut en Python */
    int ret;                                /* Bilan d'une conversion      */

#define PANEL_ITEM_CAN_SEARCH_ATTRIB_WRAPPER PYTHON_GETTER_WRAPPER_DEF  \
(                                                                       \
    _can_search,                                                        \
    "Abstract attribute defining if the panel contains content which"   \
    " can get searched.\n"                                              \
    "\n"                                                                \
    "The value has to be a boolean value: *True* or *False*.\n"         \
    "\n"                                                                \
    "The default value is *False*."                                     \
)

    result = false;

    gstate = PyGILState_Ensure();

    pytype = pygobject_lookup_class(G_TYPE_FROM_CLASS(class));

    if (PyObject_HasAttrString((PyObject *)pytype, "_can_search"))
    {
        value = PyObject_GetAttrString((PyObject *)pytype, "_can_search");

        if (value != NULL)
        {
            ret = PyBool_Check(value);

            if (ret)
                result = (value == Py_True);

            Py_DECREF(value);

        }

    }

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à consulter.                                  *
*                                                                             *
*  Description : Indique le chemin initial de la localisation d'un panneau.   *
*                                                                             *
*  Retour      : Chemin fixé associé à la position initiale.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *py_panel_item_class_get_path_wrapper(const GPanelItemClass *class)
{
    char *result;                           /* Désignation à retourner     */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyTypeObject *pytype;                   /* Classe Python concernée     */
    PyObject *value;                        /* Valeur d'attribut en Python */
    int ret;                                /* Bilan d'une conversion      */

#define PANEL_ITEM_PATH_ATTRIB_WRAPPER PYTHON_GETTER_WRAPPER_DEF    \
(                                                                   \
    _path,                                                          \
    "Abstract attribute used to provide the path to the initial"    \
    " location of the panel item.\n"                                \
    "\n"                                                            \
    "The value has to be a string."                                 \
)

    result = NULL;

    gstate = PyGILState_Ensure();

    pytype = pygobject_lookup_class(G_TYPE_FROM_CLASS(class));

    if (PyObject_HasAttrString((PyObject *)pytype, "_path"))
    {
        value = PyObject_GetAttrString((PyObject *)pytype, "_path");

        if (value != NULL)
        {
            ret = PyUnicode_Check(value);

            if (ret)
                result = strdup(PyUnicode_AsUTF8(value));

            Py_DECREF(value);

        }

    }

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à consulter.                                  *
*                                                                             *
*  Description : Indique la définition d'un éventuel raccourci clavier.       *
*                                                                             *
*  Retour      : Description d'un raccourci ou NULL si aucun de défini.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *py_panel_item_class_get_key_bindings_wrapper(const GPanelItemClass *class)
{
    char *result;                           /* Désignation à retourner     */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyTypeObject *pytype;                   /* Classe Python concernée     */
    PyObject *value;                        /* Valeur d'attribut en Python */
    int ret;                                /* Bilan d'une conversion      */

#define PANEL_ITEM_BINDINGS_ATTRIB_WRAPPER PYTHON_GETTER_WRAPPER_DEF    \
(                                                                       \
    _key_bindings,                                                      \
    "Abstract attribute used to provide an optional key bindings as"    \
    " shortcuts for the panel item.\n"                                  \
    "\n"                                                                \
    "The value has to be a string."                                     \
)

    result = NULL;

    gstate = PyGILState_Ensure();

    pytype = pygobject_lookup_class(G_TYPE_FROM_CLASS(class));

    if (PyObject_HasAttrString((PyObject *)pytype, "_key_bindings"))
    {
        value = PyObject_GetAttrString((PyObject *)pytype, "_key_bindings");

        if (value != NULL)
        {
            ret = PyUnicode_Check(value);

            if (ret)
                result = strdup(PyUnicode_AsUTF8(value));

            Py_DECREF(value);

        }

    }

    PyGILState_Release(gstate);

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

static int py_panel_item_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    GNamedWidget *widget;                   /* Composant visuel du panneau */
    int ret;                                /* Bilan de lecture des args.  */
    GPanelItem *panel;                      /* Panneau à manipuler         */

#define PANEL_ITEM_DOC                                                          \
    "PanelItem is an abstract class for panels available in the main GUI"       \
    " interface.\n"                                                             \
    "\n"                                                                        \
    "Instances can be created using the following constructor:\n"               \
    "\n"                                                                        \
    "    PanelItem(widget)"                                                     \
    "\n"                                                                        \
    "Where:\n"                                                                  \
    "* widget is an implementation of the pychrysalide.glibext.NamedWidget"     \
    " interface (see pychrysalide.gtkext.BuiltNamedWidget for a ready-to-use"   \
    " helper).\n"                                                               \
    "\n"                                                                        \
    "The PanelItem definition handles internally the supply of the *_widget*"   \
    " attribute for pychrysalide.gui.EditorItem.\n"                             \
    "\n"                                                                        \
    "Several items have to be defined as class attribute in the final class:\n" \
    "* pychrysalide.gui.PanelItem._path: path to the initial location of the"   \
    " panel item;\n"                                                            \
    "* pychrysalide.gui.PanelItem._key_bindings: optional shortcut to show the" \
    " relative panel.\n"                                                        \
    "\n"                                                                        \
    "Some extra items offer default values and thus may be defined as class"    \
    " attribute in the final class:\n"                                          \
    "* pychrysalide.gui.PanelItem._personality: rule for the panel creation;\n" \
    "* pychrysalide.gui.PanelItem._dock_at_startup: *True* if the panel should" \
    " get docked automatically at startup;\n"                                   \
    "* pychrysalide.gui.PanelItem._can_search: True if the panel contains"      \
    " content which can get searched.\n"                                        \
    "\n"                                                                        \
    "For more details about the panel path, please refer to"                    \
    " pychrysalide.gtkext.GtkDockable.\n"                                       \
    "\n"                                                                        \
    "Because panels aim to be created on demand by the Chrysalide core, calls"  \
    " to the *__init__* constructor of this abstract object must expect no"     \
    " particular argument."

    /* Récupération des paramètres */

    ret = PyArg_ParseTuple(args, "O&", convert_to_named_widget, &widget);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    panel = G_PANEL_ITEM(pygobject_get(self));

    /**
     * Si Python ne voit plus la variable représentant le panneau utilisée,
     * il va la supprimer, ce qui va supprimer le composant GTK.
     *
     * On sera donc en situation de Use-After-Free, dont les conséquences
     * arrivent très vite.
     */
    panel->widget = widget;
    g_object_ref(G_OBJECT(widget));

    return 0;

}



/* ---------------------------------------------------------------------------------- */
/*                            FONCTIONNALITES D'UN PANNEAU                            */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un binaire.                       *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Place un panneau dans l'ensemble affiché.                    *
*                                                                             *
*  Retour      : Py_None.                                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_panel_item_dock(PyObject *self, PyObject *args)
{
    GPanelItem *item;                       /* Panneau à manipuler         */

#define PANEL_ITEM_DOCK_METHOD PYTHON_METHOD_DEF    \
(                                                   \
    dock, "$self, /",                               \
    METH_NOARGS, py_panel_item,                     \
    "Display the panel item in the right place."    \
)

    item = G_PANEL_ITEM(pygobject_get(self));

    g_panel_item_dock(item);

    Py_RETURN_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un binaire.                       *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Supprime un panneau de l'ensemble affiché.                   *
*                                                                             *
*  Retour      : Py_None.                                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_panel_item_undock(PyObject *self, PyObject *args)
{
    GPanelItem *item;                       /* Panneau à manipuler         */

#define PANEL_ITEM_UNDOCK_METHOD PYTHON_METHOD_DEF  \
(                                                   \
    undock, "$self, /",                             \
    METH_NOARGS, py_panel_item,                     \
    "Hide the panel item from the main interface."  \
)

    item = G_PANEL_ITEM(pygobject_get(self));

    g_panel_item_undock(item);

    Py_RETURN_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = panneau ciblé par une mise à jour.                    *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Bascule l'affichage d'un panneau avant sa mise à jour.       *
*                                                                             *
*  Retour      : Py_None.                                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_panel_item_switch_to_updating_mask(PyObject *self, PyObject *args)
{
    GPanelItem *item;                       /* Panneau à manipuler         */

#define PANEL_ITEM_SWITCH_TO_UPDATING_MASK_METHOD PYTHON_METHOD_DEF     \
(                                                                       \
    switch_to_updating_mask, "$self, /",                                \
    METH_NOARGS, py_panel_item,                                         \
    "Switch the panel content display before its update."               \
    "\n"                                                                \
    "The *Gtk.Builder* helper linked to the panel has to define the"    \
    " following widgets:\n"                                             \
    "* 'stack': a *Gtk.Stack* instance containing the other widget;\n"  \
    "* 'content': the main *Gtk.Widget* used to show the main panel"    \
    " content;\n"                                                       \
    "* 'mask': a widget displayed during computing, like a"             \
    " *Gtk.Spinner* instance."                                          \
)

    item = G_PANEL_ITEM(pygobject_get(self));

    g_panel_item_switch_to_updating_mask(item);

    Py_RETURN_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = panneau ciblé par une mise à jour.                    *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Bascule l'affichage d'un panneau après sa mise à jour.       *
*                                                                             *
*  Retour      : Py_None.                                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_panel_item_switch_to_updated_content(PyObject *self, PyObject *args)
{
    GPanelItem *item;                       /* Panneau à manipuler         */

#define PANEL_ITEM_SWITCH_TO_UPDATED_CONTENT_METHOD PYTHON_METHOD_DEF   \
(                                                                       \
    switch_to_updated_content, "$self, /",                              \
    METH_NOARGS, py_panel_item,                                         \
    "Switch the panel content display after its update."                \
    "\n"                                                                \
    "The *Gtk.Builder* helper linked to the panel has to define the"    \
    " following widgets:\n"                                             \
    "* 'stack': a *Gtk.Stack* instance containing the other widget;\n"  \
    "* 'content': the main *Gtk.Widget* used to show the main panel"    \
    " content;\n"                                                       \
    "* 'mask': a widget displayed during computing, like a"             \
    " *Gtk.Spinner* instance."                                          \
)

    item = G_PANEL_ITEM(pygobject_get(self));

    g_panel_item_switch_to_updated_content(item);

    Py_RETURN_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit une indication sur la personnalité du panneau.       *
*                                                                             *
*  Retour      : Identifiant lié à la nature du panneau.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_panel_item_get_personality(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GPanelItem *item;                       /* Panneau à consulter         */
    PanelItemPersonality personality;       /* Valeur native à convertir   */

#define PANEL_ITEM_PERSONALITY_ATTRIB PYTHON_GET_DEF_FULL       \
(                                                               \
    personality, py_panel_item,                                 \
    "Rule for handling panel creations, as a"                   \
    " pychrysalide.gui.PanelItem.PanelItemPersonality value."   \
)

    item = G_PANEL_ITEM(pygobject_get(self));
    personality = gtk_panel_item_class_get_personality(G_PANEL_ITEM_GET_CLASS(item));

    result = cast_with_constants_group_from_type(get_python_panel_item_type(), "PanelItemPersonality", personality);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit une indication d'accroche du panneau au démarrage.   *
*                                                                             *
*  Retour      : True si le panneau doit être affiché de prime abord.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_panel_item_get_dock_at_startup(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GPanelItem *item;                       /* Panneau à consulter         */
    bool state;                             /* Indication d'ancrage        */

#define PANEL_ITEM_DOCK_AT_STARTUP_ATTRIB PYTHON_GETSET_DEF_FULL        \
(                                                                       \
    dock_at_startup, py_panel_item,                                     \
    "Tell or define if the panel should get docked automatically at"    \
    " startup.\n"                                                       \
    "\n"                                                                \
    "This state is a boolean value: *True* or *False*."                 \
)

    item = G_PANEL_ITEM(pygobject_get(self));
    state = gtk_panel_item_class_dock_at_startup(G_PANEL_ITEM_GET_CLASS(item));

    result = state ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Définit si le composant repose sur un support de l'éditeur.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_panel_item_set_dock_at_startup(PyObject *self, PyObject *value, void *closure)
{
    GPanelItem *item;                       /* Panneau à manipuler         */

    if (!PyBool_Check(value))
        return -1;

    item = G_PANEL_ITEM(pygobject_get(self));

    g_panel_item_set_dock_at_startup(item, value == Py_True);

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Détermine si un panneau peut être filtré.                    *
*                                                                             *
*  Retour      : Bilan de la consultation.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_panel_item_can_search(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GPanelItem *item;                       /* Panneau à consulter         */
    bool status;                            /* Capacité de recherche       */

#define PANEL_ITEM_CAN_SEARCH_ATTRIB PYTHON_CAN_DEF_FULL                \
(                                                                       \
    search, py_panel_item,                                              \
    "Define if the panel contains content which can get searched.\n"    \
    "\n"                                                                \
    "The result is a boolean value: *True* or *False*.\n"               \
)

    item = G_PANEL_ITEM(pygobject_get(self));
    status = gtk_panel_item_class_can_search(G_PANEL_ITEM_GET_CLASS(item));

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le chemin d'accès à utiliser pour les encapsulations.*
*                                                                             *
*  Retour      : Chemin d'accès défini.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_panel_item_get_path(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GPanelItem *item;                       /* Panneau à consulter         */
    char *path;                             /* Chemin d'accès courant      */

#define PANEL_ITEM_PATH_ATTRIB PYTHON_GETSET_DEF_FULL       \
(                                                           \
    path, py_panel_item,                                    \
    "Get or define the current path of the panel item."     \
    "\n"                                                    \
    "The path is defined as a string."                      \
)

    item = G_PANEL_ITEM(pygobject_get(self));
    path = gtk_panel_item_class_get_path(G_PANEL_ITEM_GET_CLASS(item));

    result = PyUnicode_FromString(path);

    free(path);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Définit le chemin d'accès à utiliser pour les encapsulations.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_panel_item_set_path(PyObject *self, PyObject *value, void *closure)
{
    GPanelItem *item;                       /* Panneau à manipuler         */
    const char *path;                       /* Nouveau chemin d'accès      */

    if (!PyUnicode_Check(value))
        return -1;

    item = G_PANEL_ITEM(pygobject_get(self));

    path = PyUnicode_DATA(value);

    gtk_panel_item_set_path(item, path);

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique la définition d'un éventuel raccourci clavier.       *
*                                                                             *
*  Retour      : Description d'un raccourci ou None si aucun de défini.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_panel_item_get_key_bindings(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GPanelItem *item;                       /* Panneau à consulter         */
    char *bindings;                         /* Raccourci clavier éventuel  */

#define PANEL_ITEM_KEY_BINDINGS_ATTRIB PYTHON_GET_DEF_FULL          \
(                                                                   \
    key_bindings, py_panel_item,                                    \
    "Shortcuts for displaying the panel, as a string, or *None* if" \
    " no binding is defined."                                       \
)

    item = G_PANEL_ITEM(pygobject_get(self));
    bindings = gtk_panel_item_class_get_key_bindings(G_PANEL_ITEM_GET_CLASS(item));

    if (bindings != NULL)
    {
        result = PyUnicode_FromString(bindings);
        free(bindings);
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
*  Description : Fournit le chemin d'accès à utiliser pour les encapsulations.*
*                                                                             *
*  Retour      : Chemin d'accès défini.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_panel_item_get_named_widget(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GPanelItem *item;                       /* Panneau à consulter         */
    GNamedWidget *widget;                   /* Composant nommé à transférer*/

#define PANEL_ITEM_NAMED_WIDGET_ATTRIB PYTHON_GET_DEF_FULL  \
(                                                           \
    named_widget, py_panel_item,                            \
    "Named widget as core component of the panel item.\n"   \
    "\n"                                                    \
    "The result is an implementation of the"                \
    " pychrysalide.glibext.NamedWidget interface."          \
)

    item = G_PANEL_ITEM(pygobject_get(self));
    widget = gtk_panel_item_get_named_widget(item);

    result = pygobject_new(G_OBJECT(widget));

    g_object_unref(G_OBJECT(widget));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique si le composant repose sur un support de l'éditeur.  *
*                                                                             *
*  Retour      : True si le composant est bien incrusté quelque part.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_panel_item_get_docked(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GPanelItem *item;                       /* Panneau à consulter         */
    bool docked;                            /* Statut de l'ancrage         */

#define PANEL_ITEM_DOCKED_ATTRIB PYTHON_GET_DEF_FULL    \
(                                                       \
    docked, py_panel_item,                              \
    "Dock status of the panel item.\n"                  \
    "\n"                                                \
    "The result is a boolean value: *True* or *False*." \
)

    item = G_PANEL_ITEM(pygobject_get(self));
    docked = g_panel_item_is_docked(item);

    result = docked ? Py_True : Py_False;
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

PyTypeObject *get_python_panel_item_type(void)
{
    static PyMethodDef py_panel_item_methods[] = {
        PANEL_ITEM_DOCK_METHOD,
        PANEL_ITEM_UNDOCK_METHOD,
        PANEL_ITEM_SWITCH_TO_UPDATING_MASK_METHOD,
        PANEL_ITEM_SWITCH_TO_UPDATED_CONTENT_METHOD,
        { NULL }
    };

    static PyGetSetDef py_panel_item_getseters[] = {
        PANEL_ITEM_PERSONALITY_ATTRIB_WRAPPER,
        PANEL_ITEM_DOCK_AT_STARTUP_ATTRIB_WRAPPER,
        PANEL_ITEM_CAN_SEARCH_ATTRIB_WRAPPER,
        PANEL_ITEM_PATH_ATTRIB_WRAPPER,
        PANEL_ITEM_BINDINGS_ATTRIB_WRAPPER,
        PANEL_ITEM_PERSONALITY_ATTRIB,
        PANEL_ITEM_DOCK_AT_STARTUP_ATTRIB,
        PANEL_ITEM_CAN_SEARCH_ATTRIB,
        PANEL_ITEM_PATH_ATTRIB,
        PANEL_ITEM_KEY_BINDINGS_ATTRIB,
        PANEL_ITEM_NAMED_WIDGET_ATTRIB,
        PANEL_ITEM_DOCKED_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_panel_item_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.gui.PanelItem",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = PANEL_ITEM_DOC,

        .tp_methods     = py_panel_item_methods,
        .tp_getset      = py_panel_item_getseters,

        .tp_init        = py_panel_item_init,
        .tp_new         = py_panel_item_new,

    };

    return &py_panel_item_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.gui.panels.PanelItem'. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_panel_item_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'LoadedBinary'  */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_panel_item_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.gui");

        dict = PyModule_GetDict(module);

        if (!ensure_python_editor_item_is_registered())
            return false;

        if (!ensure_python_dockable_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_PANEL_ITEM, type))
            return false;

        if (!define_panel_item_constants(type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en panneau pour GUI.                      *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_panel_item(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_panel_item_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to executable format");
            break;

        case 1:
            *((GPanelItem **)dst) = G_PANEL_ITEM(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
