
/* Chrysalide - Outil d'analyse de fichiers binaires
 * disassembler.h - prototypes pour l'encadrement des phases de désassemblage
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


#ifndef _ANALYSIS_DISASS_DISASSEMBLER_H
#define _ANALYSIS_DISASS_DISASSEMBLER_H


#include "../binary.h"
#include "../../glibext/delayed.h"



/* Procède au désassemblage d'un contenu binaire donné. */
void disassemble_binary(GLoadedBinary *, wgroup_id_t, GtkStatusStack *, GProcContext **);

/* Imprime le résultat d'un désassemblage. */
void output_disassembly(GLoadedBinary *, GProcContext *, GtkStatusStack *, GBufferCache **);



#endif  /* _ANALYSIS_DISASS_DISASSEMBLER_H */
