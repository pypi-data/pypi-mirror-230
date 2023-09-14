
/* Chrysalide - Outil d'analyse de fichiers binaires
 * global.c - équivalent Python du fichier "gui/core/global.c"
 *
 * Copyright (C) 2019 Cyrille Bagard
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


#include <assert.h>
#include <pygobject.h>


#include <gui/core/global.h>


#include "../../access.h"
#include "../../helpers.h"



/* Fournit l'adresse du constructeur principal de l'éditeur. */
static PyObject *py_global_get_editor_builder(PyObject *, PyObject *);

/* Fournit l'adresse de la fenêtre principale de l'éditeur. */
static PyObject *py_global_get_editor_window(PyObject *, PyObject *);

/* Fournit le contenu actif en cours d'étude. */
static PyObject *py_global_get_current_content(PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = non utilisé ici.                                      *
*                                                                             *
*  Description : Fournit l'adresse du constructeur principal de l'éditeur.    *
*                                                                             *
*  Retour      : Constructeur principal référencé.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_global_get_editor_builder(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance Python à retourner */
    GtkBuilder *builder;                    /* Constructeur principal      */

#define GLOBAL_GET_EDITOR_BUILDER_METHOD PYTHON_METHOD_DEF          \
(                                                                   \
    get_editor_builder, "",                                         \
    METH_NOARGS, py_global,                                         \
    "Provide access to the Chrysalide main window builder.\n"       \
    "\n"                                                            \
    "The result should be an instance of Gtk.Builder, never None."  \
)

    builder = get_editor_builder();

    if (builder != NULL)
    {
        result = pygobject_new(G_OBJECT(builder));
        g_object_unref(G_OBJECT(builder));
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
*  Description : Fournit l'adresse de la fenêtre principale de l'éditeur.     *
*                                                                             *
*  Retour      : Fenêtre principale référencée.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_global_get_editor_window(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance Python à retourner */
    GtkWindow *editor;                      /* Fenêtre principale récupérée*/

#define GLOBAL_GET_EDITOR_WINDOW_METHOD PYTHON_METHOD_DEF                               \
(                                                                                       \
    get_editor_window, "",                                                              \
    METH_NOARGS, py_global,                                                             \
    "Provide access to the Chrysalide main window, referenced as the editor window."    \
)

    editor = get_editor_window();

    if (editor != NULL)
    {
        result = pygobject_new(G_OBJECT(editor));
        g_object_unref(G_OBJECT(editor));
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
*  Description : Fournit le contenu actif en cours d'étude.                   *
*                                                                             *
*  Retour      : Instance courante de contenu étudié ou None.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_global_get_current_content(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance Python à retourner */
    GLoadedContent *content;                /* Contenu courant récupéré    */

#define GLOBAL_GET_CURRENT_CONTENT_METHOD PYTHON_METHOD_DEF     \
(                                                               \
    get_current_content, "",                                    \
    METH_NOARGS, py_global,                                     \
    "Provide access to the active loaded content, as a"         \
    " pychrysalide.analysis.LoadedContent instance, or None"    \
    " if no current content is loaded."                         \
)

    content = get_current_content();

    if (content != NULL)
    {
        result = pygobject_new(G_OBJECT(content));
        g_object_unref(G_OBJECT(content));
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
*  Description : Définit une extension du module 'core' à compléter.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool populate_gui_core_module_with_global(void)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Module à recompléter        */

    static PyMethodDef py_global_methods[] = {
        GLOBAL_GET_EDITOR_BUILDER_METHOD,
        GLOBAL_GET_EDITOR_WINDOW_METHOD,
        GLOBAL_GET_CURRENT_CONTENT_METHOD,
        { NULL }

    };

    module = get_access_to_python_module("pychrysalide.gui.core");

    result = register_python_module_methods(module, py_global_methods);

    return result;

}
