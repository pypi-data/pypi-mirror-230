
/* Chrysalide - Outil d'analyse de fichiers binaires
 * operand.h - prototypes pour les opérandes ARMv7
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


#ifndef _PLUGINS_ARM_V7_OPERAND_H
#define _PLUGINS_ARM_V7_OPERAND_H


#include <glib-object.h>


#include <arch/operand.h>



#define G_TYPE_ARMV7_OPERAND            g_armv7_operand_get_type()
#define G_ARMV7_OPERAND(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_ARMV7_OPERAND, GArmV7Operand))
#define G_IS_ARMV7_OPERAND(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_ARMV7_OPERAND))
#define G_ARMV7_OPERAND_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ARMV7_OPERAND, GArmV7OperandClass))
#define G_IS_ARMV7_OPERAND_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ARMV7_OPERAND))
#define G_ARMV7_OPERAND_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ARMV7_OPERAND, GArmV7OperandClass))


/* Définition générique d'un opérande ARMv7 (instance) */
typedef struct _GArmV7Operand GArmV7Operand;

/* Définition générique d'un opérande ARMv7 (classe) */
typedef struct _GArmV7OperandClass GArmV7OperandClass;


/* Indique le type défini par la GLib pour un opérande ARMv7. */
GType g_armv7_operand_get_type(void);



#endif  /* _PLUGINS_ARM_V7_OPERAND_H */
