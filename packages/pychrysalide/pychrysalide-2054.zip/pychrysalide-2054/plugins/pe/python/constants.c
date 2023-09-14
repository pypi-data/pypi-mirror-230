
/* Chrysalide - Outil d'analyse de fichiers binaires
 * constants.c - équivalent Python partiel du fichier "plugins/pe/pe_def.h"
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


#include <plugins/pychrysalide/helpers.h>


#include "../pe_def.h"
#include "../routine.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type dont le dictionnaire est à compléter.            *
*                                                                             *
*  Description : Définit les constantes pour le format PE.                    *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_python_pe_format_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    result = true;

    /**
     * Indices des répertoires PE
     */

    values = PyDict_New();

    if (result) result = add_const_to_group(values, "EXPORT", IMAGE_DIRECTORY_ENTRY_EXPORT);
    if (result) result = add_const_to_group(values, "IMPORT", IMAGE_DIRECTORY_ENTRY_IMPORT);
    if (result) result = add_const_to_group(values, "RESOURCE", IMAGE_DIRECTORY_ENTRY_RESOURCE);
    if (result) result = add_const_to_group(values, "EXCEPTION", IMAGE_DIRECTORY_ENTRY_EXCEPTION);
    if (result) result = add_const_to_group(values, "SECURITY", IMAGE_DIRECTORY_ENTRY_SECURITY);
    if (result) result = add_const_to_group(values, "BASERELOC", IMAGE_DIRECTORY_ENTRY_BASERELOC);
    if (result) result = add_const_to_group(values, "DEBUG", IMAGE_DIRECTORY_ENTRY_DEBUG);
    if (result) result = add_const_to_group(values, "ARCHITECTURE", IMAGE_DIRECTORY_ENTRY_ARCHITECTURE);
    if (result) result = add_const_to_group(values, "GLOBALPTR", IMAGE_DIRECTORY_ENTRY_GLOBALPTR);
    if (result) result = add_const_to_group(values, "TLS", IMAGE_DIRECTORY_ENTRY_TLS);
    if (result) result = add_const_to_group(values, "LOAD_CONFIG", IMAGE_DIRECTORY_ENTRY_LOAD_CONFIG);
    if (result) result = add_const_to_group(values, "BOUND_IMPORT", IMAGE_DIRECTORY_ENTRY_BOUND_IMPORT);
    if (result) result = add_const_to_group(values, "IAT", IMAGE_DIRECTORY_ENTRY_IAT);
    if (result) result = add_const_to_group(values, "DELAY_IMPORT", IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT);
    if (result) result = add_const_to_group(values, "COM_DESCRIPTOR", IMAGE_DIRECTORY_ENTRY_COM_DESCRIPTOR);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, false, "ImageDirectoryEntry", values,
                                            "Index number for a kind of data directory entry.");

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type dont le dictionnaire est à compléter.            *
*                                                                             *
*  Description : Définit les constantes pour les routines du format PE.       *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_python_pe_exported_routine_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    result = true;

    values = PyDict_New();

    if (result) result = add_const_to_group(values, "HAS_ORDINAL", PSF_HAS_ORDINAL);
    if (result) result = add_const_to_group(values, "FORWARDED", PSF_FORWARDED);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, true, "PeSymbolFlag", values,
                                            "Extra indications for exported PE routine symbols.");

    values = PyDict_New();

    if (result) result = add_const_to_group(values, "UNDEF_PE_ORDINAL", UNDEF_PE_ORDINAL);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, false, "OrdinalValue", values,
                                            "Extra value for exported PE routine ordinals.");

 exit:

    return result;

}
