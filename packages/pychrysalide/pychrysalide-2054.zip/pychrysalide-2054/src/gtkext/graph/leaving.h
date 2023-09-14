
/* Chrysalide - Outil d'analyse de fichiers binaires
 * leaving.h - prototypes pour les liens sortants d'un bloc de code dans une représentation graphique
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


#ifndef _GTKEXT_GRAPH_LEAVING_H
#define _GTKEXT_GRAPH_LEAVING_H


#include "cluster.h"


/* Depuis incoming.h : définition du tracé d'un lien */
typedef struct _incoming_link_t incoming_link_t;

/* Détails sur le départ d'un lien */
typedef struct _leaving_link_t
{
    GGraphCluster *owner;                   /* Propriétaire du lien        */

    GdkPoint start[2];                      /* Point de départ d'un lien   */
    size_t index;                           /* Indice sur ligne de départ  */

    bool straight;                          /* Présence d'une ligne droite */
    bool forced_straight;                   /* Forçage de verticalité      */
    size_t straight_level;                  /* Rang atteint en ligne droite*/
    bool cluster_exit;                      /* Sortie du cluster d'origine */

    incoming_link_t *other;                 /* Autre extrémité du lien     */

} leaving_link_t;


#define SHOULD_BE_VERTICAL(l) ((l)->straight || (l)->forced_straight || (l)->cluster_exit)


/* Crée un point d'attache pour un lien sortant. */
leaving_link_t *create_leaving_link(GGraphCluster *, size_t);

/* Détruit un point d'attache pour un lien sortant. */
void delete_leaving_link(leaving_link_t *);

/* Calcule l'abscisse d'un lien à son départ d'un bloc. */
gint compute_leaving_link_position(const leaving_link_t *);

/* Direction prise par le lien */
typedef enum _LeavingLinkDir
{
    LLD_NO_PREF,                            /* Direction variable          */
    LLD_TO_LEFT,                            /* Vers la gauche              */
    LLD_TO_RIGHT,                           /* Vers la droite              */

} LeavingLinkDir;

/* Détermine une direction prise par un lien à son départ. */
LeavingLinkDir get_leaving_link_direction(const leaving_link_t *, gint, gint);

/* Transmision d'éléments pour comparaisons */
typedef struct _leaving_cmp_info_t
{
    GGraphCluster *root;
    LeavingLinkDir dir;

} leaving_cmp_info_t;

/*Compare deux liens sortants. */
int cmp_leaving_links(const leaving_link_t **a, const leaving_link_t **b, const leaving_cmp_info_t *);



#endif  /* _GTKEXT_GRAPH_LEAVING_H */
