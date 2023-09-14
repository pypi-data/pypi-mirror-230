
/* Chrysalide - Outil d'analyse de fichiers binaires
 * thumb_32.c - désassemblage des instructions ARMv7 Thumb 32 bits
 *
 * Copyright (C) 2017-2018 Cyrille Bagard
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


#include "thumb_32.h"


#include <stdint.h>


#include <arch/instructions/undefined.h>
#include <common/bconst.h>


#include "opcodes/thumb_32_opcodes.h"
#include "opcodes/opcodes_tmp_thumb_32.h"



/* Désassemble une instruction ARMv7 liées au chapitre A6.3.1. */
static GArchInstruction *process_armv7_thumb_32_data_processing_modified_immediate(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A6.3.3. */
static GArchInstruction *process_armv7_thumb_32_data_processing_plain_binary_immediate(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A6.3.4. */
static GArchInstruction *process_armv7_thumb_32_branches_and_miscellaneous_control(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A6.3.4b. */
static GArchInstruction *process_armv7_thumb_32_change_processor_state_and_hints(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A6.3.4t. */
static GArchInstruction *process_armv7_thumb_32_miscellaneous_control_instructions(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A6.3.5. */
static GArchInstruction *process_armv7_thumb_32_load_store_multiple(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A6.3.6. */
static GArchInstruction *process_armv7_thumb_32_load_store_dual_load_store_exclusive_table_branch(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A6.3.7. */
static GArchInstruction *process_armv7_thumb_32_load_word(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A6.3.8. */
static GArchInstruction *process_armv7_thumb_32_load_halfword_memory_hints(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A6.3.9. */
static GArchInstruction *process_armv7_thumb_32_load_byte_memory_hints(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A6.3.10. */
static GArchInstruction *process_armv7_thumb_32_store_single_data_item(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A6.3.11. */
static GArchInstruction *process_armv7_thumb_32_data_processing_shifted_register(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A6.3.11b. */
static GArchInstruction *process_armv7_thumb_32_move_register_and_immediate_shifts(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A6.3.12. */
static GArchInstruction *process_armv7_thumb_32_data_processing_register(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A6.3.13. */
static GArchInstruction *process_armv7_thumb_32_parallel_addition_and_subtraction_signed(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A6.3.14. */
static GArchInstruction *process_armv7_thumb_32_parallel_addition_and_subtraction_unsigned(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A6.3.15. */
static GArchInstruction *process_armv7_thumb_32_miscellaneous_operations(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A6.3.16. */
static GArchInstruction *process_armv7_thumb_32_multiply_multiply_accumulate_and_absolute_difference(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A6.3.17. */
static GArchInstruction *process_armv7_thumb_32_long_multiply_long_multiply_accumulate_and_divide(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A6.3.18. */
static GArchInstruction *process_armv7_thumb_32_coprocessor_advanced_simd_and_floating_point_instructions(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A7.4. */
static GArchInstruction *process_armv7_thumb_32_advanced_simd_data_processing_instructions(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A7.4.1. */
static GArchInstruction *process_armv7_thumb_32_three_registers_of_the_same_length(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A7.4.2. */
static GArchInstruction *process_armv7_thumb_32_three_registers_of_different_lengths(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A7.4.3. */
static GArchInstruction *process_armv7_thumb_32_two_registers_and_a_scalar(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A7.4.4. */
static GArchInstruction *process_armv7_thumb_32_two_registers_and_a_shift_amount(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A7.4.5. */
static GArchInstruction *process_armv7_thumb_32_two_registers_miscellaneous(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A7.4.6. */
static GArchInstruction *process_armv7_thumb_32_one_register_and_a_modified_immediate_value(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A7.5. */
static GArchInstruction *process_armv7_thumb_32_floating_point_data_processing_instructions(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A7.6. */
static GArchInstruction *process_armv7_thumb_32_extension_register_load_store_instructions(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A7.7. */
static GArchInstruction *process_armv7_thumb_32_advanced_simd_element_or_structure_load_store_instructions(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A7.8. */
static GArchInstruction *process_armv7_thumb_32_8_16_and_32_bit_transfer_between_arm_core_and_extension_registers(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A7.9. */
static GArchInstruction *process_armv7_thumb_32_64_bit_transfers_between_arm_core_and_extension_registers(uint32_t);



/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A6.3.    *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *process_armv7_thumb_32_instruction_set_encoding(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t op1;                           /* Champ 'op1' à retrouver     */
    uint32_t op2;                           /* Champ 'op2' à retrouver     */
    uint32_t op;                            /* Champ 'op' à retrouver      */

    /**
     * Suit les directives de :
     * § A6.3 32-bit Thumb instruction encoding
     */

    if (((raw >> 29) & b111) != b111) return NULL;

    result = NULL;

    op1 = (raw >> 27) & b11;
    op2 = (raw >> 20) & b1111111;
    op = (raw >> 15) & b1;

    switch (op1)
    {
        case b01:

            if ((op2 & b1100100) == b0000000)
                result = process_armv7_thumb_32_load_store_multiple(raw);

            else if ((op2 & b1100100) == b0000100)
                result = process_armv7_thumb_32_load_store_dual_load_store_exclusive_table_branch(raw);

            else if ((op2 & b1100000) == b0100000)
                result = process_armv7_thumb_32_data_processing_shifted_register(raw);

            else if ((op2 & b1000000) == b1000000)
                result = process_armv7_thumb_32_coprocessor_advanced_simd_and_floating_point_instructions(raw);

            break;

        case b10:

            if (op == 1)
                result = process_armv7_thumb_32_branches_and_miscellaneous_control(raw);

            else
            {
                if ((op2 & b0100000) == b0000000)
                    result = process_armv7_thumb_32_data_processing_modified_immediate(raw);

                else if ((op2 & b0100000) == b0100000)
                    result = process_armv7_thumb_32_data_processing_plain_binary_immediate(raw);

            }

            break;

        case b11:

            if ((op2 & b1110001) == b0000000)
                result = process_armv7_thumb_32_store_single_data_item(raw);

            else if ((op2 & b1100111) == b0000001)
                result = process_armv7_thumb_32_load_byte_memory_hints(raw);

            else if ((op2 & b1100111) == b0000011)
                result = process_armv7_thumb_32_load_halfword_memory_hints(raw);

            else if ((op2 & b1100111) == b0000101)
                result = process_armv7_thumb_32_load_word(raw);

            else if ((op2 & b1100111) == b0000111)
                result = g_undef_instruction_new(IEB_UNDEFINED);

            else if ((op2 & b1110001) == b0010000)
                result = process_armv7_thumb_32_advanced_simd_element_or_structure_load_store_instructions(raw);

            else if ((op2 & b1110000) == b0100000)
                result = process_armv7_thumb_32_data_processing_register(raw);

            else if ((op2 & b1111000) == b0110000)
                result = process_armv7_thumb_32_multiply_multiply_accumulate_and_absolute_difference(raw);

            else if ((op2 & b1111000) == b0111000)
                result = process_armv7_thumb_32_long_multiply_long_multiply_accumulate_and_divide(raw);

            else if ((op2 & b1000000) == b1000000)
                result = process_armv7_thumb_32_coprocessor_advanced_simd_and_floating_point_instructions(raw);

            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A6.3.1.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_data_processing_modified_immediate(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t op;                            /* Champ 'op' à retrouver      */
    uint32_t rn;                            /* Champ 'rn' à retrouver      */
    uint32_t rds;                           /* Champ 'rds' à retrouver     */

    /**
     * Suit les directives de :
     * § A6.3.1 Data-processing (modified immediate)
     */

    if ((raw & 0xfa008000) != 0xf0000000) return NULL;

    result = NULL;

    op = (raw >> 21) & b1111;
    rn = (raw >> 16) & b1111;
    rds = (((raw >> 8) & b1111) << 1) | ((raw >> 20) & b1);

    switch (op)
    {
        case b0000:

            if (rds == b11111)
                result = armv7_read_thumb_32_instr_a8_tst_immediate(raw);

            else
                result = armv7_read_thumb_32_instr_a8_and_immediate(raw);

            break;

        case b0001:
            result = armv7_read_thumb_32_instr_a8_bic_immediate(raw);
            break;

        case b0010:

            if (rn == b1111)
                result = armv7_read_thumb_32_instr_a8_mov_immediate(raw);

            else
                result = armv7_read_thumb_32_instr_a8_orr_immediate(raw);

            break;

        case b0011:

            if (rn == b1111)
                result = armv7_read_thumb_32_instr_a8_mvn_immediate(raw);

            else
                result = armv7_read_thumb_32_instr_a8_orn_immediate(raw);

            break;

        case b0100:

            if (rds == b11111)
                result = armv7_read_thumb_32_instr_a8_teq_immediate(raw);

            else
                result = armv7_read_thumb_32_instr_a8_eor_immediate(raw);

            break;

        case b1000:

            if (rds == b11111)
                result = armv7_read_thumb_32_instr_a8_cmn_immediate(raw);

            else
                result = armv7_read_thumb_32_instr_a8_add_immediate_thumb(raw);

            break;

        case b1010:
            result = armv7_read_thumb_32_instr_a8_adc_immediate(raw);
            break;

        case b1011:
            result = armv7_read_thumb_32_instr_a8_sbc_immediate(raw);
            break;

        case b1101:

            if (rds == b11111)
                result = armv7_read_thumb_32_instr_a8_cmp_immediate(raw);

            else
                result = armv7_read_thumb_32_instr_a8_sub_immediate_thumb(raw);

            break;

        case b1110:
            result = armv7_read_thumb_32_instr_a8_rsb_immediate(raw);
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A6.3.3.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_data_processing_plain_binary_immediate(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t op;                            /* Champ 'op' à retrouver      */
    uint32_t rn;                            /* Champ 'rn' à retrouver      */

    /**
     * Suit les directives de :
     * § A6.3.3 Data-processing (plain binary immediate)
     */

    if ((raw & 0xfa008000) != 0xf2000000) return NULL;

    result = NULL;

    op = (raw >> 20) & b11111;
    rn = (raw >> 16) & b1111;

    switch (op)
    {
        case b00000:

            if (rn == b1111)
                result = armv7_read_thumb_32_instr_a8_adr(raw);

            else
                result = armv7_read_thumb_32_instr_a8_add_immediate_thumb(raw);

            break;

        case b00100:
            result = armv7_read_thumb_32_instr_a8_mov_immediate(raw);
            break;

        case b01010:

            if (rn == b11111)
                result = armv7_read_thumb_32_instr_a8_adr(raw);

            else
                result = armv7_read_thumb_32_instr_a8_sub_immediate_thumb(raw);

            break;

        case b01100:
            result = armv7_read_thumb_32_instr_a8_movt(raw);
            break;

        case b10000:
            result = armv7_read_thumb_32_instr_a8_ssat(raw);
            break;

        case b10010:

            if ((raw & 0x000070c0) != 0)
                result = armv7_read_thumb_32_instr_a8_ssat(raw);

            else
                result = armv7_read_thumb_32_instr_a8_ssat16(raw);

            break;

        case b10100:
            result = armv7_read_thumb_32_instr_a8_sbfx(raw);
            break;

        case b10110:

            if (rn == b11111)
                result = armv7_read_thumb_32_instr_a8_bfc(raw);

            else
                result = armv7_read_thumb_32_instr_a8_bfi(raw);

            break;

        case b11000:
            result = armv7_read_thumb_32_instr_a8_usat(raw);
            break;

        case b11010:

            if ((raw & 0x000070c0) != 0)
                result = armv7_read_thumb_32_instr_a8_usat(raw);

            else
                result = armv7_read_thumb_32_instr_a8_usat16(raw);

            break;

        case b11100:
            result = armv7_read_thumb_32_instr_a8_ubfx(raw);
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A6.3.4.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_branches_and_miscellaneous_control(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t op;                            /* Champ 'op' à retrouver      */
    uint32_t op1;                           /* Champ 'op1' à retrouver     */
    uint32_t op2;                           /* Champ 'op2' à retrouver     */
    uint32_t imm8;                          /* Champ 'imm8' à retrouver    */

    /**
     * Suit les directives de :
     * § A6.3.4 Branches and miscellaneous control
     */

    if ((raw & 0xf8000000) != 0xf0000000) return NULL;

    result = NULL;

    op = (raw >> 20) & b1111111;
    op1 = (raw >> 12) & b111;
    op2 = (raw >> 8) & b1111;
    imm8 = (raw >> 0) & b11111111;

    if (op1 == b000 && op == b1111110)
        result = armv7_read_thumb_32_instr_b9_hvc(raw);

    else if (op1 == b000 && op == b1111111)
        result = armv7_read_thumb_32_instr_b9_smc_previously_smi(raw);

    else if ((op1 & b101) == b000)
    {
        if ((op & b0111000) != b0111000)
            result = armv7_read_thumb_32_instr_a8_b(raw);

        else if ((imm8 & b00100000) == b00100000 && (op & b1111110) == b0111000)
            result = armv7_read_thumb_32_instr_b9_msr_banked_register(raw);

        else if ((imm8 & b00100000) == b00000000 && op == b0111000 && (op2 & b0011) == b0000)
            result = armv7_read_thumb_32_instr_a8_msr_register(raw);

        else if ((imm8 & b00100000) == b00000000 && op == b0111000 && (op2 & b0011) == b0001)
            result = armv7_read_thumb_32_instr_b9_msr_register(raw);

        else if ((imm8 & b00100000) == b00000000 && op == b0111000 && (op2 & b0010) == b0010)
            result = armv7_read_thumb_32_instr_b9_msr_register(raw);

        else if ((imm8 & b00100000) == b00000000 && op == b0111001)
            result = armv7_read_thumb_32_instr_b9_msr_register(raw);

        else if (op == b0111010)
            result = process_armv7_thumb_32_change_processor_state_and_hints(raw);

        else if (op == b0111011)
            result = process_armv7_thumb_32_miscellaneous_control_instructions(raw);

        else if (op == b0111100)
            result = armv7_read_thumb_32_instr_a8_bxj(raw);

        else if (imm8 == b00000000 && op == b0111101)
            result = armv7_read_thumb_32_instr_b9_eret(raw);

        else if (imm8 != b00000000 && op == b0111101)
            result = armv7_read_thumb_32_instr_b9_subs_pc_lr_thumb(raw);

        else if ((imm8 & b00100000) == b00100000 && (op & b1111110) == b0111110)
            result = armv7_read_thumb_32_instr_b9_mrs_banked_register(raw);

        else if ((imm8 & b00100000) == b00000000 && op == b0111110)
            result = armv7_read_thumb_32_instr_a8_mrs(raw);

        else if ((imm8 & b00100000) == b00000000 && op == b0111111)
            result = armv7_read_thumb_32_instr_b9_mrs(raw);

    }

    else if ((op1 & b101) == b001)
        result = armv7_read_thumb_32_instr_a8_b(raw);

    else if (op1 == b010 && op == b1111111)
        result = armv7_read_thumb_32_instr_a8_udf(raw);

    else if ((op1 & b101) == b100)
        result = armv7_read_thumb_32_instr_a8_bl_blx_immediate(raw);

    else if ((op1 & b101) == b101)
        result = armv7_read_thumb_32_instr_a8_bl_blx_immediate(raw);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 classique.                 *
*                                                                             *
*  Retour      : Désassemble une instruction ARMv7 liées au chapitre A6.3.4b. *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_change_processor_state_and_hints(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t op1;                           /* Champ 'op1' à retrouver     */
    uint32_t op2;                           /* Champ 'op2' à retrouver     */

    /**
     * Suit les directives de :
     * § A6.3.4 Branches and miscellaneous control
     *    |-> Change Processor State, and hints
     */

    if ((raw & 0xfff0d000) != 0xf3a08000) return NULL;

    result = NULL;

    op1 = (raw >> 8) & b111;
    op2 = (raw >> 0) & b11111111;

    if (op1 != b000)
        result = armv7_read_thumb_32_instr_b9_cps_thumb(raw);

    else
    {
        if (op2 == b00000000)
            result = armv7_read_thumb_32_instr_a8_nop(raw);

        else if (op2 == b00000001)
            result = armv7_read_thumb_32_instr_a8_yield(raw);

        else if (op2 == b00000010)
            result = armv7_read_thumb_32_instr_a8_wfe(raw);

        else if (op2 == b00000011)
            result = armv7_read_thumb_32_instr_a8_wfi(raw);

        else if (op2 == b00000100)
            result = armv7_read_thumb_32_instr_a8_sev(raw);

        else if ((op2 & b11110000) == b11110000)
            result = armv7_read_thumb_32_instr_a8_dbg(raw);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A6.3.4t. *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_miscellaneous_control_instructions(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t op;                            /* Champ 'op' à retrouver      */

    /**
     * Suit les directives de :
     * § A6.3.4 Branches and miscellaneous control
     *    |-> Miscellaneous control instructions
     */

    if ((raw & 0xfff0d000) != 0xf3b08000) return NULL;

    result = NULL;

    op = (raw >> 4) & b1111;

    switch (op)
    {
        case b0000:
            result = armv7_read_thumb_32_instr_a9_enterx_leavex(raw);
            break;

        case b0001:
            result = armv7_read_thumb_32_instr_a9_enterx_leavex(raw);
            break;

        case b0010:
            result = armv7_read_thumb_32_instr_a8_clrex(raw);
            break;

        case b0100:
            result = armv7_read_thumb_32_instr_a8_dsb(raw);
            break;

        case b0101:
            result = armv7_read_thumb_32_instr_a8_dmb(raw);
            break;

        case b0110:
            result = armv7_read_thumb_32_instr_a8_isb(raw);
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A6.3.5.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_load_store_multiple(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t op;                            /* Champ 'op' à retrouver      */
    uint32_t l;                             /* Champ 'l' à retrouver       */
    uint32_t wrn;                           /* Champ 'wrn' à retrouver     */

    /**
     * Suit les directives de :
     * § A6.3.5 Load/store multiple
     */

    if ((raw & 0xfe400000) != 0xe8000000) return NULL;

    result = NULL;

    op = (raw >> 23) & b11;
    l = (raw >> 20) & b1;
    wrn = (((raw >> 21) & b1) << 4) | ((raw >> 16) & b1111);

    switch (op)
    {
        case b00:

            if (l == b0)
                result = armv7_read_thumb_32_instr_b9_srs_thumb(raw);

            else
                result = armv7_read_thumb_32_instr_b9_rfe(raw);

            break;

        case b01:

            if (l == b0)
                result = armv7_read_thumb_32_instr_a8_stm_stmia_stmea(raw);

            else
            {
                if (wrn == b11101)
                    result = armv7_read_thumb_32_instr_a8_pop_thumb(raw);

                else
                    result = armv7_read_thumb_32_instr_a8_ldm_ldmia_ldmfd_thumb(raw);

            }

            break;

        case b10:

            if (l == b0)
            {
                if (wrn == b11101)
                    result = armv7_read_thumb_32_instr_a8_push(raw);

                else
                    result = armv7_read_thumb_32_instr_a8_stmdb_stmfd(raw);

            }

            else
                result = armv7_read_thumb_32_instr_a8_ldmdb_ldmea(raw);

            break;

        case b11:

            if (l == b0)
                result = armv7_read_thumb_32_instr_b9_srs_thumb(raw);

            else
                result = armv7_read_thumb_32_instr_b9_rfe(raw);

            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A6.3.6.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_load_store_dual_load_store_exclusive_table_branch(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t op1;                           /* Champ 'op1' à retrouver     */
    uint32_t op2;                           /* Champ 'op2' à retrouver     */
    uint32_t rn;                            /* Champ 'rn' à retrouver      */
    uint32_t op3;                           /* Champ 'op3' à retrouver     */

    /**
     * Suit les directives de :
     * § A6.3.6 Load/store dual, load/store exclusive, table branch
     */

    if ((raw & 0xfe400000) != 0xe8400000) return NULL;

    result = NULL;

    op1 = (raw >> 23) & 0x3;
    op2 = (raw >> 20) & 0x3;
    rn = (raw >> 16) & 0xf;
    op3 = (raw >> 4) & 0xf;

    if (op1 == b00 && op2 == b00)
        result = armv7_read_thumb_32_instr_a8_strex(raw);

    else if (op1 == b00 && op2 == b01)
        result = armv7_read_thumb_32_instr_a8_ldrex(raw);

    else if ((op1 & b10) == b00 && op2 == b10)
        result = armv7_read_thumb_32_instr_a8_strd_immediate(raw);

    else if ((op1 & b10) == b10 && (op2 & b01) == b00)
        result = armv7_read_thumb_32_instr_a8_strd_immediate(raw);

    else if ((op1 & b10) == b00 && op2 == b11)
    {
        if (rn != b1111)
            result = armv7_read_thumb_32_instr_a8_ldrd_immediate(raw);

        else/* if (rn == b1111)*/
            result = armv7_read_thumb_32_instr_a8_ldrd_literal(raw);

    }

    else if ((op1 & b10) == b10 && (op2 & b01) == b01)
    {
        if (rn != b1111)
            result = armv7_read_thumb_32_instr_a8_ldrd_immediate(raw);

        else/* if (rn == b1111)*/
            result = armv7_read_thumb_32_instr_a8_ldrd_literal(raw);

    }

    else if (op1 == b01 && op2 == b00)
        switch (op3)
        {
            case b0100:
                result = armv7_read_thumb_32_instr_a8_strexb(raw);
                break;

            case b0101:
                result = armv7_read_thumb_32_instr_a8_strexh(raw);
                break;

            case b0111:
                result = armv7_read_thumb_32_instr_a8_strexd(raw);
                break;

        }

    else if (op1 == b01 && op2 == b01)
        switch (op3)
        {
            case b0000:
                result = armv7_read_thumb_32_instr_a8_tbb_tbh(raw);
                break;

            case b0001:
                result = armv7_read_thumb_32_instr_a8_tbb_tbh(raw);
                break;

            case b0100:
                result = armv7_read_thumb_32_instr_a8_ldrexb(raw);
                break;

            case b0101:
                result = armv7_read_thumb_32_instr_a8_ldrexh(raw);
                break;

            case b0111:
                result = armv7_read_thumb_32_instr_a8_ldrexd(raw);
                break;

        }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A6.3.7.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_load_word(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t op1;                           /* Champ 'op1' à retrouver     */
    uint32_t rn;                            /* Champ 'rn' à retrouver      */
    uint32_t op2;                           /* Champ 'op2' à retrouver     */

    /**
     * Suit les directives de :
     * § A6.3.7 Load word
     */

    if ((raw & 0xfe700000) != 0xf8500000) return NULL;

    result = NULL;

    op1 = (raw >> 23) & b11;
    rn = (raw >> 16) & b1111;
    op2 = (raw >> 6) & b111111;

    switch (op1)
    {
        case b00:

            if (op2 == b000000 && rn != b1111)
                result = armv7_read_thumb_32_instr_a8_ldr_register_thumb(raw);

            else if ((op2 & b100100) == b100100 && rn != b1111)
                result = armv7_read_thumb_32_instr_a8_ldr_immediate_thumb(raw);

            else if ((op2 & b111100) == b110000 && rn != b1111)
                result = armv7_read_thumb_32_instr_a8_ldr_immediate_thumb(raw);

            else if ((op2 & b111100) == b111000 && rn != b1111)
                result = armv7_read_thumb_32_instr_a8_ldrt(raw);

            break;

        case b01:
            if (rn != b1111)
                result = armv7_read_thumb_32_instr_a8_ldr_immediate_thumb(raw);
            break;

    }

    if (result == NULL && (op1 & b10) == b00 && rn == b1111)
        result = armv7_read_thumb_32_instr_a8_ldr_literal(raw);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A6.3.8.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_load_halfword_memory_hints(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t op1;                           /* Champ 'op1' à retrouver     */
    uint32_t rn;                            /* Champ 'rn' à retrouver      */
    uint32_t rt;                            /* Champ 'rt' à retrouver      */
    uint32_t op2;                           /* Champ 'op2' à retrouver     */

    /**
     * Suit les directives de :
     * § A6.3.8 Load halfword, memory hints
     */

    if ((raw & 0xfe700000) != 0xf8300000) return NULL;

    result = NULL;

    op1 = (raw >> 23) & 0x3;
    rn = (raw >> 16) & 0xf;
    rt = (raw >> 12) & 0xf;
    op2 = (raw >> 6) & 0x3f;

    if (rn == b1111)
    {
        if ((op1 & b10) == b00)
        {
            if (rt != b1111)
                result = armv7_read_thumb_32_instr_a8_ldrh_literal(raw);

            else/* if (rt == b1111)*/
                result = armv7_read_thumb_32_instr_a8_pld_literal(raw);

        }

        else/* if ((op1 & b10) == b10)*/
        {
            if (rt != b1111)
                result = armv7_read_thumb_32_instr_a8_ldrsh_literal(raw);

            else/* if (rt == b1111)*/
                result = g_undef_instruction_new(IEB_NOP);

        }

    }

    else/* if (rn != b1111)*/
    {
        if (op1 == b00)
        {
            if ((op2 & b100100) == b100100)
                result = armv7_read_thumb_32_instr_a8_ldrh_immediate_thumb(raw);

            else if ((op2 & b111100) == b110000 && rt != b1111)
                result = armv7_read_thumb_32_instr_a8_ldrh_immediate_thumb(raw);

            else if (op2 == b000000 && rt != b1111)
                result = armv7_read_thumb_32_instr_a8_ldrh_register(raw);

            else if ((op2 & b111100) == b111000)
                result = armv7_read_thumb_32_instr_a8_ldrht(raw);

            else if (op2 == b000000 && rt == b1111)
                result = armv7_read_thumb_32_instr_a8_pld_pldw_register(raw);

            else if ((op2 & b111100) == b110000 && rt == b1111)
                result = armv7_read_thumb_32_instr_a8_pld_pldw_immediate(raw);

        }

        else if (op1 == b01)
        {
            if (rt != b1111)
                result = armv7_read_thumb_32_instr_a8_ldrh_immediate_thumb(raw);

            else/* if (rt == b1111)*/
                result = armv7_read_thumb_32_instr_a8_pld_pldw_immediate(raw);

        }

        else if (op1 == b10)
        {
            if ((op2 & b100100) == b100100)
                result = armv7_read_thumb_32_instr_a8_ldrsh_immediate(raw);

            else if ((op2 & b111100) == b110000 && rt != b1111)
                result = armv7_read_thumb_32_instr_a8_ldrsh_immediate(raw);

            else if (op2 == b000000 && rt != b1111)
                result = armv7_read_thumb_32_instr_a8_ldrsh_register(raw);

            else if ((op2 & b111100) == b111000)
                result = armv7_read_thumb_32_instr_a8_ldrsht(raw);

            else if (op2 == b000000 && rt == b1111)
                result = g_undef_instruction_new(IEB_NOP);

            else if ((op2 & b111100) == b110000 && rt == b1111)
                result = g_undef_instruction_new(IEB_NOP);

        }

        else if (op1 == b11)
        {
            if (rt != b1111)
                result = armv7_read_thumb_32_instr_a8_ldrsh_immediate(raw);

            else/* if (rt == b1111)*/
                result = g_undef_instruction_new(IEB_NOP);

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A6.3.9.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_load_byte_memory_hints(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t op1;                           /* Champ 'op1' à retrouver     */
    uint32_t rn;                            /* Champ 'rn' à retrouver      */
    uint32_t rt;                            /* Champ 'rt' à retrouver      */
    uint32_t op2;                           /* Champ 'op2' à retrouver     */

    /**
     * Suit les directives de :
     * § A6.3.9 Load byte, memory hints
     */

    if ((raw & 0xfe700000) != 0xf8100000) return NULL;

    result = NULL;

    op1 = (raw >> 23) & b11;
    rn = (raw >> 16) & b1111;
    rt = (raw >> 12) & b1111;
    op2 = (raw >> 6) & b111111;

    if (op1 == b00 && op2 == b000000 && rn != b1111)
    {
        if (rt != b1111)
            result = armv7_read_thumb_32_instr_a8_ldrb_register(raw);

        else /*if (rt == b1111) */
            result = armv7_read_thumb_32_instr_a8_pld_pldw_register(raw);

    }

    else if ((op1 & b10) == b00 && rn == b1111)
    {
        if (rt != b1111)
            result = armv7_read_thumb_32_instr_a8_ldrb_literal(raw);

        else /*if (rt == b1111) */
            result = armv7_read_thumb_32_instr_a8_pld_literal(raw);

    }

    else if (op1 == b00 && (op2 & b100100) == b100100 && rn != b1111)
        result = armv7_read_thumb_32_instr_a8_ldrb_immediate_thumb(raw);

    else if (op1 == b00 && (op2 & b111100) == b110000 && rn != b1111)
    {
        if (rt != b1111)
            result = armv7_read_thumb_32_instr_a8_ldrb_immediate_thumb(raw);

        else /*if (rt == b1111) */
            result = armv7_read_thumb_32_instr_a8_pld_pldw_immediate(raw);

    }

    else if (op1 == b00 && (op2 & b111100) == b111000 && rn != b1111)
        result = armv7_read_thumb_32_instr_a8_ldrbt(raw);

    else if (op1 == b01 && rn != b1111)
    {
        if (rt != b1111)
            result = armv7_read_thumb_32_instr_a8_ldrb_immediate_thumb(raw);

        else /*if (rt == b1111) */
            result = armv7_read_thumb_32_instr_a8_pld_pldw_immediate(raw);

    }

    if (op1 == b10 && op2 == b000000 && rn != b1111)
    {
        if (rt != b1111)
            result = armv7_read_thumb_32_instr_a8_ldrsb_register(raw);
        else /*if (rt == b1111) */
            result = armv7_read_thumb_32_instr_a8_pli_register(raw);
    }

    else if ((op1 & b10) == b10 && rn == b1111)
    {
        if (rt != b1111)
            result = armv7_read_thumb_32_instr_a8_ldrsb_literal(raw);

        else /*if (rt == b1111) */
            result = armv7_read_thumb_32_instr_a8_pli_immediate_literal(raw);

    }

    else if (op1 == b10 && (op2 & b100100) == b100100 && rn != b1111)
        result = armv7_read_thumb_32_instr_a8_ldrsb_immediate(raw);

    else if (op1 == b10 && (op2 & b111100) == b110000 && rn != b1111)
    {
        if (rt != b1111)
            result = armv7_read_thumb_32_instr_a8_ldrsb_immediate(raw);

        else /*if (rt == b1111) */
            result = armv7_read_thumb_32_instr_a8_pli_immediate_literal(raw);

    }

    else if (op1 == b10 && (op2 & b111100) == b111000 && rn != b1111)
        result = armv7_read_thumb_32_instr_a8_ldrsbt(raw);

    else if (op1 == b11 && rn != b1111)
    {
        if (rt != b1111)
            result = armv7_read_thumb_32_instr_a8_ldrsb_immediate(raw);

        else /*if (rt == b1111) */
            result = armv7_read_thumb_32_instr_a8_pli_immediate_literal(raw);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A6.3.10. *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_store_single_data_item(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t op1;                           /* Champ 'op1' à retrouver     */
    uint32_t op2;                           /* Champ 'op2' à retrouver     */

    /**
     * Suit les directives de :
     * § A6.3.10 Store single data item
     */

    if ((raw & 0xff100000) != 0xf8000000) return NULL;

    result = NULL;

    op1 = (raw >> 21) & b111;
    op2 = (raw >> 6) & b111111;

    switch (op1)
    {
        case b000:

            if (op2 == b000000)
                result = armv7_read_thumb_32_instr_a8_strb_register(raw);

            else if ((op2 & b100100) == b100100)
                result = armv7_read_thumb_32_instr_a8_strb_immediate_thumb(raw);

            else if ((op2 & b111100) == b110000)
                result = armv7_read_thumb_32_instr_a8_strb_immediate_thumb(raw);

            else if ((op2 & b111100) == b111000)
                result = armv7_read_thumb_32_instr_a8_strbt(raw);

            break;

        case b001:

            if (op2 == b000000)
                result = armv7_read_thumb_32_instr_a8_strh_register(raw);

            else if ((op2 & b100100) == b100100)
                result = armv7_read_thumb_32_instr_a8_strh_immediate_thumb(raw);

            else if ((op2 & b111100) == b110000)
                result = armv7_read_thumb_32_instr_a8_strh_immediate_thumb(raw);

            else if ((op2 & b111100) == b111000)
                result = armv7_read_thumb_32_instr_a8_strht(raw);

            break;

        case b010:

            if (op2 == b000000)
                result = armv7_read_thumb_32_instr_a8_str_register(raw);

            else if ((op2 & b100100) == b100100)
                result = armv7_read_thumb_32_instr_a8_str_immediate_thumb(raw);

            else if ((op2 & b111100) == b110000)
                result = armv7_read_thumb_32_instr_a8_str_immediate_thumb(raw);

            else if ((op2 & b111100) == b111000)
                result = armv7_read_thumb_32_instr_a8_strt(raw);

            break;

        case b100:
            result = armv7_read_thumb_32_instr_a8_strb_immediate_thumb(raw);
            break;

        case b101:
            result = armv7_read_thumb_32_instr_a8_strh_immediate_thumb(raw);
            break;

        case b110:
            result = armv7_read_thumb_32_instr_a8_str_immediate_thumb(raw);
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A6.3.11. *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_data_processing_shifted_register(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t op;                            /* Champ 'op' à retrouver      */
    uint32_t rn;                            /* Champ 'rn' à retrouver      */
    uint32_t rds;                           /* Champ 'rds' à retrouver     */

    /**
     * Suit les directives de :
     * § A6.3.11 Data-processing (shifted register)
     */

    if ((raw & 0xfe000000) != 0xea000000) return NULL;

    result = NULL;

    op = (raw >> 21) & b1111;
    rn = (raw >> 16) & b1111;
    rds = (((raw >> 8) & b1111) << 1) | ((raw >> 20) & b1);

    switch (op)
    {
        case b0000:

            if (rds == b11111)
                result = armv7_read_thumb_32_instr_a8_tst_register(raw);

            else
                result = armv7_read_thumb_32_instr_a8_and_register(raw);

            break;

        case b0001:
            result = armv7_read_thumb_32_instr_a8_bic_register(raw);
            break;

        case b0010:

            if (rn == b11111)
                result = process_armv7_thumb_32_move_register_and_immediate_shifts(raw);

            else
                result = armv7_read_thumb_32_instr_a8_orr_register(raw);

            break;

        case b0011:

            if (rn == b11111)
                result = armv7_read_thumb_32_instr_a8_mvn_register(raw);

            else
                result = armv7_read_thumb_32_instr_a8_orn_register(raw);

            break;

        case b0100:

            if (rds == b11111)
                result = armv7_read_thumb_32_instr_a8_teq_register(raw);

            else
                result = armv7_read_thumb_32_instr_a8_eor_register(raw);

            break;

        case b0110:
            result = armv7_read_thumb_32_instr_a8_pkh(raw);
            break;

        case b1000:

            if (rds == b11111)
                result = armv7_read_thumb_32_instr_a8_cmn_register(raw);

            else
                result = armv7_read_thumb_32_instr_a8_add_register_thumb(raw);

            break;

        case b1010:
            result = armv7_read_thumb_32_instr_a8_adc_register(raw);
            break;

        case b1011:
            result = armv7_read_thumb_32_instr_a8_sbc_register(raw);
            break;

        case b1101:

            if (rds == b11111)
                result = armv7_read_thumb_32_instr_a8_cmp_register(raw);

            else
                result = armv7_read_thumb_32_instr_a8_sub_register(raw);

            break;

        case b1110:
            result = armv7_read_thumb_32_instr_a8_rsb_register(raw);
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A6.3.11b.*
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_move_register_and_immediate_shifts(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t imm5;                          /* Champs 'imm[32]' à retrouver*/
    uint32_t type;                          /* Champ 'type' à retrouver    */

    /**
     * Suit les directives de :
     * § A6.3.11 Data-processing (shifted register)
     *    |-> Move register and immediate shifts
     */

    if ((raw & 0xffef0000) != 0xea4f0000) return NULL;

    result = NULL;

    imm5 = (((raw >> 12) & 0x7) << 2) | ((raw >> 6) & 0x3);
    type = (raw >> 4) & 0x3;

    switch (type)
    {
        case b00:

            if (imm5 == b00000)
                result = armv7_read_thumb_32_instr_a8_mov_register_thumb(raw);

            else/* if (imm5 != b00000)*/
                result = armv7_read_thumb_32_instr_a8_lsl_immediate(raw);

            break;

        case b01:
            result = armv7_read_thumb_32_instr_a8_lsr_immediate(raw);
            break;

        case b10:
            result = armv7_read_thumb_32_instr_a8_asr_immediate(raw);
            break;

        case b11:

            if (imm5 == b00000)
                result = armv7_read_thumb_32_instr_a8_rrx(raw);

            else/* if (imm5 != b00000)*/
                result = armv7_read_thumb_32_instr_a8_ror_immediate(raw);

            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A6.3.12. *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_data_processing_register(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t op1;                           /* Champ 'op1' à retrouver     */
    uint32_t rn;                            /* Champ 'rn' à retrouver      */
    uint32_t op2;                           /* Champ 'op2' à retrouver     */

    /**
     * Suit les directives de :
     * § A6.3.12 Data-processing (register)
     */

    if ((raw & 0xff00f000) != 0xfa00f000) return NULL;

    result = NULL;

    op1 = (raw >> 20) & b1111;
    rn = (raw >> 16) & b1111;
    op2 = (raw >> 4) & b1111;

    if ((op1 & b1110) == b0000 && op2 == b0000)
        result = armv7_read_thumb_32_instr_a8_lsl_register(raw);

    else if ((op1 & b1110) == b0010 && op2 == b0000)
        result = armv7_read_thumb_32_instr_a8_lsr_register(raw);

    else if ((op1 & b1110) == b0100 && op2 == b0000)
        result = armv7_read_thumb_32_instr_a8_asr_register(raw);

    else if ((op1 & b1110) == b0110 && op2 == b0000)
        result = armv7_read_thumb_32_instr_a8_ror_register(raw);

    else if (op1 == b0000 && (op2 & b1000) == b1000)
    {
        if (rn == b1111)
            result = armv7_read_thumb_32_instr_a8_sxth(raw);

        else
            result = armv7_read_thumb_32_instr_a8_sxtah(raw);

    }

    else if (op1 == b0001 && (op2 & b1000) == b1000)
    {
        if (rn == b1111)
            result = armv7_read_thumb_32_instr_a8_uxth(raw);

        else
            result = armv7_read_thumb_32_instr_a8_uxtah(raw);

    }

    else if (op1 == b0010 && (op2 & b1000) == b1000)
    {
        if (rn == b1111)
            result = armv7_read_thumb_32_instr_a8_sxtb16(raw);

        else
            result = armv7_read_thumb_32_instr_a8_sxtab16(raw);

    }

    else if (op1 == b0011 && (op2 & b1000) == b1000)
    {
        if (rn == b1111)
            result = armv7_read_thumb_32_instr_a8_uxtb16(raw);

        else
            result = armv7_read_thumb_32_instr_a8_uxtab16(raw);

    }

    else if (op1 == b0100 && (op2 & b1000) == b1000)
    {
        if (rn == b1111)
            result = armv7_read_thumb_32_instr_a8_sxtb(raw);

        else
            result = armv7_read_thumb_32_instr_a8_sxtab(raw);

    }

    else if (op1 == b0101 && (op2 & b1000) == b1000)
    {
        if (rn == b1111)
            result = armv7_read_thumb_32_instr_a8_uxtb(raw);

        else
            result = armv7_read_thumb_32_instr_a8_uxtab(raw);

    }

    else if ((op1 & b1000) == b1000 && (op2 & b1100) == b0000)
        result = process_armv7_thumb_32_parallel_addition_and_subtraction_signed(raw);

    else if ((op1 & b1000) == b1000 && (op2 & b1100) == b0100)
        result = process_armv7_thumb_32_parallel_addition_and_subtraction_unsigned(raw);

    else if ((op1 & b1100) == b1000 && (op2 & b1100) == b1000)
        result = process_armv7_thumb_32_miscellaneous_operations(raw);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A6.3.13. *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_parallel_addition_and_subtraction_signed(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t op1;                           /* Champ 'op1' à retrouver     */
    uint32_t op2;                           /* Champ 'op2' à retrouver     */

    /**
     * Suit les directives de :
     * § A6.3.13 Parallel addition and subtraction, signed
     */

    if ((raw & 0xff80f000) != 0xfa80f000) return NULL;

    result = NULL;

    op1 = (raw >> 20) & b111;
    op2 = (raw >> 4) & b11;

    switch (op2)
    {
        case b00:
            switch (op1)
            {
                case b001:
                    result = armv7_read_thumb_32_instr_a8_sadd16(raw);
                    break;

                case b010:
                    result = armv7_read_thumb_32_instr_a8_sasx(raw);
                    break;

                case b110:
                    result = armv7_read_thumb_32_instr_a8_ssax(raw);
                    break;

                case b101:
                    result = armv7_read_thumb_32_instr_a8_ssub16(raw);
                    break;

                case b000:
                    result = armv7_read_thumb_32_instr_a8_sadd8(raw);
                    break;

                case b100:
                    result = armv7_read_thumb_32_instr_a8_ssub8(raw);
                    break;

            }
            break;

        case b01:
            switch (op1)
            {
                case b001:
                    result = armv7_read_thumb_32_instr_a8_qadd16(raw);
                    break;

                case b010:
                    result = armv7_read_thumb_32_instr_a8_qasx(raw);
                    break;

                case b110:
                    result = armv7_read_thumb_32_instr_a8_qsax(raw);
                    break;

                case b101:
                    result = armv7_read_thumb_32_instr_a8_qsub16(raw);
                    break;

                case b000:
                    result = armv7_read_thumb_32_instr_a8_qadd8(raw);
                    break;

                case b100:
                    result = armv7_read_thumb_32_instr_a8_qsub8(raw);
                    break;

            }
            break;

        case b10:
            switch (op1)
            {
                case b001:
                    result = armv7_read_thumb_32_instr_a8_shadd16(raw);
                    break;

                case b010:
                    result = armv7_read_thumb_32_instr_a8_shasx(raw);
                    break;

                case b110:
                    result = armv7_read_thumb_32_instr_a8_shsax(raw);
                    break;

                case b101:
                    result = armv7_read_thumb_32_instr_a8_shsub16(raw);
                    break;

                case b000:
                    result = armv7_read_thumb_32_instr_a8_shadd8(raw);
                    break;

                case b100:
                    result = armv7_read_thumb_32_instr_a8_shsub8(raw);
                    break;

            }
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A6.3.14. *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_parallel_addition_and_subtraction_unsigned(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t op1;                           /* Champ 'op1' à retrouver     */
    uint32_t op2;                           /* Champ 'op2' à retrouver     */

    /**
     * Suit les directives de :
     * § A6.3.14 Parallel addition and subtraction, unsigned
     */

    if ((raw & 0xff80f0c0) != 0xfa80f040) return NULL;

    result = NULL;

    op1 = (raw >> 20) & b111;
    op2 = (raw >> 4) & b11;

    switch (op2)
    {
        case b00:
            switch (op1)
            {
                case b001:
                    result = armv7_read_thumb_32_instr_a8_uadd16(raw);
                    break;

                case b010:
                    result = armv7_read_thumb_32_instr_a8_uasx(raw);
                    break;

                case b110:
                    result = armv7_read_thumb_32_instr_a8_usax(raw);
                    break;

                case b101:
                    result = armv7_read_thumb_32_instr_a8_usub16(raw);
                    break;

                case b000:
                    result = armv7_read_thumb_32_instr_a8_uadd8(raw);
                    break;

                case b100:
                    result = armv7_read_thumb_32_instr_a8_usub8(raw);
                    break;

            }
            break;

        case b01:
            switch (op1)
            {
                case b001:
                    result = armv7_read_thumb_32_instr_a8_uqadd16(raw);
                    break;

                case b010:
                    result = armv7_read_thumb_32_instr_a8_uqasx(raw);
                    break;

                case b110:
                    result = armv7_read_thumb_32_instr_a8_uqsax(raw);
                    break;

                case b101:
                    result = armv7_read_thumb_32_instr_a8_uqsub16(raw);
                    break;

                case b000:
                    result = armv7_read_thumb_32_instr_a8_uqadd8(raw);
                    break;

                case b100:
                    result = armv7_read_thumb_32_instr_a8_uqsub8(raw);
                    break;

            }
            break;

        case b10:
            switch (op1)
            {
                case b001:
                    result = armv7_read_thumb_32_instr_a8_uhadd16(raw);
                    break;

                case b010:
                    result = armv7_read_thumb_32_instr_a8_uhasx(raw);
                    break;

                case b110:
                    result = armv7_read_thumb_32_instr_a8_uhsax(raw);
                    break;

                case b101:
                    result = armv7_read_thumb_32_instr_a8_uhsub16(raw);
                    break;

                case b000:
                    result = armv7_read_thumb_32_instr_a8_uhadd8(raw);
                    break;

                case b100:
                    result = armv7_read_thumb_32_instr_a8_uhsub8(raw);
                    break;

            }
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A6.3.15. *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_miscellaneous_operations(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t op1;                           /* Champ 'op1' à retrouver     */
    uint32_t op2;                           /* Champ 'op2' à retrouver     */

    /**
     * Suit les directives de :
     * § A6.3.15 Miscellaneous operations
     */

    if ((raw & 0xffc0f0c0) != 0xfa80f080) return NULL;

    result = NULL;

    op1 = (raw >> 20) & b11;
    op2 = (raw >> 4) & b11;

    switch (op1)
    {
        case b00:
            switch (op2)
            {
                case b00:
                    result = armv7_read_thumb_32_instr_a8_qadd(raw);
                    break;

                case b01:
                    result = armv7_read_thumb_32_instr_a8_qdadd(raw);
                    break;

                case b10:
                    result = armv7_read_thumb_32_instr_a8_qsub(raw);
                    break;

                case b11:
                    result = armv7_read_thumb_32_instr_a8_qdsub(raw);
                    break;

            }
            break;

        case b01:
            switch (op2)
            {
                case b00:
                    result = armv7_read_thumb_32_instr_a8_rev(raw);
                    break;

                case b01:
                    result = armv7_read_thumb_32_instr_a8_rev16(raw);
                    break;

                case b10:
                    result = armv7_read_thumb_32_instr_a8_rbit(raw);
                    break;

                case b11:
                    result = armv7_read_thumb_32_instr_a8_revsh(raw);
                    break;

            }
            break;

        case b10:
            if (op2 == b00)
                result = armv7_read_thumb_32_instr_a8_sel(raw);
            break;

        case b11:
            if (op2 == b00)
                result = armv7_read_thumb_32_instr_a8_clz(raw);
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A6.3.16. *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_multiply_multiply_accumulate_and_absolute_difference(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t op1;                           /* Champ 'op1' à retrouver     */
    uint32_t ra;                            /* Champ 'ra' à retrouver      */
    uint32_t op2;                           /* Champ 'op2' à retrouver     */

    /**
     * Suit les directives de :
     * § A6.3.16 Multiply, multiply accumulate, and absolute difference
     */

    if ((raw & 0xff8000c0) != 0xfb000000) return NULL;

    result = NULL;

    op1 = (raw >> 20) & b111;
    ra = (raw >> 12) & b1111;
    op2 = (raw >> 4) & b11;

    switch (op1)
    {
        case b000:

            if (op2 == b00)
            {
                if (ra == b1111)
                    result = armv7_read_thumb_32_instr_a8_mul(raw);

                else
                    result = armv7_read_thumb_32_instr_a8_mla(raw);

            }

            else if (op2 == b01)
                result = armv7_read_thumb_32_instr_a8_mls(raw);

            break;

        case b001:

            if (ra == b1111)
                result = armv7_read_thumb_32_instr_a8_smulbb_smulbt_smultb_smultt(raw);

            else
                result = armv7_read_thumb_32_instr_a8_smlabb_smlabt_smlatb_smlatt(raw);

            break;

        case b010:
            if ((op2 & b10) == b00)
            {
                if (ra == b1111)
                    result = armv7_read_thumb_32_instr_a8_smuad(raw);

                else
                    result = armv7_read_thumb_32_instr_a8_smlad(raw);

            }
            break;

        case b011:
            if ((op2 & b10) == b00)
            {
                if (ra == b1111)
                    result = armv7_read_thumb_32_instr_a8_smulwb_smulwt(raw);

                else
                    result = armv7_read_thumb_32_instr_a8_smlawb_smlawt(raw);

            }
            break;

        case b100:
            if ((op2 & b10) == b00)
            {
                if (ra == b1111)
                    result = armv7_read_thumb_32_instr_a8_smusd(raw);

                else
                    result = armv7_read_thumb_32_instr_a8_smlsd(raw);

            }
            break;

        case b101:
            if ((op2 & b10) == b00)
            {
                if (ra == b1111)
                    result = armv7_read_thumb_32_instr_a8_smmul(raw);

                else
                    result = armv7_read_thumb_32_instr_a8_smmla(raw);

            }
            break;

        case b110:
            if ((op2 & b10) == b00)
                result = armv7_read_thumb_32_instr_a8_smmls(raw);
            break;

        case b111:
            if (op2 == b00)
            {
                if (ra == b1111)
                    result = armv7_read_thumb_32_instr_a8_usad8(raw);

                else
                    result = armv7_read_thumb_32_instr_a8_usada8(raw);

            }
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A6.3.17. *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_long_multiply_long_multiply_accumulate_and_divide(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t op1;                           /* Champ 'op1' à retrouver     */
    uint32_t op2;                           /* Champ 'op2' à retrouver     */

    /**
     * Suit les directives de :
     * § A6.3.17 Long multiply, long multiply accumulate, and divide
     */

    if ((raw & 0xff800000) != 0xfb800000) return NULL;

    result = NULL;

    op1 = (raw >> 20) & b111;
    op2 = (raw >> 4) & b1111;

    switch (op1)
    {
        case b000:
            if (op2 == b0000)
                result = armv7_read_thumb_32_instr_a8_smull(raw);
            break;

        case b001:
            if (op2 == b1111)
                result = armv7_read_thumb_32_instr_a8_sdiv(raw);
            break;

        case b010:
            if (op2 == b0000)
                result = armv7_read_thumb_32_instr_a8_umull(raw);
            break;

        case b011:
            if (op2 == b1111)
                result = armv7_read_thumb_32_instr_a8_udiv(raw);
            break;

        case b100:

            if (op2 == b0000)
                result = armv7_read_thumb_32_instr_a8_smlal(raw);

            else if ((op2 & b1100) == b1000)
                result = armv7_read_thumb_32_instr_a8_smlalbb_smlalbt_smlaltb_smlaltt(raw);

            else if ((op2 & b1110) == b1100)
                result = armv7_read_thumb_32_instr_a8_smlald(raw);

            break;

        case b101:
            if ((op2 & b1110) == b1100)
                result = armv7_read_thumb_32_instr_a8_smlsld(raw);
            break;

        case b110:

            if (op2 == b0000)
                result = armv7_read_thumb_32_instr_a8_umlal(raw);

            else if (op2 == b0110)
                result = armv7_read_thumb_32_instr_a8_umaal(raw);

            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A6.3.18. *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_coprocessor_advanced_simd_and_floating_point_instructions(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t op1;                           /* Champ 'op1' à retrouver     */
    uint32_t rn;                            /* Champ 'rn' à retrouver      */
    uint32_t coproc;                        /* Champ 'coproc' à retrouver  */
    uint32_t op;                            /* Champ 'op' à retrouver      */

    /**
     * Suit les directives de :
     * § A6.3.18 Coprocessor, Advanced SIMD, and Floating-point instructions
     */

    if ((raw & 0xec000000) != 0xec000000) return NULL;

    result = NULL;

    op1 = (raw >> 20) & 0x3f;
    rn = (raw >> 16) & 0xf;
    coproc = (raw >> 8) & 0xf;
    op = (raw >> 4) & 0x1;

    if ((op1 & b111110) == b000000)
        result = g_undef_instruction_new(IEB_UNDEFINED);

    else if ((op1 & b110000) == b110000)
        result = process_armv7_thumb_32_advanced_simd_data_processing_instructions(raw);

    else if ((coproc & b1110) != b1010)
    {
        if ((op1 & b100001) == b000000 && (op1 & b111010) != b000000)
            result = armv7_read_thumb_32_instr_a8_stc_stc2(raw);

        else if ((op1 & b100001) == b000001 && (op1 & b111010) != b000000)
        {
            if (rn != b1111)
                result = armv7_read_thumb_32_instr_a8_ldc_ldc2_immediate(raw);

            else/* if (rn == b1111)*/
                result = armv7_read_thumb_32_instr_a8_ldc_ldc2_literal(raw);

        }

        else if (op1 == b000100)
            result = armv7_read_thumb_32_instr_a8_mcrr_mcrr2(raw);

        else if (op1 == b000101)
            result = armv7_read_thumb_32_instr_a8_mrrc_mrrc2(raw);

        else if ((op1 & b110000) == b100000 && op == b0)
            result = armv7_read_thumb_32_instr_a8_cdp_cdp2(raw);

        else if ((op1 & b110001) == b100000 && op == b1)
            result = armv7_read_thumb_32_instr_a8_mcr_mcr2(raw);

        else if ((op1 & b110001) == b100001 && op == b1)
            result = armv7_read_thumb_32_instr_a8_mrc_mrc2(raw);

    }

    else if ((coproc & b1110) == b1010)
    {
        if ((op1 & b100000) == b000000 && (op1 & b111010) != b000000)
            result = process_armv7_thumb_32_extension_register_load_store_instructions(raw);

        else if ((op1 & b111110) == b000100)
            result = process_armv7_thumb_32_64_bit_transfers_between_arm_core_and_extension_registers(raw);

        else if ((op1 & b110000) == b100000)
        {
            if (op == b0)
                result = process_armv7_thumb_32_floating_point_data_processing_instructions(raw);

            else/* if (op == b1)*/
                result = process_armv7_thumb_32_8_16_and_32_bit_transfer_between_arm_core_and_extension_registers(raw);

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 16 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A7.4.    *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_advanced_simd_data_processing_instructions(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t u;                             /* Champ 'u' à retrouver       */
    uint32_t a;                             /* Champ 'a' à retrouver       */
    uint32_t b;                             /* Champ 'b' à retrouver       */
    uint32_t c;                             /* Champ 'c' à retrouver       */

    /**
     * Suit les directives de :
     * § A7.4 Advanced SIMD data-processing instructions
     */

    if ((raw & 0xef000000) != 0xef000000) return NULL;

    result = NULL;

    u = (raw >> 28) & b1;
    a = (raw >> 19) & b11111;
    b = (raw >> 8) & b1111;
    c = (raw >> 4) & b1111;

    if ((a & b10000) == b00000)
        result = process_armv7_thumb_32_three_registers_of_the_same_length(raw);

    else if ((a & b10111) == b10000 && (c & b1001) == b0001)
        result = process_armv7_thumb_32_one_register_and_a_modified_immediate_value(raw);

    else if ((a & b10111) == b10001 && (c & b1001) == b0001)
        result = process_armv7_thumb_32_two_registers_and_a_shift_amount(raw);

    else if ((a & b10110) == b10010 && (c & b1001) == b0001)
        result = process_armv7_thumb_32_two_registers_and_a_shift_amount(raw);

    else if ((a & b10100) == b10100 && (c & b1001) == b0001)
        result = process_armv7_thumb_32_two_registers_and_a_shift_amount(raw);

    else if ((a & b10000) == b10000 && (c & b1001) == b1001)
        result = process_armv7_thumb_32_two_registers_and_a_shift_amount(raw);

    else if ((a & b10100) == b10000 && (c & b0101) == b0000)
        result = process_armv7_thumb_32_three_registers_of_different_lengths(raw);

    else if ((a & b10110) == b10100 && (c & b0101) == b0000)
        result = process_armv7_thumb_32_three_registers_of_different_lengths(raw);

    else if ((a & b10100) == b10000 && (c & b0101) == b0100)
        result = process_armv7_thumb_32_two_registers_and_a_scalar(raw);

    else if ((a & b10110) == b10100 && (c & b0101) == b0100)
        result = process_armv7_thumb_32_two_registers_and_a_scalar(raw);

    else if (u == b0 && (a & b10110) == b10110 && (c & b0001) == b0000)
        result = armv7_read_thumb_32_instr_a8_vext(raw);

    else if (u == b1 && (a & b10110) == b10110)
    {
        if ((b & b1000) == b0000 && (c & b0001) == b0000)
            result = process_armv7_thumb_32_two_registers_miscellaneous(raw);

        else if ((b & b1100) == b1000 && (c & b0001) == b0000)
            result = armv7_read_thumb_32_instr_a8_vtbl_vtbx(raw);

        else if (b == b1100 && (c & b1001) == b0000)
            result = armv7_read_thumb_32_instr_a8_vdup_scalar(raw);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 16 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A7.4.1.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_three_registers_of_the_same_length(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t u;                             /* Champ 'u' à retrouver       */
    uint32_t c;                             /* Champ 'c' à retrouver       */
    uint32_t a;                             /* Champ 'a' à retrouver       */
    uint32_t b;                             /* Champ 'b' à retrouver       */

    /**
     * Suit les directives de :
     * § A7.4.1 Three registers of the same length
     */

    if ((raw & 0xef800000) != 0xef000000) return NULL;

    result = NULL;

    u = (raw >> 28) & b1;
    c = (raw >> 20) & b11;
    a = (raw >> 8) & b1111;
    b = (raw >> 4) & b1;

    if (a == b0000)
    {
        if (b == b0)
            result = armv7_read_thumb_32_instr_a8_vhadd_vhsub(raw);

        else/* if (b == b1)*/
            result = armv7_read_thumb_32_instr_a8_vqadd(raw);

    }

    else if (a == b0001)
    {
        if (b == b0)
            result = armv7_read_thumb_32_instr_a8_vrhadd(raw);

        else/* if (b == b1)*/
        {
            if (u == b0)
                switch (c)
                {
                    case b00:
                        result = armv7_read_thumb_32_instr_a8_vand_register(raw);
                        break;

                    case b01:
                        result = armv7_read_thumb_32_instr_a8_vbic_register(raw);
                        break;

                    case b10:
                        /* Cf. vmov_register aussi */
                        result = armv7_read_thumb_32_instr_a8_vorr_register(raw);
                        break;

                     case b11:
                        result = armv7_read_thumb_32_instr_a8_vorn_register(raw);
                        break;

                }

            else/* if (u == b1)*/
                switch (c)
                {
                    case b00:
                        result = armv7_read_thumb_32_instr_a8_veor(raw);
                        break;

                    case b01:
                        result = armv7_read_thumb_32_instr_a8_vbif_vbit_vbsl(raw);
                        break;

                    case b10:
                        result = armv7_read_thumb_32_instr_a8_vbif_vbit_vbsl(raw);
                        break;

                     case b11:
                        result = armv7_read_thumb_32_instr_a8_vbif_vbit_vbsl(raw);
                        break;

                }

        }

    }

    else if (a == b0010)
    {
        if (b == b0)
            result = armv7_read_thumb_32_instr_a8_vhadd_vhsub(raw);

        else/* if (b == b1)*/
            result = armv7_read_thumb_32_instr_a8_vqsub(raw);

    }

    else if (a == b0011)
    {
        if (b == b0)
            result = armv7_read_thumb_32_instr_a8_vcgt_register(raw);

        else/* if (b == b1)*/
            result = armv7_read_thumb_32_instr_a8_vcge_register(raw);

    }

    else if (a == b0100)
    {
        if (b == b0)
            result = armv7_read_thumb_32_instr_a8_vshl_register(raw);

        else/* if (b == b1)*/
            result = armv7_read_thumb_32_instr_a8_vqshl_register(raw);

    }

    else if (a == b0101)
    {
        if (b == b0)
            result = armv7_read_thumb_32_instr_a8_vrshl(raw);

        else/* if (b == b1)*/
            result = armv7_read_thumb_32_instr_a8_vqrshl(raw);

    }

    else if (a == b0110)
        result = armv7_read_thumb_32_instr_a8_vmax_vmin_integer(raw);

    else if (a == b0111)
    {
        if (b == b0)
            result = armv7_read_thumb_32_instr_a8_vabd_vabdl_integer(raw);

        else/* if (b == b1)*/
            result = armv7_read_thumb_32_instr_a8_vaba_vabal(raw);

    }

    else if (a == b1000)
    {
        if (b == b0)
        {
            if (u == b0)
                result = armv7_read_thumb_32_instr_a8_vadd_integer(raw);

            else/* if (u == b1)*/
                result = armv7_read_thumb_32_instr_a8_vsub_integer(raw);

        }

        else/* if (b == b1)*/
        {
            if (u == b0)
                result = armv7_read_thumb_32_instr_a8_vtst(raw);

            else/* if (u == b1)*/
                result = armv7_read_thumb_32_instr_a8_vceq_register(raw);

        }

    }

    else if (a == b1001)
    {
        if (b == b0)
            result = armv7_read_thumb_32_instr_a8_vmla_vmlal_vmls_vmlsl_integer(raw);

        else/* if (b == b1)*/
            result = armv7_read_thumb_32_instr_a8_vmul_vmull_integer_and_polynomial(raw);

    }

    else if (a == b1010)
        result = armv7_read_thumb_32_instr_a8_vpmax_vpmin_integer(raw);

    else if (a == b1011)
    {
        if (b == b0)
        {
            if (u == b0)
                result = armv7_read_thumb_32_instr_a8_vqdmulh(raw);

            else/* if (u == b1)*/
                result = armv7_read_thumb_32_instr_a8_vqrdmulh(raw);

        }

        else/* if (b == b1)*/
        {
            if (u == b0)
                result = armv7_read_thumb_32_instr_a8_vpadd_integer(raw);

        }

    }

    else if (a == b1100)
    {
        if (b == b1 && u == b0)
            result = armv7_read_thumb_32_instr_a8_vfma_vfms(raw);

    }

    else if (a == b1101)
    {
        if (b == b0)
        {
            if (u == b0)
            {
                if ((c & b10) == b00)
                    result = armv7_read_thumb_32_instr_a8_vadd_floating_point(raw);

                else/* if ((c & b10) == b10)*/
                    result = armv7_read_thumb_32_instr_a8_vsub_floating_point(raw);

            }

            else/* if (u == b1)*/
            {
                if ((c & b10) == b00)
                    result = armv7_read_thumb_32_instr_a8_vpadd_floating_point(raw);

                else/* if ((c & b10) == b10)*/
                    result = armv7_read_thumb_32_instr_a8_vabd_floating_point(raw);

            }

        }

        else/* if (b == b1)*/
        {
            if (u == b0)
                result = armv7_read_thumb_32_instr_a8_vmla_vmls_floating_point(raw);

            else/* if (u == b1)*/
            {
                if ((c & b10) == b00)
                    result = armv7_read_thumb_32_instr_a8_vmul_floating_point(raw);

            }

        }

    }

    else if (a == b1110)
    {
        if (b == b0)
        {
            if (u == b0)
            {
                if ((c & b10) == b00)
                    result = armv7_read_thumb_32_instr_a8_vceq_register(raw);

            }

            else/* if (u == b1)*/
            {
                if ((c & b10) == b00)
                    result = armv7_read_thumb_32_instr_a8_vcge_register(raw);

                else/* if ((c & b10) == b10)*/
                    result = armv7_read_thumb_32_instr_a8_vcgt_register(raw);

            }

        }

        else/* if (b == b1)*/
        {
            if (u == b1)
                result = armv7_read_thumb_32_instr_a8_vacge_vacgt_vacle_vaclt(raw);

        }

    }

    else if (a == b1111)
    {
        if (b == b0)
        {
            if (u == b0)
                result = armv7_read_thumb_32_instr_a8_vmax_vmin_floating_point(raw);

            else/* if (u == b1)*/
                result = armv7_read_thumb_32_instr_a8_vpmax_vpmin_floating_point(raw);

        }

        else/* if (b == b1)*/
        {
            if (u == b0)
            {
                if ((c & b10) == b00)
                    result = armv7_read_thumb_32_instr_a8_vrecps(raw);

                else/* if ((c & b10) == b10)*/
                    result = armv7_read_thumb_32_instr_a8_vrsqrts(raw);

            }

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 16 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A7.4.2.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_three_registers_of_different_lengths(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t u;                             /* Champ 'u' à retrouver       */
    uint32_t a;                             /* Champ 'a' à retrouver       */

    /**
     * Suit les directives de :
     * § A7.4.2 Three registers of different lengths
     */

    if ((raw & 0xef800050) != 0xef800000) return NULL;

    result = NULL;

    u = (raw >> 28) & b1;
    a = (raw >> 8) & b1111;

    if ((a & b1110) == b0000)
        result = armv7_read_thumb_32_instr_a8_vaddl_vaddw(raw);

    else if ((a & b1110) == b0010)
        result = armv7_read_thumb_32_instr_a8_vsubl_vsubw(raw);

    else if (a == b0100)
    {
        if (u == b0)
            result = armv7_read_thumb_32_instr_a8_vaddhn(raw);

        else/* if (u == b1)*/
            result = armv7_read_thumb_32_instr_a8_vraddhn(raw);

    }

    else if (a == b0101)
        result = armv7_read_thumb_32_instr_a8_vaba_vabal(raw);

    else if (a == b0110)
    {
        if (u == b0)
            result = armv7_read_thumb_32_instr_a8_vsubhn(raw);

        else/* if (u == b1)*/
            result = armv7_read_thumb_32_instr_a8_vrsubhn(raw);

    }

    else if (a == b0111)
        result = armv7_read_thumb_32_instr_a8_vabd_vabdl_integer(raw);

    else if ((a & b1101) == b1000)
        result = armv7_read_thumb_32_instr_a8_vmla_vmlal_vmls_vmlsl_integer(raw);

    else if ((a & b1101) == b1001)
    {
        if (u == b0)
            result = armv7_read_thumb_32_instr_a8_vqdmlal_vqdmlsl(raw);

    }

    else if (a == b1100)
        result = armv7_read_thumb_32_instr_a8_vmul_vmull_integer_and_polynomial(raw);

    else if (a == b1101)
    {
        if (u == b0)
            result = armv7_read_thumb_32_instr_a8_vqdmull(raw);

    }

    else if (a == b1110)
        result = armv7_read_thumb_32_instr_a8_vmul_vmull_integer_and_polynomial(raw);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 16 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A7.4.3.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_two_registers_and_a_scalar(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t u;                             /* Champ 'u' à retrouver       */
    uint32_t a;                             /* Champ 'a' à retrouver       */

    /**
     * Suit les directives de :
     * § A7.4.3 Two registers and a scalar
     */

    if ((raw & 0xef800050) != 0xef800040) return NULL;

    result = NULL;

    u = (raw >> 28) & b1;
    a = (raw >> 8) & b1111;

    if ((a & b1010) == b0000)
        result = armv7_read_thumb_32_instr_a8_vmla_vmlal_vmls_vmlsl_by_scalar(raw);

    else if ((a & b1010) == b0010)
        result = armv7_read_thumb_32_instr_a8_vmla_vmlal_vmls_vmlsl_by_scalar(raw);

    else if ((a & b1011) == b0011 && u == b0)
        result = armv7_read_thumb_32_instr_a8_vqdmlal_vqdmlsl(raw);

    else if ((a & b1110) == b1000)
        result = armv7_read_thumb_32_instr_a8_vmul_vmull_by_scalar(raw);

    else if (a == b1010)
        result = armv7_read_thumb_32_instr_a8_vmul_vmull_by_scalar(raw);

    else if (a == b1011 && u == b0)
        result = armv7_read_thumb_32_instr_a8_vqdmull(raw);

    else if (a == b1100)
        result = armv7_read_thumb_32_instr_a8_vqdmulh(raw);

    else if (a == b1101)
        result = armv7_read_thumb_32_instr_a8_vqrdmulh(raw);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 16 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A7.4.4.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_two_registers_and_a_shift_amount(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t u;                             /* Champ 'u' à retrouver       */
    uint32_t a;                             /* Champ 'a' à retrouver       */
    uint32_t l;                             /* Champ 'l' à retrouver       */
    uint32_t b;                             /* Champ 'b' à retrouver       */

    /**
     * Suit les directives de :
     * § A7.4.4 Two registers and a shift amount
     */

    if ((raw & 0xef800010) != 0xef800010) return NULL;

    result = NULL;

    u = (raw >> 28) & b1;
    a = (raw >> 8) & b1111;
    l = (raw >> 7) & b1;
    b = (raw >> 6) & b1;

    if (a == b0000)
        result = armv7_read_thumb_32_instr_a8_vshr(raw);

    else if (a == b0001)
        result = armv7_read_thumb_32_instr_a8_vsra(raw);

    else if (a == b0010)
        result = armv7_read_thumb_32_instr_a8_vrshr(raw);

    else if (a == b0011)
        result = armv7_read_thumb_32_instr_a8_vrsra(raw);

    else if (a == b0100 && u == b1)
        result = armv7_read_thumb_32_instr_a8_vsri(raw);

    else if (a == b0101)
    {
        if (u == b0)
            result = armv7_read_thumb_32_instr_a8_vshl_immediate(raw);

        else/* if (u == b1)*/
            result = armv7_read_thumb_32_instr_a8_vsli(raw);

    }

    else if ((a & b1110) == b0110)
        result = armv7_read_thumb_32_instr_a8_vqshl_vqshlu_immediate(raw);

    else if (a == b1000)
    {
        if (u == b0)
        {
            if (b == b0 && l == b0)
                result = armv7_read_thumb_32_instr_a8_vshrn(raw);

            else if (b == b1 && l == b0)
                result = armv7_read_thumb_32_instr_a8_vrshrn(raw);

        }
        else/* if (u == b1)*/
        {
            if (b == b0 && l == b0)
                result = armv7_read_thumb_32_instr_a8_vqshrn_vqshrun(raw);

            else if (b == b1 && l == b0)
                result = armv7_read_thumb_32_instr_a8_vqrshrn_vqrshrun(raw);

        }

    }

    else if (a == b1001)
    {
        if (b == b0 && l == b0)
            result = armv7_read_thumb_32_instr_a8_vqshrn_vqshrun(raw);

        else if (b == b1 && l == b0)
            result = armv7_read_thumb_32_instr_a8_vqrshrn_vqrshrun(raw);

    }

    else if (a == b1010 && b == b0 && l == b0)
    {
        result = armv7_read_thumb_32_instr_a8_vshll(raw);

        /* ??? */
        if (result == NULL)
            result = armv7_read_thumb_32_instr_a8_vmovl(raw);

    }

    else if ((a & b1110) == b1110 && l == b0)
        result = armv7_read_thumb_32_instr_a8_vcvt_between_floating_point_and_fixed_point_advanced_simd(raw);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 16 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A7.4.5.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_two_registers_miscellaneous(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t a;                             /* Champ 'a' à retrouver       */
    uint32_t b;                             /* Champ 'b' à retrouver       */

    /**
     * Suit les directives de :
     * § A7.4.5 Two registers, miscellaneous
     */

    if ((raw & 0xffb00810) != 0xffb00000) return NULL;

    result = NULL;

    a = (raw >> 16) & b11;
    b = (raw >> 6) & b11111;

    if (a == b00)
    {
        if ((b & b11110) == b00000)
            result = armv7_read_thumb_32_instr_a8_vrev16_vrev32_vrev64(raw);

        else if ((b & b11110) == b00010)
            result = armv7_read_thumb_32_instr_a8_vrev16_vrev32_vrev64(raw);

        else if ((b & b11110) == b00100)
            result = armv7_read_thumb_32_instr_a8_vrev16_vrev32_vrev64(raw);

        else if ((b & b11100) == b01000)
            result = armv7_read_thumb_32_instr_a8_vpaddl(raw);

        else if ((b & b11110) == b10000)
            result = armv7_read_thumb_32_instr_a8_vcls(raw);

        else if ((b & b11110) == b10010)
            result = armv7_read_thumb_32_instr_a8_vclz(raw);

        else if ((b & b11110) == b10100)
            result = armv7_read_thumb_32_instr_a8_vcnt(raw);

        else if ((b & b11110) == b10110)
            result = armv7_read_thumb_32_instr_a8_vmvn_register(raw);

        else if ((b & b11100) == b11000)
            result = armv7_read_thumb_32_instr_a8_vpadal(raw);

        else if ((b & b11110) == b11100)
            result = armv7_read_thumb_32_instr_a8_vqabs(raw);

        else if ((b & b11110) == b11110)
            result = armv7_read_thumb_32_instr_a8_vqneg(raw);

    }

    else if (a == b01)
    {
        if ((b & b01110) == b00000)
            result = armv7_read_thumb_32_instr_a8_vcgt_immediate_0(raw);

        else if ((b & b01110) == b00010)
            result = armv7_read_thumb_32_instr_a8_vcge_immediate_0(raw);

        else if ((b & b01110) == b00100)
            result = armv7_read_thumb_32_instr_a8_vceq_immediate_0(raw);

        else if ((b & b01110) == b00110)
            result = armv7_read_thumb_32_instr_a8_vcle_immediate_0(raw);

        else if ((b & b01110) == b01000)
            result = armv7_read_thumb_32_instr_a8_vclt_immediate_0(raw);

        else if ((b & b01110) == b01100)
            result = armv7_read_thumb_32_instr_a8_vabs(raw);

        else if ((b & b01110) == b01110)
            result = armv7_read_thumb_32_instr_a8_vneg(raw);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 16 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A7.4.6.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_one_register_and_a_modified_immediate_value(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t cmode;                         /* Champ 'cmode' à retrouver   */
    uint32_t op;                            /* Champ 'op' à retrouver      */

    /**
     * Suit les directives de :
     * § A7.4.6 One register and a modified immediate value
     */

    if ((raw & 0xefb80090) != 0xef800010) return NULL;

    result = NULL;

    cmode = (raw >> 8) & b1111;
    op = (raw >> 5) & b1;

    if (op == b0)
    {
        if ((cmode & b1001) == b0000)
            result = armv7_read_thumb_32_instr_a8_vmov_immediate(raw);

        else if ((cmode & b1001) == b0001)
            result = armv7_read_thumb_32_instr_a8_vorr_immediate(raw);

        else if ((cmode & b1101) == b1000)
            result = armv7_read_thumb_32_instr_a8_vmov_immediate(raw);

        else if ((cmode & b1101) == b1001)
            result = armv7_read_thumb_32_instr_a8_vorr_immediate(raw);

        else if ((cmode & b1100) == b1100)
            result = armv7_read_thumb_32_instr_a8_vmov_immediate(raw);

    }

    else/* if (op == b1)*/
    {
        if ((cmode & b1001) == b0000)
            result = armv7_read_thumb_32_instr_a8_vmvn_immediate(raw);

        else if ((cmode & b1001) == b0001)
            result = armv7_read_thumb_32_instr_a8_vbic_immediate(raw);

        else if ((cmode & b1101) == b1000)
            result = armv7_read_thumb_32_instr_a8_vmvn_immediate(raw);

        else if ((cmode & b1101) == b1001)
            result = armv7_read_thumb_32_instr_a8_vbic_immediate(raw);

        else if ((cmode & b1110) == b1100)
            result = armv7_read_thumb_32_instr_a8_vmvn_immediate(raw);

        else if (cmode == b1110)
            result = armv7_read_thumb_32_instr_a8_vmov_immediate(raw);

        else if (cmode == b1111)
            result = g_undef_instruction_new(IEB_UNDEFINED);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 16 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A7.5.    *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_floating_point_data_processing_instructions(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t opc1;                          /* Champ 'opc1' à retrouver    */
    uint32_t opc2;                          /* Champ 'opc2' à retrouver    */
    uint32_t opc3;                          /* Champ 'opc3' à retrouver    */

    /**
     * Suit les directives de :
     * § A7.5 Floating-point data-processing instructions
     */

    if ((raw & 0xef000e10) != 0x0e000a00) return NULL;

    result = NULL;

    opc1 = (raw >> 20) & b1111;
    opc2 = (raw >> 16) & b1111;
    opc3 = (raw >> 6) & b11;


    if ((opc1 & b1011) == b0000)
        result = armv7_read_thumb_32_instr_a8_vmla_vmls_floating_point(raw);

    else if ((opc1 & b1011) == b0001)
        result = armv7_read_thumb_32_instr_a8_vnmla_vnmls_vnmul(raw);

    else if ((opc1 & b1011) == b0010)
    {
        if ((opc3 & b01) == b01)
            result = armv7_read_thumb_32_instr_a8_vnmla_vnmls_vnmul(raw);

        else/* if ((opc3 & b01) == b00)*/
            result = armv7_read_thumb_32_instr_a8_vmul_floating_point(raw);

    }

    else if ((opc1 & b1011) == b0011)
    {
        if ((opc3 & b01) == b00)
            result = armv7_read_thumb_32_instr_a8_vadd_floating_point(raw);

        else/* if ((opc3 & b01) == b01)*/
            result = armv7_read_thumb_32_instr_a8_vsub_floating_point(raw);

    }

    else if ((opc1 & b1011) == b1000)
    {
        if ((opc3 & b01) == b00)
            result = armv7_read_thumb_32_instr_a8_vdiv(raw);

    }

    else if ((opc1 & b1011) == b1001)
        result = armv7_read_thumb_32_instr_a8_vfnma_vfnms(raw);

    else if ((opc1 & b1011) == b1010)
        result = armv7_read_thumb_32_instr_a8_vfma_vfms(raw);

    else if ((opc1 & b1011) == b1011)
    {
        if ((opc3 & b01) == b00)
            result = armv7_read_thumb_32_instr_a8_vmov_immediate(raw);

        else if (opc2 == b0000)
        {
            if (opc3 == b01)
                result = armv7_read_thumb_32_instr_a8_vmov_register(raw);

            else if (opc3 == b11)
                result = armv7_read_thumb_32_instr_a8_vabs(raw);

        }

        else if (opc2 == b0001)
        {
            if (opc3 == b01)
                result = armv7_read_thumb_32_instr_a8_vneg(raw);

            else if (opc3 == b11)
                result = armv7_read_thumb_32_instr_a8_vsqrt(raw);

        }

        else if ((opc2 & b1110) == b0010 && (opc3 & b01) == b01)
                result = armv7_read_thumb_32_instr_a8_vcvtb_vcvtt(raw);

        else if ((opc2 & b1110) == b0100 && (opc3 & b01) == b01)
                result = armv7_read_thumb_32_instr_a8_vcmp_vcmpe(raw);

        else if (opc2 == b0111 && opc3 == b11)
                result = armv7_read_thumb_32_instr_a8_vcvt_between_double_precision_and_single_precision(raw);

        else if (opc2 == b1000 && (opc3 & b01) == b01)
                result = armv7_read_thumb_32_instr_a8_vcvt_vcvtr_between_floating_point_and_integer_floating_point(raw);

        else if ((opc2 & b1110) == b1010 && (opc3 & b01) == b01)
                result = armv7_read_thumb_32_instr_a8_vcvt_between_floating_point_and_fixed_point_floating_point(raw);

        else if ((opc2 & b1110) == b1100 && (opc3 & b01) == b01)
                result = armv7_read_thumb_32_instr_a8_vcvt_vcvtr_between_floating_point_and_integer_floating_point(raw);

        else if ((opc2 & b1110) == b1110 && (opc3 & b01) == b01)
                result = armv7_read_thumb_32_instr_a8_vcvt_between_floating_point_and_fixed_point_floating_point(raw);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 16 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A7.6.    *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_extension_register_load_store_instructions(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t opcode;                        /* Champ 'opcode' à retrouver  */
    uint32_t rn;                            /* Champ 'rn' à retrouver      */

    /**
     * Suit les directives de :
     * § A7.6 Extension register load/store instructions
     */

    if ((raw & 0xee000e00) != 0xec000a00) return NULL;

    result = NULL;

    opcode = (raw >> 20) & b11111;
    rn = (raw >> 16) & b1111;

    if ((opcode & b11110) == b00100)
        result = process_armv7_thumb_32_64_bit_transfers_between_arm_core_and_extension_registers(raw);

    else if ((opcode & b11011) == b01000)
        result = armv7_read_thumb_32_instr_a8_vstm(raw);

    else if ((opcode & b11011) == b01010)
        result = armv7_read_thumb_32_instr_a8_vstm(raw);

    else if ((opcode & b10011) == b10000)
        result = armv7_read_thumb_32_instr_a8_vstr(raw);

    else if ((opcode & b11011) == b10010)
    {
        if (rn != b1101)
            result = armv7_read_thumb_32_instr_a8_vstm(raw);

        else/* if (rn == b1101)*/
            result = armv7_read_thumb_32_instr_a8_vpush(raw);

    }

    else if ((opcode & b11011) == b01001)
        result = armv7_read_thumb_32_instr_a8_vldm(raw);

    else if ((opcode & b11011) == b01011)
    {
        if (rn != 1101)
            result = armv7_read_thumb_32_instr_a8_vldm(raw);

        else/* if (rn == 1101)*/
            result = armv7_read_thumb_32_instr_a8_vpop(raw);

    }

    else if ((opcode & b10011) == b10001)
        result = armv7_read_thumb_32_instr_a8_vldr(raw);

    else if ((opcode & b11011) == b10011)
        result = armv7_read_thumb_32_instr_a8_vldm(raw);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 16 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A7.7.    *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_advanced_simd_element_or_structure_load_store_instructions(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t a;                             /* Champ 'a' à retrouver       */
    uint32_t l;                             /* Champ 'l' à retrouver       */
    uint32_t b;                             /* Champ 'b' à retrouver       */

    /**
     * Suit les directives de :
     * § A7.7 Advanced SIMD element or structure load/store instructions
     */

    if ((raw & 0xff100000) != 0xf9000000) return NULL;

    result = NULL;

    a = (raw >> 23) & b1;
    l = (raw >> 21) & b1;
    b = (raw >> 8) & b1111;

    if (l == b0)
    {
        if (a == b0)
        {
            if (b == b0010)
                result = armv7_read_thumb_32_instr_a8_vst1_multiple_single_elements(raw);

            else if ((b & b1110) == b0110)
                result = armv7_read_thumb_32_instr_a8_vst1_multiple_single_elements(raw);

            else if (b == b1010)
                result = armv7_read_thumb_32_instr_a8_vst1_multiple_single_elements(raw);

            else if (b == b0011)
                result = armv7_read_thumb_32_instr_a8_vst2_multiple_2_element_structures(raw);

            else if ((b & b1110) == b1000)
                result = armv7_read_thumb_32_instr_a8_vst2_multiple_2_element_structures(raw);

            else if ((b & b1110) == b0100)
                result = armv7_read_thumb_32_instr_a8_vst3_multiple_3_element_structures(raw);

            else if ((b & b1110) == b0000)
                result = armv7_read_thumb_32_instr_a8_vst4_multiple_4_element_structures(raw);

        }

        else/* if (a == b1)*/
        {
            if ((b & b1011) == b0000)
                result = armv7_read_thumb_32_instr_a8_vst1_single_element_from_one_lane(raw);

            else if (b == b1000)
                result = armv7_read_thumb_32_instr_a8_vst1_single_element_from_one_lane(raw);

            else if ((b & b1011) == b0001)
                result = armv7_read_thumb_32_instr_a8_vst2_single_2_element_structure_from_one_lane(raw);

            else if (b == b1001)
                result = armv7_read_thumb_32_instr_a8_vst2_single_2_element_structure_from_one_lane(raw);

            else if ((b & b1011) == b0010)
                result = armv7_read_thumb_32_instr_a8_vst3_single_3_element_structure_from_one_lane(raw);

            else if (b == b1010)
                result = armv7_read_thumb_32_instr_a8_vst3_single_3_element_structure_from_one_lane(raw);

            else if ((b & b1011) == b0011)
                result = armv7_read_thumb_32_instr_a8_vst4_single_4_element_structure_from_one_lane(raw);

            else if (b == b1011)
                result = armv7_read_thumb_32_instr_a8_vst4_single_4_element_structure_from_one_lane(raw);

        }

    }

    else/* if (l == b1)*/
    {
        if (a == b0)
        {
            if (b == b0010)
                result = armv7_read_thumb_32_instr_a8_vld1_multiple_single_elements(raw);

            else if ((b & b1110) == b0110)
                result = armv7_read_thumb_32_instr_a8_vld1_multiple_single_elements(raw);

            else if (b == b1010)
                result = armv7_read_thumb_32_instr_a8_vld1_multiple_single_elements(raw);

            else if (b == b0011)
                result = armv7_read_thumb_32_instr_a8_vld2_multiple_2_element_structures(raw);

            else if ((b & b1110) == b1000)
                result = armv7_read_thumb_32_instr_a8_vld2_multiple_2_element_structures(raw);

            else if ((b & b1110) == b0100)
                result = armv7_read_thumb_32_instr_a8_vld3_multiple_3_element_structures(raw);

            else if ((b & b1110) == b0000)
                result = armv7_read_thumb_32_instr_a8_vld4_multiple_4_element_structures(raw);

        }

        else/* if (a == b1)*/
        {
            if ((b & b1011) == b0000)
                result = armv7_read_thumb_32_instr_a8_vld1_single_element_to_one_lane(raw);

            else if (b == b1000)
                result = armv7_read_thumb_32_instr_a8_vld1_single_element_to_one_lane(raw);

            else if (b == b1100)
                result = armv7_read_thumb_32_instr_a8_vld1_single_element_to_all_lanes(raw);

            else if ((b & b1011) == b0001)
                result = armv7_read_thumb_32_instr_a8_vld2_single_2_element_structure_to_one_lane(raw);

            else if (b == b1001)
                result = armv7_read_thumb_32_instr_a8_vld2_single_2_element_structure_to_one_lane(raw);

            else if (b == b1101)
                result = armv7_read_thumb_32_instr_a8_vld2_single_2_element_structure_to_all_lanes(raw);

            else if ((b & b1011) == b0010)
                result = armv7_read_thumb_32_instr_a8_vld3_single_3_element_structure_to_one_lane(raw);

            else if (b == b1010)
                result = armv7_read_thumb_32_instr_a8_vld3_single_3_element_structure_to_one_lane(raw);

            else if (b == b1110)
                result = armv7_read_thumb_32_instr_a8_vld3_single_3_element_structure_to_all_lanes(raw);

            else if ((b & b1011) == b0011)
                result = armv7_read_thumb_32_instr_a8_vld4_single_4_element_structure_to_one_lane(raw);

            else if (b == b1011)
                result = armv7_read_thumb_32_instr_a8_vld4_single_4_element_structure_to_one_lane(raw);

            else if (b == b1111)
                result = armv7_read_thumb_32_instr_a8_vld4_single_4_element_structure_to_all_lanes(raw);

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 16 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A7.8.    *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_8_16_and_32_bit_transfer_between_arm_core_and_extension_registers(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t a;                             /* Champ 'a' à retrouver       */
    uint32_t l;                             /* Champ 'l' à retrouver       */
    uint32_t c;                             /* Champ 'c' à retrouver       */
    uint32_t b;                             /* Champ 'b' à retrouver       */

    /**
     * Suit les directives de :
     * § A7.8 8, 16, and 32-bit transfer between ARM core and extension registers
     */

    if ((raw & 0xef000e10) != 0xee000a10) return NULL;

    result = NULL;

    a = (raw >> 21) & b111;
    l = (raw >> 20) & b1;
    c = (raw >> 8) & b1;
    b = (raw >> 5) & b11;

    if (l == b0)
    {
        if (c == b0)
        {
            if (a == b000)
                result = armv7_read_thumb_32_instr_a8_vmov_between_arm_core_register_and_single_precision_register(raw);

            else if (a == b111)
            {
                result = armv7_read_thumb_32_instr_a8_vmsr(raw); /* B9 ? */

                if (result == NULL /* ! */)
                    result = armv7_read_thumb_32_instr_b9_vmsr(raw);

            }

        }

        else/* if (c == b1)*/
        {
            if ((a & b100) == b000)
                result = armv7_read_thumb_32_instr_a8_vmov_arm_core_register_to_scalar(raw);

            else if (/*(a & b100) == b000) && */(b & b10) == b00)
                result = armv7_read_thumb_32_instr_a8_vdup_arm_core_register(raw);

        }

    }

    else/* if (l == b1)*/
    {
        if (c == b0)
        {
            if (a == b000)
                result = armv7_read_thumb_32_instr_a8_vmov_between_arm_core_register_and_single_precision_register(raw);

            else if (a == b111)
            {
                result = armv7_read_thumb_32_instr_a8_vmrs(raw); /* B9 ? */

                if (result == NULL /* ! */)
                    result = armv7_read_thumb_32_instr_b9_vmrs(raw);

            }

        }

        else/* if (c == b1)*/
            result = armv7_read_thumb_32_instr_a8_vmov_scalar_to_arm_core_register(raw);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 16 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A7.9.    *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_32_64_bit_transfers_between_arm_core_and_extension_registers(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t c;                             /* Champ 'c' à retrouver       */
    uint32_t op;                            /* Champ 'op' à retrouver      */

    /**
     * Suit les directives de :
     * § A7.9 64-bit transfers between ARM core and extension registers
     */

    if ((raw & 0xefe00e00) != 0xec400a00) return NULL;

    result = NULL;

    c = (raw >> 8) & b1;
    op = (raw >> 4) & b1111;

    if (c == b0 && (op & b1101) == 0001)
        result = armv7_read_thumb_32_instr_a8_vmov_between_two_arm_core_registers_and_two_single_precision_registers(raw);

    else if (c == b1 && (op & b1101) == 0001)
        result = armv7_read_thumb_32_instr_a8_vmov_between_two_arm_core_registers_and_a_doubleword_extension_register(raw);

    return result;

}
