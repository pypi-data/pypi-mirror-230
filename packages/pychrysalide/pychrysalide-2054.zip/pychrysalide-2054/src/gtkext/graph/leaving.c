
/* Chrysalide - Outil d'analyse de fichiers binaires
 * leaving.c - liens sortants d'un bloc de code dans une représentation graphique
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


#include "leaving.h"


#include <assert.h>
#include <malloc.h>


#include "cluster-int.h"
#include "incoming.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : owner = propriétaire du bloc de rattachement.                *
*                index = indice dans les liens de sortie.                     *
*                                                                             *
*  Description : Crée un point d'attache pour un lien sortant.                *
*                                                                             *
*  Retour      : Structure mise en place.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

leaving_link_t *create_leaving_link(GGraphCluster *owner, size_t index)
{
    leaving_link_t *result;                 /* Structure à retourner       */

    result = malloc(sizeof(leaving_link_t));

    result->owner = owner;

    result->index = index;

    result->straight = false;
    result->forced_straight = false;
    result->straight_level = SIZE_MAX;
    result->cluster_exit = false;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : link = structure à libérer de la mémoire.                    *
*                                                                             *
*  Description : Détruit un point d'attache pour un lien sortant.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void delete_leaving_link(leaving_link_t *link)
{
    free(link);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : link = information sur un lien à consulter.                  *
*                                                                             *
*  Description : Calcule l'abscisse d'un lien à son départ d'un bloc.         *
*                                                                             *
*  Retour      : Abscisse à attribuer à un départ de lien.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

gint compute_leaving_link_position(const leaving_link_t *link)
{
    gint result;                            /* Position à retourner        */

    result = g_graph_cluster_compute_leaving_link_position(link->owner, link->index);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : link = information sur un lien à consulter.                  *
*                x1   = abscisse de départ du lien d'origine.                 *
*                max  = ordonnée la plus profonde à ne pas dépasser.          *
*                                                                             *
*  Description : Détermine une direction prise par un lien à son départ.      *
*                                                                             *
*  Retour      : Direction prise à l'écran.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

LeavingLinkDir get_leaving_link_direction(const leaving_link_t *link, gint x1, gint max)
{
    LeavingLinkDir result;                  /* Préférence à retourner      */
    GGraphCluster *owner;                   /* Raccourci vers le proprio   */
    GtkAllocation alloc;                    /* Emplacement reservé         */
    gint x2;                                /* Abscisse d'arrivée de lien  */

    owner = link->other->owner;

    g_graph_cluster_get_allocation(owner, &alloc);

    if (alloc.y > max)
        result = LLD_NO_PREF;

    else
    {
        result = g_graph_cluster_get_link_direction(owner, x1, max);

        if (result == LLD_NO_PREF)
        {
            /**
             * Les liens ne sont pas encore ordonnés avec leur indice final.
             * Donc on choisit de faire au plus simple, et donc au plus rapide.
             *
             * Une alternative viable, mais tout aussi imprécise, serait d'appeler :
             *
             *    idx = g_graph_cluster_find_incoming_link(owner, link);
             *
             *    x2 = g_graph_cluster_compute_incoming_link_position(owner, idx);
             */

            x2 = alloc.x + alloc.width / 2;

            if (x1 < x2)
                result = LLD_TO_RIGHT;

            else if (x1 > x2)
                result = LLD_TO_LEFT;

            else
                result = LLD_NO_PREF;

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a    = premier lien entrant à comparer.                      *
*                b    = second lien entrant à comparer.                       *
*                info = compléments d'information pour l'opération.           *
*                                                                             *
*  Description : Compare deux liens sortants.                                 *
*                                                                             *
*  Retour      : Bilan de comparaison.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int cmp_leaving_links(const leaving_link_t **a, const leaving_link_t **b, const leaving_cmp_info_t *info)
{
    int result;                             /* Bilan à retourner           */
    GGraphCluster *owner;                   /* Raccourci vers le proprio   */
    gint pos_a;                             /* Point de départ pour A      */
    GtkAllocation alloc;                    /* Emplacement de cluster      */
    gint pos_b;                             /* Point de départ pour B      */

    /* Calcul des ordonnées des points de chute */

    owner = (*a)->other->owner;

    pos_a = G_MAXINT;

    if (!g_graph_cluster_compute_min_y_target((*a)->other->owner, info->root, &pos_a))
    {
        g_graph_cluster_get_allocation(owner, &alloc);

        pos_a = alloc.y;

    }

    owner = (*b)->other->owner;

    pos_b = G_MAXINT;

    if (!g_graph_cluster_compute_min_y_target((*b)->other->owner, info->root, &pos_b))
    {
        g_graph_cluster_get_allocation(owner, &alloc);

        pos_b = alloc.y;

    }

    /* Comparaison */

    if (pos_a < pos_b)
        result = -1;

    else if (pos_a > pos_b)
        result = 1;

    else
        result = 0;

    if (info->dir == LLD_TO_RIGHT)
        result *= -1;

    return result;

}
