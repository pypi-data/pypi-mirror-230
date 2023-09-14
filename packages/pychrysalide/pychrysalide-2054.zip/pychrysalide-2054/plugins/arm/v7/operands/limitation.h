
/* Chrysalide - Outil d'analyse de fichiers binaires
 * limitation.h - prototypes pour les décalages de valeurs
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


#ifndef _PLUGINS_ARM_V7_OPERANDS_LIMITATION_H
#define _PLUGINS_ARM_V7_OPERANDS_LIMITATION_H


#include <glib-object.h>


#include <arch/operand.h>



#define G_TYPE_ARMV7_LIMITATION_OPERAND            g_armv7_limitation_operand_get_type()
#define G_ARMV7_LIMITATION_OPERAND(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_ARMV7_LIMITATION_OPERAND, GArmV7LimitationOperand))
#define G_IS_ARMV7_LIMITATION_OPERAND(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_ARMV7_LIMITATION_OPERAND))
#define G_ARMV7_LIMITATION_OPERAND_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ARMV7_LIMITATION_OPERAND, GArmV7LimitationOperandClass))
#define G_IS_ARMV7_LIMITATION_OPERAND_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ARMV7_LIMITATION_OPERAND))
#define G_ARMV7_LIMITATION_OPERAND_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ARMV7_LIMITATION_OPERAND, GArmV7LimitationOperandClass))


/* Définition d'un opérande déterminant une limitation de domaine et d'accès (instance) */
typedef struct _GArmV7LimitationOperand GArmV7LimitationOperand;

/* Définition d'un opérande déterminant une limitation de domaine et d'accès (classe) */
typedef struct _GArmV7LimitationOperandClass GArmV7LimitationOperandClass;


/* Types de limitation domaine & accès */
typedef enum _BarrierLimitationType
{
    BLT_RESERVED    = 0,
    BLT_SY          = 0b1111,
    BLT_ST          = 0b1110,
    BLT_ISH         = 0b1011,
    BLT_ISHST       = 0b1010,
    BLT_NSH         = 0b0111,
    BLT_NSHST       = 0b0110,
    BLT_OSH         = 0b0011,
    BLT_OSHST       = 0b0010

} BarrierLimitationType;


/* Indique le type défini par la GLib pour une limitation de domaine et d'accès. */
GType g_armv7_limitation_operand_get_type(void);

/* Crée une représentation d'une limitation pour barrière. */
GArchOperand *g_armv7_limitation_operand_new(uint8_t);

/* Indique le type de limitation représentée. */
BarrierLimitationType g_armv7_limitation_operand_get_value(const GArmV7LimitationOperand *);



#endif  /* _PLUGINS_ARM_V7_OPERANDS_LIMITATION_H */
