
/* Chrysalide - Outil d'analyse de fichiers binaires
 * operand.h - prototypes pour la gestion des operandes de l'architecture JVM
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


#ifndef _ARCH_JVM_OPERAND_H
#define _ARCH_JVM_OPERAND_H


#include "../instruction.h"



/* Types d'opérandes supportés */
typedef enum _JvmOperandType JvmOperandType;



/* ---------------------- COQUILLE VIDE POUR LES OPERANDES JVM ---------------------- */


#define G_TYPE_JVM_OPERAND            g_jvm_operand_get_type()
#define G_JVM_OPERAND(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_JVM_OPERAND, GJvmOperand))
#define G_IS_JVM_OPERAND(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_JVM_OPERAND))
#define G_JVM_OPERAND_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_JVM_OPERAND, GJvmOperandClass))
#define G_IS_JVM_OPERAND_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_JVM_OPERAND))
#define G_JVM_OPERAND_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_JVM_OPERAND, GJvmOperandClass))


/* Définition d'un opérande de la JVM (instance) */
typedef struct _GJvmOperand GJvmOperand;

/* Définition d'un opérande de la JVM (classe) */
typedef struct _GJvmOperandClass GJvmOperandClass;


/* Indique le type défini par la GLib pour un opérande de JVM. */
GType g_jvm_operand_get_type(void);







/* --------------------- OPERANDES RENVOYANT VERS UNE REFERENCE --------------------- */


#define G_TYPE_JVM_REF_OPERAND                  g_jvm_ref_operand_get_type()
#define G_JVM_REF_OPERAND(obj)                  (G_TYPE_CHECK_INSTANCE_CAST((obj), g_jvm_ref_operand_get_type(), GJvmRefOperand))
#define G_IS_JVM_REF_OPERAND(obj)               (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_jvm_ref_operand_get_type()))
#define G_JVM_REF_OPERAND_GET_IFACE(inst)       (G_TYPE_INSTANCE_GET_INTERFACE((inst), g_jvm_ref_operand_get_type(), GJvmRefOperandIface))


/* Définition d'un opérande de référence de la JVM (instance) */
typedef struct _GJvmRefOperand GJvmRefOperand;

/* Définition d'un opérande de référence de la JVM (classe) */
typedef struct _GJvmRefOperandClass GJvmRefOperandClass;


/* Indique le type défini par la GLib pour un opérande de référence de JVM. */
GType g_jvm_ref_operand_get_type(void);

/* Crée un opérande de référence pour la JVM. */
GArchOperand *g_jvm_ref_operand_new(const bin_t *, off_t *, off_t, JvmOperandType);





/* ------------------------- AIDE A LA CREATION D'OPERANDES ------------------------- */


/* Types d'opérandes supportés */
enum _JvmOperandType
{
    JOT_FIELD_REF,                          /* Référence vers un champ     */
    JOT_METHOD_REF,                         /* Référence vers une méthode  */

    JOT_COUNT

};


/* Procède à la lecture d'un opérande donné. */
bool jvm_read_one_operand(GArchInstruction *, const bin_t *, off_t *, off_t, JvmOperandType, ...);



#endif  /* _ARCH_JVM_OPERAND_H */
