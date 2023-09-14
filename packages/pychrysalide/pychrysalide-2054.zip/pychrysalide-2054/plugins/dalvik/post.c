
/* Chrysalide - Outil d'analyse de fichiers binaires
 * post.h - prototypes pour les traitements complémentaires à la phase de désassemblage
 *
 * Copyright (C) 2018-2020 Cyrille Bagard
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


#include <assert.h>


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

void post_process_data_payload_references(GArchInstruction *instr, GArchProcessor *proc, GProcContext *context, GExeFormat *format)
{
    GArchOperand *op;                       /* Opérande numérique en place */
    virt_t addr;                            /* Adresse visée par le saut   */
    GBinFormat *bfmt;                       /* Version basique du format   */
    GTargetOperand *new;                    /* Instruction de ciblage      */
    vmpa2t target;                          /* Défination finale précise   */
    mrange_t trange;                        /* Etendue du symbole à créer  */
    VMPA_BUFFER(loc);                       /* Conversion en chaîne        */
    char name[12 + VMPA_MAX_LEN];           /* Etiquette de la destination */
    GBinSymbol *symbol;                     /* Nouveau symbole construit   */

    g_arch_instruction_lock_operands(instr);

    op = _g_arch_instruction_get_operand(instr, 1);
    assert(G_IS_IMM_OPERAND(op));

    if (g_imm_operand_to_virt_t(G_IMM_OPERAND(op), &addr)
        && g_exe_format_translate_address_into_vmpa(format, addr, &target))
    {
        bfmt = G_BIN_FORMAT(format);

        new = G_TARGET_OPERAND(g_target_operand_new(MDS_32_BITS_UNSIGNED, &target));

        if (!g_target_operand_resolve(new, bfmt, true))
        {
            init_mrange(&trange, &target, 0);

            vmpa2_to_string(&target, MDS_UNDEFINED, loc, NULL);

            snprintf(name, sizeof(name), "array_data_%s", loc + 2);

            symbol = g_binary_symbol_new(&trange, STP_CODE_LABEL);
            g_binary_symbol_set_alt_label(symbol, name);

            g_binary_format_add_symbol(bfmt, symbol);

            g_target_operand_resolve(new, bfmt, true);

        }

        _g_arch_instruction_replace_operand(instr, op, G_ARCH_OPERAND(new));

    }

    g_object_unref(G_OBJECT(op));

    g_arch_instruction_unlock_operands(instr);

}
