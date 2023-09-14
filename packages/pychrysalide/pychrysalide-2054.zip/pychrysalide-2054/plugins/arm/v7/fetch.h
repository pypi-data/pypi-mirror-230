
/* Chrysalide - Outil d'analyse de fichiers binaires
 * fetch.h - prototypes pour les ajouts de sauts à traiter durant la phase de désassemblage
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


#ifndef _PLUGINS_ARM_V7_FETCH_H
#define _PLUGINS_ARM_V7_FETCH_H


#include <arch/instruction.h>


#include "context.h"



/* Complète un désassemblage accompli pour une instruction. */
void help_fetching_with_instruction_b_with_orig(GArchInstruction *, GArchProcessor *, GArmV7Context *, GExeFormat *, ArmV7InstrSet);


static inline void help_fetching_with_instruction_b_from_arm(GArchInstruction *ins, GArchProcessor *proc, GArmV7Context *ctx, GExeFormat *fmt)
{
    help_fetching_with_instruction_b_with_orig(ins, proc, ctx, fmt, AV7IS_ARM);
}

static inline void help_fetching_with_instruction_b_from_thumb(GArchInstruction *ins, GArchProcessor *proc, GArmV7Context *ctx, GExeFormat *fmt)
{
    help_fetching_with_instruction_b_with_orig(ins, proc, ctx, fmt, AV7IS_THUMB);
}


/* Complète un désassemblage accompli pour une instruction. */
void help_fetching_with_instruction_bl_with_orig(GArchInstruction *, GArchProcessor *, GArmV7Context *, GExeFormat *, ArmV7InstrSet);


static inline void help_fetching_with_instruction_bl_from_arm(GArchInstruction *ins, GArchProcessor *proc, GArmV7Context *ctx, GExeFormat *fmt)
{
    help_fetching_with_instruction_bl_with_orig(ins, proc, ctx, fmt, AV7IS_ARM);
}

static inline void help_fetching_with_instruction_bl_from_thumb(GArchInstruction *ins, GArchProcessor *proc, GArmV7Context *ctx, GExeFormat *fmt)
{
    help_fetching_with_instruction_bl_with_orig(ins, proc, ctx, fmt, AV7IS_THUMB);
}


/* Complète un désassemblage accompli pour une instruction. */
void help_fetching_with_instruction_blx_with_dest(GArchInstruction *, GArchProcessor *, GArmV7Context *, GExeFormat *, ArmV7InstrSet);


static inline void help_fetching_with_instruction_blx_from_arm(GArchInstruction *ins, GArchProcessor *proc, GArmV7Context *ctx, GExeFormat *fmt)
{
    help_fetching_with_instruction_blx_with_dest(ins, proc, ctx, fmt, AV7IS_THUMB);
}

static inline void help_fetching_with_instruction_blx_from_thumb(GArchInstruction *ins, GArchProcessor *proc, GArmV7Context *ctx, GExeFormat *fmt)
{
    help_fetching_with_instruction_blx_with_dest(ins, proc, ctx, fmt, AV7IS_ARM);
}


/* Complète un désassemblage accompli pour une instruction. */
void help_fetching_with_instruction_bx_with_orig(GArchInstruction *, GArchProcessor *, GArmV7Context *, GExeFormat *, ArmV7InstrSet);


static inline void help_fetching_with_instruction_bx_from_arm(GArchInstruction *ins, GArchProcessor *proc, GArmV7Context *ctx, GExeFormat *fmt)
{
    help_fetching_with_instruction_bx_with_orig(ins, proc, ctx, fmt, AV7IS_ARM);
}

static inline void help_fetching_with_instruction_bx_from_thumb(GArchInstruction *ins, GArchProcessor *proc, GArmV7Context *ctx, GExeFormat *fmt)
{
    help_fetching_with_instruction_bx_with_orig(ins, proc, ctx, fmt, AV7IS_THUMB);
}


/* Complète un désassemblage accompli pour une instruction. */
void help_fetching_with_instruction_cb_n_z(GArchInstruction *, GArchProcessor *, GArmV7Context *, GExeFormat *);

/* Complète un désassemblage accompli pour une instruction. */
void help_fetching_with_instruction_ldr_literal_with_orig(GArchInstruction *, GArchProcessor *, GArmV7Context *, GExeFormat *, ArmV7InstrSet);


static inline void help_fetching_with_instruction_ldr_literal_from_arm(GArchInstruction *ins, GArchProcessor *proc, GArmV7Context *ctx, GExeFormat *fmt)
{
    help_fetching_with_instruction_ldr_literal_with_orig(ins, proc, ctx, fmt, AV7IS_ARM);
}

static inline void help_fetching_with_instruction_ldr_literal_from_thumb(GArchInstruction *ins, GArchProcessor *proc, GArmV7Context *ctx, GExeFormat *fmt)
{
    help_fetching_with_instruction_ldr_literal_with_orig(ins, proc, ctx, fmt, AV7IS_THUMB);
}


/* Applique la mise à jour d'un registre après coup. */
void apply_write_back(GArchInstruction *, GArchProcessor *, GArmV7Context *, GExeFormat *, ArmV7InstrSet);

/* Applique la mise à jour d'un registre après coup au besoin. */
void apply_write_back_from_registers(GArchInstruction *, GArchProcessor *, GArmV7Context *, GExeFormat *, ArmV7InstrSet);

/* Construit un suffixe adapté à une instruction IT. */
void build_it_instruction_suffix(GArchInstruction *, GArchProcessor *, GArmV7Context *, GExeFormat *, ArmV7InstrSet);



#endif  /* _PLUGINS_ARM_V7_FETCH_H */
