
/* Chrysalide - Outil d'analyse de fichiers binaires
 * constants.c - ajout des constantes de base pour les instructions
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


#include <arch/instructions/raw.h>
#include <arch/instructions/undefined.h>


#include "../../helpers.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type dont le dictionnaire est à compléter.            *
*                                                                             *
*  Description : Définit les constantes relatives aux instructions brutes.    *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_raw_instruction_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    values = PyDict_New();

    result = add_const_to_group(values, "PADDING", RIF_PADDING);
    if (result) result = add_const_to_group(values, "STRING", RIF_STRING);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, true, "RawInstrFlag", values,
                                            "Flags for some instruction properties.\n"
                                            "\n"
                                            "They can be seen as an extension of" \
                                            " pychrysalide.arch.ArchInstruction.ArchInstrFlag");

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type dont le dictionnaire est à compléter.            *
*                                                                             *
*  Description : Définit les constantes liées aux comportements erratiques.   *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_undefined_instruction_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    values = PyDict_New();

    result = add_const_to_group(values, "NOP", IEB_NOP);
    if (result) result = add_const_to_group(values, "UNDEFINED", IEB_UNDEFINED);
    if (result) result = add_const_to_group(values, "UNPREDICTABLE", IEB_UNPREDICTABLE);
    if (result) result = add_const_to_group(values, "RESERVED", IEB_RESERVED);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, false, "ExpectedBehavior", values,
                                            "List of possible behaviors of undefined instructions.");

 exit:

    return result;

}
