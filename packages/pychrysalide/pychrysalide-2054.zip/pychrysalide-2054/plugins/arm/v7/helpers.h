
/* Chrysalide - Outil d'analyse de fichiers binaires
 * helpers.h - prototypes pour l'aide à la mise en place des opérandes ARMv7
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


#ifndef _PLUGINS_ARM_V7_HELPERS_H
#define _PLUGINS_ARM_V7_HELPERS_H


#include <arch/operands/immediate.h>
#include <arch/operands/register.h>


#include "pseudo.h"
#include "operands/estate.h"
#include "operands/iflags.h"
#include "operands/it.h"
#include "operands/maccess.h"
#include "operands/register.h"
#include "operands/reglist.h"
#include "operands/rotation.h"
#include "operands/shift.h"
#include "registers/banked.h"
#include "registers/basic.h"
#include "registers/coproc.h"
#include "registers/simd.h"
#include "registers/special.h"
#include "../register.h"



/**
 * Définitions élaborées à partir des spécifications.
 */


#define AdvSIMDExpandImm(op, cmode, imm8)                                           \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        uint64_t __val;                                                             \
        if (armv7_advanced_simd_expand_imm(op, cmode, imm8, &__val))                \
            __result = g_imm_operand_new_from_value(MDS_64_BITS_UNSIGNED, __val);   \
        else                                                                        \
            __result = NULL;                                                        \
        __result;                                                                   \
    })


#define AlignedRegister(reg, align)                                                 \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        GArmV7RegisterOperand *__cast;                                              \
        __result = reg;                                                             \
        if (__result != NULL && align != 0)                                         \
        {                                                                           \
            __cast = G_ARMV7_REGISTER_OPERAND(__result);                            \
            g_armv7_register_operand_define_alignement(__cast, align);              \
        }                                                                           \
        __result;                                                                   \
    })


#define ARMExpandImm(imm12)                                                         \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        uint32_t __val;                                                             \
        if (armv7_arm_expand_imm(imm12, &__val))                                    \
            __result = g_imm_operand_new_from_value(MDS_32_BITS_UNSIGNED, __val);   \
        else                                                                        \
            __result = NULL;                                                        \
        __result;                                                                   \
    })


#define ARMExpandImm_C(imm12, c)                                                    \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        uint32_t __val;                                                             \
        if (armv7_arm_expand_imm_c(imm12, (bool []) { c }, &__val))                 \
            __result = g_imm_operand_new_from_value(MDS_32_BITS_UNSIGNED, __val);   \
        else                                                                        \
            __result = NULL;                                                        \
        __result;                                                                   \
    })


#define BankedRegister(r, sysm)                                                     \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        GArchRegister *__reg;                                                       \
        __reg = g_armv7_banked_register_new(r, sysm);                               \
        if (__reg == NULL)                                                          \
            __result = NULL;                                                        \
        else                                                                        \
            __result = g_armv7_register_operand_new(G_ARMV7_REGISTER(__reg));       \
        __result;                                                                   \
    })


#define BitDiff(msb, lsb)                                                           \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        uint32_t __width;                                                           \
        __width = msb - lsb + 1;                                                    \
        __result = g_imm_operand_new_from_value(MDS_32_BITS_UNSIGNED, __width);     \
        __result;                                                                   \
    })


#define BuildFixedShift(type, val)                                                  \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        uint32_t __val;                                                             \
        GArchOperand *__shift_val;                                                  \
        __val = val;                                                                \
        __shift_val = g_imm_operand_new_from_value(MDS_32_BITS_UNSIGNED, __val);    \
        if (__shift_val == NULL)                                                    \
            __result = NULL;                                                        \
        else                                                                        \
        {                                                                           \
            __result = g_armv7_shift_operand_new(type, __shift_val);                \
            if (__result == NULL)                                                   \
                g_object_unref(G_OBJECT(__shift_val));                              \
        }                                                                           \
        __result;                                                                   \
    })


#define BuildRegShift(type, reg)                                                    \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        SRType __shift_t;                                                           \
        if (!armv7_decode_reg_shift(type, &__shift_t))                              \
            __result = NULL;                                                        \
        else                                                                        \
            __result = g_armv7_shift_operand_new(__shift_t, reg);                   \
        __result;                                                                   \
    })


#define CoProcessor(idx)                                                            \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        GArchRegister *__reg;                                                       \
        __reg = g_armv7_cp_register_new(idx);                                       \
        if (__reg == NULL)                                                          \
            __result = NULL;                                                        \
        else                                                                        \
            __result = g_armv7_register_operand_new(G_ARMV7_REGISTER(__reg));       \
        __result;                                                                   \
    })


#define DecodeImmShift(type, imm5)                                                  \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        SRType __shift_t;                                                           \
        uint8_t __shift_n;                                                          \
        GArchOperand *__op_n;                                                       \
        if (!armv7_decode_imm_shift(type, imm5, &__shift_t, &__shift_n))            \
            __result = NULL;                                                        \
        else                                                                        \
        {                                                                           \
            __op_n = g_imm_operand_new_from_value(MDS_8_BITS_UNSIGNED, __shift_n);  \
            __result = g_armv7_shift_operand_new(__shift_t, __op_n);                \
        }                                                                           \
        __result;                                                                   \
    })


#define DecodeImmShiftAmount(type, imm5)                                            \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        uint8_t __shift_n;                                                          \
        if (!armv7_decode_imm_shift(type, imm5, (SRType []) { 0 }, &__shift_n))     \
            __result = NULL;                                                        \
        else                                                                        \
            __result = g_imm_operand_new_from_value(MDS_8_BITS_UNSIGNED, __shift_n);\
        __result;                                                                   \
    })


#define DoubleWordVector(idx)                                                       \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        GArchRegister *__reg;                                                       \
        __reg = g_armv7_simd_register_new(SRM_DOUBLE_WORD, idx);                    \
        if (__reg == NULL)                                                          \
            __result = NULL;                                                        \
        else                                                                        \
            __result = g_armv7_register_operand_new(G_ARMV7_REGISTER(__reg));       \
        __result;                                                                   \
    })


#define DynamicVectorTable(target, count, first, rel)                               \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        size_t __i;                                                                 \
        GArchRegister *__reg;                                                       \
        if (count % rel != 0)                                                       \
            __result = NULL;                                                        \
        else                                                                        \
        {                                                                           \
            __result = g_armv7_reglist_operand_new(0);                              \
            for (__i = 0; __i < (count / rel); __i++)                               \
            {                                                                       \
                __reg = g_armv7_simd_register_new(target, first + __i);             \
                if (__reg == NULL)                                                  \
                {                                                                   \
                    g_object_unref(G_OBJECT(__result));                             \
                    __result = NULL;                                                \
                    break;                                                          \
                }                                                                   \
                g_armv7_reglist_add_register(G_ARMV7_REGLIST_OPERAND(__result),     \
                                             G_ARMV7_REGISTER(__reg));              \
            }                                                                       \
        }                                                                           \
        __result;                                                                   \
    })


#define Endian(big)                                                                 \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        __result = g_armv7_endian_operand_new(big);                                 \
        __result;                                                                   \
    })


#define FixedShift(type, imm5)                                                      \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        uint8_t __shift_n;                                                          \
        __shift_n = imm5;                                                           \
        __result = g_imm_operand_new_from_value(MDS_8_BITS_UNSIGNED, __shift_n);    \
        __result;                                                                   \
    })


#define IFlagsDefinition(a, i, f)                                                   \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        __result = g_armv7_iflags_operand_new(a, i, f);                             \
        __result;                                                                   \
    })

#define ITCond(firstcond, mask)                                                     \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        __result = g_armv7_itcond_operand_new(firstcond, mask);                     \
        __result;                                                                   \
    })

#define MemAccessOffset(base, off)                                                  \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        __result = g_armv7_maccess_operand_new(base, off, NULL, false, false);      \
        __result;                                                                   \
    })


#define MemAccessOffsetExtended(base, off, shift)                                   \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        __result = g_armv7_maccess_operand_new(base, off, shift, false, false);     \
        __result;                                                                   \
    })


#define MemAccessPreIndexed(base, off)                                              \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        __result = g_armv7_maccess_operand_new(base, off, NULL, false, true);       \
        __result;                                                                   \
    })


#define MemAccessPreIndexedExtended(base, off, shift)                               \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        __result = g_armv7_maccess_operand_new(base, off, shift, false, true);      \
        __result;                                                                   \
    })


#define MemAccessPostIndexed(base, off)                                             \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        __result = g_armv7_maccess_operand_new(base, off, NULL, true, true);        \
        __result;                                                                   \
    })


#define MemAccessPostIndexedExtended(base, off, shift)                              \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        __result = g_armv7_maccess_operand_new(base, off, shift, true, true);       \
        __result;                                                                   \
    })


#define MinusBitDiff(msb, lsb)                                                      \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        uint32_t __width;                                                           \
        __width = msb - lsb + 1 + 1;                                                \
        __result = g_imm_operand_new_from_value(MDS_32_BITS_UNSIGNED, __width);     \
        __result;                                                                   \
    })


#define Multiplication(factor, val)                                                 \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        uint32_t __computed;                                                        \
        __computed = factor * val;                                                  \
        __result = g_imm_operand_new_from_value(MDS_32_BITS_UNSIGNED, __computed);  \
        __result;                                                                   \
    })


#define NextDoubleWordVector(ref, n)                                                \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        GArchRegister *__reg;                                                       \
        uint8_t __idx;                                                              \
        __reg = g_register_operand_get_register(G_REGISTER_OPERAND(ref));           \
        __idx = g_arm_register_get_index(G_ARM_REGISTER(__reg));                    \
        g_object_unref(G_OBJECT(__reg));                                            \
        __reg = g_armv7_simd_register_new(SRM_DOUBLE_WORD, __idx + n);              \
        if (__reg == NULL)                                                          \
            __result = NULL;                                                        \
        else                                                                        \
            __result = g_armv7_register_operand_new(G_ARMV7_REGISTER(__reg));       \
        __result;                                                                   \
    })


#define NextRegister(idx)                                                           \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        GArchRegister *__reg;                                                       \
        __reg = g_armv7_basic_register_new(idx + 1);                                \
        if (__reg == NULL)                                                          \
            __result = NULL;                                                        \
        else                                                                        \
            __result = g_armv7_register_operand_new(G_ARMV7_REGISTER(__reg));       \
        __result;                                                                   \
    })


#define NextSingleWordVector(prev)                                                  \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        GArchRegister *__reg;                                                       \
        uint8_t __idx;                                                              \
        __reg = g_register_operand_get_register(G_REGISTER_OPERAND(prev));          \
        __idx = g_arm_register_get_index(G_ARM_REGISTER(__reg));                    \
        g_object_unref(G_OBJECT(__reg));                                            \
        __reg = g_armv7_simd_register_new(SRM_SINGLE_WORD, __idx + 1);              \
        if (__reg == NULL)                                                          \
            __result = NULL;                                                        \
        else                                                                        \
            __result = g_armv7_register_operand_new(G_ARMV7_REGISTER(__reg));       \
        __result;                                                                   \
    })


#define QuadWordVector(idx)                                                         \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        GArchRegister *__reg;                                                       \
        __reg = g_armv7_simd_register_new(SRM_QUAD_WORD, idx);                      \
        if (__reg == NULL)                                                          \
            __result = NULL;                                                        \
        else                                                                        \
            __result = g_armv7_register_operand_new(G_ARMV7_REGISTER(__reg));       \
        __result;                                                                   \
    })


#define Register(idx)                                                               \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        GArchRegister *__reg;                                                       \
        __reg = g_armv7_basic_register_new(idx);                                    \
        if (__reg == NULL)                                                          \
            __result = NULL;                                                        \
        else                                                                        \
            __result = g_armv7_register_operand_new(G_ARMV7_REGISTER(__reg));       \
        __result;                                                                   \
    })


#define RegList(mask)                                                               \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        __result = g_armv7_reglist_operand_new(mask);                               \
        __result;                                                                   \
    })


#define RegListWithoutPC(mask)                                                      \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        GArmV7Register *__pc;                                                       \
        GArmV7RegListOperand *__list;                                               \
        __result = RegList(mask);                                                   \
        if (__result != NULL)                                                       \
        {                                                                           \
            __pc = G_ARMV7_REGISTER(g_armv7_basic_register_new(15));                \
            __list = G_ARMV7_REGLIST_OPERAND(__result);                             \
            if (g_armv7_reglist_operand_has_register(__list, __pc))                 \
            {                                                                       \
                g_object_unref(G_OBJECT(__result));                                 \
                __result = NULL;                                                    \
            }                                                                       \
            g_object_unref(G_OBJECT(__pc));                                         \
        }                                                                           \
        __result;                                                                   \
    })


#define RegListWithPC(mask)                                                         \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        GArmV7Register *__pc;                                                       \
        GArmV7RegListOperand *__list;                                               \
        __result = RegList(mask);                                                   \
        if (__result != NULL)                                                       \
        {                                                                           \
            __pc = G_ARMV7_REGISTER(g_armv7_basic_register_new(15));                \
            __list = G_ARMV7_REGLIST_OPERAND(__result);                             \
            if (!g_armv7_reglist_operand_has_register(__list, __pc))                \
            {                                                                       \
                g_object_unref(G_OBJECT(__result));                                 \
                __result = NULL;                                                    \
            }                                                                       \
            g_object_unref(G_OBJECT(__pc));                                         \
        }                                                                           \
        __result;                                                                   \
    })


#define Rotation(val5)                                                              \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        uint8_t __rot;                                                              \
        GArchOperand *__rot_op;                                                     \
        __rot = val5;                                                               \
        __rot_op = g_imm_operand_new_from_value(MDS_8_BITS_UNSIGNED, __rot);        \
        __result = g_armv7_rotation_operand_new(__rot_op);                          \
        if (__result == NULL)                                                       \
            g_object_unref(G_OBJECT(__rot_op));                                     \
        __result;                                                                   \
    })


#define SignExtend(val, size, top)                                                  \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        MemoryDataSize __mds;                                                       \
        uint ## size ## _t __val;                                                   \
        __mds = MDS_ ## size ## _BITS_SIGNED;                                       \
        __val = armv7_sign_extend(val, top, size);                                  \
        __result = g_imm_operand_new_from_value(__mds, __val);                      \
        __result;                                                                   \
    })


#define SingleRegList(t)                                                            \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        __result = g_armv7_reglist_operand_new(1 << t);                             \
        __result;                                                                   \
    })


#define SingleWordVector(idx)                                                       \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        GArchRegister *__reg;                                                       \
        __reg = g_armv7_simd_register_new(SRM_SINGLE_WORD, idx);                    \
        if (__reg == NULL)                                                          \
            __result = NULL;                                                        \
        else                                                                        \
            __result = g_armv7_register_operand_new(G_ARMV7_REGISTER(__reg));       \
        __result;                                                                   \
    })


#define SpecReg(target)                                                             \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        GArchRegister *__reg;                                                       \
        __reg = g_armv7_special_register_new(target);                               \
        if (__reg == NULL)                                                          \
            __result = NULL;                                                        \
        else                                                                        \
            __result = g_armv7_register_operand_new(G_ARMV7_REGISTER(__reg));       \
        __result;                                                                   \
    })


#define SpecRegFromMask(mask)                                                       \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        GArchRegister *__reg;                                                       \
        switch (mask)                                                               \
        {                                                                           \
            case b10:                                                               \
                __reg = g_armv7_special_register_new(SRT_APSR_NZCVQ);               \
                break;                                                              \
            case b1:                                                                \
                __reg = g_armv7_special_register_new(SRT_APSR_G);                   \
                break;                                                              \
            case b11:                                                               \
                __reg = g_armv7_special_register_new(SRT_APSR_NZCVQG);              \
                break;                                                              \
            default:                                                                \
                __reg = NULL;                                                       \
                break;                                                              \
        }                                                                           \
        if (__reg == NULL)                                                          \
            __result = NULL;                                                        \
        else                                                                        \
            __result = g_armv7_register_operand_new(G_ARMV7_REGISTER(__reg));       \
        __result;                                                                   \
    })


#define SpecRegFromReg(reg)                                                         \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        GArchRegister *__reg;                                                       \
        switch (reg)                                                                \
        {                                                                           \
            case b0:                                                                \
                __reg = g_armv7_special_register_new(SRT_FPSID);                    \
                break;                                                              \
            case b1:                                                                \
                __reg = g_armv7_special_register_new(SRT_FPSCR);                    \
                break;                                                              \
            case b110:                                                              \
                __reg = g_armv7_special_register_new(SRT_MVFR1);                    \
                break;                                                              \
            case b111:                                                              \
                __reg = g_armv7_special_register_new(SRT_MVFR0);                    \
                break;                                                              \
            case b1000:                                                             \
                __reg = g_armv7_special_register_new(SRT_FPEXC);                    \
                break;                                                              \
            default:                                                                \
                __reg = NULL;                                                       \
                break;                                                              \
        }                                                                           \
        if (__reg == NULL)                                                          \
            __result = NULL;                                                        \
        else                                                                        \
            __result = g_armv7_register_operand_new(G_ARMV7_REGISTER(__reg));       \
        __result;                                                                   \
    })


#define SpecRegCSPSR(r)                                                             \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        GArchRegister *__reg;                                                       \
        __reg = g_armv7_special_register_new(r == 1 ? SRT_SPSR : SRT_CPSR);         \
        if (__reg == NULL)                                                          \
            __result = NULL;                                                        \
        else                                                                        \
            __result = g_armv7_register_operand_new(G_ARMV7_REGISTER(__reg));       \
        __result;                                                                   \
    })


#define ThumbExpandImm(imm12)                                                       \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        uint32_t __val;                                                             \
        if (armv7_thumb_expand_imm(imm12, &__val))                                  \
            __result = g_imm_operand_new_from_value(MDS_32_BITS_UNSIGNED, __val);   \
        else                                                                        \
            __result = NULL;                                                        \
        __result;                                                                   \
    })


#define ThumbExpandImm_C(imm12, c)                                                  \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        uint32_t __val;                                                             \
        if (armv7_thumb_expand_imm_c(imm12, (bool []) { c }, &__val))               \
            __result = g_imm_operand_new_from_value(MDS_32_BITS_UNSIGNED, __val);   \
        else                                                                        \
            __result = NULL;                                                        \
        __result;                                                                   \
    })


#define UInt(val)                                                                   \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        __result = g_imm_operand_new_from_value(MDS_32_BITS_UNSIGNED, val);         \
        __result;                                                                   \
    })


#define UIntInc(sat4)                                                               \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        uint8_t __val;                                                              \
        __val = sat4;                                                               \
        __result = g_imm_operand_new_from_value(MDS_8_BITS_UNSIGNED, __val);        \
        __result;                                                                   \
    })


#define UncheckedWrittenBackReg(regop)                                              \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        GArchRegister *__reg;                                                       \
        if (regop == NULL)                                                          \
            __result = NULL;                                                        \
        else                                                                        \
        {                                                                           \
            __reg = g_register_operand_get_register(G_REGISTER_OPERAND(regop));     \
            g_object_unref(G_OBJECT(regop));                                        \
            __result = g_armv7_register_operand_new(G_ARMV7_REGISTER(__reg));       \
        }                                                                           \
        __result;                                                                   \
    })


#define VectorTable(list, count)                                                    \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        size_t __i;                                                                 \
        GArchRegister *__reg;                                                       \
        __result = g_armv7_reglist_operand_new(0);                                  \
        for (__i = 0; __i < count; __i++)                                           \
        {                                                                           \
            __reg = g_register_operand_get_register(G_REGISTER_OPERAND(list[__i])); \
            g_object_unref(G_OBJECT(list[__i]));                                    \
            g_armv7_reglist_add_register(G_ARMV7_REGLIST_OPERAND(__result),         \
                                         G_ARMV7_REGISTER(__reg));                  \
        }                                                                           \
        __result;                                                                   \
    })


#define VectorTableDim1(op1)                                                        \
    VectorTable(((GArchOperand *[]) { op1 }), 1)


#define VectorTableDim2(op1, op2)                                                   \
    VectorTable(((GArchOperand *[]) { op1, op2 }), 2)


#define VectorTableDim3(op1, op2, op3)                                              \
    VectorTable(((GArchOperand *[]) { op1, op2, op3 }), 3)


#define VectorTableDim4(op1, op2, op3, op4)                                         \
    VectorTable(((GArchOperand *[]) { op1, op2, op3, op4 }), 4)


#define WrittenBackReg(regop, writeback)                                            \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        GArchRegister *__reg;                                                       \
        GArmV7RegisterOperand *__armv7_op;                                          \
        if (regop == NULL)                                                          \
            __result = NULL;                                                        \
        else                                                                        \
        {                                                                           \
            __reg = g_register_operand_get_register(G_REGISTER_OPERAND(regop));     \
            g_object_unref(G_OBJECT(regop));                                        \
            __result = g_armv7_register_operand_new(G_ARMV7_REGISTER(__reg));       \
            if (__result != NULL && writeback == 1)                                 \
            {                                                                       \
                __armv7_op = G_ARMV7_REGISTER_OPERAND(__result);                    \
                g_armv7_register_operand_write_back(__armv7_op, true);              \
            }                                                                       \
        }                                                                           \
        __result;                                                                   \
    })


#define Zeros(i)                                                                    \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        MemoryDataSize __mds;                                                       \
        uint ## i ## _t __val;                                                      \
        __mds = MDS_ ## i ## _BITS_UNSIGNED;                                        \
        __val = 0;                                                                  \
        __result = g_imm_operand_new_from_value(__mds, __val);                      \
        __result;                                                                   \
    })


#define ZeroExtend(x, i)                                                            \
    ({                                                                              \
        GArchOperand *__result;                                                     \
        MemoryDataSize __mds;                                                       \
        uint ## i ## _t __val;                                                      \
        __mds = MDS_ ## i ## _BITS_UNSIGNED;                                        \
        __val = armv7_zero_extend(x, -1, i);                                        \
        __result = g_imm_operand_new_from_value(__mds, __val);                      \
        __result;                                                                   \
    })


/**
 * Définitions complémentaires.
 */


#define APSR_C 0


/**
 * Petite glue vers le format ARM générique...
 */


#define g_armv7_instruction_extend_keyword(ins, ext) \
    g_arm_instruction_extend_keyword(G_ARM_INSTRUCTION(ins), ext)



/**
 * Vieilleries à conserver au cas où...
 */


#if 0

#include "cregister.h"
#include "operands/limitation.h"


#define BarrierLimitation(opt)                                              \
    ({                                                                      \
        GArchOperand *__result;                                             \
        __result = g_armv7_limitation_operand_new(opt);                     \
        __result;                                                           \
    })


#define CRegister(idx)                                                      \
    ({                                                                      \
        GArchOperand *__result;                                             \
        GArmV7CRegister *__reg;                                             \
        __reg = g_armv7_cregister_new(idx);                                 \
        if (__reg == NULL)                                                  \
            __result = NULL;                                                \
        else                                                                \
            __result = g_armv7_register_operand_new(__reg);                 \
        __result;                                                           \

#endif



#endif  /* _PLUGINS_ARM_V7_HELPERS_H */
