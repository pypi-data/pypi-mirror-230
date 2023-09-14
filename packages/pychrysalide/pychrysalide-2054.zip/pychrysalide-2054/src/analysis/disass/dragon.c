
/* Chrysalide - Outil d'analyse de fichiers binaires
 * dragon.c - capacités apportées par la lecture du livre du dragon
 *
 * Copyright (C) 2016-2019 Cyrille Bagard
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


#include "dragon.h"


#include <assert.h>
#include <malloc.h>


#include "block.h"



/* ---------------------------- ENCAPSULATION DES NOEUDS ---------------------------- */


/* Description de noeud, en référence à "Compilers: Principles, Techniques, and Tools" */
struct _dragon_node
{
    GArchInstruction *first;                /* Arrivée d'un lien (début)   */
    GArchInstruction *last;                 /* Départ d'un lien (fin)      */

    bitfield_t *paths_bits;                 /* Masque de noeuds accessibles*/
    bitfield_t *bits;                       /* Représentation par masque   */

};


/* Définition des blocs d'allocation */
#define NODE_ALLOC_SIZE 100


/* Dénombre le nombre de noeuds présents dans une routine. */
static dragon_node *create_dragon_nodes(GArchProcessor *, const instr_coverage *, const mrange_t *, const vmpa2t *, size_t *);

/* Supprime de la mémoire tous les noeuds détectés. */
static void delete_dragon_nodes(dragon_node *, size_t);

/* Termine l'initialisation de noeuds trouvés dans une routine. */
static void init_mask_for_nodes(dragon_node *, size_t);



/* ---------------------------- ENCAPSULATION DES NOEUDS ---------------------------- */


/* Concentration de tous les efforts */
struct _dragon_knight
{
    dragon_node *nodes;                     /* Noeuds mis en place         */
    size_t count;                           /* Taille de la liste          */

};



/* ---------------------------------------------------------------------------------- */
/*                            DECOUPAGES DE CODE EN NOEUDS                            */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : proc     = ensemble d'instructions à parcourir.              *
*                coverage = zone de couverture où rechercher des instructions.*
*                range    = zone de couverture de la routine analysée.        *
*                start    = adresse du début de l'analyse.                    *
*                count    = taille de la liste de noeuds retournés. [OUT]     *
*                                                                             *
*  Description : Dénombre le nombre de noeuds présents dans une routine.      *
*                                                                             *
*  Retour      : Liste de noeuds initialisés de façon incomplète.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static dragon_node *create_dragon_nodes(GArchProcessor *proc, const instr_coverage *coverage, const mrange_t *range, const vmpa2t *start, size_t *count)
{
    dragon_node *result;                    /* Liste à créer et renvoyer   */
    size_t allocated;                       /* Dimensionnement en mémoire  */
    bool need_alloc;                        /* Besoin d'une extension ?    */
    GArchInstruction *last;                 /* Mémorisation du passé       */
    instr_iter_t *iter;                     /* Boucle de parcours          */
    GArchInstruction *instr;                /* Instruction analysée        */
    size_t scount;                          /* Nombre de liens de source   */
    bool cut;                               /* Un découpage a été réalisé ?*/
    size_t i;                               /* Boucle de parcours          */
    const instr_link_t *source;             /* Instruction de source liée  */
    dragon_node *new;                       /* Nouvel élément à créer      */
    size_t dcount;                          /* Nombre de liens de dest.    */
    const instr_link_t *dest;               /* Instruction de destination  */

    result = NULL;
    *count = 0;

    allocated = 0;
    need_alloc = true;

    iter = g_arch_processor_get_covered_iter_from_address(proc, coverage, start);
    if (iter == NULL) goto cdn_no_coverage;

    restrict_instruction_iterator(iter, range);

    for (last = NULL, instr = get_instruction_iterator_current(iter);
         instr != NULL;
         last = instr, instr = get_instruction_iterator_next(iter))
    {
        /* Découpage en blocs */

        if (need_alloc)
        {
            need_alloc = false;

            (*count)++;

            if (*count >= allocated)
            {
                allocated += NODE_ALLOC_SIZE;
                result = (dragon_node *)realloc(result, allocated * sizeof(dragon_node));
            }

            new = &result[*count - 1];

            new->first = instr;

        }

        /**
         * Il y a plusieurs raisons à la création d'un nouveau bloc :
         *
         *  - une instruction définit un saut vers une autre,
         *    et cette seconde instruction démarre donc un nouveau bloc.
         *
         *    Pour traiter ce cas, il suffit d'analyser toutes les arrivées.
         *
         *  - une instruction réalise un saut inconditionnel vers une autre.
         *    Cela se matérialise par un lien de type ILT_JUMP, ou de façon
         *    plus abstraite par un point de retour.
         *
         *    Pour traiter ce cas, on s'attache à regarder les destinations.
         */

        else
        {
            /* Analyse des sources */

            g_arch_instruction_lock_src(instr);
            scount = g_arch_instruction_count_sources(instr);

            cut = false;

            for (i = 0; i < scount && !cut; i++)
            {
                source = g_arch_instruction_get_source(instr, i);

                switch (source->type)
                {
                    case ILT_EXEC_FLOW:
                    case ILT_JUMP:
                    case ILT_CASE_JUMP:
                    case ILT_JUMP_IF_TRUE:
                    case ILT_JUMP_IF_FALSE:

                        result[*count - 1].last = last;

                        (*count)++;
                        i = scount;

                        if (*count >= allocated)
                        {
                            allocated += NODE_ALLOC_SIZE;
                            result = (dragon_node *)realloc(result, allocated * sizeof(dragon_node));
                        }

                        new = &result[*count - 1];

                        new->first = instr;

                        cut = true;

                        break;

                    default:
                        break;

                }

                unref_instr_link(source);

            }

            g_arch_instruction_unlock_src(instr);

        }

        /* Analyse des destinations */

        g_arch_instruction_lock_dest(instr);
        dcount = g_arch_instruction_count_destinations(instr);

        cut = false;

        for (i = 0; i < dcount && !cut; i++)
        {
            dest = g_arch_instruction_get_destination(instr, i);

            switch (dest->type)
            {
                case ILT_JUMP:

                    result[*count - 1].last = instr;

                    cut = true;

                    need_alloc = true;

                    break;

                default:
                    break;

            }

            unref_instr_link(dest);

        }

        g_arch_instruction_unlock_dest(instr);

        if (!need_alloc && g_arch_instruction_get_flags(instr) & AIF_RETURN_POINT)
        {
            result[*count - 1].last = instr;

            need_alloc = true;

        }

        g_object_unref(G_OBJECT(instr));

    }

    if (*count > 0)
        result[*count - 1].last = last;

    delete_instruction_iterator(iter);

 cdn_no_coverage:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : nodes = liste de noeuds détectés dans une routine.           *
*                count = taille de cette liste de noeuds à traiter.           *
*                                                                             *
*  Description : Supprime de la mémoire tous les noeuds détectés.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void delete_dragon_nodes(dragon_node *nodes, size_t count)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < count; i++)
    {
        delete_bit_field(nodes[i].paths_bits);
        delete_bit_field(nodes[i].bits);
    }

    free(nodes);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : nodes = liste de noeuds détectés dans une routine.           *
*                count = taille de cette liste de noeuds à traiter.           *
*                                                                             *
*  Description : Termine l'initialisation de noeuds trouvés dans une routine. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void init_mask_for_nodes(dragon_node *nodes, size_t count)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < count; i++)
    {
        nodes[i].paths_bits = create_bit_field(count, false);
        nodes[i].bits = create_bit_field(count, i > 0);
    }

    set_in_bit_field(nodes[0].bits, 0, 1);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node  = noeud de code à considérer.                          *
*                first = instruction de départ à renseigner ou NULL. [OUT]    *
*                last  = instruction d'arrivée à renseigner ou NULL. [OUT]    *
*                                                                             *
*  Description : Fournit les instructions bornant un noeud de code.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void get_dragon_node_bounding_instructions(dragon_node *node, GArchInstruction **first, GArchInstruction **last)
{
    if (first != NULL)
        *first = node->first;

    if (last != NULL)
        *last = node->last;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : nodes = liste de noeuds détectés dans une routine.           *
*                                                                             *
*  Description : Fournit un noeud particulier à partir d'une liste.           *
*                                                                             *
*  Retour      : Noeud ciblé.                                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

dragon_node *get_dragon_node(dragon_node *nodes, size_t index)
{
    return nodes + index;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : nodes = liste de noeuds détectés dans une routine.           *
*                node  = noeud ciblé au sein de cette liste.                  *
*                                                                             *
*  Description : Fournit l'indice d'un noeud particulier à partir d'une liste.*
*                                                                             *
*  Retour      : Indice du noeud ciblé.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t get_dragon_node_index(dragon_node *nodes, dragon_node *node)
{
    return node - nodes;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : nodes = liste de noeuds détectés dans une routine.           *
*                count = taille de cette liste de noeuds à parcourir.         *
*                final = précise si l'instruction visée est la première.      *
*                instr = instruction à retrouver en tant que début de noeud.  *
*                                                                             *
*  Description : Recherche un noeud selon son intruction de départ.           *
*                                                                             *
*  Retour      : Noeud trouvé ou NULL si aucune trouvaille.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

dragon_node *find_node_for_instruction(dragon_node *nodes, size_t count, bool final, const GArchInstruction *instr)
{
    dragon_node *result;                    /* Résultat des recherches     */
    const mrange_t *irange;                 /* Emplacement d'instruction   */

    int find_node_from_range(const mrange_t *range, const dragon_node *node)
    {
        int status;                         /* Bilan à retourner           */
        const mrange_t *nrange;             /* Emplacement de noeud        */

        nrange = g_arch_instruction_get_range(final ? node->last : node->first);

        status = cmp_mrange(range, nrange);

        return status;

    }

    irange = g_arch_instruction_get_range(instr);

    result = bsearch(irange, nodes, count, sizeof(dragon_node), (__compar_fn_t)find_node_from_range);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : nodes = liste de noeuds détectés dans une routine.           *
*                count = taille de cette liste de noeuds à traiter.           *
*                                                                             *
*  Description : Marque tous les noeuds accessibles pour chaque noeud de code.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : Les chemins issus de boucles ne sont pas pris en compte.     *
*                On cherche à construire une hiérarchie, pas une réalité.     *
*                                                                             *
******************************************************************************/

void compute_all_paths(dragon_node *nodes, size_t count)
{
    void follow_flow_in_nodes(dragon_node *node)
    {
        size_t dcount;                      /* Nombre de liens de dest.    */
        size_t i;                           /* Boucle de parcours          */
        const instr_link_t *dest;           /* Instructions de destination */
        dragon_node *next;                  /* Noeud suivant dans le code  */
        size_t id;                          /* Indice du bit associé       */

        g_arch_instruction_lock_dest(node->last);
        dcount = g_arch_instruction_count_destinations(node->last);

        for (i = 0; i < dcount; i++)
        {
            dest = g_arch_instruction_get_destination(node->last, i);

            switch (dest->type)
            {
                case ILT_EXEC_FLOW:
                case ILT_JUMP:
                case ILT_CASE_JUMP:
                case ILT_JUMP_IF_TRUE:
                case ILT_JUMP_IF_FALSE:

                    next = find_node_for_instruction(nodes, count, false, dest->linked);
                    if (next == NULL) break;

                    id = get_dragon_node_index(nodes, next);
                    set_in_bit_field(node->paths_bits, id, 1);

                    follow_flow_in_nodes(next);
                    or_bit_field(node->paths_bits, next->paths_bits);

                    break;

                default:
                    break;

            }

            unref_instr_link(dest);

        }

        g_arch_instruction_unlock_dest(node->last);

    }

    follow_flow_in_nodes(&nodes[0]);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node = noeud représentant une portion de code à consulter.   *
*                                                                             *
*  Description : Fournit la liste des noeuds accessibles depuis un autre.     *
*                                                                             *
*  Retour      : Champ de bits en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const bitfield_t *get_paths_bits(const dragon_node *node)
{
    return node->paths_bits;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : nodes = liste de noeuds détectés dans une routine.           *
*                count = taille de cette liste de noeuds à traiter.           *
*                                                                             *
*  Description : Détermine toute la chaîne hiérarchique de domination.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void compute_all_dominators(dragon_node *nodes, size_t count)
{
    bitfield_t *inter;                      /* Intersection de dominations */
    bool changed;                           /* Note un changement qq part  */
    size_t k;                               /* Boucle de parcours #1       */
    dragon_node *node;                      /* Noeud à traiter             */
    dragon_node *predecessor;               /* Noeud prédécesseur direct   */
    size_t scount;                          /* Nombre de liens de source   */
    size_t i;                               /* Boucle de parcours #2       */
    const instr_link_t *source;             /* Instruction d'origine       */

    inter = create_bit_field(count, false);

    do
    {
        changed = false;

        for (k = 1; k < count; k++)
        {
            node = &nodes[k];

            set_all_in_bit_field(inter);

            g_arch_instruction_lock_src(node->first);
            scount = g_arch_instruction_count_sources(node->first);
            //assert(scount > 0); // un 'ret' coupe, le suivant n'a pas de source

            for (i = 0; i < scount; i++)
            {
                source = g_arch_instruction_get_source(node->first, i);

                switch (source->type)
                {
                    case ILT_EXEC_FLOW:
                    case ILT_JUMP:
                    case ILT_CASE_JUMP:
                    case ILT_JUMP_IF_TRUE:
                    case ILT_JUMP_IF_FALSE:

                        predecessor = find_node_for_instruction(nodes, count, true, source->linked);

                        if (predecessor != NULL)
                            and_bit_field(inter, predecessor->bits);

                        break;

                    default:
                        break;

                }

                unref_instr_link(source);

            }

            g_arch_instruction_unlock_src(node->first);

            set_in_bit_field(inter, k, 1);

            if (compare_bit_fields(node->bits, inter) != 0)
            {
                copy_bit_field(node->bits, inter);
                changed = true;
            }

        }

    }
    while (changed);

    delete_bit_field(inter);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node = noeud représentant une portion de code à consulter.   *
*                                                                             *
*  Description : Fournit la liste des noeuds dominés par un noeud.            *
*                                                                             *
*  Retour      : Champ de bits en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const bitfield_t *get_domination_bits(const dragon_node *node)
{
    return node->bits;

}



/* ---------------------------------------------------------------------------------- */
/*                              ENCAPSULATION DES NOEUDS                              */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : proc     = ensemble d'instructions à parcourir.              *
*                coverage = zone de couverture où rechercher des instructions.*
*                range    = zone de couverture de la routine analysée.        *
*                start    = adresse du début de l'analyse.                    *
*                                                                             *
*  Description : Attaque la complexité d'un code en créant des noeuds.        *
*                                                                             *
*  Retour      : Définition d'un complexe de noeuds établis.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

dragon_knight *begin_dragon_knight(GArchProcessor *proc, const instr_coverage *coverage, const mrange_t *range, const vmpa2t *start)
{
    dragon_knight *result;                  /* Données à retourner         */
    dragon_node *nodes;                     /* Noeuds mis en place         */
    size_t count;                           /* Nombre de ces noeuds        */

    result = NULL;

    nodes = create_dragon_nodes(proc, coverage, range, start, &count);

    if (nodes != NULL)
    {
        init_mask_for_nodes(nodes, count);

        result = (dragon_knight *)calloc(1, sizeof(dragon_knight));

        result->nodes = nodes;
        result->count = count;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : knight = données représentant une complexité traitée.        *
*                                                                             *
*  Description : Supprime de la mémoire les données d'une complexité de code. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void end_dragon_knight(dragon_knight *knight)
{
    delete_dragon_nodes(knight->nodes, knight->count);

    free(knight);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : knight = données représentant une complexité à considérer.   *
*                nodes  = noeuds de code associés à récupérer ou NULL. [OUT]  *
*                count  = taille de cette liste de noeuds ou NULL. [OUT]      *
*                                                                             *
*  Description : Fournit les éléments utiles à un traitement de blocs de code.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void get_dragon_knight_content(const dragon_knight *knight, dragon_node **nodes, size_t *count)
{
    if (nodes != NULL) *nodes = knight->nodes;
    if (count != NULL) *count = knight->count;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : knight = données représentant une complexité à considérer.   *
*                                                                             *
*  Description : Fournit un noeud particulier à partir d'une liste.           *
*                                                                             *
*  Retour      : Noeud ciblé.                                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

dragon_node *get_dragon_knight_node(const dragon_knight *knight, size_t index)
{
    assert(index < knight->count);

    return knight->nodes + index;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : knight = données représentant une complexité à considérer.   *
*                node   = noeud ciblé au sein de cette liste.                 *
*                                                                             *
*  Description : Fournit l'indice d'un noeud particulier à partir d'une liste.*
*                                                                             *
*  Retour      : Indice du noeud ciblé.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t get_dragon_knight_node_index(const dragon_knight *knight, dragon_node *node)
{
    size_t result;                          /* Indice à retourner          */

    result = (node - knight->nodes);

    assert(result < knight->count);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : knight = données représentant une complexité à considérer.   *
*                final = précise si l'instruction visée est la première.      *
*                instr = instruction à retrouver en tant que début de noeud.  *
*                                                                             *
*  Description : Recherche un noeud selon son intruction de départ.           *
*                                                                             *
*  Retour      : Noeud trouvé ou NULL si aucune trouvaille.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

dragon_node *find_knight_node_for_instruction(const dragon_knight *knight, bool final, const GArchInstruction *instr)
{
    dragon_node *result;                    /* Résultat des recherches     */

    result = find_node_for_instruction(knight->nodes, knight->count, final, instr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : knight = rassemblement des complexités de code.              *
*                binary = binaire contenant l'ensemble des instructions.      *
*                                                                             *
*  Description : Traduit une complexité de noeuds en liste de blocs basiques. *
*                                                                             *
*  Retour      : Liste de blocs basiques créés.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBlockList *translate_dragon_knight(const dragon_knight *knight, GLoadedBinary *binary)
{
    GBlockList *result;                     /* Liste à retourner           */
    dragon_node *nodes;                     /* Liste des noeuds détectés   */
    size_t count;                           /* Taille de cette liste       */
    size_t i;                               /* Boucle de parcours          */
    dragon_node *node;                      /* Noeud à traiter             */
    GArchInstruction *first;                /* Première instruction        */
    GArchInstruction *last;                 /* Dernière instruction        */
    GCodeBlock *block;                      /* Nouveau bloc basique        */

    get_dragon_knight_content(knight, &nodes, &count);

    compute_all_dominators(nodes, count);

    result = g_block_list_new(count);

    for (i = 0; i < count; i++)
    {
        node = get_dragon_node(nodes, i);

        get_dragon_node_bounding_instructions(node, &first, &last);

        block = g_basic_block_new(binary, first, last, node->bits);

        g_block_list_add_block(result, block, i);

    }

    return result;

}
