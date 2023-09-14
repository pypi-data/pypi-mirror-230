
/* Chrysalide - Outil d'analyse de fichiers binaires
 * manager.h - prototypes pour la prise en compte d'une syntaxe du langage d'assemblage
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


#ifndef _TOOLS_D2C_SYNTAX_MANAGER_H
#define _TOOLS_D2C_SYNTAX_MANAGER_H


#include <stdbool.h>


#include "../bits/manager.h"
#include "../conv/manager.h"



/* Syntaxe d'une ligne d'assembleur */
typedef struct _asm_pattern asm_pattern;


/* Crée un nouvel indicateur pour l'écriture d'une instruction. */
asm_pattern *create_asm_pattern(void);

/* Supprime de la mémoire un indicateur d'écriture ASM. */
void delete_asm_pattern(asm_pattern *);

/* Enregistre la présence d'un nouvel opérande dans la syntaxe. */
void register_asm_pattern_item(asm_pattern *, char *);

/* Marque les champs de bits effectivement utilisés. */
bool mark_asm_pattern_items(const asm_pattern *, const coding_bits *, const conv_list *);

/* Déclare les variables C associées aux opérandes de syntaxe. */
bool declare_asm_pattern(const asm_pattern *, int, const coding_bits *, const conv_list *, const char *, bool *);

/* Fournit si elle existe un nom nouveau pour une instruction. */
const char *get_keyword_from_asm_pattern(const asm_pattern *);

/* Définit les variables C associées aux opérandes de syntaxe. */
bool define_asm_pattern(const asm_pattern *, int, const char *, const coding_bits *, const conv_list *, const char *, bool *);



#endif  /* _TOOLS_D2C_SYNTAX_MANAGER_H */
