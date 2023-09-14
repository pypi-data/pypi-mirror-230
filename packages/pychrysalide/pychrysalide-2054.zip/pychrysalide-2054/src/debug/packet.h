
/* Chrysalide - Outil d'analyse de fichiers binaires
 * packet.h - prototypes pour la définition des paquets issus des protocoles de débogage
 *
 * Copyright (C) 2010-2018 Cyrille Bagard
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


#ifndef _DEBUG_PACKET_H
#define _DEBUG_PACKET_H


#include <glib-object.h>
#include <sys/uio.h>



#define G_TYPE_DEBUG_PACKET               g_debug_packet_get_type()
#define G_DEBUG_PACKET(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), g_debug_packet_get_type(), GDebugPacket))
#define G_IS_DEBUG_PACKET(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_debug_packet_get_type()))
#define G_DEBUG_PACKET_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DEBUG_PACKET, GDebugPacketClass))
#define G_IS_DEBUG_PACKET_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DEBUG_PACKET))
#define G_DEBUG_PACKET_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DEBUG_PACKET, GDebugPacketClass))


/* Répresentation d'un paquet de débogage (instance) */
typedef struct _GDebugPacket GDebugPacket;

/* Répresentation d'un paquet de débogage (classe) */
typedef struct _GDebugPacketClass GDebugPacketClass;



/* Indique le type défini pour un paquet de débogage. */
GType g_debug_packet_get_type(void);

/* Précise les zones mémoires correspondant au contenu. */
void g_debug_packet_vectorize(GDebugPacket *, struct iovec [UIO_MAXIOV], int *);

/* Fournit l'élement suivant un autre pour un parcours. */
GDebugPacket *g_debug_packet_get_next_iter(const GDebugPacket *, const GDebugPacket *);

/* Ajoute un paquet à une liste de paquets. */
void g_debug_packet_push(GDebugPacket **, GDebugPacket *);

/* Retire et fournit le premier élément d'une liste de paquets. */
GDebugPacket *g_debug_packet_pop(GDebugPacket **);

/* Retire et fournit un élément d'une liste de paquets. */
void g_debug_packet_extract(GDebugPacket **, GDebugPacket *);



#endif  /* _DEBUG_PACKET_H */
