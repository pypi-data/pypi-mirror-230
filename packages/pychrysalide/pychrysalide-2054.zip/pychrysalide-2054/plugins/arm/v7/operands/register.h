
/* Chrysalide - Outil d'analyse de fichiers binaires
 * register.h - prototypes pour les opérandes visant un registre ARMv7
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


#ifndef _PLUGINS_ARM_V7_OPERANDS_REGISTER_H
#define _PLUGINS_ARM_V7_OPERANDS_REGISTER_H


#include <glib-object.h>
#include <stdbool.h>


#include <arch/operand.h>


#include "../register.h"



/* Etats particuliers d'un opérande de valeur immédiate */
typedef enum _A7RegOpFlag
{
    A7ROF_HAS_ALIGNMENT = AOF_USER_FLAG(0), /* Validité de l'alignement    */
    A7ROF_WRITE_BACK    = AOF_USER_FLAG(1), /* Mise à jour du registre ?   */

} A7RegOpFlag;


#define G_TYPE_ARMV7_REGISTER_OPERAND            g_armv7_register_operand_get_type()
#define G_ARMV7_REGISTER_OPERAND(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_ARMV7_REGISTER_OPERAND, GArmV7RegisterOperand))
#define G_IS_ARMV7_REGISTER_OPERAND(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_ARMV7_REGISTER_OPERAND))
#define G_ARMV7_REGISTER_OPERAND_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ARMV7_REGISTER_OPERAND, GArmV7RegisterOperandClass))
#define G_IS_ARMV7_REGISTER_OPERAND_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ARMV7_REGISTER_OPERAND))
#define G_ARMV7_REGISTER_OPERAND_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ARMV7_REGISTER_OPERAND, GArmV7RegisterOperandClass))


/* Définition d'un opérande visant un registre ARMv7 (instance) */
typedef struct _GArmV7RegisterOperand GArmV7RegisterOperand;

/* Définition d'un opérande visant un registre ARMv7 (classe) */
typedef struct _GArmV7RegisterOperandClass GArmV7RegisterOperandClass;


/* Indique le type défini par la GLib pour un opérande de registre ARMv7. */
GType g_armv7_register_operand_get_type(void);

/* Crée un opérande visant un registre ARMv7. */
GArchOperand *g_armv7_register_operand_new(GArmV7Register *);

/* Définit un alignement à appliquer à l'opérande de registre. */
void g_armv7_register_operand_define_alignement(GArmV7RegisterOperand *, unsigned int);

/* Détermine si le registre est mis à jour après l'opération. */
void g_armv7_register_operand_write_back(GArmV7RegisterOperand *, bool);



#endif  /* _PLUGINS_ARM_V7_OPERANDS_REGISTER_H */
