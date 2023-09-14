
/* Chrysalide - Outil d'analyse de fichiers binaires
 * maccess.h - prototypes pour les accès à la mémorie à partir d'un registre et d'un décalage
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


#ifndef _PLUGINS_ARM_V7_OPERANDS_MACCESS_H
#define _PLUGINS_ARM_V7_OPERANDS_MACCESS_H


#include <glib-object.h>
#include <stdbool.h>


#include <arch/operand.h>


#include "../pseudo.h"



/* Etats particuliers d'un opérande de valeur immédiate */
typedef enum _A7MAccessOpFlag
{
    A7MAOF_POST_INDEXED = AOF_USER_FLAG(0), /* Position du décalage        */
    A7MAOF_WRITE_BACK   = AOF_USER_FLAG(1), /* Mise à jour de la base      */

} A7MAccessOpFlag;


#define G_TYPE_ARMV7_MACCESS_OPERAND            g_armv7_maccess_operand_get_type()
#define G_ARMV7_MACCESS_OPERAND(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_ARMV7_MACCESS_OPERAND, GArmV7MAccessOperand))
#define G_IS_ARMV7_MACCESS_OPERAND(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_ARMV7_MACCESS_OPERAND))
#define G_ARMV7_MACCESS_OPERAND_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ARMV7_MACCESS_OPERAND, GArmV7MAccessOperandClass))
#define G_IS_ARMV7_MACCESS_OPERAND_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ARMV7_MACCESS_OPERAND))
#define G_ARMV7_MACCESS_OPERAND_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ARMV7_MACCESS_OPERAND, GArmV7MAccessOperandClass))


/* Définition d'un opérande offrant un accès à la mémoire depuis une base (instance) */
typedef struct _GArmV7MAccessOperand GArmV7MAccessOperand;

/* Définition d'un opérande offrant un accès à la mémoire depuis une base (classe) */
typedef struct _GArmV7MAccessOperandClass GArmV7MAccessOperandClass;


/* Indique le type défini par la GLib pour un accès à la mémoire depuis une base. */
GType g_armv7_maccess_operand_get_type(void);

/* Crée un accès à la mémoire depuis une base et un décalage. */
GArchOperand *g_armv7_maccess_operand_new(GArchOperand *, GArchOperand *, GArchOperand *, bool, bool);

/* Founit la base d'un accès à la mémoire. */
GArchOperand *g_armv7_maccess_operand_get_base(const GArmV7MAccessOperand *);

/* Founit le décalage d'un accès à la mémoire depuis la base. */
GArchOperand *g_armv7_maccess_operand_get_offset(const GArmV7MAccessOperand *);

/* Founit le décalage d'un décalage pour un accès mémoire. */
GArchOperand *g_armv7_maccess_operand_get_shift(const GArmV7MAccessOperand *);

/* Indique si le décalage est post-indexé. */
bool g_armv7_maccess_operand_is_post_indexed(const GArmV7MAccessOperand *);

/* Indique si la base est mise à jour après usage. */
bool g_armv7_maccess_operand_has_to_write_back(const GArmV7MAccessOperand *);



#endif  /* _PLUGINS_ARM_V7_OPERANDS_MACCESS_H */
