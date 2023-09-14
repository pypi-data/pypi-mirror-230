
/* Chrysalide - Outil d'analyse de fichiers binaires
 * menubar.c - prototypes pour l'équivalent Python du fichier "gui/menubar.c"
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


#include "menubar.h"


#include <malloc.h>
#include <pygobject.h>


#include <gui/menubar.h>


#include "item.h"
#include "../access.h"
#include "../helpers.h"



#define MENU_BAR_DOC                                                            \
    "MenuBar is an object providing interactions with the main bar of menus.\n" \
    "\n"                                                                        \
    "This object is built by the GUI core of Chrysalide and is not aimed to"    \
    " get created from Python bindings. This singleton is thus a"               \
    " pychrysalide.gui.EditorItem instance which can be retrieved with"         \
    " 'menubar' as key."


/* Fournit le constructeur associé à la barre de menus. */
static PyObject *py_menu_bar_get_builder(PyObject *self, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le constructeur associé à la barre de menus.         *
*                                                                             *
*  Retour      : Instance du constructeur (principal) associé à la barre.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_menu_bar_get_builder(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GMenuBar *bar;                          /* Elément à consulter         */
    GtkBuilder *builder;                    /* Instance GTK visée          */

#define MENU_BAR_BUILDER_ATTRIB PYTHON_GET_DEF_FULL                     \
(                                                                       \
    builder, py_menu_bar,                                               \
    "Builder linked to the main menubar, as a Gtk.Builder instance."    \
)

    bar = G_MENU_BAR(pygobject_get(self));

    builder = g_menu_bar_get_builder(bar);

    result = pygobject_new(G_OBJECT(builder));
    g_object_unref(G_OBJECT(builder));

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

PyTypeObject *get_python_menu_bar_type(void)
{
    static PyMethodDef py_menu_bar_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_menu_bar_getseters[] = {
        MENU_BAR_BUILDER_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_menu_bar_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.gui.MenuBar",

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = MENU_BAR_DOC,

        .tp_methods     = py_menu_bar_methods,
        .tp_getset      = py_menu_bar_getseters,

        .tp_new         = no_python_constructor_allowed,

    };

    return &py_menu_bar_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.gui.MenuBar'.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_menu_bar_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'MenuBar'       */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_menu_bar_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.gui");

        dict = PyModule_GetDict(module);

        if (!ensure_python_editor_item_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_MENU_BAR, type))
            return false;

    }

    return true;

}
