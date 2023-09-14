
/* Chrysalide - Outil d'analyse de fichiers binaires
 * raw.h - prototypes pour les instructions pures vues de l'esprit
 *
 * Copyright (C) 2014-2020 Cyrille Bagard
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


#ifndef _ARCH_INSTRUCTIONS_RAW_H
#define _ARCH_INSTRUCTIONS_RAW_H


#include <glib-object.h>


#include "../instruction.h"
#include "../vmpa.h"



/* ------------------------- INSTRUCTION INCONNUE / DONNEES ------------------------- */


#define G_TYPE_RAW_INSTRUCTION            g_raw_instruction_get_type()
#define G_RAW_INSTRUCTION(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_RAW_INSTRUCTION, GRawInstruction))
#define G_IS_RAW_INSTRUCTION(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_RAW_INSTRUCTION))
#define G_RAW_INSTRUCTION_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_RAW_INSTRUCTION, GRawInstructionClass))
#define G_IS_RAW_INSTRUCTION_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_RAW_INSTRUCTION))
#define G_RAW_INSTRUCTION_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_RAW_INSTRUCTION, GRawInstructionClass))


/* Définition générique d'une instruction brute d'architecture (instance) */
typedef struct _GRawInstruction GRawInstruction;

/* Définition générique d'une instruction brute d'architecture (classe) */
typedef struct _GRawInstructionClass GRawInstructionClass;


/* Indique le type défini pour une instruction inconnue d'architecture. */
GType g_raw_instruction_get_type(void);

/* Crée une instruction de type 'db/dw/etc' simple. */
GArchInstruction *g_raw_instruction_new_from_value(const vmpa2t *, MemoryDataSize, uint64_t);

/* Crée une instruction de type 'db/dw/etc' pour un uleb128. */
GArchInstruction *g_raw_instruction_new_uleb128(const GBinContent *content, vmpa2t *);

/* Crée une instruction de type 'db/dw/etc' pour un sleb128. */
GArchInstruction *g_raw_instruction_new_sleb128(const GBinContent *content, vmpa2t *);

/* Crée une instruction de type 'db/dw/etc' étendue. */
GArchInstruction *g_raw_instruction_new_array(const GBinContent *, MemoryDataSize, size_t, vmpa2t *, SourceEndian);

/* Drapeaux pour informations complémentaires */
typedef enum _RawInstrFlag
{
    RIF_PADDING = (1 << (AIF_USER_BIT + 0)),/* Données de bourrage         */
    RIF_STRING  = (1 << (AIF_USER_BIT + 1)),/* Impression en chaîne        */

} RawInstrFlag;

/* Marque l'instruction comme ne contenant que du bourrage. */
void g_raw_instruction_mark_as_padding(GRawInstruction *, bool);

/* Indique si le contenu de l'instruction est du bourrage. */
bool g_raw_instruction_is_padding(const GRawInstruction *);

/* Marque l'instruction comme contenant une chaîne de texte. */
void g_raw_instruction_mark_as_string(GRawInstruction *, bool);

/* Indique si le contenu de l'instruction est un texte. */
bool g_raw_instruction_is_string(const GRawInstruction *);



#endif  /* _ARCH_INSTRUCTIONS_RAW_H */
