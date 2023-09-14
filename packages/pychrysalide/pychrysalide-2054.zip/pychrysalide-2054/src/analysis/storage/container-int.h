
/* Chrysalide - Outil d'analyse de fichiers binaires
 * container-int.h - définitions internes propres aux conteneurs d'objets entreposables dans un cache
 *
 * Copyright (C) 2020 Cyrille Bagard
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


#ifndef _ANALYSIS_STORAGE_CONTAINER_INT_H
#define _ANALYSIS_STORAGE_CONTAINER_INT_H


#include "container.h"



/* Contrôle l'accès au contenu d'un conteneur. */
typedef void (* lock_unlock_container_cb) (GCacheContainer *, bool);

/* Détermine si le conteneur a ses accès verrouillés. */
#ifndef NDEBUG
typedef bool (* is_locked_container_cb) (GCacheContainer *);
#endif

/* Indique si le contenu d'un conteneur peut être mis en cache. */
typedef bool (* can_store_container_cb) (GCacheContainer *);

/* Intermédiaire pour un conteneur d'objets entreposables (interface) */
struct _GCacheContainerIface
{
    GTypeInterface base_iface;              /* A laisser en premier        */

    lock_unlock_container_cb lock_unlock;   /* Contrôle d'accès au contenu */
#ifndef NDEBUG
    is_locked_container_cb is_locked;       /* Validation des verrous      */
#endif
    can_store_container_cb can_store;       /* Mise en cache possible ?    */

};


/* Redéfinition */
typedef GCacheContainerIface GCacheContainerInterface;



#endif  /* _ANALYSIS_STORAGE_CONTAINER_INT_H */
