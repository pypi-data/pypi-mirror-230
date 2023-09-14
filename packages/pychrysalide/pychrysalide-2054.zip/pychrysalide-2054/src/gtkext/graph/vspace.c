
/* Chrysalide - Outil d'analyse de fichiers binaires
 * vspace.c - encadrement des espaces verticaux réservés
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


#include "vspace.h"


#include <malloc.h>


#include "cluster-int.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : manager = structure à initialiser.                           *
*                                                                             *
*  Description : Initialise les réservations liens verticaux.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void init_vspace_manager(vspace_manager_t *manager)
{
    manager->pending = NULL;
    manager->pending_count = 0;

    manager->left = NULL;
    manager->left_count = 0;

    manager->right = NULL;
    manager->right_count = 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : manager = structure à vider.                                 *
*                                                                             *
*  Description : Termine les réservations liens verticaux.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void exit_vspace_manager(vspace_manager_t *manager)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < manager->pending_count; i++)
        free(manager->pending[i].pts);

    if (manager->pending != NULL)
        free(manager->pending);

    if (manager->left != NULL)
        free(manager->left);

    if (manager->right != NULL)
        free(manager->right);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : manager  = structure à compléter.                            *
*                from     = point de départ du lien concerné.                 *
*                to       = point d'arrivée du lien concerné.                 *
*                pts      = points intermédiaires du tracé complet final.     *
*                external = précise une sortie du cadre du cluster premier.   *
*                                                                             *
*  Description : Inscrit une nouvelle réservation d'espace latéral.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void extend_vspace_manager(vspace_manager_t *manager, leaving_link_t *from, incoming_link_t *to, GdkPoint *pts, bool external)
{
    vspace_booking_t *new;                  /* Réservation à constituer    */

    manager->pending = realloc(manager->pending, ++manager->pending_count * sizeof(vspace_booking_t));

    new = &manager->pending[manager->pending_count - 1];

    new->from = from;
    new->to = to;

    new->pts = pts;

    new->external = external;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : manager  = gestion des espaces latéraux à consulter.         *
*                external = précise une sortie du cadre du cluster premier.   *
*                alloc    = emplacement idéal pour l'affichage. [OUT]         *
*                                                                             *
*  Description : Détermine l'emplacement requis pour les espaces latéraux.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void compute_vspace_manager_needed_alloc(const vspace_manager_t *manager, bool external, GtkAllocation *alloc)
{
    gint width;                             /* Largeur supplémentaire      */
    size_t count;                           /* Nombre de liens retenus     */
    size_t i;                               /* Boucle de parcours          */

    width = 0;

    /* Extension de la largeur, à gauche */

    count = 0;

    for (i = 0; i < manager->left_count; i++)
        if (manager->left[i]->external == external)
            count++;

    width += count * LINK_MARGIN;

    alloc->x -= width;

    /* Extension de la largeur, à droite */

    count = 0;

    for (i = 0; i < manager->right_count; i++)
        if (manager->right[i]->external == external)
            count++;

    width += count * LINK_MARGIN;

    alloc->width += width;

    /* Extension de la hauteur */

    if (!external)
        alloc->height += manager->pending_count * VERTICAL_MARGIN;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : manager = gestion d'espaces latéraux à manipuler.            *
*                                                                             *
*  Description : Réorganise au besoin les liens de boucle entre blocs.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void sort_incoming_links_for_vspace_manager(vspace_manager_t *manager)
{
    size_t i;                               /* Boucle de parcours          */
    vspace_booking_t *pending;              /* Elément traité              */
    gint x1;                                /* Abscisse de départ de lien  */
    size_t idx;                             /* Indice du lien entrant      */
    gint x2;                                /* Abscisse d'arrivée de lien  */
    bool for_left;                          /* Répartition par la gauche ? */

    for (i = 0; i < manager->pending_count; i++)
    {
        pending = &manager->pending[i];

        x1 = g_graph_cluster_compute_leaving_link_position(pending->from->owner, pending->from->index);

        idx = g_graph_cluster_find_incoming_link(pending->to->owner, pending->from);

        x2 = g_graph_cluster_compute_incoming_link_position(pending->to->owner, idx);

        /**
         * Prise en compte d'une boucle while (1);
         */
        if (pending->from->owner == pending->to->owner)
            for_left = (x2 < x1);
        else
            for_left = (x1 < x2);

        if (for_left)
        {
            manager->left = realloc(manager->left, ++manager->left_count * sizeof(vspace_booking_t *));
            manager->left[manager->left_count - 1] = pending;
        }
        else
        {
            manager->right = realloc(manager->right, ++manager->right_count * sizeof(vspace_booking_t *));
            manager->right[manager->right_count - 1] = pending;
        }

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : manager = structure à actualiser.                            *
*                offset = décalage à appliquer.                               *
*                                                                             *
*  Description : Décale vers la droite un ensemble de points.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void offset_x_vspace_manager(vspace_manager_t *manager, gint offset)
{
    size_t i;                               /* Boucle de parcours          */
    vspace_booking_t *booking;              /* Réservation à traiter       */

    for (i = 0; i < manager->left_count; i++)
    {
        booking = manager->left[i];

        booking->pts[0].x += offset;
        booking->pts[1].x += offset;

    }

    for (i = 0; i < manager->right_count; i++)
    {
        booking = manager->right[i];

        booking->pts[0].x += offset;
        booking->pts[1].x += offset;

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : manager  = structure à consulter.                            *
*                needed   = espace nécessaire et alloué pour les blocs.       *
*                external = précise une sortie du cadre du cluster premier.   *
*                                                                             *
*  Description : Détermine les abscisses de tous les liens en place.          *
*                                                                             *
*  Retour      : Eventuelle marge à gauche devenue nécessaire.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

gint compute_loop_link_x_with_vspace_manager(const vspace_manager_t *manager, const GtkAllocation *needed, bool external)
{
    gint result;                            /* Eventuelle marge à renvoyer */
    size_t count;                           /* Quantité de liens traités   */
    size_t i;                               /* Boucle de parcours          */
    vspace_booking_t *booking;              /* Réservation à traiter       */
    gint x;                                 /* Position à appliquer        */

    count = 0;

    for (i = 0; i < manager->left_count; i++)
    {
        booking = manager->left[i];

        if (booking->external != external)
            continue;

        x = ++count * LINK_MARGIN;

        booking->pts[0].x = needed->x - x;
        booking->pts[1].x = needed->x - x;

    }

    result = count * LINK_MARGIN;

    count = 0;

    for (i = 0; i < manager->right_count; i++)
    {
        booking = manager->right[i];

        if (booking->external != external)
            continue;

        x = ++count * LINK_MARGIN;

        booking->pts[0].x = needed->x + needed->width + x;
        booking->pts[1].x = needed->x + needed->width + x;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : manager = structure à consulter.                             *
*                needed  = espace nécessaire et alloué pour les blocs.        *
*                                                                             *
*  Description : Détermine les ordonnées de tous les liens en place.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void compute_loop_link_y_with_vspace_manager(const vspace_manager_t *manager, const GtkAllocation *needed)
{
    gint real_bottom;                       /* Point de départ réel        */
    size_t i;                               /* Boucle de parcours          */
    vspace_booking_t *booking;              /* Réservation à traiter       */

    real_bottom = needed->y + needed->height - manager->pending_count * VERTICAL_MARGIN;

    for (i = 0; i < manager->pending_count; i++)
    {
        booking = &manager->pending[i];

        /**
         * On corrige le raccourci pris sans distinction de type de lien dans
         * la fonction g_graph_cluster_compute_link_y_positions().
         */

        booking->from->start[1].y = real_bottom +  (i + 1) * VERTICAL_MARGIN;

        /* Définition de l'ordonnée des points du lien */

        booking->pts[0].y = booking->from->start[1].y;

        booking->pts[1].y = booking->to->end[0].y;

    }

}
