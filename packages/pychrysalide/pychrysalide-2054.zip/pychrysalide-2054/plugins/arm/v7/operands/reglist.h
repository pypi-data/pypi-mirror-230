
/* Chrysalide - Outil d'analyse de fichiers binaires
 * reglist.h - prototypes pour les accès à la mémorie à partir d'un registre et d'un décalage
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


#ifndef _PLUGINS_ARM_V7_OPERANDS_REGLIST_H
#define _PLUGINS_ARM_V7_OPERANDS_REGLIST_H


#include <glib-object.h>
#include <stdbool.h>


#include <arch/operand.h>


#include "../register.h"



#define G_TYPE_ARMV7_REGLIST_OPERAND            g_armv7_reglist_operand_get_type()
#define G_ARMV7_REGLIST_OPERAND(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_ARMV7_REGLIST_OPERAND, GArmV7RegListOperand))
#define G_IS_ARMV7_REGLIST_OPERAND(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_ARMV7_REGLIST_OPERAND))
#define G_ARMV7_REGLIST_OPERAND_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ARMV7_REGLIST_OPERAND, GArmV7RegListOperandClass))
#define G_IS_ARMV7_REGLIST_OPERAND_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ARMV7_REGLIST_OPERAND))
#define G_ARMV7_REGLIST_OPERAND_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ARMV7_REGLIST_OPERAND, GArmV7RegListOperandClass))


/* Définition d'un opérande listant une série de registres ARM (instance) */
typedef struct _GArmV7RegListOperand GArmV7RegListOperand;

/* Définition d'un opérande listant une série de registres ARM (classe) */
typedef struct _GArmV7RegListOperandClass GArmV7RegListOperandClass;


/* Indique le type défini par la GLib pour une liste de registres ARM. */
GType g_armv7_reglist_operand_get_type(void);

/* Crée une liste vierge de registres ARM. */
GArchOperand *g_armv7_reglist_operand_new(uint16_t);

/* Ajoute un registre à une liste de registres ARM. */
void g_armv7_reglist_add_register(GArmV7RegListOperand *, GArmV7Register *);

/* Compte le nombre de registres ARM composant la liste. */
size_t g_armv7_reglist_count_registers(const GArmV7RegListOperand *);

/* Founit un élément donné d'une liste de registres ARM. */
GArmV7Register *g_armv7_reglist_operand_get_register(const GArmV7RegListOperand *, size_t );

/* Indique si un registre est présent dans une liste. */
bool g_armv7_reglist_operand_has_register(const GArmV7RegListOperand *, const GArmV7Register *);



#endif  /* _PLUGINS_ARM_V7_OPERANDS_REGLIST_H */
