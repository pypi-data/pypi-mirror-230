
/* Chrysalide - Outil d'analyse de fichiers binaires
 * proxy.h - prototypes pour les opérandes renvoyant vers des éléments non architecturaux
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


#ifndef _ARCH_OPERANDS_PROXY_H
#define _ARCH_OPERANDS_PROXY_H


#include <glib-object.h>


#include "feeder.h"
#include "../operand.h"



/* ------------------ OPERANDES CONSTITUANT DE PURS INTERMEDIAIRES ------------------ */


#define G_TYPE_PROXY_OPERAND            g_proxy_operand_get_type()
#define G_PROXY_OPERAND(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_PROXY_OPERAND, GProxyOperand))
#define G_IS_PROXY_OPERAND(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_PROXY_OPERAND))
#define G_PROXY_OPERAND_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_PROXY_OPERAND, GProxyOperandClass))
#define G_IS_PROXY_OPERAND_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_PROXY_OPERAND))
#define G_PROXY_OPERAND_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_PROXY_OPERAND, GProxyOperandClass))


/* Définition d'un opérande renvoyant vers un élément (instance) */
typedef struct _GProxyOperand GProxyOperand;

/* Définition d'un opérande renvoyant vers un élément (classe) */
typedef struct _GProxyOperandClass GProxyOperandClass;


/* Indique le type défini pour un opérande d'architecture. */
GType g_proxy_operand_get_type(void);

/* Crée un opérande renvoyant vers un élément non architectural. */
GArchOperand *g_proxy_operand_new(GProxyFeeder *);

/* Fournit le fournisseur représenté par l'opérande. */
GProxyFeeder *g_proxy_operand_get_feeder(const GProxyOperand *);



#endif  /* _ARCH_OPERANDS_PROXY_H */
