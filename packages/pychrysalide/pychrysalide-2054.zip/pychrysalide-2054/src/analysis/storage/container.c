
/* Chrysalide - Outil d'analyse de fichiers binaires
 * container.c - conteneurs d'objets entreposables dans un cache
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


#include "container.h"


#include <assert.h>


#include "container-int.h"



/* Procède à l'initialisation de l'interface de conteneur. */
static void g_cache_container_default_init(GCacheContainerInterface *);



/* Détermine le type d'une interface pour un conteneur d'objets entreposables. */
G_DEFINE_INTERFACE(GCacheContainer, g_cache_container, G_TYPE_OBJECT)


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de conteneur.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_cache_container_default_init(GCacheContainerInterface *iface)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : container = conteneur à manipuler.                           *
*                lock      = indique une demande de verrou.                   *
*                                                                             *
*  Description : Contrôle l'accès au contenu d'un conteneur.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_cache_container_lock_unlock(GCacheContainer *container, bool lock)
{
    GCacheContainerIface *iface;            /* Interface utilisée          */

    assert(g_cache_container_is_locked(container));

    iface = G_CACHE_CONTAINER_GET_IFACE(container);

    iface->lock_unlock(container, lock);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : container = conteneur à consulter.                           *
*                                                                             *
*  Description : Détermine si le conteneur a ses accès verrouillés.           *
*                                                                             *
*  Retour      : Bilan de la consultation.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

#ifndef NDEBUG
bool g_cache_container_is_locked(GCacheContainer *container)
{
    bool result;                            /* Bilan à retourner           */
    GCacheContainerIface *iface;            /* Interface utilisée          */

    iface = G_CACHE_CONTAINER_GET_IFACE(container);

    result = iface->is_locked(container);

    return result;

}
#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : container = conteneur à consulter.                           *
*                                                                             *
*  Description : Indique si le contenu d'un conteneur peut être mis en cache. *
*                                                                             *
*  Retour      : Bilan de la consultation.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_cache_container_can_store(GCacheContainer *container)
{
    bool result;                            /* Bilan à retourner           */
    GCacheContainerIface *iface;            /* Interface utilisée          */

    assert(g_cache_container_is_locked(container));

    iface = G_CACHE_CONTAINER_GET_IFACE(container);

    result = iface->can_store(container);

    return result;

}
