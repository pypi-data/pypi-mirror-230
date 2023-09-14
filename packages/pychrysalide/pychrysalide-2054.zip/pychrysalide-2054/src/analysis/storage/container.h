
/* Chrysalide - Outil d'analyse de fichiers binaires
 * container.h - prototypes pour les conteneurs d'objets entreposables dans un cache
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


#ifndef _ANALYSIS_STORAGE_CONTAINER_H
#define _ANALYSIS_STORAGE_CONTAINER_H


#include <glib-object.h>


#include "../../common/packed.h"



#define G_TYPE_CACHE_CONTAINER             g_cache_container_get_type()
#define G_CACHE_CONTAINER(obj)             (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_CACHE_CONTAINER, GCacheContainer))
#define G_CACHE_CONTAINER_CLASS(vtable)    (G_TYPE_CHECK_CLASS_CAST((vtable), G_TYPE_CACHE_CONTAINER, GCacheContainerIface))
#define G_IS_CACHE_CONTAINER(obj)          (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_CACHE_CONTAINER))
#define G_IS_CACHE_CONTAINER_CLASS(vtable) (G_TYPE_CHECK_CLASS_TYPE((vtable), G_TYPE_CACHE_CONTAINER))
#define G_CACHE_CONTAINER_GET_IFACE(inst)  (G_TYPE_INSTANCE_GET_INTERFACE((inst), G_TYPE_CACHE_CONTAINER, GCacheContainerIface))


/* Intermédiaire pour un conteneur d'objets entreposables (coquille vide) */
typedef struct _GCacheContainer GCacheContainer;

/* Intermédiaire pour un conteneur d'objets entreposables (interface) */
typedef struct _GCacheContainerIface GCacheContainerIface;


/* Détermine le type d'une interface pour un conteneur d'objets entreposables. */
GType g_cache_container_get_type(void) G_GNUC_CONST;

/* Contrôle l'accès au contenu d'un conteneur. */
void g_cache_container_lock_unlock(GCacheContainer *, bool);

/* Détermine si le conteneur a ses accès verrouillés. */
#ifndef NDEBUG
bool g_cache_container_is_locked(GCacheContainer *);
#endif

/* Indique si le contenu d'un conteneur peut être mis en cache. */
bool g_cache_container_can_store(GCacheContainer *);



#endif  /* _ANALYSIS_STORAGE_CONTAINER_H */
