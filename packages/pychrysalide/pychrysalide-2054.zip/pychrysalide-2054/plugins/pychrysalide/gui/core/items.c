
/* Chrysalide - Outil d'analyse de fichiers binaires
 * items.c - équivalent Python du fichier "gui/core/items.c"
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


#include "items.h"


#include <pygobject.h>


#include <gui/core/items.h>


#include "../../access.h"
#include "../../helpers.h"
#include "../../analysis/loaded.h"
#include "../../analysis/project.h"
#include "../../glibext/loadedpanel.h"



/* Lance une actualisation du fait d'un changement de contenu. */
static PyObject *py_items_change_current_content(PyObject *, PyObject *);

/* Lance une actualisation du fait d'un changement de vue. */
static PyObject *py_items_change_current_view(PyObject *, PyObject *);

/* Lance une actualisation du fait d'un changement de contenu. */
static PyObject *py_items_update_current_view(PyObject *, PyObject *);

/* Lance une actualisation relative à l'étendue du projet. */
static PyObject *py_items_update_project(PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un binaire.                       *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Lance une actualisation du fait d'un changement de contenu.  *
*                                                                             *
*  Retour      : None.                                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_items_find_editor_item_by_type(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Trouvaille à retourner      */
    GType type;                             /* Type d'élément à traiter    */
    int ret;                                /* Bilan de lecture des args.  */
    GEditorItem *found;                     /* Instance retrouvée ou NULL  */

#define ITEMS_FIND_EDITOR_ITEM_BY_TYPE_METHOD PYTHON_METHOD_DEF     \
(                                                                   \
    find_editor_item_by_type, "cls",                                \
    METH_VARARGS, py_items,                                         \
    "Find the editor component belonging to a given class."         \
    "\n"                                                            \
    "The provided *cls* has to be an pychrysalide.gui.EditorItem"   \
    " derived class."                                               \
    "\n"                                                            \
    "The result is an pychrysalide.gui.EditorItem instance or None" \
    " if no component is found for the given key."                  \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_gtype, &type);
    if (!ret) return NULL;

    if (!g_type_is_a(type, G_TYPE_EDITOR_ITEM))
    {
        PyErr_SetString(PyExc_TypeError, "the argument must be a class derived from pychrysalide.gui.EditorItem");
        return NULL;
    }

    found = find_editor_item_by_type(type);

    if (found == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }
    else
    {
        result = pygobject_new(G_OBJECT(found));
        g_object_ref(G_OBJECT(found));
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un binaire.                       *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Lance une actualisation du fait d'un changement de contenu.  *
*                                                                             *
*  Retour      : None.                                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_items_change_current_content(PyObject *self, PyObject *args)
{
    GLoadedContent *content;                /* Instance GLib correspondante*/
    int ret;                                /* Bilan de lecture des args.  */

#define ITEMS_CHANGE_CURRENT_CONTENT_METHOD PYTHON_METHOD_DEF           \
(                                                                       \
    change_current_content, "content",                                  \
    METH_VARARGS, py_items,                                             \
    "Change the current loaded content in the GUI."                     \
    "\n"                                                                \
    "The new content has to be a pychrysalide.analysis.LoadedContent"   \
    " instance."                                                        \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_loaded_content, &content);
    if (!ret) return NULL;

    change_editor_items_current_content(content);

    Py_RETURN_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un binaire.                       *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Lance une actualisation du fait d'un changement de vue.      *
*                                                                             *
*  Retour      : None.                                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_items_change_current_view(PyObject *self, PyObject *args)
{
    GLoadedPanel *panel;                    /* Instance GLib correspondante*/
    int ret;                                /* Bilan de lecture des args.  */

#define ITEMS_CHANGE_CURRENT_VIEW_METHOD PYTHON_METHOD_DEF              \
(                                                                       \
    change_current_view, "view",                                        \
    METH_VARARGS, py_items,                                             \
    "Change the current view in the GUI."                               \
    "\n"                                                                \
    "The new content has to be a pychrysalide.glibext.LoadedPanel"      \
    " instance."                                                        \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_loaded_panel, &panel);
    if (!ret) return NULL;

    change_editor_items_current_view(panel);

    Py_RETURN_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un binaire.                       *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Lance une actualisation du fait d'un changement de contenu.  *
*                                                                             *
*  Retour      : None.                                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_items_update_current_view(PyObject *self, PyObject *args)
{
    GLoadedPanel *panel;                    /* Instance GLib correspondante*/
    int ret;                                /* Bilan de lecture des args.  */

#define ITEMS_UPDATE_CURRENT_VIEW_METHOD PYTHON_METHOD_DEF          \
(                                                                   \
    update_current_view, "view",                                    \
    METH_VARARGS, py_items,                                         \
    "Update the current view in the GUI."                           \
    "\n"                                                            \
    "The new view has to be a pychrysalide.glibext.LoadedPanel"     \
    " instance."                                                    \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_loaded_panel, &panel);
    if (!ret) return NULL;

    update_editor_items_current_view(panel);

    Py_RETURN_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un binaire.                       *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Lance une actualisation relative à l'étendue du projet.      *
*                                                                             *
*  Retour      : None.                                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_items_update_project(PyObject *self, PyObject *args)
{
    GStudyProject *project;                 /* Instance GLib correspondante*/
    int ret;                                /* Bilan de lecture des args.  */

#define ITEMS_UPDATE_PROJECT_METHOD PYTHON_METHOD_DEF               \
(                                                                   \
    update_project, "project",                                      \
    METH_VARARGS, py_items,                                         \
    "Update the GUI for the current project."                       \
    "\n"                                                            \
    "The provided project has to be an instance (or a subclass)"    \
    " of pychrysalide.analysis.StudyProject."                       \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_study_project, &project);
    if (!ret) return NULL;

    update_project_area(project);

    Py_RETURN_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Définit une extension du module 'gui.core' à compléter.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool populate_gui_core_module_with_items(void)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Module à recompléter        */

    static PyMethodDef py_items_methods[] = {
        ITEMS_FIND_EDITOR_ITEM_BY_TYPE_METHOD,
        ITEMS_CHANGE_CURRENT_CONTENT_METHOD,
        ITEMS_CHANGE_CURRENT_VIEW_METHOD,
        ITEMS_UPDATE_CURRENT_VIEW_METHOD,
        ITEMS_UPDATE_PROJECT_METHOD,
        { NULL }
    };

    module = get_access_to_python_module("pychrysalide.gui.core");

    result = register_python_module_methods(module, py_items_methods);

    return result;

}
