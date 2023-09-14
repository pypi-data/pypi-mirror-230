
/* Chrysalide - Outil d'analyse de fichiers binaires
 * it.h - prototypes pour la manipulation des informations de l'instruction TI
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


#ifndef _PLUGINS_ARM_V7_OPERANDS_IT_H
#define _PLUGINS_ARM_V7_OPERANDS_IT_H


#include <glib-object.h>


#include <arch/operand.h>


#include "../../cond.h"



#define G_TYPE_ARMV7_ITCOND_OPERAND            g_armv7_itcond_operand_get_type()
#define G_ARMV7_ITCOND_OPERAND(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_ARMV7_ITCOND_OPERAND, GArmV7ITCondOperand))
#define G_IS_ARMV7_ITCOND_OPERAND(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_ARMV7_ITCOND_OPERAND))
#define G_ARMV7_ITCOND_OPERAND_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ARMV7_ITCOND_OPERAND, GArmV7ITCondOperandClass))
#define G_IS_ARMV7_ITCOND_OPERAND_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ARMV7_ITCOND_OPERAND))
#define G_ARMV7_ITCOND_OPERAND_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ARMV7_ITCOND_OPERAND, GArmV7ITCondOperandClass))


/* Définition d'un opérande organisant l'application d'une instruction IT (instance) */
typedef struct _GArmV7ITCondOperand GArmV7ITCondOperand;

/* Définition d'un opérande organisant l'application d'une instruction IT (classe) */
typedef struct _GArmV7ITCondOperandClass GArmV7ITCondOperandClass;


/* Indique le type défini par la GLib pour l'application d'une instruction IT. */
GType g_armv7_itcond_operand_get_type(void);

/* Crée un opérande lié à une instruction IT. */
GArchOperand *g_armv7_itcond_operand_new(uint8_t, uint8_t);

/* Fournit la condition associée à l'opérande. */
ArmCondCode g_armv7_itcond_operand_get_firstcond(const GArmV7ITCondOperand *);

/* Fournit le masque d'interprétation de la condition. */
uint8_t g_armv7_itcond_operand_get_mask(const GArmV7ITCondOperand *);



#endif  /* _PLUGINS_ARM_V7_OPERANDS_IT_H */
