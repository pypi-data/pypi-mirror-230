
/* Chrysalide - Outil d'analyse de fichiers binaires
 * syntax.h - prototypes pour la représentation complète d'une syntaxe
 *
 * Copyright (C) 2014-2018 Cyrille Bagard
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


#ifndef _TOOLS_D2C_SYNTAX_H
#define _TOOLS_D2C_SYNTAX_H



#include "assert/manager.h"
#include "bits/manager.h"
#include "conv/manager.h"
#include "id/manager.h"
#include "pattern/manager.h"
#include "rules/manager.h"



/* Mémorisation d'une définition de syntaxe */
typedef struct _encoding_syntax encoding_syntax;


/* Crée un nouveau suivi d'une définition de syntaxe. */
encoding_syntax *create_encoding_syntax(void);

/* Supprime de la mémoire le suivi d'une définition de syntaxe. */
void delete_encoding_syntax(encoding_syntax *);

/* Fournit le gestionnaire des définitions d'identifiant. */
instr_id *get_encoding_syntax_subid(const encoding_syntax *);

/* Fournit la liste de conditions préalables. */
disass_assert *get_assertions_for_encoding_syntax(const encoding_syntax *);

/* Fournit la liste des fonctions de conversion. */
conv_list *get_conversions_in_encoding_syntax(const encoding_syntax *);

/* Fournit l'indicateur des écritures correctes d'assembleur. */
asm_pattern *get_asm_pattern_in_encoding_syntax(const encoding_syntax *);

/* Fournit un ensemble de règles supplémentaires éventuel. */
decoding_rules *get_rules_in_encoding_syntax(const encoding_syntax *);

/* Marque les éléments de syntaxe effectivement utilisés. */
bool mark_syntax_items(const encoding_syntax *, const coding_bits *);

/* Déclare les éléments d'une syntaxe isolée. */
bool declare_encoding_syntax(const encoding_syntax *, int, const coding_bits *);

/* Amorce la construction des éléments d'une syntaxe. */
bool write_encoding_syntax(const encoding_syntax *, int, const char *, const coding_bits *, bool, const char *, const char *, const size_t *, bool *);



#endif  /* _TOOLS_D2C_SYNTAX_H */
