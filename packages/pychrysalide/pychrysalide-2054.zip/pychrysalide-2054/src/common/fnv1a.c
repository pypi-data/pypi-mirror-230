
/* Chrysalide - Outil d'analyse de fichiers binaires
 * fnv1a.c - implémentaton du calcul rapide d'empreintes de chaînes
 *
 * Copyright (C) 2012-2018 Cyrille Bagard
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


#include "fnv1a.h"



/* Constante d'initialisation */
#define FNV1A_64_INIT 0xcbf29ce484222325ull

/* Coefficient magique ! */
#define FNV_64_PRIME 0x100000001b3ull



/******************************************************************************
*                                                                             *
*  Paramètres  : a = première empreinte à manipuler.                          *
*                b = seconde empreinte à manipuler.                           *
*                                                                             *
*  Description : Détermine si deux empreintes FNV1a sont indentiques ou non.  *
*                                                                             *
*  Retour      : Bilan de la comparaison : -1, 0 ou 1.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int cmp_fnv_64a(fnv64_t a, fnv64_t b)
{
    int result;                             /* Bilan à retourner           */

    if (a < b) result = -1;
    else if (a == b) result = 0;
    else result = 1;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : str = chaîne de caractères à traiter.                        *
*                                                                             *
*  Description : Détermine l'empreinte FNV1a d'une chaîne de caractères.      *
*                                                                             *
*  Retour      : Valeur calculée.                                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

fnv64_t fnv_64a_hash(const char *str)
{
    fnv64_t result;                         /* Valeur à retourner          */
    unsigned char *iter;                    /* Boucle de parcours          */

    result = FNV1A_64_INIT;

    for (iter = (unsigned char *)str; *iter; iter++)
    {
        result ^= (fnv64_t)*iter;
        result *= FNV_64_PRIME;
    }

    return result;

}
