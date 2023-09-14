
/* Chrysalide - Outil d'analyse de fichiers binaires
 * op_ret.c - décodage des ordres de retour
 *
 * Copyright (C) 2018 Cyrille Bagard
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
 *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.
 */


#include "opcodes.h"


#include "instruction.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : data = flux de données à analyser.                           *
*                pos  = position courante dans ce flux. [OUT]                 *
*                len  = taille totale des données à analyser.                 *
*                addr = adresse virtuelle de l'instruction.                   *
*                proc = architecture ciblée par le désassemblage.             *
*                                                                             *
*  Description : Décode une instruction de type 'areturn'.                    *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *jvm_read_instr_areturn(const bin_t *data, off_t *pos, off_t len, vmpa_t addr, const GJvmProcessor *proc)
{
    GArchInstruction *result;               /* Instruction à retourner     */

    result = g_jvm_instruction_new(JOP_ARETURN);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : data = flux de données à analyser.                           *
*                pos  = position courante dans ce flux. [OUT]                 *
*                len  = taille totale des données à analyser.                 *
*                addr = adresse virtuelle de l'instruction.                   *
*                proc = architecture ciblée par le désassemblage.             *
*                                                                             *
*  Description : Décode une instruction de type 'dreturn'.                    *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *jvm_read_instr_dreturn(const bin_t *data, off_t *pos, off_t len, vmpa_t addr, const GJvmProcessor *proc)
{
    GArchInstruction *result;               /* Instruction à retourner     */

    result = g_jvm_instruction_new(JOP_DRETURN);

    return result;

}
/******************************************************************************
*                                                                             *
*  Paramètres  : data = flux de données à analyser.                           *
*                pos  = position courante dans ce flux. [OUT]                 *
*                len  = taille totale des données à analyser.                 *
*                addr = adresse virtuelle de l'instruction.                   *
*                proc = architecture ciblée par le désassemblage.             *
*                                                                             *
*  Description : Décode une instruction de type 'freturn'.                    *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *jvm_read_instr_freturn(const bin_t *data, off_t *pos, off_t len, vmpa_t addr, const GJvmProcessor *proc)
{
    GArchInstruction *result;               /* Instruction à retourner     */

    result = g_jvm_instruction_new(JOP_FRETURN);

    return result;

}
/******************************************************************************
*                                                                             *
*  Paramètres  : data = flux de données à analyser.                           *
*                pos  = position courante dans ce flux. [OUT]                 *
*                len  = taille totale des données à analyser.                 *
*                addr = adresse virtuelle de l'instruction.                   *
*                proc = architecture ciblée par le désassemblage.             *
*                                                                             *
*  Description : Décode une instruction de type 'ireturn'.                    *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *jvm_read_instr_ireturn(const bin_t *data, off_t *pos, off_t len, vmpa_t addr, const GJvmProcessor *proc)
{
    GArchInstruction *result;               /* Instruction à retourner     */

    result = g_jvm_instruction_new(JOP_IRETURN);

    return result;

}
/******************************************************************************
*                                                                             *
*  Paramètres  : data = flux de données à analyser.                           *
*                pos  = position courante dans ce flux. [OUT]                 *
*                len  = taille totale des données à analyser.                 *
*                addr = adresse virtuelle de l'instruction.                   *
*                proc = architecture ciblée par le désassemblage.             *
*                                                                             *
*  Description : Décode une instruction de type 'lreturn'.                    *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *jvm_read_instr_lreturn(const bin_t *data, off_t *pos, off_t len, vmpa_t addr, const GJvmProcessor *proc)
{
    GArchInstruction *result;               /* Instruction à retourner     */

    result = g_jvm_instruction_new(JOP_LRETURN);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : data = flux de données à analyser.                           *
*                pos  = position courante dans ce flux. [OUT]                 *
*                len  = taille totale des données à analyser.                 *
*                addr = adresse virtuelle de l'instruction.                   *
*                proc = architecture ciblée par le désassemblage.             *
*                                                                             *
*  Description : Décode une instruction de type 'return'.                     *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *jvm_read_instr_return(const bin_t *data, off_t *pos, off_t len, vmpa_t addr, const GJvmProcessor *proc)
{
    GArchInstruction *result;               /* Instruction à retourner     */

    result = g_jvm_instruction_new(JOP_RETURN);

    return result;

}
