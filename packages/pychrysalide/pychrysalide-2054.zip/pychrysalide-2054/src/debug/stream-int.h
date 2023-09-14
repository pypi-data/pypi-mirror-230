
/* Chrysalide - Outil d'analyse de fichiers binaires
 * stream-int.h - prototypes internes pour la gestion des connexions liées aux débogages.
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


#ifndef _DEBUG_STREAM_INT_H
#define _DEBUG_STREAM_INT_H


#include "stream.h"



/* Etablit de façon effective une connexion à la cible. */
typedef bool (* debug_connect_fc) (GDebugStream *);



/* Attend le signalement de données à traiter. */
typedef bool (* debug_poll_fc) (GDebugStream *);

/* Réceptionne un paquet de données d'un serveur de débogage. */
typedef bool (* debug_pkt_op_fc) (GDebugStream *, GDebugPacket *);

/* Libère le contenu alloué d'un paquet de débogage. */
typedef void (* debug_free_pkt_fc) (GDebugStream *, GDebugPacket *);






/* Envoie des données à un serveur de débogage. */
typedef bool (* send_debug_data_fc) (GDebugStream *, const char *, size_t);

/* Réceptionne un octet de donnée d'un serveur de débogage. */
typedef bool (* recv_debug_byte_fc) (GDebugStream *, char *);


/* Flux de communication avec un serveur de débogage (instance) */
struct _GDebugStream
{
    GObject parent;                         /* A laisser en premier        */

    debug_connect_fc connect;               /* Connexion distante          */

    debug_poll_fc poll;                     /* Attente de traitements      */
    debug_pkt_op_fc send_packet;            /* Emission d'un paquet        */
    debug_pkt_op_fc recv_packet;            /* Réception d'un paquet       */
    debug_free_pkt_fc free_packet;          /* Libération d'un paquet      */

    GThread *listening;                     /* Thread pour les réceptions  */

    GType pkt_type;                         /* Type des paquets traités    */
    GDebugPacket *free_packets;             /* Liste des disponibles       */
    GMutex free_mutex;                      /* Accès à la liste            */

    GDebugPacket *recv_packets;             /* Liste des paquets reçus     */
    GCond recv_cond;                        /* Attente de disponibilité    */
    GMutex recv_mutex;                      /* Accès à la liste            */

};


/* Flux de communication avec un serveur de débogage (classe) */
struct _GDebugStreamClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};



#endif  /* _DEBUG_STREAM_INT_H */
