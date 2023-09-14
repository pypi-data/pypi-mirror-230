
/* Chrysalide - Outil d'analyse de fichiers binaires
 * net.c - fonctions complémentaires liées au réseau
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


#include "net.h"


#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>



/******************************************************************************
*                                                                             *
*  Paramètres  : server = nom ou adresse du serveur à contacter.              *
*                port   = port de connexion.                                  *
*                addr   = éventuelle remontée d'informations. [OUT]           *
*                                                                             *
*  Description : Ouvre une connexion TCP à un serveur quelconque.             *
*                                                                             *
*  Retour      : Flux ouvert en lecture/écriture ou -1 en cas d'échec.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int connect_via_tcp(const char *server, const char *port, struct sockaddr_in *addr)
{
    int result;                             /* Bilan à retourner           */
    struct addrinfo hints;                  /* Type de connexion souhaitée */
    struct addrinfo *infos;                 /* Informations disponibles    */
    int ret;                                /* Bilan d'un appel            */
    struct addrinfo *iter;                  /* Boucle de parcours          */

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

    if (addr != NULL)
    {
        ret = getpeername(result, (struct sockaddr *)addr,
                          (socklen_t []){ sizeof(struct sockaddr_in) });

        if (ret == -1)
        {
            perror("getpeername");
            close(result);
            return -1;
        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : sock   = nom ou adresse du serveur à contacter.              *
*                buffer = tampon pour la réception des données. [OUT]         *
*                max    = taille prévue pour ce tampon.                       *
*                len    = quantité de données effectivement reçues. [OUT]     *
*                                                                             *
*  Description : Reçoit du réseau autant de données que possible.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool recv_all(int sock, char *buffer, size_t max, size_t *len)
{
    bool result;                            /* Bilan global à retourner    */
    ssize_t ret;                            /* Bilan d'un appel            */

    result = true;

    buffer[0] = '\0';
    max--;  /* '\0' final */
    *len = 0;

    do
    {
        ret = recv(sock, buffer + *len, max, *len > 0 ? MSG_DONTWAIT : 0);

        printf("ret = %zd\n", ret);

        if (ret == -1 && *len == 0)
        {
            if (errno == EAGAIN || errno == EWOULDBLOCK)
                continue;
            else
                result = false;
        }

        else if (ret > 0)
        {
            max -= ret;
            *len += ret;
        }

    }
    while (ret > 0);

    buffer[*len] = '\0';

    return result;

}
