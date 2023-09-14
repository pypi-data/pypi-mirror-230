
/* Chrysalide - Outil d'analyse de fichiers binaires
 * target.h - prototypes pour les opérandes ciblant un symbole
 *
 * Copyright (C) 2014-2018 Cyrille Bagard
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


#ifndef _ARCH_OPERANDS_TARGET_H
#define _ARCH_OPERANDS_TARGET_H


#include <glib-object.h>
#include <stdbool.h>


#include "../archbase.h"
#include "../operand.h"
#include "../vmpa.h"



/* Etats particuliers d'un opérande de valeur immédiate */
typedef enum _TargetOpFlag
{
    TOF_STRICT = AOF_USER_FLAG(0),          /* Résolution stricte          */

} TargetOpFlag;


#define G_TYPE_TARGET_OPERAND            g_target_operand_get_type()
#define G_TARGET_OPERAND(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_TARGET_OPERAND, GTargetOperand))
#define G_IS_TARGET_OPERAND(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_TARGET_OPERAND))
#define G_TARGET_OPERAND_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_TARGET_OPERAND, GTargetOperandClass))
#define G_IS_TARGET_OPERAND_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_TARGET_OPERAND))
#define G_TARGET_OPERAND_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_TARGET_OPERAND, GTargetOperandClass))


/* Définition d'un opérande ciblant idéalement un symbole connu (instance) */
typedef struct _GTargetOperand GTargetOperand;

/* Définition d'un opérande ciblant idéalement un symbole connu (classe) */
typedef struct _GTargetOperandClass GTargetOperandClass;


/* Indique le type défini pour un opérande d'architecture. */
GType g_target_operand_get_type(void);

/* Crée un opérande réprésentant une valeur numérique. */
GArchOperand *g_target_operand_new(MemoryDataSize, const vmpa2t *);

/* Renseigne la taille de la valeur indiquée à la construction. */
MemoryDataSize g_target_operand_get_size(const GTargetOperand *);

/* Tente une résolution de symbole. */
bool g_target_operand_resolve(GTargetOperand *, GBinFormat *, bool);

/* Fournit les indications concernant le symbole associé. */
GBinSymbol *g_target_operand_get_symbol(const GTargetOperand *, phys_t *);



#endif  /* _ARCH_OPERANDS_TARGET_H */
