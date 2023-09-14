
/* Chrysalide - Outil d'analyse de fichiers binaires
 * operand.h - prototypes pour l'aide à la création d'opérandes Dalvik
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


#ifndef _PLUGINS_DALVIK_OPERAND_H
#define _PLUGINS_DALVIK_OPERAND_H


#include <arch/instruction.h>
#include <plugins/dex/format.h>


#include "operands/args.h"
#include "operands/pool.h"
#include "operands/register.h"



/**
 * Cf. les documentations suivantes :
 * - http://www.netmite.com/android/mydroid/dalvik/docs/instruction-formats.html
 * - http://www.netmite.com/android/mydroid/dalvik/docs/dalvik-bytecode.html
 * - http://pallergabor.uw.hu/androidblog/dalvik_opcodes.html
 */


/* Construction d'identifiants typés */

#define DALVIK_OP_LEN_OFF   28
#define DALVIK_OP_LEN_MASK  0xf0000000

#define DALVIK_OP_REG_OFF   24
#define DALVIK_OP_REG_MASK  0x0f000000
#define DALVIK_OP_REG_RANGE 0xf

#define DALVIK_OP_POOL_OFF  20
#define DALVIK_OP_POOL_MASK 0x00f00000

#define DALVIK_OP_BASE_MASK(b) (b & ~DALVIK_OP_POOL_MASK)

#define DALVIK_OP_LEN(l)        ((l) << DALVIK_OP_LEN_OFF)
#define DALVIK_OP_GET_LEN(v)    (((v) & DALVIK_OP_LEN_MASK) >> DALVIK_OP_LEN_OFF)

#define DALVIK_OP_REG(r)        ((r) << DALVIK_OP_REG_OFF)
#define DALVIK_OP_COUNT_REG(v)  (((v) & DALVIK_OP_REG_MASK) >> DALVIK_OP_REG_OFF)

#define DALVIK_OP_POOL(p)       ((p) << DALVIK_OP_POOL_OFF)
#define DALVIK_OP_GET_POOL(v)   (((v) & DALVIK_OP_POOL_MASK) >> DALVIK_OP_POOL_OFF)

#define DALVIK_OP_MNEMONIC_1(v0)         ((v0) - 'a')
#define DALVIK_OP_MNEMONIC_2(v0, v1)     (((v0) - 'a') | ((v1) - 'a') << 5)
#define DALVIK_OP_MNEMONIC_3(v0, v1, v2) (((v0) - 'a') | ((v1) - 'a') << 5 | ((v2) - 'a') << 10)

#define DALVIK_OP_GET_MNEMONIC(v) (v & 0x7fff)


/* Types d'opérandes supportés */
typedef enum _DalvikOperandType
{
    DALVIK_OPT_10T = DALVIK_OP_LEN(1) | DALVIK_OP_REG(0) | DALVIK_OP_MNEMONIC_1('t'),
    DALVIK_OPT_10X = DALVIK_OP_LEN(1) | DALVIK_OP_REG(0) | DALVIK_OP_MNEMONIC_1('x'),

    DALVIK_OPT_11N = DALVIK_OP_LEN(1) | DALVIK_OP_REG(1) | DALVIK_OP_MNEMONIC_1('n'),
    DALVIK_OPT_11X = DALVIK_OP_LEN(1) | DALVIK_OP_REG(1) | DALVIK_OP_MNEMONIC_1('x'),

    DALVIK_OPT_12X = DALVIK_OP_LEN(1) | DALVIK_OP_REG(2) | DALVIK_OP_MNEMONIC_1('x'),

    DALVIK_OPT_20T = DALVIK_OP_LEN(2) | DALVIK_OP_REG(0) | DALVIK_OP_MNEMONIC_1('t'),

    DALVIK_OPT_21C = DALVIK_OP_LEN(2) | DALVIK_OP_REG(1) | DALVIK_OP_MNEMONIC_1('c'),
    DALVIK_OPT_21H = DALVIK_OP_LEN(2) | DALVIK_OP_REG(1) | DALVIK_OP_MNEMONIC_1('h'),
    DALVIK_OPT_21S = DALVIK_OP_LEN(2) | DALVIK_OP_REG(1) | DALVIK_OP_MNEMONIC_1('s'),
    DALVIK_OPT_21T = DALVIK_OP_LEN(2) | DALVIK_OP_REG(1) | DALVIK_OP_MNEMONIC_1('t'),

    DALVIK_OPT_22B = DALVIK_OP_LEN(2) | DALVIK_OP_REG(2) | DALVIK_OP_MNEMONIC_1('b'),
    DALVIK_OPT_22C = DALVIK_OP_LEN(2) | DALVIK_OP_REG(2) | DALVIK_OP_MNEMONIC_1('c'),
    DALVIK_OPT_22S = DALVIK_OP_LEN(2) | DALVIK_OP_REG(2) | DALVIK_OP_MNEMONIC_1('s'),
    DALVIK_OPT_22T = DALVIK_OP_LEN(2) | DALVIK_OP_REG(2) | DALVIK_OP_MNEMONIC_1('t'),
    DALVIK_OPT_22X = DALVIK_OP_LEN(2) | DALVIK_OP_REG(2) | DALVIK_OP_MNEMONIC_1('x'),

    DALVIK_OPT_23X = DALVIK_OP_LEN(2) | DALVIK_OP_REG(3) | DALVIK_OP_MNEMONIC_1('x'),

    DALVIK_OPT_30T = DALVIK_OP_LEN(3) | DALVIK_OP_REG(0) | DALVIK_OP_MNEMONIC_1('t'),

    DALVIK_OPT_31C = DALVIK_OP_LEN(3) | DALVIK_OP_REG(1) | DALVIK_OP_MNEMONIC_1('c'),
    DALVIK_OPT_31I = DALVIK_OP_LEN(3) | DALVIK_OP_REG(1) | DALVIK_OP_MNEMONIC_1('i'),
    DALVIK_OPT_31T = DALVIK_OP_LEN(3) | DALVIK_OP_REG(1) | DALVIK_OP_MNEMONIC_1('t'),

    DALVIK_OPT_32X = DALVIK_OP_LEN(3) | DALVIK_OP_REG(2) | DALVIK_OP_MNEMONIC_1('x'),

    DALVIK_OPT_35C = DALVIK_OP_LEN(3) | DALVIK_OP_REG(5) | DALVIK_OP_MNEMONIC_1('c'),

    DALVIK_OPT_3RC = DALVIK_OP_LEN(3) | DALVIK_OP_REG(DALVIK_OP_REG_RANGE) | DALVIK_OP_MNEMONIC_2('r', 'c'),

    DALVIK_OPT_51L = DALVIK_OP_LEN(5) | DALVIK_OP_REG(1) | DALVIK_OP_MNEMONIC_1('l')

} DalvikOperandType;


/* Procède à la lecture d'opérandes pour une instruction. */
bool dalvik_read_operands(GArchInstruction *, GExeFormat *, const GBinContent *, vmpa2t *, SourceEndian, DalvikOperandType);

/* Procède à la lecture d'opérandes pour une instruction. */
void dalvik_mark_first_operand_as_written(GArchInstruction *);



#endif  /* _PLUGINS_DALVIK_OPERAND_H */
