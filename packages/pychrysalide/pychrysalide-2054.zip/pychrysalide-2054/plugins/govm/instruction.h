
/* Chrysalide - Outil d'analyse de fichiers binaires
 * instruction.h - prototypes pour la gestion des instructions de la machine virtuelle GoVM
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


#ifndef _PLUGINS_GOVM_INSTRUCTION_H
#define _PLUGINS_GOVM_INSTRUCTION_H


#include "../../src/arch/archbase.h"



/* Enumération de tous les opcodes */
typedef enum _GoVMOpcodes
{
    GOP_SYSCALL,                            /* syscall (0x00)              */
    GOP_LI,                                 /* li (0x01)                   */
    GOP_JMP,                                /* jmp (0x02)                  */
    GOP_JZ,                                 /* jz (0x03)                   */
    GOP_LB,                                 /* lb (0x04)                   */
    GOP_LW,                                 /* lw (0x05)                   */
    GOP_SB,                                 /* sb (0x06)                   */
    GOP_SW,                                 /* sw (0x07)                   */
    GOP_ADD,                                /* add (0x08)                  */
    GOP_SALLOC,                             /* salloc (0x09)               */
    GOP_DIV,                                /* div (0x0a)                  */
    GOP_NOR,                                /* nor (0x0b)                  */
    GOP_POP,                                /* pop (0x0c)                  */
    GOP_DUP,                                /* dup (0x0d)                  */
    GOP_ROT,                                /* rot (0x0e)                  */
    GOP_ROT3,                               /* rot3 (0x0f)                 */
    GOP_MOV_A,                              /* pop (0x10)                  */
    GOP_MOV_B,                              /* pop (0x11)                  */
    GOP_MOV_C,                              /* pop (0x12)                  */
    GOP_MOV_D,                              /* pop (0x13)                  */
    GOP_MOV_E,                              /* pop (0x14)                  */
    GOP_MOV_F,                              /* pop (0x15)                  */
    GOP_A_MOV,                              /* push (0x16)                 */
    GOP_B_MOV,                              /* push (0x17)                 */
    GOP_C_MOV,                              /* push (0x18)                 */
    GOP_D_MOV,                              /* push (0x19)                 */
    GOP_E_MOV,                              /* push (0x1a)                 */
    GOP_F_MOV,                              /* push (0x1b)                 */
    GOP_CALL,                               /* call (0x1c)                 */
    GOP_LWS,                                /* lws (0x1d)                  */
    GOP_SWS,                                /* sws (0x1e)                  */
    GOP_SUB,                                /* sub (0x1f)                  */
    GOP_NOT,                                /* not (0x20)                  */
    GOP_EQU,                                /* equ (0x21)                  */
    GOP_LOE,                                /* loe (0x22)                  */
    GOP_GOE,                                /* goe (0x23)                  */
    GOP_LT,                                 /* lt (0x24)                   */
    GOP_GT,                                 /* gt (0x25)                   */
    GOP_AND,                                /* and (0x26)                  */
    GOP_OR,                                 /* or (0x27)                   */
    GOP_SHL,                                /* shl (0x28)                  */
    GOP_SHR,                                /* shr (0x29)                  */
    GOP_MUL,                                /* mul (0x2a)                  */
    GOP_NOP,                                /* nop (0x2b)                  */
    GOP_XOR,                                /* xor (0x2c)                  */

    GOP_COUNT

} GoVMOpcodes;





/* Fournit de quoi encodée une instruction donnée. */
bin_t get_govm_instruction_opcode(GoVMOpcodes);






#endif  /* _PLUGINS_GOVM_INSTRUCTION_H */
