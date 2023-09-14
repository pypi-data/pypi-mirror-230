
/* Chrysalide - Outil d'analyse de fichiers binaires
 * op_nop.c - décodage des absences d'opération
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
*  Description : Décode une instruction de type 'nop'.                        *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *jvm_read_instr_nop(const bin_t *data, off_t *pos, off_t len, vmpa_t addr, const GJvmProcessor *proc)
{
    GArchInstruction *result;               /* Instruction à retourner     */

    result = g_jvm_instruction_new(JOP_NOP);

    return result;

}
