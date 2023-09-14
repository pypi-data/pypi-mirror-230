
/* Chrysalide - Outil d'analyse de fichiers binaires
 * links.c - résolution des liens entre différentes instructions
 *
 * Copyright (C) 2010-2020 Cyrille Bagard
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


#include "links.h"


#include <assert.h>


#include "../../arch/instruction.h"
#include "../../arch/instructions/raw.h"
#include "../../arch/operands/immediate.h"
#include "../../arch/operands/target.h"
#include "../../arch/operands/targetable.h"



/* Complète un désassemblage accompli pour une instruction. */
static void convert_immediate_into_target(GArchInstruction *, size_t, GBinFormat *);



/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction désassemblée à traiter.                  *
*                prev  = instruction précédente.                              *
*                                                                             *
*  Description : Rétablit un lien naturel coupé par un autre lien.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void establish_natural_link(GArchInstruction *instr, GArchInstruction *prev)
{
    size_t count;                           /* Nbre de sources affichées   */
    bool has_src;                           /* Présence de sources ?       */
    const instr_link_t *other;              /* Instruction diverse liée    */
    size_t i;                               /* Boucle de parcours          */
    bool need;                              /* Besoin exprimé pour ce lien */

    /**
     * Si rien ne vient séparer les deux instructions,
     * on ne peut pas créer de lien plus naturel que l'existant.
     */

    g_arch_instruction_lock_src(instr);

    count = g_arch_instruction_count_sources(instr);

    has_src = false;

    for (i = 0; i < count && !has_src; i++)
    {
        other = g_arch_instruction_get_source(instr, i);

        if (other->type != ILT_REF)
            has_src = true;

        unref_instr_link(other);

    }

    g_arch_instruction_unlock_src(instr);

    if (!has_src)
        return;

    /**
     * Si on se trouve à une extrémité, on ne se lie pas
     * avec le voisin.
     */

    if (g_arch_instruction_get_flags(prev) & AIF_RETURN_POINT)
        return;

    if (g_arch_instruction_get_flags(instr) & AIF_ROUTINE_START)
        return;

    /**
     * On s'assure que le lien naturel est nécessaire et qu'il n'est pas
     * déjà en place.
     */

    g_arch_instruction_lock_dest(prev);

    count = g_arch_instruction_count_destinations(prev);

    need = true;

    for (i = 0; i < count && need; i++)
    {
        other = g_arch_instruction_get_destination(prev, i);

        switch (other->type)
        {
            case ILT_EXEC_FLOW:
                need = false;
                break;

            case ILT_JUMP:
            case ILT_CASE_JUMP:
                need = false;
                break;

            case ILT_JUMP_IF_TRUE:
            case ILT_JUMP_IF_FALSE:
                need = (other->linked != instr);
                break;

            default:
                break;

        }

        unref_instr_link(other);

    }

    g_arch_instruction_unlock_dest(prev);

    if (need)
    {
        /* Vérification de la cohérence de l'ensemble */
#ifndef NDEBUG

        g_arch_instruction_lock_src(instr);
        count = g_arch_instruction_count_sources(instr);

        for (i = 0; i < count; i++)
        {
            other = g_arch_instruction_get_source(instr, i);

            switch (other->type)
            {
                case ILT_EXEC_FLOW:
                    assert(false);
                    break;

                case ILT_JUMP:
                case ILT_CASE_JUMP:
                case ILT_JUMP_IF_TRUE:
                case ILT_JUMP_IF_FALSE:
                case ILT_LOOP:
                case ILT_CATCH_EXCEPTION:
                    assert(other->linked != prev);
                    break;

                default:
                    break;

            }

            unref_instr_link(other);

        }

        g_arch_instruction_unlock_src(instr);

#endif

        g_arch_instruction_link_with(prev, instr, ILT_EXEC_FLOW);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr  = instruction désassemblée à traiter.                 *
*                index  = indice de l'opérande à traiter.                     *
*                format = accès aux données du binaire d'origine.             *
*                                                                             *
*  Description : Complète un désassemblage accompli pour une instruction.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void convert_immediate_into_target(GArchInstruction *instr, size_t index, GBinFormat *format)
{
    GArchOperand *op;                       /* Opérande numérique en place */
    GImmOperand *imm;                       /* Version native de l'opérande*/
    virt_t addr;                            /* Adresse visée par le saut   */
    MemoryDataSize msize;                   /* Taille de l'opérande        */
    vmpa2t target;                          /* Défination finale précise   */
    GTargetOperand *new;                    /* Instruction de ciblage      */

    op = _g_arch_instruction_get_operand(instr, index);

    if (!G_IS_IMM_OPERAND(op))
        goto ciit_done;

    imm = G_IMM_OPERAND(op);

    if (g_imm_operand_get_display(imm) != IOD_HEX)
        goto ciit_done;

    if (g_imm_operand_to_virt_t(imm, &addr))
    {
        msize = g_imm_operand_get_size(imm);

        if (g_exe_format_translate_address_into_vmpa(G_EXE_FORMAT(format), addr, &target))
        {
            new = G_TARGET_OPERAND(g_target_operand_new(msize, &target));

            if (!g_target_operand_resolve(new, format, false))
                g_object_unref(G_OBJECT(new));
            else
                _g_arch_instruction_replace_operand(instr, op, G_ARCH_OPERAND(new));

        }

    }

 ciit_done:

    g_object_unref(G_OBJECT(op));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr  = instruction désassemblée à traiter.                 *
*                format = accès aux données du binaire d'origine.             *
*                proc   = ensemble d'instructions à relier.                   *
*                                                                             *
*  Description : Complète un désassemblage accompli pour une instruction.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void establish_links_for_instruction(GArchInstruction *instr, GBinFormat *format, GArchProcessor *proc)
{
    bool skip;                              /* Saut des conversions        */
    size_t count;                           /* Nombre d'opérandes présents */
    size_t i;                               /* Boucle de parcours          */
    GArchOperand *op;                       /* Opérande numérique en place */
    const mrange_t *range;                  /* Emplacement de l'instruction*/
    vmpa2t addr;                            /* Localisation plus complète  */
    GArchInstruction *target;               /* Instruction visée au final  */

    if (G_IS_RAW_INSTRUCTION(instr))
        skip = g_raw_instruction_is_string(G_RAW_INSTRUCTION(instr));
    else
        skip = false;

    g_arch_instruction_lock_operands(instr);

    count = _g_arch_instruction_count_operands(instr);

    for (i = 0; i < count; i++)
    {
        if (!skip)
            convert_immediate_into_target(instr, i, format);

        op = _g_arch_instruction_get_operand(instr, i);
        if (!G_IS_TARGETABLE_OPERAND(op)) goto next_op;

        range = g_arch_instruction_get_range(instr);

        if (!g_targetable_operand_get_addr(G_TARGETABLE_OPERAND(op), get_mrange_addr(range), format, proc, &addr))
            goto next_op;

        target = g_arch_processor_find_instr_by_address(proc, &addr);

        if (target != NULL)
        {
            if (!g_arch_instruction_has_link_to(instr, target))
                g_arch_instruction_link_with(instr, target, ILT_REF);

            g_object_unref(G_OBJECT(target));

        }

    next_op:

        g_object_unref(G_OBJECT(op));

    }

    g_arch_instruction_unlock_operands(instr);

}
