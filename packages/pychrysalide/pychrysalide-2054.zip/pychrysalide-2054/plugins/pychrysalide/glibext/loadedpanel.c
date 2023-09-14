
/* Chrysalide - Outil d'analyse de fichiers binaires
 * loadedpanel.c - équivalent Python du fichier "glibext/gloadedpanel.h"
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


#include "loadedpanel.h"


#include <assert.h>
#include <pygobject.h>


#include <i18n.h>
#include <glibext/gloadedpanel-int.h>


#include "constants.h"
#include "linecursor.h"
#include "../access.h"
#include "../helpers.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Procède à l'initialisation de l'interface de génération. */
static void py_loaded_panel_interface_init(GLoadedPanelIface *, gpointer *);

/* S'assure qu'un emplacement donné est visible à l'écran. */
static void py_loaded_panel_scroll_to_cursor_wrapper(GLoadedPanel *, const GLineCursor *, ScrollPositionTweak, bool);



/* ------------------------- CONNEXION AVEC L'API DE PYTHON ------------------------- */


/* S'assure qu'un emplacement donné est visible à l'écran. */
static PyObject *py_loaded_panel_scroll_to_cursor(PyObject *, PyObject *);



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

static void py_loaded_panel_interface_init(GLoadedPanelIface *iface, gpointer *unused)
{

#define LOADED_PANEL_DOC                                                    \
    "LoadPanel defines an interface for all panels which can be included"   \
    " inside the main graphical window.\n"                                  \
    "\n"                                                                    \
    "A typical class declaration for a new implementation looks like:\n"    \
    "\n"                                                                    \
    "    class NewImplem(GObject.Object, LoadedPanel():\n"                  \
    "        ...\n"                                                         \
    "\n"                                                                    \
    "The following methods have to be defined for new implementations:\n"   \
    "* pychrysalide.glibext.LoadedPanel._scroll_to_cursor();\n"

    iface->scroll = py_loaded_panel_scroll_to_cursor_wrapper;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel  = composant GTK à manipuler.                          *
*                cursor = emplacement à présenter à l'écran.                  *
*                tweak  = adaptation finale à effectuer.                      *
*                move   = doit-on déplacer le curseur à l'adresse indiquée ?  *
*                                                                             *
*  Description : S'assure qu'un emplacement donné est visible à l'écran.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_loaded_panel_scroll_to_cursor_wrapper(GLoadedPanel *panel, const GLineCursor *cursor, ScrollPositionTweak tweak, bool move)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *tweak_obj;                    /* Détails en versionPython    */
    PyObject *move_obj;                     /* Consigne de déplacement     */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */

#define LOADED_PANEL_SCROLL_TO_CURSOR_WRAPPER PYTHON_WRAPPER_DEF                \
(                                                                               \
    _scroll_to_cursor, "$self, cursor, tweak, move, /",                         \
    METH_VARARGS,                                                               \
    "Abstract method used to ensure a given address is displayed in the view"   \
    " panel.\n"                                                                 \
    "\n"                                                                        \
    "The *cursor* argument is a pychrysalide.glibext.LineCursor location. The"  \
    " *tweak* parameter defines the final adjustment for new location and the"  \
    " *move* order is a boolean value which implies a scroll operation if"      \
    " requiered."                                                               \
)

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(panel));

    if (has_python_method(pyobj, "_scroll_to_cursor"))
    {
        tweak_obj = cast_with_constants_group_from_type(get_python_loaded_panel_type(),
                                                        "ScrollPositionTweak", tweak);

        move_obj = (move ? Py_True : Py_False);
        Py_INCREF(move_obj);

        args = PyTuple_New(3);
        PyTuple_SetItem(args, 0, pygobject_new(G_OBJECT(cursor)));
        PyTuple_SetItem(args, 1, tweak_obj);
        PyTuple_SetItem(args, 2, move_obj);

        pyret = run_python_method(pyobj, "_scroll_to_cursor", args);

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
*  Paramètres  : self = classe représentant un tampon de code.                *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : S'assure qu'un emplacement donné est visible à l'écran.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_loaded_panel_scroll_to_cursor(PyObject *self, PyObject *args)
{
    GLineCursor *cursor;                    /* Emplacement à cibler        */
    ScrollPositionTweak tweak;              /* Adapation à effectuer       */
    int move;                               /* Déplacement à l'écran ?     */
    int ret;                                /* Bilan de lecture des args.  */
    GLoadedPanel *panel;                    /* Panneau à manipuler         */

#define LOADED_PANEL_SCROLL_TO_CURSOR_METHOD PYTHON_METHOD_DEF                  \
(                                                                               \
    scroll_to_cursor, "$self, cursor, tweak, move, /",                          \
    METH_VARARGS, py_loaded_panel,                                              \
    "Ensure a given address is displayed in the view panel.\n"                  \
    "\n"                                                                        \
    "The *cursor* argument is a pychrysalide.glibext.LineCursor location. The"  \
    " *tweak* parameter defines the final adjustment for new location and the"  \
    " *move* order is a boolean value which implies a scroll operation if"      \
    " requiered."                                                               \
)

    ret = PyArg_ParseTuple(args, "O&O&p", convert_to_line_cursor, &cursor,
                           convert_to_scroll_position_tweak, &tweak, &move);
    if (!ret) return NULL;

    panel = G_LOADED_PANEL(pygobject_get(self));

    g_loaded_panel_scroll_to_cursor(panel, cursor, tweak, move);

    Py_RETURN_NONE;

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

PyTypeObject *get_python_loaded_panel_type(void)
{
    static PyMethodDef py_loaded_panel_methods[] = {
        LOADED_PANEL_SCROLL_TO_CURSOR_WRAPPER,
        LOADED_PANEL_SCROLL_TO_CURSOR_METHOD,
        { NULL }
    };

    static PyGetSetDef py_loaded_panel_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_loaded_panel_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.glibext.LoadedPanel",
        .tp_basicsize   = sizeof(PyObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = LOADED_PANEL_DOC,

        .tp_methods     = py_loaded_panel_methods,
        .tp_getset      = py_loaded_panel_getseters,

    };

    return &py_loaded_panel_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.glibext.LoadedPanel'.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_loaded_panel_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'LineGenerator' */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    static GInterfaceInfo info = {          /* Paramètres d'inscription    */

        .interface_init = (GInterfaceInitFunc)py_loaded_panel_interface_init,
        .interface_finalize = NULL,
        .interface_data = NULL,

    };

    type = get_python_loaded_panel_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.glibext");

        dict = PyModule_GetDict(module);

        if (!register_interface_for_pygobject(dict, G_TYPE_LOADED_PANEL, type, &info))
            return false;

        if (!define_loaded_panel_constants(type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en panneau de contenu chargé.             *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_loaded_panel(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_loaded_panel_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to loaded panel");
            break;

        case 1:
            *((GLoadedPanel **)dst) = G_LOADED_PANEL(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
