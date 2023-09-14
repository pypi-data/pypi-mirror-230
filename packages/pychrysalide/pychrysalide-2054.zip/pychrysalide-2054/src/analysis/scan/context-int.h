
/* Chrysalide - Outil d'analyse de fichiers binaires
 * context-int.h - prototypes internes pour un suivi d'analyses via contextes
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


#ifndef _ANALYSIS_SCAN_CONTEXT_INT_H
#define _ANALYSIS_SCAN_CONTEXT_INT_H


#include "context.h"


#include "expr.h"
#include "../../common/fnv1a.h"



#define ALLOCATION_STEP 10

/* Mémorisation des correspondances partielles */
typedef struct _atom_match_tracker_t
{
    phys_t *matches;                        /* Correspondances à confirmer */
    size_t allocated;                       /* Taille du talbeau préparé   */
    size_t used;                            /* Nombre d'éléments présents  */

} atom_match_tracker_t;

/* Mémorisation des correspondances complètes, par motif */
typedef struct _full_match_tracker_t
{
    GSearchPattern *pattern;                /* Motif commun aux trouvailles*/

    GScanMatch **matches;                   /* Correspondances confirmées  */
    size_t allocated;                       /* Taille du talbeau préparé   */
    size_t used;                            /* Nombre d'éléments présents  */

} full_match_tracker_t;

/* Condition définissant une règle de correspondance */
typedef struct _rule_condition_t
{
    char *name;                             /* Désignation de la règle     */
    fnv64_t name_hash;                      /* Empreinte de la désignation */

    GScanExpression *expr;                  /* Condition de correspondance */
    bool final_reduced;                     /* Réduction finale tentée ?   */

} rule_condition_t;

/* Contexte de suivi d'une analyse en cours (instance) */
struct _GScanContext
{
    GObject parent;                         /* A laisser en premier        */

    GScanOptions *options;                  /* Options d'analyses          */

    GBinContent *content;                   /* Contenu binaire traité      */
    bool scan_done;                         /* Phase d'analyse terminée ?  */

    patid_t next_patid;                     /* Prochain indice utilisable  */

    atom_match_tracker_t *atom_trackers;    /* Correspondances partielles  */

    full_match_tracker_t **full_trackers;   /* Correspondances confirmées  */
    size_t full_count;                      /* Quantité de correspondances */

    rule_condition_t *conditions;           /* Ensemble de règles suivies  */
    size_t cond_count;                      /* Quantité de ces conditions  */

};

/* Contexte de suivi d'une analyse en cours (classe) */
struct _GScanContextClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};



#endif  /* _ANALYSIS_SCAN_CONTEXT_INT_H */
