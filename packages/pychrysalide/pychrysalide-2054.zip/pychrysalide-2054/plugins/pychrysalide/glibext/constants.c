
/* Chrysalide - Outil d'analyse de fichiers binaires
 * constants.c - ajout des constantes de base pour les extensions à la GLib
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


#include <i18n.h>
#include <glibext/bufferline.h>
#include <glibext/comparison.h>
#include <glibext/configuration.h>
#include <glibext/linesegment.h>
#include <glibext/gbinportion.h>
#ifdef INCLUDE_GTK_SUPPORT
#   include <glibext/gloadedpanel.h>
#endif


#include "../helpers.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type dont le dictionnaire est à compléter.            *
*                                                                             *
*  Description : Définit les constantes relatives aux portions de binaires.   *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_binary_portion_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *strdict;                      /* Groupe de chaînes constantes*/
    PyObject *values;                       /* Groupe de valeurs à établir */

    result = create_string_constants_group_to_type(type, "BinaryPortionCode",
                                                   "Selector names for the CSS rendering.", &strdict);

    if (result) result = extend_string_constants_group(strdict, "RAW", BPC_RAW);
    if (result) result = extend_string_constants_group(strdict, "CODE", BPC_CODE);
    if (result) result = extend_string_constants_group(strdict, "DATA", BPC_DATA);
    if (result) result = extend_string_constants_group(strdict, "DATA_RO", BPC_DATA_RO);
    if (result) result = extend_string_constants_group(strdict, "DISASS_ERROR", BPC_DISASS_ERROR);

    if (!result)
        goto exit;

    values = PyDict_New();

    result = add_const_to_group(values, "NONE", PAC_NONE);
    if (result) result = add_const_to_group(values, "READ", PAC_READ);
    if (result) result = add_const_to_group(values, "WRITE", PAC_WRITE);
    if (result) result = add_const_to_group(values, "EXEC", PAC_EXEC);
    if (result) result = add_const_to_group(values, "ALL", PAC_ALL);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, false, "PortionAccessRights", values,
                                            "Access rights for binary portions.");

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en constante PortionAccessRights.         *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_portion_access_rights(PyObject *arg, void *dst)
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
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to PortionAccessRights");
            break;

        case 1:
            value = PyLong_AsUnsignedLong(arg);

            if ((value & ~PAC_ALL) != 0)
            {
                PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to PortionAccessRights");
                result = 0;
            }

            else
                *((PortionAccessRights *)dst) = value;

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
*  Description : Définit les constantes relatives aux lignes de tampon.       *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_buffer_line_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    values = PyDict_New();

    result = add_const_to_group(values, "NONE", BLF_NONE);
    if (result) result = add_const_to_group(values, "HAS_CODE", BLF_HAS_CODE);
    if (result) result = add_const_to_group(values, "IS_LABEL", BLF_IS_LABEL);
    if (result) result = add_const_to_group(values, "ENTRYPOINT", BLF_ENTRYPOINT);
    if (result) result = add_const_to_group(values, "BOOKMARK", BLF_BOOKMARK);
    if (result) result = add_const_to_group(values, "WIDTH_MANAGER", BLF_WIDTH_MANAGER);
    if (result) result = add_const_to_group(values, "ALL", BLF_ALL);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, true, "BufferLineFlags", values,
                                            "Optional flags linked to a rendering line.");

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en constante BufferLineFlags.             *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_buffer_line_flags(PyObject *arg, void *dst)
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
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to BufferLineFlags");
            break;

        case 1:
            value = PyLong_AsUnsignedLong(arg);

            if ((value & BLF_ALL) != value)
            {
                PyErr_SetString(PyExc_TypeError, "invalid value for BufferLineFlags");
                result = 0;
            }

            else
                *((BufferLineFlags *)dst) = value;

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
*  Description : Définit les constantes relatives aux modes de comparaison.   *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_comparable_item_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    values = PyDict_New();

    result = add_const_to_group(values, "LT", RCO_LT);
    if (result) result = add_const_to_group(values, "LE", RCO_LE);
    if (result) result = add_const_to_group(values, "EQ", RCO_EQ);
    if (result) result = add_const_to_group(values, "NE", RCO_NE);
    if (result) result = add_const_to_group(values, "GT", RCO_GT);
    if (result) result = add_const_to_group(values, "GE", RCO_GE);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, true, "RichCmpOperation", values,
                                            "Modes for objects comparison.");

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type dont le dictionnaire est à compléter.            *
*                                                                             *
*  Description : Définit les constantes relatives aux paramètres de config.   *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_config_param_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    values = PyDict_New();

    result = add_const_to_group(values, "BOOLEAN", CPT_BOOLEAN);
    if (result) result = add_const_to_group(values, "INTEGER", CPT_INTEGER);
    if (result) result = add_const_to_group(values, "ULONG", CPT_ULONG);
    if (result) result = add_const_to_group(values, "STRING", CPT_STRING);
    if (result) result = add_const_to_group(values, "COLOR", CPT_COLOR);
    if (result) result = add_const_to_group(values, "COUNT", CPT_COUNT);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, false, "ConfigParamType", values,
                                            "Kind of value available for configuration parameter types.");

    values = PyDict_New();

    result = add_const_to_group(values, "UNDEFINED", CPS_UNDEFINED);
    if (result) result = add_const_to_group(values, "CHANGED", CPS_CHANGED);
    if (result) result = add_const_to_group(values, "DEFAULT", CPS_DEFAULT);
    if (result) result = add_const_to_group(values, "EMPTY", CPS_EMPTY);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, true, "ConfigParamState", values,
                                            "States of a value carried by a configuration parameter.");

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en constante ConfigParamType.             *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_config_param_type(PyObject *arg, void *dst)
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
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to ConfigParamType");
            break;

        case 1:

            value = PyLong_AsUnsignedLong(arg);

            if (value > CPT_COUNT)
            {
                result = 0;
                PyErr_SetString(PyExc_ValueError, _("invalid configuration parameter type"));
            }

            else
                *((ConfigParamType *)dst) = value;

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
*  Description : Définit les constantes relatives aux segments de ligne.      *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_line_segment_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    values = PyDict_New();

    result = add_const_to_group(values, "NONE", RTT_NONE);
    if (result) result = add_const_to_group(values, "RAW", RTT_RAW);
    if (result) result = add_const_to_group(values, "RAW_FULL", RTT_RAW_FULL);
    if (result) result = add_const_to_group(values, "RAW_NULL", RTT_RAW_NULL);
    if (result) result = add_const_to_group(values, "PRINTABLE", RTT_PRINTABLE);
    if (result) result = add_const_to_group(values, "NOT_PRINTABLE", RTT_NOT_PRINTABLE);
    if (result) result = add_const_to_group(values, "COMMENT", RTT_COMMENT);
    if (result) result = add_const_to_group(values, "INDICATION", RTT_INDICATION);
    if (result) result = add_const_to_group(values, "PHYS_ADDR_PAD", RTT_PHYS_ADDR_PAD);
    if (result) result = add_const_to_group(values, "PHYS_ADDR", RTT_PHYS_ADDR);
    if (result) result = add_const_to_group(values, "VIRT_ADDR_PAD", RTT_VIRT_ADDR_PAD);
    if (result) result = add_const_to_group(values, "VIRT_ADDR", RTT_VIRT_ADDR);
    if (result) result = add_const_to_group(values, "RAW_CODE", RTT_RAW_CODE);
    if (result) result = add_const_to_group(values, "RAW_CODE_NULL", RTT_RAW_CODE_NULL);
    if (result) result = add_const_to_group(values, "LABEL", RTT_LABEL);
    if (result) result = add_const_to_group(values, "INSTRUCTION", RTT_INSTRUCTION);
    if (result) result = add_const_to_group(values, "IMMEDIATE", RTT_IMMEDIATE);
    if (result) result = add_const_to_group(values, "REGISTER", RTT_REGISTER);
    if (result) result = add_const_to_group(values, "PUNCT", RTT_PUNCT);
    if (result) result = add_const_to_group(values, "HOOK", RTT_HOOK);
    if (result) result = add_const_to_group(values, "SIGNS", RTT_SIGNS);
    if (result) result = add_const_to_group(values, "LTGT", RTT_LTGT);
    if (result) result = add_const_to_group(values, "SECTION", RTT_SECTION);
    if (result) result = add_const_to_group(values, "SEGMENT", RTT_SEGMENT);
    if (result) result = add_const_to_group(values, "STRING", RTT_STRING);
    if (result) result = add_const_to_group(values, "VAR_NAME", RTT_VAR_NAME);
    if (result) result = add_const_to_group(values, "KEY_WORD", RTT_KEY_WORD);
    if (result) result = add_const_to_group(values, "ERROR", RTT_ERROR);
    if (result) result = add_const_to_group(values, "COUNT", RTT_COUNT);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, false, "RenderingTagType", values,
                                            "Kinds of text rendering.");

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en constante RenderingTagType.            *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_rendering_tag_type(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)&PyLong_Type);

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to RenderingTagType");
            break;

        case 1:
            *((RenderingTagType *)dst) = PyLong_AsUnsignedLong(arg);
            break;

        default:
            assert(false);
            break;

    }

    return result;

}


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type dont le dictionnaire est à compléter.            *
*                                                                             *
*  Description : Définit les constantes relatives aux panneaux de chargement. *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_loaded_panel_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    values = PyDict_New();

    result = add_const_to_group(values, "RAW", SPT_RAW);
    if (result) result = add_const_to_group(values, "TOP", SPT_TOP);
    if (result) result = add_const_to_group(values, "CENTER", SPT_CENTER);
    if (result) result = add_const_to_group(values, "BOTTOM", SPT_BOTTOM);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, false, "ScrollPositionTweak", values,
                                            "Details for adjusting the displayed position while scrolling.");

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en constante ScrollPositionTweak.         *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_scroll_position_tweak(PyObject *arg, void *dst)
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
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to ScrollPositionTweak");
            break;

        case 1:

            value = PyLong_AsUnsignedLong(arg);

            if (!IS_VALID_STP(value))
            {
                result = 0;
                PyErr_SetString(PyExc_ValueError, _("invalid position tweak"));
            }

            else
                *((ScrollPositionTweak *)dst) = value;

            break;

        default:
            assert(false);
            break;

    }

    return result;

}


#endif
