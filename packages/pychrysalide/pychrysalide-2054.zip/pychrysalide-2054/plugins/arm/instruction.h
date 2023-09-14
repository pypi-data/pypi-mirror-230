
/* Chrysalide - Outil d'analyse de fichiers binaires
 * instruction.h - prototypes pour la gestion des instructions ARM
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


#ifndef _PLUGINS_ARM_INSTRUCTION_H
#define _PLUGINS_ARM_INSTRUCTION_H


#include <glib-object.h>
#include <stdbool.h>
#include <stdint.h>


#include <arch/instruction.h>


#include "cond.h"



#define G_TYPE_ARM_INSTRUCTION               g_arm_instruction_get_type()
#define G_ARM_INSTRUCTION(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), g_arm_instruction_get_type(), GArmInstruction))
#define G_IS_ARM_INSTRUCTION(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_arm_instruction_get_type()))
#define G_ARM_INSTRUCTION_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ARM_INSTRUCTION, GArmInstructionClass))
#define G_IS_ARM_INSTRUCTION_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ARM_INSTRUCTION))
#define G_ARM_INSTRUCTION_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ARM_INSTRUCTION, GArmInstructionClass))


/* Définition d'une instruction d'architecture ARM (instance) */
typedef struct _GArmInstruction GArmInstruction;

/* Définition d'une instruction d'architecture ARM (classe) */
typedef struct _GArmInstructionClass GArmInstructionClass;


/* Indique le type défini pour une représentation d'une instruction ARM. */
GType g_arm_instruction_get_type(void);

/* Etend la désignation d'un nom d'instruction. */
bool g_arm_instruction_extend_keyword(GArmInstruction *, const char *);

/* Définit les conditions d'exécution d'une instruction ARM. */
bool g_arm_instruction_set_cond(GArmInstruction *, ArmCondCode);

/* Indique les conditions d'exécution d'une instruction ARM. */
ArmCondCode g_arm_instruction_get_cond(const GArmInstruction *);



#endif  /* _PLUGINS_ARM_INSTRUCTION_H */
