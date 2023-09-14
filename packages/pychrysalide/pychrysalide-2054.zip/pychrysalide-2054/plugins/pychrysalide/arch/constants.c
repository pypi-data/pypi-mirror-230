
/* Chrysalide - Outil d'analyse de fichiers binaires
 * constants.c - ajout des constantes de base pour les architectures
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


#include <arch/instruction.h>
#include <arch/processor.h>
#include <arch/vmpa.h>


#include "../helpers.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type dont le dictionnaire est à compléter.            *
*                                                                             *
*  Description : Définit les constantes relatives aux instructions.           *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_arch_instruction_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    values = PyDict_New();

    result = add_const_to_group(values, "NONE", AIF_NONE);
    if (result) result = add_const_to_group(values, "ROUTINE_START", AIF_ROUTINE_START);
    if (result) result = add_const_to_group(values, "RETURN_POINT", AIF_RETURN_POINT);
    if (result) result = add_const_to_group(values, "COND_RETURN_POINT", AIF_COND_RETURN_POINT);
    if (result) result = add_const_to_group(values, "CALL", AIF_CALL);
    if (result) result = add_const_to_group(values, "LOW_USER", AIF_LOW_USER);
    if (result) result = add_const_to_group(values, "HIGH_USER", AIF_HIGH_USER);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, true, "ArchInstrFlag", values,
                                            "Flags for some instruction properties.");

    values = PyDict_New();

    result = add_const_to_group(values, "FETCH", IPH_FETCH);
    if (result) result = add_const_to_group(values, "LINK", IPH_LINK);
    if (result) result = add_const_to_group(values, "POST", IPH_POST);
    if (result) result = add_const_to_group(values, "COUNT", IPH_COUNT);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, false, "InstrProcessHook", values,
                                            "Kind of hook for instruction processing after disassembling.");

    values = PyDict_New();

    result = add_const_to_group(values, "EXEC_FLOW", ILT_EXEC_FLOW);
    if (result) result = add_const_to_group(values, "JUMP", ILT_JUMP);
    if (result) result = add_const_to_group(values, "CASE_JUMP", ILT_CASE_JUMP);
    if (result) result = add_const_to_group(values, "JUMP_IF_TRUE", ILT_JUMP_IF_TRUE);
    if (result) result = add_const_to_group(values, "JUMP_IF_FALSE", ILT_JUMP_IF_FALSE);
    if (result) result = add_const_to_group(values, "LOOP", ILT_LOOP);
    if (result) result = add_const_to_group(values, "CALL", ILT_CALL);
    if (result) result = add_const_to_group(values, "CATCH_EXCEPTION", ILT_CATCH_EXCEPTION);
    if (result) result = add_const_to_group(values, "REF", ILT_REF);
    if (result) result = add_const_to_group(values, "COUNT", ILT_COUNT);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, false, "InstructionLinkType", values,
                                            "Kind of link between two instructions.");

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type dont le dictionnaire est à compléter.            *
*                                                                             *
*  Description : Définit les constantes relatives aux processeurs.            *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_arch_processor_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    values = PyDict_New();

    result = add_const_to_group(values, "DISASSEMBLY", APE_DISASSEMBLY);
    if (result) result = add_const_to_group(values, "LABEL", APE_LABEL);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, true, "ArchProcessingError", values,
                                            "Flags for error occurring while disassembling instructions.");

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en constante ArchProcessingError.         *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_arch_processing_error(PyObject *arg, void *dst)
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
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to ArchProcessingError");
            break;

        case 1:
            value = PyLong_AsUnsignedLong(arg);

            if ((value & (APE_DISASSEMBLY | APE_LABEL)) != 0)
            {
                PyErr_SetString(PyExc_TypeError, "invalid value for ArchProcessingError");
                result = 0;
            }

            else
                *((ArchProcessingError *)dst) = value;

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
*  Description : Définit les constantes relatives aux emplacements.           *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_arch_vmpa_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    values = PyDict_New();

    result = add_const_to_group(values, "NO_PHYSICAL", VMPA_NO_PHYSICAL);
    if (result) result = add_const_to_group(values, "NO_VIRTUAL", VMPA_NO_VIRTUAL);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, false, "VmpaSpecialValue", values,
                                            "Special values for memory locations.");

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type dont le dictionnaire est à compléter.            *
*                                                                             *
*  Description : Définit les constantes relatives aux contextes.              *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_proc_context_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    values = PyDict_New();

    result = add_const_to_group(values, "ENTRY_POINT", DPL_ENTRY_POINT);
    if (result) result = add_const_to_group(values, "FORMAT_POINT", DPL_FORMAT_POINT);
    if (result) result = add_const_to_group(values, "SYMBOL", DPL_SYMBOL);
    if (result) result = add_const_to_group(values, "OTHER", DPL_OTHER);
    if (result) result = add_const_to_group(values, "COUNT", DPL_COUNT);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, true, "DisassPriorityLevel", values,
                                            "Level of priority for a given point during the" \
                                            " disassembling process.");

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en constante DisassPriorityLevel.         *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_disass_priority_level(PyObject *arg, void *dst)
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
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to DisassPriorityLevel");
            break;

        case 1:
            value = PyLong_AsUnsignedLong(arg);

            if (value > DPL_COUNT)
            {
                PyErr_SetString(PyExc_TypeError, "invalid value for DisassPriorityLevel");
                result = 0;
            }

            else
                *((DisassPriorityLevel *)dst) = value;

            break;

        default:
            assert(false);
            break;

    }

    return result;

}
