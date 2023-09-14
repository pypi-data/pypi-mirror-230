
/* Chrysalide - Outil d'analyse de fichiers binaires
 * incoming.h - prototypes pour les liens entrants d'un bloc de code dans une représentation graphique
 *
 * Copyright (C) 2019 Cyrille Bagard
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


#ifndef _GTKEXT_GRAPH_INCOMING_H
#define _GTKEXT_GRAPH_INCOMING_H


#include "cluster.h"
#include "edge.h"



/* Depuis leaving.h : détails sur le départ d'un lien */
typedef struct _leaving_link_t leaving_link_t;

/* Définition du tracé d'un lien */
typedef struct _incoming_link_t
{
    GGraphCluster *owner;                   /* Propriétaire du lien        */

    InstructionLinkType type;               /* Complexité du tracé         */

    const size_t *hslot;                    /* Couche horizontale réservée */
    GdkPoint end[2];                        /* Point d'arrivée final       */

    GGraphEdge *edge;                       /* Lien complet en préparation */

    leaving_link_t *other;                  /* Autre extrémité du lien     */

} incoming_link_t;


/* Crée un point d'attache pour un lien entrant simple. */
incoming_link_t *create_incoming_link(GGraphCluster *, InstructionLinkType, leaving_link_t *);

/* Crée un point d'attache pour un lien entrant de boucle. */
incoming_link_t *create_incoming_loop_link(GGraphCluster *, const GdkPoint *, leaving_link_t *);

/* Détruit un point d'attache pour un lien entrant. */
void delete_incoming_link(incoming_link_t *);

/* Compare deux liens entrants. */
int cmp_incoming_links(const incoming_link_t **, const incoming_link_t **);



#endif  /* _GTKEXT_GRAPH_INCOMING_H */
