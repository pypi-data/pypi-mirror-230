
/* Chrysalide - Outil d'analyse de fichiers binaires
 * pool.h - prototypes pour les opérandes pointant vers la table des constantes
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


#ifndef _PLUGINS_DALVIK_OPERANDS_POOL_H
#define _PLUGINS_DALVIK_OPERANDS_POOL_H


#include <glib-object.h>
#include <stdint.h>


#include <arch/operand.h>
#include <common/endianness.h>
#include <plugins/dex/pool.h>



#define G_TYPE_DALVIK_POOL_OPERAND            g_dalvik_pool_operand_get_type()
#define G_DALVIK_POOL_OPERAND(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_DALVIK_POOL_OPERAND, GDalvikPoolOperand))
#define G_IS_DALVIK_POOL_OPERAND(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_DALVIK_POOL_OPERAND))
#define G_DALVIK_POOL_OPERAND_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DALVIK_POOL_OPERAND, GDalvikPoolOperandClass))
#define G_IS_DALVIK_POOL_OPERAND_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DALVIK_POOL_OPERAND))
#define G_DALVIK_POOL_OPERAND_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DALVIK_POOL_OPERAND, GDalvikPoolOperandClass))


/* Définition d'un opérande visant un élément de table de constantes Dalvik (instance) */
typedef struct _GDalvikPoolOperand GDalvikPoolOperand;

/* Définition d'un opérande visant un élément de table de constantes Dalvik (classe) */
typedef struct _GDalvikPoolOperandClass GDalvikPoolOperandClass;


/* Type de table de constantes */
typedef enum _DalvikPoolType
{
    DPT_NONE        = 0x0,
    DPT_STRING      = 0x1,
    DPT_TYPE        = 0x2,
    DPT_PROTO       = 0x3,
    DPT_FIELD       = 0x4,
    DPT_METHOD      = 0x5

} DalvikPoolType;


/* Indique le type défini par la GLib pour un un élément de table de constantes Dalvik. */
GType g_dalvik_pool_operand_get_type(void);

/* Crée un opérande visant un élément constant Dalvik. */
GArchOperand *g_dalvik_pool_operand_new(GDexFormat *, DalvikPoolType, const GBinContent *, vmpa2t *, MemoryDataSize, SourceEndian);

/* Indique la nature de la table de constantes visée ici. */
DalvikPoolType g_dalvik_pool_operand_get_pool_type(const GDalvikPoolOperand *);

/* Indique l'indice de l'élément dans la table de constantes. */
uint32_t g_dalvik_pool_operand_get_index(const GDalvikPoolOperand *);



#endif  /* _PLUGINS_DALVIK_OPERANDS_POOL_H */
