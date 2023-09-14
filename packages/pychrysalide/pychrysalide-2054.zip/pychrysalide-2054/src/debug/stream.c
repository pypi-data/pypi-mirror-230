
/* Chrysalide - Outil d'analyse de fichiers binaires
 * stream.c - gestion des connexions aux serveurs de débogage.
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


#include "stream.h"


#include <stdio.h>
#include <stdlib.h>
#include <glib/gthread.h>


#include "stream-int.h"
#include "../common/dllist.h"   /* FIXME : remme ! */



/* Initialise la classe des flux de communication de débogage. */
static void g_debug_stream_class_init(GDebugStreamClass *);

/* Initialise une instance de flux de communication de débogage. */
static void g_debug_stream_init(GDebugStream *);

/* Ecoute une connexion à un serveur de débogage. */
static void *debug_stream_thread(GDebugStream *);

/* Réceptionne un paquet d'un serveur de débogage. */
static bool g_debug_stream_read_packet(GDebugStream *, GDebugPacket *);



/* Indique le type défini pour un flux de communication avec un serveur de débogage. */
G_DEFINE_TYPE(GDebugStream, g_debug_stream, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des flux de communication de débogage.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_debug_stream_class_init(GDebugStreamClass *klass)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stream = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une instance de flux de communication de débogage.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_debug_stream_init(GDebugStream *stream)
{
    g_mutex_init(&stream->free_mutex);

    g_cond_init(&stream->recv_cond);
    g_mutex_init(&stream->recv_mutex);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stream = paramètres de connexion distante.                   *
*                                                                             *
*  Description : Etablit de façon effective une connexion à la cible.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_debug_stream_connect(GDebugStream *stream)
{
    if (stream->connect == NULL || !stream->connect(stream))
        return false;

    if (!g_thread_new("chrysalide_stream", (GThreadFunc)debug_stream_thread, stream))
    {
        /* TODO : disconnect ! */
        return false;
    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stream = encadrement associée à l'opération.                 *
*                                                                             *
*  Description : Ecoute une connexion à un serveur de débogage.               *
*                                                                             *
*  Retour      : ???                                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void *debug_stream_thread(GDebugStream *stream)
{
    bool status;                            /* Bilan d'évolution           */
    GDebugPacket *packet;                   /* Nouveau paquet reçu         */

    while (1)
    {
        status = stream->poll(stream);
        if (!status) break;

        packet = g_debug_stream_get_free_packet(stream);

        if (stream->recv_packet(stream, packet))
        {
            g_mutex_lock(&stream->recv_mutex);
            g_debug_packet_push(&stream->recv_packets, packet);
            g_mutex_unlock(&stream->recv_mutex);

            g_cond_signal(&stream->recv_cond);

        }
        else g_debug_stream_mark_packet_as_free(stream, packet);

    }

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stream = flux de communication de débogage à consulter.      *
*                                                                             *
*  Description : Fournit un paquet prêt à emploi.                             *
*                                                                             *
*  Retour      : Paquet prêt à emploi.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDebugPacket *g_debug_stream_get_free_packet(GDebugStream *stream)
{
    GDebugPacket *result;                   /* Paquet à retourner          */

    g_mutex_lock(&stream->free_mutex);

    if (dl_list_empty(stream->free_packets))
        result = g_object_new(stream->pkt_type, NULL);

    else
        result = g_debug_packet_pop(&stream->free_packets);

    g_mutex_unlock(&stream->free_mutex);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stream = flux de communication de débogage à mettre à jour.  *
*                packet = paquet à considérer comme disponible.               *
*                                                                             *
*  Description : Place un paquet en attente d'une future utilisation.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_debug_stream_mark_packet_as_free(GDebugStream *stream, GDebugPacket *packet)
{
    stream->free_packet(stream, packet);

    g_mutex_lock(&stream->free_mutex);

    g_debug_packet_push(&stream->free_packets, packet);

    g_mutex_unlock(&stream->free_mutex);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stream = flux ouvert en écriture à mettre à jour.            *
*                packet = données à transmettre.                              *
*                                                                             *
*  Description : Envoie un paquet à un serveur de débogage.                   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_debug_stream_send_packet(GDebugStream *stream, GDebugPacket *packet)
{
    bool result;                            /* Bilan à retourner           */

    result = stream->send_packet(stream, packet);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stream = flux de communication de débogage à consulter.      *
*                filter = éventuelle fonction de sélection du paquet.         *
*                data   = éventuelle donnée à associer au filtrage.           *
*                                                                             *
*  Description : Fournit un paquet reçu d'un serveur de débogage.             *
*                                                                             *
*  Retour      : Paquet de débogage.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDebugPacket *g_debug_stream_recv_packet(GDebugStream *stream, filter_packet_fc filter, void *data)
{
    GDebugPacket *result;                   /* Paquet à retourner          */

    g_mutex_lock(&stream->recv_mutex);

    if (filter != NULL)
    {
 gdsrp_try_again:

        for (result = stream->recv_packets;
             result != NULL;
             result = g_debug_packet_get_next_iter(stream->recv_packets, result))
        {
            if (filter(result, data))
            {
                g_debug_packet_extract(&stream->recv_packets, result);
                break;
            }
        }

        if (result == NULL)
        {
            g_cond_wait(&stream->recv_cond, &stream->recv_mutex);
            goto gdsrp_try_again;
        }

    }
    else
    {
        if (dl_list_empty(stream->recv_packets))
            g_cond_wait(&stream->recv_cond, &stream->recv_mutex);

        result = g_debug_packet_pop(&stream->recv_packets);

    }

    g_mutex_unlock(&stream->recv_mutex);

    return result;

}
