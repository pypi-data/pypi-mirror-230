
/* Chrysalide - Outil d'analyse de fichiers binaires
 * panels.c - équivalent Python du fichier "gui/core/panels.c"
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


#include "panels.h"


#include <pygobject.h>


#include <core/params.h>
#include <gui/core/panels.h>


#include "../panel.h"
#include "../../access.h"
#include "../../helpers.h"



/* Enregistre un panneau comme partie intégrante de l'éditeur. */
static PyObject *py_panels_register_panel(PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Enregistre un panneau comme partie intégrante de l'éditeur.  *
*                                                                             *
*  Retour      : None.                                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_panels_register_panel(PyObject *self, PyObject *args)
{
    GType type;                             /* Type de panneau à traiter   */
    int ret;                                /* Bilan de lecture des args.  */
    PyObject *meta;                         /* Type _GObjectMetaBase       */
    PyObject *instance;                     /* Initialisation forcée       */

#define PANELS_REGISTER_PANEL_METHOD PYTHON_METHOD_DEF          \
(                                                               \
    register_panel, "cls",                                      \
    METH_VARARGS, py_panels,                                    \
    "Register a panel class for the GUI."                       \
    "\n"                                                        \
    "The provided *cls* has to be a pychrysalide.gui.PanelItem" \
    " derived class."                                           \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_gtype, &type);
    if (!ret) return NULL;

    if (!g_type_is_a(type, G_TYPE_PANEL_ITEM))
    {
        PyErr_SetString(PyExc_TypeError, "the argument must be a class derived from pychrysalide.gui.PanelItem");
        return NULL;
    }

    /**
     * Si la classe transmise n'a jamais été utilisée pour créer une instance,
     * py_panel_item_new() n'a donc jamais été exécutée et le type dynamique
     * associé au panneau n'a jamais été initialisé par Chrysalide.
     *
     * Cette création dynamique de type est donc forcée ici.
     */

    ret = PyArg_ParseTuple(args, "O", &meta);
    if (!ret) return NULL;

    instance = PyObject_CallObject(meta, NULL);

    if (instance == NULL)
    {
        PyErr_SetString(PyExc_TypeError, "the argument must be a class derived from pychrysalide.gui.PanelItem");
        return NULL;
    }

    Py_DECREF(instance);

    /**
     * Rechargement du type, afin d'obtenir la version dynamique avec certitude.
     */

    ret = PyArg_ParseTuple(args, "O&", convert_to_gtype, &type);
    if (!ret) return NULL;

    register_panel_item(type, get_main_configuration());

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

bool populate_gui_core_module_with_panels(void)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Module à recompléter        */

    static PyMethodDef py_panels_methods[] = {
        PANELS_REGISTER_PANEL_METHOD,
        { NULL }
    };

    module = get_access_to_python_module("pychrysalide.gui.core");

    result = register_python_module_methods(module, py_panels_methods);

    return result;

}
