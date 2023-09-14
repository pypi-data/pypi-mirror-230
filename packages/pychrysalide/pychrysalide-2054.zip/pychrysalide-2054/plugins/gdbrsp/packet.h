
/* Chrysalide - Outil d'analyse de fichiers binaires
 * packet.h - prototypes pour la manipulation des paquets de données GDB.
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


#ifndef _DEBUG_GDBRSP_PACKET_H
#define _DEBUG_GDBRSP_PACKET_H


#include <glib-object.h>
#include <stdbool.h>
#include <stdint.h>



#define G_TYPE_GDB_PACKET               g_gdb_packet_get_type()
#define G_GDB_PACKET(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), g_gdb_packet_get_type(), GGdbPacket))
#define G_IS_GDB_PACKET(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_gdb_packet_get_type()))
#define G_GDB_PACKET_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_GDB_PACKET, GGdbPacketClass))
#define G_IS_GDB_PACKET_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_GDB_PACKET))
#define G_GDB_PACKET_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_GDB_PACKET, GGdbPacketClass))


/* Répresentation d'un paquet GDB (instance) */
typedef struct _GGdbPacket GGdbPacket;

/* Répresentation d'un paquet GDB (classe) */
typedef struct _GGdbPacketClass GGdbPacketClass;



/* Indique le type défini pour une répresentation de paquet GDB. */
GType g_gdb_packet_get_type(void);

/* Crée une représentation de paquet GDB. */
GGdbPacket *g_gdb_packet_new(void);

/* Prépare un paquet pour un envoi prochain. */
void g_gdb_packet_start_new_command(GGdbPacket *);

/* Complète un paquet pour un envoi prochain. */
void g_gdb_packet_append(GGdbPacket *, const char *);

/* Détermine l'empreinte des données d'un paquet GDB. */
void g_gdb_packet_compute_checksum(GGdbPacket *);

/* Contrôle l'intégrité des données d'un paquet GDB. */
bool g_gdb_packet_verify_checksum(GGdbPacket *, uint8_t);

/* Décode et/ou décompresse un paquet GDB. */
bool g_gdb_packet_decode(GGdbPacket *);

/* Fournit le contenu du paquet. */
void g_gdb_packet_get_data(const GGdbPacket *, const char **, size_t *, uint8_t *);

/* Ajoute un paquet à une liste de paquets. */
void g_gdb_packet_push(GGdbPacket **, GGdbPacket *);

/* Retire et fournit le premier élément d'une liste de paquets. */
GGdbPacket *g_gdb_packet_pop(GGdbPacket **);



#endif  /* _DEBUG_GDBRSP_PACKET_H */
