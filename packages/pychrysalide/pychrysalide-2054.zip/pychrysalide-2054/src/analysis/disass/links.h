
/* Chrysalide - Outil d'analyse de fichiers binaires
 * links.h - prototypes pour la résolution des liens entre différentes instructions
 *
 * Copyright (C) 2010-2018 Cyrille Bagard
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


#ifndef _ANALYSIS_DISASS_LINKS_H
#define _ANALYSIS_DISASS_LINKS_H


#include "../../arch/instruction.h"
#include "../../arch/processor.h"
#include "../../format/format.h"



/* Rétablit un lien naturel coupé par un autre lien. */
void establish_natural_link(GArchInstruction *, GArchInstruction *);

/* Complète un désassemblage accompli pour une instruction. */
void establish_links_for_instruction(GArchInstruction *, GBinFormat *, GArchProcessor *);



#endif  /* _ANALYSIS_DISASS_LINKS_H */
