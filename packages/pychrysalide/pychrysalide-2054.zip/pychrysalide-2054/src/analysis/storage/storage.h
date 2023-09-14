
/* Chrysalide - Outil d'analyse de fichiers binaires
 * storage.h - prototypes pour la conservation sur disque d'objets construits
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


#ifndef _ANALYSIS_STORAGE_STORAGE_H
#define _ANALYSIS_STORAGE_STORAGE_H


#include <glib-object.h>
#include <stdbool.h>


#include "serialize.h"
#include "tpmem.h"



#define G_TYPE_OBJECT_STORAGE            g_object_storage_get_type()
#define G_OBJECT_STORAGE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_OBJECT_STORAGE, GObjectStorage))
#define G_IS_OBJECT_STORAGE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_OBJECT_STORAGE))
#define G_OBJECT_STORAGE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_OBJECT_STORAGE, GObjectStorageClass))
#define G_IS_OBJECT_STORAGE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_OBJECT_STORAGE))
#define G_OBJECT_STORAGE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_OBJECT_STORAGE, GObjectStorageClass))


/* Définition d'une conservation d'objets construits (instance) */
typedef struct _GObjectStorage GObjectStorage;

/* Définition d'une conservation d'objets construits (classe) */
typedef struct _GObjectStorageClass GObjectStorageClass;


/* Indique le type défini pour une conservation d'objets construits. */
GType g_object_storage_get_type(void);

/* Crée le support d'une conservation d'objets en place. */
GObjectStorage *g_object_storage_new(const char *);

#define get_storage_linked_format(s)                            \
    ({                                                          \
        void*__result;                                          \
        __result = g_object_get_data(G_OBJECT(s), "format");    \
        g_object_ref(G_OBJECT(__result));                       \
        __result;                                               \
    })

/* Charge le support d'une conservation d'objets en place. */
GObjectStorage *g_object_storage_load(packed_buffer_t *);

/* Sauvegarde le support d'une conservation d'objets en place. */
bool g_object_storage_store(GObjectStorage *, packed_buffer_t *);

/* Charge un objet à partir de données rassemblées. */
GSerializableObject *g_object_storage_load_object(GObjectStorage *, const char *, off64_t);

/* Charge un objet interne à partir de données rassemblées. */
GSerializableObject *g_object_storage_unpack_object(GObjectStorage *, const char *, packed_buffer_t *);

/* Sauvegarde un object sous forme de données rassemblées. */
bool g_object_storage_store_object(GObjectStorage *, const char *, const GSerializableObject *, off64_t *);

/* Charge un objet interne à partir de données rassemblées. */
bool g_object_storage_unpack_object_2(GObjectStorage *, const char *, packed_buffer_t *, GType, ...);

/* Sauvegarde un object interne sous forme de données. */
bool g_object_storage_pack_object(GObjectStorage *, const char *, const GSerializableObject *, packed_buffer_t *);



#endif  /* _ANALYSIS_STORAGE_STORAGE_H */
