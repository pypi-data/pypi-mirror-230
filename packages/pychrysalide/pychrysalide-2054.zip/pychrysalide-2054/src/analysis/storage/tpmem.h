
/* Chrysalide - Outil d'analyse de fichiers binaires
 * tpmem.h - prototypes pour la mémorisation des types d'objets mis en cache
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


#ifndef _ANALYSIS_STORAGE_TPMEM_H
#define _ANALYSIS_STORAGE_TPMEM_H


#include <glib-object.h>


#include "../../common/packed.h"



#define G_TYPE_TYPE_MEMORY            g_type_memory_get_type()
#define G_TYPE_MEMORY(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_TYPE_MEMORY, GTypeMemory))
#define G_IS_TYPE_MEMORY(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_TYPE_MEMORY))
#define G_TYPE_MEMORY_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_TYPE_MEMORY, GTypeMemoryClass))
#define G_IS_TYPE_MEMORY_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_TYPE_MEMORY))
#define G_TYPE_MEMORY_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_TYPE_MEMORY, GTypeMemoryClass))


/* Définition d'une mémoire de types d'objets (instance) */
typedef struct _GTypeMemory GTypeMemory;

/* Définition d'une mémoire de types d'objets (classe) */
typedef struct _GTypeMemoryClass GTypeMemoryClass;


/* Indique le type défini pour une mémoire de types d'objets. */
GType g_type_memory_get_type(void);

/* Crée une mémoire pour types d'objets. */
GTypeMemory *g_type_memory_new(void);

/* Apprend tous les types mémorisés dans un tampon. */
bool g_type_memory_load_types(GTypeMemory *, packed_buffer_t *);

/* Crée une nouvelle instance d'objet à partir de son type. */
GObject *g_type_memory_create_object(GTypeMemory *, packed_buffer_t *);

/* Sauvegarde le type d'un objet instancié. */
bool g_type_memory_store_object_gtype(GTypeMemory *, GObject *, packed_buffer_t *);

/* Enregistre tous les types mémorisés dans un tampon. */
bool g_type_memory_store_types(GTypeMemory *, packed_buffer_t *);



#endif  /* _ANALYSIS_STORAGE_TPMEM_H */
