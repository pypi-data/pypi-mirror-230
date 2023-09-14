
/* Chrysalide - Outil d'analyse de fichiers binaires
 * shift.h - prototypes pour les décalages de valeurs
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


#ifndef _PLUGINS_ARM_V7_OPERANDS_SHIFT_H
#define _PLUGINS_ARM_V7_OPERANDS_SHIFT_H


#include <glib-object.h>


#include <arch/operand.h>


#include "../pseudo.h"



#define G_TYPE_ARMV7_SHIFT_OPERAND            g_armv7_shift_operand_get_type()
#define G_ARMV7_SHIFT_OPERAND(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_ARMV7_SHIFT_OPERAND, GArmV7ShiftOperand))
#define G_IS_ARMV7_SHIFT_OPERAND(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_ARMV7_SHIFT_OPERAND))
#define G_ARMV7_SHIFT_OPERAND_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ARMV7_SHIFT_OPERAND, GArmV7ShiftOperandClass))
#define G_IS_ARMV7_SHIFT_OPERAND_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ARMV7_SHIFT_OPERAND))
#define G_ARMV7_SHIFT_OPERAND_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ARMV7_SHIFT_OPERAND, GArmV7ShiftOperandClass))


/* Définition d'un opérande visant une opérande de décalage ARMv7 (instance) */
typedef struct _GArmV7ShiftOperand GArmV7ShiftOperand;

/* Définition d'un opérande visant une opérande de décalage ARMv7 (classe) */
typedef struct _GArmV7ShiftOperandClass GArmV7ShiftOperandClass;


/* Indique le type défini par la GLib pour une opérande de décalage ARMv7. */
GType g_armv7_shift_operand_get_type(void);

/* Crée un réceptacle pour opérande de décalage ARMv7. */
GArchOperand *g_armv7_shift_operand_new(SRType, GArchOperand *);

/* Indique la forme de décalage représenté. */
SRType g_armv7_shift_operand_get_shift_type(const GArmV7ShiftOperand *);

/* Founit la valeur utilisée pour un décalage. */
GArchOperand *g_armv7_shift_operand_get_shift_value(const GArmV7ShiftOperand *);



#endif  /* _PLUGINS_ARM_V7_OPERANDS_SHIFT_H */
