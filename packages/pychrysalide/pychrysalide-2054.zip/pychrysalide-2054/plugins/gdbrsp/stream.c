
/* Chrysalide - Outil d'analyse de fichiers binaires
 * stream.c - gestion des connexions aux serveurs GDB.
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


#include "stream.h"


#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <strings.h>
#include <glib/gthread.h>
#include <sys/select.h>


#include "gdb-int.h"
#include "stream-int.h"
#include "utils.h"
#include "../../common/dllist.h"
#include "../../core/logs.h"



/* Initialise la classe des flux de communication avec GDB. */
static void g_gdb_stream_class_init(GGdbStreamClass *);

/* Initialise une instance de flux de communication avec GDB. */
static void g_gdb_stream_init(GGdbStream *);

/* Supprime toutes les références externes. */
static void g_gdb_stream_dispose(GGdbStream *);

/* Procède à la libération totale de la mémoire. */
static void g_gdb_stream_finalize(GGdbStream *);

/* Envoie un acquittement pour la dernière réception. */
static bool gdb_stream_ack(GGdbStream *);

/* Ecoute une connexion à un serveur GDB. */
static void *gdb_stream_thread(GGdbStream *);

/* Reste en alerte quant au changement de statut de l'exécution. */
static void *gdb_stream_status_thread(GGdbStream *);

/* Réceptionne un paquet d'un serveur GDB. */
static bool g_gdb_stream_read_packet(GGdbStream *, GGdbPacket *);



/* Indique le type défini pour un flux de communication avec un serveur GDB. */
G_DEFINE_TYPE(GGdbStream, g_gdb_stream, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des flux de communication avec GDB.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_gdb_stream_class_init(GGdbStreamClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_gdb_stream_dispose;
    object->finalize = (GObjectFinalizeFunc)g_gdb_stream_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stream = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une instance de flux de communication avec GDB.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_gdb_stream_init(GGdbStream *stream)
{
    g_mutex_init(&stream->free_mutex);

    g_cond_init(&stream->recv_cond);
    g_mutex_init(&stream->recv_mutex);

    g_cond_init(&stream->status_cond);
    g_mutex_init(&stream->status_mutex);

    stream->skip_ack = false;

    stream->want_status = false;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stream = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_gdb_stream_dispose(GGdbStream *stream)
{
    g_object_unref(G_OBJECT(stream->owner));


    /* TODO... */


    G_OBJECT_CLASS(g_gdb_stream_parent_class)->dispose(G_OBJECT(stream));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stream = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_gdb_stream_finalize(GGdbStream *stream)
{

    /* TODO */


    G_OBJECT_CLASS(g_gdb_stream_parent_class)->finalize(G_OBJECT(stream));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stream = instance à modifier.                                *
*                                                                             *
*  Description : Ne participe plus aux acquitements de paquets.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_gdb_stream_do_not_ack(GGdbStream *stream)
{
    stream->skip_ack = true;

}



/******************************************************************************
*                                                                             *
*  Paramètres  : stream = instance à réellement lancer.                       *
*                                                                             *
*  Description : Lance l'écoute d'un flux de communication avec GDB.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_gdb_stream_listen(GGdbStream *stream)
{
    bool result;                            /* Bilan final à retourner     */

    result = true;

    if (!g_thread_new("chrysalide_gdb_stream", (GThreadFunc)gdb_stream_thread, stream))
        result = false;

    if (!g_thread_new("chrysalide_gdb_status", (GThreadFunc)gdb_stream_status_thread, stream))
        result = false;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stream = encadrement associée à l'opération.                 *
*                                                                             *
*  Description : Envoie un acquittement pour la dernière réception.           *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool gdb_stream_ack(GGdbStream *stream)
{
    ///
    //return true;

    bool result;                            /* Bilan à retourner           */
    GGdbPacket *packet;                     /* Paquet à envoyer            */

    packet = g_gdb_stream_get_free_packet(stream);

    g_gdb_packet_start_new_command(packet);
    g_gdb_packet_append(packet, "+");

    result = g_gdb_stream_send_packet(stream, packet);

    g_gdb_stream_mark_packet_as_free(stream, packet);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stream = encadrement associée à l'opération.                 *
*                                                                             *
*  Description : Ecoute une connexion à un serveur GDB.                       *
*                                                                             *
*  Retour      : ???                                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void *gdb_stream_thread(GGdbStream *stream)
{
    fd_set rfds;                            /* Liste des flux à surveiller */
    int ret;                                /* Bilan d'un appel            */
    GGdbPacket *packet;                     /* Nouveau paquet reçu         */


    const char *data;                       /* Données reçues à analyser   */
    size_t len;                             /* Quantité de ces données     */



    while (1)
    {
        FD_ZERO(&rfds);
        FD_SET(stream->fd, &rfds);

        ret = select(stream->fd + 1, &rfds, NULL, NULL, NULL);

        switch (ret)
        {
            case -1:
                perror("select()");
                break;

            case 0:
                break;

            default:

                packet = g_gdb_stream_get_free_packet(stream);

                g_gdb_packet_start_new_command(packet);

                if (g_gdb_stream_read_packet(stream, packet))
                {
                    /* Acquittement ? */
                    if (!stream->skip_ack)
                    {
                        if (!gdb_stream_ack(stream)) goto bad_recv;
                    }


                    /* On conserve le résultat ? */


                    g_gdb_packet_get_data(packet, &data, &len, NULL);


                    //printf("---------------------------\n");
                    //printf(">> want status ? %d\n", stream->want_status);
                    //printf(">> got '%s'\n", data);


                    if (len >= 1)
                    {
                        if (stream->want_status)
                            stream->want_status = false;

                        else if (index("STWX", data[0]) != NULL)
                        {
                            g_mutex_lock(&stream->status_mutex);
                            g_gdb_packet_push(&stream->status_packets, packet);
                            g_mutex_unlock(&stream->status_mutex);

                            g_cond_signal(&stream->status_cond);

                            break;
                        }

                        // else message inconnu -> log_message() !

                    }




                    g_mutex_lock(&stream->recv_mutex);
                    g_gdb_packet_push(&stream->recv_packets, packet);
                    g_mutex_unlock(&stream->recv_mutex);

                    g_cond_signal(&stream->recv_cond);

                }

                else
                    g_gdb_stream_mark_packet_as_free(stream, packet);

                break;

 bad_recv:

                printf("bad things happend...\n");

                g_gdb_stream_mark_packet_as_free(stream, packet);

                break;

        }

    }


    printf("Oh noes....\n");


    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stream = encadrement associée à l'opération.                 *
*                                                                             *
*  Description : Reste en alerte quant au changement de statut de l'exécution.*
*                                                                             *
*  Retour      : ???                                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void *gdb_stream_status_thread(GGdbStream *stream)
{
    GGdbPacket *packet;                     /* Nouveau paquet reçu         */
    const char *data;                       /* Données reçues à analyser   */
    size_t len;                             /* Quantité de ces données     */
    bool malformed;                         /* Echec d'interprétation      */
    uint8_t byte;                           /* Valeur quelconque sur 8 bits*/
    bool ret;                               /* Bilan d'un appel            */

    while (1)
    {
        /* Réception d'un nouveau paquet de statut */

        g_mutex_lock(&stream->status_mutex);

        if (dl_list_empty(stream->status_packets))
            g_cond_wait(&stream->status_cond, &stream->status_mutex);

        packet = g_gdb_packet_pop(&stream->status_packets);

        g_mutex_unlock(&stream->status_mutex);

        /* Traitement du paquet reçu */

        g_gdb_packet_get_data(packet, &data, &len, NULL);

        malformed = false;

        switch (data[0])
        {
            case 'S':

                ret = read_fixed_byte(data + 1, len - 1, &byte);

                if (!ret)
                {
                    malformed = true;
                    goto gsst_processed;
                }

                g_gdb_debugger_receive_signal_reply(stream->owner, byte);
                break;

            case 'T':
                assert(false);  // TODO
                break;

            case 'W':

                ret = read_fixed_byte(data + 1, len - 1, &byte);

                if (!ret)
                {
                    malformed = true;
                    goto gsst_processed;
                }


                // TODO : ";process:pid"


                printf("Program exited (status=%hhu)\n", byte);


                g_gdb_debugger_receive_exit_reply(stream->owner, byte, -1);


                // log_message en cas de mauvais format...


                break;


            default:
                assert(false);
                break;

        }

 gsst_processed:

        if (malformed && true/* TODO : config->show_... */)
            log_variadic_message(LMT_WARNING, "Malformed GDB status reply: '%s'", data);

        g_gdb_stream_mark_packet_as_free(stream, packet);

    }

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stream = flux de communication avec GDB à consulter.         *
*                                                                             *
*  Description : Fournit un paquet prêt à emploi.                             *
*                                                                             *
*  Retour      : Paquet prêt à emploi.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GGdbPacket *g_gdb_stream_get_free_packet(GGdbStream *stream)
{
    GGdbPacket *result;                     /* Paquet à retourner          */

    g_mutex_lock(&stream->free_mutex);

    if (dl_list_empty(stream->free_packets))
        result = g_gdb_packet_new();

    else
        result = g_gdb_packet_pop(&stream->free_packets);

    g_mutex_unlock(&stream->free_mutex);

    // ???
    //g_gdb_packet_start_new_command(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stream = flux de communication avec GDB à mettre à jour.     *
*                packet = paquet à considérer comme disponible.               *
*                                                                             *
*  Description : Place un paquet en attente d'une future utilisation.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_gdb_stream_mark_packet_as_free(GGdbStream *stream, GGdbPacket *packet)
{
    //// Utile ?
    g_gdb_packet_start_new_command(packet);


    g_mutex_lock(&stream->free_mutex);

    g_gdb_packet_push(&stream->free_packets, packet);

    g_mutex_unlock(&stream->free_mutex);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stream = flux ouvert en lecture  à utiliser.                 *
*                packet = données à recevoir.                                 *
*                                                                             *
*  Description : Réceptionne un paquet d'un serveur GDB.                      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_gdb_stream_read_packet(GGdbStream *stream, GGdbPacket *packet)
{
    bool result;                            /* Bilan à renvoyer            */
    char tmp[3];                            /* Tampon de réception         */
    uint8_t checksum;                       /* Contrôle d'intégrité        */

    do
    {
        result = stream->recv_byte(stream, tmp);
        if (tmp[0] != '+') break;
    }
    while (0);

    if (tmp[0] != '$') return false;

    tmp[1] = '\0';

    while ((result = stream->recv_byte(stream, tmp)))
    {
        //printf(" .. '%c'\n", tmp[0]);

        if (tmp[0] == '#') break;
        else g_gdb_packet_append(packet, tmp);
    }

    if (result)
    {
        result = stream->recv_byte(stream, &tmp[0]);
        result &= stream->recv_byte(stream, &tmp[1]);

        tmp[2] = 0;
        checksum = strtol(tmp, NULL, 16);

    }

    if (result)
        result = g_gdb_packet_verify_checksum(packet, checksum);

    if (result)
        result = g_gdb_packet_decode(packet);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stream = flux ouvert en écriture à mettre à jour.            *
*                packet = données à transmettre.                              *
*                                                                             *
*  Description : Envoie un paquet à un serveur GDB.                           *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/
#include <string.h>
bool g_gdb_stream_send_packet(GGdbStream *stream, GGdbPacket *packet)
{
    bool result;                            /* Bilan à renvoyer            */
    const char *data;                       /* Données à envoyer           */
    size_t len;                             /* Quantité de ces données     */
    uint8_t checksum;                       /* Contrôle d'intégrité        */
    char tmp[3];                            /* Impression du checksum      */

    g_gdb_packet_get_data(packet, &data, &len, NULL);

#if 1
    /* Ack ? */
    if (len == 1 && data[0] == '+')
        result = stream->send_data(stream, "+", 1);

    else
#endif
    {

    result = stream->send_data(stream, "$", 1);
    //result = stream->send_data(stream, "+$", 2);

    g_gdb_packet_compute_checksum(packet);
    g_gdb_packet_get_data(packet, &data, &len, &checksum);


    if (len == 1 && data[0] == '?')
        stream->want_status = true;

    /*
    if (memcmp(data, "vCont;c", strlen("vCont;c")) == 0)
        stream->want_status = true;
    */



    result &= stream->send_data(stream, data, len);

    result = stream->send_data(stream, "#", 1);

    snprintf(tmp, 3, "%02hhx", checksum);
    result &= stream->send_data(stream, tmp, 2);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stream = flux de communication avec GDB à consulter.         *
*                                                                             *
*  Description : Fournit un paquet reçu d'un serveur GDB.                     *
*                                                                             *
*  Retour      : Paquet GDB.                                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GGdbPacket *g_gdb_stream_recv_packet(GGdbStream *stream)
{
    GGdbPacket *result;                     /* Paquet à retourner          */

    g_mutex_lock(&stream->recv_mutex);

    if (dl_list_empty(stream->recv_packets))
        g_cond_wait(&stream->recv_cond, &stream->recv_mutex);

    result = g_gdb_packet_pop(&stream->recv_packets);

    g_mutex_unlock(&stream->recv_mutex);

    return result;

}
