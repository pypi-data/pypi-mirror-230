
/* Chrysalide - Outil d'analyse de fichiers binaires
 * post.h - prototypes pour les traitements complémentaires à la phase de désassemblage
 *
 * Copyright (C) 2016-2018 Cyrille Bagard
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


#ifndef _ARCH_POST_H
#define _ARCH_POST_H


#include "instruction.h"
#include "../format/symbol.h"



/* Associe un symbole à la valeur ciblée par un opérande. */
void post_process_target_resolution(GArchInstruction *, GArchProcessor *, GProcContext *, GExeFormat *, size_t, SymbolType);



#endif  /* _ARCH_POST_H */
