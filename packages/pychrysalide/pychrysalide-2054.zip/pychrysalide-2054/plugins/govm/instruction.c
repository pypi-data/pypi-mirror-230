
/* Chrysalide - Outil d'analyse de fichiers binaires
 * instruction.h - gestion des instructions de la machine virtuelle GoVM
 *
 * Copyright (C) 2009-2018 Cyrille Bagard
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


#include "instruction.h"





/* Répertoire de toutes les instructions GoVM */
typedef struct _govm_instruction
{
    bin_t opcode;                           /* Opcode de l'instruction     */

    const char *keyword;                    /* Mot clef de la commande     */

} govm_instruction;


static govm_instruction _instructions[GOP_COUNT] = {

    [GOP_SYSCALL]   = { 0x00, "syscall" },
    [GOP_LI]        = { 0x01, "li" },
    [GOP_JMP]       = { 0x02, "jmp" },
    [GOP_JZ]        = { 0x03, "jz" },
    [GOP_LB]        = { 0x04, "lb" },
    [GOP_LW]        = { 0x05, "lw" },
    [GOP_SB]        = { 0x06, "sb" },
    [GOP_SW]        = { 0x07, "sw" },
    [GOP_ADD]       = { 0x08, "add" },
    [GOP_SALLOC]    = { 0x09, "salloc" },
    [GOP_DIV]       = { 0x0a, "div" },
    [GOP_NOR]       = { 0x0b, "nor" },
    [GOP_POP]       = { 0x0c, "pop" },
    [GOP_DUP]       = { 0x0d, "dup" },
    [GOP_ROT]       = { 0x0e, "rot" },
    [GOP_ROT3]      = { 0x0f, "rot3" },
    [GOP_MOV_A]     = { 0x10, "pop" },
    [GOP_MOV_B]     = { 0x11, "pop" },
    [GOP_MOV_C]     = { 0x12, "pop" },
    [GOP_MOV_D]     = { 0x13, "pop" },
    [GOP_MOV_E]     = { 0x14, "pop" },
    [GOP_MOV_F]     = { 0x15, "pop" },
    [GOP_A_MOV]     = { 0x16, "push" },
    [GOP_B_MOV]     = { 0x17, "push" },
    [GOP_C_MOV]     = { 0x18, "push" },
    [GOP_D_MOV]     = { 0x19, "push" },
    [GOP_E_MOV]     = { 0x1a, "push" },
    [GOP_F_MOV]     = { 0x1b, "push" },
    [GOP_CALL]      = { 0x1c, "call" },
    [GOP_LWS]       = { 0x1d, "lws" },
    [GOP_SWS]       = { 0x1e, "sws" },
    [GOP_SUB]       = { 0x1f, "sub" },
    [GOP_NOT]       = { 0x20, "not" },
    [GOP_EQU]       = { 0x21, "equ" },
    [GOP_LOE]       = { 0x22, "loe" },
    [GOP_GOE]       = { 0x23, "goe" },
    [GOP_LT]        = { 0x24, "lt" },
    [GOP_GT]        = { 0x25, "gt" },
    [GOP_AND]       = { 0x26, "and" },
    [GOP_OR]        = { 0x27, "or" },
    [GOP_SHL]       = { 0x28, "shl" },
    [GOP_SHR]       = { 0x29, "shr" },
    [GOP_MUL]       = { 0x2a, "mul" },
    [GOP_NOP]       = { 0x2b, "nop" },
    [GOP_XOR]       = { 0x2c, "xor" }

};




/******************************************************************************
*                                                                             *
*  Paramètres  : id = identifiant de l'instruction à exporter.                *
*                                                                             *
*  Description : Fournit de quoi encodée une instruction donnée.              *
*                                                                             *
*  Retour      : Valeur de codage de l'instruction.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bin_t get_govm_instruction_opcode(GoVMOpcodes id)
{
    return _instructions[id].opcode;

}
