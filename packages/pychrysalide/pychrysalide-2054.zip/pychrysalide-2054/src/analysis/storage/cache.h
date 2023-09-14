
/* Chrysalide - Outil d'analyse de fichiers binaires
 * cache.h - prototypes pour la conservation hors mémoire d'objets choisis
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _ANALYSIS_STORAGE_CACHE_H
#define _ANALYSIS_STORAGE_CACHE_H


#include <glib-object.h>


#include "container.h"
#include "../loaded.h"



#define G_TYPE_OBJECT_CACHE            g_object_cache_get_type()
#define G_OBJECT_CACHE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_OBJECT_CACHE, GObjectCache))
#define G_IS_OBJECT_CACHE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_OBJECT_CACHE))
#define G_OBJECT_CACHE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_OBJECT_CACHE, GObjectCacheClass))
#define G_IS_OBJECT_CACHE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_OBJECT_CACHE))
#define G_OBJECT_CACHE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_OBJECT_CACHE, GObjectCacheClass))


/* Définition d'un cache d'objets entreposables (instance) */
typedef struct _GObjectCache GObjectCache;

/* Définition d'un cache d'objets entreposables (classe) */
typedef struct _GObjectCacheClass GObjectCacheClass;


/* Indique le type défini pour un cache d'objets entreposables. */
GType g_object_cache_get_type(void);

/* Crée le support d'un cache d'objets entreposables. */
GObjectCache *g_object_cache_new(GLoadedContent *);

/* Introduit un contenu dans un cache d'objets. */
void g_object_cache_add(GObjectCache *, GCacheContainer *);



#endif  /* _ANALYSIS_STORAGE_CACHE_H */
