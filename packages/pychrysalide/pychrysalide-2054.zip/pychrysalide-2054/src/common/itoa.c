
/* Chrysalide - Outil d'analyse de fichiers binaires
 * itoa.c - conversion d'un nombre en chaîne de caractères
 *
 * Copyright (C) 2023 Cyrille Bagard
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


#include "itoa.h"


#include <assert.h>
#include <malloc.h>
#include <math.h>



/******************************************************************************
*                                                                             *
*  Paramètres  : n    = nombre à transformer.                                 *
*                base = base à considérer pour la sortie.                     *
*                                                                             *
*  Description : Convertit une valeur en une forme textuelle.                 *
*                                                                             *
*  Retour      : Chaîne de caractères mises en place.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *itoa(long long n, unsigned char base)
{
    char *result;                           /* Texte à retourner           */
    size_t size;                            /* Taille de chaîne en sortie  */
    char *iter;                             /* Tête d'écriture             */
#ifndef NDEBUG
    size_t counter;                         /* Décompte des impressions    */
#endif
    long long rem;                          /* Unité à transposer          */

    /**
     * Préparation du stockage de la chaîne finale.
     */

    if (n == 0)
        size = 1;

    else if (n < 0)
    {
        size = (size_t)(log(-n) / log(base) + 1);
        size++;
    }
    else
        size = (size_t)(log(n) / log(base) + 1);

    /* '\0' final */
    size++;

    result = malloc(size);
    if (result == NULL) goto exit;

    /**
     * Remplissage avec la valeur textuelle correspondant à la valeur fournie.
     */

#ifndef NDEBUG
    counter = 0;
#endif

    if (n < 0)
    {
        result[0] = '-';
#ifndef NDEBUG
        counter++;
#endif

        n *= -1;

    }

    iter = result + size - 1;

    *iter-- = '\0';
#ifndef NDEBUG
    counter++;
#endif

    if (n == 0)
    {
        *iter-- = '0';
#ifndef NDEBUG
        counter++;
#endif
    }

    else
        while (n > 0)
        {
            rem = n % base;

            if (rem >= 10)
                *iter-- = 'a' + (rem - 10);
            else
                *iter-- = '0' + rem;

#ifndef NDEBUG
            counter++;
#endif

            n = n / base;

        }

    assert(counter < size);

 exit:

    return result;

}
