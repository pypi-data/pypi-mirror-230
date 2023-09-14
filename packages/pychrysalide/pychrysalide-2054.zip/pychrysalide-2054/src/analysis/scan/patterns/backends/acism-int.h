
/* Chrysalide - Outil d'analyse de fichiers binaires
 * acism-int.h - prototypes internes pour la méthode de recherche basée sur l'algorithme Aho-Corasick Interleaved State-transition Matrix
 *
 * Copyright (C) 2022 Cyrille Bagard
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


#ifndef _ANALYSIS_SCAN_PATTERNS_BACKENDS_ACISM_INT_H
#define _ANALYSIS_SCAN_PATTERNS_BACKENDS_ACISM_INT_H


#include "acism.h"


#include <stdint.h>


#include "../backend-int.h"
#include "../../../../common/bits.h"



//#define __USE_BYTE_FREQ
//#define __SORT_BEFORE_BITMASK


#define ACSIM_ATOM_SIZE 7



/* Définition d'une portion de cible */
typedef struct _acism_source_t
{
    const uint8_t *atoms;                   /* Motif remarquable           */
    size_t len;                             /* Nombre d'octets considérés  */

    patid_t pid;                            /* Identifiant de suivi        */

} acism_source_t;

/* Etude de la fréquence des octets pour attribution des codes */
typedef struct _acism_freq_rank_t
{
    unsigned int frequency;                 /* Occurrences d'un octet      */
    uint8_t rank;                           /* Valeur dudit octet          */

} acism_freq_rank_t;

/* Identifiant unique pour une valeur 8 bits donnée (max 257) */
typedef uint16_t acism_code_t;

#define MIN_ACISM_CODE 0
#define MAX_ACISM_CODE 0xffff

/* Noeud de l'arborescence brute */
typedef struct _acism_trie_node_t
{
    struct _acism_trie_node_t *parent;      /* Noeud parent pour remontée  */
    struct _acism_trie_node_t *sibling;     /* Noeud de même niveau suivant*/
    struct _acism_trie_node_t *child;       /* Noeud de lecture suivant    */
    struct _acism_trie_node_t *suffix_link; /* Retour en cas d'échec       */

    bin_t data;                             /* Donnée brute représentée    */
    acism_code_t code;                      /* Identifiant du noeud        */

    patid_t pid;                            /* Identifiant de suivi        */

    acism_code_t min_child_code;            /* Plus petit code suivant     */
    acism_code_t max_child_code;            /* Plus grand code suivant     */
    size_t children_count;                  /* Nombre de codes suivants    */

    size_t matched_atom;                    /* Indice de correspondance    */

    size_t state_index;                     /* Indice de le tableau final  */

} acism_trie_node_t;

/* Cellule du tableau compressé final */
typedef union _acism_state_t
{
    uint32_t raw;                           /* Valeur brute                */

    struct
    {
        union
        {
            /* Indice 0 */
            struct
            {
                unsigned int match : 1;     /* Correspondance ici          */
                unsigned int suffix : 1;    /* Correspondance ailleurs     */
                unsigned int unused : 4;    /* Espace encore disponible    */
                unsigned int atom_size : 3; /* Taille d'atome représenté   */
            };

            /* Indice 1 et + */
            unsigned int code : 9;          /* Position depuis la base     */

        };

        unsigned int index : 23;            /* Indice de saut              */

    };

} acism_state_t;

/* Méthode de recherche basée sur l'algorithme Acism (instance) */
struct _GAcismBackend
{
    GEngineBackend parent;                  /* A laisser en premier        */

#ifdef __USE_BYTE_FREQ
    acism_code_t codes_for_bytes[256];      /* Traduction octets -> codes  */
    acism_code_t codes_count;               /* Quantité de traductions     */
#endif

    acism_source_t *sources;                /* Liste de motifs remarquables*/
    size_t sources_count;                   /* Quantité de ces motifs      */

    size_t nchars;                          /* Taille cumulée des motifs   */

#ifdef __USE_BYTE_FREQ
    acism_freq_rank_t frequencies[256];     /* Fréquences des octets       */
#endif

    acism_trie_node_t *nodes;               /* Liste de noeuds             */
    size_t nodes_used;                      /* Nombre de noeuds utilisés   */

    bitfield_t *bitmap_usage;               /* Localisation des usages     */
    acism_state_t *states;                  /* Tableau de transitions      */
    patid_t *pids;                          /* Identifiants de motifs      */

};

/* Méthode de recherche basée sur l'algorithme Acism (classe) */
struct _GAcismBackendClass
{
    GEngineBackendClass parent;             /* A laisser en premier        */

};



#endif  /* _ANALYSIS_SCAN_PATTERNS_BACKENDS_ACISM_INT_H */
