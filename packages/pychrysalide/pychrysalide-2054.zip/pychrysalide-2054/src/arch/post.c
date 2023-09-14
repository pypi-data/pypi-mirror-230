
/* Chrysalide - Outil d'analyse de fichiers binaires
 * post.c - traitements complémentaires à la phase de désassemblage
 *
 * Copyright (C) 2016-2020 Cyrille Bagard
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


#include "processor.h"
#include "operands/immediate.h"
#include "operands/target.h"
#include "../analysis/routine.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction ARMv7 à traiter.                       *
*                proc    = représentation de l'architecture utilisée.         *
*                context = contexte associé à la phase de désassemblage.      *
*                format  = accès aux données du binaire d'origine.            *
*                index   = indice de l'opérande précisant le saut.            *
*                type    = type du nouveau simple à mettre en place.          *
*                                                                             *
*  Description : Associe un symbole à la valeur ciblée par un opérande.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void post_process_target_resolution(GArchInstruction *instr, GArchProcessor *proc, GProcContext *context, GExeFormat *format, size_t index, SymbolType type)
{
    GArchOperand *op;                       /* Opérande numérique en place */
    virt_t addr;                            /* Adresse visée par le saut   */
    vmpa2t target;                          /* Emplacement de la cible     */
    GBinFormat *bfmt;                       /* Version basique du format   */
    MemoryDataSize ptr_size;                /* Taille de l'espace mémoire  */
    GTargetOperand *new;                    /* Instruction de ciblage      */
    mrange_t trange;                        /* Etendue du symbole à créer  */
    VMPA_BUFFER(loc);                       /* Conversion en chaîne        */
    char name[5 + VMPA_MAX_LEN];            /* Etiquette de la destination */
    GBinRoutine *routine;                   /* Nouvelle routine trouvée    */
    GBinSymbol *symbol;                     /* Nouveau symbole construit   */

    g_arch_instruction_lock_operands(instr);

    op = _g_arch_instruction_get_operand(instr, index);
    assert(G_IS_IMM_OPERAND(op));

    if (g_imm_operand_to_virt_t(G_IMM_OPERAND(op), &addr)
        && g_exe_format_translate_address_into_vmpa(format, addr, &target))
    {
        bfmt = G_BIN_FORMAT(format);

        ptr_size = g_arch_processor_get_memory_size(proc);

        new = G_TARGET_OPERAND(g_target_operand_new(ptr_size, &target));

        if (!g_target_operand_resolve(new, bfmt, true))
        {
            init_mrange(&trange, &target, 0);

            vmpa2_to_string(&target, MDS_UNDEFINED, loc, NULL);

            switch (type)
            {
                case STP_ROUTINE:
                    snprintf(name, sizeof(name), "sub_%s", loc + 2);

                    routine = g_binary_routine_new();
                    symbol = G_BIN_SYMBOL(routine);

                    g_binary_symbol_set_range(symbol, &trange);
                    g_binary_routine_set_name(routine, strdup(name));
                    break;

                case STP_CODE_LABEL:
                    snprintf(name, sizeof(name), "loc_%s", loc + 2);

                    symbol = g_binary_symbol_new(&trange, type);
                    g_binary_symbol_set_alt_label(symbol, name);
                    break;

                default:
                    assert(false);
                    symbol = NULL;
                    break;

            }

            g_binary_format_add_symbol(bfmt, symbol);

            g_target_operand_resolve(new, bfmt, true);

        }

        _g_arch_instruction_replace_operand(instr, op, G_ARCH_OPERAND(new));

    }

    g_object_unref(G_OBJECT(op));

    g_arch_instruction_unlock_operands(instr);

}
