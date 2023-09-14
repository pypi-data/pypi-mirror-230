
/* Chrysalide - Outil d'analyse de fichiers binaires
 * dragon.h - prototypes pour les capacités apportées par la lecture du livre du dragon
 *
 * Copyright (C) 2016-2018 Cyrille Bagard
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


#ifndef _ANALYSIS_DISASS_DRAGON_H
#define _ANALYSIS_DISASS_DRAGON_H


#include "../binary.h"
#include "../block.h"
#include "../../arch/processor.h"
#include "../../common/bits.h"



/* -------------------------- DECOUPAGES DE CODE EN NOEUDS -------------------------- */


/* Description de noeud, en référence à "Compilers: Principles, Techniques, and Tools" */
typedef struct _dragon_node dragon_node;


/* Fournit les instructions bornant un noeud de code. */
void get_dragon_node_bounding_instructions(dragon_node *, GArchInstruction **, GArchInstruction **);

/* Fournit un noeud particulier à partir d'une liste. */
dragon_node *get_dragon_node(dragon_node *, size_t);

/* Fournit l'indice d'un noeud particulier à partir d'une liste. */
size_t get_dragon_node_index(dragon_node *, dragon_node *);

/* Recherche un noeud selon son intruction de départ. */
dragon_node *find_node_for_instruction(dragon_node *, size_t, bool, const GArchInstruction *);

/* Marque tous les noeuds accessibles pour chaque noeud de code. */
void compute_all_paths(dragon_node *, size_t);

/* Fournit la liste des noeuds accessibles depuis un autre. */
const bitfield_t *get_paths_bits(const dragon_node *);

/* Détermine toute la chaîne hiérarchique de domination. */
void compute_all_dominators(dragon_node *, size_t);

/* Fournit la liste des noeuds dominés par un noeud. */
const bitfield_t *get_domination_bits(const dragon_node *);



/* ---------------------------- ENCAPSULATION DES NOEUDS ---------------------------- */


/* Concentration de tous les efforts */
typedef struct _dragon_knight dragon_knight;


/* Attaque la complexité d'un code en créant des noeuds. */
dragon_knight *begin_dragon_knight(GArchProcessor *, const instr_coverage *, const mrange_t *, const vmpa2t *);

/* Supprime de la mémoire les données d'une complexité de code. */
void end_dragon_knight(dragon_knight *);

/* Fournit les éléments utiles à un traitement de blocs de code. */
void get_dragon_knight_content(const dragon_knight *, dragon_node **, size_t *);

/* Fournit un noeud particulier à partir d'une liste. */
dragon_node *get_dragon_knight_node(const dragon_knight *, size_t);

/* Fournit l'indice d'un noeud particulier à partir d'une liste. */
size_t get_dragon_knight_node_index(const dragon_knight *, dragon_node *);

/* Recherche un noeud selon son intruction de départ. */
dragon_node *find_knight_node_for_instruction(const dragon_knight *, bool, const GArchInstruction *);

/* Traduit une complexité de noeuds en liste de blocs basiques. */
GBlockList *translate_dragon_knight(const dragon_knight *, GLoadedBinary *);



#endif  /* _ANALYSIS_DISASS_DRAGON_H */
