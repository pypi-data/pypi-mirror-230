
/* Chrysalide - Outil d'analyse de fichiers binaires
 * instriter.h - prototypes pour le parcours simplifié d'un ensemble d'instructions
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


#ifndef _ARCH_INSTRITER_H
#define _ARCH_INSTRITER_H


#include "instruction.h"



/* Depuis "processeur.h" : définition générique d'un processeur d'architecture (instance) */
typedef struct _GArchProcessor GArchProcessor;

/* Suivi d'un parcours d'instructions */
typedef struct _instr_iter_t instr_iter_t;


/* Construit un itérateur pour parcourir des instructions. */
instr_iter_t *create_instruction_iterator(GArchProcessor *, size_t);

/* Duplique un itérateur de parcours d'instructions existant. */
instr_iter_t *copy_instruction_iterator(const instr_iter_t *);

/* Détruit un itérateur mis en place. */
void delete_instruction_iterator(instr_iter_t *);

/* Limite le parcours des instructions à une zone donnée. */
void restrict_instruction_iterator(instr_iter_t *, const mrange_t *);

/* Fournit l'instruction courante de l'itérateur. */
GArchInstruction *get_instruction_iterator_current(instr_iter_t *);

/* Fournit l'instruction qui en précède une autre. */
GArchInstruction *get_instruction_iterator_prev(instr_iter_t *);

/* Fournit l'instruction qui en suit une autre. */
GArchInstruction *get_instruction_iterator_next(instr_iter_t *);

/* Détermine s'il reste une instruction dans l'itération. */
bool has_instruction_iterator_next(const instr_iter_t *);



#endif  /* _ARCH_INSTRITER_H */
