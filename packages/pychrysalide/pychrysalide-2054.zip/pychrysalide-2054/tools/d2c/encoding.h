
/* Chrysalide - Outil d'analyse de fichiers binaires
 * encoding.h - prototypes pour la représentation complète d'un encodage
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


#ifndef _TOOLS_D2C_ENCODING_H
#define _TOOLS_D2C_ENCODING_H


#include <stdbool.h>


#include "pproc.h"
#include "syntax.h"
#include "bits/manager.h"
#include "format/manager.h"
#include "hooks/manager.h"



/* Mémorisation d'un encodage complet */
typedef struct _encoding_spec encoding_spec;


/* Crée un nouveau suivi de l'encodage d'une instruction. */
encoding_spec *create_encoding_spec(void);

/* Supprime de la mémoire un suivi d'encodage d'une instruction. */
void delete_encoding_spec(encoding_spec *);

/* Définit le nom de code d'une spécification d'encodage. */
void define_encoding_spec_code_name(encoding_spec *, char *, unsigned int);

/* Indique si une spécification se range dans une catégorie. */
bool has_encoding_spec_prefix(const encoding_spec *, const char *);

/* Construit la distinction propre à un encodage. */
char *build_encoding_spec_prefix(const encoding_spec *spec);

/* Fournit le gestionnaire des définitions d'opérandes. */
operands_format *get_format_in_encoding_spec(const encoding_spec *);

/* Fournit le gestionnaire des bits d'un encodage d'instruction. */
coding_bits *get_bits_in_encoding_spec(const encoding_spec *);

/* Fournit la liste des fonctions à lier à une instruction. */
instr_hooks *get_hooks_in_encoding_spec(const encoding_spec *);

/* Enregistre une définition de syntaxe supplémentaire. */
void push_new_encoding_syntax(encoding_spec *);

/* Fournit un lien vers la définition de syntaxe courante. */
encoding_syntax *get_current_encoding_syntax(const encoding_spec *);

/* Traduit en code une sous-fonction de désassemblage. */
bool write_encoding_spec_raw_disass(const encoding_spec *, int, const char *, const char *, const pre_processor *);

/* Traduit en code une sous-fonction de désassemblage. */
bool write_encoding_spec_format_disass(const encoding_spec *, int, const char *, const char *, const char *);

/* Imprime les mots clefs de chaque syntaxe. */
bool write_encoding_spec_keywords(const encoding_spec *, int, const char *);

/* Imprime la définition d'un sous-identifiant pour un encodage. */
bool write_encoding_spec_subid(const encoding_spec *, int, const char *);

/* Imprime d'éventuels décrochages spécifiés pour un encodage. */
bool write_encoding_spec_hooks(const encoding_spec *, int, const char *, bool);



#endif  /* _TOOLS_D2C_ENCODING_H */
