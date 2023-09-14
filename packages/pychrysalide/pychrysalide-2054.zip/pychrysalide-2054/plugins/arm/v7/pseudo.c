
/* Chrysalide - Outil d'analyse de fichiers binaires
 * pseudo.c - implémentation des pseudo-fonctions de spécification
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


#include "pseudo.h"


#include <assert.h>
#include <stddef.h>


#include <common/bconst.h>



/******************************************************************************
*                                                                             *
*  Paramètres  : x     = valeur sur 32 bits maximum à traiter.                *
*                n     = nombre de bits à prendre en compte.                  *
*                shift = nombre de décalages visés.                           *
*                carry = retenue enventuelle à constituer. [OUT]              *
*                value = nouvelle valeur calculée. [OUT]                      *
*                                                                             *
*  Description : Traduit la fonction 'LSL_C'.                                 *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool armv7_lsl_c(uint32_t x, unsigned int n, unsigned int shift, bool *carry, uint32_t *value)
{
    if (n > 32) return false;
    if (shift == 0) return false;

    if (carry != NULL)
        *carry = x & (1 << (n - 1));

    *value = x << shift;

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : x     = valeur sur 32 bits maximum à traiter.                *
*                n     = nombre de bits à prendre en compte.                  *
*                shift = nombre de décalages visés.                           *
*                value = nouvelle valeur calculée. [OUT]                      *
*                                                                             *
*  Description : Traduit la fonction 'LSL'.                                   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool armv7_lsl(uint32_t x, unsigned int n, unsigned int shift, uint32_t *value)
{
    bool result;                            /* Bilan final à retourner     */

    if (shift == 0)
        result = true;

    else
        result = armv7_lsl_c(x, n, shift, NULL, value);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : x     = valeur sur 32 bits maximum à traiter.                *
*                n     = nombre de bits à prendre en compte.                  *
*                shift = nombre de décalages visés.                           *
*                carry = retenue enventuelle à constituer. [OUT]              *
*                value = nouvelle valeur calculée. [OUT]                      *
*                                                                             *
*  Description : Traduit la fonction 'LSR_C'.                                 *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool armv7_lsr_c(uint32_t x, unsigned int n, unsigned int shift, bool *carry, uint32_t *value)
{
    if (n > 32) return false;
    if (shift == 0) return false;

    if (carry != NULL)
        *carry = x & (1 << (shift - 1));

    *value = x >> shift;

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : x     = valeur sur 32 bits maximum à traiter.                *
*                n     = nombre de bits à prendre en compte.                  *
*                shift = nombre de décalages visés.                           *
*                value = nouvelle valeur calculée. [OUT]                      *
*                                                                             *
*  Description : Traduit la fonction 'LSR'.                                   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool armv7_lsr(uint32_t x, unsigned int n, unsigned int shift, uint32_t *value)
{
    bool result;                            /* Bilan final à retourner     */

    if (shift == 0)
        result = x;

    else
        result = armv7_lsr_c(x, n, shift, NULL, value);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : x     = valeur sur 32 bits maximum à traiter.                *
*                n     = nombre de bits à prendre en compte.                  *
*                shift = nombre de décalages visés.                           *
*                carry = retenue enventuelle à constituer. [OUT]              *
*                value = nouvelle valeur calculée. [OUT]                      *
*                                                                             *
*  Description : Traduit la fonction 'ASR_C'.                                 *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool armv7_asr_c(uint32_t x, unsigned int n, unsigned int shift, bool *carry, uint32_t *value)
{
    if (n > 32) return false;
    if (shift == 0) return false;

    if (carry != NULL)
        *carry = x & (1 << (shift - 1));

    *value = ((int32_t)x) >> shift;

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : x     = valeur sur 32 bits maximum à traiter.                *
*                n     = nombre de bits à prendre en compte.                  *
*                shift = nombre de décalages visés.                           *
*                value = nouvelle valeur calculée. [OUT]                      *
*                                                                             *
*  Description : Traduit la fonction 'ASR'.                                   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool armv7_asr(uint32_t x, unsigned int n, unsigned int shift, uint32_t *value)
{
    bool result;                            /* Bilan final à retourner     */

    if (shift == 0)
        result = true;

    else
        result = armv7_asr_c(x, n, shift, NULL, value);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : x     = valeur sur 32 bits maximum à traiter.                *
*                n     = nombre de bits à prendre en compte.                  *
*                shift = nombre de décalages visés.                           *
*                carry = retenue enventuelle à constituer. [OUT]              *
*                value = nouvelle valeur calculée. [OUT]                      *
*                                                                             *
*  Description : Traduit la fonction 'ROR_C'.                                 *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool armv7_ror_c(uint32_t x, unsigned int n, unsigned int shift, bool *carry, uint32_t *value)
{
    if (n > 32) return false;
    if (shift == 0) return false;

    *value = (x >> shift) | (x << (32 - shift));

    if (carry != NULL)
        *carry = *value & (1 << (n - 1));

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : x     = valeur sur 32 bits maximum à traiter.                *
*                n     = nombre de bits à prendre en compte.                  *
*                shift = nombre de décalages visés.                           *
*                value = nouvelle valeur calculée. [OUT]                      *
*                                                                             *
*  Description : Traduit la fonction 'ROR'.                                   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool armv7_ror(uint32_t x, unsigned int n, unsigned int shift, uint32_t *value)
{
    bool result;                            /* Bilan final à retourner     */

    if (shift == 0)
        result = true;

    else
        result = armv7_ror_c(x, n, shift, NULL, value);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : x     = valeur sur 32 bits maximum à traiter.                *
*                n     = nombre de bits à prendre en compte.                  *
*                carry = retenue enventuelle à utiliser puis constituer. [OUT]*
*                value = nouvelle valeur calculée. [OUT]                      *
*                                                                             *
*  Description : Traduit la fonction 'RRX_C'.                                 *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool armv7_rrx_c(uint32_t x, unsigned int n, bool *carry, uint32_t *value)
{
    bool new_c;                             /* Nouvelle retenue à retenir  */

    new_c = x & 0x1;

    *value = (*carry ? 1 : 0) << (n - 1) | x >> 1;

    *carry = new_c;

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : x     = valeur sur 32 bits maximum à traiter.                *
*                n     = nombre de bits à prendre en compte.                  *
*                carry = retenue enventuelle à utiliser.                      *
*                value = nouvelle valeur calculée. [OUT]                      *
*                                                                             *
*  Description : Traduit la fonction 'RRX'.                                   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool armv7_rrx(uint32_t x, unsigned int n, bool carry, uint32_t *value)
{
    return armv7_rrx_c(x, n, &carry, value);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : imm12 = valeur sur 32 bits maximum à traiter.                *
*                carry = retenue enventuelle à utiliser / constituer. [OUT]   *
*                value = nouvelle valeur calculée. [OUT]                      *
*                                                                             *
*  Description : Traduit la fonction 'ARMExpandImm_C'.                        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool armv7_arm_expand_imm_c(uint32_t imm12, bool *carry, uint32_t *value)
{
    bool result;                            /* Bilan final à retourner     */
    uint32_t unrotated;                     /* Transformation à décaller   */

    /**
     * Selon les spécifications, x contient toujours 12 bits utiles seulement.
     */

    unrotated = armv7_zero_extend(imm12 & 0xff, 8, 32);

    result = armv7_shift(unrotated, 32, SRType_ROR, 2 * ((imm12 >> 8) & 0xf), carry, value);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : imm12 = valeur sur 32 bits maximum à traiter.                *
*                carry = retenue enventuelle à utiliser / constituer. [OUT]   *
*                value = nouvelle valeur calculée. [OUT]                      *
*                                                                             *
*  Description : Traduit la fonction 'ARMExpandImm'.                          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool armv7_arm_expand_imm(uint32_t imm12, uint32_t *value)
{
    return armv7_arm_expand_imm_c(imm12, (bool []) { false /* FIXME : APSR.C */ }, value);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : imm12 = valeur sur 32 bits maximum à traiter.                *
*                carry = retenue enventuelle à utiliser / constituer. [OUT]   *
*                value = nouvelle valeur calculée. [OUT]                      *
*                                                                             *
*  Description : Traduit la fonction 'ThumbExpandImm_C'.                      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool armv7_thumb_expand_imm_c(uint32_t imm12, bool *carry, uint32_t *value)
{
    bool result;                            /* Conclusion à faire remonter */
    uint8_t byte;                           /* Octet à reproduire          */
    uint32_t unrotated;                     /* Transformation à décaller   */

    result = true;

    if (((imm12 >> 10) & b11) == b00)
    {
        byte = imm12 & 0xff;

        switch ((imm12 >> 8) & b11)
        {
            case b00:
                *value = armv7_zero_extend(byte, 8, 32);
                break;

            case b01:
                if (byte == 0)
                    result = false;
                else
                    *value = byte << 16 | byte;
                break;

            case b10:
                if (byte == 0)
                    result = false;
                else
                    *value = byte << 24 | byte << 8;
                break;

            case b11:
                if (byte == 0)
                    result = false;
                else
                    *value = byte << 24 | byte << 16 | byte << 8 | byte;
                break;

        }

    }
    else
    {
        unrotated = 1 << 7 | (imm12 & 0x3f);
        result = armv7_ror_c(unrotated, 32, (imm12 >> 7) & 0x1f, carry, value);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : imm12 = valeur sur 32 bits maximum à traiter.                *
*                carry = retenue enventuelle à utiliser / constituer. [OUT]   *
*                value = nouvelle valeur calculée. [OUT]                      *
*                                                                             *
*  Description : Traduit la fonction 'ThumbExpandImm'.                        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool armv7_thumb_expand_imm(uint32_t imm12, uint32_t *value)
{
    return armv7_thumb_expand_imm_c(imm12, (bool []) { false /* FIXME : APSR.C */ }, value);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : op    = encodage d'opération.                                *
*                cmode = détails quant au mode d'opération.                   *
*                imm8  = valeur sur 8 bits à étendre.                         *
*                value = nouvelle valeur calculée. [OUT]                      *
*                                                                             *
*  Description : Traduit la fonction 'AdvSIMDExpandImm'.                      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool armv7_advanced_simd_expand_imm(bool op, uint8_t cmode, uint8_t imm8, uint64_t *value)
{
    bool result;                            /* Bilan à retourner           */
    uint64_t raw;                           /* Valeur d'entrée sur 64 bits */
    uint8_t cmode_31;                       /* Partie d'argument ciblée    */
    uint64_t imm8a;                         /* Valeur sur 8 bits #1        */
    uint64_t imm8b;                         /* Valeur sur 8 bits #2        */
    uint64_t imm8c;                         /* Valeur sur 8 bits #3        */
    uint64_t imm8d;                         /* Valeur sur 8 bits #4        */
    uint64_t imm8e;                         /* Valeur sur 8 bits #5        */
    uint64_t imm8f;                         /* Valeur sur 8 bits #6        */
    uint64_t imm8g;                         /* Valeur sur 8 bits #7        */
    uint64_t imm8h;                         /* Valeur sur 8 bits #8        */
    uint32_t imm32;                         /* Valeur sur 32 bits          */

    result = true;

    raw = imm8;

    cmode_31 = (cmode >> 1) & 0x7;

    switch (cmode_31)
    {
        case b000:
            *value = armv7_replicate_64(raw, 2);
            break;

        case b001:
            *value = armv7_replicate_64(raw << 8, 2);
            break;

        case b010:
            *value = armv7_replicate_64(raw << 16, 2);
            break;

        case b011:
            *value = armv7_replicate_64(raw << 24, 2);
            break;

        case b100:
            *value = armv7_replicate_64(raw, 4);
            break;

        case b101:
            *value = armv7_replicate_64(raw << 8, 4);
            break;

        case b110:

            if ((cmode & 0x1) == 0)
                *value = armv7_replicate_64(raw << 8 | 0xff, 2);
            else
                *value = armv7_replicate_64(raw << 16 | 0xffff, 2);
            break;

        case b111:

            if ((cmode & 0x1) == 0)
            {
                if (!op)
                    *value = armv7_replicate_64(raw, 8);

                else
                {
                    imm8a = armv7_replicate_8((imm8 & 0x80) >> 7, 8);
                    imm8b = armv7_replicate_8((imm8 & 0x40) >> 6, 8);
                    imm8c = armv7_replicate_8((imm8 & 0x20) >> 5, 8);
                    imm8d = armv7_replicate_8((imm8 & 0x10) >> 4, 8);
                    imm8e = armv7_replicate_8((imm8 & 0x8) >> 3, 8);
                    imm8f = armv7_replicate_8((imm8 & 0x4) >> 2, 8);
                    imm8g = armv7_replicate_8((imm8 & 0x2) >> 1, 8);
                    imm8h = armv7_replicate_8((imm8 & 0x1) >> 0, 8);

                    *value = (imm8a << 56) | (imm8b << 48) | (imm8c << 40) | (imm8d << 32) \
                        | (imm8e << 24) | (imm8f << 16) | (imm8g << 8) | imm8h;

                }

            }
            else
            {
                if (!op)
                {
                    imm32 = (raw & 0x80) << 31 \
                        | ((uint64_t)(raw & 0x40 ? 0 : 1)) << 30 \
                        | armv7_replicate_8((raw & 0x40) >> 6, 5) \
                        | ((raw & 0x3f) << 19);

                    *value = armv7_replicate_64(imm32, 2);

                }

                else
                    result = false;

            }
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type2 = type de décalage encodé sur 2 bits.                  *
*                imm5  = valeur de décalage entière sur 5 bits.               *
*                type  = type de décalage à constituer. [OUT]                 *
*                value = valeur pleine et entière à utiliser. [OUT]           *
*                                                                             *
*  Description : Traduit la fonction 'DecodeImmShift'.                        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool armv7_decode_imm_shift(uint8_t type2, uint8_t imm5, SRType *type, uint8_t *value)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    switch (type2)
    {
        case b00:
            *type = SRType_LSL;
            *value = imm5;
            break;

        case b01:
            *type = SRType_LSR;
            *value = (imm5 == 0 ? 32 : imm5);
            break;

        case b10:
            *type = SRType_ASR;
            *value = (imm5 == 0 ? 32 : imm5);
            break;

        case b11:
            if (imm5 == 0)
            {
                *type = SRType_RRX;
                *value = 1;
            }
            else
            {
                *type = SRType_ROR;
                *value = imm5;
            }
            break;

        default:
            result = false;
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type2 = type de décalage encodé sur 2 bits.                  *
*                type  = type de décalage à constituer. [OUT]                 *
*                                                                             *
*  Description : Traduit la fonction 'DecodeRegShift'.                        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool armv7_decode_reg_shift(uint8_t type2, SRType *type)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    switch (type2)
    {
        case b00:
            *type = SRType_LSL;
            break;

        case b01:
            *type = SRType_LSR;
            break;

        case b10:
            *type = SRType_ASR;
            break;

        case b11:
            *type = SRType_ROR;
            break;

        default:
            result = false;
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : x      = valeur sur 32 bits maximum à traiter.               *
*                n      = nombre de bits à prendre en compte.                 *
*                type   = type d'opération à mener.                           *
*                amount = quantité liée à l'opération à mener.                *
*                carry  = retenue enventuelle à utiliser / constituer. [OUT]  *
*                value  = nouvelle valeur calculée. [OUT]                     *
*                                                                             *
*  Description : Traduit la fonction 'Shift_C'.                               *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool armv7_shift_c(uint32_t x, unsigned int n, SRType type, unsigned int amount, bool *carry, uint32_t *value)
{
    bool result;                            /* Bilan final à retourner     */

    if (type == SRType_RRX && amount != 1) return false;

    if (amount == 0)
    {
        *value = x;
        return true;
    }

    result = true;     /* Pour GCC... */

    switch (type)
    {
        case SRType_LSL:
            result = armv7_lsl_c(x, n, amount, carry, value);
            break;

        case SRType_LSR:
            result = armv7_lsr_c(x, n, amount, carry, value);
            break;

        case SRType_ASR:
            result = armv7_asr_c(x, n, amount, carry, value);
            break;

        case SRType_ROR:
            result = armv7_ror_c(x, n, amount, carry, value);
            break;

        case SRType_RRX:
            result = armv7_rrx_c(x, n, carry, value);
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : x      = valeur sur 32 bits maximum à traiter.               *
*                n      = nombre de bits à prendre en compte.                 *
*                type   = type d'opération à mener.                           *
*                amount = quantité liée à l'opération à mener.                *
*                carry  = retenue enventuelle à utiliser.                     *
*                value  = nouvelle valeur calculée. [OUT]                     *
*                                                                             *
*  Description : Traduit la fonction 'Shift'.                                 *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool armv7_shift(uint32_t x, unsigned int n, SRType type, unsigned int amount, bool carry, uint32_t *value)
{
    return armv7_shift_c(x, n, type, amount, &carry, value);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : x = valeur sur 8 bits à traiter.                             *
*                n = nombre de partie à recopier.                             *
*                                                                             *
*  Description : Constitue une value à partir de réplications.                *
*                                                                             *
*  Retour      : Nouvelle valeur calculée.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

uint8_t armv7_replicate_8(uint8_t x, unsigned int n)
{
    uint8_t result;                         /* Value à retourner           */
    unsigned int step;                      /* Marge de progression        */
    unsigned int i;                         /* Boucle de parcours          */

    assert(8 % n == 0);

    result = 0;

    step = 8 / n;

    for (i = 0; i < 8; i += step)
        result |= (x << (i * step));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : x = valeur sur 64 bits à traiter.                            *
*                n = nombre de partie à recopier.                             *
*                                                                             *
*  Description : Constitue une value à partir de réplications.                *
*                                                                             *
*  Retour      : Nouvelle valeur calculée.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

uint64_t armv7_replicate_64(uint64_t x, unsigned int n)
{
    uint64_t result;                        /* Value à retourner           */
    unsigned int step;                      /* Marge de progression        */
    unsigned int i;                         /* Boucle de parcours          */

    assert(64 % n == 0);

    result = 0;

    step = 64 / n;

    for (i = 0; i < 64; i += step)
        result |= (x << (i * step));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : x = valeur sur 32 bits maximum à traiter.                    *
*                n = nombre de bits à prendre en compte.                      *
*                i = taille finale à obtenir.                                 *
*                                                                             *
*  Description : Traduit la fonction 'ZeroExtend'.                            *
*                                                                             *
*  Retour      : Nouvelle valeur calculée.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

uint32_t armv7_zero_extend(uint32_t x, unsigned int n, unsigned int i)
{
    return x;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : x = valeur sur 32 bits maximum à traiter.                    *
*                t = bit de poids nombre de bits à prendre en compte.         *
*                i = taille finale à obtenir.                                 *
*                                                                             *
*  Description : Fournit une aide pour la fonction 'SignExtend'.              *
*                                                                             *
*  Retour      : Nouvelle valeur calculée.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

uint32_t armv7_sign_extend(uint32_t x, unsigned int t, unsigned int i)
{
    uint32_t result;                        /* Valeur à retourner          */
    bool set;                               /* Bit de poids fort à 1 ?     */
    unsigned int k;                         /* Boucle de parcours          */

    result = 0;

    set = (x & (1 << t));

    switch (i)
    {

#define SIGN_EXTEND_CASE(sz)                    \
        case sz:                                \
            result = x;                         \
            if (set)                            \
                for (k = t + 1; k < sz; k++)    \
                    result |= (1 << k);         \
            break;

        SIGN_EXTEND_CASE(4);
        SIGN_EXTEND_CASE(8);
        SIGN_EXTEND_CASE(16);
        SIGN_EXTEND_CASE(32);

    }

    return result;

}
