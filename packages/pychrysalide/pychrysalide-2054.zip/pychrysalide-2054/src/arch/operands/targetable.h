
/* Chrysalide - Outil d'analyse de fichiers binaires
 * targetable.h - prototypes pour les opérandes ciblant une portion de désassemblage
 *
 * Copyright (C) 2020 Cyrille Bagard
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


#ifndef _ARCH_OPERANDS_TARGETABLE_H
#define _ARCH_OPERANDS_TARGETABLE_H


#include <glib-object.h>
#include <stdbool.h>


#include "../vmpa.h"
#include "../processor.h"
#include "../../format/format.h"



#define G_TYPE_TARGETABLE_OPERAND             (g_targetable_operand_get_type())
#define G_TARGETABLE_OPERAND(obj)             (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_TARGETABLE_OPERAND, GTargetableOperand))
#define G_TARGETABLE_OPERAND_CLASS(vtable)    (G_TYPE_CHECK_CLASS_CAST((vtable), G_TYPE_TARGETABLE_OPERAND, GTargetableOperandIface))
#define G_IS_TARGETABLE_OPERAND(obj)          (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_TARGETABLE_OPERAND))
#define G_IS_TARGETABLE_OPERAND_CLASS(vtable) (G_TYPE_CHECK_CLASS_TYPE((vtable), G_TYPE_TARGETABLE_OPERAND))
#define G_TARGETABLE_OPERAND_GET_IFACE(inst)  (G_TYPE_INSTANCE_GET_INTERFACE((inst), G_TYPE_TARGETABLE_OPERAND, GTargetableOperandIface))


/* Opérande ciblant une portion de désassemblage (coquille vide) */
typedef struct _GTargetableOperand GTargetableOperand;

/* Opérande ciblant une portion de désassemblage (interface) */
typedef struct _GTargetableOperandIface GTargetableOperandIface;


/* Détermine le type d'une interface pour le ciblage d'une portion de désassemblage. */
GType g_targetable_operand_get_type(void) G_GNUC_CONST;

/* Obtient l'adresse de la cible visée par un opérande. */
bool g_targetable_operand_get_addr(const GTargetableOperand *, const vmpa2t *, GBinFormat *, GArchProcessor *, vmpa2t *);



#endif  /* _ARCH_OPERANDS_TARGETABLE_H */
