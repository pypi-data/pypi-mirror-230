
/* Chrysalide - Outil d'analyse de fichiers binaires
 * tcp.h - prototypes pour la gestion des connexions TCP aux serveurs GDB.
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


#ifndef _DEBUG_GDBRSP_TCP_H
#define _DEBUG_GDBRSP_TCP_H


#include "gdb.h"
#include "stream.h"



#define G_TYPE_GDB_TCP_CLIENT               g_gdb_tcp_client_get_type()
#define G_GDB_TCP_CLIENT(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), g_gdb_tcp_client_get_type(), GGdbTcpClient))
#define G_IS_GDB_TCP_CLIENT(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_gdb_tcp_client_get_type()))
#define G_GDB_TCP_CLIENT_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_GDB_TCP_CLIENT, GGdbTcpClientClass))
#define G_IS_GDB_TCP_CLIENT_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_GDB_TCP_CLIENT))
#define G_GDB_TCP_CLIENT_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_GDB_TCP_CLIENT, GGdbTcpClientClass))


/* Flux de communication TCP avec un serveur GDB (instance) */
typedef struct _GGdbTcpClient GGdbTcpClient;

/* Flux de communication TCP avec un serveur GDB (classe) */
typedef struct _GGdbTcpClientClass GGdbTcpClientClass;



/* Indique le type défini pour un flux de communication TCP avec un serveur GDB. */
GType g_gdb_tcp_client_get_type(void);

/* Crée une nouvelle connexion TCP à un serveur GDB. */
GGdbStream *g_gdb_tcp_client_new(const char *, const char *, GGdbDebugger *);



#endif  /* _DEBUG_GDBRSP_TCP_H */
