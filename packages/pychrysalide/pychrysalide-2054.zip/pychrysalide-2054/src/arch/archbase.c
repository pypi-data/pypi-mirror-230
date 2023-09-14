
/* Chrysalide - Outil d'analyse de fichiers binaires
 * archbase.c - définitions de base pour les architectures
 *
 * Copyright (C) 2009-2018 Cyrille Bagard
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


#include "archbase.h"


#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>



/******************************************************************************
*                                                                             *
*  Paramètres  : a = première adresse à comparer.                             *
*                b = seconde adresse à comparer.                              *
*                                                                             *
*  Description : Etablit la comparaison entre deux adresses.                  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int compare_vmpa(const vmpa_t *a, const vmpa_t *b)
{
    int result;                             /* Bilan à retourner           */

    if (*a < *b)
        result = -1;

    else if (*a == *b)
        result = 0;

    else
        result = 1;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : addr   = adresse virtuelle ou physique à traiter.            *
*                msize  = taille de cette adresse.                            *
*                buffer = chaîne de caractères à constituer. [OUT]            *
*                                                                             *
*  Description : Transforme une adresse en chaîne de caractères.              *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t vmpa_to_string(vmpa_t addr, MemoryDataSize msize, char buffer[VMPA_MAX_SIZE])
{
    size_t result;                          /* Taille en place à renvoyer  */

    switch (msize)
    {
        case MDS_8_BITS:
            snprintf(buffer, VMPA_MAX_SIZE,"0x%02" PRIx64, addr);
            result = 4;
            break;

        case MDS_16_BITS:
            snprintf(buffer, VMPA_MAX_SIZE, "0x%04" PRIx64, addr);
            result = 6;
            break;

        case MDS_32_BITS:
            snprintf(buffer, VMPA_MAX_SIZE, "0x%08" PRIx64, addr);
            result = 10;
            break;

        case MDS_64_BITS:
            snprintf(buffer, VMPA_MAX_SIZE, "0x%016" PRIx64, addr);
            result = 18;
            break;

        default:
            result = 0;
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : buffer = chaîne de caractères à consulter.                   *
*                                                                             *
*  Description : Transforme une chaîne de caractères en adresse.              *
*                                                                             *
*  Retour      : Adresse obtenue.                                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

vmpa_t string_to_vmpa(const char *buffer)
{
    return (vmpa_t)strtoull(buffer, NULL, 16);

}
