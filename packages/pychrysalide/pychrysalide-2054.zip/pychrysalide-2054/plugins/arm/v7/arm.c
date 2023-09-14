
/* Chrysalide - Outil d'analyse de fichiers binaires
 * arm.c - désassemblage des instructions ARMv7
 *
 * Copyright (C) 2017-2019 Cyrille Bagard
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


#include "arm.h"


#include <stdint.h>


#include <arch/instructions/undefined.h>
#include <common/bconst.h>


#include "opcodes/arm_opcodes.h"
#include "opcodes/opcodes_tmp_arm.h"



/* Désassemble une instruction ARMv7 de données ou autre. */
static GArchInstruction *process_armv7_arm_data_processing_and_miscellaneous_instructions(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A5.2.1. */
static GArchInstruction *process_armv7_arm_data_processing_register(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A5.2.2. */
static GArchInstruction *process_armv7_arm_data_processing_register_shifted_register(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A5.2.3. */
static GArchInstruction *process_armv7_arm_data_processing_immediate(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A5.2.5. */
static GArchInstruction *process_armv7_arm_multiply_and_multiply_accumulate(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A5.2.6. */
static GArchInstruction *process_armv7_arm_saturating_addition_and_subtraction(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A5.2.7. */
static GArchInstruction *process_armv7_arm_halfword_multiply_and_multiply_accumulate(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A5.2.8. */
static GArchInstruction *process_armv7_arm_extra_load_store_instructions(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A5.2.9. */
static GArchInstruction *process_armv7_arm_extra_load_store_instructions_unprivileged(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A5.2.10. */
static GArchInstruction *process_armv7_arm_synchronization_primitives(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A5.2.11. */
static GArchInstruction *process_armv7_arm_msr_immediate_and_hints(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A5.2.12. */
static GArchInstruction *process_armv7_arm_miscellaneous_instructions(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A5.3. */
static GArchInstruction *process_armv7_arm_load_store_word_and_unsigned_byte(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A5.4. */
static GArchInstruction *process_armv7_arm_media_instructions(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A5.4.1. */
static GArchInstruction *process_armv7_arm_parallel_addition_and_subtraction_signed(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A5.4.2. */
static GArchInstruction *process_armv7_arm_parallel_addition_and_subtraction_unsigned(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A5.4.3. */
static GArchInstruction *process_armv7_arm_packing_unpacking_saturation_and_reversal(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A5.4.4. */
static GArchInstruction *process_armv7_arm_signed_multiply_signed_and_unsigned_divide(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A5.5. */
static GArchInstruction *process_armv7_arm_branch_branch_with_link_and_block_data_transfer(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A5.6. */
static GArchInstruction *process_armv7_arm_coprocessor_instructions_and_supervisor_call(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A5.7. */
static GArchInstruction *process_armv7_arm_unconditional_instructions(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A5.7.1. */
static GArchInstruction *process_armv7_arm_memory_hints_advanced_simd_instructions_and_miscellaneous_instructions(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A7.4. */
static GArchInstruction *process_armv7_arm_advanced_simd_data_processing_instructions(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A7.4.1. */
static GArchInstruction *process_armv7_arm_three_registers_of_the_same_length(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A7.4.2. */
static GArchInstruction *process_armv7_arm_three_registers_of_different_lengths(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A7.4.3. */
static GArchInstruction *process_armv7_arm_two_registers_and_a_scalar(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A7.4.4. */
static GArchInstruction *process_armv7_arm_two_registers_and_a_shift_amount(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A7.4.5. */
static GArchInstruction *process_armv7_arm_two_registers_miscellaneous(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A7.4.6. */
static GArchInstruction *process_armv7_arm_one_register_and_a_modified_immediate_value(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A7.5. */
static GArchInstruction *process_armv7_arm_floating_point_data_processing_instructions(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A7.6. */
static GArchInstruction *process_armv7_arm_extension_register_load_store_instructions(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A7.7. */
static GArchInstruction *process_armv7_arm_advanced_simd_element_or_structure_load_store_instructions(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A7.8. */
static GArchInstruction *process_armv7_arm_8_16_and_32_bit_transfer_between_arm_core_and_extension_registers(uint32_t);

/* Désassemble une instruction ARMv7 liées au chapitre A7.9. */
static GArchInstruction *process_armv7_arm_64_bit_transfers_between_arm_core_and_extension_registers(uint32_t);



/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A5.1.    *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *process_armv7_arm_instruction_set_encoding(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t cond;                          /* Champ 'cond' à retrouver    */
    uint32_t op1;                           /* Champ 'op1' à retrouver     */
    uint32_t op;                            /* Champ 'op' à retrouver      */

    /**
     * Suit les directives de :
     * § A5.1 ARM instruction set encoding
     */

    result = NULL;

    cond = (raw >> 28) & 0xf;
    op1 = (raw >> 25) & 0x7;
    op = (raw >> 4) & 0x1;

    if (cond != b1111)
    {
        if ((op1 & b110) == b000)
            result = process_armv7_arm_data_processing_and_miscellaneous_instructions(raw);

        else if (op1 == b010)
            result = process_armv7_arm_load_store_word_and_unsigned_byte(raw);

        else if (op1 == b011)
        {
            if (op == b0)
                result = process_armv7_arm_load_store_word_and_unsigned_byte(raw);

            else/* if (op == b1)*/
                result = process_armv7_arm_media_instructions(raw);

        }

        else if ((op1 & b110) == b100)
            result = process_armv7_arm_branch_branch_with_link_and_block_data_transfer(raw);

        else if ((op1 & b110) == b110)
            result = process_armv7_arm_coprocessor_instructions_and_supervisor_call(raw);

    }

    else /* if (cond == b1111) */
        result = process_armv7_arm_unconditional_instructions(raw);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 de données ou autre.       *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_arm_data_processing_and_miscellaneous_instructions(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    uint32_t op;                            /* Champ 'op' à retrouver      */
    uint32_t op1;                           /* Champ 'op1' à retrouver     */
    uint32_t op2;                           /* Champ 'op2' à retrouver     */

    /**
     * Suit les directives de :
     * § A5.2 Data-processing and miscellaneous instructions
     */

    result = NULL;

    op = (raw >> 25) & 0x1;
    op1 = (raw >> 20) & 0x1f;
    op2 = (raw >> 4) & 0xf;

    if (op == b0)
    {
        if ((op1 & b11001) != b10000)
        {
            if ((op2 & b0001) == b0000)
                result = process_armv7_arm_data_processing_register(raw);

            else if ((op2 & b1001) == b0001)
                result = process_armv7_arm_data_processing_register_shifted_register(raw);

            if (result != NULL) goto padpami_found;

        }

        else /* if ((op1 & b11001) == b10000) */
        {
            if ((op2 & b1000) == b0000)
                result = process_armv7_arm_miscellaneous_instructions(raw);

            else if ((op2 & b1001) == b1000)
                result = process_armv7_arm_halfword_multiply_and_multiply_accumulate(raw);

            if (result != NULL) goto padpami_found;

        }

        if ((op1 & b10000) == b00000)
        {
            if (op2 == b1001)
                result = process_armv7_arm_multiply_and_multiply_accumulate(raw);

            if (result != NULL) goto padpami_found;

        }

        if ((op1 & b10000) == b10000)
        {
            if (op2 == b1001)
                result = process_armv7_arm_synchronization_primitives(raw);

            if (result != NULL) goto padpami_found;

        }

        if ((op1 & b10010) != b00010)
        {
            if (op2 == b1011)
                result = process_armv7_arm_extra_load_store_instructions(raw);

            else if ((op2 & b1101) == b1101)
                result = process_armv7_arm_extra_load_store_instructions(raw);

            if (result != NULL) goto padpami_found;

        }

        else /* if ((op1 & b10010) != b00010) */
        {
            if (op2 == b1011)
                result = process_armv7_arm_extra_load_store_instructions_unprivileged(raw);

            else if ((op2 & b1101) == b1101)
                result = process_armv7_arm_extra_load_store_instructions(raw);

            if (result != NULL) goto padpami_found;

        }

    }

    else
    {
        if ((op1 & b11001) != b10000)
            result = process_armv7_arm_data_processing_immediate(raw);

        else if (op1 == b10000)
            result = armv7_read_arm_instr_a8_mov_immediate(raw);

        else if (op1 == b10100)
            result = armv7_read_arm_instr_a8_movt(raw);

        else if ((op1 & b11011) == b10010)
            result = process_armv7_arm_msr_immediate_and_hints(raw);

    }

 padpami_found:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A5.2.1.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_arm_data_processing_register(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    uint32_t op;                            /* Champ 'op' à retrouver      */
    uint32_t imm5;                          /* Champ 'imm5' à retrouver    */
    uint32_t op2;                           /* Champ 'op2' à retrouver     */

    /**
     * Suit les directives de :
     * § A5.2.1 Data-processing (register)
     */

    if ((raw & 0x0e000010) != 0x00000000) return NULL;

    result = NULL;

    op = (raw >> 20) & 0x1f;
    imm5 = (raw >> 7) & 0x1f;
    op2 = (raw >> 5) & 0x3;

    if ((op & b11110) == b00000)
        result = armv7_read_arm_instr_a8_and_register(raw);

    else if ((op & b11110) == b00010)
        result = armv7_read_arm_instr_a8_eor_register(raw);

    else if ((op & b11110) == b00100)
        result = armv7_read_arm_instr_a8_sub_register(raw);

    else if ((op & b11110) == b00110)
        result = armv7_read_arm_instr_a8_rsb_register(raw);

    else if ((op & b11110) == b01000)
        result = armv7_read_arm_instr_a8_add_register_arm(raw);

    else if ((op & b11110) == b01010)
        result = armv7_read_arm_instr_a8_adc_register(raw);

    else if ((op & b11110) == b01100)
        result = armv7_read_arm_instr_a8_sbc_register(raw);

    else if ((op & b11110) == b01110)
        result = armv7_read_arm_instr_a8_rsc_register(raw);

    /*
    else if ((op & b11001) == b10000)
        result = process_armv7_arm_data_processing_and_miscellaneous_instructions(raw);
    */

    else if (op == b10001)
        result = armv7_read_arm_instr_a8_tst_register(raw);

    else if (op == b10011)
        result = armv7_read_arm_instr_a8_teq_register(raw);

    else if (op == b10101)
        result = armv7_read_arm_instr_a8_cmp_register(raw);

    else if (op == b10111)
        result = armv7_read_arm_instr_a8_cmn_register(raw);

    else if ((op & b11110) == b11000)
        result = armv7_read_arm_instr_a8_orr_register(raw);

    else if ((op & b11110) == b11010)
    {
        if (op2 == b00)
        {
            if (imm5 == b00000)
                result = armv7_read_arm_instr_a8_mov_register_arm(raw);

            else
                result = armv7_read_arm_instr_a8_lsl_immediate(raw);

        }

        else if (op2 == b01)
            result = armv7_read_arm_instr_a8_lsr_immediate(raw);

        else if (op2 == b10)
            result = armv7_read_arm_instr_a8_asr_immediate(raw);

        else if (op2 == b11)
        {
            if (imm5 == b00000)
                result = armv7_read_arm_instr_a8_rrx(raw);

            else
                result = armv7_read_arm_instr_a8_ror_immediate(raw);

        }

     }

    else if ((op & b11110) == b11100)
        result = armv7_read_arm_instr_a8_bic_register(raw);

    else if ((op & b11110) == b11110)
        result = armv7_read_arm_instr_a8_mvn_register(raw);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A5.2.2.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_arm_data_processing_register_shifted_register(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    uint32_t op1;                           /* Champ 'op1' à retrouver     */
    uint32_t op2;                           /* Champ 'op2' à retrouver     */

    /**
     * Suit les directives de :
     * § A5.2.2 Data-processing (register-shifted register)
     */

    if ((raw & 0x0e000090) != 0x00000010) return NULL;

    result = NULL;

    op1 = (raw >> 20) & 0x1f;
    op2 = (raw >> 5) & 0x3;

    if ((op1 & b11110) == b00000)
        result = armv7_read_arm_instr_a8_and_register_shifted_register(raw);

    else if ((op1 & b11110) == b00010)
        result = armv7_read_arm_instr_a8_eor_register_shifted_register(raw);

    else if ((op1 & b11110) == b00100)
        result = armv7_read_arm_instr_a8_sub_register_shifted_register(raw);

    else if ((op1 & b11110) == b00110)
        result = armv7_read_arm_instr_a8_rsb_register_shifted_register(raw);

    else if ((op1 & b11110) == b01000)
        result = armv7_read_arm_instr_a8_add_register_shifted_register(raw);

    else if ((op1 & b11110) == b01010)
        result = armv7_read_arm_instr_a8_adc_register_shifted_register(raw);

    else if ((op1 & b11110) == b01100)
        result = armv7_read_arm_instr_a8_sbc_register_shifted_register(raw);

    else if ((op1 & b11110) == b01110)
        result = armv7_read_arm_instr_a8_rsc_register_shifted_register(raw);

#if 0
    else if ((op1 & b11001) == b10000)
        /* See Data-processing and miscellaneous instructions on page A5-196 */
#endif

    else if (op1 == b10001)
        result = armv7_read_arm_instr_a8_tst_register_shifted_register(raw);

    else if (op1 == b10011)
        result = armv7_read_arm_instr_a8_teq_register_shifted_register(raw);

    else if (op1 == b10101)
        result = armv7_read_arm_instr_a8_cmp_register_shifted_register(raw);

    else if (op1 == b10111)
        result = armv7_read_arm_instr_a8_cmn_register_shifted_register(raw);

    else if ((op1 & b11110) == b11000)
        result = armv7_read_arm_instr_a8_orr_register_shifted_register(raw);

    else if ((op1 & b11110) == b11010)
    {
        if (op2 == b00)
            result = armv7_read_arm_instr_a8_lsl_register(raw);

        else if (op2 == b01)
            result = armv7_read_arm_instr_a8_lsr_register(raw);

        else if (op2 == b10)
            result = armv7_read_arm_instr_a8_asr_register(raw);

        else if (op2 == b11)
            result = armv7_read_arm_instr_a8_ror_register(raw);

    }

    else if ((op1 & b11110) == b11100)
        result = armv7_read_arm_instr_a8_bic_register_shifted_register(raw);

    else if ((op1 & b11110) == b11110)
        result = armv7_read_arm_instr_a8_mvn_register_shifted_register(raw);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A5.2.3.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_arm_data_processing_immediate(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    uint32_t op;                            /* Champ 'op' à retrouver      */
    uint32_t rn;                            /* Champ 'rn' à retrouver      */

    /**
     * Suit les directives de :
     * § A5.2.3 Data-processing (immediate)
     */

    if ((raw & 0x0e000000) != 0x02000000) return NULL;

    result = NULL;

    op = (raw >> 20) & 0x1f;
    rn = (raw >> 16) & 0xf;

    if ((op & b11110) == b00000)
        result = armv7_read_arm_instr_a8_and_immediate(raw);

    else if ((op & b11110) == b00010)
        result = armv7_read_arm_instr_a8_eor_immediate(raw);

    else if ((op & b11110) == b00100)
    {
        if (rn == b1111)
            result = armv7_read_arm_instr_a8_adr(raw);

        else
            result = armv7_read_arm_instr_a8_sub_immediate_arm(raw);

    }

    else if ((op & b11110) == b00110)
        result = armv7_read_arm_instr_a8_rsb_immediate(raw);

    else if ((op & b11110) == b01000)
    {
        if (rn == b1111)
            result = armv7_read_arm_instr_a8_adr(raw);

        else
            result = armv7_read_arm_instr_a8_add_immediate_arm(raw);

    }

    else if ((op & b11110) == b01010)
        result = armv7_read_arm_instr_a8_adc_immediate(raw);

    else if ((op & b11110) == b01100)
        result = armv7_read_arm_instr_a8_sbc_immediate(raw);

    else if ((op & b11110) == b01110)
        result = armv7_read_arm_instr_a8_rsc_immediate(raw);

    /*
    else if ((op & b11110) == b10000)
        result = process_armv7_arm_data_processing_and_miscellaneous_instructions(raw);
    */

    else if (op == b10001)
        result = armv7_read_arm_instr_a8_tst_immediate(raw);

    else if (op == b10011)
        result = armv7_read_arm_instr_a8_teq_immediate(raw);

    else if (op == b10101)
        result = armv7_read_arm_instr_a8_cmp_immediate(raw);

    else if (op == b10111)
        result = armv7_read_arm_instr_a8_cmn_immediate(raw);

    else if ((op & b11110) == b11000)
        result = armv7_read_arm_instr_a8_orr_immediate(raw);

    else if ((op & b11110) == b11010)
        result = armv7_read_arm_instr_a8_mov_immediate(raw);

    else if ((op & b11110) == b11100)
        result = armv7_read_arm_instr_a8_bic_immediate(raw);

    else if ((op & b11110) == b11110)
        result = armv7_read_arm_instr_a8_mvn_immediate(raw);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A5.2.5.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_arm_multiply_and_multiply_accumulate(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    uint32_t op;                            /* Champ 'op' à retrouver      */

    /**
     * Suit les directives de :
     * § A5.2.5 Multiply and multiply accumulate
     */

    if ((raw & 0x0f0000f0) != 0x00000090) return NULL;

    result = NULL;

    op = (raw >> 20) & 0xf;

    if ((op & b1110) == b0000)
        result = armv7_read_arm_instr_a8_mul(raw);

    else if ((op & b1110) == b0010)
        result = armv7_read_arm_instr_a8_mla(raw);

    else if (op == b0100)
        result = armv7_read_arm_instr_a8_umaal(raw);

    else if (op == b0101)
        result = NULL;  /* Non défini */

    else if (op == b0110)
        result = armv7_read_arm_instr_a8_mls(raw);

    else if (op == b0111)
        result = NULL;  /* Non défini */

    else if ((op & b1110) == b1000)
        result = armv7_read_arm_instr_a8_umull(raw);

    else if ((op & b1110) == b1010)
        result = armv7_read_arm_instr_a8_umlal(raw);

    else if ((op & b1110) == b1100)
        result = armv7_read_arm_instr_a8_smull(raw);

    else if ((op & b1110) == b1110)
        result = armv7_read_arm_instr_a8_smlal(raw);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A5.2.6.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_arm_saturating_addition_and_subtraction(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    uint32_t op;                            /* Champ 'op' à retrouver      */

    /**
     * Suit les directives de :
     * § A5.2.6 Saturating addition and subtraction
     */

    if ((raw & 0x0f9000f0) != 0x01000050) return NULL;

    result = NULL;

    op = (raw >> 21) & 0x3;

    if (op == b00)
        result = armv7_read_arm_instr_a8_qadd(raw);

    else if (op == b01)
        result = armv7_read_arm_instr_a8_qsub(raw);

    else if (op == b10)
        result = armv7_read_arm_instr_a8_qdadd(raw);

    else if (op == b11)
        result = armv7_read_arm_instr_a8_qdsub(raw);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A5.2.7.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_arm_halfword_multiply_and_multiply_accumulate(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    uint32_t op1;                           /* Champ 'op1' à retrouver     */
    uint32_t op;                            /* Champ 'op' à retrouver      */

    /**
     * Suit les directives de :
     * § A5.2.7 Halfword multiply and multiply accumulate
     */

    if ((raw & 0x0f900090) != 0x01000080) return NULL;

    result = NULL;

    op1 = (raw >> 21) & 0x3;
    op = (raw >> 5) & 0x1;

    if (op1 == b00)
        result = armv7_read_arm_instr_a8_smlabb_smlabt_smlatb_smlatt(raw);

    else if (op1 == b01)
    {
        if (op == b0)
            result = armv7_read_arm_instr_a8_smlawb_smlawt(raw);

        else/* if (op == b1)*/
            result = armv7_read_arm_instr_a8_smulwb_smulwt(raw);

    }

    else if (op1 == b10)
        result = armv7_read_arm_instr_a8_smlalbb_smlalbt_smlaltb_smlaltt(raw);

    else if (op1 == b11)
        result = armv7_read_arm_instr_a8_smulbb_smulbt_smultb_smultt(raw);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A5.2.8.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_arm_extra_load_store_instructions(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    uint32_t op1;                           /* Champ 'op1' à retrouver     */
    uint32_t rn;                            /* Champ 'rn' à retrouver      */
    uint32_t op2;                           /* Champ 'op2' à retrouver     */

    /**
     * Suit les directives de :
     * § A5.2.8 Extra load/store instructions
     */

    if ((raw & 0x0e000090) != 0x00000090) return NULL;

    result = NULL;

    op1 = (raw >> 20) & 0x1f;
    rn = (raw >> 16) & 0xf;
    op2 = (raw >> 5) & 0x3;

    if (op2 == b01)
    {
        if ((op1 & b00101) == b00000)
            result = armv7_read_arm_instr_a8_strh_register(raw);

        else if ((op1 & b00101) == b00001)
            result = armv7_read_arm_instr_a8_ldrh_register(raw);

        else if ((op1 & b00101) == b00100)
            result = armv7_read_arm_instr_a8_strh_immediate_arm(raw);

        else/* if ((op1 & b00101) == b00101)*/
        {
            if (rn == b1111)
                result = armv7_read_arm_instr_a8_ldrh_literal(raw);

            else
                result = armv7_read_arm_instr_a8_ldrh_immediate_arm(raw);

        }

    }

    else if (op2 == b10)
    {
        if ((op1 & b00101) == b00000)
            result = armv7_read_arm_instr_a8_ldrd_register(raw);

        else if ((op1 & b00101) == b00001)
            result = armv7_read_arm_instr_a8_ldrsb_register(raw);

        else if ((op1 & b00101) == b00100)
        {
            if (rn == b1111)
                result = armv7_read_arm_instr_a8_ldrd_literal(raw);

            else
                result = armv7_read_arm_instr_a8_ldrd_immediate(raw);

        }

        else/* if ((op1 & b00101) == b00101)*/
        {
            if (rn == b1111)
                result = armv7_read_arm_instr_a8_ldrsb_literal(raw);

            else
                result = armv7_read_arm_instr_a8_ldrsb_immediate(raw);

        }

    }

    else if (op2 == b11)
    {
        if ((op1 & b00101) == b00000)
            result = armv7_read_arm_instr_a8_strd_register(raw);

        else if ((op1 & b00101) == b00001)
            result = armv7_read_arm_instr_a8_ldrsh_register(raw);

        else if ((op1 & b00101) == b00100)
            result = armv7_read_arm_instr_a8_strd_immediate(raw);

        else/* if ((op1 & b00101) == b00101)*/
        {
            if (rn == b1111)
                result = armv7_read_arm_instr_a8_ldrsh_literal(raw);

            else
                result = armv7_read_arm_instr_a8_ldrsh_immediate(raw);

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A5.2.9.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_arm_extra_load_store_instructions_unprivileged(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    uint32_t op;                            /* Champ 'op' à retrouver      */
    uint32_t op2;                           /* Champ 'op2' à retrouver     */

    /**
     * Suit les directives de :
     * § A5.2.9 Extra load/store instructions, unprivileged
     */

    if ((raw & 0x0f200090) != 0x00200090) return NULL;

    result = NULL;

    op = (raw >> 20) & 0x1;
    op2 = (raw >> 5) & 0x3;

    if (op2 == b01)
    {
        if (op == b0)
            result = armv7_read_arm_instr_a8_strht(raw);

        else/* if (op == b1)*/
            result = armv7_read_arm_instr_a8_ldrht(raw);

    }

    else if (op2 == b10)
    {
        if (op == b1)
            result = armv7_read_arm_instr_a8_ldrsbt(raw);

    }

    else if (op2 == b11)
    {
        if (op == b1)
            result = armv7_read_arm_instr_a8_ldrsht(raw);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A5.2.10. *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_arm_synchronization_primitives(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    uint32_t op;                            /* Champ 'op' à retrouver      */

    /**
     * Suit les directives de :
     * § A5.2.10 Synchronization primitives
     */

    if ((raw & 0x0f0000f0) != 0x01000090) return NULL;

    result = NULL;

    op = (raw >> 20) & 0xf;

    if ((op & b1011) == b0000)
        result = armv7_read_arm_instr_a8_swp_swpb(raw);

    else if (op == b1000)
        result = armv7_read_arm_instr_a8_strex(raw);

    else if (op == b1001)
        result = armv7_read_arm_instr_a8_ldrex(raw);

    else if (op == b1010)
        result = armv7_read_arm_instr_a8_strexd(raw);

    else if (op == b1011)
        result = armv7_read_arm_instr_a8_ldrexd(raw);

    else if (op == b1100)
        result = armv7_read_arm_instr_a8_strexb(raw);

    else if (op == b1101)
        result = armv7_read_arm_instr_a8_ldrexb(raw);

    else if (op == b1110)
        result = armv7_read_arm_instr_a8_strexh(raw);

    else if (op == b1111)
        result = armv7_read_arm_instr_a8_ldrexh(raw);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A5.2.11. *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_arm_msr_immediate_and_hints(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    uint32_t op;                            /* Champ 'op' à retrouver      */
    uint32_t op1;                           /* Champ 'op1' à retrouver     */
    uint32_t op2;                           /* Champ 'op2' à retrouver     */

    /**
     * Suit les directives de :
     * § A5.2.11 MSR (immediate), and hints
     */

    if ((raw & 0x0fb00000) != 0x03200000) return NULL;

    result = NULL;

    op = (raw >> 22) & 0x1;
    op1 = (raw >> 16) & 0xf;
    op2 = (raw >> 0) & 0x1;

    if (op == b0)
    {
        if (op1 == b0000)
        {
            if (op2 == b00000000)
                result = armv7_read_arm_instr_a8_nop(raw);

            else if (op2 == b00000001)
                result = armv7_read_arm_instr_a8_yield(raw);

            else if (op2 == b00000010)
                result = armv7_read_arm_instr_a8_wfe(raw);

            else if (op2 == b00000011)
                result = armv7_read_arm_instr_a8_wfi(raw);

            else if (op2 == b00000100)
                result = armv7_read_arm_instr_a8_sev(raw);

            else if ((op2 & b11110000) == b11110000)
                result = armv7_read_arm_instr_a8_dbg(raw);

        }

        else if (op1 == b0100 || (op1 & b1011) == b1000)
            result = armv7_read_arm_instr_a8_msr_immediate(raw);

        else if ((op1 & b0011) == b0001 || (op1 & b0010) == b0010)
            result = armv7_read_arm_instr_b9_msr_immediate(raw);

    }

    else/* if (op == b1)*/
        result = armv7_read_arm_instr_b9_msr_immediate(raw);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A5.2.12. *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_arm_miscellaneous_instructions(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    uint32_t op;                            /* Champ 'op' à retrouver      */
    uint32_t op1;                           /* Champ 'op1' à retrouver     */
    uint32_t b;                             /* Champ 'b' à retrouver       */
    uint32_t op2;                           /* Champ 'op2' à retrouver     */

    /**
     * Suit les directives de :
     * § A5.2.12 Miscellaneous instructions
     */

    if ((raw & 0x0f900080) != 0x01000000) return NULL;

    result = NULL;

    op = (raw >> 21) & 0x3;
    op1 = (raw >> 16) & 0xf;
    b = (raw >> 9) & 0x1;
    op2 = (raw >> 4) & 0x7;

    if (op2 == b000)
    {
        if (b == b1)
        {
            if ((op & b01) == b00)
                result = armv7_read_arm_instr_b9_mrs_banked_register(raw);

            else/* if ((op & b01) == b01)*/
                result = armv7_read_arm_instr_b9_msr_banked_register(raw);

        }
        else/* if (b == b0)*/
        {
            if ((op & b01) == b00)
                result = armv7_read_arm_instr_a8_mrs(raw); /* B9 ? */

            else if (op == b01)
            {
                if ((op1 & b0011) == b0000)
                    result = armv7_read_arm_instr_a8_msr_register(raw);

                else if ((op1 & b0011) == b0001 || (op1 & b0010) == b0010)
                    result = armv7_read_arm_instr_b9_msr_register(raw);

            }

            else if (op == b11)
                result = armv7_read_arm_instr_b9_msr_register(raw);

        }

    }

    else if (op2 == b001)
    {
        if (op == b01)
            result = armv7_read_arm_instr_a8_bx(raw);

        else if (op == b11)
            result = armv7_read_arm_instr_a8_clz(raw);

    }

    else if (op2 == b010)
    {
        if (op == b01)
            result = armv7_read_arm_instr_a8_bxj(raw);

    }

    else if (op2 == b011)
    {
        if (op == b01)
            result = armv7_read_arm_instr_a8_blx_register(raw);

    }

    else if (op2 == b101)
        result = process_armv7_arm_saturating_addition_and_subtraction(raw);

    else if (op2 == b110)
    {
        if (op == b11)
            result = armv7_read_arm_instr_b9_eret(raw);

    }

    else if (op2 == b111)
    {
        if (op == b)
            result = armv7_read_arm_instr_a8_bkpt(raw);

        else if (op == b)
            result = armv7_read_arm_instr_b9_hvc(raw);

        else if (op == b)
            result = armv7_read_arm_instr_b9_smc_previously_smi(raw);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A5.3.    *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_arm_load_store_word_and_unsigned_byte(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    uint32_t a;                             /* Champ 'a' à retrouver       */
    uint32_t op1;                           /* Champ 'op1' à retrouver     */
    uint32_t rn;                            /* Champ 'rn' à retrouver      */
    uint32_t b;                             /* Champ 'b' à retrouver       */

    /**
     * Suit les directives de :
     * § A5.3 Load/store word and unsigned byte
     */

    if ((raw & 0x0c000000) != 0x04000000) return NULL;

    result = NULL;

    a = (raw >> 25) & 0x1;
    op1 = (raw >> 20) & 0x1f;
    rn = (raw >> 16) & 0xf;
    b = (raw >> 4) & 0x1;

    if (a == b0)
    {
        if ((op1 & b00101) == b00000 && (op1 & b10111) != b00010)
            result = armv7_read_arm_instr_a8_str_immediate_arm(raw);

        else if ((op1 & b10111) == b00010)
            result = armv7_read_arm_instr_a8_strt(raw);

        else if ((op1 & b00101) == b00001 && (op1 & b10111) != b00011)
        {
            if (rn != b1111)
                result = armv7_read_arm_instr_a8_ldr_immediate_arm(raw);
            else
                result = armv7_read_arm_instr_a8_ldr_literal(raw);
        }

        else if ((op1 & b10111) == b00011)
            result = armv7_read_arm_instr_a8_ldrt(raw);

        else if ((op1 & b00101) == b00100 && (op1 & b10110) != b00110)
            result = armv7_read_arm_instr_a8_strb_immediate_arm(raw);

        else if ((op1 & b10110) == b00110)
            result = armv7_read_arm_instr_a8_strbt(raw);

        else if ((op1 & b00101) == b00101 && (op1 & b10111) != b00111)
        {
            if (rn != b1111)
                result = armv7_read_arm_instr_a8_ldrb_immediate_arm(raw);
            else
                result = armv7_read_arm_instr_a8_ldrb_literal(raw);
        }

        else if ((op1 & b10111) == b00111)
            result = armv7_read_arm_instr_a8_ldrbt(raw);

    }
    else /*if (a == b1)*/
    {
        if ((op1 & b00101) == b00000 && (op1 & b10111) != b00010 && b == b0)
            result = armv7_read_arm_instr_a8_str_register(raw);

        else if ((op1 & b10111) == b00010 && b == b0)
            result = armv7_read_arm_instr_a8_strt(raw);

        else if ((op1 & b00101) == b00001 && (op1 & b10111) != b00011 && b == b0)
            result = armv7_read_arm_instr_a8_ldr_register_arm(raw);

        else if ((op1 & b10111) == b00011 && b == b0)
            result = armv7_read_arm_instr_a8_ldrt(raw);

        else if ((op1 & b00101) == b00100 && (op1 & b10110) != b00110 && b == b0)
            result = armv7_read_arm_instr_a8_strb_register(raw);

        else if ((op1 & b10110) == b00110 && b == b0)
            result = armv7_read_arm_instr_a8_strbt(raw);

        else if ((op1 & b00101) == b00101 && (op1 & b10111) != b00111 && b == b0)
                result = armv7_read_arm_instr_a8_ldrb_register(raw);

        else if ((op1 & b10111) == b00111 && b == b0)
            result = armv7_read_arm_instr_a8_ldrbt(raw);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A5.4.    *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_arm_media_instructions(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    uint32_t cond;                          /* Champ 'cond' à retrouver    */
    uint32_t op1;                           /* Champ 'op1' à retrouver     */
    uint32_t rd;                            /* Champ 'rd' à retrouver      */
    uint32_t op2;                           /* Champ 'op2' à retrouver     */
    uint32_t rn;                            /* Champ 'rn' à retrouver      */

    /**
     * Suit les directives de :
     * § A5.4 Media instructions
     */

    if ((raw & 0x0e000010) != 0x06000010) return NULL;

    result = NULL;

    cond = (raw >> 28) & 0xf;
    op1 = (raw >> 20) & 0x1f;
    rd = (raw >> 12) & 0xf;
    op2 = (raw >> 5) & 0x7;
    rn = (raw >> 0) & 0xf;

    if ((op1 & b11100) == b00000)
        result = process_armv7_arm_parallel_addition_and_subtraction_signed(raw);

    else if ((op1 & b11100) == b00100)
        result = process_armv7_arm_parallel_addition_and_subtraction_unsigned(raw);

    else if ((op1 & b11000) == b01000)
        result = process_armv7_arm_packing_unpacking_saturation_and_reversal(raw);

    else if ((op1 & b11000) == b10000)
        result = process_armv7_arm_signed_multiply_signed_and_unsigned_divide(raw);

    else if (op1 == b11000)
    {
        if (op2 == b000)
        {
            if (rd == b1111)
                result = armv7_read_arm_instr_a8_usad8(raw);
            else
                result = armv7_read_arm_instr_a8_usada8(raw);
        }

        goto a54_done;

    }

    else if ((op1 & b11110) == b11010)
    {
        if ((op2 & b011) == b010)
            result = armv7_read_arm_instr_a8_sbfx(raw);

        goto a54_done;

    }

    else if ((op1 & b11110) == b11100)
    {
        if ((op2 & b011) == b000)
        {
            if (rn == b1111)
                result = armv7_read_arm_instr_a8_bfc(raw);
            else
                result = armv7_read_arm_instr_a8_bfi(raw);
        }

        goto a54_done;

    }

    else if ((op1 & b11110) == b11110)
    {
        if ((op2 & b011) == b010)
            result = armv7_read_arm_instr_a8_ubfx(raw);

        goto a54_done;

    }

    else if (op1 == b11111 && op2 == b111 && cond == b1110)
        result = armv7_read_arm_instr_a8_udf(raw);

 a54_done:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A5.4.1.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_arm_parallel_addition_and_subtraction_signed(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    uint32_t op1;                           /* Champ 'op1' à retrouver     */
    uint32_t op2;                           /* Champ 'op2' à retrouver     */

    /**
     * Suit les directives de :
     * § A5.4.1 Parallel addition and subtraction, signed
     */

    if ((raw & 0x0fc00010) != 0x06000010) return NULL;

    result = NULL;

    op1 = (raw >> 20) & 0x3;
    op2 = (raw >> 5) & 0x7;

    if (op1 == b01)
    {
        if (op2 == b000)
            result = armv7_read_arm_instr_a8_sadd16(raw);

        else if (op2 == b001)
            result = armv7_read_arm_instr_a8_sasx(raw);

        else if (op2 == b010)
            result = armv7_read_arm_instr_a8_ssax(raw);

        else if (op2 == b011)
            result = armv7_read_arm_instr_a8_ssub16(raw);

        else if (op2 == b100)
            result = armv7_read_arm_instr_a8_sadd8(raw);

        else if (op2 == b111)
            result = armv7_read_arm_instr_a8_ssub8(raw);

    }

    else if (op1 == b10)
    {
        if (op2 == b000)
            result = armv7_read_arm_instr_a8_qadd16(raw);

        else if (op2 == b001)
            result = armv7_read_arm_instr_a8_qasx(raw);

        else if (op2 == b010)
            result = armv7_read_arm_instr_a8_qsax(raw);

        else if (op2 == b011)
            result = armv7_read_arm_instr_a8_qsub16(raw);

        else if (op2 == b100)
            result = armv7_read_arm_instr_a8_qadd8(raw);

        else if (op2 == b111)
            result = armv7_read_arm_instr_a8_qsub8(raw);

    }

    else if (op1 == b11)
    {
        if (op2 == b000)
            result = armv7_read_arm_instr_a8_shadd16(raw);

        else if (op2 == b001)
            result = armv7_read_arm_instr_a8_shasx(raw);

        else if (op2 == b010)
            result = armv7_read_arm_instr_a8_shsax(raw);

        else if (op2 == b011)
            result = armv7_read_arm_instr_a8_shsub16(raw);

        else if (op2 == b100)
            result = armv7_read_arm_instr_a8_shadd8(raw);

        else if (op2 == b111)
            result = armv7_read_arm_instr_a8_shsub8(raw);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A5.4.2.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_arm_parallel_addition_and_subtraction_unsigned(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    uint32_t op1;                           /* Champ 'op1' à retrouver     */
    uint32_t op2;                           /* Champ 'op2' à retrouver     */

    /**
     * Suit les directives de :
     * § A5.4.2 Parallel addition and subtraction, unsigned
     */

    if ((raw & 0x0fc00010) != 0x06400010) return NULL;

    result = NULL;

    op1 = (raw >> 20) & 0x3;
    op2 = (raw >> 5) & 0x7;

    if (op1 == b01)
    {
        if (op2 == b000)
            result = armv7_read_arm_instr_a8_uadd16(raw);

        else if (op2 == b001)
            result = armv7_read_arm_instr_a8_uasx(raw);

        else if (op2 == b010)
            result = armv7_read_arm_instr_a8_usax(raw);

        else if (op2 == b011)
            result = armv7_read_arm_instr_a8_usub16(raw);

        else if (op2 == b100)
            result = armv7_read_arm_instr_a8_uadd8(raw);

        else if (op2 == b111)
            result = armv7_read_arm_instr_a8_usub8(raw);

    }

    else if (op1 == b10)
    {
        if (op2 == b000)
            result = armv7_read_arm_instr_a8_uqadd16(raw);

        else if (op2 == b001)
            result = armv7_read_arm_instr_a8_uqasx(raw);

        else if (op2 == b010)
            result = armv7_read_arm_instr_a8_uqsax(raw);

        else if (op2 == b011)
            result = armv7_read_arm_instr_a8_uqsub16(raw);

        else if (op2 == b100)
            result = armv7_read_arm_instr_a8_uqadd8(raw);

        else if (op2 == b111)
            result = armv7_read_arm_instr_a8_uqsub8(raw);

    }

    else if (op1 == b11)
    {
        if (op2 == b000)
            result = armv7_read_arm_instr_a8_uhadd16(raw);

        else if (op2 == b001)
            result = armv7_read_arm_instr_a8_uhasx(raw);

        else if (op2 == b010)
            result = armv7_read_arm_instr_a8_uhsax(raw);

        else if (op2 == b011)
            result = armv7_read_arm_instr_a8_uhsub16(raw);

        else if (op2 == b100)
            result = armv7_read_arm_instr_a8_uhadd8(raw);

        else if (op2 == b111)
            result = armv7_read_arm_instr_a8_uhsub8(raw);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A5.4.3.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_arm_packing_unpacking_saturation_and_reversal(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    uint32_t op1;                           /* Champ 'op1' à retrouver     */
    uint32_t a;                             /* Champ 'a' à retrouver       */
    uint32_t op2;                           /* Champ 'op2' à retrouver     */

    /**
     * Suit les directives de :
     * § A5.4.3 Packing, unpacking, saturation, and reversal
     */

    if ((raw & 0x0f800010) != 0x06800010) return NULL;

    result = NULL;

    op1 = (raw >> 20) & 0x7;
    a = (raw >> 16) & 0xf;
    op2 = (raw >> 5) & 0x7;

    if ((op1 & b111) == b000)
    {
        if ((op2 & b001) == b000)
        {
            result = armv7_read_arm_instr_a8_pkh(raw);
            goto a543_done;
        }
        else if (op2 == b011)
        {
            if (a == b1111)
            {
                result = armv7_read_arm_instr_a8_sxtb16(raw);
                goto a543_done;
            }
            else
            {
                result = armv7_read_arm_instr_a8_sxtab16(raw);
                goto a543_done;
            }
        }
        else if (op2 == b101)
        {
            result = armv7_read_arm_instr_a8_sel(raw);
            goto a543_done;
        }
    }

    else if ((op1 & b110) == b010 && (op2 & b001) == b000)
    {
        result = armv7_read_arm_instr_a8_ssat(raw);
        goto a543_done;
    }

    else if (op1 == b010)
    {
        if (op2 == b001)
        {
            result = armv7_read_arm_instr_a8_ssat16(raw);
            goto a543_done;
        }
        else if (op2 == b011)
        {
            if (a == b1111)
            {
                result = armv7_read_arm_instr_a8_sxtb(raw);
                goto a543_done;
            }
            else
            {
                result = armv7_read_arm_instr_a8_sxtab(raw);
                goto a543_done;
            }
        }
    }

    else if (op1 == b011)
    {
        if (op2 == b001)
        {
            result = armv7_read_arm_instr_a8_rev(raw);
            goto a543_done;
        }
        else if (op2 == b011)
        {
            if (a == b1111)
            {
                result = armv7_read_arm_instr_a8_sxth(raw);
                goto a543_done;
            }
            else
            {
                result = armv7_read_arm_instr_a8_sxtah(raw);
                goto a543_done;
            }
        }
        else if (op2 == b101)
        {
            result = armv7_read_arm_instr_a8_rev16(raw);
            goto a543_done;
        }
    }

    else if (op1 == b100 && op2 == b011)
    {
        if (a == b1111)
        {
            result = armv7_read_arm_instr_a8_uxtb16(raw);
            goto a543_done;
        }
        else
        {
            result = armv7_read_arm_instr_a8_uxtab16(raw);
            goto a543_done;
        }
    }

    else if ((op1 & b110) == b110 && (op2 & b001) == b000)
    {
        result = armv7_read_arm_instr_a8_usat(raw);
        goto a543_done;
    }

    else if (op1 == b110)
    {
        if (op2 == b001)
        {
            result = armv7_read_arm_instr_a8_usat16(raw);
            goto a543_done;
        }
        else if (op2 == b011)
        {
            if (a == b1111)
            {
                result = armv7_read_arm_instr_a8_uxtb(raw);
                goto a543_done;
            }
            else
            {
                result = armv7_read_arm_instr_a8_uxtab(raw);
                goto a543_done;
            }
        }
    }

    else if (op1 == b111)
    {
        if (op2 == b001)
        {
            result = armv7_read_arm_instr_a8_rbit(raw);
            goto a543_done;
        }
        else if (op2 == b011)
        {
            if (a == b1111)
            {
                result = armv7_read_arm_instr_a8_uxth(raw);
                goto a543_done;
            }
            else
            {
                result = armv7_read_arm_instr_a8_uxtah(raw);
                goto a543_done;
            }
        }
        else if (op2 == b101)
        {
            result = armv7_read_arm_instr_a8_revsh(raw);
            goto a543_done;
        }
    }

 a543_done:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A5.4.4.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_arm_signed_multiply_signed_and_unsigned_divide(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    uint32_t op1;                           /* Champ 'op1' à retrouver     */
    uint32_t a;                             /* Champ 'a' à retrouver       */
    uint32_t op2;                           /* Champ 'op2' à retrouver     */

    /**
     * Suit les directives de :
     * § A5.4.4 Signed multiply, signed and unsigned divide
     */

    if ((raw & 0x0f800010) != 0x07000010) return NULL;

    result = NULL;

    op1 = (raw >> 20) & 0x7;
    a = (raw >> 12) & 0xf;
    op2 = (raw >> 5) & 0x7;

    if (op1 == b000)
    {
        if ((op2 & b110) == b000)
        {
            if (a != b1111)
                result = armv7_read_arm_instr_a8_smlad(raw);
            else/* if (a == b1111)*/
                result = armv7_read_arm_instr_a8_smuad(raw);

        }

        else if ((op2 & b110) == b010)
        {
            if (a != b1111)
                result = armv7_read_arm_instr_a8_smlsd(raw);
            else/* if (a == b1111)*/
                result = armv7_read_arm_instr_a8_smusd(raw);

        }

    }

    else if (op1 == b001)
    {
        if (op2 == b000)
            result = armv7_read_arm_instr_a8_sdiv(raw);

    }

    else if (op1 == b011)
    {
        if (op2 == b000)
            result = armv7_read_arm_instr_a8_udiv(raw);

    }

    else if (op1 == b100)
    {
        if ((op2 & b110) == b000)
            result = armv7_read_arm_instr_a8_smlald(raw);

        else if ((op2 & b110) == b010)
            result = armv7_read_arm_instr_a8_smlsld(raw);

    }

    else if (op1 == b101)
    {
        if ((op2 & b110) == b000)
        {
            if (a != b1111)
                result = armv7_read_arm_instr_a8_smmla(raw);
            else/* if (a == b1111)*/
                result = armv7_read_arm_instr_a8_smmul(raw);

        }

        else if ((op2 & b110) == b110)
            result = armv7_read_arm_instr_a8_smmls(raw);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A5.5.    *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_arm_branch_branch_with_link_and_block_data_transfer(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    uint32_t op;                            /* Champ 'op' à retrouver      */
    uint32_t rn;                            /* Champ 'rn' à retrouver      */
    uint32_t r;                             /* Champ 'r' à retrouver       */

    /**
     * Suit les directives de :
     * § A5.5 Branch, branch with link, and block data transferr
     */

    if ((raw & 0x0c000000) != 0x08000000) return NULL;

    result = NULL;

    op = (raw >> 20) & 0x3f;
    rn = (raw >> 16) & 0xf;
    r = (raw >> 15) & 0x1;

    if ((op & b111101) == b000000)
        result = armv7_read_arm_instr_a8_stmda_stmed(raw);

    else if ((op & b111101) == b000001) 
        result = armv7_read_arm_instr_a8_ldmda_ldmfa(raw);

    else if ((op & b111101) == b001000)
        result = armv7_read_arm_instr_a8_stm_stmia_stmea(raw);

    else if (op == b001001)
        result = armv7_read_arm_instr_a8_ldm_ldmia_ldmfd_arm(raw);

    else if (op == b001011)
    {
        if (rn != b1101)
            result = armv7_read_arm_instr_a8_ldm_ldmia_ldmfd_arm(raw);
        else /* if (rn == b1101) */
            result = armv7_read_arm_instr_a8_pop_arm(raw);
     }

    else if (op == b010000)
        result = armv7_read_arm_instr_a8_stmdb_stmfd(raw);

    else if (op == b010010)
    {
        if (rn != b1101)
            result = armv7_read_arm_instr_a8_stmdb_stmfd(raw);
        else /* if (rn == b1101) */
            result = armv7_read_arm_instr_a8_push(raw);
    }

    else if ((op & b111101) == b010001)
        result = armv7_read_arm_instr_a8_ldmdb_ldmea(raw);

    else if ((op & b111101) == b011000)
        result = armv7_read_arm_instr_a8_stmib_stmfa(raw);

    else if ((op & b111101) == b011001)
        result = armv7_read_arm_instr_a8_ldmib_ldmed(raw);

    else if ((op & b100101) == b000100)
        result = armv7_read_arm_instr_b9_stm_user_registers(raw);

    else if ((op & b100101) == b000101)
    {
        if (r == b0)
            result = armv7_read_arm_instr_b9_ldm_user_registers(raw);
        else /* if (r == b1) */
            result = armv7_read_arm_instr_b9_ldm_exception_return(raw);
    }

    else if ((op & b110000) == b100000)
        result = armv7_read_arm_instr_a8_b(raw);

    else if ((op & b110000) == b110000)
        result = armv7_read_arm_instr_a8_bl_blx_immediate(raw);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A5.6.    *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_arm_coprocessor_instructions_and_supervisor_call(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    uint32_t op1;                           /* Champ 'op1' à retrouver     */
    uint32_t rn;                            /* Champ 'rn' à retrouver      */
    uint32_t coproc;                        /* Champ 'coproc' à retrouver      */
    uint32_t op;                            /* Champ 'op' à retrouver      */

    /**
     * Suit les directives de :
     * § A5.6 Coprocessor instructions, and Supervisor Call
     */

    if ((raw & 0x0c000000) != 0x0c000000) return NULL;

    result = NULL;

    op1 = (raw >> 20) & 0x3f;
    rn = (raw >> 16) & 0xf;
    coproc = (raw >> 8) & 0xf;
    op = (raw >> 4) & 0x1;

    if ((op1 & b111110) == b000000)
        result = g_undef_instruction_new(IEB_UNDEFINED);

    else if ((op1 & b110000) == b110000)
        result = armv7_read_arm_instr_a8_svc_previously_swi(raw);

    else if ((coproc & b1110) != b1010)
    {
        if ((op1 & b100001) == b000000 && (op1 & b111011) != b000000)
            result = armv7_read_arm_instr_a8_stc_stc2(raw);

        else if ((op1 & b100001) == b000001 && (op1 & b111011) != b000001)
        {
            if (rn != b1111)
                result = armv7_read_arm_instr_a8_ldc_ldc2_immediate(raw);
            else
                result = armv7_read_arm_instr_a8_ldc_ldc2_literal(raw);

        }

        else if (op1 == b000100)
            result = armv7_read_arm_instr_a8_mcrr_mcrr2(raw);

        else if (op1 == b000101)
            result = armv7_read_arm_instr_a8_mrrc_mrrc2(raw);


        else if ((op1 & b110000) == b100000 && op == b0)
            result = armv7_read_arm_instr_a8_cdp_cdp2(raw);

        else if ((op1 & b110001) == b100000 && op == b1)
            result = armv7_read_arm_instr_a8_mcr_mcr2(raw);

        else if ((op1 & b110001) == b100001 && op == b1)
            result = armv7_read_arm_instr_a8_mrc_mrc2(raw);

    }

    else if ((coproc & b1110) == b1010)
    {
        if ((op1 & b100000) == b000000 && (op1 & b111010) != b000000)
            result = process_armv7_arm_extension_register_load_store_instructions(raw);

        else if ((op1 & b111110) == b000100)
            result = process_armv7_arm_64_bit_transfers_between_arm_core_and_extension_registers(raw);

        else if ((op1 & b110000) == b100000)
        {
            if (op == b0)
                result = process_armv7_arm_floating_point_data_processing_instructions(raw);

            else/* if (op == b1) */
                result = process_armv7_arm_8_16_and_32_bit_transfer_between_arm_core_and_extension_registers(raw);

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A5.7.    *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_arm_unconditional_instructions(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    uint32_t op1;                           /* Champ 'op1' à retrouver     */
    uint32_t rn;                            /* Champ 'rn' à retrouver      */
    uint32_t op;                            /* Champ 'op' à retrouver      */

    /**
     * Suit les directives de :
     * § A5.7 Unconditional instructions
     */

    if ((raw & 0xf0000000) != 0xf0000000) return NULL;

    result = NULL;

    op1 = (raw >> 20) & 0xff;
    rn = (raw >> 16) & 0xf;
    op = (raw >> 4) & 0x1;

    if ((op1 & b10000000) == b00000000)
        result = process_armv7_arm_memory_hints_advanced_simd_instructions_and_miscellaneous_instructions(raw);

    else if ((op1 & b11100101) == b10000100)
        result = armv7_read_arm_instr_b9_srs_arm(raw);

    else if ((op1 & b11100101) == b10000001)
        result = armv7_read_arm_instr_b9_rfe(raw);

    else if ((op1 & b11100000) == b10100000)
        result = armv7_read_arm_instr_a8_bl_blx_immediate(raw);

    else if ((op1 & b11100001) == b11000000 && (op1 & b11111011) != b11000000)
        result = armv7_read_arm_instr_a8_stc_stc2(raw);

    else if ((op1 & b11100001) == b11000001 && (op1 & b11111011) != b11000001)
    {
        if (rn != b1111)
            result = armv7_read_arm_instr_a8_ldc_ldc2_immediate(raw);
        else/* if (rn == b1111)*/
            result = armv7_read_arm_instr_a8_ldc_ldc2_literal(raw);
    }

    else if (op1 == b11000100)
        result = armv7_read_arm_instr_a8_mcrr_mcrr2(raw);

    else if (op1 == b11000101)
        result = armv7_read_arm_instr_a8_mrrc_mrrc2(raw);

    else if ((op1 & b11110000) == b11100000 && op == b0)
        result = armv7_read_arm_instr_a8_cdp_cdp2(raw);

    else if ((op1 & b11110001) == b11100000 && op == b1)
        result = armv7_read_arm_instr_a8_mcr_mcr2(raw);

    else if ((op1 & b11110001) == b11100001 && op == b1)
        result = armv7_read_arm_instr_a8_mrc_mrc2(raw);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 32 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A5.7.1.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_arm_memory_hints_advanced_simd_instructions_and_miscellaneous_instructions(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    uint32_t op1;                           /* Champ 'op1' à retrouver     */
    uint32_t rn;                            /* Champ 'rn' à retrouver      */
    uint32_t op2;                           /* Champ 'op2' à retrouver     */

    /**
     * Suit les directives de :
     * § A5.7.1 Memory hints, Advanced SIMD instructions, and miscellaneous instructions
     */

    if ((raw & 0xf8000000) != 0xf0000000) return NULL;

    result = NULL;

    op1 = (raw >> 20) & 0x7f;
    rn = (raw >> 16) & 0xf;
    op2 = (raw >> 4) & 0xf;

    if (op1 == b0010000)
    {
        if ((op2 & b0010) == b0000 && (rn & b0001) == b0000)
            result = armv7_read_arm_instr_b9_cps_arm(raw);

        else if (op2 == b0000 && (rn & b0001) == b0001)
            result = armv7_read_arm_instr_a8_setend(raw);

    }

    else if ((op1 & b1100000) == b0100000)
        result = process_armv7_arm_advanced_simd_data_processing_instructions(raw);

    else if ((op1 & b1110001) == b1000000)
        result = process_armv7_arm_advanced_simd_element_or_structure_load_store_instructions(raw);

    else if ((op1 & b1110111) == b1000001)
        result = g_undef_instruction_new(IEB_NOP);

    else if ((op1 & b1110111) == b1000101)
        result = armv7_read_arm_instr_a8_pli_immediate_literal(raw);

    else if ((op1 & b1110011) == b1000011)
        result = g_undef_instruction_new(IEB_UNPREDICTABLE);

    else if ((op1 & b1110111) == b1010101)
    {
        if (rn != b1111)
            result = armv7_read_arm_instr_a8_pld_pldw_immediate(raw);
        else
            result = g_undef_instruction_new(IEB_UNPREDICTABLE);

    }

    else if ((op1 & b1110111) == b1010101)
    {
        if (rn != b1111)
            result = armv7_read_arm_instr_a8_pld_pldw_immediate(raw);
        else
            result = armv7_read_arm_instr_a8_pld_literal(raw);

    }

    else if (op1 == b1010011)
        result = g_undef_instruction_new(IEB_UNPREDICTABLE);

    else if (op1 == b1010111)
    {
        if (op2 == b0000)
            result = g_undef_instruction_new(IEB_UNPREDICTABLE);

        else if (op2 == b0001)
            result = armv7_read_arm_instr_a8_clrex(raw);

        else if ((op2 & b1110) == b0010)
            result = g_undef_instruction_new(IEB_UNPREDICTABLE);

        else if (op2 == b0100)
            result = armv7_read_arm_instr_a8_dsb(raw);

        else if (op2 == b0101)
            result = armv7_read_arm_instr_a8_dmb(raw);

        else if (op2 == b0110)
            result = armv7_read_arm_instr_a8_isb(raw);

        else if (op2 == b0111)
            result = g_undef_instruction_new(IEB_UNPREDICTABLE);

        else if ((op2 & b1000) == b1000)
            result = g_undef_instruction_new(IEB_UNPREDICTABLE);

    }

    else if ((op1 & b1111011) == b1011011)
        result = g_undef_instruction_new(IEB_UNPREDICTABLE);

    else if ((op1 & b1110111) == b1100001 && (op2 & b0001) == b0000)
        result = g_undef_instruction_new(IEB_NOP);

    else if ((op1 & b1110111) == b1100101 && (op2 & b0001) == b0000)
        result = armv7_read_arm_instr_a8_pli_register(raw);

    else if ((op1 & b1110111) == b1110001 && (op2 & b0001) == b0000)
        result = armv7_read_arm_instr_a8_pld_pldw_register(raw);

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

static GArchInstruction *process_armv7_arm_advanced_simd_data_processing_instructions(uint32_t raw)
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

    if ((raw & 0xfe000000) != 0xf2000000) return NULL;

    result = NULL;

    u = (raw >> 24) & b1;
    a = (raw >> 19) & b11111;
    b = (raw >> 8) & b1111;
    c = (raw >> 4) & b1111;

    if ((a & b10000) == b00000)
        result = process_armv7_arm_three_registers_of_the_same_length(raw);

    else if ((a & b10111) == b10000 && (c & b1001) == b0001)
        result = process_armv7_arm_one_register_and_a_modified_immediate_value(raw);

    else if ((a & b10111) == b10001 && (c & b1001) == b0001)
        result = process_armv7_arm_two_registers_and_a_shift_amount(raw);

    else if ((a & b10110) == b10010 && (c & b1001) == b0001)
        result = process_armv7_arm_two_registers_and_a_shift_amount(raw);

    else if ((a & b10100) == b10100 && (c & b1001) == b0001)
        result = process_armv7_arm_two_registers_and_a_shift_amount(raw);

    else if ((a & b10000) == b10000 && (c & b1001) == b1001)
        result = process_armv7_arm_two_registers_and_a_shift_amount(raw);

    else if ((a & b10100) == b10000 && (c & b0101) == b0000)
        result = process_armv7_arm_three_registers_of_different_lengths(raw);

    else if ((a & b10110) == b10100 && (c & b0101) == b0000)
        result = process_armv7_arm_three_registers_of_different_lengths(raw);

    else if ((a & b10100) == b10000 && (c & b0101) == b0100)
        result = process_armv7_arm_two_registers_and_a_scalar(raw);

    else if ((a & b10110) == b10100 && (c & b0101) == b0100)
        result = process_armv7_arm_two_registers_and_a_scalar(raw);

    else if (u == b0 && (a & b10110) == b10110 && (c & b0001) == b0000)
        result = armv7_read_arm_instr_a8_vext(raw);

    else if (u == b1 && (a & b10110) == b10110)
    {
        if ((b & b1000) == b0000 && (c & b0001) == b0000)
            result = process_armv7_arm_two_registers_miscellaneous(raw);

        else if ((b & b1100) == b1000 && (c & b0001) == b0000)
            result = armv7_read_arm_instr_a8_vtbl_vtbx(raw);

        else if (b == b1100 && (c & b1001) == b0000)
            result = armv7_read_arm_instr_a8_vdup_scalar(raw);

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

static GArchInstruction *process_armv7_arm_three_registers_of_the_same_length(uint32_t raw)
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

    if ((raw & 0xfe800000) != 0xf2000000) return NULL;

    result = NULL;

    u = (raw >> 24) & b1;
    c = (raw >> 20) & b11;
    a = (raw >> 8) & b1111;
    b = (raw >> 4) & b1;

    if (a == b0000)
    {
        if (b == b0)
            result = armv7_read_arm_instr_a8_vhadd_vhsub(raw);

        else/* if (b == b1)*/
            result = armv7_read_arm_instr_a8_vqadd(raw);

    }

    else if (a == b0001)
    {
        if (b == b0)
            result = armv7_read_arm_instr_a8_vrhadd(raw);

        else/* if (b == b1)*/
        {
            if (u == b0)
                switch (c)
                {
                    case b00:
                        result = armv7_read_arm_instr_a8_vand_register(raw);
                        break;

                    case b01:
                        result = armv7_read_arm_instr_a8_vbic_register(raw);
                        break;

                    case b10:
                        /* Cf. vmov_register aussi */
                        result = armv7_read_arm_instr_a8_vorr_register(raw);
                        break;

                     case b11:
                        result = armv7_read_arm_instr_a8_vorn_register(raw);
                        break;

                }

            else/* if (u == b1)*/
                switch (c)
                {
                    case b00:
                        result = armv7_read_arm_instr_a8_veor(raw);
                        break;

                    case b01:
                        result = armv7_read_arm_instr_a8_vbif_vbit_vbsl(raw);
                        break;

                    case b10:
                        result = armv7_read_arm_instr_a8_vbif_vbit_vbsl(raw);
                        break;

                     case b11:
                        result = armv7_read_arm_instr_a8_vbif_vbit_vbsl(raw);
                        break;

                }

        }

    }

    else if (a == b0010)
    {
        if (b == b0)
            result = armv7_read_arm_instr_a8_vhadd_vhsub(raw);

        else/* if (b == b1)*/
            result = armv7_read_arm_instr_a8_vqsub(raw);

    }

    else if (a == b0011)
    {
        if (b == b0)
            result = armv7_read_arm_instr_a8_vcgt_register(raw);

        else/* if (b == b1)*/
            result = armv7_read_arm_instr_a8_vcge_register(raw);

    }

    else if (a == b0100)
    {
        if (b == b0)
            result = armv7_read_arm_instr_a8_vshl_register(raw);

        else/* if (b == b1)*/
            result = armv7_read_arm_instr_a8_vqshl_register(raw);

    }

    else if (a == b0101)
    {
        if (b == b0)
            result = armv7_read_arm_instr_a8_vrshl(raw);

        else/* if (b == b1)*/
            result = armv7_read_arm_instr_a8_vqrshl(raw);

    }

    else if (a == b0110)
        result = armv7_read_arm_instr_a8_vmax_vmin_integer(raw);

    else if (a == b0111)
    {
        if (b == b0)
            result = armv7_read_arm_instr_a8_vabd_vabdl_integer(raw);

        else/* if (b == b1)*/
            result = armv7_read_arm_instr_a8_vaba_vabal(raw);

    }

    else if (a == b1000)
    {
        if (b == b0)
        {
            if (u == b0)
                result = armv7_read_arm_instr_a8_vadd_integer(raw);

            else/* if (u == b1)*/
                result = armv7_read_arm_instr_a8_vsub_integer(raw);

        }

        else/* if (b == b1)*/
        {
            if (u == b0)
                result = armv7_read_arm_instr_a8_vtst(raw);

            else/* if (u == b1)*/
                result = armv7_read_arm_instr_a8_vceq_register(raw);

        }

    }

    else if (a == b1001)
    {
        if (b == b0)
            result = armv7_read_arm_instr_a8_vmla_vmlal_vmls_vmlsl_integer(raw);

        else/* if (b == b1)*/
            result = armv7_read_arm_instr_a8_vmul_vmull_integer_and_polynomial(raw);

    }

    else if (a == b1010)
        result = armv7_read_arm_instr_a8_vpmax_vpmin_integer(raw);

    else if (a == b1011)
    {
        if (b == b0)
        {
            if (u == b0)
                result = armv7_read_arm_instr_a8_vqdmulh(raw);

            else/* if (u == b1)*/
                result = armv7_read_arm_instr_a8_vqrdmulh(raw);

        }

        else/* if (b == b1)*/
        {
            if (u == b0)
                result = armv7_read_arm_instr_a8_vpadd_integer(raw);

        }

    }

    else if (a == b1100)
    {
        if (b == b1 && u == b0)
            result = armv7_read_arm_instr_a8_vfma_vfms(raw);

    }

    else if (a == b1101)
    {
        if (b == b0)
        {
            if (u == b0)
            {
                if ((c & b10) == b00)
                    result = armv7_read_arm_instr_a8_vadd_floating_point(raw);

                else/* if ((c & b10) == b10)*/
                    result = armv7_read_arm_instr_a8_vsub_floating_point(raw);

            }

            else/* if (u == b1)*/
            {
                if ((c & b10) == b00)
                    result = armv7_read_arm_instr_a8_vpadd_floating_point(raw);

                else/* if ((c & b10) == b10)*/
                    result = armv7_read_arm_instr_a8_vabd_floating_point(raw);

            }

        }

        else/* if (b == b1)*/
        {
            if (u == b0)
                result = armv7_read_arm_instr_a8_vmla_vmls_floating_point(raw);

            else/* if (u == b1)*/
            {
                if ((c & b10) == b00)
                    result = armv7_read_arm_instr_a8_vmul_floating_point(raw);

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
                    result = armv7_read_arm_instr_a8_vceq_register(raw);

            }

            else/* if (u == b1)*/
            {
                if ((c & b10) == b00)
                    result = armv7_read_arm_instr_a8_vcge_register(raw);

                else/* if ((c & b10) == b10)*/
                    result = armv7_read_arm_instr_a8_vcgt_register(raw);

            }

        }

        else/* if (b == b1)*/
        {
            if (u == b1)
                result = armv7_read_arm_instr_a8_vacge_vacgt_vacle_vaclt(raw);

        }

    }

    else if (a == b1111)
    {
        if (b == b0)
        {
            if (u == b0)
                result = armv7_read_arm_instr_a8_vmax_vmin_floating_point(raw);

            else/* if (u == b1)*/
                result = armv7_read_arm_instr_a8_vpmax_vpmin_floating_point(raw);

        }

        else/* if (b == b1)*/
        {
            if (u == b0)
            {
                if ((c & b10) == b00)
                    result = armv7_read_arm_instr_a8_vrecps(raw);

                else/* if ((c & b10) == b10)*/
                    result = armv7_read_arm_instr_a8_vrsqrts(raw);

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

static GArchInstruction *process_armv7_arm_three_registers_of_different_lengths(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t u;                             /* Champ 'u' à retrouver       */
    uint32_t a;                             /* Champ 'a' à retrouver       */

    /**
     * Suit les directives de :
     * § A7.4.2 Three registers of different lengths
     */

    if ((raw & 0xfe800050) != 0xf2800000) return NULL;

    result = NULL;

    u = (raw >> 24) & b1;
    a = (raw >> 8) & b1111;

    if ((a & b1110) == b0000)
        result = armv7_read_arm_instr_a8_vaddl_vaddw(raw);

    else if ((a & b1110) == b0010)
        result = armv7_read_arm_instr_a8_vsubl_vsubw(raw);

    else if (a == b0100)
    {
        if (u == b0)
            result = armv7_read_arm_instr_a8_vaddhn(raw);

        else/* if (u == b1)*/
            result = armv7_read_arm_instr_a8_vraddhn(raw);

    }

    else if (a == b0101)
        result = armv7_read_arm_instr_a8_vaba_vabal(raw);

    else if (a == b0110)
    {
        if (u == b0)
            result = armv7_read_arm_instr_a8_vsubhn(raw);

        else/* if (u == b1)*/
            result = armv7_read_arm_instr_a8_vrsubhn(raw);

    }

    else if (a == b0111)
        result = armv7_read_arm_instr_a8_vabd_vabdl_integer(raw);

    else if ((a & b1101) == b1000)
        result = armv7_read_arm_instr_a8_vmla_vmlal_vmls_vmlsl_integer(raw);

    else if ((a & b1101) == b1001)
    {
        if (u == b0)
            result = armv7_read_arm_instr_a8_vqdmlal_vqdmlsl(raw);

    }

    else if (a == b1100)
        result = armv7_read_arm_instr_a8_vmul_vmull_integer_and_polynomial(raw);

    else if (a == b1101)
    {
        if (u == b0)
            result = armv7_read_arm_instr_a8_vqdmull(raw);

    }

    else if (a == b1110)
        result = armv7_read_arm_instr_a8_vmul_vmull_integer_and_polynomial(raw);

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

static GArchInstruction *process_armv7_arm_two_registers_and_a_scalar(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t u;                             /* Champ 'u' à retrouver       */
    uint32_t a;                             /* Champ 'a' à retrouver       */

    /**
     * Suit les directives de :
     * § A7.4.3 Two registers and a scalar
     */

    if ((raw & 0xfe800050) != 0xf2800040) return NULL;

    result = NULL;

    u = (raw >> 24) & b1;
    a = (raw >> 8) & b1111;

    if ((a & b1010) == b0000)
        result = armv7_read_arm_instr_a8_vmla_vmlal_vmls_vmlsl_by_scalar(raw);

    else if ((a & b1010) == b0010)
        result = armv7_read_arm_instr_a8_vmla_vmlal_vmls_vmlsl_by_scalar(raw);

    else if ((a & b1011) == b0011 && u == b0)
        result = armv7_read_arm_instr_a8_vqdmlal_vqdmlsl(raw);

    else if ((a & b1110) == b1000)
        result = armv7_read_arm_instr_a8_vmul_vmull_by_scalar(raw);

    else if (a == b1010)
        result = armv7_read_arm_instr_a8_vmul_vmull_by_scalar(raw);

    else if (a == b1011 && u == b0)
        result = armv7_read_arm_instr_a8_vqdmull(raw);

    else if (a == b1100)
        result = armv7_read_arm_instr_a8_vqdmulh(raw);

    else if (a == b1101)
        result = armv7_read_arm_instr_a8_vqrdmulh(raw);

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

static GArchInstruction *process_armv7_arm_two_registers_and_a_shift_amount(uint32_t raw)
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

    if ((raw & 0xfe800010) != 0xf2800010) return NULL;

    result = NULL;

    u = (raw >> 24) & b1;
    a = (raw >> 8) & b1111;
    l = (raw >> 7) & b1;
    b = (raw >> 6) & b1;

    if (a == b0000)
        result = armv7_read_arm_instr_a8_vshr(raw);

    else if (a == b0001)
        result = armv7_read_arm_instr_a8_vsra(raw);

    else if (a == b0010)
        result = armv7_read_arm_instr_a8_vrshr(raw);

    else if (a == b0011)
        result = armv7_read_arm_instr_a8_vrsra(raw);

    else if (a == b0100 && u == b1)
        result = armv7_read_arm_instr_a8_vsri(raw);

    else if (a == b0101)
    {
        if (u == b0)
            result = armv7_read_arm_instr_a8_vshl_immediate(raw);

        else/* if (u == b1)*/
            result = armv7_read_arm_instr_a8_vsli(raw);

    }

    else if ((a & b1110) == b0110)
        result = armv7_read_arm_instr_a8_vqshl_vqshlu_immediate(raw);

    else if (a == b1000)
    {
        if (u == b0)
        {
            if (b == b0 && l == b0)
                result = armv7_read_arm_instr_a8_vshrn(raw);

            else if (b == b1 && l == b0)
                result = armv7_read_arm_instr_a8_vrshrn(raw);

        }
        else/* if (u == b1)*/
        {
            if (b == b0 && l == b0)
                result = armv7_read_arm_instr_a8_vqshrn_vqshrun(raw);

            else if (b == b1 && l == b0)
                result = armv7_read_arm_instr_a8_vqrshrn_vqrshrun(raw);

        }

    }

    else if (a == b1001)
    {
        if (b == b0 && l == b0)
            result = armv7_read_arm_instr_a8_vqshrn_vqshrun(raw);

        else if (b == b1 && l == b0)
            result = armv7_read_arm_instr_a8_vqrshrn_vqrshrun(raw);

    }

    else if (a == b1010 && b == b0 && l == b0)
    {
        result = armv7_read_arm_instr_a8_vshll(raw);

        /* ??? */
        if (result == NULL)
            result = armv7_read_arm_instr_a8_vmovl(raw);

    }

    else if ((a & b1110) == b1110 && l == b0)
        result = armv7_read_arm_instr_a8_vcvt_between_floating_point_and_fixed_point_advanced_simd(raw);

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

static GArchInstruction *process_armv7_arm_two_registers_miscellaneous(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t a;                             /* Champ 'a' à retrouver       */
    uint32_t b;                             /* Champ 'b' à retrouver       */

    /**
     * Suit les directives de :
     * § A7.4.5 Two registers, miscellaneous
     */

    if ((raw & 0xffb00810) != 0xf3b00000) return NULL;

    result = NULL;

    a = (raw >> 16) & b11;
    b = (raw >> 6) & b11111;

    if (a == b00)
    {
        if ((b & b11110) == b00000)
            result = armv7_read_arm_instr_a8_vrev16_vrev32_vrev64(raw);

        else if ((b & b11110) == b00010)
            result = armv7_read_arm_instr_a8_vrev16_vrev32_vrev64(raw);

        else if ((b & b11110) == b00100)
            result = armv7_read_arm_instr_a8_vrev16_vrev32_vrev64(raw);

        else if ((b & b11100) == b01000)
            result = armv7_read_arm_instr_a8_vpaddl(raw);

        else if ((b & b11110) == b10000)
            result = armv7_read_arm_instr_a8_vcls(raw);

        else if ((b & b11110) == b10010)
            result = armv7_read_arm_instr_a8_vclz(raw);

        else if ((b & b11110) == b10100)
            result = armv7_read_arm_instr_a8_vcnt(raw);

        else if ((b & b11110) == b10110)
            result = armv7_read_arm_instr_a8_vmvn_register(raw);

        else if ((b & b11100) == b11000)
            result = armv7_read_arm_instr_a8_vpadal(raw);

        else if ((b & b11110) == b11100)
            result = armv7_read_arm_instr_a8_vqabs(raw);

        else if ((b & b11110) == b11110)
            result = armv7_read_arm_instr_a8_vqneg(raw);

    }

    else if (a == b01)
    {
        if ((b & b01110) == b00000)
            result = armv7_read_arm_instr_a8_vcgt_immediate_0(raw);

        else if ((b & b01110) == b00010)
            result = armv7_read_arm_instr_a8_vcge_immediate_0(raw);

        else if ((b & b01110) == b00100)
            result = armv7_read_arm_instr_a8_vceq_immediate_0(raw);

        else if ((b & b01110) == b00110)
            result = armv7_read_arm_instr_a8_vcle_immediate_0(raw);

        else if ((b & b01110) == b01000)
            result = armv7_read_arm_instr_a8_vclt_immediate_0(raw);

        else if ((b & b01110) == b01100)
            result = armv7_read_arm_instr_a8_vabs(raw);

        else if ((b & b01110) == b01110)
            result = armv7_read_arm_instr_a8_vneg(raw);

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

static GArchInstruction *process_armv7_arm_one_register_and_a_modified_immediate_value(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t cmode;                         /* Champ 'cmode' à retrouver   */
    uint32_t op;                            /* Champ 'op' à retrouver      */

    /**
     * Suit les directives de :
     * § A7.4.6 One register and a modified immediate value
     */

    if ((raw & 0xfeb80090) != 0xf2800010) return NULL;

    result = NULL;

    cmode = (raw >> 8) & b1111;
    op = (raw >> 5) & b1;

    if (op == b0)
    {
        if ((cmode & b1001) == b0000)
            result = armv7_read_arm_instr_a8_vmov_immediate(raw);

        else if ((cmode & b1001) == b0001)
            result = armv7_read_arm_instr_a8_vorr_immediate(raw);

        else if ((cmode & b1101) == b1000)
            result = armv7_read_arm_instr_a8_vmov_immediate(raw);

        else if ((cmode & b1101) == b1001)
            result = armv7_read_arm_instr_a8_vorr_immediate(raw);

        else if ((cmode & b1100) == b1100)
            result = armv7_read_arm_instr_a8_vmov_immediate(raw);

    }

    else/* if (op == b1)*/
    {
        if ((cmode & b1001) == b0000)
            result = armv7_read_arm_instr_a8_vmvn_immediate(raw);

        else if ((cmode & b1001) == b0001)
            result = armv7_read_arm_instr_a8_vbic_immediate(raw);

        else if ((cmode & b1101) == b1000)
            result = armv7_read_arm_instr_a8_vmvn_immediate(raw);

        else if ((cmode & b1101) == b1001)
            result = armv7_read_arm_instr_a8_vbic_immediate(raw);

        else if ((cmode & b1110) == b1100)
            result = armv7_read_arm_instr_a8_vmvn_immediate(raw);

        else if (cmode == b1110)
            result = armv7_read_arm_instr_a8_vmov_immediate(raw);

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

static GArchInstruction *process_armv7_arm_floating_point_data_processing_instructions(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t opc1;                          /* Champ 'opc1' à retrouver    */
    uint32_t opc2;                          /* Champ 'opc2' à retrouver    */
    uint32_t opc3;                          /* Champ 'opc3' à retrouver    */

    /**
     * Suit les directives de :
     * § A7.5 Floating-point data-processing instructions
     */

    if ((raw & 0x0f000e10) != 0x0e000a00) return NULL;

    result = NULL;

    opc1 = (raw >> 20) & b1111;
    opc2 = (raw >> 16) & b1111;
    opc3 = (raw >> 6) & b11;


    if ((opc1 & b1011) == b0000)
        result = armv7_read_arm_instr_a8_vmla_vmls_floating_point(raw);

    else if ((opc1 & b1011) == b0001)
        result = armv7_read_arm_instr_a8_vnmla_vnmls_vnmul(raw);

    else if ((opc1 & b1011) == b0010)
    {
        if ((opc3 & b01) == b01)
            result = armv7_read_arm_instr_a8_vnmla_vnmls_vnmul(raw);

        else/* if ((opc3 & b01) == b00)*/
            result = armv7_read_arm_instr_a8_vmul_floating_point(raw);

    }

    else if ((opc1 & b1011) == b0011)
    {
        if ((opc3 & b01) == b00)
            result = armv7_read_arm_instr_a8_vadd_floating_point(raw);

        else/* if ((opc3 & b01) == b01)*/
            result = armv7_read_arm_instr_a8_vsub_floating_point(raw);

    }

    else if ((opc1 & b1011) == b1000)
    {
        if ((opc3 & b01) == b00)
            result = armv7_read_arm_instr_a8_vdiv(raw);

    }

    else if ((opc1 & b1011) == b1001)
        result = armv7_read_arm_instr_a8_vfnma_vfnms(raw);

    else if ((opc1 & b1011) == b1010)
        result = armv7_read_arm_instr_a8_vfma_vfms(raw);

    else if ((opc1 & b1011) == b1011)
    {
        if ((opc3 & b01) == b00)
            result = armv7_read_arm_instr_a8_vmov_immediate(raw);

        else if (opc2 == b0000)
        {
            if (opc3 == b01)
                result = armv7_read_arm_instr_a8_vmov_register(raw);

            else if (opc3 == b11)
                result = armv7_read_arm_instr_a8_vabs(raw);

        }

        else if (opc2 == b0001)
        {
            if (opc3 == b01)
                result = armv7_read_arm_instr_a8_vneg(raw);

            else if (opc3 == b11)
                result = armv7_read_arm_instr_a8_vsqrt(raw);

        }

        else if ((opc2 & b1110) == b0010 && (opc3 & b01) == b01)
                result = armv7_read_arm_instr_a8_vcvtb_vcvtt(raw);

        else if ((opc2 & b1110) == b0100 && (opc3 & b01) == b01)
                result = armv7_read_arm_instr_a8_vcmp_vcmpe(raw);

        else if (opc2 == b0111 && opc3 == b11)
                result = armv7_read_arm_instr_a8_vcvt_between_double_precision_and_single_precision(raw);

        else if (opc2 == b1000 && (opc3 & b01) == b01)
                result = armv7_read_arm_instr_a8_vcvt_vcvtr_between_floating_point_and_integer_floating_point(raw);

        else if ((opc2 & b1110) == b1010 && (opc3 & b01) == b01)
                result = armv7_read_arm_instr_a8_vcvt_between_floating_point_and_fixed_point_floating_point(raw);

        else if ((opc2 & b1110) == b1100 && (opc3 & b01) == b01)
                result = armv7_read_arm_instr_a8_vcvt_vcvtr_between_floating_point_and_integer_floating_point(raw);

        else if ((opc2 & b1110) == b1110 && (opc3 & b01) == b01)
                result = armv7_read_arm_instr_a8_vcvt_between_floating_point_and_fixed_point_floating_point(raw);

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

static GArchInstruction *process_armv7_arm_extension_register_load_store_instructions(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t opcode;                        /* Champ 'opcode' à retrouver  */
    uint32_t rn;                            /* Champ 'rn' à retrouver      */

    /**
     * Suit les directives de :
     * § A7.6 Extension register load/store instructions
     */

    if ((raw & 0x0e000e00) != 0x0c000a00) return NULL;

    result = NULL;

    opcode = (raw >> 20) & b11111;
    rn = (raw >> 16) & b1111;

    if ((opcode & b11110) == b00100)
        result = process_armv7_arm_64_bit_transfers_between_arm_core_and_extension_registers(raw);

    else if ((opcode & b11011) == b01000)
        result = armv7_read_arm_instr_a8_vstm(raw);

    else if ((opcode & b11011) == b01010)
        result = armv7_read_arm_instr_a8_vstm(raw);

    else if ((opcode & b10011) == b10000)
        result = armv7_read_arm_instr_a8_vstr(raw);

    else if ((opcode & b11011) == b10010)
    {
        if (rn != b1101)
            result = armv7_read_arm_instr_a8_vstm(raw);

        else/* if (rn == b1101)*/
            result = armv7_read_arm_instr_a8_vpush(raw);

    }

    else if ((opcode & b11011) == b01001)
        result = armv7_read_arm_instr_a8_vldm(raw);

    else if ((opcode & b11011) == b01011)
    {
        if (rn != 1101)
            result = armv7_read_arm_instr_a8_vldm(raw);

        else/* if (rn == 1101)*/
            result = armv7_read_arm_instr_a8_vpop(raw);

    }

    else if ((opcode & b10011) == b10001)
        result = armv7_read_arm_instr_a8_vldr(raw);

    else if ((opcode & b11011) == b10011)
        result = armv7_read_arm_instr_a8_vldm(raw);

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

static GArchInstruction *process_armv7_arm_advanced_simd_element_or_structure_load_store_instructions(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t a;                             /* Champ 'a' à retrouver       */
    uint32_t l;                             /* Champ 'l' à retrouver       */
    uint32_t b;                             /* Champ 'b' à retrouver       */

    /**
     * Suit les directives de :
     * § A7.7 Advanced SIMD element or structure load/store instructions
     */

    if ((raw & 0xff100000) != 0xf4000000) return NULL;

    result = NULL;

    a = (raw >> 23) & b1;
    l = (raw >> 21) & b1;
    b = (raw >> 8) & b1111;

    if (l == b0)
    {
        if (a == b0)
        {
            if (b == b0010)
                result = armv7_read_arm_instr_a8_vst1_multiple_single_elements(raw);

            else if ((b & b1110) == b0110)
                result = armv7_read_arm_instr_a8_vst1_multiple_single_elements(raw);

            else if (b == b1010)
                result = armv7_read_arm_instr_a8_vst1_multiple_single_elements(raw);

            else if (b == b0011)
                result = armv7_read_arm_instr_a8_vst2_multiple_2_element_structures(raw);

            else if ((b & b1110) == b1000)
                result = armv7_read_arm_instr_a8_vst2_multiple_2_element_structures(raw);

            else if ((b & b1110) == b0100)
                result = armv7_read_arm_instr_a8_vst3_multiple_3_element_structures(raw);

            else if ((b & b1110) == b0000)
                result = armv7_read_arm_instr_a8_vst4_multiple_4_element_structures(raw);

        }

        else/* if (a == b1)*/
        {
            if ((b & b1011) == b0000)
                result = armv7_read_arm_instr_a8_vst1_single_element_from_one_lane(raw);

            else if (b == b1000)
                result = armv7_read_arm_instr_a8_vst1_single_element_from_one_lane(raw);

            else if ((b & b1011) == b0001)
                result = armv7_read_arm_instr_a8_vst2_single_2_element_structure_from_one_lane(raw);

            else if (b == b1001)
                result = armv7_read_arm_instr_a8_vst2_single_2_element_structure_from_one_lane(raw);

            else if ((b & b1011) == b0010)
                result = armv7_read_arm_instr_a8_vst3_single_3_element_structure_from_one_lane(raw);

            else if (b == b1010)
                result = armv7_read_arm_instr_a8_vst3_single_3_element_structure_from_one_lane(raw);

            else if ((b & b1011) == b0011)
                result = armv7_read_arm_instr_a8_vst4_single_4_element_structure_from_one_lane(raw);

            else if (b == b1011)
                result = armv7_read_arm_instr_a8_vst4_single_4_element_structure_from_one_lane(raw);

        }

    }

    else/* if (l == b1)*/
    {
        if (a == b0)
        {
            if (b == b0010)
                result = armv7_read_arm_instr_a8_vld1_multiple_single_elements(raw);

            else if ((b & b1110) == b0110)
                result = armv7_read_arm_instr_a8_vld1_multiple_single_elements(raw);

            else if (b == b1010)
                result = armv7_read_arm_instr_a8_vld1_multiple_single_elements(raw);

            else if (b == b0011)
                result = armv7_read_arm_instr_a8_vld2_multiple_2_element_structures(raw);

            else if ((b & b1110) == b1000)
                result = armv7_read_arm_instr_a8_vld2_multiple_2_element_structures(raw);

            else if ((b & b1110) == b0100)
                result = armv7_read_arm_instr_a8_vld3_multiple_3_element_structures(raw);

            else if ((b & b1110) == b0000)
                result = armv7_read_arm_instr_a8_vld4_multiple_4_element_structures(raw);

        }

        else/* if (a == b1)*/
        {
            if ((b & b1011) == b0000)
                result = armv7_read_arm_instr_a8_vld1_single_element_to_one_lane(raw);

            else if (b == b1000)
                result = armv7_read_arm_instr_a8_vld1_single_element_to_one_lane(raw);

            else if (b == b1100)
                result = armv7_read_arm_instr_a8_vld1_single_element_to_all_lanes(raw);

            else if ((b & b1011) == b0001)
                result = armv7_read_arm_instr_a8_vld2_single_2_element_structure_to_one_lane(raw);

            else if (b == b1001)
                result = armv7_read_arm_instr_a8_vld2_single_2_element_structure_to_one_lane(raw);

            else if (b == b1101)
                result = armv7_read_arm_instr_a8_vld2_single_2_element_structure_to_all_lanes(raw);

            else if ((b & b1011) == b0010)
                result = armv7_read_arm_instr_a8_vld3_single_3_element_structure_to_one_lane(raw);

            else if (b == b1010)
                result = armv7_read_arm_instr_a8_vld3_single_3_element_structure_to_one_lane(raw);

            else if (b == b1110)
                result = armv7_read_arm_instr_a8_vld3_single_3_element_structure_to_all_lanes(raw);

            else if ((b & b1011) == b0011)
                result = armv7_read_arm_instr_a8_vld4_single_4_element_structure_to_one_lane(raw);

            else if (b == b1011)
                result = armv7_read_arm_instr_a8_vld4_single_4_element_structure_to_one_lane(raw);

            else if (b == b1111)
                result = armv7_read_arm_instr_a8_vld4_single_4_element_structure_to_all_lanes(raw);

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

static GArchInstruction *process_armv7_arm_8_16_and_32_bit_transfer_between_arm_core_and_extension_registers(uint32_t raw)
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

    if ((raw & 0x0f000e10) != 0x0e000a10) return NULL;

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
                result = armv7_read_arm_instr_a8_vmov_between_arm_core_register_and_single_precision_register(raw);

            else if (a == b111)
            {
                result = armv7_read_arm_instr_a8_vmsr(raw); /* B9 ? */

                if (result == NULL /* ! */)
                    result = armv7_read_arm_instr_b9_vmsr(raw);

            }

        }

        else/* if (c == b1)*/
        {
            if ((a & b100) == b000)
                result = armv7_read_arm_instr_a8_vmov_arm_core_register_to_scalar(raw);

            else if (/*(a & b100) == b000) && */(b & b10) == b00)
                result = armv7_read_arm_instr_a8_vdup_arm_core_register(raw);

        }

    }

    else/* if (l == b1)*/
    {
        if (c == b0)
        {
            if (a == b000)
                result = armv7_read_arm_instr_a8_vmov_between_arm_core_register_and_single_precision_register(raw);

            else if (a == b111)
            {
                result = armv7_read_arm_instr_a8_vmrs(raw); /* B9 ? */

                if (result == NULL /* ! */)
                    result = armv7_read_arm_instr_b9_vmrs(raw);

            }

        }

        else/* if (c == b1)*/
            result = armv7_read_arm_instr_a8_vmov_scalar_to_arm_core_register(raw);

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

static GArchInstruction *process_armv7_arm_64_bit_transfers_between_arm_core_and_extension_registers(uint32_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint32_t c;                             /* Champ 'c' à retrouver       */
    uint32_t op;                            /* Champ 'op' à retrouver      */

    /**
     * Suit les directives de :
     * § A7.9 64-bit transfers between ARM core and extension registers
     */

    if ((raw & 0x0fe00e00) != 0x0c400a00) return NULL;

    result = NULL;

    c = (raw >> 8) & b1;
    op = (raw >> 4) & b1111;

    if (c == b0 && (op & b1101) == 0001)
        result = armv7_read_arm_instr_a8_vmov_between_two_arm_core_registers_and_two_single_precision_registers(raw);

    else if (c == b1 && (op & b1101) == 0001)
        result = armv7_read_arm_instr_a8_vmov_between_two_arm_core_registers_and_a_doubleword_extension_register(raw);

    return result;

}
