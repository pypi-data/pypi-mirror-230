
/* Chrysalide - Outil d'analyse de fichiers binaires
 * hspace.h - prototypes pour l'encadrement des espaces horizontaux réservés
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


#ifndef _GTKEXT_GRAPH_HSPACE_H
#define _GTKEXT_GRAPH_HSPACE_H


#include <glib.h>



/* Réservation pour les lignes horizontales */
typedef struct _hspace_booking
{
    gint start;                             /* Abscisse de départ de ligne */
    size_t index;                           /* Indice de rangée verticale  */

} hspace_booking;


/* Prépare une réservation d'espace pour ligne horizontale. */
hspace_booking *create_hspace_booking(gint);

/* Compare deux réservations d'espace. */
int cmp_hspace_booking_r2l(const hspace_booking **, const hspace_booking **);

/* Compare deux réservations d'espace. */
int cmp_hspace_booking_l2r(const hspace_booking **, const hspace_booking **);



#endif  /* _GTKEXT_GRAPH_HSPACE_H */
