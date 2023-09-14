
/* Chrysalide - Outil d'analyse de fichiers binaires
 * cache.h - prototypes internes pour la conservation hors mémoire d'objets choisis
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


#ifndef _ANALYSIS_STORAGE_CACHE_INT_H
#define _ANALYSIS_STORAGE_CACHE_INT_H


#include "cache.h"



/* Définition d'un cache d'objets entreposables (instance) */
struct _GObjectCache
{
    GObject parent;                         /* A laisser en premier        */

    GLoadedContent *loaded;                 /* Contenu principal           */

    char *filename;                         /* Fichier local utilisé       */
    int fd;                                 /* Descripteur du flux associé */

    GCacheContainer **containers;           /* Objets en sursis            */
    size_t count;                           /* Quantité de ces objets      */
    size_t free_ptr;                        /* Point d'enregistrement      */
    GMutex mutex;                           /* Contrôle d'accès à la liste */

};

/* Définition d'un cache d'objets entreposables (classe) */
struct _GObjectCacheClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};


/* Associe un contenu à un cache d'objets. */
bool g_object_cache_open_for(GObjectCache *, GLoadedContent *);



#endif  /* _ANALYSIS_STORAGE_CACHE_INT_H */
