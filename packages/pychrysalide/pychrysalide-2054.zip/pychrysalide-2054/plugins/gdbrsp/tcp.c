
/* Chrysalide - Outil d'analyse de fichiers binaires
 * tcp.c - gestion des connexions TCP aux serveurs GDB.
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


#include "tcp.h"


#include <netdb.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/types.h>


#include "stream-int.h"


#include "../../common/net.h"


/* Flux de communication TCP avec un serveur GDB (instance) */
struct _GGdbTcpClient
{
    GGdbStream parent;                      /* A laisser en premier        */

};


/* Flux de communication TCP avec un serveur GDB (classe) */
struct _GGdbTcpClientClass
{
    GGdbStreamClass parent;                 /* A laisser en premier        */

};


/* Initialise la classe des flux de communication TCP avec GDB. */
static void g_gdb_tcp_client_class_init(GGdbTcpClientClass *);

/* Initialise une instance de flux de communication avec GDB. */
static void g_gdb_tcp_client_init(GGdbTcpClient *);

/* Ouvre une connexion TCP à un serveur GDB. */
//static int connect_via_tcp(const char *, const char *);

/* Envoie des données à un serveur GDB. */
static bool g_gdb_tcp_client_send_data(GGdbTcpClient *, const char *, size_t);

/* Réceptionne un octet de donnée d'un serveur GDB. */
static bool g_gdb_tcp_client_recv_byte(GGdbTcpClient *, char *);



/* Indique le type défini pour un flux de communication TCP avec un serveur GDB. */
G_DEFINE_TYPE(GGdbTcpClient, g_gdb_tcp_client, G_TYPE_GDB_STREAM);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des flux de communication TCP avec GDB. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_gdb_tcp_client_class_init(GGdbTcpClientClass *klass)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : client = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une instance de flux de communication avec GDB.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_gdb_tcp_client_init(GGdbTcpClient *client)
{
    GGdbStream *stream;                     /* Version parente             */

    stream = G_GDB_STREAM(client);

    stream->send_data = (send_gdb_data_fc)g_gdb_tcp_client_send_data;
    stream->recv_byte = (recv_gdb_byte_fc)g_gdb_tcp_client_recv_byte;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : server = nom ou adresse du serveur à contacter.              *
*                port   = port de connexion.                                  *
*                                                                             *
*  Description : Ouvre une connexion TCP à un serveur GDB.                    *
*                                                                             *
*  Retour      : Flux ouvert en lecture/écriture ou -1 en cas d'échec.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/
#if 0
static int connect_via_tcp(const char *server, const char *port)
{
    int result;                             /* Bilan à retourner           */
    struct addrinfo hints;                  /* Type de connexion souhaitée */
    struct addrinfo *infos;                 /* Informations disponibles    */
    int ret;                                /* Bilan d'un appel            */
    struct addrinfo *iter;                  /* Boucle de parcours          */
    struct sockaddr_in addr;                /* Infos de connexion distante */

    memset(&hints, 0, sizeof(struct addrinfo));

    hints.ai_family = AF_UNSPEC;        /* IPv4 ou IPv6 */
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_flags = 0;
    hints.ai_protocol = 0;              /* N'importe quel protocole */

    ret = getaddrinfo(server, port, &hints, &infos);
    if (ret != 0)
    {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(ret));
        return -1;
    }

    for (iter = infos; iter != NULL; iter = iter->ai_next)
    {
        result = socket(iter->ai_family, iter->ai_socktype, iter->ai_protocol);
        if (result == -1) continue;

        ret = connect(result, iter->ai_addr, iter->ai_addrlen);
        if (ret == 0) break;

        perror("connect");
        close(result);

    }

    freeaddrinfo(infos);

    if (iter == NULL) return -1;

    ret = getpeername(result, (struct sockaddr *)&addr, (socklen_t []){ sizeof(struct sockaddr_in) });
    if (ret == -1)
    {
        perror("getpeername");
        close(result);
        return -1;
    }

    printf("Connecté à %s:%hd\n", server, ntohs(addr.sin_port));

    return result;

}
#endif

/******************************************************************************
*                                                                             *
*  Paramètres  : server = nom ou adresse du serveur à contacter.              *
*                port   = port de connexion.                                  *
*                owner  = débogueur tributaire du canal de communication.     *
*                                                                             *
*  Description : Crée une nouvelle connexion TCP à un serveur GDB.            *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GGdbStream *g_gdb_tcp_client_new(const char *server, const char *port, GGdbDebugger *owner)
{
    GGdbTcpClient *result;                  /* Structure à retourner       */
    int sock;                               /* Flux ouvert à construire    */

    sock = connect_via_tcp(server, port, NULL);
    if (sock == -1) return NULL;

    result = g_object_new(G_TYPE_GDB_TCP_CLIENT, NULL);

    G_GDB_STREAM(result)->fd = sock;

    G_GDB_STREAM(result)->owner = owner;
    g_object_ref(G_OBJECT(owner));

    if (!g_gdb_stream_listen(G_GDB_STREAM(result)))
        goto ggtcn_error;

    return G_GDB_STREAM(result);

 ggtcn_error:

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : client = flux ouvert en écriture à utiliser.                 *
*                data   = données à envoyer.                                  *
*                len    = quantité de ces données.                            *
*                                                                             *
*  Description : Envoie des données à un serveur GDB.                         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_gdb_tcp_client_send_data(GGdbTcpClient *client, const char *data, size_t len)
{
    ssize_t sent;                           /* Quantité de données envoyée */

    sent = send(G_GDB_STREAM(client)->fd, data, len, 0);

    //printf("  sent '%s'\n", data);
    //printf("  sent ? %d vs %d\n", (int)sent, (int)len);

    return (sent == len);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : client = flux ouvert en lecture à utiliser.                  *
*                data   = donnée à recevoir.                                  *
*                                                                             *
*  Description : Réceptionne un octet de donnée d'un serveur GDB.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_gdb_tcp_client_recv_byte(GGdbTcpClient *client, char *data)
{
    ssize_t got;                            /* Quantité de données reçue   */

    got = recv(G_GDB_STREAM(client)->fd, data, 1, 0);

    //printf("  got ? %d vs %d -> %c (0x%02hhx\n", (int)got, (int)1, *data, *data);

    return (got == 1);

}
