
/* Chrysalide - Outil d'analyse de fichiers binaires
 * hspace.c - encadrement des espaces horizontaux réservés
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


#include "hspace.h"


#include <assert.h>
#include <malloc.h>
#ifndef NDEBUG
#   include <stdbool.h>
#endif



/******************************************************************************
*                                                                             *
*  Paramètres  : start = abscisse de départ de ligne.                         *
*                                                                             *
*  Description : Prépare une réservation d'espace pour ligne horizontale.     *
*                                                                             *
*  Retour      : Structure mise en place pour la conservation d'informations. *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

hspace_booking *create_hspace_booking(gint start)
{
    hspace_booking *result;                 /* Structure à retourner       */

    result = malloc(sizeof(hspace_booking));

    result->start = start;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = première réservation d'espace à comparer.                *
*                b = seconde réservation d'espace à comparer.                 *
*                                                                             *
*  Description : Compare deux réservations d'espace.                          *
*                                                                             *
*  Retour      : Bilan de comparaison.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int cmp_hspace_booking_r2l(const hspace_booking **a, const hspace_booking **b)
{
    int result;                             /* Bilan à retourner           */

    if ((*a)->start > (*b)->start)
        result = -1;

    else if ((*a)->start < (*b)->start)
        result = 1;

    else
    {
        assert(false);
        result = 0;
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = première réservation d'espace à comparer.                *
*                b = seconde réservation d'espace à comparer.                 *
*                                                                             *
*  Description : Compare deux réservations d'espace.                          *
*                                                                             *
*  Retour      : Bilan de comparaison.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int cmp_hspace_booking_l2r(const hspace_booking **a, const hspace_booking **b)
{
    int result;                             /* Bilan à retourner           */

    if ((*a)->start < (*b)->start)
        result = -1;

    else if ((*a)->start > (*b)->start)
        result = 1;

    else
    {
        assert(false);
        result = 0;
    }

    return result;

}
