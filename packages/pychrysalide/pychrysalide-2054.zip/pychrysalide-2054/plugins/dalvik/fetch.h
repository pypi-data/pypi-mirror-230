
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


#ifndef _PLUGINS_DALVIK_FETCH_H
#define _PLUGINS_DALVIK_FETCH_H


#include <arch/instruction.h>


#include "context.h"



/* Pousse une adresse précisée par un saut pour désassemblage. */
void help_fetching_with_dalvik_instruction(GArchInstruction *, GArchProcessor *, GDalvikContext *, GExeFormat *, size_t);


static inline void help_fetching_with_dalvik_fill_array_data_instruction(GArchInstruction *ins, GArchProcessor *proc, GDalvikContext *ctx, GExeFormat *fmt)
{
    help_fetching_with_dalvik_instruction(ins, proc, ctx, fmt, 1);
}

static inline void help_fetching_with_dalvik_goto_instruction(GArchInstruction *ins, GArchProcessor *proc, GDalvikContext *ctx, GExeFormat *fmt)
{
    help_fetching_with_dalvik_instruction(ins, proc, ctx, fmt, 0);
}

static inline void help_fetching_with_dalvik_if_instruction(GArchInstruction *ins, GArchProcessor *proc, GDalvikContext *ctx, GExeFormat *fmt)
{
    help_fetching_with_dalvik_instruction(ins, proc, ctx, fmt, 2);
}

static inline void help_fetching_with_dalvik_ifz_instruction(GArchInstruction *ins, GArchProcessor *proc, GDalvikContext *ctx, GExeFormat *fmt)
{
    help_fetching_with_dalvik_instruction(ins, proc, ctx, fmt, 1);
}



#endif  /* _PLUGINS_DALVIK_FETCH_H */
