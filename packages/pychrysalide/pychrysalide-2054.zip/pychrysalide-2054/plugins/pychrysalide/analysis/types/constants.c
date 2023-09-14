
/* Chrysalide - Outil d'analyse de fichiers binaires
 * constants.c - ajout des constantes de base pour les types
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


#include <analysis/types/basic.h>
#include <analysis/types/cse.h>
#include <analysis/types/encaps.h>


#include "../../helpers.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type dont le dictionnaire est à compléter.            *
*                                                                             *
*  Description : Définit les constantes relatives aux types de base.          *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_basic_type_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    values = PyDict_New();

    result = add_const_to_group(values, "VOID", BTP_VOID);
    if (result) result = add_const_to_group(values, "WCHAR_T", BTP_WCHAR_T);
    if (result) result = add_const_to_group(values, "BOOL", BTP_BOOL);
    if (result) result = add_const_to_group(values, "CHAR", BTP_CHAR);
    if (result) result = add_const_to_group(values, "SCHAR", BTP_SCHAR);
    if (result) result = add_const_to_group(values, "UCHAR", BTP_UCHAR);
    if (result) result = add_const_to_group(values, "SHORT", BTP_SHORT);
    if (result) result = add_const_to_group(values, "USHORT", BTP_USHORT);
    if (result) result = add_const_to_group(values, "INT", BTP_INT);
    if (result) result = add_const_to_group(values, "UINT", BTP_UINT);
    if (result) result = add_const_to_group(values, "LONG", BTP_LONG);
    if (result) result = add_const_to_group(values, "ULONG", BTP_ULONG);
    if (result) result = add_const_to_group(values, "LONG_LONG", BTP_LONG_LONG);
    if (result) result = add_const_to_group(values, "ULONG_LONG", BTP_ULONG_LONG);
    if (result) result = add_const_to_group(values, "INT128", BTP_INT128);
    if (result) result = add_const_to_group(values, "UINT128", BTP_UINT128);
    if (result) result = add_const_to_group(values, "FLOAT", BTP_FLOAT);
    if (result) result = add_const_to_group(values, "DOUBLE", BTP_DOUBLE);
    if (result) result = add_const_to_group(values, "LONG_DOUBLE", BTP_LONG_DOUBLE);
    if (result) result = add_const_to_group(values, "FLOAT128", BTP_FLOAT128);
    if (result) result = add_const_to_group(values, "ELLIPSIS", BTP_ELLIPSIS);
    if (result) result = add_const_to_group(values, "754R_64", BTP_754R_64);
    if (result) result = add_const_to_group(values, "754R_128", BTP_754R_128);
    if (result) result = add_const_to_group(values, "754R_32", BTP_754R_32);
    if (result) result = add_const_to_group(values, "754R_16", BTP_754R_16);
    if (result) result = add_const_to_group(values, "754R_N", BTP_754R_N);
    if (result) result = add_const_to_group(values, "CHAR32_T", BTP_CHAR32_T);
    if (result) result = add_const_to_group(values, "CHAR16_T", BTP_CHAR16_T);
    if (result) result = add_const_to_group(values, "AUTO", BTP_AUTO);
    if (result) result = add_const_to_group(values, "DECL_AUTO", BTP_DECL_AUTO);
    if (result) result = add_const_to_group(values, "INVALID", BTP_INVALID);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, false, "BaseType", values,
                                            "Identifiers for basic data types.");

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en constante BaseType.                    *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_basic_type_base_type(PyObject *arg, void *dst)
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
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to BaseType");
            break;

        case 1:
            value = PyLong_AsUnsignedLong(arg);

            if (value > BTP_INVALID)
            {
                PyErr_SetString(PyExc_TypeError, "invalid value for BaseType");
                result = 0;
            }

            else
                *((BaseType *)dst) = value;

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
*  Description : Définit les constantes relatives aux classes et énumérations.*
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_class_enum_type_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    values = PyDict_New();

    result = add_const_to_group(values, "UNKNOWN", CEK_UNKNOWN);
    if (result) result = add_const_to_group(values, "STRUCT", CEK_STRUCT);
    if (result) result = add_const_to_group(values, "ENUM", CEK_ENUM);
    if (result) result = add_const_to_group(values, "CLASS", CEK_CLASS);
    if (result) result = add_const_to_group(values, "NAMESPACE", CEK_NAMESPACE);
    if (result) result = add_const_to_group(values, "VIRTUAL_TABLE", CEK_VIRTUAL_TABLE);
    if (result) result = add_const_to_group(values, "VIRTUAL_STRUCT", CEK_VIRTUAL_STRUCT);
    if (result) result = add_const_to_group(values, "COUNT", CEK_COUNT);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, false, "ClassEnumKind", values,
                                            "Kind of types such as classes, structures and enumerations.");

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en constante ClassEnumKind.               *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_class_enum_type_class_enum_kind(PyObject *arg, void *dst)
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
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to ClassEnumKind");
            break;

        case 1:
            value = PyLong_AsUnsignedLong(arg);

            if (value > CEK_COUNT)
            {
                PyErr_SetString(PyExc_TypeError, "invalid value for ClassEnumKind");
                result = 0;
            }

            else
                *((ClassEnumKind *)dst) = value;

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
*  Description : Définit les constantes relatives aux types encapsulés.       *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_encapsulated_type_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    values = PyDict_New();

    result = add_const_to_group(values, "POINTER", ECT_POINTER);
    if (result) result = add_const_to_group(values, "ARRAY", ECT_ARRAY);
    if (result) result = add_const_to_group(values, "REFERENCE", ECT_REFERENCE);
    if (result) result = add_const_to_group(values, "RVALUE_REF", ECT_RVALUE_REF);
    if (result) result = add_const_to_group(values, "COMPLEX", ECT_COMPLEX);
    if (result) result = add_const_to_group(values, "IMAGINARY", ECT_IMAGINARY);
    if (result) result = add_const_to_group(values, "COUNT", ECT_COUNT);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, false, "EncapsulationType", values,
                                            "Identifiers for basic data types.");

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en constante EncapsulationType.           *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_encapsulation_type(PyObject *arg, void *dst)
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
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to EncapsulationType");
            break;

        case 1:
            value = PyLong_AsUnsignedLong(arg);

            if (value > ECT_COUNT)
            {
                PyErr_SetString(PyExc_TypeError, "invalid value for EncapsulationType");
                result = 0;
            }

            else
                *((EncapsulationType *)dst) = value;

            break;

        default:
            assert(false);
            break;

    }

    return result;

}
