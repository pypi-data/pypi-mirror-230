
/* Chrysalide - Outil d'analyse de fichiers binaires
 * stream.h - prototypes pour la gestion des connexions aux serveurs GDB.
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#ifndef _DEBUG_GDBRSP_STREAM_H
#define _DEBUG_GDBRSP_STREAM_H


#include "packet.h"



#define G_TYPE_GDB_STREAM               g_gdb_stream_get_type()
#define G_GDB_STREAM(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), g_gdb_stream_get_type(), GGdbStream))
#define G_IS_GDB_STREAM(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_gdb_stream_get_type()))
#define G_GDB_STREAM_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_GDB_STREAM, GGdbStreamClass))
#define G_IS_GDB_STREAM_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_GDB_STREAM))
#define G_GDB_STREAM_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_GDB_STREAM, GGdbStreamClass))


/* Flux de communication avec un serveur GDB (instance) */
typedef struct _GGdbStream GGdbStream;

/* Flux de communication avec un serveur GDB (classe) */
typedef struct _GGdbStreamClass GGdbStreamClass;



/* Indique le type défini pour un flux de communication avec un serveur GDB. */
GType g_gdb_stream_get_type(void);

/* Ne participe plus aux acquitements de paquets. */
void g_gdb_stream_do_not_ack(GGdbStream *);

/* Fournit un paquet prêt à emploi. */
GGdbPacket *g_gdb_stream_get_free_packet(GGdbStream *);

/* Place un paquet en attente d'une future utilisation. */
void g_gdb_stream_mark_packet_as_free(GGdbStream *, GGdbPacket *);

/* Envoie un paquet à un serveur GDB. */
bool g_gdb_stream_send_packet(GGdbStream *, GGdbPacket *);

/* Fournit un paquet reçu d'un serveur GDB. */
GGdbPacket *g_gdb_stream_recv_packet(GGdbStream *);



#endif  /* _DEBUG_GDBRSP_STREAM_H */
