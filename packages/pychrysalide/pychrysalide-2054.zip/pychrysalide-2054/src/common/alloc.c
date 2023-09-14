
/* Chrysalide - Outil d'analyse de fichiers binaires
 * alloc.c - gestion particulière des allocations
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#include "alloc.h"


#include <malloc.h>



/******************************************************************************
*                                                                             *
*  Paramètres  : ptr       = pointeur à traiter.                              *
*                allocated = taille actuellement allouée. [OUT]               *
*                needed    = taille finale nécessaire.                        *
*                                                                             *
*  Description : Assure qu'une zone de mémoire allouée a la taille requise.   *
*                                                                             *
*  Retour      : Pointeur à utiliser avec assurance.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void *ensure_allocation_size(void *ptr, size_t *allocated, size_t needed)
{
    void *result;                           /* Pointeur à renvoyer         */

    if (needed < *allocated)
        result = ptr;

    else
    {
        *allocated = needed;
        result = realloc(ptr, needed);
    }

    return result;

}
