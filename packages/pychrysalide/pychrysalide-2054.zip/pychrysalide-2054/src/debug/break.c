
/* Chrysalide - Outil d'analyse de fichiers binaires
 * break.c - manipulation des points d'arrêt
 *
 * Copyright (C) 2010-2018 Cyrille Bagard
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


#include "break.h"


#include <assert.h>
#include <malloc.h>


#include "break-int.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : bp   = point d'arrêt à initialiser.                          *
*                addr = adresse d'action du point d'arrêt.                    *
*                                                                             *
*  Description : Initialise le coeur d'un point d'arrêt.                      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void init_raw_breakpoint(raw_breakpoint *bp, virt_t addr)
{
    bp->addr = addr;

    bp->count = 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bp = point d'arrêt à traiter.                                *
*                                                                             *
*  Description : Libère le coeur d'un point d'arrêt.                          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void fini_raw_breakpoint(raw_breakpoint *bp)
{
    if (bp->count > 1)
        free(bp->sources);

    free(bp);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bp = point d'arrêt à consulter.                              *
*                                                                             *
*  Description : Indique l'adresse du point d'arrêt dans la mémoire ciblée.   *
*                                                                             *
*  Retour      : Adresse associée au point d'arrêt.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

virt_t get_raw_breakpoint_addr(const raw_breakpoint *bp)
{
    return bp->addr;

}



/******************************************************************************
*                                                                             *
*  Paramètres  : bp = point d'arrêt à consulter.                              *
*                                                                             *
*  Description : Fournit l'adresse d'origine d'un point d'arrêt de pas à pas. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : Un appel à cette fonction n'est valide que pour un point     *
*                d'arrêt de type RBO_STEP.                                    *
*                                                                             *
******************************************************************************/

virt_t get_raw_breakpoint_prev_addr(const raw_breakpoint *bp)
{
    virt_t result;                          /* Localisation à retourner    */
    bool found;                             /* Valide une obtention        */
    size_t i;                               /* Boucle de parcours          */

    switch (bp->count)
    {
        case 1:
            assert(bp->source.origin == RBO_INTERNAL || bp->source.origin == RBO_STEP);
            result = bp->source.previous;
            break;

        default:

            result = VMPA_NO_VIRTUAL;

            found = false;

            for (i = 0; i < bp->count && !found; i++)
                if (bp->sources[i].origin == RBO_INTERNAL || bp->sources[i].origin == RBO_STEP)
                {
                    result = bp->sources[i].previous;
                    found = true;
                }

            assert(found);

            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : addr = adresse à consulter.                                  *
*                bp   = point d'arrêt à consulter.                            *
*                                                                             *
*  Description : Effectue une comparaison entre adresse et point d'arrêt.     *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int compare_raw_breakpoint_with_addr(const virt_t *addr, const raw_breakpoint **bp)
{
    int result;                             /* Bilan à retourner           */

    if (*addr < (*bp)->addr)
        result = -1;

    else if (*addr == (*bp)->addr)
        result = 0;

    else
        result = 1;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = premier point d'arrêt à consulter.                       *
*                b = second point d'arrêt à consulter.                        *
*                                                                             *
*  Description : Effectue une comparaison entre deux points d'arrêt.          *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int compare_raw_breakpoints(const raw_breakpoint **a, const raw_breakpoint **b)
{
    int result;                             /* Bilan à retourner           */

    result = compare_raw_breakpoint_with_addr(&(*a)->addr, b);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bp       = point d'arrêt à manipuler.                        *
*                origin   = origine de la création du point d'arrêt.          *
*                tid      = identifiant du thread concerné.                   *
*                previous = éventuelle adresse précédent celle du point.      *
*                                                                             *
*  Description : Enregistre la source d'un point d'arrêt posé.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void set_raw_breakpoint_origin(raw_breakpoint *bp, RawBpOrigin origin, dbg_thread_id_t tid, virt_t previous)
{
#ifndef NDEBUG
    size_t i;                               /* Boucle de parcours          */
#endif
    bp_source *src;                         /* Source à définir            */
    bp_source tmp;                          /* Copie temporaire            */

#ifndef NDEBUG

    if (bp->count == 1)
        assert(bp->source.tid != tid || (bp->source.origin & origin) == 0);

    else
        for (i = 0; i < bp->count; i++)
            if (bp->source.tid == tid)
            {
                assert((bp->sources[i].origin & origin) == 0);
                break;
            }

#endif

    bp->count++;

    switch (bp->count)
    {
        case 1:
            src = &bp->source;
            break;

        case 2:
            tmp = bp->source;
            bp->sources = (bp_source *)calloc(2, sizeof(bp_source));
            bp->sources[0] = tmp;
            src = &bp->sources[1];
            break;

        default:
            bp->sources = (bp_source *)realloc(bp->sources, bp->count * sizeof(bp_source));
            src = &bp->sources[bp->count - 1];
            break;

    }

    src->origin = origin;
    src->tid = tid;
    src->previous = previous;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bp       = point d'arrêt à manipuler.                        *
*                origin   = origine de la création du point d'arrêt.          *
*                tid      = identifiant du thread concerné.                   *
*                previous = éventuelle adresse précédent celle du point.      *
*                                                                             *
*  Description : Oublie la source d'un point d'arrêt posé.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void unset_raw_breakpoint_origin(raw_breakpoint *bp, RawBpOrigin origin, dbg_thread_id_t tid)
{
    size_t i;                               /* Boucle de parcours #1       */
    bp_source tmp;                          /* Copie temporaire            */
#ifndef NDEBUG
    size_t j;                               /* Boucle de parcours #2       */
#endif

    bool has_same_origin(bp_source *src)
    {
        bool result;

        result = (src->origin == origin && src->tid == tid);

        return result;

    }

    switch (bp->count)
    {
        case 1:

            if (has_same_origin(&bp->source))
                bp->count = 0;

            break;

        case 2:

            if (has_same_origin(&bp->sources[0]))
            {
                assert(!has_same_origin(&bp->sources[1]));

                tmp = bp->sources[1];

                bp->count = 1;
                free(bp->sources);

                bp->source = tmp;

            }

            else if (has_same_origin(&bp->sources[1]))
            {
                assert(!has_same_origin(&bp->sources[0]));

                tmp = bp->sources[0];

                bp->count = 1;
                free(bp->sources);

                bp->source = tmp;

            }

            break;

        default:

            for (i = 0; i < bp->count; i++)
            {
                if (has_same_origin(&bp->sources[i]))
                {
                    if ((i + 1) < bp->count)
                        memmove(&bp->sources[i], &bp->sources[i + 1], (bp->count - i - 1) * sizeof(bp_source));

                    bp->sources = (bp_source *)realloc(bp->sources, --bp->count * sizeof(bp_source));

#ifndef NDEBUG
                    for (j = i; j < bp->count; j++)
                        assert(!has_same_origin(&bp->sources[j]));
#endif

                    break;

                }

            }

            break;

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bp     = point d'arrêt à manipuler.                          *
*                origin = origine de la création du point d'arrêt.            *
*                tid    = identifiant du thread concerné.                     *
*                                                                             *
*  Description : Indique si le point d'arrêt correspond à une source donnée.  *
*                                                                             *
*  Retour      : Bilan de l'analyse.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool has_raw_breakpoint_origin(const raw_breakpoint *bp, RawBpOrigin origin, dbg_thread_id_t tid)
{
    bool result;                            /* Conclusion à retourner      */
    size_t i;                               /* Boucle de parcours          */

    if (bp->count == 1)
        result = (bp->source.tid == tid && (bp->source.origin & origin) != 0);

    else
    {
        result = false;

        for (i = 0; i < bp->count && !result; i++)
            result = (bp->sources[i].tid == tid && (bp->sources[i].origin & origin) != 0);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bp     = point d'arrêt à manipuler.                          *
*                origin = origine de la création du point d'arrêt.            *
*                tid    = identifiant du thread concerné.                     *
*                prev   = adresse d'instruction qui a conduit à des poses.    *
*                                                                             *
*  Description : Indique si le point d'arrêt correspond à une origine donnée. *
*                                                                             *
*  Retour      : Bilan de l'analyse.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool has_raw_breakpoint_previous_address(const raw_breakpoint *bp, RawBpOrigin origin, dbg_thread_id_t tid, virt_t prev)
{
    bool result;                            /* Conclusion à retourner      */
    size_t i;                               /* Boucle de parcours          */

    if (bp->count == 1)
        result = (bp->source.tid == tid && (bp->source.origin & origin) != 0 && bp->source.previous == prev);

    else
    {
        result = false;

        for (i = 0; i < bp->count && !result; i++)
            result = (bp->sources[i].tid == tid && (bp->sources[i].origin & origin) != 0 && bp->sources[i].previous == prev);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bp = point d'arrêt à consulter.                              *
*                                                                             *
*  Description : Indique si un point d'arrêt a encore une utilité.            *
*                                                                             *
*  Retour      : true si le point peut être retiré, false sinon.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool is_breakpoint_useless(const raw_breakpoint *bp)
{
    bool result;                            /* Conclusion à faire remonter */

    result = (bp->count == 0);

    return result;

}
