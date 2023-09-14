
/* Chrysalide - Outil d'analyse de fichiers binaires
 * atom.h - prototypes pour la détermination d'atomes à partir de motifs
 *
 * Copyright (C) 2023 Cyrille Bagard
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


#ifndef _ANALYSIS_SCAN_PATTERNS_TOKENS_ATOM_H
#define _ANALYSIS_SCAN_PATTERNS_TOKENS_ATOM_H


#include <stdbool.h>


#include "../backend.h"
#include "../../context.h"
#include "../../../../arch/vmpa.h"
#include "../../../../common/bits.h"
#include "../../../../common/szstr.h"



/* Suivi des motifs réellement recherchés */
typedef struct _tracked_scan_atom_t
{
    phys_t pos;                             /* Début de sélection atomique */
    phys_t len;                             /* Taille de ladite sélection  */
    phys_t rem;                             /* Reste après l'atome         */

    patid_t pid;                            /* Identifiant de la bribe     */

} tracked_scan_atom_t;


/* Note l'intêret de rechercher un octet particulier. */
int rate_byte_quality(bin_t, bitfield_t *, size_t *);

/* Termine la notation d'un ensemble d'octets. */
int finish_quality_rating(const bitfield_t *, size_t);

/* Détermine la portion idéale de recherche. */
void find_best_atom(const sized_binary_t *, size_t , tracked_scan_atom_t *, size_t *);

/* Etablit la liste des cas de figures ignorant la casse. */
sized_binary_t *make_atoms_case_insensitive(const sized_binary_t *, const tracked_scan_atom_t *, size_t);

/* Etablit la liste des cas de figures avec un octet partiel. */
sized_binary_t *make_atoms_from_masked_byte(bin_t, bin_t, size_t *);

/* Enregistre l'atome déterminé d'une série d'octets. */
bool enroll_prepared_atom(const sized_binary_t *, GScanContext *, GEngineBackend *, tracked_scan_atom_t *);



#endif  /* _ANALYSIS_SCAN_PATTERNS_TOKENS_ATOM_H */
