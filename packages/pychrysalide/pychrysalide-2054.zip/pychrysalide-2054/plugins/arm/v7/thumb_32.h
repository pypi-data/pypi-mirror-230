
/* Chrysalide - Outil d'analyse de fichiers binaires
 * thumb_32.h - prototypes pour le désassemblage des instructions ARMv7 Thumb 32 bits
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


#ifndef _PLUGINS_ARM_V7_THUMB_32_H
#define _PLUGINS_ARM_V7_THUMB_32_H


#include <arch/instruction.h>



/* Désassemble une instruction ARMv7 liées au chapitre A6.3. */
GArchInstruction *process_armv7_thumb_32_instruction_set_encoding(uint32_t);



#endif  /* _PLUGINS_ARM_V7_THUMB_32_H */
