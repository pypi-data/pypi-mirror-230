
/* Chrysalide - Outil d'analyse de fichiers binaires
 * serialize.h - objets entreposables dans un cache
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


#include "serialize.h"


#include "serialize-int.h"



/* Procède à l'initialisation de l'interface de mise en cache. */
static void g_serializable_object_default_init(GSerializableObjectInterface *);



/* Détermine le type d'une interface pour la mise en cache d'objet. */
G_DEFINE_INTERFACE(GSerializableObject, g_serializable_object, G_TYPE_OBJECT)


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de mise en cache.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_serializable_object_default_init(GSerializableObjectInterface *iface)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : object  = élément GLib à constuire.                          *
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à lire.                                *
*                                                                             *
*  Description : Charge un objet depuis une mémoire tampon.                   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_serializable_object_load(GSerializableObject *object, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GSerializableObjectIface *iface;        /* Interface utilisée          */

    iface = G_SERIALIZABLE_OBJECT_GET_IFACE(object);

    result = iface->load(object, storage, pbuf);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : object  = élément GLib à consulter.                          *
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à remplir.                             *
*                                                                             *
*  Description : Sauvegarde un objet dans une mémoire tampon.                 *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_serializable_object_store(const GSerializableObject *object, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GSerializableObjectIface *iface;        /* Interface utilisée          */

    iface = G_SERIALIZABLE_OBJECT_GET_IFACE(object);

    result = iface->store(object, storage, pbuf);

    return result;

}
