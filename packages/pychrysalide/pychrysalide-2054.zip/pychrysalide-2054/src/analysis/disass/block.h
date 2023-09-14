
/* Chrysalide - Outil d'analyse de fichiers binaires
 * block.h - prototypes pour l'encadrement des instructions par blocs
 *
 * Copyright (C) 2016-2019 Cyrille Bagard
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


#ifndef _ANALYSIS_DISASS_BLOCK_H
#define _ANALYSIS_DISASS_BLOCK_H


#include <glib-object.h>


#include "../binary.h"
#include "../block.h"
#include "../../arch/instruction.h"
#include "../../common/bits.h"



/* ------------------------ MISE EN PLACE DES BLOCS BASIQUES ------------------------ */


#define G_TYPE_BASIC_BLOCK              g_basic_block_get_type()
#define G_BASIC_BLOCK(obj)              (G_TYPE_CHECK_INSTANCE_CAST((obj), g_basic_block_get_type(), GBasicBlock))
#define G_IS_BASIC_BLOCK(obj)           (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_basic_block_get_type()))
#define G_BASIC_BLOCK_CLASS(klass)      (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_BASIC_BLOCK, GBasicBlockClass))
#define G_IS_BASIC_BLOCK_CLASS(klass)   (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_BASIC_BLOCK))
#define G_BASIC_BLOCK_GET_CLASS(obj)    (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_BASIC_BLOCK, GBasicBlockClass))


/* Description d'un bloc basique d'instructions (instance) */
typedef struct _GBasicBlock GBasicBlock;

/* Description d'un bloc basique d'instructions (classe) */
typedef struct _GBasicBlockClass GBasicBlockClass;


/* Indique le type défini pour un bloc d'instructions basique. */
GType g_basic_block_get_type(void);

/* Crée un bloc basique d'exécution d'instructions. */
GCodeBlock *g_basic_block_new(GLoadedBinary *, GArchInstruction *, GArchInstruction *, const bitfield_t *);

/* Fournit les instructions limites d'un bloc basique. */
void g_basic_block_get_boundaries(const GBasicBlock *, GArchInstruction **, GArchInstruction **);

/* Fournit un itérateur d'instructions limité au bloc basique. */
instr_iter_t *g_basic_block_get_iterator(const GBasicBlock *, GArchProcessor *);



#endif  /* _ANALYSIS_DISASS_BLOCK_H */
