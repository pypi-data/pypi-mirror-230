
/* Chrysalide - Outil d'analyse de fichiers binaires
 * bitap-int.h - prototypes internes pour la méthode de recherche basée sur l'algorithme Bitap
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


#ifndef _ANALYSIS_SCAN_PATTERNS_BACKENDS_BITAP_INT_H
#define _ANALYSIS_SCAN_PATTERNS_BACKENDS_BITAP_INT_H


#include "bitap.h"


#include <immintrin.h>


#include "../backend-int.h"
#include "../../../../common/cpu.h"
#include "../../../../../config.h"



#define BITAP_ATOM_SIZE 7


#ifdef HAVE_AVX2

/* Suivi d'un groupe de chaînes */
typedef struct _grouped_strings_avx2_t
{
    __m256i pattern_masks[256];             /* Programmation de détections */
    __m256i found_masks;                    /* Masques multiples d'alerte  */

    __m256i R;                              /* Résultats courants          */

    size_t m[32];                           /* Taille des chaînes          */

    patid_t found_id[32];                   /* Indice des résultats        */

    size_t available;                       /* Nombre de places disponibles*/
    size_t used;                            /* Quantité de places utilisées*/

} grouped_strings_avx2_t;

/* Suivi de l'ensemble de chaînes */
typedef struct _group_manager_avx2_t
{
    grouped_strings_avx2_t **strings_8;     /* Chaînes de taille 8 max     */
    size_t count_8;                         /* Quantité de ces chaînes     */

} group_manager_avx2_t;

#endif

#ifdef HAVE_AVX512_F

/* Suivi d'un groupe de chaînes */
typedef struct _grouped_strings_avx512_t
{
    __m512i pattern_masks[256];             /* Programmation de détections */
    __m512i found_masks;                    /* Masques multiples d'alerte  */

    __m512i R;                              /* Résultats courants          */

    size_t m[64];                           /* Taille des chaînes          */

    patid_t found_id[64];                   /* Indice des résultats        */

    size_t used;                            /* Quantité de places utilisées*/
    size_t available;                       /* Nombre de places disponibles*/

} grouped_strings_avx512_t;

/* Suivi de l'ensemble de chaînes */
typedef struct _group_manager_avx512_t
{
    grouped_strings_avx512_t **strings_8;   /* Chaînes de taille 8 max     */
    size_t count_8;                         /* Quantité de ces chaînes     */

} group_manager_avx512_t;

#endif


/* Méthode de recherche basée sur l'algorithme Bitap (instance) */
struct _GBitapBackend
{
    GEngineBackend parent;                  /* A laisser en premier        */

    CPUSMIDFeature optimization;            /* Mode de calculs             */

#if defined HAVE_AVX2 || defined HAVE_AVX512_F
    union
    {
#   ifdef HAVE_AVX2
        group_manager_avx2_t manager_avx2;  /* Gestionnaire pour AVX2      */
#   endif
#   ifdef HAVE_AVX512_F
        group_manager_avx512_t manager_avx512;/* Gestionnaire pour AVX-512 */
#   endif
    };
#endif

};

/* Méthode de recherche basée sur l'algorithme Bitap (classe) */
struct _GBitapBackendClass
{
    GEngineBackendClass parent;             /* A laisser en premier        */

};



#endif  /* _ANALYSIS_SCAN_PATTERNS_BACKENDS_BITAP_INT_H */
