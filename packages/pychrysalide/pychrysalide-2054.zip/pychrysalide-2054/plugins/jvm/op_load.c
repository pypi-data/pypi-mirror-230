
/* Chrysalide - Outil d'analyse de fichiers binaires
 * op_load.c - décodage des instructions de chargement
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
*  Description : Décode une instruction de type 'aload_n'.                    *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *jvm_read_instr_aload_n(const bin_t *data, off_t *pos, off_t len, vmpa_t addr, const GJvmProcessor *proc)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    JvmOpcodes opcode;                      /* Instruction effective       */

    opcode = JOP_ALOAD_0 + (data[*pos] - 0x2a);

    (*pos)++;

    result = g_jvm_instruction_new(opcode);

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
*  Description : Décode une instruction de type 'iload_n'.                    *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *jvm_read_instr_iload_n(const bin_t *data, off_t *pos, off_t len, vmpa_t addr, const GJvmProcessor *proc)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    JvmOpcodes opcode;                      /* Instruction effective       */

    opcode = JOP_ILOAD_0 + (data[*pos] - 0x1a);

    (*pos)++;

    result = g_jvm_instruction_new(opcode);

    return result;

}
