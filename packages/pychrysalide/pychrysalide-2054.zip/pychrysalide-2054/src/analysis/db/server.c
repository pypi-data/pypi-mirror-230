
/* Chrysalide - Outil d'analyse de fichiers binaires
 * server.c - mise en place d'un fournisseur d'éléments ajoutés
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


#include "server.h"


#include <assert.h>
#include <dirent.h>
#include <fcntl.h>
#include <malloc.h>
#include <netdb.h>
#include <poll.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <openssl/err.h>
#include <openssl/ssl.h>
#include <sys/file.h>


#include <i18n.h>


#include "auth.h"
#include "backend.h"
#include "cdb.h"
#include "controller.h"
#include "protocol.h"
#include "misc/rlestr.h"
#include "../../common/extstr.h"
#include "../../common/io.h"
#include "../../common/pathname.h"
#include "../../common/xdg.h"
#include "../../core/logs.h"



/* Format générique des adresses de connexion */
typedef union _gen_sockaddr_t
{
    struct sockaddr_un unix_addr;           /* Adresse d'écoute Unix       */
    struct sockaddr_in inet4_addr;          /* Adresse d'écoute IPv4       */
    struct sockaddr_in6 inet6_addr;         /* Adresse d'écoute IPv6       */
    struct sockaddr inet_4_6_addr;          /* Adresse d'écoute IPv4/6     */

} gen_sockaddr_t;


/* Assure que le point de connexion est vierge. */
typedef bool (* lock_server_socket_cb) (GHubServer *);

/* Assure que le point de connexion est rendu disponible. */
typedef void (* unlock_server_socket_cb) (GHubServer *);


/* Description de serveur à l'écoute (instance) */
struct _GHubServer
{
    GObject parent;                         /* A laisser en premier        */

    char *working;                          /* Répertoire de travail       */

    SSL_CTX *tls_ctx;                       /* Contexte du chiffrement     */

    int fd;                                 /* Canal de communication      */
    int domain;                             /* Domaine du canal            */
    gen_sockaddr_t addr;                    /* Adresse d'écoute générique  */
    socklen_t sock_len;                     /* Taille de cette adresse     */
    char *desc;                             /* Désignation du serveur      */

    lock_server_socket_cb lock_socket;      /* Procédure de nettoyage ?    */
    unlock_server_socket_cb unlock_socket;  /* Procédure de nettoyage ?    */
    int lock_fd;                            /* Eventuel verrou d'accès     */

    GThread *listener;                      /* Procédure de traitement     */

    GList *controllers;                     /* Liste des administrateurs   */
    GMutex ctrl_mutex;                      /* Verrou pour l'accès         */
    GList *archives;                        /* Liste des aanlystes         */
    GMutex ar_mutex;                        /* Verrou pour l'accès         */

    GMutex wait_mutex;                      /* Accès à la condition        */
    GCond wait_cond;                        /* Attente de signal           */

};

/* Description de serveur à l'écoute (classe) */
struct _GHubServerClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};


/* Indice pour le passage d'arguments */
static int _ssl_data_index = -1;


/* Initialise la classe des descriptions de fichier binaire. */
static void g_hub_server_class_init(GHubServerClass *);

/* Initialise une description de fichier binaire. */
static void g_hub_server_init(GHubServer *);

/* Supprime toutes les références externes. */
static void g_hub_server_dispose(GHubServer *);

/* Procède à la libération totale de la mémoire. */
static void g_hub_server_finalize(GHubServer *);

/* Assure que le point de connexion est vierge. */
static bool g_hub_server_lock_internal_socket(GHubServer *);

/* Assure que le point de connexion est rendu disponible. */
static void g_hub_server_unlock_internal_socket(GHubServer *);

/* Vérifie la légitimité d'une connexion sécurisée au serveur. */
static int g_hub_server_verify(int, X509_STORE_CTX *);

/* Assure l'accueil des nouveaux clients. */
static void *g_hub_server_listener(GHubServer *);

/* Assure l'accueil des nouveaux clients administrateurs. */
static GServerBackend *g_hub_server_handle_admin(GHubServer *, packed_buffer_t *, const char *, DBError *, bool *);

/* Assure l'accueil des nouveaux clients analystes. */
static GServerBackend *g_hub_server_handle_analyst(GHubServer *, packed_buffer_t *, const char *, DBError *, bool *);

/* Enregistre dans une liste interne un support de suivi. */
static void g_hub_server_register_backend(GHubServer *, GServerBackend *);

/* Suit les variations du compteur de références d'un greffon. */
static void on_backend_ref_toggle(GHubServer *, GServerBackend *, gboolean);



/* Indique le type défini pour une description de serveur à l'écoute. */
G_DEFINE_TYPE(GHubServer, g_hub_server, G_TYPE_OBJECT);


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

static void g_hub_server_class_init(GHubServerClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_hub_server_dispose;
    object->finalize = (GObjectFinalizeFunc)g_hub_server_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : server = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une description de fichier binaire.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_hub_server_init(GHubServer *server)
{
    server->working = NULL;

    server->tls_ctx = NULL;

    server->fd = -1;

    server->lock_socket = NULL;
    server->unlock_socket = NULL;
    server->lock_fd = -1;

    server->controllers = NULL;
    g_mutex_init(&server->ctrl_mutex);
    server->archives = NULL;
    g_mutex_init(&server->ar_mutex);

    g_mutex_init(&server->wait_mutex);
    g_cond_init(&server->wait_cond);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : server = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_hub_server_dispose(GHubServer *server)
{
    GList *iter;                            /* Boucle de parcours          */

    g_hub_server_stop(server);

    for (iter = g_list_first(server->controllers);
         iter != NULL;
         iter = g_list_first(server->controllers))
    {
        g_object_unref(G_OBJECT(iter->data));
    }

    g_mutex_clear(&server->ctrl_mutex);

    for (iter = g_list_first(server->archives);
         iter != NULL;
         iter = g_list_first(server->archives))
    {
        g_object_unref(G_OBJECT(iter->data));
    }

    g_mutex_clear(&server->ar_mutex);

    g_mutex_clear(&server->wait_mutex);
    g_cond_clear(&server->wait_cond);

    G_OBJECT_CLASS(g_hub_server_parent_class)->dispose(G_OBJECT(server));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : server = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_hub_server_finalize(GHubServer *server)
{
    int ret;                                /* Bilan d'un appel            */

    if (server->working != NULL)
        free(server->working);

    assert(server->tls_ctx == NULL);

    free(server->desc);

    if (server->lock_fd != -1)
    {
        ret = flock(server->lock_fd, LOCK_UN);
        if (ret == -1)
            LOG_ERROR_N("flock");

        ret = close(server->lock_fd);
        if (ret == -1)
            LOG_ERROR_N("close");

    }

    G_OBJECT_CLASS(g_hub_server_parent_class)->finalize(G_OBJECT(server));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prépare un serveur de BD pour les clients internes.          *
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'échec.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GHubServer *g_hub_server_new_internal(void)
{
    GHubServer *result;                     /* Adresse à retourner         */
    bool status;                            /* Bilan d'un chargement       */

    result = g_object_new(G_TYPE_HUB_SERVER, NULL);

    result->working = get_db_working_directory("servers", "standalone", NULL, NULL);

    /* Détermination du point d'écoute */

    result->domain = AF_UNIX;

    status = build_internal_server_socket(&result->addr.unix_addr);
    if (!status) goto sock_error;

    result->sock_len = sizeof(struct sockaddr_un);

    /* Désignation humaine */

    asprintf(&result->desc, "unix://%s", result->addr.unix_addr.sun_path);

    /* Aide pour une sortie propre ? */

    result->lock_socket = g_hub_server_lock_internal_socket;
    result->unlock_socket = g_hub_server_unlock_internal_socket;

    return result;

 sock_error:

    g_object_unref(G_OBJECT(result));

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : server = instance à consulter et préparer.                   *
*                                                                             *
*  Description : Assure que le point de connexion est vierge.                 *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_hub_server_lock_internal_socket(GHubServer *server)
{
    bool result;                            /* Bilan à faire remonter      */
    char *sock_path;                        /* Chemin vers le canal UNIX   */
    char *lock_path;                        /* Chemin vers le verrou       */
    int ret;                                /* Bilan d'un appel            */

    result = false;

    sock_path = server->addr.unix_addr.sun_path;

    /* Partie d'exclusivité */

    lock_path = strdup(sock_path);
    lock_path = stradd(lock_path, ".lock");

    assert(server->lock_fd == -1);

    server->lock_fd = open(lock_path, O_RDONLY | O_CREAT, 0600);
    if (server->lock_fd == -1)
    {
        LOG_ERROR_N("open");
        goto exit;
    }

    free(lock_path);

    ret = flock(server->lock_fd, LOCK_EX | LOCK_NB);

    result = (ret == 0);

    if (!result)
        goto exit;

    /* Partie de nettoye */

    ret = access(sock_path, F_OK);

    if (ret == 0)
    {
        ret = unlink(sock_path);

        if (ret != 0)
        {
            LOG_ERROR_N("unlink");

            ret = flock(server->lock_fd, LOCK_UN);
            if (ret == -1)
                LOG_ERROR_N("flock");

            ret = close(server->lock_fd);
            if (ret == -1)
                LOG_ERROR_N("close");

            result = false;

        }

    }

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : server = instance à consulter et nettoyer.                   *
*                                                                             *
*  Description : Assure que le point de connexion est rendu disponible.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_hub_server_unlock_internal_socket(GHubServer *server)
{
    int ret;                                /* Bilan d'un appel            */

    assert(server->lock_fd != -1);

    ret = flock(server->lock_fd, LOCK_UN);
    if (ret == -1)
        LOG_ERROR_N("flock");

    ret = close(server->lock_fd);
    if (ret == -1)
        LOG_ERROR_N("close");

    server->lock_fd = -1;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : host = désignation du serveur à lancer.                      *
*                port = port d'écoute à ouvrir.                               *
*                ipv6 = adopte une préférence pour les adresses IPv6.         *
*                                                                             *
*  Description : Prépare un serveur de BD pour les clients distants.          *
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'échec.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GHubServer *g_hub_server_new_remote(const char *host, const char *port, bool ipv6)
{
    GHubServer *result;                     /* Adresse à retourner         */
    struct addrinfo hints;                  /* Cadre de connexion souhaité */
    struct addrinfo *available;             /* Cadres de connexion dispos  */
    int ret;                                /* Bilan d'une consultation    */
    struct addrinfo *iter;                  /* Boucle de parcours          */
    size_t desclen;                         /* Taille de désignation       */
    struct sockaddr_in *addr4;              /* Adresse IPv4 brute          */
    struct sockaddr_in6 *addr6;             /* Adresse IPv6 brute          */
    const char *ip;                         /* Adresse IPv4 ou IPv6        */

    result = g_object_new(G_TYPE_HUB_SERVER, NULL);

    assert(host != NULL);

    if (port == NULL)
        port = "1337";

    result->working = get_db_working_directory("servers", host, port, NULL);

    /* Détermination du point d'écoute */

    memset(&hints, 0, sizeof(hints));

    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_protocol = IPPROTO_TCP;

    ret = getaddrinfo(host, port, &hints, &available);
    if (ret != 0)
    {
        LOG_ERROR_GAI_N("getaddrinfo", ret);
        goto error;
    }

    result->domain = AF_UNSPEC;

    /**
     * Premier tour : on essaie de se plier à la demande.
     */

    for (iter = available; iter != NULL && result->domain == AF_UNSPEC; iter = iter->ai_next)
    {
        if (ipv6 && iter->ai_family != AF_INET6)
            continue;

        if (!ipv6 && iter->ai_family != AF_INET)
            continue;

        result->domain = iter->ai_family;

        memcpy(&result->addr.inet_4_6_addr, iter->ai_addr, iter->ai_addrlen);
        result->sock_len = iter->ai_addrlen;

    }

    /**
     * Second tour : on fait avec ce qu'on a.
     */

    for (iter = available; iter != NULL && result->domain == AF_UNSPEC; iter = iter->ai_next)
    {
        if (iter->ai_family != AF_INET6 && iter->ai_family != AF_INET)
            continue;

        result->domain = iter->ai_family;

        memcpy(&result->addr.inet_4_6_addr, iter->ai_addr, iter->ai_addrlen);
        result->sock_len = iter->ai_addrlen;

    }

    if (available != NULL)
        freeaddrinfo(available);

    if (result->domain == AF_UNSPEC)
    {
        log_variadic_message(LMT_ERROR, _("No suitable address found for %s:%s"), host, port);
        goto error;
    }

    /* Désignation humaine */

    desclen = INET6_ADDRSTRLEN + 1 + strlen(port) + 1;
    result->desc = calloc(desclen, sizeof(char));

    if (result->domain == AF_INET)
    {
        addr4 = (struct sockaddr_in *)&result->addr.inet_4_6_addr;
        ip = inet_ntop(result->domain, &addr4->sin_addr, result->desc, INET6_ADDRSTRLEN);
    }

    else if (result->domain == AF_INET6)
    {
        addr6 = (struct sockaddr_in6 *)&result->addr.inet_4_6_addr;
        ip = inet_ntop(result->domain, &addr6->sin6_addr, result->desc, INET6_ADDRSTRLEN);
    }

    else
    {
        assert(false);
        ip = NULL;
    }

    if (ip == NULL)
    {
        LOG_ERROR_N("inet_ntop");
        goto error;
    }

    log_variadic_message(LMT_INFO, _("Resolved server IP: %s"), ip);

    snprintf(result->desc + strlen(ip), 1 + strlen(port) + 1, ":%s", port);

    return result;

 error:

    g_object_unref(G_OBJECT(result));

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : preverify_ok = état de la prévalidation.                     *
*                ctx          = contexte de la certification en cours.        *
*                                                                             *
*  Description : Vérifie la légitimité d'une connexion sécurisée au serveur.  *
*                                                                             *
*  Retour      : 1 si la connexion est validée, 0 sinon.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int g_hub_server_verify(int preverify_ok, X509_STORE_CTX *ctx)
{
    int result;                             /* Bilan à retourner           */
    X509 *peer_cert;                        /* Certificat côté client      */
    SSL *ssl;                               /* Structure de connexion SLL  */
    SSL_CTX *ssl_ctx;                       /* Contexte SSL du serveur     */
    GHubServer *server;                     /* Serveur concerné            */
    char *filename;                         /* Chemin d'accès reconstruit  */
    FILE *stream;                           /* Flux ouvert en lecture      */
    X509 *ca_cert;                          /* Certificat CA du serveur    */
    int status;                             /* Bilan d'une comparaison     */
    char *authorized_dir;                   /* Répertoire des autorisations*/
    DIR *dir;                               /* Répertoire à parcourir      */
    struct dirent *entry;                   /* Elément trouvé              */
    X509 *authorized_cert;                  /* Certificat de client validé */

    result = 0;

    peer_cert = X509_STORE_CTX_get_current_cert(ctx);

    /* Récupération du serveur interne */

    ssl = X509_STORE_CTX_get_ex_data(ctx, SSL_get_ex_data_X509_STORE_CTX_idx());
    ssl_ctx = SSL_get_SSL_CTX(ssl);

    server = SSL_CTX_get_ex_data(ssl_ctx, _ssl_data_index);
    assert(server != NULL);

    /* Test du certificat d'autorité */

    filename = strdup(server->working);
    filename = stradd(filename, "ca-cert.pem");

    stream = fopen(filename, "rb");
    if (stream == NULL) goto authorized;

    ca_cert = PEM_read_X509(stream, NULL, NULL, NULL);

    fclose(stream);

    status = X509_cmp(peer_cert, ca_cert);

    if (status == 0)
        result = 1;

    X509_free(ca_cert);

    free(filename);

    if (result == 1)
        goto verified;

    /* Détermination du répertoire des autorisations */

 authorized:

    authorized_dir = strdup(server->working);
    authorized_dir = stradd(authorized_dir, "authorized" G_DIR_SEPARATOR_S);

    dir = opendir(authorized_dir);
    if (dir == NULL) goto verified;

    /* Recherche d'une entrée de validation */

    while (result == 0)
    {
        entry = readdir(dir);

        if (entry == NULL)
        {
            if (errno != 0)
                LOG_ERROR_N("readdir");

            break;

        }

        if (entry->d_type != DT_REG && entry->d_type != DT_LNK) continue;
        if (entry->d_name[0] == '.') continue;

        filename = strdup(authorized_dir);
        filename = stradd(filename, G_DIR_SEPARATOR_S);
        filename = stradd(filename, entry->d_name);

        stream = fopen(filename, "rb");
        if (stream == NULL) goto next;

        authorized_cert = PEM_read_X509(stream, NULL, NULL, NULL);

        fclose(stream);

        status = X509_cmp(peer_cert, authorized_cert);

        if (status == 0)
            result = 1;

        X509_free(authorized_cert);

 next:

        free(filename);

    }

    /* Sortie */

    closedir(dir);

 verified:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : server = serveur pour les accès distants à manipuler.        *
*                                                                             *
*  Description : Assure l'accueil des nouveaux clients.                       *
*                                                                             *
*  Retour      : NULL.                                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void *g_hub_server_listener(GHubServer *server)
{
    struct pollfd fds;                      /* Surveillance des flux       */
    int ret;                                /* Bilan d'un appel            */
    gen_sockaddr_t peer;                    /* Adresse cliente             */
    int fd;                                 /* Canal établi vers un client */
    SSL *tls_fd;                            /* Même canal, mais sécurisé   */
    GServerBackend *backend;                /* Support de suivi créé       */
    const char *ip;                         /* Statut de la conversion     */
    char *peer_name;                        /* Désignation du correspondant*/
    DBError error;                          /* Validation de la connexion  */
    packed_buffer_t in_pbuf;                /* Tampon de réception         */
    bool status;                            /* Bilan d'une opération       */
    uint32_t cmd;                           /* Commande initiale lue       */
    uint32_t version;                       /* Version du client lue       */
    uint32_t role;                          /* Rôle visé par le client     */
    bool new;                               /* Besoin d'ajout à une liste  */
    packed_buffer_t out_pbuf;               /* Tampon d'émission           */

    fds.fd = server->fd;
    fds.events = POLLIN | POLLPRI;

    while (server->fd != -1)
    {
        ret = poll(&fds, 1, -1);
        if (ret != 1) continue;

        /* Le canal est fermé, une sortie doit être demandée... */
        if (fds.revents & POLLNVAL)
            break;

        /**
         * Même chose, cf. "TCP: When is EPOLLHUP generated?"
         * https://stackoverflow.com/questions/52976152/tcp-when-is-epollhup-generated/52976327#52976327
         */

        if (fds.revents & (POLLHUP | POLLRDHUP))
            break;

        if (fds.revents & (POLLIN | POLLPRI))
        {
            fd = accept(server->fd, (struct sockaddr *)&peer, (socklen_t []) { sizeof(gen_sockaddr_t) });
            if (fd == -1)
            {
                LOG_ERROR_N("accept");
                continue;
            }

            tls_fd = SSL_new(server->tls_ctx);

            if (tls_fd == NULL)
            {
                LOG_ERROR_OPENSSL;
                goto end_of_client;
            }

            SSL_set_fd(tls_fd, fd);

            ret = SSL_accept(tls_fd);

            if (ret != 1)
            {
                LOG_ERROR_OPENSSL;
                goto invalid_conn;
            }

            /* Construction d'une représentation */

            backend = NULL;

            if (*((sa_family_t *)&peer) == AF_UNIX)
                peer_name = strdup(server->desc);

            else if (*((sa_family_t *)&peer) == AF_INET)
            {
                peer_name = calloc(INET6_ADDRSTRLEN + 1 + 5 + 1, sizeof(char));

                ip = inet_ntop(AF_INET, &peer.inet4_addr.sin_addr, peer_name, INET6_ADDRSTRLEN);
                if (ip == NULL)
                {
                    LOG_ERROR_N("inet_ntop");
                    goto ip_error;
                }

                snprintf(peer_name + strlen(ip), 1 + 5, ":%hu", ntohs(peer.inet4_addr.sin_port));

            }

            else if (*((sa_family_t *)&peer) == AF_INET6)
            {
                peer_name = calloc(INET6_ADDRSTRLEN + 1 + 5 + 1, sizeof(char));

                ip = inet_ntop(AF_INET6, &peer.inet6_addr.sin6_addr, peer_name, INET6_ADDRSTRLEN);
                if (ip == NULL)
                {
                    LOG_ERROR_N("inet_ntop");
                    goto ip_error;
                }

                snprintf(peer_name + strlen(ip), 1 + 5, ":%hu", ntohs(peer.inet6_addr.sin6_port));

            }

            else
                goto invalid_conn;

            error = DBE_NONE;

            /**
             * Le premier "paquet" reçu de la part d'un client doit contenir les informations suivantes :
             *    - la commande 'DBC_HELO' ;
             *    - le numéro de version du client ;
             *    - le rôle attendu.
             *    - l'empreinte du binaire analysé.
             *
             * Tout ceci est à synchroniser avec la fonction g_db_client_start().
             */

            init_packed_buffer(&in_pbuf);

            status = ssl_recv_packed_buffer(&in_pbuf, tls_fd);
            if (!status)
            {
                log_variadic_message(LMT_ERROR, _("Error while getting the initial packet from '%s'..."),
                                     peer_name);
                error = DBE_BAD_EXCHANGE;
                goto error_receiving;
            }

            status = extract_packed_buffer(&in_pbuf, &cmd, sizeof(uint32_t), true);
            if (!status)
            {
                log_variadic_message(LMT_ERROR, _("Error while getting the initial command from '%s'..."),
                                     peer_name);
                error = DBE_BAD_EXCHANGE;
                goto error_receiving;
            }

            status = extract_packed_buffer(&in_pbuf, &version, sizeof(uint32_t), true);
            if (!status)
            {
                log_variadic_message(LMT_ERROR, _("Error while getting the protocol version from '%s'..."),
                                     peer_name);
                error = DBE_BAD_EXCHANGE;
                goto error_receiving;
            }

            status = extract_packed_buffer(&in_pbuf, &role, sizeof(uint32_t), true);
            if (!status)
            {
                log_variadic_message(LMT_ERROR, _("Error while getting the expected role from '%s'..."),
                                     peer_name);
                error = DBE_BAD_EXCHANGE;
                goto error_receiving;
            }

            if (cmd != DBC_HELO)
            {
                log_variadic_message(LMT_ERROR, _("The client from '%s' did not introduce itself!"),
                                     peer_name);
                error = DBE_BAD_EXCHANGE;
                goto error_receiving;
            }

            if (version != CDB_PROTOCOL_VERSION)
            {
                log_variadic_message(LMT_ERROR,
                                     _("The client from '%s' does not use the same protocol: 0x%08x vs 0x%08x..."),
                                     peer_name, be32toh(version), CDB_PROTOCOL_VERSION);
                error = DBE_WRONG_VERSION;
                goto error_receiving;
            }

            switch (role)
            {
                case CRL_ADMIN:
                    backend = g_hub_server_handle_admin(server, &in_pbuf, peer_name, &error, &new);
                    break;

                case CRL_ANALYST:
                    backend = g_hub_server_handle_analyst(server, &in_pbuf, peer_name, &error, &new);
                    break;

                default:
                    log_variadic_message(LMT_ERROR, _("Unknown client role 0x%x requested by '%s'"),
                                         role, peer_name);
                    backend = NULL;
                    error = DBE_BAD_EXCHANGE;
                    new = false;
                    break;

            }

            assert((backend == NULL && error != DBE_NONE) || (backend != NULL && error == DBE_NONE));

 error_receiving:

            /**
             * Le serveur doit répondre pour un message type :
             *    - la commande 'DBC_WELCOME' ;
             *    - un identifiant d'erreur.
             */

            exit_packed_buffer(&in_pbuf);

            init_packed_buffer(&out_pbuf);

            status = extend_packed_buffer(&out_pbuf, (uint32_t []) { DBC_WELCOME }, sizeof(uint32_t), true);
            if (!status) goto out_error;

            status = extend_packed_buffer(&out_pbuf, (uint32_t []) { error }, sizeof(uint32_t), true);
            if (!status) goto out_error;

            status = ssl_send_packed_buffer(&out_pbuf, tls_fd);
            if (!status) goto out_error;

            /**
             * L'ajout dans la liste des clients connectés provoque un envoi de mises à jour.
             * L'éventuelle erreur survenant pendant l'envoi ne peut donc pas être remontée
             * lors des échanges initiaux, car ces derniers seraient alors précédés des mises à jour...
             */

            if (backend != NULL)
            {
                if (new)
                    g_hub_server_register_backend(server, backend);

                g_server_backend_add_client(backend, tls_fd, peer_name);

            }

 out_error:

            if (backend != NULL)
                g_object_unref(G_OBJECT(backend));

            exit_packed_buffer(&out_pbuf);

 ip_error:

            free(peer_name);

            if (backend != NULL)
                continue;

 invalid_conn:

            SSL_free(tls_fd);

 end_of_client:

            close(fd);

        }

    }

    g_hub_server_stop(server);

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : server    = serveur pour les accès distants à manipuler.     *
*                in_pbuf   = reste des premières données reçues.              *
*                peer_name = désignation de la connexion entrante.            *
*                error     = code d'erreur issu du traitement. [OUT]          *
*                new       = indique si le résultat doit être ajouté. [OUT]   *
*                                                                             *
*  Description : Assure l'accueil des nouveaux clients administrateurs.       *
*                                                                             *
*  Retour      : Instance de support de suivi mise en place.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GServerBackend *g_hub_server_handle_admin(GHubServer *server, packed_buffer_t *in_pbuf, const char *peer_name, DBError *error, bool *new)
{
    GCdbController *result;                 /* Support de suivi à retourner*/
    char *basedir;                          /* Répertoire de stockage      */

    if (has_more_data_in_packed_buffer(in_pbuf))
    {
        log_variadic_message(LMT_ERROR, _("The client from '%s' provided too much data!"), peer_name);

        result = NULL;

        *error = DBE_BAD_EXCHANGE;
        *new = false;

    }
    else
    {
        basedir = strdup(server->working);
        basedir = stradd(basedir, "cdbs" G_DIR_SEPARATOR_S);

        result = g_cdb_controller_new(basedir, error);

        free(basedir);

        *new = true;

    }

    return G_SERVER_BACKEND(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : server    = serveur pour les accès distants à manipuler.     *
*                in_pbuf   = reste des premières données reçues.              *
*                peer_name = désignation de la connexion entrante.            *
*                error     = code d'erreur issu du traitement. [OUT]          *
*                new       = indique si le résultat doit être ajouté. [OUT]   *
*                                                                             *
*  Description : Assure l'accueil des nouveaux clients analystes.             *
*                                                                             *
*  Retour      : Instance de support de suivi mise en place.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GServerBackend *g_hub_server_handle_analyst(GHubServer *server, packed_buffer_t *in_pbuf, const char *peer_name, DBError *error, bool *new)
{
    GCdbArchive *result;                    /* Support de suivi à retourner*/
    rle_string hash;                        /* Empreinte du binaire visé   */
    rle_string class;                       /* Nature du contenu visé      */
    bool status;                            /* Bilan d'une opération       */
    GList *iter;                            /* Boucle de parcours          */
    GCdbArchive *archive;                   /* Destinataire final du client*/
    char *basedir;                          /* Répertoire de stockage      */
    char *tmpdir;                           /* Répertoire de travail       */

    result = NULL;

    *error = DBE_BAD_EXCHANGE;
    *new = false;

    /* Fin de réception des données envoyées */

    setup_empty_rle_string(&hash);

    status = unpack_rle_string(&hash, in_pbuf);
    if (!status)
    {
        log_variadic_message(LMT_ERROR, _("Error while getting the binary hash from '%s'..."), peer_name);
        goto error_receiving;
    }

    if (is_rle_string_empty(&hash))
    {
        log_variadic_message(LMT_ERROR, _("The submitted binary hash from '%s' is empty!"), peer_name);
        goto wrong_receiving_0;
    }

    setup_empty_rle_string(&class);

    status = unpack_rle_string(&class, in_pbuf);
    if (!status)
    {
        log_variadic_message(LMT_ERROR, _("Error while getting the content class from '%s'..."), peer_name);
        goto wrong_receiving_0;
    }

    if (is_rle_string_empty(&class))
    {
        log_variadic_message(LMT_ERROR, _("The submitted content class from '%s' is empty!"), peer_name);
        goto wrong_receiving_1;
    }

    if (has_more_data_in_packed_buffer(in_pbuf))
    {
        log_variadic_message(LMT_ERROR, _("The client from '%s' provided too much data!"), peer_name);
        goto wrong_receiving_1;
    }

    /* Recherche d'un support existant adapté */

    g_mutex_lock(&server->ar_mutex);

    for (iter = g_list_first(server->archives); iter != NULL; iter = g_list_next(iter))
    {
        archive = G_CDB_ARCHIVE(iter->data);

        if (g_cdb_archive_compare_is_suitable_for(archive, &hash, &class))
            break;

    }

    if (iter != NULL)
    {
        result = archive;
        g_object_ref(G_OBJECT(result));
    }

    g_mutex_unlock(&server->ar_mutex);

    /* Nouvelle création au besoin */

    if (result == NULL)
    {
        basedir = strdup(server->working);
        basedir = stradd(basedir, "cdbs" G_DIR_SEPARATOR_S);

        tmpdir = strdup(server->working);
        tmpdir = stradd(tmpdir, "tmp" G_DIR_SEPARATOR_S);

        result = g_cdb_archive_new(basedir, tmpdir, &hash, &class, error);

        free(tmpdir);
        free(basedir);

        *new = true;

    }

 wrong_receiving_1:

    exit_rle_string(&class);

 wrong_receiving_0:

    exit_rle_string(&hash);

 error_receiving:

    return (result != NULL ? G_SERVER_BACKEND(result) : NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : server  = serveur pour les accès distants à manipuler.       *
*                backend = support de suivi de connexion.                     *
*                                                                             *
*  Description : Enregistre dans une liste interne un support de suivi.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_hub_server_register_backend(GHubServer *server, GServerBackend *backend)
{
    GList **list;                           /* Liste à parcourir           */
    GMutex *mutex;                          /* Verrou à manipuler          */

    /* Sélection des éléments concernés */

    if (G_IS_CDB_CONTROLLER(backend))
    {
        list = &server->controllers;
        mutex = &server->ctrl_mutex;
    }
    else if (G_IS_CDB_ARCHIVE(backend))
    {
        list = &server->archives;
        mutex = &server->ar_mutex;
    }
    else
        assert(false);

    /* Retrait de l'élément inutilisé */

    g_mutex_lock(mutex);

    g_object_ref(G_OBJECT(backend));

    *list = g_list_append(*list, backend);

    g_object_add_toggle_ref(G_OBJECT(backend), (GToggleNotify)on_backend_ref_toggle, server);

    g_mutex_unlock(mutex);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : server  = serveur pour les accès distants à manipuler.       *
*                backend = support de suivi de connexion.                     *
*                last    = indication sur la valeur du compteur de références.*
*                                                                             *
*  Description : Suit les variations du compteur de références d'un greffon.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_backend_ref_toggle(GHubServer *server, GServerBackend *backend, gboolean last)
{
    GList **list;                           /* Liste à parcourir           */
    GMutex *mutex;                          /* Verrou à manipuler          */
    GList *iter;                            /* Boucle de parcours          */

    if (last)
    {
        /* Sélection des éléments concernés */

        if (G_IS_CDB_CONTROLLER(backend))
        {
            list = &server->controllers;
            mutex = &server->ctrl_mutex;
        }
        else if (G_IS_CDB_ARCHIVE(backend))
        {
            list = &server->archives;
            mutex = &server->ar_mutex;
        }
        else
            assert(false);

        /* Retrait de l'élément inutilisé */

        g_mutex_lock(mutex);

        for (iter = g_list_first(*list); iter != NULL; iter = g_list_first(*list))
        {
            *list = g_list_delete_link(*list, iter);
        }

        g_object_remove_toggle_ref(G_OBJECT(backend), (GToggleNotify)on_backend_ref_toggle, server);

        g_mutex_unlock(mutex);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : server  = serveur pour les accès distants à manipuler.       *
*                backlog = nombre de connexions maximal.                      *
*                keep    = conservation du serveur en avant plan.             *
*                                                                             *
*  Description : Démarre le serveur de base de données.                       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

ServerStartStatus g_hub_server_start(GHubServer *server, int backlog, bool keep)
{
    ServerStartStatus result;               /* Bilan à retourner           */
    const SSL_METHOD *method;               /* Mode du canal sécurisé      */
    char *filename;                         /* Fichier PEM à manipuler     */
    int ret;                                /* Bilan d'un appel            */
    STACK_OF(X509_NAME) *ca_cert;           /* Certificat de l'autorité    */
    bool status;                            /* Bilan d'un nettoyage        */

    result = SSS_FAILURE;

    /* Définition d'un environnement TLS */

    method = TLS_server_method();

    server->tls_ctx = SSL_CTX_new(method);

    if (server->tls_ctx == NULL)
    {
        LOG_ERROR_OPENSSL;
        goto quick_error;
    }

    filename = strdup(server->working);
    filename = stradd(filename, "server-cert.pem");

    ret = SSL_CTX_use_certificate_file(server->tls_ctx, filename, SSL_FILETYPE_PEM);

    free(filename);

    if (ret != 1)
    {
        LOG_ERROR_OPENSSL;
        goto tls_error;
    }

    filename = strdup(server->working);
    filename = stradd(filename, "server-key.pem");

    ret = SSL_CTX_use_PrivateKey_file(server->tls_ctx, filename, SSL_FILETYPE_PEM);

    free(filename);

    if (ret != 1)
    {
        LOG_ERROR_OPENSSL;
        goto tls_error;
    }

    ret = SSL_CTX_check_private_key(server->tls_ctx);

    if (ret != 1)
    {
        LOG_ERROR_OPENSSL;
        goto tls_error;
    }

    /* Validation des certificats */

    if (_ssl_data_index == -1)
    {
        _ssl_data_index = SSL_get_ex_new_index(0, NULL, NULL, NULL, NULL);
        assert(_ssl_data_index != -1);
    }

    ret = SSL_CTX_set_ex_data(server->tls_ctx, _ssl_data_index, server);
    if (ret != 1)
    {
        LOG_ERROR_OPENSSL;
        goto tls_error;
    }

    SSL_CTX_set_verify(server->tls_ctx, SSL_VERIFY_PEER | SSL_VERIFY_FAIL_IF_NO_PEER_CERT, g_hub_server_verify);

    filename = strdup(server->working);
    filename = stradd(filename, "ca-cert.pem");

    ca_cert = SSL_load_client_CA_file(filename);

    free(filename);

    if (ca_cert == NULL)
    {
        LOG_ERROR_OPENSSL;
        goto tls_error;
    }

    SSL_CTX_set_client_CA_list(server->tls_ctx, ca_cert);

    /* Mise en place d'un canal de communication */

    server->fd = socket(server->domain, SOCK_STREAM, 0);
    if (server->fd == -1)
    {
        LOG_ERROR_N("socket");
        return false;
    }

    ret = setsockopt(server->fd, SOL_SOCKET, SO_REUSEADDR, (int []) { 1 }, sizeof(int));
    if (ret == -1)
    {
        LOG_ERROR_N("setsockopt");
        goto network_error;
    }

    if (server->lock_socket != NULL)
    {
        status = server->lock_socket(server);
        if (!status)
        {
            result = SSS_ALREADY_RUNNING;
            goto network_error;
        }

    }

    ret = bind(server->fd, (struct sockaddr *)&server->addr, server->sock_len);
    if (ret == -1)
    {
        LOG_ERROR_N("bind");
        goto network_error;
    }

    ret = listen(server->fd, backlog);
    if (ret == -1)
    {
        LOG_ERROR_N("listen");
        goto network_error;
    }

    if (!keep)
    {
        ret = daemon(1, 1);
        if (ret != 0)
        {
            LOG_ERROR_N("daemon");
            goto network_error;
        }

    }

    server->listener = g_thread_new("cdb_listener", (GThreadFunc)g_hub_server_listener, server);

    log_variadic_message(LMT_PROCESS, _("Server started and listening at %s"), server->desc);

    result = SSS_SUCCESS;

    return result;

 network_error:

    close(server->fd);
    server->fd = -1;

 tls_error:

    SSL_CTX_free(server->tls_ctx);
    server->tls_ctx = NULL;

 quick_error:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : server = serveur pour les accès distants à consulter.        *
*                                                                             *
*  Description : Attend l'arrête du serveur de base de données.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_hub_server_wait_for_stop(GHubServer *server)
{
    g_mutex_lock(&server->wait_mutex);

    g_cond_wait(&server->wait_cond, &server->wait_mutex);

    g_mutex_unlock(&server->wait_mutex);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : server = serveur pour les accès distants à manipuler.        *
*                                                                             *
*  Description : Arrête le serveur de base de données.                        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_hub_server_stop(GHubServer *server)
{
    int fd;                                 /* Canal à clôturer            */
    int ret;                                /* Bilan d'un appel            */

    /* Canal de communication */

    if (server->fd == -1)
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

    fd = server->fd;

    server->fd = -1;

    ret = shutdown(fd, SHUT_RDWR);
    if (ret == -1) LOG_ERROR_N("shutdown");

    ret = close(fd);
    if (ret == -1) LOG_ERROR_N("close");

    g_thread_join(server->listener);

    /* Verrou d'accès */

    if (server->unlock_socket != NULL)
        server->unlock_socket(server);

    /* Environnement TLS */

    SSL_CTX_free(server->tls_ctx);
    server->tls_ctx = NULL;

    /* Fin de service */

    g_mutex_lock(&server->wait_mutex);
    g_cond_signal(&server->wait_cond);
    g_mutex_unlock(&server->wait_mutex);

}
