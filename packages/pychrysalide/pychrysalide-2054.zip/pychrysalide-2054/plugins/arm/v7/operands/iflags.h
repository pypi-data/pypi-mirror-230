
/* Chrysalide - Outil d'analyse de fichiers binaires
 * iflags.h - prototypes pour les opérandes précisant un masque d'interruption ARMv7
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


#ifndef _PLUGINS_ARM_V7_OPERANDS_IFLAGS_H
#define _PLUGINS_ARM_V7_OPERANDS_IFLAGS_H


#include <glib-object.h>
#include <stdbool.h>


#include <arch/operand.h>



/* Etats particuliers d'un opérande de valeur immédiate */
typedef enum _A7IFlagsOpFlag
{
    A7IFOF_ABORT = AOF_USER_FLAG(0),        /* Interruption d'arrêt async. */
    A7IFOF_IRQ   = AOF_USER_FLAG(1),        /* Interruption IRQ            */
    A7IFOF_FIQ   = AOF_USER_FLAG(2),        /* Interruption FIQ            */

} A7IFlagsOpFlag;


#define G_TYPE_ARMV7_IFLAGS_OPERAND            g_armv7_iflags_operand_get_type()
#define G_ARMV7_IFLAGS_OPERAND(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_ARMV7_IFLAGS_OPERAND, GArmV7IFlagsOperand))
#define G_IS_ARMV7_IFLAGS_OPERAND(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_ARMV7_IFLAGS_OPERAND))
#define G_ARMV7_IFLAGS_OPERAND_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ARMV7_IFLAGS_OPERAND, GArmV7IFlagsOperandClass))
#define G_IS_ARMV7_IFLAGS_OPERAND_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ARMV7_IFLAGS_OPERAND))
#define G_ARMV7_IFLAGS_OPERAND_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ARMV7_IFLAGS_OPERAND, GArmV7IFlagsOperandClass))


/* Définition d'un opérande précisant un masque d'interruption ARMv7 (instance) */
typedef struct _GArmV7IFlagsOperand GArmV7IFlagsOperand;

/* Définition d'un opérande précisant un masque d'interruption ARMv7 (classe) */
typedef struct _GArmV7IFlagsOperandClass GArmV7IFlagsOperandClass;


/* Indique le type défini par la GLib pour un opérande de masque d'interruption ARMv7. */
GType g_armv7_iflags_operand_get_type(void);

/* Crée un opérande de masque d'interruption ARMv7. */
GArchOperand *g_armv7_iflags_operand_new(bool, bool, bool);



#endif  /* _PLUGINS_ARM_V7_OPERANDS_IFLAGS_H */
