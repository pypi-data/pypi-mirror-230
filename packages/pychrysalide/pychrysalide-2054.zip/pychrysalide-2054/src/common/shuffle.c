
/* Chrysalide - Outil d'analyse de fichiers binaires
 * shuffle.c - permtutation aléatoire des éléments d'un ensemble fini
 *
 * Copyright (C) 2016-2018 Cyrille Bagard
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


#include "shuffle.h"


#include <malloc.h>
#include <stdlib.h>
#include <string.h>



/******************************************************************************
*                                                                             *
*  Paramètres  : panel = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Mélange le contenu d'une liste.                              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void shuffle(void *base, size_t nmemb, size_t size)
{
    char *list;                             /* Conversion pour le confort  */
    char *tmp;                              /* Lieu de transition          */
    size_t i;                               /* Boucle de parcours          */
    size_t j;                               /* Emplacement aléatoire       */

    /**
     * Application de l'algorithme Fisher-Yates.
     *
     * Cf. https://en.wikipedia.org/wiki/Fisher%E2%80%93Yates_shuffle
     *
     * En version hors-ligne, cela donne :
     *
     *    -- To shuffle an array a of n elements (indices 0..n-1):
     *    for i from 0 to n−2 do
     *        j ← random integer such that i ≤ j < n
     *        exchange a[i] and a[j]
     *
     */

    if (nmemb > 1)
    {
        list = (char *)base;

        tmp = malloc(size);

        for (i = 0; i < (nmemb - 1); i++)
        {
            j = i + rand() % (nmemb - i);

            if (j != i)
            {
                memcpy(tmp, list + i * size, size);
                memcpy(list + i * size, list + j * size, size);
                memcpy(list + j * size, tmp, size);
            }

        }

        free(tmp);

    }

}
