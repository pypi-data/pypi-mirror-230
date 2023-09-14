
/* Chrysalide - Outil d'analyse de fichiers binaires
 * stream.h - prototypes pour la gestion des connexions aux serveurs de débogage.
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


#ifndef _DEBUG_STREAM_H
#define _DEBUG_STREAM_H


#include <stdbool.h>


#include "packet.h"



#define G_TYPE_DEBUG_STREAM               g_debug_stream_get_type()
#define G_DEBUG_STREAM(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), g_debug_stream_get_type(), GDebugStream))
#define G_IS_DEBUG_STREAM(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_debug_stream_get_type()))
#define G_DEBUG_STREAM_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DEBUG_STREAM, GDebugStreamClass))
#define G_IS_DEBUG_STREAM_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DEBUG_STREAM))
#define G_DEBUG_STREAM_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DEBUG_STREAM, GDebugStreamClass))


/* Flux de communication avec un serveur de débogage (instance) */
typedef struct _GDebugStream GDebugStream;

/* Flux de communication avec un serveur de débogage (classe) */
typedef struct _GDebugStreamClass GDebugStreamClass;


/* Filtre la récupération de paquet */
typedef bool (* filter_packet_fc) (const GDebugPacket *, void *);


/* Indique le type défini pour un flux de communication avec un serveur de débogage. */
GType g_debug_stream_get_type(void);

/* Etablit de façon effective une connexion à la cible. */
bool g_debug_stream_connect(GDebugStream *);

/* Fournit un paquet prêt à emploi. */
GDebugPacket *g_debug_stream_get_free_packet(GDebugStream *);

/* Place un paquet en attente d'une future utilisation. */
void g_debug_stream_mark_packet_as_free(GDebugStream *, GDebugPacket *);

/* Envoie un paquet à un serveur de débogage. */
bool g_debug_stream_send_packet(GDebugStream *, GDebugPacket *);

/* Fournit un paquet reçu d'un serveur de débogage. */
GDebugPacket *g_debug_stream_recv_packet(GDebugStream *, filter_packet_fc, void *);



#endif  /* _DEBUG_STREAM_H */
