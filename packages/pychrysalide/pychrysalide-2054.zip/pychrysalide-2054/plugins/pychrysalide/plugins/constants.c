
/* Chrysalide - Outil d'analyse de fichiers binaires
 * constants.c - ajout des constantes principales
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


#include "constants.h"


#include <plugins/plugin-def.h>


#include "../helpers.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type dont le dictionnaire est à compléter.            *
*                                                                             *
*  Description : Définit les constantes relatives aux greffons Python.        *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_plugin_module_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    result = true;

    values = PyDict_New();

    if (result) result = add_const_to_group(values, "BASIC_NONE", PGA_BASIC_NONE);
    if (result) result = add_const_to_group(values, "PLUGIN_INIT", PGA_PLUGIN_INIT);
    if (result) result = add_const_to_group(values, "PLUGIN_LOADED", PGA_PLUGIN_LOADED);
    if (result) result = add_const_to_group(values, "PLUGIN_EXIT", PGA_PLUGIN_EXIT);
    if (result) result = add_const_to_group(values, "NATIVE_PLUGINS_LOADED", PGA_NATIVE_PLUGINS_LOADED);
    if (result) result = add_const_to_group(values, "ALL_PLUGINS_LOADED", PGA_ALL_PLUGINS_LOADED);
    if (result) result = add_const_to_group(values, "TYPE_BUILDING", PGA_TYPE_BUILDING);
    if (result) result = add_const_to_group(values, "GUI_THEME", PGA_GUI_THEME);
    if (result) result = add_const_to_group(values, "PANEL_CREATION", PGA_PANEL_CREATION);
    if (result) result = add_const_to_group(values, "PANEL_DOCKING", PGA_PANEL_DOCKING);
    if (result) result = add_const_to_group(values, "CONTENT_EXPLORER", PGA_CONTENT_EXPLORER);
    if (result) result = add_const_to_group(values, "CONTENT_RESOLVER", PGA_CONTENT_RESOLVER);
    if (result) result = add_const_to_group(values, "CONTENT_ANALYZED", PGA_CONTENT_ANALYZED);
    if (result) result = add_const_to_group(values, "FORMAT_ANALYSIS_STARTED", PGA_FORMAT_ANALYSIS_STARTED);
    if (result) result = add_const_to_group(values, "FORMAT_PRELOAD", PGA_FORMAT_PRELOAD);
    if (result) result = add_const_to_group(values, "FORMAT_ATTACH_DEBUG", PGA_FORMAT_ATTACH_DEBUG);
    if (result) result = add_const_to_group(values, "FORMAT_ANALYSIS_ENDED", PGA_FORMAT_ANALYSIS_ENDED);
    if (result) result = add_const_to_group(values, "FORMAT_POST_ANALYSIS_STARTED", PGA_FORMAT_POST_ANALYSIS_STARTED);
    if (result) result = add_const_to_group(values, "FORMAT_POST_ANALYSIS_ENDED", PGA_FORMAT_POST_ANALYSIS_ENDED);
    if (result) result = add_const_to_group(values, "DISASSEMBLY_STARTED", PGA_DISASSEMBLY_STARTED);
    if (result) result = add_const_to_group(values, "DISASSEMBLY_RAW", PGA_DISASSEMBLY_RAW);
    if (result) result = add_const_to_group(values, "DISASSEMBLY_HOOKED_LINK", PGA_DISASSEMBLY_HOOKED_LINK);
    if (result) result = add_const_to_group(values, "DISASSEMBLY_HOOKED_POST", PGA_DISASSEMBLY_HOOKED_POST);
    if (result) result = add_const_to_group(values, "DISASSEMBLY_LIMITED", PGA_DISASSEMBLY_LIMITED);
    if (result) result = add_const_to_group(values, "DISASSEMBLY_LOOPS", PGA_DISASSEMBLY_LOOPS);
    if (result) result = add_const_to_group(values, "DISASSEMBLY_LINKED", PGA_DISASSEMBLY_LINKED);
    if (result) result = add_const_to_group(values, "DISASSEMBLY_GROUPED", PGA_DISASSEMBLY_GROUPED);
    if (result) result = add_const_to_group(values, "DISASSEMBLY_RANKED", PGA_DISASSEMBLY_RANKED);
    if (result) result = add_const_to_group(values, "DISASSEMBLY_ENDED", PGA_DISASSEMBLY_ENDED);
    if (result) result = add_const_to_group(values, "DETECTION_OBFUSCATORS", PGA_DETECTION_OBFUSCATORS);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, false, "PluginAction", values,
                                            "Features with which plugins can extend the core of Chrysalide.");

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en constante PluginAction.                *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_plugin_action(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */
    unsigned long value;                    /* Valeur récupérée            */

    result = PyObject_IsInstance(arg, (PyObject *)&PyLong_Type);

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to PluginAction");
            break;

        case 1:
            value = PyLong_AsUnsignedLong(arg);
            *((PluginAction *)dst) = value;
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
