
/* Chrysalide - Outil d'analyse de fichiers binaires
 * singleton-int.h - définitions internes propres aux réductions du nombre d'instances d'un même type
 *
 * Copyright (C) 2021 Cyrille Bagard
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


#ifndef _GLIBEXT_SINGLETON_INT_H
#define _GLIBEXT_SINGLETON_INT_H


#include "singleton.h"



/* Fournit une liste de candidats embarqués par un candidat. */
typedef GSingletonCandidate ** (* list_inner_instances_fc) (const GSingletonCandidate *, size_t *);

/* Met à jour une liste de candidats embarqués par un candidat. */
typedef void (* update_inner_instances_fc) (GSingletonCandidate *, GSingletonCandidate **, size_t);

/* Fournit l'empreinte d'un candidat à une centralisation. */
typedef guint (* hash_candidate_fc) (const GSingletonCandidate *);

/* Détermine si deux candidats à l'unicité sont identiques. */
typedef gboolean (* is_candidate_equal_fc) (const GSingletonCandidate *, const GSingletonCandidate *);

/* Marque un candidat comme figé. */
typedef void (* set_candidate_ro_fc) (GSingletonCandidate *);

/* Indique si le candidat est figé. */
typedef bool (* is_candidate_ro_fc) (const GSingletonCandidate *);


/* Instance d'objet visant à être unique (interface) */
struct _GSingletonCandidateIface
{
    GTypeInterface base_iface;              /* A laisser en premier        */

    list_inner_instances_fc list_inner;     /* Récupération d'internes     */
    update_inner_instances_fc update_inner; /* Mise à jour des éléments    */

    hash_candidate_fc hash;                 /* Prise d'empreinte           */
    is_candidate_equal_fc is_equal;         /* Comparaison                 */

    set_candidate_ro_fc set_ro;             /* Bascule en mode figé        */
    is_candidate_ro_fc is_ro;               /* Consultation de l'état      */

};


/* Redéfinition */
typedef GSingletonCandidateIface GSingletonCandidateInterface;



#endif  /* _GLIBEXT_SINGLETON_INT_H */
