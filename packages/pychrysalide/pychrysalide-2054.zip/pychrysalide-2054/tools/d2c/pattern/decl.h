
/* Chrysalide - Outil d'analyse de fichiers binaires
 * decl.h - déclarations de prototypes utiles
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#ifndef _TOOLS_D2C_PATTERN_DECL_H
#define _TOOLS_D2C_PATTERN_DECL_H


#include "manager.h"



/* Interprête des données liées à une définition de syntaxe. */
bool load_asm_pattern_from_raw_line(asm_pattern *, const char *);



#endif  /* _TOOLS_D2C_PATTERN_DECL_H */
