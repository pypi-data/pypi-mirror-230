
/* Chrysalide - Outil d'analyse de fichiers binaires
 * pending.c - consolidation de correspondances partielles
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


#include "pending.h"


#include <malloc.h>
#include <stdlib.h>
#include <string.h>


#include "../../../common/sort.h"



/* ------------------------- MEMORISATION D'UNE ZONE BORNEE ------------------------- */


/* Compare deux couvertures bornées de correspondances. */
static int compare_match_area(const match_area_t *, const match_area_t *);



/* -------------------- CONSERVATION DE CORRESPONDANCES ETABLIES -------------------- */


#define PENDING_ALLOC_SIZE 10







/* ---------------------------------------------------------------------------------- */
/*                           MEMORISATION D'UNE ZONE BORNEE                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : a = pointeur vers la première zone à analyser.               *
*                b = pointeur vers la seconde zone à analyser.                *
*                                                                             *
*  Description : Compare deux couvertures bornées de correspondances.         *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int compare_match_area(const match_area_t *a, const match_area_t *b)
{
    int result;                             /* Bilan à renvoyer            */

    result = sort_unsigned_long_long(a->start, b->start);

    if (result == 0)
        result = sort_unsigned_long_long(a->end, b->end);

    if (result == 0)
        result = sort_unsigned_long_long(a->ttl, b->ttl);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                      CONSERVATION DE CORRESPONDANCES ETABLIES                      */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : matches = suivi de correspondances à initialiser.            *
*                start   = première position du contenu (souvent 0).          *
*                end     = position de fin du contenu.                        *
*                                                                             *
*  Description : Initialise une structure de consolidation de correspondances.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void init_pending_matches(pending_matches_t *matches, const phys_t *start, const phys_t *end)
{
    matches->content_start = *start;
    matches->content_end = *end;

    matches->areas = NULL;
    matches->allocated = 0;
    matches->used = 0;

    matches->initialized = false;

    matches->abort = false;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dest = suivi de correspondances à initialiser. [OUT]         *
*                src  = suivi de correspondances à copier.                    *
*                                                                             *
*  Description : Copie une structure de consolidation de correspondances.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void copy_pending_matches(pending_matches_t *dest, const pending_matches_t *src)
{
    dest->content_start = src->content_start;
    dest->content_end = src->content_end;

    dest->areas = malloc(src->used * sizeof(match_area_t));
    dest->allocated = src->used;
    dest->used = src->used;

    memcpy(dest->areas, src->areas, src->used * sizeof(match_area_t));

    dest->initialized = src->initialized;

    dest->abort = src->abort;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dest = suivi de correspondances à initialiser. [OUT]         *
*                src  = suivi de correspondances à copier.                    *
*                                                                             *
*  Description : Fusionne une structure de consolidation avec une autre.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void merge_pending_matches(pending_matches_t *dest, const pending_matches_t *src)
{
    if ((dest->used + src->used) > dest->allocated)
    {
        dest->allocated += src->used;

        dest->areas = realloc(dest->areas, dest->allocated * sizeof(match_area_t));

    }

    memcpy(&dest->areas[dest->used], src->areas, src->used * sizeof(match_area_t));

    dest->used += src->used;

    dest->initialized |= src->initialized;

    dest->abort |= src->abort;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : matches = suivi de correspondances à purger.                 *
*                                                                             *
*  Description : Libère la mémoire utilisée par une consolidation.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void exit_pending_matches(pending_matches_t *matches)
{
    if (matches->areas != NULL)
        free(matches->areas);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : matches = suivi de correspondances à consulter.              *
*                                                                             *
*  Description : Dénombre les correspondances établies jusque là.             *
*                                                                             *
*  Retour      : Quantité de correspondances complètes jusqu'à présent.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t count_pending_matches(const pending_matches_t *matches)
{
    size_t result;                          /* Quantité à renvoyer         */

    result = matches->used;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : matches = suivi de correspondances à consulter.              *
*                count   = nombre de correspondances en attente. [OUT]        *
*                                                                             *
*  Description : Fournit la liste des correspondances établies à présent.     *
*                                                                             *
*  Retour      : Liste de correspondances en lecture seule.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

match_area_t * const *get_all_pending_matches(const pending_matches_t *matches, size_t *count)
{
    match_area_t * const *result;           /* Série à renvoyer            */

    result = &matches->areas;

    *count = matches->used;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : matches = suivi de correspondances à compléter.              *
*                start   = point de départ d'une nouvelle correspondance.     *
*                length  = taille de la zone couverte.                        *
*                                                                             *
*  Description : Ajoute au suivi la définition d'une nouvelle correspondance. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void add_pending_match(pending_matches_t *matches, phys_t start, phys_t length)
{
    match_area_t *area;                     /* Zone à initialiser          */

    if (matches->used == matches->allocated)
    {
        matches->allocated += PENDING_ALLOC_SIZE;

        matches->areas = realloc(matches->areas, matches->allocated * sizeof(match_area_t));

    }

    area = &matches->areas[matches->used++];

    area->start = start;
    area->end = start + length;

    assert(matches->content_start <= area->start);
    assert(area->end <= matches->content_end);

    area->ttl = 1;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : matches = suivi de correspondances à compléter.              *
*                target  = indice de la zone de correspondance concernée.     *
*                start   = nouvelle position initiale de la zone couverte.    *
*                                                                             *
*  Description : Etend une zone couverte dans le suivi des correspondances.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void extend_pending_match_beginning(pending_matches_t *matches, size_t target, phys_t start)
{
    match_area_t *area;                     /* Zone à actualiser           */

    assert(target < matches->used);

    area = &matches->areas[target];

    if (area->ttl == 0)
    {
        assert(matches->content_start <= start);

        area->start = start;

        area->ttl = 1;

    }
    else
    {
        assert(area->ttl == 1);

        add_pending_match(matches, start, area->end - start);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : matches = suivi de correspondances à compléter.              *
*                target  = indice de la zone de correspondance concernée.     *
*                length  = taille de la zone couverte supplémentaire.         *
*                                                                             *
*  Description : Etend une zone couverte dans le suivi des correspondances.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void extend_pending_match_ending(pending_matches_t *matches, size_t target, phys_t end)
{
    match_area_t *area;                     /* Zone à actualiser           */

    assert(target < matches->used);

    area = &matches->areas[target];

    if (area->ttl == 0)
    {
        assert(end <= matches->content_end);

        area->end = end;

        area->ttl = 1;

    }
    else
    {
        assert(area->ttl == 1);

        add_pending_match(matches, area->start, end - area->start);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : matches = suivi de correspondances à modifier.               *
*                                                                             *
*  Description : Réinitialisation à 0 tous les TTL de correspondances.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void reset_pending_matches_ttl(pending_matches_t *matches)
{
    size_t i;                               /* Boucle de parcours          */

    assert(matches->initialized);

    for (i = 0; i < matches->used; i++)
        matches->areas[i].ttl = 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : matches = suivi de correspondances à modifier.               *
*                                                                             *
*  Description : Retire toutes les correspondances sans issue pour l'analyse. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void purge_pending_matches(pending_matches_t *matches)
{
    match_area_t *del_start;                /* Départ d'une zone morte     */
    match_area_t *del_end;                  /* Fin d'une zone morte        */
    size_t del_remaining;                   /* Nombre de valides ensuite   */
    size_t del_count;                       /* Nombre d'éléments à effacer */
    size_t i;                               /* Boucle de parcours          */

    assert(matches->initialized);

    /**
     * Note : le code original était le suivant :
     *

     *    for (i = matches->used; i > 0; i--)
     *        if (matches->areas[i - 1].ttl == 0)
     *        {
     *            memmove(&matches->areas[i - 1], &matches->areas[i], (matches->used - i) * sizeof(match_area_t));
     *            matches->used--;
     *        }
     *
     * Pour éviter les appels à memmove(), un déplacement par blocs est désormais visée.
     */

    del_start = NULL;
    del_end = NULL;
    del_count = 0;
    del_remaining = 0;

    /* Suppression en bloc si possible */

    for (i = matches->used; i > 0; i--)
    {
        if (matches->areas[i - 1].ttl == 0)
        {
            del_start = &matches->areas[i - 1];

            if (del_end == NULL)
            {
                del_end = del_start;
                del_remaining = matches->used - i;
            }

            del_count++;

        }
        else
        {
            if (del_start != NULL)
            {
                assert(&matches->areas[i] == del_start);

                if (del_remaining > 0)
                    memmove(del_start, del_end + 1, del_remaining * sizeof(match_area_t));

                assert(matches->used > del_count);
                matches->used -= del_count;

                del_start = NULL;
                del_end = NULL;
                del_count = 0;
                del_remaining = 0;

            }

        }

    }

    /* Dernier traitement au besoin */

    if (del_start != NULL)
    {
        assert(&matches->areas[0] == del_start);

        if (del_remaining > 0)
            memmove(del_start, del_end + 1, del_remaining * sizeof(match_area_t));

        assert(matches->used >= del_count);
        matches->used -= del_count;

    }

    /* Bilan */

    matches->abort = (matches->used == 0);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : matches = suivi de correspondances à finaliser.              *
*                                                                             *
*  Description : Trie les correspondances et retire tous les doublons.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void sort_and_filter_pending_matches(pending_matches_t *matches)
{
    match_area_t *last;                     /* Dernière zone conservée     */
    size_t i;                               /* Boucle de parcours          */
    match_area_t *cur;                      /* Zone courante dans l'analyse*/

    if (matches->used > 0)
    {
        qsort(matches->areas, matches->used, sizeof(match_area_t), (__compar_fn_t)compare_match_area);

        last = &matches->areas[0];

        for (i = 1; i < matches->used; i++)
        {
            cur = &matches->areas[i];

            if (last->start != cur->start || last->end != cur->end)
            {
                if ((cur - last) > 1)
                {
                    memmove(last + 1, cur, (matches->used - i) * sizeof(match_area_t));
                    matches->used -= (cur - last + 1);
                }

                last = cur;

            }

        }

        cur = &matches->areas[matches->used - 1];

        if (last != cur)
            matches->used = last - matches->areas + 1;

    }

}
