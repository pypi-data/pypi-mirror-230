
/* Chrysalide - Outil d'analyse de fichiers binaires
 * post.h - prototypes pour les traitements complémentaires à la phase de désassemblage
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


#ifndef _PLUGINS_ARM_V7_POST_H
#define _PLUGINS_ARM_V7_POST_H


#include <arch/post.h>



static inline void post_process_branch_instructions(GArchInstruction *ins, GArchProcessor *proc, GProcContext *ctx, GExeFormat *fmt)
{
    post_process_target_resolution(ins, proc, ctx, fmt, 0, STP_CODE_LABEL);

}

static inline void post_process_branch_and_link_instructions(GArchInstruction *ins, GArchProcessor *proc, GProcContext *ctx, GExeFormat *fmt)
{
    post_process_target_resolution(ins, proc, ctx, fmt, 0, STP_ROUTINE);

}

static inline void post_process_comp_and_branch_instructions(GArchInstruction *ins, GArchProcessor *proc, GProcContext *ctx, GExeFormat *fmt)
{
    post_process_target_resolution(ins, proc, ctx, fmt, 1, STP_CODE_LABEL);

}


/* Complète un désassemblage accompli pour une instruction. */
void post_process_ldr_instructions(GArchInstruction *, GArchProcessor *, GProcContext *, GExeFormat *);



#endif  /* _PLUGINS_ARM_V7_POST_H */
