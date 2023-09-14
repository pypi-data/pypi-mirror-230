
/* Chrysalide - Outil d'analyse de fichiers binaires
 * instruction.h - prototypes pour la gestion des instructions ARMv7
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


#ifndef _PLUGINS_ARM_V7_INSTRUCTION_H
#define _PLUGINS_ARM_V7_INSTRUCTION_H


#include <glib-object.h>
#include <stdbool.h>
#include <stdint.h>


#include <arch/instruction.h>


#include "opcodes/subidentifiers.h"



#define G_TYPE_ARMV7_INSTRUCTION            g_armv7_instruction_get_type()
#define G_ARMV7_INSTRUCTION(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_ARMV7_INSTRUCTION, GArmV7Instruction))
#define G_IS_ARMV7_INSTRUCTION(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_ARMV7_INSTRUCTION))
#define G_ARMV7_INSTRUCTION_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ARMV7_INSTRUCTION, GArmV7InstructionClass))
#define G_IS_ARMV7_INSTRUCTION_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ARMV7_INSTRUCTION))
#define G_ARMV7_INSTRUCTION_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ARMV7_INSTRUCTION, GArmV7InstructionClass))


/* Définition d'une instruction d'architecture ARMv7 (instance) */
typedef struct _GArmV7Instruction GArmV7Instruction;

/* Définition d'une instruction d'architecture ARMv7 (classe) */
typedef struct _GArmV7InstructionClass GArmV7InstructionClass;


/* Indique le type défini pour une représentation d'une instruction ARMv7. */
GType g_armv7_instruction_get_type(void);

/* Crée une instruction pour l'architecture ARMv7. */
GArchInstruction *g_armv7_instruction_new(itid_t, ARMv7Syntax);

/* Précise l'encodage d'une instruction ARMv7 dans le détail. */
void g_armv7_instruction_set_encoding(GArmV7Instruction *, const char *);

/* Définit si une instruction ARMv7 met à jour les drapeaux. */
bool g_armv7_instruction_define_setflags(GArmV7Instruction *, bool);

/* Indique si une instruction ARMv7 met à jour les drapeaux. */
bool g_armv7_instruction_get_setflags(const GArmV7Instruction *);



#endif  /* _PLUGINS_ARM_V7_INSTRUCTION_H */
