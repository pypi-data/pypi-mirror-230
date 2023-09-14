
/* Chrysalide - Outil d'analyse de fichiers binaires
 * support.c - conformité dans l'interfaçage client/serveur
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


#include "support.h"


#include <stdlib.h>
#include <string.h>



/* Indications quant à l'interfaçage client/serveur GDB (instance) */
struct _GGdbSupport
{
    GObject parent;                         /* A laisser en premier        */

    unsigned long packet_size;              /* Taille maximale d'un paquet */

    bool os_data;


    bool extended_mode;                     /* Mode étendu présent & actif */


    char *id;

};

/* Indications quant à l'interfaçage client/serveur GDB (classe) */
struct _GGdbSupportClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};


/* Initialise la classe des détails d'interfaçage GDB. */
static void g_gdb_support_class_init(GGdbSupportClass *);

/* Procède à l'initialisation des détails d'interfaçage GDB. */
static void g_gdb_support_init(GGdbSupport *);

/* Supprime toutes les références externes. */
static void g_gdb_support_dispose(GGdbSupport *);

/* Procède à la libération totale de la mémoire. */
static void g_gdb_support_finalize(GGdbSupport *);

/* Lit une valeur booléenne à partir des détails du serveur. */
static bool g_gdb_support_read_bool(GGdbSupport *, const char *, const char *, bool *);

/* Lit une valeur longue à partir des détails du serveur. */
static bool g_gdb_support_read_ulong(GGdbSupport *, const char *, const char *, unsigned long *);



/* Indique le type défini par la GLib pour les détails d'interfaçage GDB. */
G_DEFINE_TYPE(GGdbSupport, g_gdb_support, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe de débogueur à initialiser.                   *
*                                                                             *
*  Description : Initialise la classe des détails d'interfaçage GDB.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_gdb_support_class_init(GGdbSupportClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_gdb_support_dispose;
    object->finalize = (GObjectFinalizeFunc)g_gdb_support_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : support = instance de débogueur à préparer.                  *
*                                                                             *
*  Description : Procède à l'initialisation des détails d'interfaçage GDB.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_gdb_support_init(GGdbSupport *support)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : support = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_gdb_support_dispose(GGdbSupport *support)
{
    G_OBJECT_CLASS(g_gdb_support_parent_class)->dispose(G_OBJECT(support));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : support = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_gdb_support_finalize(GGdbSupport *support)
{
    G_OBJECT_CLASS(g_gdb_support_parent_class)->finalize(G_OBJECT(support));

}














#include <string.h>

static char *build_id(GGdbStream *stream)
{
    char *result;                           /* Identifiant à renvoyer      */
    GGdbPacket *packet;                     /* Paquet de communication     */
    bool status;                            /* Bilan d'une communication   */
    const char *data;                       /* Données reçues à analyser   */
    const char *start;                      /* Début d'identification      */
    const char *end;                        /* Fin d'identification        */

    result = NULL;

    /* Envoi de la requête */

    packet = g_gdb_stream_get_free_packet(stream);

    g_gdb_packet_start_new_command(packet);
    g_gdb_packet_append(packet, "?");

    status = g_gdb_stream_send_packet(stream, packet);

    if (!status)
        goto ggdgat_exit;

    /* Réception de la réponse */

    packet = g_gdb_stream_recv_packet(stream);

    g_gdb_packet_get_data(packet, &data, NULL, NULL);

    start = strstr(data, "thread:");
    if (start == NULL) goto ggdgat_exit;

    start += sizeof("thread:") - 1 /* '\0' */;

    end = strstr(start, ";");
    if (end == NULL) goto ggdgat_exit;

    result = strndup(start, end - start);

 ggdgat_exit:

    g_gdb_stream_mark_packet_as_free(stream, packet);

    return result;

}







/******************************************************************************
*                                                                             *
*  Paramètres  : stream = flux de communication ouvert avec le débogueur.     *
*                                                                             *
*  Description : Crée une définition des détails d'interfaçage GDB.           *
*                                                                             *
*  Retour      : Instance de détails mise en place ou NULL.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GGdbSupport *g_gdb_support_new(GGdbStream *stream)
{
    GGdbSupport *result;                    /* Débogueur à retourner       */
    GGdbPacket *packet;                     /* Paquet de communication GDB */


    //goto end;

    //goto skip;

    packet = g_gdb_stream_get_free_packet(stream);

    g_gdb_packet_start_new_command(packet);
    //g_gdb_packet_append(packet, "qSupported:multiprocess+;xmlRegisters");
    g_gdb_packet_append(packet, "qSupported");

    g_gdb_packet_append(packet, "qSupported:multiprocess+;swbreak+;hwbreak+;qRelocInsn+;fork-events+;vfork-events+;exec-events+;vContSupported+;QThreadEvents+;no-resumed+");


    bool test;

    const char *data;                       /* Données reçues à analyser   */
    size_t len;

    test = g_gdb_stream_send_packet(stream, packet);



    printf(" >> Paquet '%s' bien envoyé ? %s\n", "qSupported", test ? "oui" : "non");



    g_gdb_stream_mark_packet_as_free(stream, packet);

    packet = g_gdb_stream_recv_packet(stream);

    g_gdb_packet_get_data(packet, &data, &len, NULL);

    printf(" << Réception de '%s'\n", data);




    result = g_object_new(G_TYPE_GDB_SUPPORT, NULL);



    /* Découpage des éléments de réponse */

    char *answer;                           /* Réponse modifiable          */
    char *save;                             /* Sauvegarde de position      */
    char *token;                            /* Elément de réponse cerné    */

    answer = strdup(data);

    for (token = strtok_r(answer, ";", &save);
         token != NULL;
         token = strtok_r(NULL, ";", &save))
    {


        printf("TOKEN :: %s\n", token);

        if (g_gdb_support_read_ulong(result, token, "PacketSize", &result->packet_size))
            continue;

        if (g_gdb_support_read_bool(result, token, "qXfer:osdata:read", &result->os_data))
        {
            printf(" -->> %d\n", result->os_data);
            continue;
        }




    }

    free(answer);



    /**
     * Première chose : plus d'acquitement !
     *
     * Dans les faits, c'est impossible à gérer en asynchrone. Par exemple :
     *
     *  C> vCont;c
     *  C> g           Txx... <S
     *
     * Si le client envoie une commande en même temps que le serveur envoie
     * quelque chose, le serveur attend dans tous les cas un acquitement.
     * Donc il va consommer les données envoyées par le client jusqu'à y
     * trouver ce qu'il cherche.
     */

    /* Envoi de la requête */

    packet = g_gdb_stream_get_free_packet(stream);

    g_gdb_packet_start_new_command(packet);
    g_gdb_packet_append(packet, "QStartNoAckMode");

    test = g_gdb_stream_send_packet(stream, packet);

    g_gdb_stream_mark_packet_as_free(stream, packet);

    if (!test)
        goto ggsn_error;

    /* Réception de la réponse */

    packet = g_gdb_stream_recv_packet(stream);

    g_gdb_packet_get_data(packet, &data, NULL, NULL);

    if (strcmp(data, "OK") != 0)
        goto ggsn_error;

    g_gdb_stream_mark_packet_as_free(stream, packet);

    /* Désactivation des acquitements */

    g_gdb_stream_do_not_ack(stream);

    /**
     * Passage en mode étendu. C'est obligatoire pour pouvoir redémarrer un
     * programme débogué.
     */

    /* Envoi de la requête */

    packet = g_gdb_stream_get_free_packet(stream);

    g_gdb_packet_start_new_command(packet);
    g_gdb_packet_append(packet, "!");

    test = g_gdb_stream_send_packet(stream, packet);

    g_gdb_stream_mark_packet_as_free(stream, packet);

    if (!test)
        goto ggsn_error;

    /* Réception de la réponse */

    packet = g_gdb_stream_recv_packet(stream);

    g_gdb_packet_get_data(packet, &data, NULL, NULL);

    result->extended_mode = (strcmp(data, "OK") == 0);

    g_gdb_stream_mark_packet_as_free(stream, packet);




    result->id = build_id(stream);



#if 0
    //end:

#define CMD "?"


    packet = g_gdb_stream_get_free_packet(stream);

    g_gdb_packet_start_new_command(packet);
    //g_gdb_packet_append(packet, "qSupported:multiprocess+;xmlRegisters");
    g_gdb_packet_append(packet, CMD);


    test = g_gdb_stream_send_packet(stream, packet);



    printf(" >> Paquet '%s' bien envoyé ? %s\n", CMD, test ? "oui" : "non");



    g_gdb_stream_mark_packet_as_free(stream, packet);

    packet = g_gdb_stream_recv_packet(stream);

    g_gdb_packet_get_data(packet, &data, &len, NULL);

    printf(" << [pkt = %p ] Réception de '%s' (len=%d)\n", packet, data, (int)len);


#endif



    // qfThreadInfo


#undef CMD

    //#define CMD "qXfer:threads:read::0,1fff"
    //#define CMD "qXfer:btrace:read:all:0,1fff"
    //#define CMD "g"
    //#define CMD "m400000,8"
#define CMD "qsThreadInfo"

    packet = g_gdb_stream_get_free_packet(stream);

    g_gdb_packet_start_new_command(packet);
    //g_gdb_packet_append(packet, "qSupported:multiprocess+;xmlRegisters");
    g_gdb_packet_append(packet, CMD);


    test = g_gdb_stream_send_packet(stream, packet);



    printf(" >> Paquet '%s' bien envoyé ? %s\n", CMD, test ? "oui" : "non");



    g_gdb_stream_mark_packet_as_free(stream, packet);

    packet = g_gdb_stream_recv_packet(stream);

    g_gdb_packet_get_data(packet, &data, &len, NULL);

    printf(" << [pkt = %p ] Réception de '%s' (len=%d)\n", packet, data, (int)len);











    return result;

 ggsn_error:



    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : support = ensemble de détails à préciser.                    *
*                raw     = données brutes à parcourir.                        *
*                name    = désignation de la valeur recherchée.               *
*                value   = emplacement de la valeur à inscrire.               *
*                                                                             *
*  Description : Lit une valeur booléenne à partir des détails du serveur.    *
*                                                                             *
*  Retour      : true en cas d'affectation, false dans tous les autres cas.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_gdb_support_read_bool(GGdbSupport *support, const char *raw, const char *name, bool *value)
{
    bool result;                            /* Bilan à retourner           */
    size_t rlen;                            /* Taille de l'ensemble        */
    size_t nlen;                            /* Taille du nom               */

    rlen = strlen(raw);
    nlen = strlen(name);

    if ((nlen + 1) != rlen)
        return false;

    if (strncmp(raw, name, nlen) != 0)
        return false;

    switch (raw[nlen])
    {
        case '+':
            *value = true;
            result = true;
            break;

        case '-':
        case '?':
            *value = false;
            result = true;
            break;

        default:
            result = false;
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : support = ensemble de détails à préciser.                    *
*                raw     = données brutes à parcourir.                        *
*                name    = désignation de la valeur recherchée.               *
*                value   = emplacement de la valeur à inscrire.               *
*                                                                             *
*  Description : Lit une valeur longue à partir des détails du serveur.       *
*                                                                             *
*  Retour      : true en cas d'affectation, false dans tous les autres cas.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_gdb_support_read_ulong(GGdbSupport *support, const char *raw, const char *name, unsigned long *value)
{
    size_t rlen;                            /* Taille de l'ensemble        */
    size_t nlen;                            /* Taille du nom               */
    unsigned long v;                        /* Valeur récupérée à assigner */

    rlen = strlen(raw);
    nlen = strlen(name);

    if (strncmp(raw, name, nlen) != 0)
        return false;

    if (raw[nlen] != '=')
        return false;

    v = strtoul(raw + nlen + 1, NULL, 16);

    if (v == ULONG_MAX/* && errno == ERANGE*/)
        return false;

    *value = v;

    return true;

}






char *g_gdb_support_get_id(const GGdbSupport *support)
{
    return support->id;

}





