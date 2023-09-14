
/* Chrysalide - Outil d'analyse de fichiers binaires
 * offset.h - prototypes pour la prise en compte des espaces entre octets dans un motif de recherche
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


#ifndef _ANALYSIS_SCAN_PATTERNS_TOKENS_OFFSET_H
#define _ANALYSIS_SCAN_PATTERNS_TOKENS_OFFSET_H


#include <stdbool.h>

#include "../../../../arch/vmpa.h"



/* Mémorisation d'une souplesse dans les positions visées */
typedef struct _node_offset_range_t
{
    /**
     * Les deux champs ci-après font bien référence à des positions absolues,
     * et non à des bornes d'espace, lors que les résultats de correspondances
     * sont encore non initialisés.
     *
     * Ensuite ces bornes représentent bien un espace séparant les résultats
     * issus de deux noeuds.
     */
    phys_t min;                             /* Position minimale           */
    phys_t max;                             /* Position maximale           */

} node_offset_range_t;


/* Fournit les bornes d'une zone à analyser. */
bool get_node_offset_range(const node_offset_range_t *, phys_t, phys_t, phys_t *, phys_t *);






/* Mémorisation d'une souplesse dans les positions visées */
typedef struct _node_search_offset_t
{
    node_offset_range_t range;              /* Bornes de décalage uniques  */

    node_offset_range_t *ranges;            /* Bornes de décalage multiples*/
    size_t allocated;                       /* Nombre d'allocations        */

    node_offset_range_t *gen_ptr;           /* Accès générique à la liste  */

    size_t used;                            /* Nombre de bornes présentes  */

} node_search_offset_t;


/* Initialise une mémorisation d'intervales de tolérance. */
void init_node_search_offset(node_search_offset_t *);

/* Copie une mémorisation d'intervales entre positions. */
void copy_node_search_offset(node_search_offset_t *, const node_search_offset_t *);

/* Fusionne une mémorisation d'intervales entre positions. */
void merge_node_search_offset(node_search_offset_t *, const node_search_offset_t *);

/* Met fin à une mémorisation d'intervales de tolérance. */
void exit_node_search_offset(node_search_offset_t *);

/* Fournit la liste des tolérances bornées établies à présent. */
/* TODO : supprimer un niveau d'indirection */
node_offset_range_t * const *get_node_search_offset_ranges(const node_search_offset_t *, size_t *);

/* Ajoute un nouvel espace borné aux décalages tolérés. */
void add_range_to_node_search_offset(node_search_offset_t *, phys_t, phys_t, const phys_t *);

#define disable_all_ranges_in_node_search_offset(off) \
    (off)->used = 0

/* Indique si une position est comprise dans un intervale. */
bool does_node_search_offset_include_pos_forward(const node_search_offset_t *, phys_t, phys_t);



#endif  /* _ANALYSIS_SCAN_PATTERNS_TOKENS_OFFSET_H */
