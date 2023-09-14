
/* Chrysalide - Outil d'analyse de fichiers binaires
 * constants.c - équivalent Python partiel du fichier "plugins/dex/dex_def.h"
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


#include <gui/panel.h>


#include "../helpers.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type dont le dictionnaire est à compléter.            *
*                                                                             *
*  Description : Définit les constantes pour les panneaux graphiques.         *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_panel_item_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    values = PyDict_New();

    result = add_const_to_group(values, "INVALID", PIP_INVALID);
    if (result) result = add_const_to_group(values, "SINGLETON", PIP_SINGLETON);
    if (result) result = add_const_to_group(values, "PERSISTENT_SINGLETON", PIP_PERSISTENT_SINGLETON);
    if (result) result = add_const_to_group(values, "BINARY_VIEW", PIP_BINARY_VIEW);
    if (result) result = add_const_to_group(values, "OTHER", PIP_OTHER);
    if (result) result = add_const_to_group(values, "COUNT", PIP_COUNT);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, false, "PanelItemPersonality", values,
                                            "Types of panel items.");

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en constante PanelItemPersonality.        *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_panel_item_personality(PyObject *arg, void *dst)
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
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to PanelItemPersonality");
            break;

        case 1:
            value = PyLong_AsUnsignedLong(arg);

            if (value > PIP_COUNT)
            {
                PyErr_SetString(PyExc_TypeError, "invalid value for PanelItemPersonality");
                result = 0;
            }

            else
                *((PanelItemPersonality *)dst) = value;

            break;

        default:
            assert(false);
            break;

    }

    return result;

}
