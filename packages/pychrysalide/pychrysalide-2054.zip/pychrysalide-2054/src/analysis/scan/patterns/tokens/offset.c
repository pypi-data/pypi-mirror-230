
/* Chrysalide - Outil d'analyse de fichiers binaires
 * offset.c - décomposition d'un motif de recherche en atomes assemblés
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#include "offset.h"


#include <assert.h>






/******************************************************************************
*                                                                             *
*  Paramètres  : range     = bornes décrivant un espace quelconque.           *
*                available = espace restant disponible.                       *
*                min       = point de départ pour parcourir une zone. [OUT]   *
*                max       = point d'arrivée pour parcourir une zone. [OUT]   *
*                                                                             *
*  Description : Fournit les bornes d'une zone à analyser.                    *
*                                                                             *
*  Retour      : true si assez d'espace est disponible, false sinon.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool get_node_offset_range(const node_offset_range_t *range, phys_t len, phys_t available, phys_t *min, phys_t *max)
{
    bool result;                            /* Bilan à retourner           */

    if ((len + range->min) > available)
        result = false;

    else
    {
        result = true;

        *min = range->min;
        *max = range->max;

        if ((len + *max) > available)
        {
            *max = available - len;
            assert(*max >= *min);
        }

    }

    return result;

}











/******************************************************************************
*                                                                             *
*  Paramètres  : offset = suivi de tolérances bornées à initialiser.          *
*                                                                             *
*  Description : Initialise une mémorisation d'intervales de tolérance.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void init_node_search_offset(node_search_offset_t *offset)
{
    offset->ranges = NULL;
    offset->allocated = 0;

    offset->gen_ptr = NULL;

    offset->used = 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dest = suivi de tolérances bornées à initialiser. [OUT]      *
*                src  = suivi de tolérances bornées à copier.                 *
*                                                                             *
*  Description : Copie une mémorisation d'intervales entre positions.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void copy_node_search_offset(node_search_offset_t *dest, const node_search_offset_t *src)
{
    init_node_search_offset(dest);

    switch (src->used)
    {
        case 0:
            dest->gen_ptr = NULL;
            break;

        case 1:
            dest->range = src->range;
            dest->gen_ptr = &dest->range;
            break;

        default:
            dest->ranges = malloc(src->used * sizeof(node_offset_range_t));
            memcpy(dest->ranges, src->ranges, src->used * sizeof(node_offset_range_t));
            dest->gen_ptr = dest->ranges;;
            break;

    }

    dest->used = src->used;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dest = suivi de tolérances bornées à initialiser. [OUT]      *
*                src  = suivi de tolérances bornées à copier.                 *
*                                                                             *
*  Description : Fusionne une mémorisation d'intervales entre positions.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void merge_node_search_offset(node_search_offset_t *dest, const node_search_offset_t *src)
{
    node_offset_range_t * const *list;      /* Liste d'intervales à copier */
    size_t i;                               /* Boucle de parcours          */

    if ((dest->used + src->used) > 1 && (dest->used + src->used) > dest->allocated)
    {
        dest->allocated += src->used;

        dest->ranges = realloc(dest->ranges, dest->allocated * sizeof(node_offset_range_t));

    }

    list = get_node_search_offset_ranges(src, (size_t []){ 0 });

    for (i = 0; i < src->used; i++)
        add_range_to_node_search_offset(dest, (*list)[i].min, (*list)[i].max, NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : offset = suivi de tolérances bornées à terminer.             *
*                                                                             *
*  Description : Met fin à une mémorisation d'intervales de tolérance.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void exit_node_search_offset(node_search_offset_t *offset)
{
    if (offset->ranges != NULL)
        free(offset->ranges);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : offset = suivi de tolérances bornées à consulter.            *
*                count  = nombre de bornes enregistrées. [OUT]                *
*                                                                             *
*  Description : Fournit la liste des tolérances bornées établies à présent.  *
*                                                                             *
*  Retour      : Liste d'intervales en lecture seule.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

node_offset_range_t * const *get_node_search_offset_ranges(const node_search_offset_t *offset, size_t *count)
{
    node_offset_range_t * const *result;    /* Série à renvoyer            */

    result = &offset->gen_ptr;

    *count = offset->used;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : offset   = suivi de tolérances bornées à consulter.          *
*                min      = point de départ pour parcourir une zone.          *
*                max      = point d'arrivée pour parcourir une zone.          *
*                datasize = taille maximale pour définir une inversion NOT.   *
*                                                                             *
*  Description : Ajoute un nouvel espace borné aux décalages tolérés.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void add_range_to_node_search_offset(node_search_offset_t *offset, phys_t min, phys_t max, const phys_t *datasize)
{
    bool not;                               /* Traduction de la taille     */
    size_t needed;                          /* Nombre d'emplacements requis*/

    not = (datasize != NULL);

    /* Si le réceptacle unique peut être employé... */
    if (offset->used == 0 && !not)
    {
        offset->range.min = min;
        offset->range.max = max;

        offset->used = 1;

        offset->gen_ptr = &offset->range;

    }

    /* Sinon le groupe dynamique est sollicité */
    else
    {
        needed = offset->used + (not ? 2 : 1);

        if (needed > offset->allocated)
        {
            offset->ranges = realloc(offset->ranges, needed * sizeof(node_offset_range_t));
            offset->allocated = needed;
        }

        /* Bascule d'un éventuel intervale courant */
        if (offset->used == 1)
        {
            offset->ranges[0].min = offset->range.min;
            offset->ranges[0].max = offset->range.max;
        }

        if (not)
        {
            if (min > 0)
            {
                offset->ranges[offset->used].min = 0;
                offset->ranges[offset->used].max = min - 1;

                offset->used++;

            }

            if ((max + 1) < *datasize)
            {
                offset->ranges[offset->used].min = max + 1;
                offset->ranges[offset->used].max = *datasize - (max + 1);

                offset->used++;

            }

        }
        else
        {
            offset->ranges[offset->used].min = min;
            offset->ranges[offset->used].max = max;

            offset->used++;

        }

        offset->gen_ptr = offset->ranges;

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : offset = suivi de tolérances bornées à consulter.            *
*                last   = dernière position validée.                          *
*                pos    = nouvelle position potentielle.                      *
*                                                                             *
*  Description : Indique si une position est comprise dans un intervale.      *
*                                                                             *
*  Retour      : Bilan de la détermination.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool does_node_search_offset_include_pos_forward(const node_search_offset_t *offset, phys_t last, phys_t pos)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours          */
    const node_offset_range_t *range;       /* Accès rapide aux infos.     */

    result = false;

    for (i = 0; i < offset->used; i++)
    {
        range = &offset->gen_ptr[i];

        result = ((last + range->min) <= pos && pos <= (last + range->max));
        if (result) break;

    }

    return result;

}
