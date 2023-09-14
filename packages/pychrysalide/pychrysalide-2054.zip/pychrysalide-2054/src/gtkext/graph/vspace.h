
/* Chrysalide - Outil d'analyse de fichiers binaires
 * vspace.h - prototypes pour l'encadrement des espaces verticaux réservés
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


#ifndef _GTKEXT_GRAPH_VSPACE_H
#define _GTKEXT_GRAPH_VSPACE_H


#include "incoming.h"
#include "leaving.h"



/* Réservations d'espaces latéraux */
typedef struct _vspace_booking_t
{
    leaving_link_t *from;                   /* Bloc de départ du lien      */
    incoming_link_t *to;                    /* Bloc d'arrivée du lien      */

    GdkPoint *pts;                          /* Coordonnées des points      */

    bool external;                          /* Lien vers un cluster parent */

} vspace_booking_t;

/* Réservations d'espaces latéraux */
typedef struct _vspace_manager_t
{
    vspace_booking_t *pending;              /* Besoins exprimés            */
    size_t pending_count;                   /* Nombre de ces besoins       */

    vspace_booking_t **left;                /* Lignes disposées à gauche   */
    size_t left_count;                      /* Quantité de ces lignes      */

    vspace_booking_t **right;               /* Lignes disposées à droite  */
    size_t right_count;                     /* Quantité de ces lignes      */

} vspace_manager_t;


/* Initialise les réservations liens verticaux. */
void init_vspace_manager(vspace_manager_t *);

/* Termine les réservations liens verticaux. */
void exit_vspace_manager(vspace_manager_t *);

/* Inscrit une nouvelle réservation d'espace latéral. */
void extend_vspace_manager(vspace_manager_t *, leaving_link_t *, incoming_link_t *, GdkPoint *, bool);

/* Détermine l'emplacement requis pour les espaces latéraux. */
void compute_vspace_manager_needed_alloc(const vspace_manager_t *, bool, GtkAllocation *);

/* Réorganise au besoin les liens de boucle entre blocs. */
void sort_incoming_links_for_vspace_manager(vspace_manager_t *);

/* Décale vers la droite un ensemble de points. */
void offset_x_vspace_manager(vspace_manager_t *, gint);

/* Détermine les abscisses de tous les liens en place. */
gint compute_loop_link_x_with_vspace_manager(const vspace_manager_t *, const GtkAllocation *, bool);

/* Détermine les ordonnées de tous les liens en place. */
void compute_loop_link_y_with_vspace_manager(const vspace_manager_t *, const GtkAllocation *);



#endif  /* _GTKEXT_GRAPH_VSPACE_H */
