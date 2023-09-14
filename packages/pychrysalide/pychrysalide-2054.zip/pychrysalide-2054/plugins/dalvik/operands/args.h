
/* Chrysalide - Outil d'analyse de fichiers binaires
 * args.h - prototypes pour les listes d'opérandes rassemblées en arguments
 *
 * Copyright (C) 2010-2012x Cyrille Bagard
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


#ifndef _PLUGINS_DALVIK_OPERANDS_ARGS_H
#define _PLUGINS_DALVIK_OPERANDS_ARGS_H


#include <glib-object.h>


#include <arch/operand.h>



#define G_TYPE_DALVIK_ARGS_OPERAND            g_dalvik_args_operand_get_type()
#define G_DALVIK_ARGS_OPERAND(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_DALVIK_ARGS_OPERAND, GDalvikArgsOperand))
#define G_IS_DALVIK_ARGS_OPERAND(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_DALVIK_ARGS_OPERAND))
#define G_DALVIK_ARGS_OPERAND_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DALVIK_ARGS_OPERAND, GDalvikArgsOperandClass))
#define G_IS_DALVIK_ARGS_OPERAND_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DALVIK_ARGS_OPERAND))
#define G_DALVIK_ARGS_OPERAND_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DALVIK_ARGS_OPERAND, GDalvikArgsOperandClass))


/* Définition d'un opérande visant une liste d'opérandes Dalvik (instance) */
typedef struct _GDalvikArgsOperand GDalvikArgsOperand;

/* Définition d'un opérande visant une liste d'opérandes Dalvik (classe) */
typedef struct _GDalvikArgsOperandClass GDalvikArgsOperandClass;


/* Indique le type défini par la GLib pour une liste d'arguments Dalvik. */
GType g_dalvik_args_operand_get_type(void);

/* Crée un réceptacle pour opérandes Dalvik servant d'arguments. */
GArchOperand *g_dalvik_args_operand_new(void);

/* Ajoute un élément à la liste d'arguments Dalvik. */
void g_dalvik_args_operand_add(GDalvikArgsOperand *, GArchOperand *);

/* Fournit le nombre d'arguments pris en charge. */
size_t g_dalvik_args_count(const GDalvikArgsOperand *);

/* Founit un élément de la liste d'arguments Dalvik. */
GArchOperand *g_dalvik_args_operand_get(const GDalvikArgsOperand *, size_t);



#endif  /* _PLUGINS_DALVIK_OPERANDS_ARGS_H */
