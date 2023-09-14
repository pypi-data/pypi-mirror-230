
/* Chrysalide - Outil d'analyse de fichiers binaires
 * link.h - prototypes pour l'édition des liens après la phase de désassemblage
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


#ifndef _PLUGINS_DALVIK_LINK_H
#define _PLUGINS_DALVIK_LINK_H


#include <arch/link.h>



/* Etablit une référence entre utilisation et origine de chaîne. */
void handle_links_for_dalvik_string(GArchInstruction *, GArchProcessor *, GProcContext *, GExeFormat *);


static inline void handle_dalvik_if_branch_as_link(GArchInstruction *ins, GArchProcessor *proc, GProcContext *ctx, GExeFormat *fmt)
{
    handle_branch_as_link(ins, proc, ctx, fmt, 2);
}

static inline void handle_dalvik_ifz_branch_as_link(GArchInstruction *ins, GArchProcessor *proc, GProcContext *ctx, GExeFormat *fmt)
{
    handle_branch_as_link(ins, proc, ctx, fmt, 1);
}


/* Etablit tous les liens liés à un embranchement compressé. */
void handle_dalvik_packed_switch_links(GArchInstruction *, GArchProcessor *, GProcContext *, GExeFormat *);

/* Etablit une référence entre appelant et appelé. */
void handle_links_between_caller_and_callee(GArchInstruction *, GArchProcessor *, GProcContext *, GExeFormat *);



#endif  /* _PLUGINS_DALVIK_LINK_H */
