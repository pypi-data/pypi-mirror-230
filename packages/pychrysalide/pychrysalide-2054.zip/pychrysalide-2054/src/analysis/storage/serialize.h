
/* Chrysalide - Outil d'analyse de fichiers binaires
 * serialize.h - prototypes pour les objets entreposables dans un cache
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


#ifndef _ANALYSIS_STORAGE_SERIALIZE_H
#define _ANALYSIS_STORAGE_SERIALIZE_H


#include <glib-object.h>


#include "../../common/packed.h"



#define G_TYPE_SERIALIZABLE_OBJECT             g_serializable_object_get_type()
#define G_SERIALIZABLE_OBJECT(obj)             (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SERIALIZABLE_OBJECT, GSerializableObject))
#define G_SERIALIZABLE_OBJECT_CLASS(vtable)    (G_TYPE_CHECK_CLASS_CAST((vtable), G_TYPE_SERIALIZABLE_OBJECT, GSerializableObjectIface))
#define G_IS_SERIALIZABLE_OBJECT(obj)          (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SERIALIZABLE_OBJECT))
#define G_IS_SERIALIZABLE_OBJECT_CLASS(vtable) (G_TYPE_CHECK_CLASS_TYPE((vtable), G_TYPE_SERIALIZABLE_OBJECT))
#define G_SERIALIZABLE_OBJECT_GET_IFACE(inst)  (G_TYPE_INSTANCE_GET_INTERFACE((inst), G_TYPE_SERIALIZABLE_OBJECT, GSerializableObjectIface))


/* Intermédiaire pour la mise en cache d'objet (coquille vide) */
typedef struct _GSerializableObject GSerializableObject;

/* Intermédiaire pour la mise en cache d'objet (interface) */
typedef struct _GSerializableObjectIface GSerializableObjectIface;


/* Détermine le type d'une interface pour la mise en cache d'objet. */
GType g_serializable_object_get_type(void) G_GNUC_CONST;

/* storage.h : définition d'une conservation d'objets construits */
typedef struct _GObjectStorage GObjectStorage;

/* Charge un objet depuis une mémoire tampon. */
bool g_serializable_object_load(GSerializableObject *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un objet dans une mémoire tampon. */
bool g_serializable_object_store(const GSerializableObject *, GObjectStorage *, packed_buffer_t *);



#endif  /* _ANALYSIS_STORAGE_SERIALIZE_H */
