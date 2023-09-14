
/* Chrysalide - Outil d'analyse de fichiers binaires
 * storage.h - prototypes pour la conservation hors mémoire vive des instructions désassemblées
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _ARCH_STORAGE_H
#define _ARCH_STORAGE_H


#include <glib-object.h>


#include <stdbool.h>


#include "processor.h"



/* ------------------- MECANISME DE SAUVEGARDE ET DE RESTAURATION ------------------- */


/* Définition générique d'une instruction d'architecture (instance) */
typedef struct _GArchInstruction GArchInstruction;


#define G_TYPE_ASM_STORAGE            g_asm_storage_get_type()
#define G_ASM_STORAGE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_ASM_STORAGE, GAsmStorage))
#define G_IS_ASM_STORAGE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_ASM_STORAGE))
#define G_ASM_STORAGE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ASM_STORAGE, GAsmStorageClass))
#define G_IS_ASM_STORAGE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ASM_STORAGE))
#define G_ASM_STORAGE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ASM_STORAGE, GAsmStorageClass))


/* Définition d'une conservation d'instructions d'assemblage (instance) */
typedef struct _GAsmStorage GAsmStorage;

/* Définition d'une conservation d'instructions d'assemblage (classe) */
typedef struct _GAsmStorageClass GAsmStorageClass;


/* Indique le type défini pour une conservation d'instructions d'assemblage. */
GType g_asm_storage_get_type(void);

/* Crée le support d'une conservation d'instructions. */
GAsmStorage *g_asm_storage_new_compressed(GArchProcessor *, const gchar *);

/* Détermine si un cache d'instructions complet existe. */
bool g_asm_storage_has_cache(const GAsmStorage *);

/* Crée une nouvelle instance d'objet à partir de son type. */
GObject *g_asm_storage_create_object(GAsmStorage *, packed_buffer_t *);

/* Sauvegarde le type d'un objet instancié. */
bool g_asm_storage_store_object_gtype(GAsmStorage *, GObject *, packed_buffer_t *);

/* Type de fichier intermédiaire */
typedef enum _StorageFileType
{
    SFT_INSTRUCTION,                        /* Pour instructions           */
    SFT_OPERAND,                            /* Pour opérandes              */
    SFT_REGISTER                            /* Pour registres              */

} StorageFileType;

/* Charge des données rassemblées. */
bool _g_asm_storage_load_data(const GAsmStorage *, StorageFileType, packed_buffer_t *, off64_t);

#define g_asm_storage_load_instruction_data(s, b, p) \
    _g_asm_storage_load_data(s, SFT_INSTRUCTION, b, p)

#define g_asm_storage_load_operand_data(s, b, p) \
    _g_asm_storage_load_data(s, SFT_OPERAND, b, p)

#define g_asm_storage_load_register_data(s, b, p) \
    _g_asm_storage_load_data(s, SFT_REGISTER, b, p)

/* Sauvegarde des données rassemblées. */
bool _g_asm_storage_store_data(const GAsmStorage *, StorageFileType, packed_buffer_t *, off64_t *);

#define g_asm_storage_store_instruction_data(s, b, p) \
    _g_asm_storage_store_data(s, SFT_INSTRUCTION, b, p)

#define g_asm_storage_store_operand_data(s, b, p) \
    _g_asm_storage_store_data(s, SFT_OPERAND, b, p)

#define g_asm_storage_store_register_data(s, b, p) \
    _g_asm_storage_store_data(s, SFT_REGISTER, b, p)

/* Lance une restauration complète d'unsauvegarde compressée. */
bool g_asm_storage_open(GAsmStorage *, GBinFormat *, wgroup_id_t);

/* Fournit l'instruction correspondant à une position indicée. */
GArchInstruction *g_asm_storage_get_instruction_at(GAsmStorage *, GBinFormat *, off64_t, packed_buffer_t *);

/* Programme une sauvegarde complète et compressée. */
void g_asm_storage_save(GAsmStorage *);



#endif  /* _ARCH_STORAGE_H */
