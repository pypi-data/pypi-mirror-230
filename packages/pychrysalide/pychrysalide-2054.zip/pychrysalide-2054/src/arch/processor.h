
/* Chrysalide - Outil d'analyse de fichiers binaires
 * processor.h - prototypes pour la gestion générique des architectures
 *
 * Copyright (C) 2008-2019 Cyrille Bagard
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


#ifndef _ARCH_PROCESSOR_H
#define _ARCH_PROCESSOR_H


#include <glib-object.h>


#include "context.h"
#include "instriter.h"
#include "instruction.h"
#include "../common/endianness.h"
#include "../format/executable.h"



#define G_TYPE_ARCH_PROCESSOR            g_arch_processor_get_type()
#define G_ARCH_PROCESSOR(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_ARCH_PROCESSOR, GArchProcessor))
#define G_IS_ARCH_PROCESSOR(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_ARCH_PROCESSOR))
#define G_ARCH_PROCESSOR_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ARCH_PROCESSOR, GArchProcessorClass))
#define G_IS_ARCH_PROCESSOR_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ARCH_PROCESSOR))
#define G_ARCH_PROCESSOR_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ARCH_PROCESSOR, GArchProcessorClass))



/* Définition générique d'un processeur d'architecture (instance) */
typedef struct _GArchProcessor GArchProcessor;

/* Définition générique d'un processeur d'architecture (classe) */
typedef struct _GArchProcessorClass GArchProcessorClass;


/* Indique le type défini pour un processeur d'architecture. */
GType g_arch_processor_get_type(void);

/* Fournit la désignation interne du processeur d'architecture. */
char *g_arch_processor_get_key(const GArchProcessor *);

/* Fournit le nom humain de l'architecture visée. */
char *g_arch_processor_get_desc(const GArchProcessor *);

/* Fournit le boustime du processeur d'une architecture. */
SourceEndian g_arch_processor_get_endianness(const GArchProcessor *);

/* Fournit la taille de l'espace mémoire d'une architecture. */
MemoryDataSize g_arch_processor_get_memory_size(const GArchProcessor *);

/* Fournit la taille min. des instructions d'une architecture. */
MemoryDataSize g_arch_processor_get_instruction_min_size(const GArchProcessor *);

/* Indique si l'architecture possède un espace virtuel ou non. */
bool g_arch_processor_has_virtual_space(const GArchProcessor *);

/* Fournit un contexte propre au processeur d'une architecture. */
GProcContext *g_arch_processor_get_context(const GArchProcessor *);

/* Désassemble une instruction dans un flux de données. */
GArchInstruction *g_arch_processor_disassemble(const GArchProcessor *, GProcContext *, const GBinContent *, vmpa2t *, GExeFormat *);



/* ------------------ RASSEMBLEMENT DES INSTRUCTIONS DESASSEMBLEES ------------------ */


/* Protège ou lève la protection de l'accès aux instructions. */
void g_arch_processor_lock_unlock(GArchProcessor *, bool);

#define g_arch_processor_lock(p) g_arch_processor_lock_unlock(p, true)
#define g_arch_processor_unlock(p) g_arch_processor_lock_unlock(p, false)

/* Fournit la marque de dernière modification des instructions. */
unsigned int g_arch_processor_get_stamp(const GArchProcessor *);

/* Compte le nombre d'instructions représentées. */
size_t g_arch_processor_count_instructions(const GArchProcessor *);

/* Note les instructions désassemblées avec une architecture. */
void g_arch_processor_set_instructions(GArchProcessor *, GArchInstruction **, size_t);

/* Ajoute une instruction désassemblée à la liste. */
void g_arch_processor_add_instruction(GArchProcessor *, GArchInstruction *);

/* Retire une instruction désassemblée de la liste. */
void g_arch_processor_remove_instruction(GArchProcessor *proc, GArchInstruction *);

/* Fournit une instruction désassemblée pour une architecture. */
GArchInstruction *g_arch_processor_get_instruction(const GArchProcessor *, size_t);



/* ------------------ CONSERVATION DES SOUCIS DURANT LE CHARGEMENT ------------------ */


/* Types d'erreurs détectées */

#define PROC_ERROR(idx) ((idx << 2) | (1 << 0))

typedef enum _ArchProcessingError
{
    APE_DISASSEMBLY = PROC_ERROR(0),        /* Code non reconnu            */
    APE_LABEL       = PROC_ERROR(1)         /* Etiquette non référencée    */

} ArchProcessingError;


/* Protège ou lève la protection de l'accès aux erreurs. */
void g_arch_processor_lock_unlock_errors(GArchProcessor *, bool);

#define g_arch_processor_lock_errors(p) g_arch_processor_lock_unlock_errors(p, true)
#define g_arch_processor_unlock_errors(p) g_arch_processor_lock_unlock_errors(p, false)

/* Etend la liste des soucis détectés avec de nouvelles infos. */
void g_arch_processor_add_error(GArchProcessor *, ArchProcessingError, const vmpa2t *, const char *);

/* Indique le nombre d'erreurs relevées au niveau assembleur. */
size_t g_arch_processor_count_errors(GArchProcessor *);

/* Fournit les éléments concernant un soucis détecté. */
bool g_arch_processor_get_error(GArchProcessor *, size_t, ArchProcessingError *, vmpa2t *, char **);



/* ------------------ MANIPULATIONS DES INSTRUCTIONS DESASSEMBLEES ------------------ */


/* Couverture d'un groupe d'instructions */
typedef struct _instr_coverage  instr_coverage;


/* Recherche un groupe d'instruction d'après son adresse. */
const instr_coverage *g_arch_processor_find_coverage_by_address(const GArchProcessor *, const vmpa2t *);

/* Recherche une instruction d'après son adresse. */
GArchInstruction *_g_arch_processor_find_instr_by_address(GArchProcessor *, const vmpa2t *, bool);

/* Recherche rapidement une instruction d'après son adresse. */
GArchInstruction *_g_arch_processor_find_covered_instr_by_address(const GArchProcessor *, const instr_coverage *, const vmpa2t *, bool);

#define g_arch_processor_find_instr_by_address(proc, addr)                                          \
    _g_arch_processor_find_instr_by_address(proc, addr, false)

#define g_arch_processor_find_covered_instr_by_address(proc, coverage, addr)                        \
    ({                                                                                              \
        GArchInstruction *__result;                                                                 \
        g_arch_processor_lock(proc);                                                                \
        __result = _g_arch_processor_find_covered_instr_by_address(proc, coverage, addr, false);    \
        g_arch_processor_unlock(proc);                                                              \
        __result;                                                                                   \
    })

/* Met en place un itérateur d'instruction selon une adresse. */
instr_iter_t *_g_arch_processor_get_iter_from_address(GArchProcessor *, const vmpa2t *, bool);

/* Met en place un itérateur d'instruction selon une adresse. */
instr_iter_t *_g_arch_processor_get_covered_iter_from_address(GArchProcessor *, const instr_coverage *, const vmpa2t *, bool);

#define g_arch_processor_get_iter_from_address(proc, addr) \
    _g_arch_processor_get_iter_from_address(proc, addr, false)

#define g_arch_processor_get_covered_iter_from_address(proc, coverage, addr)                        \
    ({                                                                                              \
        instr_iter_t *__result;                                                                     \
        g_arch_processor_lock(proc);                                                                \
        __result = _g_arch_processor_get_covered_iter_from_address(proc, coverage, addr, false);    \
        g_arch_processor_unlock(proc);                                                              \
        __result;                                                                                   \
    })



#endif  /* _ARCH_PROCESSOR_H */
