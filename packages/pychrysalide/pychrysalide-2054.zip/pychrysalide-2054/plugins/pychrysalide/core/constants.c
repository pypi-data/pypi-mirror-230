
/* Chrysalide - Outil d'analyse de fichiers binaires
 * constants.c - ajout des constantes liées au coeur du programme
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


#include <core/logs.h>
#include <core/params.h>


#include "../helpers.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont le dictionnaire est à compléter.        *
*                                                                             *
*  Description : Définit les constantes pour les types de messages.           *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_core_logs_constants(PyObject *module)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    values = PyDict_New();

    result = add_const_to_group(values, "INFO", LMT_INFO);
    if (result) result = add_const_to_group(values, "PROCESS", LMT_PROCESS);
    if (result) result = add_const_to_group(values, "WARNING", LMT_WARNING);
    if (result) result = add_const_to_group(values, "BAD_BINARY", LMT_BAD_BINARY);
    if (result) result = add_const_to_group(values, "LMT_ERROR", LMT_ERROR);
    if (result) result = add_const_to_group(values, "EXT_ERROR", LMT_EXT_ERROR);
    if (result) result = add_const_to_group(values, "COUNT", LMT_COUNT);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_module(module, false, "LogMessageType", values,
                                              "Available types for log messages.");

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en constante LogMessageType.              *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_log_message_type(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */
    unsigned long value;                    /* Valeur transcrite           */

    result = PyObject_IsInstance(arg, (PyObject *)&PyLong_Type);

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to LogMessageType");
            break;

        case 1:
            value = PyLong_AsUnsignedLong(arg);

            if (value >= LMT_COUNT)
            {
                PyErr_SetString(PyExc_TypeError, "invalid value for LogMessageType");
                result = 0;
            }

            else
                *((LogMessageType *)dst) = value;

            break;

        default:
            assert(false);
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont le dictionnaire est à compléter.        *
*                                                                             *
*  Description : Définit les constantes pour les désignations de paramètres.  *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_core_params_constants(PyObject *module)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *strdict;                      /* Groupe de chaînes constantes*/

    result = create_string_constants_group_to_module(module, "MainParameterKeys",
                                                   "Keys referring to main configuration parameters.", &strdict);

    if (result) result = extend_string_constants_group(strdict, "FORMAT_NO_NAME", MPK_FORMAT_NO_NAME);
    if (result) result = extend_string_constants_group(strdict, "INTERNAL_THEME", MPK_INTERNAL_THEME);
    if (result) result = extend_string_constants_group(strdict, "TITLE_BAR", MPK_TITLE_BAR);
    if (result) result = extend_string_constants_group(strdict, "LAST_PROJECT", MPK_LAST_PROJECT);
    if (result) result = extend_string_constants_group(strdict, "SKIP_EXIT_MSG", MPK_SKIP_EXIT_MSG);
    if (result) result = extend_string_constants_group(strdict, "MAXIMIZED", MPK_MAXIMIZED);
    if (result) result = extend_string_constants_group(strdict, "ELLIPSIS_HEADER", MPK_ELLIPSIS_HEADER);
    if (result) result = extend_string_constants_group(strdict, "ELLIPSIS_TAB", MPK_ELLIPSIS_TAB);
    if (result) result = extend_string_constants_group(strdict, "WELCOME_STARTUP", MPK_WELCOME_STARTUP);
    if (result) result = extend_string_constants_group(strdict, "WELCOME_CHECK", MPK_WELCOME_CHECK);
    if (result) result = extend_string_constants_group(strdict, "LABEL_OFFSET", MPK_LABEL_OFFSET);
    if (result) result = extend_string_constants_group(strdict, "HEX_PADDING", MPK_HEX_PADDING);
    if (result) result = extend_string_constants_group(strdict, "SELECTION_LINE", MPK_SELECTION_LINE);
    if (result) result = extend_string_constants_group(strdict, "TOOLTIP_MAX_CALLS", MPK_TOOLTIP_MAX_CALLS);
    if (result) result = extend_string_constants_group(strdict, "TOOLTIP_MAX_STRINGS", MPK_TOOLTIP_MAX_STRINGS);
    if (result) result = extend_string_constants_group(strdict, "HEX_UPPER_CASE", MPK_HEX_UPPER_CASE);
    if (result) result = extend_string_constants_group(strdict, "LINK_DEFAULT", MPK_LINK_DEFAULT);
    if (result) result = extend_string_constants_group(strdict, "LINK_BRANCH_TRUE", MPK_LINK_BRANCH_TRUE);
    if (result) result = extend_string_constants_group(strdict, "LINK_BRANCH_FALSE", MPK_LINK_BRANCH_FALSE);
    if (result) result = extend_string_constants_group(strdict, "LINK_LOOP", MPK_LINK_LOOP);
    if (result) result = extend_string_constants_group(strdict, "KEYBINDINGS_EDIT", MPK_KEYBINDINGS_EDIT);
    if (result) result = extend_string_constants_group(strdict, "TMPDIR", MPK_TMPDIR);
    if (result) result = extend_string_constants_group(strdict, "AUTO_SAVE", MPK_AUTO_SAVE);

    return result;

}
