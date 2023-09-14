
/* Chrysalide - Outil d'analyse de fichiers binaires
 * link.c - édition des liens après la phase de désassemblage
 *
 * Copyright (C) 2015-2020 Cyrille Bagard
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


#include "link.h"


#include <assert.h>


#include "operands/immediate.h"
#include "operands/targetable.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction ARMv7 à traiter.                       *
*                proc    = représentation de l'architecture utilisée.         *
*                context = contexte associé à la phase de désassemblage.      *
*                format  = acès aux données du binaire d'origine.             *
*                                                                             *
*  Description : Etablit un lien de saut selon une instruction donnée.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void handle_jump_as_link(GArchInstruction *instr, GArchProcessor *proc, GProcContext *context, GExeFormat *format)
{
    GArchOperand *op;                       /* Opérande numérique en place */
    virt_t virt;                            /* Adresse virtuelle           */
    vmpa2t addr;                            /* Adresse de destination      */
    GArchInstruction *target;               /* Ligne visée par la référence*/

    g_arch_instruction_lock_operands(instr);

    assert(_g_arch_instruction_count_operands(instr) > 0);

    op = _g_arch_instruction_get_operand(instr, 0);

    g_arch_instruction_unlock_operands(instr);

    if (G_IS_IMM_OPERAND(op)
        && g_imm_operand_to_virt_t(G_IMM_OPERAND(op), &virt)
        && g_exe_format_translate_address_into_vmpa(format, virt, &addr))
    {
        target = g_arch_processor_find_instr_by_address(proc, &addr);

        if (target != NULL)
        {
            g_arch_instruction_link_with(instr, target, ILT_JUMP);
            g_object_unref(G_OBJECT(target));
        }

    }

    g_object_unref(G_OBJECT(op));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction ARMv7 à traiter.                       *
*                proc    = représentation de l'architecture utilisée.         *
*                context = contexte associé à la phase de désassemblage.      *
*                format  = acès aux données du binaire d'origine.             *
*                index   = indice de l'opérande à traiter dans l'instruction. *
*                                                                             *
*  Description : Etablit un lien d'appel selon une instruction donnée.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void handle_branch_as_link(GArchInstruction *instr, GArchProcessor *proc, GProcContext *context, GExeFormat *format, size_t index)
{
    GArchOperand *op;                       /* Opérande numérique en place */
    const mrange_t *range;                  /* Emplacement de l'instruction*/
    bool defined;                           /* Adresse définie ?           */
    vmpa2t addr;                            /* Adresse de destination      */
    GArchInstruction *target;               /* Ligne visée par la référence*/
    vmpa2t next;                            /* Position suivante           */

    g_arch_instruction_lock_operands(instr);

    assert(_g_arch_instruction_count_operands(instr) > index);

    op = _g_arch_instruction_get_operand(instr, index);

    g_arch_instruction_unlock_operands(instr);

    if (G_IS_TARGETABLE_OPERAND(op))
    {
        range = g_arch_instruction_get_range(instr);

        defined = g_targetable_operand_get_addr(G_TARGETABLE_OPERAND(op), get_mrange_addr(range),
                                                G_BIN_FORMAT(format), proc, &addr);
    }

    else
        defined = false;

    g_object_unref(G_OBJECT(op));

    if (defined)
    {
        target = g_arch_processor_find_instr_by_address(proc, &addr);

        if (target != NULL)
        {
            g_arch_instruction_link_with(instr, target, ILT_JUMP_IF_TRUE);

            g_object_unref(G_OBJECT(target));

        }

        compute_mrange_end_addr(range, &next);

        target = g_arch_processor_find_instr_by_address(proc, &next);

        if (target != NULL)
        {
            g_arch_instruction_link_with(instr, target, ILT_JUMP_IF_FALSE);

            g_object_unref(G_OBJECT(target));

        }

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction ARMv7 à traiter.                       *
*                proc    = représentation de l'architecture utilisée.         *
*                context = contexte associé à la phase de désassemblage.      *
*                format  = acès aux données du binaire d'origine.             *
*                                                                             *
*  Description : Etablit un lien d'appel selon une instruction donnée.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void handle_call_as_link(GArchInstruction *instr, GArchProcessor *proc, GProcContext *context, GExeFormat *format)
{
    GArchOperand *op;                       /* Opérande numérique en place */
    virt_t virt;                            /* Adresse virtuelle           */
    vmpa2t addr;                            /* Adresse de destination      */
    GArchInstruction *target;               /* Ligne visée par la référence*/

    g_arch_instruction_lock_operands(instr);

    assert(_g_arch_instruction_count_operands(instr) > 0);

    op = _g_arch_instruction_get_operand(instr, 0);

    g_arch_instruction_unlock_operands(instr);

    if (G_IS_IMM_OPERAND(op)
        && g_imm_operand_to_virt_t(G_IMM_OPERAND(op), &virt)
        && g_exe_format_translate_address_into_vmpa(format, virt, &addr))
    {
        target = g_arch_processor_find_instr_by_address(proc, &addr);

        if (target != NULL)
        {
            g_arch_instruction_link_with(instr, target, ILT_CALL);
            g_object_unref(G_OBJECT(target));
        }

    }

    g_object_unref(G_OBJECT(op));

}
