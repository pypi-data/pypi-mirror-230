
/* Chrysalide - Outil d'analyse de fichiers binaires
 * pending.h - prototypes pour la consolidation de correspondances partielles
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


#ifndef _ANALYSIS_SCAN_MATCHES_PENDING_H
#define _ANALYSIS_SCAN_MATCHES_PENDING_H


#include <assert.h>
#include <stdbool.h>


#include "../../content.h"



/* Couverture d'une correspondance */
typedef struct _match_area_t
{
    phys_t start;                           /* Point de départ             */
    phys_t end;                             /* Point d'arrivée (exclus)    */

    unsigned long ttl;                      /* Durée de vie pour analyse   */

} match_area_t;

/* Suivi de correspondances */
typedef struct _pending_matches_t
{
    phys_t content_start;                   /* Point de début du contenu   */
    phys_t content_end;                     /* Point de fin du contenu     */

    match_area_t *areas;                    /* Zones couvertes             */
    size_t allocated;                       /* Nombre d'allocations        */
    size_t used;                            /* Nombre de zones             */

    bool initialized;                       /* Etat du suivi               */

    bool abort;                             /* Inutilité d'une poursuite   */

} pending_matches_t;


/* Initialise une structure de consolidation de correspondances. */
void init_pending_matches(pending_matches_t *, const phys_t *, const phys_t *);

/* Copie une structure de consolidation de correspondances. */
void copy_pending_matches(pending_matches_t *, const pending_matches_t *);

/* Fusionner une structure de consolidation avec une autre. */
void merge_pending_matches(pending_matches_t *, const pending_matches_t *);

/* Libère la mémoire utilisée par une consolidation. */
void exit_pending_matches(pending_matches_t *);

// TODO ajouter un assert(used == 0) si !initialized */
#define are_pending_matches_initialized(pm) pm->initialized

#define set_pending_matches_initialized(pm) pm->initialized = true

/* Dénombre les correspondances établies jusque là. */
size_t count_pending_matches(const pending_matches_t *);

/* Fournit la liste des correspondances établies à présent. */
match_area_t * const  *get_all_pending_matches(const pending_matches_t *, size_t *);

/*  Ajoute au suivi la définition d'une nouvelle correspondance. */
void add_pending_match(pending_matches_t *, phys_t, phys_t);

/* Etend une zone couverte dans le suivi des correspondances. */
void extend_pending_match_beginning(pending_matches_t *, size_t, phys_t);

/* Etend une zone couverte dans le suivi des correspondances. */
void extend_pending_match_ending(pending_matches_t *, size_t, phys_t);

/* Réinitialisation à 0 tous les TTL de correspondances. */
void reset_pending_matches_ttl(pending_matches_t *);

#define keep_pending_match(p)   \
    do                          \
    {                           \
        assert(p->ttl == 0);    \
        p->ttl = 1;             \
    }                           \
    while (0);

/* Retire toutes les correspondances sans issue pour l'analyse. */
void purge_pending_matches(pending_matches_t *);

/* Trie les correspondances et retire tous les doublons. */
void sort_and_filter_pending_matches(pending_matches_t *);



#endif  /* _ANALYSIS_SCAN_MATCHES_PENDING_H */
