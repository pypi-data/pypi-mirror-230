
/* Chrysalide - Outil d'analyse de fichiers binaires
 * link.h - prototypes pour l'édition des liens après la phase de désassemblage
 *
 * Copyright (C) 2015-2018 Cyrille Bagard
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


#ifndef _ARCH_LINK_H
#define _ARCH_LINK_H


#include "instruction.h"
#include "processor.h"



/* Etablit un lien de saut selon une instruction donnée. */
void handle_jump_as_link(GArchInstruction *, GArchProcessor *, GProcContext *, GExeFormat *);

/* Etablit un lien d'appel selon une instruction donnée. */
void handle_branch_as_link(GArchInstruction *, GArchProcessor *, GProcContext *, GExeFormat *, size_t);


static inline void handle_branch_if_true_as_link(GArchInstruction *ins, GArchProcessor *proc, GProcContext *ctx, GExeFormat *fmt)
{
    handle_branch_as_link(ins, proc, ctx, fmt, 0);
}

static inline void handle_comp_and_branch_if_true_as_link(GArchInstruction *ins, GArchProcessor *proc, GProcContext *ctx, GExeFormat *fmt)
{
    handle_branch_as_link(ins, proc, ctx, fmt, 1);
}


/* Etablit un lien d'appel selon une instruction donnée. */
void handle_call_as_link(GArchInstruction *, GArchProcessor *, GProcContext *, GExeFormat *);



#endif  /* _ARCH_LINK_H */
