
/* Chrysalide - Outil d'analyse de fichiers binaires
 * fetch.c - ajouts de sauts à traiter durant la phase de désassemblage
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


#include "fetch.h"


#include <assert.h>


#include <arch/operands/immediate.h>



/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction ARMv7 à traiter.                       *
*                proc    = représentation de l'architecture utilisée.         *
*                context = contexte associé à la phase de désassemblage.      *
*                format  = acès aux données du binaire d'origine.             *
*                index   = indice de l'opérande précisant le saut.            *
*                                                                             *
*  Description : Pousse une adresse précisée par un saut pour désassemblage.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void help_fetching_with_dalvik_instruction(GArchInstruction *instr, GArchProcessor *proc, GDalvikContext *context, GExeFormat *format, size_t index)
{
    GArchOperand *op;                       /* Opérande numérique en place */
    virt_t target;                          /* Adresse virtuelle visée     */
    bool status;                            /* Bilan de récupération       */

    op = g_arch_instruction_get_operand(instr, index);
    assert(G_IS_IMM_OPERAND(op));

    status = g_imm_operand_to_virt_t(G_IMM_OPERAND(op), &target);
    assert(status);

    g_object_unref(G_OBJECT(op));

    if (status)
        g_proc_context_push_drop_point(G_PROC_CONTEXT(context), DPL_OTHER, target);

}
