
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
#include <stdio.h>


#include <i18n.h>
#include <arch/processor.h>
#include <arch/instructions/raw.h>
#include <arch/operands/immediate.h>
#include <arch/operands/register.h>
#include <common/extstr.h>
#include <format/known.h>
#include <format/format.h>
#include <format/preload.h>


#include "operands/it.h"
#include "operands/offset.h"
#include "operands/register.h"
#include "operands/reglist.h"
#include "../instruction.h"
#include "../register.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction ARMv7 à traiter.                       *
*                proc    = représentation de l'architecture utilisée.         *
*                context = contexte associé à la phase de désassemblage.      *
*                format  = acès aux données du binaire d'origine.             *
*                iset    = type de jeu d'instructions courant à faire suivre. *
*                                                                             *
*  Description : Complète un désassemblage accompli pour une instruction.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void help_fetching_with_instruction_b_with_orig(GArchInstruction *instr, GArchProcessor *proc, GArmV7Context *context, GExeFormat *format, ArmV7InstrSet iset)
{
    const mrange_t *range;                  /* Emplacementt d'instruction  */
    virt_t pc;                              /* Position dans l'exécution   */
    GImmOperand *op;                        /* Opérande numérique en place */
    int32_t offset;                         /* Décalage encodé en dur      */
    virt_t target;                          /* Adresse virtuelle visée     */

    range = g_arch_instruction_get_range(instr);

    pc = get_virt_addr(get_mrange_addr(range));




    switch (iset)
    {
        case AV7IS_ARM:
            pc += 8;
            break;
        case AV7IS_THUMB:
            pc += 4;
            break;
        default:
            assert(0);
            break;
    }



    //pc += get_mrange_length(range);

    op = G_IMM_OPERAND(g_arch_instruction_get_operand(instr, 0));

    if (g_imm_operand_get_value(op, MDS_32_BITS_SIGNED, &offset))
        g_imm_operand_set_value(op, MDS_32_BITS_UNSIGNED, pc + offset);

    else assert(0);

    g_object_unref(G_OBJECT(op));

    target = pc + offset;

    //g_armv7_context_define_encoding(context, target, iset);
    g_proc_context_push_drop_point(G_PROC_CONTEXT(context), DPL_OTHER, target, iset);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction ARMv7 à traiter.                       *
*                proc    = représentation de l'architecture utilisée.         *
*                context = contexte associé à la phase de désassemblage.      *
*                format  = acès aux données du binaire d'origine.             *
*                iset    = type de jeu d'instructions courant à faire suivre. *
*                                                                             *
*  Description : Complète un désassemblage accompli pour une instruction.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void help_fetching_with_instruction_bl_with_orig(GArchInstruction *instr, GArchProcessor *proc, GArmV7Context *context, GExeFormat *format, ArmV7InstrSet iset)
{
    const mrange_t *range;                  /* Emplacementt d'instruction  */
    virt_t pc;                              /* Position dans l'exécution   */
    GImmOperand *op;                        /* Opérande numérique en place */
    int32_t offset;                         /* Décalage encodé en dur      */
    virt_t target;                          /* Adresse virtuelle visée     */

    range = g_arch_instruction_get_range(instr);

    pc = get_virt_addr(get_mrange_addr(range));

    /**
     * Qu'on se trouve en mode Thumb ou ARM, l'instruction
     * ne peut qu'être encodée sur 4 octets.
     */

    assert(get_mrange_length(range) == 4);

    switch (iset)
    {
        case AV7IS_ARM:
            pc += 8;
            break;
        case AV7IS_THUMB:
            pc += 4;
            break;
        default:
            assert(0);
            break;
    }

    op = G_IMM_OPERAND(g_arch_instruction_get_operand(instr, 0));

    if (g_imm_operand_get_value(op, MDS_32_BITS_SIGNED, &offset))
        g_imm_operand_set_value(op, MDS_32_BITS_UNSIGNED, pc + offset);

    else assert(0);

    g_object_unref(G_OBJECT(op));

    target = pc + offset;

    //g_armv7_context_define_encoding(context, target, iset);
    g_proc_context_push_drop_point(G_PROC_CONTEXT(context), DPL_OTHER, target, iset);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction ARMv7 à traiter.                       *
*                proc    = représentation de l'architecture utilisée.         *
*                context = contexte associé à la phase de désassemblage.      *
*                format  = acès aux données du binaire d'origine.             *
*                iset    = type de jeu d'instructions courant à inverser.     *
*                                                                             *
*  Description : Complète un désassemblage accompli pour une instruction.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void help_fetching_with_instruction_blx_with_dest(GArchInstruction *instr, GArchProcessor *proc, GArmV7Context *context, GExeFormat *format, ArmV7InstrSet iset)
{
    const mrange_t *range;                  /* Emplacementt d'instruction  */
    virt_t pc;                              /* Position dans l'exécution   */
    GImmOperand *op;                        /* Opérande numérique en place */
    int32_t offset;                         /* Décalage encodé en dur      */
    virt_t target;                          /* Adresse virtuelle visée     */

    range = g_arch_instruction_get_range(instr);

    pc = get_virt_addr(get_mrange_addr(range));

    /**
     * Qu'on se trouve en mode Thumb ou ARM, l'instruction
     * ne peut qu'être encodée sur 4 octets.
     */

    assert(get_mrange_length(range) == 4);

    pc += 4;
    pc -= pc % 4;

    op = G_IMM_OPERAND(g_arch_instruction_get_operand(instr, 0));

    if (g_imm_operand_get_value(op, MDS_32_BITS_SIGNED, &offset))
        g_imm_operand_set_value(op, MDS_32_BITS_UNSIGNED, pc + offset);

    else assert(0);

    g_object_unref(G_OBJECT(op));

    target = pc + offset;

    //g_armv7_context_define_encoding(context, target, iset);
    g_proc_context_push_drop_point(G_PROC_CONTEXT(context), DPL_OTHER, target, iset);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction ARMv7 à traiter.                       *
*                proc    = représentation de l'architecture utilisée.         *
*                context = contexte associé à la phase de désassemblage.      *
*                format  = acès aux données du binaire d'origine.             *
*                iset    = type de jeu d'instructions courant à faire suivre. *
*                                                                             *
*  Description : Complète un désassemblage accompli pour une instruction.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void help_fetching_with_instruction_bx_with_orig(GArchInstruction *instr, GArchProcessor *proc, GArmV7Context *context, GExeFormat *format, ArmV7InstrSet iset)
{
    GArchOperand *op;                       /* Opérande numérique en place */
    GArmRegister *reg;                      /* Registre matériel manipulé  */
    bool is_pc;                             /* Nature de ce même registre  */
    const mrange_t *range;                  /* Emplacementt d'instruction  */
    virt_t pc;                              /* Position dans l'exécution   */

    op = g_arch_instruction_get_operand(instr, 0);
    assert(G_IS_REGISTER_OPERAND(op));

    /**
     * On ne sait agir qu'avec le seul contenu facilement prédictible : pc !
     */

    reg = G_ARM_REGISTER(g_register_operand_get_register(G_REGISTER_OPERAND(op)));

    is_pc = (g_arm_register_get_index(reg) == 15 /* pc */);

    g_object_unref(G_OBJECT(reg));

    if (!is_pc) goto hfwibwo_no_pc;

    /**
     * On bascule alors le mode de décodage à cette adresse...
     */

    range = g_arch_instruction_get_range(instr);

    pc = get_virt_addr(get_mrange_addr(range));

    switch (iset)
    {
        case AV7IS_ARM:
            pc += 8;
            //g_armv7_context_define_encoding(context, 
            g_proc_context_push_drop_point(G_PROC_CONTEXT(context), DPL_OTHER, pc, AV7IS_THUMB);
            break;
        case AV7IS_THUMB:
            pc += 4;
            //g_armv7_context_define_encoding(context, 
            g_proc_context_push_drop_point(G_PROC_CONTEXT(context), DPL_OTHER, pc, AV7IS_ARM);
            break;
        default:
            assert(0);
            break;
    }

 hfwibwo_no_pc:

    g_object_unref(G_OBJECT(op));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction ARMv7 à traiter.                       *
*                proc    = représentation de l'architecture utilisée.         *
*                context = contexte associé à la phase de désassemblage.      *
*                format  = acès aux données du binaire d'origine.             *
*                                                                             *
*  Description : Complète un désassemblage accompli pour une instruction.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void help_fetching_with_instruction_cb_n_z(GArchInstruction *instr, GArchProcessor *proc, GArmV7Context *context, GExeFormat *format)
{
    const mrange_t *range;                  /* Emplacementt d'instruction  */
    virt_t pc;                              /* Position dans l'exécution   */
    GImmOperand *op;                        /* Opérande numérique en place */
    uint32_t offset;                        /* Décalage encodé en dur      */
    virt_t target;                          /* Adresse virtuelle visée     */

    range = g_arch_instruction_get_range(instr);

    pc = get_virt_addr(get_mrange_addr(range));

    /**
     * En mode Thumb, pc a pour valeur l'adresse courante plus 4.
     */

    pc += 4;

    op = G_IMM_OPERAND(g_arch_instruction_get_operand(instr, 1));

    if (g_imm_operand_get_value(op, MDS_32_BITS_UNSIGNED, &offset))
        g_imm_operand_set_value(op, MDS_32_BITS_UNSIGNED, pc + offset);

    else assert(0);

    g_object_unref(G_OBJECT(op));

    target = pc + offset;

    //g_armv7_context_define_encoding(context, target, AV7IS_THUMB);
    g_proc_context_push_drop_point(G_PROC_CONTEXT(context), DPL_OTHER, target, AV7IS_THUMB);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction ARMv7 à traiter.                       *
*                proc    = représentation de l'architecture utilisée.         *
*                context = contexte associé à la phase de désassemblage.      *
*                format  = acès aux données du binaire d'origine.             *
*                iset    = type de jeu d'instructions courant.                *
*                                                                             *
*  Description : Complète un désassemblage accompli pour une instruction.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void help_fetching_with_instruction_ldr_literal_with_orig(GArchInstruction *instr, GArchProcessor *proc, GArmV7Context *context, GExeFormat *format, ArmV7InstrSet iset)
{
    const mrange_t *range;                  /* Emplacementt d'instruction  */
    phys_t phys_pc;                         /* Position dans l'exécution   */
    GArchOperand *op;                       /* Opérande de surcouche       */
    uint32_t offset;                        /* Décalage encodé en dur      */
    bool ret;                               /* Bilan d'une récupération    */
    off_t val_offset;                       /* Position de valeur à lire   */
    vmpa2t loaded_addr;                     /* Adresse de valeur chargée   */
    mrange_t loaded_range;                  /* Espace de chargement        */
    GBinFormat *base;                       /* version parente du format   */
    GBinContent *content;                   /* Contenu binaire à relire    */
    SourceEndian endian;                    /* Boutisme du format parent   */
    uint32_t target;                        /* Adresse virtuelle visée     */
    vmpa2t pos;                             /* Tête de lecture de valeur   */
    VMPA_BUFFER(loc);                       /* Adresse au format texte     */
    GPreloadInfo *info;                     /* Informations préchargées    */
    GArchInstruction *loaded;               /* Instruction de valeur       */
    bool inserted;                          /* Bilan d'une insertion       */
    char *desc;                             /* Description d'accompagnement*/
    size_t index;                           /* Indice d'un existant ?      */
    GDbComment *comment;                    /* Définition de commentaire   */
    GArchOperand *new;                      /* Instruction de ciblage      */

    /* Récupération de l'adresse visée par le chargement */

    range = g_arch_instruction_get_range(instr);

    phys_pc = get_phy_addr(get_mrange_addr(range));

    phys_pc &= ~3;
    //phys_pc = (phys_pc + 3) & ~3;

    switch (iset)
    {
        case AV7IS_ARM:
            phys_pc += 8;
            break;
        case AV7IS_THUMB:
            phys_pc += 4;
            break;
        default:
            assert(0);
            break;
    }

    g_arch_instruction_lock_operands(instr);

    op = _g_arch_instruction_get_operand(instr, 1);
    assert(G_IS_IMM_OPERAND(op));

    ret = g_imm_operand_get_value(G_IMM_OPERAND(op), MDS_32_BITS_UNSIGNED, &offset);
    if (!ret)
    {
        assert(0);
        g_object_unref(G_OBJECT(op));
        g_arch_instruction_unlock_operands(instr);
        return;
    }

    /* Transformations et conservation d'une position de chargement */

    val_offset = phys_pc + offset;

    if (!g_exe_format_translate_offset_into_vmpa(format, val_offset, &loaded_addr))
    {
        /**
         * Ce cas de figure correspond à la situation où une instruction "ldr"
         * tente de charger une valeur qui se trouve sur un segment qui n'est
         * pas chargé en mémoire par exemple.
         *
         * Dans la pratique, on pourrait parfois retrouver la valeur ciblée,
         * mais effectivement cette donnée n'est pas disponible au moment de
         * l'exécution.
         */

        g_arch_processor_add_error(proc, APE_DISASSEMBLY, get_mrange_addr(range),
                                   _("Unable to load a value which is not addressable"));

        g_object_unref(G_OBJECT(op));
        g_arch_instruction_unlock_operands(instr);
        return;
    }

    init_mrange(&loaded_range, &loaded_addr, 4);

    /* Lecture de la valeur vers laquelle renvoyer */

    base = G_BIN_FORMAT(format);

    content = g_known_format_get_content(G_KNOWN_FORMAT(base));

    endian = g_binary_format_get_endianness(base);

    copy_vmpa(&pos, &loaded_addr);

    ret = g_binary_content_read_u32(content, &pos, endian, &target);

    g_object_unref(G_OBJECT(content));

    if (!ret)
    {
        g_object_unref(G_OBJECT(op));
        g_arch_instruction_unlock_operands(instr);
        return;
    }

    /* Réalise l'intégration de la valeur chargée */

    copy_vmpa(&pos, &loaded_addr);

    info = G_PRELOAD_INFO(context);

    loaded = g_raw_instruction_new_from_value(&pos, MDS_32_BITS_UNSIGNED, target);

    inserted = g_preload_info_add_instruction(info, loaded);

    if (inserted)
    {
        /* Commentaire associé */

        vmpa2_virt_to_string(get_mrange_addr(range), MDS_32_BITS, loc, NULL);
        asprintf(&desc, _("Value used @ %s"), loc);

        g_preload_info_lock_comments(info);

        comment = g_preload_info_find_comment_at(info, &loaded_addr, &index);

        if (comment == NULL)
        {
            comment = g_db_comment_new(&loaded_addr, CET_INLINED, BLF_HAS_CODE, desc);
            g_db_item_add_flag(G_DB_ITEM(comment), DIF_VOLATILE);

            _g_preload_info_add_comment(info, comment);

        }

        else
        {
            desc = strprep(desc, "\n");
            desc = strprep(desc, g_db_comment_get_text(comment));

            g_object_unref(G_OBJECT(comment));

            comment = g_db_comment_new(&loaded_addr, CET_INLINED, BLF_HAS_CODE, desc);
            g_db_item_add_flag(G_DB_ITEM(comment), DIF_VOLATILE);

            g_preload_info_replace_comment_at(info, index, comment);

        }

        g_preload_info_unlock_comments(info);

        free(desc);

    }

    /* Mise à jour de l'affichage et conclusion */

    new = g_imm_operand_new_from_value(MDS_32_BITS_UNSIGNED, target);
    _g_arch_instruction_replace_operand(instr, op, new);

    g_object_unref(G_OBJECT(op));
    g_arch_instruction_unlock_operands(instr);



    //exit(0);



    //target = pc + offset;


    if (target & 0x1)
        iset = AV7IS_THUMB;
    //else
    //    iset = AV7IS_ARM;

    //g_armv7_context_define_encoding(context, target, AV7IS_THUMB);
    g_proc_context_push_drop_point(G_PROC_CONTEXT(context), DPL_OTHER, target, iset);


    //exit(0);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction ARMv7 à traiter.                       *
*                proc    = représentation de l'architecture utilisée.         *
*                context = contexte associé à la phase de désassemblage.      *
*                format  = acès aux données du binaire d'origine.             *
*                iset    = type de jeu d'instructions courant.                *
*                                                                             *
*  Description : Applique la mise à jour d'un registre après coup.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void apply_write_back(GArchInstruction *instr, GArchProcessor *proc, GArmV7Context *context, GExeFormat *format, ArmV7InstrSet iset)
{
    GArchOperand *op;                       /* Opérande de registre        */

    g_arch_instruction_lock_operands(instr);

    op = _g_arch_instruction_get_operand(instr, 0);
    assert(G_IS_ARMV7_REGISTER_OPERAND(op));

    g_armv7_register_operand_write_back(G_ARMV7_REGISTER_OPERAND(op), true);

    g_object_unref(G_OBJECT(op));

    g_arch_instruction_unlock_operands(instr);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction ARMv7 à traiter.                       *
*                proc    = représentation de l'architecture utilisée.         *
*                context = contexte associé à la phase de désassemblage.      *
*                format  = acès aux données du binaire d'origine.             *
*                iset    = type de jeu d'instructions courant.                *
*                                                                             *
*  Description : Applique la mise à jour d'un registre après coup au besoin.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void apply_write_back_from_registers(GArchInstruction *instr, GArchProcessor *proc, GArmV7Context *context, GExeFormat *format, ArmV7InstrSet iset)
{
    GArchOperand *op;                       /* Opérande à manipuler        */
    GArmV7RegisterOperand *regop;           /* Opérande de registre        */
    GArchRegister *reg_ref;                 /* Registre de référence       */
    GArmV7RegListOperand *reglist;          /* Opérande de liste de reg.   */
    size_t count;                           /* Taille de la liste          */
    bool inside;                            /* Intersection de registres   */
    size_t i;                               /* Boucle de parcours          */
    GArmV7Register *reg;                    /* Registre à analyser         */

    g_arch_instruction_lock_operands(instr);

    op = _g_arch_instruction_get_operand(instr, 0);
    assert(G_IS_ARMV7_REGISTER_OPERAND(op));

    regop = G_ARMV7_REGISTER_OPERAND(op);

    reg_ref = g_register_operand_get_register(G_REGISTER_OPERAND(regop));

    op = _g_arch_instruction_get_operand(instr, 1);
    assert(G_IS_ARMV7_REGLIST_OPERAND(op));

    reglist = G_ARMV7_REGLIST_OPERAND(op);

    count = g_armv7_reglist_count_registers(reglist);

    inside = false;

    for (i = 0; i < count && !inside; i++)
    {
        reg = g_armv7_reglist_operand_get_register(reglist, i);

        inside = (g_arch_register_compare(reg_ref, G_ARCH_REGISTER(reg)) == 0);

        g_object_unref(G_OBJECT(reg));

    }

    if (!inside)
        g_armv7_register_operand_write_back(regop, true);

    g_object_unref(G_OBJECT(regop));
    g_object_unref(G_OBJECT(reglist));

    g_arch_instruction_unlock_operands(instr);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction ARMv7 à traiter.                       *
*                proc    = représentation de l'architecture utilisée.         *
*                context = contexte associé à la phase de désassemblage.      *
*                format  = acès aux données du binaire d'origine.             *
*                iset    = type de jeu d'instructions courant.                *
*                                                                             *
*  Description : Construit un suffixe adapté à une instruction IT.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void build_it_instruction_suffix(GArchInstruction *instr, GArchProcessor *proc, GArmV7Context *context, GExeFormat *format, ArmV7InstrSet iset)
{
    GArchOperand *op;                       /* Opérande à manipuler        */
    GArmV7ITCondOperand *itcond;            /* Opérande de l'instruction   */
    uint8_t firstcond;                      /* Indication sur la condition */
    uint8_t mask;                           /* Masque d'application        */
    char suffix[4];                         /* Suffixe à attribuer         */

    g_arch_instruction_lock_operands(instr);

    op = _g_arch_instruction_get_operand(instr, 0);
    assert(G_IS_ARMV7_ITCOND_OPERAND(op));

    itcond = G_ARMV7_ITCOND_OPERAND(op);

    firstcond = g_armv7_itcond_operand_get_firstcond(itcond);
    mask = g_armv7_itcond_operand_get_mask(itcond);

    firstcond &= 0x1;

    if ((mask & 0x7) == 0x4)
    {
        suffix[0] = ((mask & 0x8) >> 3) == firstcond ? 't' : 'e';
        suffix[1] = '\0';
    }

    else if ((mask & 0x3) == 0x2)
    {
        suffix[0] = ((mask & 0x8) >> 3) == firstcond ? 't' : 'e';
        suffix[1] = ((mask & 0x4) >> 2) == firstcond ? 't' : 'e';
        suffix[2] = '\0';
    }

    else if ((mask & 0x1) == 0x1)
    {
        suffix[0] = ((mask & 0x8) >> 3) == firstcond ? 't' : 'e';
        suffix[1] = ((mask & 0x4) >> 2) == firstcond ? 't' : 'e';
        suffix[2] = ((mask & 0x2) >> 1) == firstcond ? 't' : 'e';
        suffix[3] = '\0';
    }

    else
        suffix[0] = '\0';

    if (suffix[0] != '\0')
        g_arm_instruction_extend_keyword(G_ARM_INSTRUCTION(instr), suffix);

    g_object_unref(G_OBJECT(itcond));

    g_arch_instruction_unlock_operands(instr);

}
