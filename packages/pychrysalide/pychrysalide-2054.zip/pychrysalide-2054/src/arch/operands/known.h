
/* Chrysalide - Outil d'analyse de fichiers binaires
 * known.h - prototypes pour les opérandes représentant des valeurs numériques avec sémantique
 *
 * Copyright (C) 2021 Cyrille Bagard
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


#ifndef _ARCH_OPERANDS_KNOWN_H
#define _ARCH_OPERANDS_KNOWN_H


#include <glib-object.h>


#include "immediate.h"
#include "../operand.h"



#define G_TYPE_KNOWN_IMM_OPERAND            g_known_imm_operand_get_type()
#define G_KNOWN_IMM_OPERAND(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_KNOWN_IMM_OPERAND, GKnownImmOperand))
#define G_IS_KNOWN_IMM_OPERAND(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_KNOWN_IMM_OPERAND))
#define G_KNOWN_IMM_OPERAND_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_KNOWN_IMM_OPERAND, GKnownImmOperandClass))
#define G_IS_KNOWN_IMM_OPERAND_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_KNOWN_IMM_OPERAND))
#define G_KNOWN_IMM_OPERAND_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_KNOWN_IMM_OPERAND, GKnownImmOperandClass))


/* Définition d'un remplacement d'opérande de valeur numérique (instance) */
typedef struct _GKnownImmOperand GKnownImmOperand;

/* Définition d'un remplacement d'opérande de valeur numérique (classe) */
typedef struct _GKnownImmOperandClass GKnownImmOperandClass;


/* Indique le type défini pour un remplacemet d'opérande de valeur numérique. */
GType g_known_imm_operand_get_type(void);

/* Crée un opérande remplaçant visuellement une valeur. */
GArchOperand *g_known_imm_operand_new(const GImmOperand *, const char *);



#endif  /* _ARCH_OPERANDS_KNOWN_H */
