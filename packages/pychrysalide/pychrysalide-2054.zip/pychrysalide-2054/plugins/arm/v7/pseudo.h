
/* Chrysalide - Outil d'analyse de fichiers binaires
 * pseudo.h - prototypes pour l'implémentation des pseudo-fonctions de spécification
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


#ifndef _PLUGINS_ARM_V7_PSEUDO_H
#define _PLUGINS_ARM_V7_PSEUDO_H


#include <stdbool.h>
#include <stdint.h>



/**
 * § A2.2.1 - Integer arithmetic
 */


/* Traduit la fonction 'LSL_C'. */
bool armv7_lsl_c(uint32_t, unsigned int, unsigned int, bool *, uint32_t *);

/* Traduit la fonction 'LSL'. */
bool armv7_lsl(uint32_t, unsigned int, unsigned int, uint32_t *);

/* Traduit la fonction 'LSR_C'. */
bool armv7_lsr_c(uint32_t, unsigned int, unsigned int, bool *, uint32_t *);

/* Traduit la fonction 'LSR'. */
bool armv7_lsr(uint32_t, unsigned int, unsigned int, uint32_t *);

/* Traduit la fonction 'ASR_C'. */
bool armv7_asr_c(uint32_t, unsigned int, unsigned int, bool *, uint32_t *);

/* Traduit la fonction 'ASR'. */
bool armv7_asr(uint32_t, unsigned int, unsigned int, uint32_t *);

/* Traduit la fonction 'ROR_C'. */
bool armv7_ror_c(uint32_t, unsigned int, unsigned int, bool *, uint32_t *);

/* Traduit la fonction 'ROR'. */
bool armv7_ror(uint32_t, unsigned int, unsigned int, uint32_t *);

/* Traduit la fonction 'RRX_C'. */
bool armv7_rrx_c(uint32_t, unsigned int, bool *, uint32_t *);

/* Traduit la fonction 'RRX'. */
bool armv7_rrx(uint32_t, unsigned int, bool, uint32_t *);



/**
 * § A5.2.4 - Modified immediate constants in ARM instructions
 */


/* Traduit la fonction 'ARMExpandImm_C'. */
bool armv7_arm_expand_imm_c(uint32_t, bool *, uint32_t *);

/* Traduit la fonction 'ARMExpandImm'. */
bool armv7_arm_expand_imm(uint32_t, uint32_t *);



/**
 * § A6.3.2 - Modified immediate constants in Thumb instructions
 */


/* Traduit la fonction 'ThumbExpandImm_C'. */
bool armv7_thumb_expand_imm_c(uint32_t, bool *, uint32_t *);

/* Traduit la fonction 'ThumbExpandImm'. */
bool armv7_thumb_expand_imm(uint32_t, uint32_t *);



/**
 * § A7.4.6 - One register and a modified immediate value
 */


/* Traduit la fonction 'AdvSIMDExpandImm'. */
bool armv7_advanced_simd_expand_imm(bool, uint8_t, uint8_t, uint64_t *);



/**
 * § A8.4.3 - Pseudocode details of instruction-specified shifts and rotates
 */


typedef enum _SRType
{
    SRType_LSL,
    SRType_LSR,
    SRType_ASR,
    SRType_ROR,
    SRType_RRX

} SRType;


/* Traduit la fonction 'DecodeImmShift'. */
bool armv7_decode_imm_shift(uint8_t, uint8_t, SRType *, uint8_t *);

/* Traduit la fonction 'DecodeRegShift'. */
bool armv7_decode_reg_shift(uint8_t, SRType *);

/* Traduit la fonction 'Shift_C'. */
bool armv7_shift_c(uint32_t, unsigned int, SRType, unsigned int, bool *, uint32_t *);

/* Traduit la fonction 'Shift'. */
bool armv7_shift(uint32_t, unsigned int, SRType, unsigned int, bool, uint32_t *);



/**
 * § P.5.3 - Bitstring manipulation
 */


/* Constitue une value à partir de réplications. */
uint8_t armv7_replicate_8(uint8_t, unsigned int);

/* Constitue une value à partir de réplications. */
uint64_t armv7_replicate_64(uint64_t, unsigned int);

/* Traduit la fonction 'ZeroExtend'. */
uint32_t armv7_zero_extend(uint32_t, unsigned int, unsigned int);

/* Fournit une aide pour la fonction 'SignExtend'. */
uint32_t armv7_sign_extend(uint32_t, unsigned int, unsigned int);



#endif  /* _PLUGINS_ARM_V7_PSEUDO_H */
