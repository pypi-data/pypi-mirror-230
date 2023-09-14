
/* Chrysalide - Outil d'analyse de fichiers binaires
 * stream-int.h - prototypes internes pour la gestion des connexions aux serveurs GDB.
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


#ifndef _DEBUG_GDBRSP_STREAM_INT_H
#define _DEBUG_GDBRSP_STREAM_INT_H


#include "gdb.h"
#include "stream.h"



/* Envoie des données à un serveur GDB. */
typedef bool (* send_gdb_data_fc) (GGdbStream *, const char *, size_t);

/* Réceptionne un octet de donnée d'un serveur GDB. */
typedef bool (* recv_gdb_byte_fc) (GGdbStream *, char *);


/* Flux de communication avec un serveur GDB (instance) */
struct _GGdbStream
{
    GObject parent;                         /* A laisser en premier        */

    int fd;                                 /* Flux ouvert en L./E.        */

    GGdbDebugger *owner;                    /* Propriétaire du flux        */

    send_gdb_data_fc send_data;             /* Envoi d'un paquet GDB       */
    recv_gdb_byte_fc recv_byte;             /* Réception d'un paquet GDB   */

    GThread *listening;                     /* Thread pour les réceptions  */

    GGdbPacket *free_packets;               /* Liste des disponibles       */
    GMutex free_mutex;                      /* Accès à la liste            */

    GGdbPacket *recv_packets;               /* Liste des paquets reçus     */
    GCond recv_cond;                        /* Attente de disponibilité    */
    GMutex recv_mutex;                      /* Accès à la liste            */

    GGdbPacket *status_packets;             /* Liste des paquets d'état    */
    GCond status_cond;                      /* Attente de disponibilité    */
    GMutex status_mutex;                    /* Accès à la liste            */




    bool skip_ack;

    bool want_status;


};


/* Flux de communication avec un serveur GDB (classe) */
struct _GGdbStreamClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};


/* Lance l'écoute d'un flux de communication avec GDB. */
bool g_gdb_stream_listen(GGdbStream *);



#endif  /* _DEBUG_GDBRSP_STREAM_INT_H */
