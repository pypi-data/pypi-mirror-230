
/* Chrysalide - Outil d'analyse de fichiers binaires
 * constants.c - ajout des constantes liées aux analyses
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


#include <analysis/type.h>
#include <common/endianness.h>


#include "../helpers.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type dont le dictionnaire est à compléter.            *
*                                                                             *
*  Description : Définit les constantes relatives aux contenus binaires.      *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_analysis_content_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    values = PyDict_New();

    result = add_const_to_group(values, "LITTLE", SRE_LITTLE);
    if (result) result = add_const_to_group(values, "LITTLE_WORD", SRE_LITTLE_WORD);
    if (result) result = add_const_to_group(values, "BIG_WORD", SRE_BIG_WORD);
    if (result) result = add_const_to_group(values, "BIG", SRE_BIG);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, false, "SourceEndian", values,
                                            "Endianness of handled data.");

    values = PyDict_New();

    result = add_const_to_group(values, "UNDEFINED", MDS_UNDEFINED);
    if (result) result = add_const_to_group(values, "_4_BITS_UNSIGNED", MDS_4_BITS_UNSIGNED);
    if (result) result = add_const_to_group(values, "_8_BITS_UNSIGNED", MDS_8_BITS_UNSIGNED);
    if (result) result = add_const_to_group(values, "_16_BITS_UNSIGNED", MDS_16_BITS_UNSIGNED);
    if (result) result = add_const_to_group(values, "_32_BITS_UNSIGNED", MDS_32_BITS_UNSIGNED);
    if (result) result = add_const_to_group(values, "_64_BITS_UNSIGNED", MDS_64_BITS_UNSIGNED);
    if (result) result = add_const_to_group(values, "_4_BITS_SIGNED", MDS_4_BITS_SIGNED);
    if (result) result = add_const_to_group(values, "_8_BITS_SIGNED", MDS_8_BITS_SIGNED);
    if (result) result = add_const_to_group(values, "_16_BITS_SIGNED", MDS_16_BITS_SIGNED);
    if (result) result = add_const_to_group(values, "_32_BITS_SIGNED", MDS_32_BITS_SIGNED);
    if (result) result = add_const_to_group(values, "_64_BITS_SIGNED", MDS_64_BITS_SIGNED);
    if (result) result = add_const_to_group(values, "_4_BITS", MDS_4_BITS_UNSIGNED);
    if (result) result = add_const_to_group(values, "_8_BITS", MDS_8_BITS_UNSIGNED);
    if (result) result = add_const_to_group(values, "_16_BITS", MDS_16_BITS_UNSIGNED);
    if (result) result = add_const_to_group(values, "_32_BITS", MDS_32_BITS_UNSIGNED);
    if (result) result = add_const_to_group(values, "_64_BITS", MDS_64_BITS_UNSIGNED);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, false, "MemoryDataSize", values,
                                            "Size of processed data.");

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en constante SourceEndian.                *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_source_endian(PyObject *arg, void *dst)
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
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to SourceEndian");
            break;

        case 1:
            value = PyLong_AsUnsignedLong(arg);

            if (value > SRE_BIG)
            {
                PyErr_SetString(PyExc_TypeError, "invalid value for SourceEndian");
                result = 0;
            }

            else
                *((SourceEndian *)dst) = value;

            break;

        default:
            assert(false);
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en constante MemoryDataSize.              *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_memory_data_size(PyObject *arg, void *dst)
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
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to MemoryDataSize");
            break;

        case 1:
            value = PyLong_AsUnsignedLong(arg);

            if (value != MDS_UNDEFINED
                && (value < MDS_4_BITS_UNSIGNED && value > MDS_64_BITS_UNSIGNED)
                && (value < MDS_4_BITS_SIGNED && value > MDS_64_BITS_SIGNED))
            {
                PyErr_SetString(PyExc_TypeError, "invalid value for MemoryDataSize");
                result = 0;
            }

            else
                *((MemoryDataSize *)dst) = value;

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
*  Description : Définit les constantes pour les types de données.            *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_analysis_data_type_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    values = PyDict_New();

    result = add_const_to_group(values, "NONE", TQF_NONE);
    if (result) result = add_const_to_group(values, "RESTRICT", TQF_RESTRICT);
    if (result) result = add_const_to_group(values, "VOLATILE", TQF_VOLATILE);
    if (result) result = add_const_to_group(values, "CONST", TQF_CONST);
    if (result) result = add_const_to_group(values, "ALL", TQF_ALL);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, false, "TypeQualifier", values,
                                            "Qualifier for a data type.");

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en constante TypeQualifier.               *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_data_type_qualifier(PyObject *arg, void *dst)
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
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to TypeQualifier");
            break;

        case 1:
            value = PyLong_AsUnsignedLong(arg);

            if ((value & ~TQF_ALL) != 0)
            {
                PyErr_SetString(PyExc_TypeError, "invalid value for TypeQualifier");
                result = 0;
            }

            else
                *((TypeQualifier *)dst) = value;

            break;

        default:
            assert(false);
            break;

    }

    return result;

}
