
/* Chrysalide - Outil d'analyse de fichiers binaires
 * rename.h - prototypes pour les opérandes pouvant être renommées
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


#ifndef _ARCH_OPERANDS_RENAME_H
#define _ARCH_OPERANDS_RENAME_H


#include <glib-object.h>



/* ------------------------ INTERFACE POUR OPERANDE RENOMMEE ------------------------ */


#define G_TYPE_RENAMED_OPERAND             (g_renamed_operand_get_type())
#define G_RENAMED_OPERAND(obj)             (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_RENAMED_OPERAND, GRenamedOperand))
#define G_RENAMED_OPERAND_CLASS(vtable)    (G_TYPE_CHECK_CLASS_CAST((vtable), G_TYPE_RENAMED_OPERAND, GRenamedOperandIface))
#define G_IS_RENAMED_OPERAND(obj)          (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_RENAMED_OPERAND))
#define G_IS_RENAMED_OPERAND_CLASS(vtable) (G_TYPE_CHECK_CLASS_TYPE((vtable), G_TYPE_RENAMED_OPERAND))
#define G_RENAMED_OPERAND_GET_IFACE(inst)  (G_TYPE_INSTANCE_GET_INTERFACE((inst), G_TYPE_RENAMED_OPERAND, GRenamedOperandIface))


/* Opérande renommé avec un texte alternatif (coquille vide) */
typedef struct _GRenamedOperand GRenamedOperand;

/* Opérande renommé avec un texte alternatif (interface) */
typedef struct _GRenamedOperandIface GRenamedOperandIface;


/* Détermine le type d'une interface pour un opérande renommé. */
GType g_renamed_operand_get_type(void) G_GNUC_CONST;

/* Fournit un texte comme représentation alternative d'opérande. */
char *g_renamed_operand_get_text(const GRenamedOperand *);



/* ----------------------- INTERFACE POUR OPERANDE RENOMMABLE ----------------------- */


#define G_TYPE_RENAMEABLE_OPERAND             (g_renameable_operand_get_type())
#define G_RENAMEABLE_OPERAND(obj)             (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_RENAMEABLE_OPERAND, GRenameableOperand))
#define G_RENAMEABLE_OPERAND_CLASS(vtable)    (G_TYPE_CHECK_CLASS_CAST((vtable), G_TYPE_RENAMEABLE_OPERAND, GRenameableOperandIface))
#define G_IS_RENAMEABLE_OPERAND(obj)          (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_RENAMEABLE_OPERAND))
#define G_IS_RENAMEABLE_OPERAND_CLASS(vtable) (G_TYPE_CHECK_CLASS_TYPE((vtable), G_TYPE_RENAMEABLE_OPERAND))
#define G_RENAMEABLE_OPERAND_GET_IFACE(inst)  (G_TYPE_INSTANCE_GET_INTERFACE((inst), G_TYPE_RENAMEABLE_OPERAND, GRenameableOperandIface))


/* Opérande offrant une capacité de renommage (coquille vide) */
typedef struct _GRenameableOperand GRenameableOperand;

/* Opérande offrant une capacité de renommage (interface) */
typedef struct _GRenameableOperandIface GRenameableOperandIface;


/* Détermine le type d'une interface pour le renommage d'un opérande. */
GType g_renameable_operand_get_type(void) G_GNUC_CONST;

/* Construit un opérande de représentation alternative. */
GRenamedOperand *g_renameable_operand_build(const GRenameableOperand *, const char *);



#endif  /* _ARCH_OPERANDS_RENAME_H */
