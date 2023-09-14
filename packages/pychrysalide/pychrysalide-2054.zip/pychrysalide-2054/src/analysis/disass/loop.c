
/* Chrysalide - Outil d'analyse de fichiers binaires
 * loop.c - détection des boucles dans du code machine
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


#include "loop.h"


#include <assert.h>
#include <malloc.h>


#include "block.h"



/**
 * Adaptation de l'algorithme : "A New Algorithm for Identifying Loops in Decompilation".
 */



/* Informations associées à un bloc */
typedef struct _bblock_info_t
{
    bool traversed;                         /* Etat du traitement          */
    unsigned int dfsp_pos;                  /* Indice dans un chemin       */
    struct _bblock_info_t *iloop_header;    /* Pointeur de bloc d'entête   */

    bool irreducible;                       /* Détection d'irreducible     */

} bblock_info_t;

/* Informations associées à un lien */
typedef struct _bblock_link_t
{
    GCodeBlock *linked;                     /* Destination du bloc visé    */
    InstructionLinkType type;               /* Type de liaison             */
    bblock_info_t *info;                    /* Informations sur ce bloc    */

} bblock_link_t;


/* Détermine les liens vers des blocs successeurs d'un bloc. */
static bblock_link_t *get_block_links(GCodeBlock *, bblock_info_t *, bool, size_t *);

#define get_block_predecessors(b, i, c) \
    get_block_links(b, i, false, c)

#define get_block_successors(b, i, c) \
    get_block_links(b, i, true, c)

/* Libère de la mémoire les liens vers des blocs successeurs. */
static void delete_block_links(bblock_link_t *, size_t);

/* Marque un bloc comme étant un entête de boucle. */
static void tag_loop_head(bblock_info_t *, bblock_info_t *);

/* Parcourt une arborescence de blocs à la recherche de boucles. */
static bblock_info_t *traverse_basic_blocks_dfs(bblock_info_t *, GBlockList *, bblock_info_t *, unsigned int);

/* Indique si une boucle doit être définie. */
static bool _should_be_natural_loop_link(bblock_info_t *, bblock_info_t *);

/* Indique si une boucle doit être définie. */
static bool should_be_natural_loop_link(bblock_info_t *, bblock_info_t *);

/* Définit les boucles entre un ensemble de blocs basiques. */
static void define_basic_blocks_loops(GBlockList *list, bblock_info_t *);



/******************************************************************************
*                                                                             *
*  Paramètres  : block = bloc de code, basique, à considérer.                 *
*                info  = informations complémentaires quant aux blocs.        *
*                succ  = true si les successeurs sont visés, false sinon.     *
*                count = nombre de liens effectivement utiles. [OUT]          *
*                                                                             *
*  Description : Détermine les liens vers des blocs successeurs d'un bloc.    *
*                                                                             *
*  Retour      : Liste de liens retrouvés ou NULL si vraiment aucun.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bblock_link_t *get_block_links(GCodeBlock *block, bblock_info_t *info, bool succ, size_t *count)
{
    bblock_link_t *result;                  /* Liste à retourner           */
    size_t allocated;                       /* Nombre d'éléments au maximum*/
    block_link_t *links;                    /* Liens associés au bloc      */
    size_t i;                               /* Boucle de parcours          */
    bblock_link_t *new;                     /* Mémorisation de ce lien     */

    if (succ)
        links = g_code_block_get_destinations(block, &allocated);
    else
        links = g_code_block_get_sources(block, &allocated);

    result = malloc(allocated * sizeof(bblock_link_t));

    *count = 0;

    for (i = 0; i < allocated; i++)
    {
        switch (links[i].type)
        {
            case ILT_EXEC_FLOW:
            case ILT_JUMP:
            case ILT_CASE_JUMP:
            case ILT_JUMP_IF_TRUE:
            case ILT_JUMP_IF_FALSE:

                new = &result[(*count)++];

                new->linked = links[i].linked;
                g_object_ref(G_OBJECT(new->linked));

                new->type = links[i].type;

                new->info = info + g_code_block_get_index(new->linked);

                break;

            default:
                break;

        }

        unref_block_link(&links[i]);

    }

    if (links != NULL)
        free(links);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : links = liste de liens retrouvés ou NULL si vraiment aucun.  *
*                count = nombre de liens effectivement utiles.                *
*                                                                             *
*  Description : Libère de la mémoire les liens vers des blocs successeurs.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void delete_block_links(bblock_link_t *links, size_t count)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < count; i++)
        g_object_unref(G_OBJECT(links[i].linked));

    if (links != NULL)
        free(links);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : blk = bloc à mettre à jour.                                  *
*                hdr = bloc d'entête à mémoriser.                             *
*                                                                             *
*  Description : Marque un bloc comme étant un entête de boucle.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void tag_loop_head(bblock_info_t *blk, bblock_info_t *hdr)
{
    bblock_info_t *cur1;                    /* Boucle de parcours #1       */
    bblock_info_t *cur2;                    /* Boucle de parcours #2       */
    bblock_info_t *ih;                      /* Boucle de parcours #3       */

    if (blk == hdr || hdr == NULL)
        goto done;

    cur1 = blk;
    cur2 = hdr;

    while (cur1->iloop_header != NULL)
    {
        ih = cur1->iloop_header;

        if (ih == cur2)
            goto done;

        if (ih->dfsp_pos < cur2->dfsp_pos)
        {
            cur1->iloop_header = cur2;
            cur1 = cur2;
            cur2 = ih;
        }

        else
            cur1 = ih;

    }

    cur1->iloop_header = cur2;

 done:

    ;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : root = élément racine à considérer.                          *
*                list = liste de blocs de code à consulter.                   *
*                info = informations complémentaires quant aux blocs.         *
*                pos  = position dans le chemin courant.                      *
*                                                                             *
*  Description : Parcourt une arborescence de blocs à la recherche de boucles.*
*                                                                             *
*  Retour      : Entête de boucle trouvée ou NULL.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bblock_info_t *traverse_basic_blocks_dfs(bblock_info_t *root, GBlockList *list, bblock_info_t *info, unsigned int pos)
{
    GCodeBlock *block;                      /* Bloc basique courant        */
    bblock_link_t *links;                   /* Liste de successeurs        */
    size_t count;                           /* Taille de cette liste       */
    size_t i;                               /* Boucle de parcours          */
    bblock_info_t *succ;                    /* Successeur à traiter        */
    bblock_info_t *nh;                      /* Nouvel entête de boucle     */
    bblock_info_t *h;                       /* Entête de boucle            */

    root->traversed = true;
    root->dfsp_pos = pos;

    block = g_block_list_get_block(list, root - info);

    links = get_block_successors(block, info, &count);

    for (i = 0; i < count; i++)
    {
        succ = links[i].info;

        /* Cas A : bloc jamais traversé */
        if (!succ->traversed)
        {
            nh = traverse_basic_blocks_dfs(succ, list, info, pos + 1);
            tag_loop_head(root, nh);
        }

        else
        {
            /* Le successeur est dans DFSP(root) */
            if (succ->dfsp_pos > 0)
            {
                /* Cas B : on le marque en tant qu'entête de boucle */
                tag_loop_head(root, succ);
            }

            /* Cas C : on ne fait rien */
            else if (succ->iloop_header == NULL)
            {

            }

            else
            {
                h = succ->iloop_header;

                /* h est dans DFSP(root) */
                if (h->dfsp_pos > 0)
                {
                    /* Cas D */
                    tag_loop_head(root, h);
                }

                /* h n'est pas dans DFSP(root) */
                else
                {
                    /* Cas E : réentrance */

                    succ->irreducible = true;

                    while (h->iloop_header != NULL)
                    {
                        h = h->iloop_header;

                        /* h est dans DFSP(root) */
                        if (h->dfsp_pos > 0)
                        {
                            tag_loop_head(root, h);
                            break;
                        }

                    }

                }

            }

        }

    }

    delete_block_links(links, count);

    g_object_unref(G_OBJECT(block));

    /* Efface la position du bloc courant dans le chemin */
    root->dfsp_pos = 0;

    return root->iloop_header;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dest   = informations du bloc de destination.                *
*                header = informations de l'entête de boucle.                 *
*                                                                             *
*  Description : Indique si une boucle doit être définie.                     *
*                                                                             *
*  Retour      : true si une boucle naturelle est bien présente.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool _should_be_natural_loop_link(bblock_info_t *dest, bblock_info_t *header)
{
    bool result;                            /* Conclusion à retourner      */

    result = (dest == header);

    if (!result && header != NULL)
        result = _should_be_natural_loop_link(dest, header->iloop_header);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dest   = informations du bloc de destination.                *
*                header = informations de l'entête de boucle.                 *
*                                                                             *
*  Description : Indique si une boucle doit être définie.                     *
*                                                                             *
*  Retour      : true si une boucle naturelle est bien présente.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool should_be_natural_loop_link(bblock_info_t *dest, bblock_info_t *header)
{
    bool result;                            /* Conclusion à retourner      */

    result = _should_be_natural_loop_link(dest, header);

    if (!result && dest->iloop_header != NULL)
        result = should_be_natural_loop_link(dest->iloop_header, header);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list = liste de blocs de code à consulter.                   *
*                info = informations complémentaires quant aux blocs.         *
*                                                                             *
*  Description : Définit les boucles entre un ensemble de blocs basiques.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void define_basic_blocks_loops(GBlockList *list, bblock_info_t *info)
{
    size_t available;                       /* Quantité de blocs présents  */
    size_t i;                               /* Boucle de parcours #1       */
    bblock_info_t *iter;                    /* Boucle de parcours #2       */
    GCodeBlock *block;                      /* Bloc basique courant        */
    bblock_link_t *links;                   /* Liste de successeurs        */
    size_t count;                           /* Taille de cette liste       */
    size_t k;                               /* Boucle de parcours #3       */
    GArchInstruction *first;                /* Instruction initiale de bloc*/
    GArchInstruction *last;                 /* Instruction finale de bloc  */
#ifndef NDEBUG
    bool status;                            /* Bilan du changement         */
#endif

    available = g_block_list_count_blocks(list);

    for (i = 0, iter = info; i < available; i++, iter++)
    {
        block = g_block_list_get_block(list, i);

        if (iter->irreducible)
        {
            links = get_block_predecessors(block, info, &count);

            for (k = 0; k < count; k++)
                if (should_be_natural_loop_link(iter->iloop_header, links[k].info->iloop_header)
                    /**
                     * Il se peut qu'un bloc fasse référence à lui même !
                     *
                     * Cf. tests/analysis/disass/jinit_color_converter.bin
                     *
                     * On évite ici une boucle sans fin en officialisant cette boucle.
                     */
                    || links[k].info == iter->iloop_header)
                {
                    g_basic_block_get_boundaries(G_BASIC_BLOCK(links[k].linked), NULL, &last);
                    g_basic_block_get_boundaries(G_BASIC_BLOCK(block), &first, NULL);

                    g_arch_instruction_lock_dest(last);

#ifndef NDEBUG
                    status = g_arch_instruction_change_link(last, first, links[k].type, ILT_LOOP);
                    assert(status);
#else
                    g_arch_instruction_change_link(last, first, links[k].type, ILT_LOOP);
#endif

                    g_arch_instruction_unlock_dest(last);

                    g_object_unref(G_OBJECT(first));
                    g_object_unref(G_OBJECT(last));

                }

        }

        else
        {
            links = get_block_successors(block, info, &count);

            for (k = 0; k < count; k++)
                if (_should_be_natural_loop_link(links[k].info, iter->iloop_header)
                    /**
                     * Il se peut qu'un bloc fasse référence à lui même !
                     *
                     * Cf. tests/analysis/disass/selfloop.c
                     *
                     * On évite ici une boucle sans fin en officialisant cette boucle.
                     */
                    || links[k].info == iter)
                {
                    g_basic_block_get_boundaries(G_BASIC_BLOCK(block), NULL, &last);
                    g_basic_block_get_boundaries(G_BASIC_BLOCK(links[k].linked), &first, NULL);

                    g_arch_instruction_lock_dest(last);

#ifndef NDEBUG
                    status = g_arch_instruction_change_link(last, first, links[k].type, ILT_LOOP);
                    assert(status);
#else
                    g_arch_instruction_change_link(last, first, links[k].type, ILT_LOOP);
#endif

                    g_arch_instruction_unlock_dest(last);

                    g_object_unref(G_OBJECT(first));
                    g_object_unref(G_OBJECT(last));

                }

        }

        delete_block_links(links, count);

        g_object_unref(G_OBJECT(block));

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list = liste de blocs de code à consulter.                   *
*                                                                             *
*  Description : Détecte les boucles dans du code machine.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void detect_loops_in_basic_blocks(GBlockList *list)
{
    size_t count;                           /* Quantité de blocs présents  */
    bblock_info_t *info;                    /* Informations supplémentaires*/

    count = g_block_list_count_blocks(list);

    /**
     * Un premier jet consistait à filtrer sur le nombre de blocs : s'il n'y
     * en avait qu'un, il n'y avait à priori pas de raison de rechercher des
     * boucles !
     *
     * Mais c'était sans compter une routine se résumant à une boucle infinie...
     *
     * C'est par exemple le cas avec la fonction operator new[] (_ZnajRKSt9nothrow_t)
     * de l'échantillon b6990fc6913d839809c72d1d482cb2c295c4840fc6a1f40f38923464e958ffae.
     */

    info = calloc(count, sizeof(bblock_info_t));

    traverse_basic_blocks_dfs(&info[0], list, info, 1);

    define_basic_blocks_loops(list, info);

    free(info);

}
