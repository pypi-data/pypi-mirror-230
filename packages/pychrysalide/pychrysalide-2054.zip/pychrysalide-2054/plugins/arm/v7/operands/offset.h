
/* Chrysalide - Outil d'analyse de fichiers binaires
 * offset.h - prototypes pour la constitution d'un décalage positif ou négatif
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


#ifndef _PLUGINS_ARM_V7_OPERANDS_OFFSET_H
#define _PLUGINS_ARM_V7_OPERANDS_OFFSET_H


#include <glib-object.h>
#include <stdbool.h>


#include <arch/operand.h>


#include "../pseudo.h"



/* Etats particuliers d'un opérande de valeur immédiate */
typedef enum _A7OffOpFlag
{
    A7OOF_POSITIVE = AOF_USER_FLAG(0),      /* Sens du décalage            */

} A7OffOpFlag;


#define G_TYPE_ARMV7_OFFSET_OPERAND            g_armv7_offset_operand_get_type()
#define G_ARMV7_OFFSET_OPERAND(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_ARMV7_OFFSET_OPERAND, GArmV7OffsetOperand))
#define G_IS_ARMV7_OFFSET_OPERAND(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_ARMV7_OFFSET_OPERAND))
#define G_ARMV7_OFFSET_OPERAND_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ARMV7_OFFSET_OPERAND, GArmV7OffsetOperandClass))
#define G_IS_ARMV7_OFFSET_OPERAND_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ARMV7_OFFSET_OPERAND))
#define G_ARMV7_OFFSET_OPERAND_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ARMV7_OFFSET_OPERAND, GArmV7OffsetOperandClass))


/* Définition d'un opérande visant à constituer un décalage relatif ARMv7 (instance) */
typedef struct _GArmV7OffsetOperand GArmV7OffsetOperand;

/* Définition d'un opérande visant à constituer un décalage relatif ARMv7 (classe) */
typedef struct _GArmV7OffsetOperandClass GArmV7OffsetOperandClass;


/* Indique le type défini par la GLib pour un décalage relatif ARMv7. */
GType g_armv7_offset_operand_get_type(void);

/* Crée un décalage selon un sens et une valeur donnés. */
GArchOperand *g_armv7_offset_operand_new(bool, GArchOperand *);

/* Founit la valeur utilisée pour un décalage. */
GArchOperand *g_armv7_offset_operand_get_value(const GArmV7OffsetOperand *);



#endif  /* _PLUGINS_ARM_V7_OPERANDS_OFFSET_H */
