
/* Chrysalide - Outil d'analyse de fichiers binaires
 * backend-int.h - prototypes internes pour une méthode de recherches au sein d'un contenu binaire
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


#ifndef _ANALYSIS_SCAN_PATTERNS_BACKEND_INT_H
#define _ANALYSIS_SCAN_PATTERNS_BACKEND_INT_H


#include "backend.h"



/* Indique la taille maximale des suites d'octets recherchées. */
typedef size_t (* get_backend_atom_max_size_fc) (const GEngineBackend *);

/* Inscrit dans le moteur une chaîne de caractères à rechercher. */
typedef patid_t (* enroll_plain_into_backend_fc) (GEngineBackend *, GScanContext *, const uint8_t *, size_t);

/* Met en ordre les derniers détails avant un premier scan. */
typedef void (* warm_up_backend_fc) (GEngineBackend *);

/* Parcours un contenu binaire à la recherche de motifs. */
typedef void (* run_backend_scan_fc) (const GEngineBackend *, GScanContext *);

/* Imprime quelques faits quant aux éléments mis en place. */
typedef void (* output_backend_stats_fc) (const GEngineBackend *);


/* Méthode de traitement d'un contenu binaire pour recherches (instance) */
struct _GEngineBackend
{
    GObject parent;                         /* A laisser en premier        */

};

/* Méthode de traitement d'un contenu binaire pour recherches (classe) */
struct _GEngineBackendClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    get_backend_atom_max_size_fc get_max_size;  /* Taille maximale d'atome */
    enroll_plain_into_backend_fc enroll_plain;  /* Inscription simple      */
    warm_up_backend_fc warm_up;             /* Préchauffage avant analyse  */
    run_backend_scan_fc run_scan;           /* Lancement d'une analyse     */
    output_backend_stats_fc output;         /* Impression de statistiques  */

};



#endif  /* _ANALYSIS_SCAN_PATTERNS_BACKEND_INT_H */
