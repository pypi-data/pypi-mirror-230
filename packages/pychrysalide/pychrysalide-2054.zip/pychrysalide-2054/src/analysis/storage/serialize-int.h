
/* Chrysalide - Outil d'analyse de fichiers binaires
 * serialize-int.h - définitions internes propres aux objets entreposables dans un cache
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


#ifndef _ANALYSIS_STORAGE_SERIALIZE_INT_H
#define _ANALYSIS_STORAGE_SERIALIZE_INT_H


#include "serialize.h"


#include "storage.h"



/* Charge un objet depuis une mémoire tampon. */
typedef bool (* load_serializable_object_cb) (GSerializableObject *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un objet dans une mémoire tampon. */
typedef bool (* store_serializable_object_cb) (const GSerializableObject *, GObjectStorage *, packed_buffer_t *);


/* Intermédiaire pour la mise en cache d'objet (interface) */
struct _GSerializableObjectIface
{
    GTypeInterface base_iface;              /* A laisser en premier        */

    load_serializable_object_cb load;       /* Chargement                  */
    store_serializable_object_cb store;     /* Enregistrement              */

};


/* Redéfinition */
typedef GSerializableObjectIface GSerializableObjectInterface;



#endif  /* _ANALYSIS_STORAGE_SERIALIZE_INT_H */
