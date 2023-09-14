
/* Chrysalide - Outil d'analyse de fichiers binaires
 * displaypanel.c - prototypes pour l'équivalent Python du fichier "gtkext/gtkdisplaypanel.c"
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#include "displaypanel.h"


#include <pygobject.h>


#include <gtkext/gtkdisplaypanel.h>


#include "../access.h"
#include "../helpers.h"



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

PyTypeObject *get_python_display_panel_type(void)
{
    static PyMethodDef py_display_panel_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_display_panel_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_display_panel_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.gtkext.DisplayPanel",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = "PyChrysalide view panel.",

        .tp_methods     = py_display_panel_methods,
        .tp_getset      = py_display_panel_getseters,

    };

    static PyTypeObject *result = NULL;

    if (result == NULL)
        result = define_python_dynamic_type(&py_display_panel_type);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.gtkext.DisplayPanel'.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_display_panel_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'DisplayPanel'  */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_display_panel_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.gtkext");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, GTK_TYPE_DISPLAY_PANEL, type))
            return false;

    }

    return true;

}
