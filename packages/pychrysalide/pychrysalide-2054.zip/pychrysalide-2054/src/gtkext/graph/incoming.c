
/* Chrysalide - Outil d'analyse de fichiers binaires
 * incoming.c - liens entrants d'un bloc de code dans une représentation graphique
 *
 * Copyright (C) 2019 Cyrille Bagard
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


#include "incoming.h"


#include <malloc.h>


#include "leaving.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : owner = propriétaire du bloc de rattachement.                *
*                type  = type de lien simple attendu.                         *
*                other = point de départ du lien formé.                       *
*                                                                             *
*  Description : Crée un point d'attache pour un lien entrant simple.         *
*                                                                             *
*  Retour      : Structure mise en place.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

incoming_link_t *create_incoming_link(GGraphCluster *owner, InstructionLinkType type, leaving_link_t *other)
{
    incoming_link_t *result;                /* Structure à retourner       */
    GCodeBlock *src;                        /* Bloc d'origine du lien      */
    GCodeBlock *dst;                        /* Bloc de destination du lien */

    result = malloc(sizeof(incoming_link_t));

    result->owner = owner;

    result->type = type;

    src = g_graph_cluster_get_block(other->owner);
    dst = g_graph_cluster_get_block(owner);

    if (type == ILT_JUMP_IF_TRUE)
        result->edge = g_graph_edge_new_true(src, dst,
                                             &other->start[0], &other->start[1],
                                             &result->end[0], &result->end[1]);

    else if (type == ILT_JUMP_IF_FALSE)
        result->edge = g_graph_edge_new_false(src, dst,
                                              &other->start[0], &other->start[1],
                                              &result->end[0], &result->end[1]);

    else
        result->edge = g_graph_edge_new(src, dst,
                                        &other->start[0], &other->start[1],
                                        &result->end[0], &result->end[1]);

    g_object_unref(G_OBJECT(src));
    g_object_unref(G_OBJECT(dst));

    result->other = other;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : owner = propriétaire du bloc de rattachement.                *
*                other = point de départ du lien formé.                       *
*                                                                             *
*  Description : Crée un point d'attache pour un lien entrant de boucle.      *
*                                                                             *
*  Retour      : Structure mise en place.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

incoming_link_t *create_incoming_loop_link(GGraphCluster *owner, const GdkPoint *midpts, leaving_link_t *other)
{
    incoming_link_t *result;                /* Structure à retourner       */
    GCodeBlock *src;                        /* Bloc d'origine du lien      */
    GCodeBlock *dst;                        /* Bloc de destination du lien */

    result = malloc(sizeof(incoming_link_t));

    result->owner = owner;

    result->type = ILT_LOOP;

    src = g_graph_cluster_get_block(other->owner);
    dst = g_graph_cluster_get_block(owner);

    result->edge = g_graph_edge_new_loop(src, dst,
                                         &other->start[0], &other->start[1],
                                         &midpts[0], &midpts[1],
                                         &result->end[0], &result->end[1]);

    g_object_unref(G_OBJECT(src));
    g_object_unref(G_OBJECT(dst));

    result->other = other;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : link = structure à libérer de la mémoire.                    *
*                                                                             *
*  Description : Détruit un point d'attache pour un lien entrant.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void delete_incoming_link(incoming_link_t *link)
{
    free(link);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = premier lien entrant à comparer.                         *
*                b = second lien entrant à comparer.                          *
*                                                                             *
*  Description : Compare deux liens entrants.                                 *
*                                                                             *
*  Retour      : Bilan de comparaison.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int cmp_incoming_links(const incoming_link_t **a, const incoming_link_t **b)
{
    int result;                             /* Bilan à retourner           */
    gint pos_a;                             /* Point de départ pour A      */
    gint pos_b;                             /* Point de départ pour B      */

    pos_a = compute_leaving_link_position((*a)->other);

    pos_b = compute_leaving_link_position((*b)->other);

    if (pos_a < pos_b)
        result = -1;

    else if (pos_a > pos_b)
        result = 1;

    else
        result = 0;

    return result;

}
