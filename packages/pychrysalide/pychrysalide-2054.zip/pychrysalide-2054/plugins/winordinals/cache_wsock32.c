
/* Chrysalide - Outil d'analyse de fichiers binaires
 * cache_wsock32.c - fourniture des ordinaux du fichier wsock32.dll
 *
 * Copyright (C) 2021 Cyrille Bagard
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


#include "cache_wsock32.h"


#include <stddef.h>



/**
 * Empreintes du fichier wsock32.dll :
 *
 *   - MD5 : 2afbb671a865f43c0476d685dc77b4df
 *   - SHA1 : 233125ad8fd18a65d5939b80160ce3e5c19c0184
 *   - SHA256 : 0c310f70350ba9801f0421c2da2595beaa3fef55d43d6928d53a674dfcd6e9fb
 */


/* Liste des ordinaux référencés */
static const char *_wsock32_ordinals[1143] = {
    [1] = "accept",
    [2] = "bind",
    [3] = "closesocket",
    [4] = "connect",
    [5] = "getpeername",
    [6] = "getsockname",
    [7] = "getsockopt",
    [8] = "htonl",
    [9] = "htons",
    [10] = "inet_addr",
    [11] = "inet_ntoa",
    [12] = "ioctlsocket",
    [13] = "listen",
    [14] = "ntohl",
    [15] = "ntohs",
    [16] = "recv",
    [17] = "recvfrom",
    [18] = "select",
    [19] = "send",
    [20] = "sendto",
    [21] = "setsockopt",
    [22] = "shutdown",
    [23] = "socket",
    [51] = "gethostbyaddr",
    [52] = "gethostbyname",
    [53] = "getprotobyname",
    [54] = "getprotobynumber",
    [55] = "getservbyname",
    [56] = "getservbyport",
    [101] = "WSAAsyncSelect",
    [102] = "WSAAsyncGetHostByAddr",
    [103] = "WSAAsyncGetHostByName",
    [104] = "WSAAsyncGetProtoByNumber",
    [105] = "WSAAsyncGetProtoByName",
    [106] = "WSAAsyncGetServByPort",
    [107] = "WSAAsyncGetServByName",
    [108] = "WSACancelAsyncRequest",
    [109] = "WSASetBlockingHook",
    [110] = "WSAUnhookBlockingHook",
    [111] = "WSAGetLastError",
    [112] = "WSASetLastError",
    [113] = "WSACancelBlockingCall",
    [114] = "WSAIsBlocking",
    [115] = "WSAStartup",
    [1100] = "inet_network",
    [1101] = "getnetbyname",
    [1102] = "rcmd",
    [1103] = "rexec",
    [1104] = "rresvport",
    [1105] = "sethostname",
    [1106] = "dn_expand",
    [1107] = "WSARecvEx",
    [1108] = "s_perror",
    [1109] = "GetAddressByNameA",
    [1110] = "GetAddressByNameW",
    [1111] = "EnumProtocolsA",
    [1112] = "EnumProtocolsW",
    [1113] = "GetTypeByNameA",
    [1114] = "GetTypeByNameW",
    [1115] = "GetNameByTypeA",
    [1116] = "GetNameByTypeW",
    [1117] = "SetServiceA",
    [1118] = "SetServiceW",
    [1119] = "GetServiceA",
    [1140] = "TransmitFile",
    [1141] = "AcceptEx",
    [1142] = "GetAcceptExSockaddrs",
};



/******************************************************************************
*                                                                             *
*  Paramètres  : ordinal = valeur ordinale à considérer.                      *
*                                                                             *
*  Description : Fournit le nom du symbole associé à un ordinal donné.        *
*                                                                             *
*  Retour      : Désignation du symbole trouvé ou NULL en cas d'échec.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *find_wsock32_name_for_ordinal(uint16_t ordinal)
{
    const char *result;                     /* Désignation à renvoyer      */

    if (ordinal >= 1143)
        result = NULL;

    else
        result = _wsock32_ordinals[ordinal];

    return result;

}
