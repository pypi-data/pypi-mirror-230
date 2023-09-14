
/* Chrysalide - Outil d'analyse de fichiers binaires
 * thumb_16.c - désassemblage des instructions ARMv7 Thumb 16 bits
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


#include "thumb_16.h"


#include <stdint.h>


#include <common/bconst.h>


#include "opcodes/thumb_16_opcodes.h"
#include "opcodes/opcodes_tmp_thumb_16.h"



/* Désassemble une instruction ARMv7 liées au chapitre A6.2.1 */
static GArchInstruction *process_armv7_thumb_16_shift_immediate_add_subtract_move_and_compare(uint16_t);

/* Désassemble une instruction ARMv7 liées au chapitre A6.2.2. */
static GArchInstruction *process_armv7_thumb_16_data_processing(uint16_t);

/* Désassemble une instruction ARMv7 liées au chapitre A6.2.3. */
static GArchInstruction *process_armv7_thumb_16_special_data_instructions_and_branch_and_exchange(uint16_t);

/* Désassemble une instruction ARMv7 liées au chapitre A6.2.4. */
static GArchInstruction *process_armv7_thumb_16_load_store_single_data_item(uint16_t);

/* Désassemble une instruction ARMv7 liées au chapitre A6.2.5. */
static GArchInstruction *process_armv7_thumb_16_miscellaneous_16_bit_instructions(uint16_t);

/* Désassemble une instruction ARMv7 liées au chapitre A6.2.5.b. */
static GArchInstruction *process_armv7_thumb_16_miscellaneous_16_bit_instructions_if_then_and_hints(uint16_t);

/* Désassemble une instruction ARMv7 liées au chapitre A6.2.6. */
static GArchInstruction *process_armv7_thumb_16_conditional_branch_and_supervisor_call(uint16_t);



/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 16 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A6.2.    *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *process_armv7_thumb_16_instruction_set_encoding(uint16_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint16_t opcode;                        /* Champ 'opcode' à retrouver  */

    /**
     * Suit les directives de :
     * § A6.2 16-bit Thumb instruction encoding
     */

    result = NULL;

    opcode = (raw >> 10) & b111111;

    if ((opcode & b110000) == b000000)
        result = process_armv7_thumb_16_shift_immediate_add_subtract_move_and_compare(raw);

    else if (opcode == b010000)
        result = process_armv7_thumb_16_data_processing(raw);

    else if (opcode == b010001)
        result = process_armv7_thumb_16_special_data_instructions_and_branch_and_exchange(raw);

    else if ((opcode & b111110) == b010010)
        result = armv7_read_thumb_16_instr_a8_ldr_literal(raw);

    else if ((opcode & b111100) == b010100)
        result = process_armv7_thumb_16_load_store_single_data_item(raw);

    else if ((opcode & b111000) == b011000)
        result = process_armv7_thumb_16_load_store_single_data_item(raw);

    else if ((opcode & b111000) == b100000)
        result = process_armv7_thumb_16_load_store_single_data_item(raw);

    else if ((opcode & b111110) == b101000)
        result = armv7_read_thumb_16_instr_a8_adr(raw);

    else if ((opcode & b111110) == b101010)
        result = armv7_read_thumb_16_instr_a8_add_sp_plus_immediate(raw);

    else if ((opcode & b111100) == b101100)
        result = process_armv7_thumb_16_miscellaneous_16_bit_instructions(raw);

    else if ((opcode & b111110) == b110000)
        result = armv7_read_thumb_16_instr_a8_stm_stmia_stmea(raw);

    else if ((opcode & b111110) == b110010)
        result = armv7_read_thumb_16_instr_a8_ldm_ldmia_ldmfd_thumb(raw);

    else if ((opcode & b111100) == b110100)
        result = process_armv7_thumb_16_conditional_branch_and_supervisor_call(raw);

    else if ((opcode & b111110) == b111000)
        result = armv7_read_thumb_16_instr_a8_b(raw);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 16 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A6.2.1.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_16_shift_immediate_add_subtract_move_and_compare(uint16_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint16_t opcode;                        /* Champ 'opcode' à retrouver  */

    /**
     * Suit les directives de :
     * § A6.2.1 Shift (immediate), add, subtract, move, and compare
     */

    if ((raw & 0xc000) != 0x0000) return NULL;

    result = NULL;

    opcode = (raw >> 9) & b11111;

    if ((opcode & b11100) == b00000)
        result = armv7_read_thumb_16_instr_a8_lsl_immediate(raw);

    else if ((opcode & b11100) == b00100)
        result = armv7_read_thumb_16_instr_a8_lsr_immediate(raw);

    else if ((opcode & b11100) == b01000)
        result = armv7_read_thumb_16_instr_a8_asr_immediate(raw);

    else if (opcode == b01100)
        result = armv7_read_thumb_16_instr_a8_add_register_thumb(raw);

    else if (opcode == b01101)
        result = armv7_read_thumb_16_instr_a8_sub_register(raw);

    else if (opcode == b01110)
        result = armv7_read_thumb_16_instr_a8_add_immediate_thumb(raw);

    else if (opcode == b01111)
        result = armv7_read_thumb_16_instr_a8_sub_immediate_thumb(raw);

    else if ((opcode & b11100) == b10000)
        result = armv7_read_thumb_16_instr_a8_mov_immediate(raw);

    else if ((opcode & b11100) == b10100)
        result = armv7_read_thumb_16_instr_a8_cmp_immediate(raw);

    else if ((opcode & b11100) == b11000)
        result = armv7_read_thumb_16_instr_a8_add_immediate_thumb(raw);

    else if ((opcode & b11100) == b11100)
        result = armv7_read_thumb_16_instr_a8_sub_immediate_thumb(raw);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 16 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A6.2.2.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_16_data_processing(uint16_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint16_t opcode;                        /* Champ 'opcode' à retrouver  */

    /**
     * Suit les directives de :
     * § A6.2.2 Data-processing
     */

    if ((raw & 0xfc00) != 0x4000) return NULL;

    result = NULL;

    opcode = (raw >> 6) & b1111;

    switch (opcode)
    {
        case b0000:
            result = armv7_read_thumb_16_instr_a8_and_register(raw);
            break;

        case b0001:
            result = armv7_read_thumb_16_instr_a8_eor_register(raw);
            break;

        case b0010:
            result = armv7_read_thumb_16_instr_a8_lsl_register(raw);
            break;

        case b0011:
            result = armv7_read_thumb_16_instr_a8_lsr_register(raw);
            break;

        case b0100:
            result = armv7_read_thumb_16_instr_a8_asr_register(raw);
            break;

        case b0101:
            result = armv7_read_thumb_16_instr_a8_adc_register(raw);
            break;

        case b0110:
            result = armv7_read_thumb_16_instr_a8_sbc_register(raw);
            break;

        case b0111:
            result = armv7_read_thumb_16_instr_a8_ror_register(raw);
            break;

        case b1000:
            result = armv7_read_thumb_16_instr_a8_tst_register(raw);
            break;

        case b1001:
            result = armv7_read_thumb_16_instr_a8_rsb_immediate(raw);
            break;

        case b1010:
            result = armv7_read_thumb_16_instr_a8_cmp_register(raw);
            break;

        case b1011:
            result = armv7_read_thumb_16_instr_a8_cmn_register(raw);
            break;

        case b1100:
            result = armv7_read_thumb_16_instr_a8_orr_register(raw);
            break;

        case b1101:
            result = armv7_read_thumb_16_instr_a8_mul(raw);
            break;

        case b1110:
            result = armv7_read_thumb_16_instr_a8_bic_register(raw);
            break;

        case b1111:
            result = armv7_read_thumb_16_instr_a8_mvn_register(raw);
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 16 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A6.2.3.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_16_special_data_instructions_and_branch_and_exchange(uint16_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint16_t opcode;                        /* Champ 'opcode' à retrouver  */

    /**
     * Suit les directives de :
     * § A6.2.3 Special data instructions and branch and exchange
     */

    if ((raw & 0xfc00) != 0x4400) return NULL;

    result = NULL;

    opcode = (raw >> 6) & b1111;

    if (opcode == b0000)
        result = armv7_read_thumb_16_instr_a8_add_register_thumb(raw);

    else if (opcode == b0001)
        result = armv7_read_thumb_16_instr_a8_add_register_thumb(raw);

    else if ((opcode & b1110) == b0010)
        result = armv7_read_thumb_16_instr_a8_add_register_thumb(raw);

    else if ((opcode & b1100) == b0100)
        result = armv7_read_thumb_16_instr_a8_cmp_register(raw);

    else if (opcode == b1000)
        result = armv7_read_thumb_16_instr_a8_mov_register_thumb(raw);

    else if (opcode == b1001)
        result = armv7_read_thumb_16_instr_a8_mov_register_thumb(raw);

    else if ((opcode & b1110) == b1010)
        result = armv7_read_thumb_16_instr_a8_mov_register_thumb(raw);

    else if ((opcode & b1110) == b1100)
        result = armv7_read_thumb_16_instr_a8_bx(raw);

    else if ((opcode & b1110) == b1110)
        result = armv7_read_thumb_16_instr_a8_blx_register(raw);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 16 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A6.2.4.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_16_load_store_single_data_item(uint16_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint16_t opa;                           /* Champ 'opa' à retrouver     */
    uint16_t opb;                           /* Champ 'opb' à retrouver     */

    /**
     * Suit les directives de :
     * § A6.2.4 Load/store single data item
     */

    result = NULL;

    opa = (raw >> 12) & b1111;
    opb = (raw >> 9) & b111;

    switch (opa)
    {
        case b0101:
            switch (opb)
            {
                case b000:
                    result = armv7_read_thumb_16_instr_a8_str_register(raw);
                    break;

                case b001:
                    result = armv7_read_thumb_16_instr_a8_strh_register(raw);
                    break;

                case b010:
                    result = armv7_read_thumb_16_instr_a8_strb_register(raw);
                    break;

                case b011:
                    result = armv7_read_thumb_16_instr_a8_ldrsb_register(raw);
                    break;

                case b100:
                    result = armv7_read_thumb_16_instr_a8_ldr_register_thumb(raw);
                    break;

                case b101:
                    result = armv7_read_thumb_16_instr_a8_ldrh_register(raw);
                    break;

                case b110:
                    result = armv7_read_thumb_16_instr_a8_ldrb_register(raw);
                    break;

                case b111:
                    result = armv7_read_thumb_16_instr_a8_ldrsh_register(raw);
                    break;

            }
            break;

        case b0110:

            if ((opb & b100) == b000)
                    result = armv7_read_thumb_16_instr_a8_str_immediate_thumb(raw);
            else /*if ((opb & b100) == b100)*/
                    result = armv7_read_thumb_16_instr_a8_ldr_immediate_thumb(raw);

            break;

        case b0111:

            if ((opb & b100) == b000)
                    result = armv7_read_thumb_16_instr_a8_strb_immediate_thumb(raw);
            else /*if ((opb & b100) == b100)*/
                    result = armv7_read_thumb_16_instr_a8_ldrb_immediate_thumb(raw);

            break;

        case b1000:

            if ((opb & b100) == b000)
                    result = armv7_read_thumb_16_instr_a8_strh_immediate_thumb(raw);
            else /*if ((opb & b100) == b100)*/
                    result = armv7_read_thumb_16_instr_a8_ldrh_immediate_thumb(raw);

            break;

        case b1001:

            if ((opb & b100) == b000)
                    result = armv7_read_thumb_16_instr_a8_str_immediate_thumb(raw);
            else /*if ((opb & b100) == b100)*/
                    result = armv7_read_thumb_16_instr_a8_ldr_immediate_thumb(raw);

            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 16 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A6.2.5.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_16_miscellaneous_16_bit_instructions(uint16_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint16_t opcode;                        /* Champ 'opcode' à retrouver  */

    /**
     * Suit les directives de :
     * § A6.2.5 Miscellaneous 16-bit instructions
     */

    if ((raw & 0xf000) != 0xb000) return NULL;

    result = NULL;

    opcode = (raw >> 5) & b1111111;

    if ((opcode & b1111100) == b0000000)
        result = armv7_read_thumb_16_instr_a8_add_sp_plus_immediate(raw);

    else if ((opcode & b1111100) == b0000100)
        result = armv7_read_thumb_16_instr_a8_sub_sp_minus_immediate(raw);

    else if ((opcode & b1111000) == b0001000)
        result = armv7_read_thumb_16_instr_a8_cbnz_cbz(raw);

    else if ((opcode & b1111110) == b0010000)
        result = armv7_read_thumb_16_instr_a8_sxth(raw);

    else if ((opcode & b1111110) == b0010010)
        result = armv7_read_thumb_16_instr_a8_sxtb(raw);

    else if ((opcode & b1111110) == b0010100)
        result = armv7_read_thumb_16_instr_a8_uxth(raw);

    else if ((opcode & b1111110) == b0010110)
        result = armv7_read_thumb_16_instr_a8_uxtb(raw);

    else if ((opcode & b1111000) == b0011000)
        result = armv7_read_thumb_16_instr_a8_cbnz_cbz(raw);

    else if ((opcode & b1110000) == b0100000)
        result = armv7_read_thumb_16_instr_a8_push(raw);

    else if (opcode == b0110010)
        result = armv7_read_thumb_16_instr_a8_setend(raw);

    else if (opcode == b0110011)
        result = armv7_read_thumb_16_instr_b9_cps_thumb(raw);

    else if ((opcode & b1111000) == b1001000)
        result = armv7_read_thumb_16_instr_a8_cbnz_cbz(raw);

    else if ((opcode & b1111110) == b1010000)
        result = armv7_read_thumb_16_instr_a8_rev(raw);

    else if ((opcode & b1111110) == b1010010)
        result = armv7_read_thumb_16_instr_a8_rev16(raw);

    else if ((opcode & b1111110) == b1010110)
        result = armv7_read_thumb_16_instr_a8_revsh(raw);

    else if ((opcode & b1111000) == b1011000)
        result = armv7_read_thumb_16_instr_a8_cbnz_cbz(raw);

    else if ((opcode & b1110000) == b1100000)
        result = armv7_read_thumb_16_instr_a8_pop_thumb(raw);

    else if ((opcode & b1111000) == b1110000)
        result = armv7_read_thumb_16_instr_a8_bkpt(raw);

    else if ((opcode & b1111000) == b1111000)
        result = process_armv7_thumb_16_miscellaneous_16_bit_instructions_if_then_and_hints(raw);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 16 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A6.2.5.b.*
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_16_miscellaneous_16_bit_instructions_if_then_and_hints(uint16_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint16_t opa;                           /* Champ 'opa' à retrouver     */
    uint16_t opb;                           /* Champ 'opb' à retrouver     */

    /**
     * Suit les directives de :
     * § A6.2.5 Miscellaneous 16-bit instructions
     *    |-> If-Then, and hints
     */

    if ((raw & 0xff00) != 0xbf00) return NULL;

    result = NULL;

    opa = (raw >> 4) & b1111;
    opb = (raw >> 0) & b1111;

    if (opb != b0000)
        result = armv7_read_thumb_16_instr_a8_it(raw);

    else
        switch (opa)
        {
            case b0000:
                result = armv7_read_thumb_16_instr_a8_nop(raw);
                break;

            case b0001:
                result = armv7_read_thumb_16_instr_a8_yield(raw);
                break;

            case b0010:
                result = armv7_read_thumb_16_instr_a8_wfe(raw);
                break;

            case b0011:
                result = armv7_read_thumb_16_instr_a8_wfi(raw);
                break;

            case b0100:
                result = armv7_read_thumb_16_instr_a8_sev(raw);
                break;

        }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw = donnée brute de 16 bits à désassembler.                *
*                                                                             *
*  Description : Désassemble une instruction ARMv7 liées au chapitre A6.2.6.  *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *process_armv7_thumb_16_conditional_branch_and_supervisor_call(uint16_t raw)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    uint16_t opcode;                        /* Champ 'opcode' à retrouver  */

    /**
     * Suit les directives de :
     * § A6.2.6 Conditional branch, and Supervisor Call
     */

    if ((raw & 0xf000) != 0xd000) return NULL;

    result = NULL;

    opcode = (raw >> 8) & b1111;

    switch (opcode)
    {
        case b1110:
            result = armv7_read_thumb_16_instr_a8_udf(raw);
            break;

        case b1111:
            result = armv7_read_thumb_16_instr_a8_svc_previously_swi(raw);
            break;

        default:
            result = armv7_read_thumb_16_instr_a8_b(raw);
            break;

    }

    return result;

}
