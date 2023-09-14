
/* Chrysalide - Outil d'analyse de fichiers binaires
 * estate.h - prototypes pour le basculement de boutisme
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


#ifndef _PLUGINS_ARM_V7_OPERANDS_ESTATE_H
#define _PLUGINS_ARM_V7_OPERANDS_ESTATE_H


#include <glib-object.h>


#include <arch/operand.h>



/* Etats particuliers d'un opérande de valeur immédiate */
typedef enum _A7EStateOpFlag
{
    A7ESOF_BIG = AOF_USER_FLAG(0),          /* Grand boutisme à afficher ? */

} A7EStateOpFlag;


#define G_TYPE_ARMV7_ENDIAN_OPERAND            g_armv7_endian_operand_get_type()
#define G_ARMV7_ENDIAN_OPERAND(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_ARMV7_ENDIAN_OPERAND, GArmV7EndianOperand))
#define G_IS_ARMV7_ENDIAN_OPERAND(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_ARMV7_ENDIAN_OPERAND))
#define G_ARMV7_ENDIAN_OPERAND_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ARMV7_ENDIAN_OPERAND, GArmV7EndianOperandClass))
#define G_IS_ARMV7_ENDIAN_OPERAND_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ARMV7_ENDIAN_OPERAND))
#define G_ARMV7_ENDIAN_OPERAND_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ARMV7_ENDIAN_OPERAND, GArmV7EndianOperandClass))


/* Définition d'un opérande affichant le choix d'un boutisme (instance) */
typedef struct _GArmV7EndianOperand GArmV7EndianOperand;

/* Définition d'un opérande affichant le choix d'un boutisme (classe) */
typedef struct _GArmV7EndianOperandClass GArmV7EndianOperandClass;


/* Indique le type défini par la GLib pour une endian de domaine et d'accès. */
GType g_armv7_endian_operand_get_type(void);

/* Crée une représentation de boutisme ARMv7. */
GArchOperand *g_armv7_endian_operand_new(bool);



#endif  /* _PLUGINS_ARM_V7_OPERANDS_ESTATE_H */
