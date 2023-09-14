
/* Chrysalide - Outil d'analyse de fichiers binaires
 * client.c - connexion à un serveur Chrysalide
 *
 * Copyright (C) 2014-2019 Cyrille Bagard
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


#include "client.h"


#include <assert.h>
#include <malloc.h>
#include <netdb.h>
#include <poll.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <openssl/err.h>


#include <i18n.h>


#include "client-int.h"
#include "auth.h"
#include "protocol.h"
#include "misc/rlestr.h"
#include "../../common/extstr.h"
#include "../../common/io.h"
#include "../../common/xdg.h"
#include "../../core/logs.h"



/* Initialise la classe des descriptions de fichier binaire. */
static void g_hub_client_class_init(GHubClientClass *);

/* Initialise une description de fichier binaire. */
static void g_hub_client_init(GHubClient *);

/* Supprime toutes les références externes. */
static void g_hub_client_dispose(GHubClient *);

/* Procède à la libération totale de la mémoire. */
static void g_hub_client_finalize(GHubClient *);

/* Format générique des adresses de connexion */
typedef union _gen_sockaddr_t
{
    struct sockaddr_in inet4_addr;          /* Adresse d'écoute IPv4       */
    struct sockaddr_in6 inet6_addr;         /* Adresse d'écoute IPv6       */
    struct sockaddr inet_4_6_addr;          /* Adresse d'écoute IPv4/6     */

} gen_sockaddr_t;

/* Démarre réellement la connexion à la base de données. */
static bool g_hub_client_start_common(GHubClient *, char *);



/* Indique le type défini pour une description de client à l'écoute. */
G_DEFINE_TYPE(GHubClient, g_hub_client, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des descriptions de fichier binaire.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_hub_client_class_init(GHubClientClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_hub_client_dispose;
    object->finalize = (GObjectFinalizeFunc)g_hub_client_finalize;

    klass->role = CRL_UNDEFINED;
    klass->complete_hello = NULL;
    klass->recv_func = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : client = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une description de fichier binaire.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_hub_client_init(GHubClient *client)
{
    client->working = NULL;

    client->tls_ctx = NULL;

    client->fd = -1;
    client->tls_fd = NULL;
    client->desc = NULL;

    g_mutex_init(&client->sending_lock);
    client->stop_ctrl[0] = -1;
    client->stop_ctrl[1] = -1;
    client->update = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : archive = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_hub_client_dispose(GHubClient *client)
{
    g_mutex_clear(&client->sending_lock);

    G_OBJECT_CLASS(g_hub_client_parent_class)->dispose(G_OBJECT(client));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : client = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_hub_client_finalize(GHubClient *client)
{
    if (client->working != NULL)
        free(client->working);

    assert(client->tls_ctx == NULL);
    assert(client->tls_fd == NULL);

    if (client->desc != NULL)
        free(client->desc);

    G_OBJECT_CLASS(g_hub_client_parent_class)->finalize(G_OBJECT(client));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : client = client pour les accès distants à manipuler.         *
*                                                                             *
*  Description : Démarre la connexion à la base de données interne.           *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_hub_client_start_internal(GHubClient *client)
{
    bool status;                            /* Bilan de la connexion       */
    struct sockaddr_un addr;                /* Adresse de transmission     */
    int ret;                                /* Bilan d'un appel            */
    char *desc;                             /* Description du serveur ciblé*/

    /* Identification du serveur à contacter */

    status = build_internal_server_socket(&addr);
    if (!status) goto fs_error;

    /* Création d'un canal de communication */

    client->fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (client->fd == -1)
    {
        LOG_ERROR_N("socket");
        goto fs_error;
    }

    ret = connect(client->fd, (struct sockaddr *)&addr, sizeof(struct sockaddr_un));
    if (ret == -1)
    {
        LOG_ERROR_N("connect");
        goto no_listening;
    }

    asprintf(&desc, "unix://%s", addr.sun_path);

    client->working = get_db_working_directory("clients", "standalone", NULL, NULL);

    status = g_hub_client_start_common(client, desc);

    if (!status)
        goto no_listening;

    return true;

 no_listening:

    close(client->fd);
    client->fd = -1;

 fs_error:

    return false;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : client = client pour les accès distants à manipuler.         *
*                host   = hôte à représenter pour le service.                 *
*                port   = port de connexion pour les clients.                 *
*                ipv6   = adopte une préférence pour les adresses IPv6.       *
*                                                                             *
*  Description : Démarre la connexion à la base de données distante.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_hub_client_start_remote(GHubClient *client, const char *host, const char *port, bool ipv6)
{
    struct addrinfo hints;                  /* Cadre de connexion souhaité */
    struct addrinfo *available;             /* Cadres de connexion dispos  */
    int ret;                                /* Bilan d'une consultation    */
    int domain;                             /* Domaine du canal            */
    struct addrinfo *iter;                  /* Boucle de parcours          */
    gen_sockaddr_t addr;                    /* Adresse d'écoute générique  */
    socklen_t sock_len;                     /* Taille de cette adresse     */
    char *desc;                             /* Description du serveur ciblé*/
    bool status;                            /* Bilan de la connexion       */

    /* Détermination du point d'écoute */

    memset(&hints, 0, sizeof(hints));

    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_protocol = IPPROTO_TCP;

    ret = getaddrinfo(host, port, &hints, &available);
    if (ret != 0)
    {
        LOG_ERROR_GAI_N("getaddrinfo", ret);
        goto no_target;
    }

    domain = AF_UNSPEC;

    /**
     * Premier tour : on essaie de se plier à la demande.
     */

    for (iter = available; iter != NULL && domain == AF_UNSPEC; iter = iter->ai_next)
    {
        if (ipv6 && iter->ai_family != AF_INET6)
            continue;

        if (!ipv6 && iter->ai_family != AF_INET)
            continue;

        domain = iter->ai_family;

        memcpy(&addr.inet_4_6_addr, iter->ai_addr, iter->ai_addrlen);
        sock_len = iter->ai_addrlen;

    }

    /**
     * Second tour : on fait avec ce qu'on a.
     */

    for (iter = available; iter != NULL && domain == AF_UNSPEC; iter = iter->ai_next)
    {
        if (iter->ai_family != AF_INET6 && iter->ai_family != AF_INET)
            continue;

        domain = iter->ai_family;

        memcpy(&addr.inet_4_6_addr, iter->ai_addr, iter->ai_addrlen);
        sock_len = iter->ai_addrlen;

    }

    if (available != NULL)
        freeaddrinfo(available);

    if (domain == AF_UNSPEC)
    {
        log_variadic_message(LMT_ERROR, _("No suitable address found for %s:%s"), host, port);
        goto no_target;
    }

    /* Création d'un canal de communication */

    client->fd = socket(domain, SOCK_STREAM, 0);
    if (client->fd == -1)
    {
        LOG_ERROR_N("socket");
        goto error_socket;
    }

    ret = connect(client->fd, (struct sockaddr *)&addr, sock_len);
    if (ret == -1)
    {
        LOG_ERROR_N("connect");
        goto no_listening;
    }

    asprintf(&desc, "%s:%s", host, port);

    client->working = get_db_working_directory("clients", host, port, NULL);

    status = g_hub_client_start_common(client, desc);

    if (!status)
        goto no_listening;

    return true;

 no_listening:

    close(client->fd);
    client->fd = -1;

 error_socket:
 no_target:

    return false;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : client = client pour les accès distants à manipuler.         *
*                host   = hôte à représenter pour le service.                 *
*                port   = port de connexion pour les clients.                 *
*                                                                             *
*  Description : Démarre réellement la connexion à la base de données.        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_hub_client_start_common(GHubClient *client, char *desc)
{
    const SSL_METHOD *method;               /* Mode du canal sécurisé      */
    char *filename;                         /* Fichier PEM à manipuler     */
    int ret;                                /* Bilan d'un appel            */
    char *rootdir;                          /* Racine pour le client       */
    GHubClientClass *class;                 /* Classe du client connecté   */
    packed_buffer_t out_pbuf;               /* Tampon d'émission           */
    bool status;                            /* Bilan d'une opération       */
    packed_buffer_t in_pbuf;                /* Tampon de réception         */
    uint32_t data;                          /* Mot de données lues         */
    DBError error;                          /* Validation de la connexion  */

    client->desc = desc;

    /* Définition d'un environnement TLS */

    method = TLS_client_method();

    client->tls_ctx = SSL_CTX_new(method);

    if (client->tls_ctx == NULL)
    {
        LOG_ERROR_OPENSSL;
        goto quick_error;
    }

    filename = strdup(client->working);
    filename = stradd(filename, "client-cert.pem");

    ret = SSL_CTX_use_certificate_file(client->tls_ctx, filename, SSL_FILETYPE_PEM);

    free(filename);

    if (ret != 1)
    {
        LOG_ERROR_OPENSSL;
        goto tls_error;
    }

    rootdir = get_db_working_directory("clients", NULL, NULL, NULL);

    filename = strdup(rootdir);
    filename = stradd(filename, "client-key.pem");

    ret = SSL_CTX_use_PrivateKey_file(client->tls_ctx, filename, SSL_FILETYPE_PEM);

    free(filename);
    free(rootdir);

    if (ret != 1)
    {
        LOG_ERROR_OPENSSL;
        goto tls_error;
    }

    /* Validation des certificats */

    SSL_CTX_set_verify(client->tls_ctx, SSL_VERIFY_PEER, NULL);

    filename = strdup(client->working);
    filename = stradd(filename, "ca-cert.pem");

    ret = SSL_CTX_load_verify_locations(client->tls_ctx, filename, NULL);

    free(filename);

    if (ret != 1)
    {
        LOG_ERROR_OPENSSL;
        goto tls_error;
    }

    /* Mise en place d'un canal de communication */

    client->tls_fd = SSL_new(client->tls_ctx);

    if (client->tls_fd == NULL)
    {
        LOG_ERROR_OPENSSL;
        goto tls_error;
    }

    SSL_set_fd(client->tls_fd, client->fd);

    ret = SSL_connect(client->tls_fd);

    if (ret != 1)
    {
        LOG_ERROR_OPENSSL;
        goto ssl_error;
    }

    class = G_HUB_CLIENT_GET_CLASS(client);

    /**
     * On réalise l'envoi initial ; le premier paquet doit contenir :
     *    - la commande 'DBC_HELO' ;
     *    - le numéro de version du client ;
     *    - le rôle attendu de la connexion ;
     *    - des données complémentaires éventuelles.
     *
     * Tout ceci est à synchroniser avec la fonction g_db_server_listener().
     */

    init_packed_buffer(&out_pbuf);

    status = extend_packed_buffer(&out_pbuf, (uint32_t []) { DBC_HELO }, sizeof(uint32_t), true);
    if (!status) goto setup_error;

    status = extend_packed_buffer(&out_pbuf, (uint32_t []) { CDB_PROTOCOL_VERSION }, sizeof(uint32_t), true);
    if (!status) goto setup_error;

    status = extend_packed_buffer(&out_pbuf, &class->role, sizeof(uint32_t), true);
    if (!status) goto setup_error;

    if (class->complete_hello != NULL)
    {
        status = class->complete_hello(client, &out_pbuf);
        if (!status) goto setup_error;
    }

    status = ssl_send_packed_buffer(&out_pbuf, client->tls_fd);
    if (!status) goto setup_error;

    /**
     * Le serveur doit répondre pour un message type :
     *    - la commande 'DBC_WELCOME' ;
     *    - un identifiant d'erreur ('DBE_NONE', 'DBE_BAD_EXCHANGE'
     *      ou 'DBE_WRONG_VERSION' ... 'DBE_LOADING_ERROR').
     */

    init_packed_buffer(&in_pbuf);

    status = ssl_recv_packed_buffer(&in_pbuf, client->tls_fd);
    if (!status) goto comm_error;

    status = extract_packed_buffer(&in_pbuf, &data, sizeof(uint32_t), true);
    if (!status) goto comm_error;

    if (data != DBC_WELCOME)
    {
        log_variadic_message(LMT_ERROR, _("The server '%s' did not welcome us!"), desc);
        goto comm_error;
    }

    status = extract_packed_buffer(&in_pbuf, &data, sizeof(uint32_t), true);
    if (!status) goto comm_error;

    error = data;

    switch (error)
    {
        case DBE_NONE:
            log_variadic_message(LMT_INFO, _("Connected to the server '%s'!"), desc);
            break;

        case DBE_WRONG_VERSION:
            log_variadic_message(LMT_ERROR, _("The server '%s' does not use our protocol version (0x%08x)..."),
                                 desc, CDB_PROTOCOL_VERSION);
            goto comm_error;
            break;

        case DBE_XML_VERSION_ERROR:
            log_variadic_message(LMT_ERROR, _("The archive from the server '%s' does not use our protocol version (0x%08x)..."),
                                 desc, CDB_PROTOCOL_VERSION);
            goto comm_error;
            break;

        case DBE_DB_LOADING_ERROR:
            log_variadic_message(LMT_ERROR, _("The server '%s' got into troubles while loading the database...."),
                                 desc);
            goto comm_error;
            break;

        default:
            log_variadic_message(LMT_ERROR, _("The server '%s' has run into an error (%u)..."),
                                 desc, error);
            goto comm_error;
            break;

    }

    ret = pipe(client->stop_ctrl);
    if (ret != 0)
    {
        LOG_ERROR_N("pipe");
        goto sys_error;
    }

    client->update = g_thread_try_new("cdb_client", class->recv_func, client, NULL);
    if (client->update == NULL)
    {
        log_variadic_message(LMT_ERROR, _("Failed to start a listening thread for the server '%s'!"),
                             desc);
        goto sys_error;
    }

    exit_packed_buffer(&out_pbuf);
    exit_packed_buffer(&in_pbuf);

    return true;

 sys_error:
 comm_error:

    exit_packed_buffer(&in_pbuf);

 setup_error:

    exit_packed_buffer(&out_pbuf);

 ssl_error:

    SSL_free(client->tls_fd);
    client->tls_fd = NULL;

 tls_error:

    SSL_CTX_free(client->tls_ctx);
    client->tls_ctx = NULL;

 quick_error:

    return false;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : client = client pour les accès distants à manipuler.         *
*                                                                             *
*  Description : Arrête la connexion à la base de données.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_hub_client_stop(GHubClient *client)
{
    int fd;                                 /* Canal à clôturer            */
    int ret;                                /* Bilan d'un appel            */
    ssize_t sent;                           /* Quantité de données émises  */

    /* Gestion du double appel */

    if (client->fd == -1)
    {
        /**
         * Si la fermture est forcée, le thread de traitement va terminer en erreur.
         * Donc cette fonction sera appelée deux fois. Seule la première va affecter
         * le contexte, donc on le peut pas s'assurer de la condition suivante dans
         * tous les cas.
         */

        /*assert(client->tls_ctx == NULL);*/
        return;
    }

    fd = client->fd;

    client->fd = -1;

    /* Ordre d'arrêt */

    if (g_thread_self() != client->update)
    {
        sent = write(client->stop_ctrl[1], "\xf0", 1);
        if (sent != 1) LOG_ERROR_N("write");

        g_thread_join(client->update);

    }

    /* Fermeture des flux */

    SSL_free(client->tls_fd);
    client->tls_fd = NULL;

    SSL_CTX_free(client->tls_ctx);
    client->tls_ctx = NULL;

    ret = close(fd);
    if (ret == -1) LOG_ERROR_N("close");

    ret = close(client->stop_ctrl[0]);
    if (ret == -1) LOG_ERROR_N("close");
    client->stop_ctrl[0] = -1;

    ret = close(client->stop_ctrl[1]);
    if (ret == -1) LOG_ERROR_N("close");
    client->stop_ctrl[1] = -1;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : client = client pour les accès distants à manipuler.         *
*                                                                             *
*  Description : Identifie le canal de communication pour envois au serveur.  *
*                                                                             *
*  Retour      : Descripteur de flux normalement ouvert.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

SSL *g_hub_client_get_ssl_fd(GHubClient *client)
{
    SSL *result;                            /* Canal à retourner           */
#ifndef NDEBUG
    int ret;                                /* Validation de transmission  */
#endif

    g_mutex_lock(&client->sending_lock);

    result = client->tls_fd;

    if (result == NULL)
        g_mutex_unlock(&client->sending_lock);

    else
    {
#ifndef NDEBUG
        ret = SSL_up_ref(result);
        assert(ret == 1);
#else
        SSL_up_ref(result);
#endif
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : client = client pour les accès distants à manipuler.         *
*                tls_fd = canal de communication SSL.                         *
*                                                                             *
*  Description : Marque le canal de communication comme disponible.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_hub_client_put_ssl_fd(GHubClient *client, SSL *tls_fd)
{
    g_mutex_unlock(&client->sending_lock);

    SSL_free(tls_fd);

}
