
/* Chrysalide - Outil d'analyse de fichiers binaires
 * register.h - prototypes pour les aides auxiliaires relatives aux registres Dalvik
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


#ifndef _ARCH_OPERANDS_REGISTER_H
#define _ARCH_OPERANDS_REGISTER_H


#include <glib-object.h>
#include <stdbool.h>


#include "../operand.h"
#include "../register.h"



/* ------------------------- REGISTRE SOUS FORME D'OPERANDE ------------------------- */


/* Etats particuliers d'un opérande de registre */
typedef enum _RegOpFlag
{
    ROF_IS_WRITTEN = AOF_USER_FLAG(0),      /* Opération d'écriture ?      */

} RegOpFlag;


#define G_TYPE_REGISTER_OPERAND            g_register_operand_get_type()
#define G_REGISTER_OPERAND(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_REGISTER_OPERAND, GRegisterOperand))
#define G_IS_REGISTER_OPERAND(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_REGISTER_OPERAND))
#define G_REGISTER_OPERAND_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_REGISTER_OPERAND, GRegisterOperandClass))
#define G_IS_REGISTER_OPERAND_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_REGISTER_OPERAND))
#define G_REGISTER_OPERAND_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_REGISTER_OPERAND, GRegisterOperandClass))


/* Définition d'un opérande visant un registre (instance) */
typedef struct _GRegisterOperand GRegisterOperand;

/* Définition d'un opérande visant un registre (classe) */
typedef struct _GRegisterOperandClass GRegisterOperandClass;


/* Indique le type défini par la GLib pour un opérande de registre. */
GType g_register_operand_get_type(void);

/* Fournit le registre associé à l'opérande. */
GArchRegister *g_register_operand_get_register(const GRegisterOperand *);



#endif  /* _ARCH_OPERANDS_REGISTER_H */
