
/* Chrysalide - Outil d'analyse de fichiers binaires
 * register.h - prototypes pour les opérandes visant un registre Dalvik
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


#ifndef _PLUGINS_DALVIK_OPERANDS_REGISTER_H
#define _PLUGINS_DALVIK_OPERANDS_REGISTER_H


#include <glib-object.h>
#include <stdbool.h>


#include <analysis/content.h>
#include <arch/operand.h>


#include "../register.h"



#define G_TYPE_DALVIK_REGISTER_OPERAND            g_dalvik_register_operand_get_type()
#define G_DALVIK_REGISTER_OPERAND(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_DALVIK_REGISTER_OPERAND, GDalvikRegisterOperand))
#define G_IS_DALVIK_REGISTER_OPERAND(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_DALVIK_REGISTER_OPERAND))
#define G_DALVIK_REGISTER_OPERAND_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DALVIK_REGISTER_OPERAND, GDalvikRegisterOperandClass))
#define G_IS_DALVIK_REGISTER_OPERAND_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DALVIK_REGISTER_OPERAND))
#define G_DALVIK_REGISTER_OPERAND_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DALVIK_REGISTER_OPERAND, GDalvikRegisterOperandClass))


/* Définition d'un opérande visant un registre Dalvik (instance) */
typedef struct _GDalvikRegisterOperand GDalvikRegisterOperand;

/* Définition d'un opérande visant un registre Dalvik (classe) */
typedef struct _GDalvikRegisterOperandClass GDalvikRegisterOperandClass;


/* Indique le type défini par la GLib pour un opérande de registre Dalvik. */
GType g_dalvik_register_operand_get_type(void);

/* Crée un opérande visant un registre Dalvik. */
GArchOperand *g_dalvik_register_operand_new(const GBinContent *, vmpa2t *, bool *, MemoryDataSize, SourceEndian);

/* Crée un opérande visant un registre Dalvik. */
GArchOperand *g_dalvik_register_operand_new_from_existing(GArchRegister *);

/* Fournit le registre Dalvik associé à l'opérande. */
const GDalvikRegister *g_dalvik_register_operand_get(const GDalvikRegisterOperand *);



#endif  /* _PLUGINS_DALVIK_OPERANDS_REGISTER_H */
