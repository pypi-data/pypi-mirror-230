
/* Chrysalide - Outil d'analyse de fichiers binaires
 * constants.c - équivalent Python partiel du fichier "plugins/dex/dex_def.h"
 *
 * Copyright (C) 2019-2020 Cyrille Bagard
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


#include <format/format.h>
#include <format/strsym.h>
#include <format/symbol.h>


#include "../helpers.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type dont le dictionnaire est à compléter.            *
*                                                                             *
*  Description : Définit les constantes pour les formats binaires.            *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_binary_format_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    values = PyDict_New();

    result = add_const_to_group(values, "SPECIFICATION", BFE_SPECIFICATION);
    if (result) result = add_const_to_group(values, "STRUCTURE", BFE_STRUCTURE);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, true, "BinaryFormatError", values,
                                            "Flags for error occurring while loading a binary format.");

    values = PyDict_New();

    result = add_const_to_group(values, "NONE", FFL_NONE);
    if (result) result = add_const_to_group(values, "RUN_IN_KERNEL_SPACE", FFL_RUN_IN_KERNEL_SPACE);
    if (result) result = add_const_to_group(values, "MASK", FFL_MASK);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, true, "FormatFlag", values,
                                            "Extra indications for formats.");

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en constante BinaryFormatError.           *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_binary_format_error(PyObject *arg, void *dst)
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
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to BinaryFormatError");
            break;

        case 1:
            value = PyLong_AsUnsignedLong(arg);

            if ((value & (BFE_SPECIFICATION | BFE_STRUCTURE)) != 0)
            {
                PyErr_SetString(PyExc_TypeError, "invalid value for BinaryFormatError");
                result = 0;
            }

            else
                *((BinaryFormatError *)dst) = value;

            break;

        default:
            assert(false);
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type dont le dictionnaire est à compléter.            *
*                                                                             *
*  Description : Définit les constantes pour les symboles binaires.           *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_binary_symbol_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    values = PyDict_New();

    result = add_const_to_group(values, "DATA", STP_DATA);
    if (result) result = add_const_to_group(values, "ROUTINE", STP_ROUTINE);
    if (result) result = add_const_to_group(values, "CODE_LABEL", STP_CODE_LABEL);
    if (result) result = add_const_to_group(values, "OBJECT", STP_OBJECT);
    if (result) result = add_const_to_group(values, "ENTRY_POINT", STP_ENTRY_POINT);
    if (result) result = add_const_to_group(values, "RO_STRING", STP_RO_STRING);
    if (result) result = add_const_to_group(values, "DYN_STRING", STP_DYN_STRING);
    if (result) result = add_const_to_group(values, "COUNT", STP_COUNT);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, false, "SymbolType", values,
                                            "Available values for symbol types.");

    values = PyDict_New();

    result = add_const_to_group(values, "INTERNAL", SSS_INTERNAL);
    if (result) result = add_const_to_group(values, "EXPORTED", SSS_EXPORTED);
    if (result) result = add_const_to_group(values, "IMPORTED", SSS_IMPORTED);
    if (result) result = add_const_to_group(values, "DYNAMIC", SSS_DYNAMIC);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, false, "SymbolStatus", values,
                                            "Status of a symbol visibility.");

    values = PyDict_New();

    result = add_const_to_group(values, "NONE", SFL_NONE);
    if (result) result = add_const_to_group(values, "HAS_NM_PREFIX", SFL_HAS_NM_PREFIX);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, true, "SymbolFlag", values,
                                            "Extra indications for symbols.");

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type dont le dictionnaire est à compléter.            *
*                                                                             *
*  Description : Définit les constantes pour les symboles liés à des chaînes. *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_string_symbol_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    result = true;

    values = PyDict_New();

    if (result) result = add_const_to_group(values, "NONE", SET_NONE);
    if (result) result = add_const_to_group(values, "ASCII", SET_ASCII);
    if (result) result = add_const_to_group(values, "UTF_8", SET_UTF_8);
    if (result) result = add_const_to_group(values, "MUTF_8", SET_MUTF_8);
    if (result) result = add_const_to_group(values, "GUESS", SET_GUESS);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, false, "StringEncodingType", values,
                                            "Kinds of encoding for strings.");

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en constante StringEncodingType.          *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_string_encoding_type(PyObject *arg, void *dst)
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
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to StringEncodingType");
            break;

        case 1:
            value = PyLong_AsUnsignedLong(arg);

            if (value > SET_GUESS)
            {
                PyErr_SetString(PyExc_TypeError, "invalid value for StringEncodingType");
                result = 0;
            }

            else
                *((StringEncodingType *)dst) = value;

            break;

        default:
            assert(false);
            break;

    }

    return result;

}
