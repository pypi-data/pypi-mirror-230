
/* Chrysalide - Outil d'analyse de fichiers binaires
 * rank.c - classement des blocs d'instructions
 *
 * Copyright (C) 2013-2019 Cyrille Bagard
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


#include "rank.h"


#include <assert.h>



/* Classe les blocs basiques d'une routine. */
void rank_routine_block(const GBlockList *, GCodeBlock *);



/******************************************************************************
*                                                                             *
*  Paramètres  : list  = ensemble de blocs basiques à traiter.                *
*                block = bloc d'analyse courant.                              *
*                                                                             *
*  Description : Classe les blocs basiques d'une routine.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void rank_routine_block(const GBlockList *list, GCodeBlock *block)
{
    size_t next;                            /* Rang suivant obtenu         */
    size_t dcount;                          /* Nombre de liens de dest.    */
    block_link_t *links;                    /* Liens associés au bloc      */
    size_t i;                               /* Boucle de parcours          */
    block_link_t *dest;                     /* Bloc visé par un autre      */
    InstructionLinkType type;               /* Raccourci pour confort      */
    unsigned int rank;                      /* Rang à constituer           */

    next = g_code_block_get_rank(block) + 1;

    links = g_code_block_get_destinations(block, &dcount);

    for (i = 0; i < dcount; i++)
    {
        dest = &links[i];

        type = dest->type;

        /* La boucle de remontée n'abaisse pas les rangs */
        if (type == ILT_LOOP) goto next_dest;

        /**
         * On se doit de suivre le même cheminement que celui emprunté lors
         * du parcours de create_dragon_nodes().
         * Sinon, les chemins divergent et une récursion infinie peut survenir.
         */
        if (type != ILT_EXEC_FLOW
            && type != ILT_JUMP
            && type != ILT_CASE_JUMP
            && type != ILT_JUMP_IF_TRUE
            && type != ILT_JUMP_IF_FALSE)
            goto next_dest;

        rank = g_code_block_get_rank(dest->linked);

        if (next > rank || rank == -1)
        {
            g_code_block_set_rank(dest->linked, next);

            rank_routine_block(list, dest->linked);

        }

 next_dest:

        unref_block_link(dest);

    }

    if (links != NULL)
        free(links);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : routine = routine regroupant les blocs à traiter.            *
*                                                                             *
*  Description : Classe les blocs des routines.                               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void rank_routine_blocks(GBinRoutine *routine)
{
    GBlockList *blocks;                     /* Ensemble des blocs d'instr. */
    GCodeBlock *start;                      /* Bloc basique de départ      */

    blocks = g_binary_routine_get_basic_blocks(routine);

    start = g_block_list_get_block(blocks, 0);
    assert(start != NULL);

    g_code_block_set_rank(start, 0);

    rank_routine_block(blocks, start);

    g_object_unref(G_OBJECT(start));

    g_object_unref(G_OBJECT(blocks));

}
