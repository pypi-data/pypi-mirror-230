
/* Chrysalide - Outil d'analyse de fichiers binaires
 * post.c - traitements complémentaires à la phase de désassemblage
 *
 * Copyright (C) 2017-2020 Cyrille Bagard
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


#include "post.h"


#include <arch/operands/immediate.h>
#include <arch/operands/target.h>



/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction ARMv7 à traiter.                       *
*                proc    = représentation de l'architecture utilisée.         *
*                context = contexte associé à la phase de désassemblage.      *
*                format  = accès aux données du binaire d'origine.            *
*                                                                             *
*  Description : Complète un désassemblage accompli pour une instruction.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void post_process_ldr_instructions(GArchInstruction *instr, GArchProcessor *proc, GProcContext *context, GExeFormat *format)
{
    GArchOperand *op;                       /* Opérande numérique en place */
    virt_t addr;                            /* Adresse visée par le saut   */
    GBinFormat *bfmt;                       /* Version basique du format   */
    GTargetOperand *new;                    /* Instruction de ciblage      */
    vmpa2t target;                          /* Défination finale précise   */

    g_arch_instruction_lock_operands(instr);

    op = _g_arch_instruction_get_operand(instr, 1);

    if (!G_IS_IMM_OPERAND(op))
        goto ppli_release;

    if (g_imm_operand_to_virt_t(G_IMM_OPERAND(op), &addr)
        && g_exe_format_translate_address_into_vmpa(format, addr, &target))
    {
        bfmt = G_BIN_FORMAT(format);

        new = G_TARGET_OPERAND(g_target_operand_new(MDS_32_BITS_UNSIGNED, &target));

        if (!g_target_operand_resolve(new, bfmt, true))
            g_object_unref(G_OBJECT(new));

        else
            _g_arch_instruction_replace_operand(instr, op, G_ARCH_OPERAND(new));

    }

 ppli_release:

    g_object_unref(G_OBJECT(op));

    g_arch_instruction_unlock_operands(instr);

}
