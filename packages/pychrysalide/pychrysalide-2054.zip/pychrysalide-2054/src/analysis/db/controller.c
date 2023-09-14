
/* Chrysalide - Outil d'analyse de fichiers binaires
 * controller.h - prototypes pour la gestion d'un ensemble d'archives au format CDB
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


#include "controller.h"


#include <assert.h>
#include <errno.h>
#include <dirent.h>
#include <malloc.h>
#include <poll.h>
#include <pthread.h>
#include <string.h>


#include <i18n.h>


#include "backend-int.h"
#include "misc/rlestr.h"
#include "../../common/leb128.h"
#include "../../common/packed.h"
#include "../../core/logs.h"



/* Description d'un contrôleur d'archives (instance) */
struct _GCdbController
{
    GServerBackend parent;                  /* A laisser en premier        */

    char *basedir;                          /* Répertoire du serveur       */

    SSL *tls_fd;                            /* Canal de communication      */
    char *peer_name;                        /* Désignation du correspondant*/
    char *user;                             /* Utilisateur connecté        */

};

/* Description d'un contrôleur d'archives (classe) */
struct _GCdbControllerClass
{
    GServerBackendClass parent;             /* A laisser en premier        */

};


/* Initialise la classe des contrôleurs d'archives. */
static void g_cdb_controller_class_init(GCdbControllerClass *);

/* Initialise un contrôleur d'archives. */
static void g_cdb_controller_init(GCdbController *);

/* Supprime toutes les références externes. */
static void g_cdb_controller_dispose(GCdbController *);

/* Procède à la libération totale de la mémoire. */
static void g_cdb_controller_finalize(GCdbController *);

/* Assure le traitement des requêtes de contrôle. */
static void *g_cdb_controller_process(GCdbController *);

/* Prend en compte une connexion nouvelle d'un utilisateur. */
static void g_cdb_controller_add_client(GCdbController *, SSL *, const char *, const char *);

/* Envoie au client la liste des binaires présents. */
static bool g_cdb_controller_send_existing_binaries(GCdbController *, packed_buffer_t *);



/* Indique le type défini pour une gestion d'archives. */
G_DEFINE_TYPE(GCdbController, g_cdb_controller, G_TYPE_SERVER_BACKEND);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des contrôleurs d'archives.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_cdb_controller_class_init(GCdbControllerClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GServerBackendClass *backend;           /* Classe parente              */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_cdb_controller_dispose;
    object->finalize = (GObjectFinalizeFunc)g_cdb_controller_finalize;

    backend = G_SERVER_BACKEND_CLASS(klass);

    backend->thread_name = "cdb_controller";
    backend->thread_func = (GThreadFunc)g_cdb_controller_process;

    backend->add_client = (add_backend_client_fc)g_cdb_controller_add_client;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : controller = instance à initialiser.                         *
*                                                                             *
*  Description : Initialise un contrôleur d'archives.                         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_cdb_controller_init(GCdbController *controller)
{
    controller->basedir = NULL;

    controller->tls_fd = NULL;
    controller->peer_name = NULL;
    controller->user = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : controller = instance d'objet GLib à traiter.                *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_cdb_controller_dispose(GCdbController *controller)
{
    g_server_backend_stop(G_SERVER_BACKEND(controller));

    G_OBJECT_CLASS(g_cdb_controller_parent_class)->dispose(G_OBJECT(controller));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : controller = instance d'objet GLib à traiter.                *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_cdb_controller_finalize(GCdbController *controller)
{
    if (controller->basedir != NULL)
        free(controller->basedir);

    if (controller->tls_fd != NULL)
        SSL_free(controller->tls_fd);

    if (controller->peer_name != NULL)
        free(controller->peer_name);

    if (controller->user != NULL)
        free(controller->user);

    G_OBJECT_CLASS(g_cdb_controller_parent_class)->finalize(G_OBJECT(controller));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : basedir = répertoire de stockage des enregistrements.        *
*                error   = indication éventuelle en cas d'échec. [OUT]        *
*                                                                             *
*  Description : Définit ou ouvre une archive d'éléments utilisateur.         *
*                                                                             *
*  Retour      : Structure mise en plae ou NULL en cas d'échec.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GCdbController *g_cdb_controller_new(const char *basedir, DBError *error)
{
    GCdbController *result;                 /* Adresse à retourner         */

    result = g_object_new(G_TYPE_CDB_CONTROLLER, NULL);

    result->basedir = strdup(basedir);

    *error = DBE_NONE;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : controller = centralisation de tous les savoirs.             *
*                                                                             *
*  Description : Assure le traitement des requêtes de contrôle.               *
*                                                                             *
*  Retour      : NULL.                                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void *g_cdb_controller_process(GCdbController *controller)
{
    GServerBackend *base;                   /* Base de l'instance          */
    struct pollfd fds[3];                   /* Surveillance des flux       */
    int ret;                                /* Bilan d'un appel            */
    packed_buffer_t in_pbuf;                /* Tampon de réception         */
    bool status;                            /* Bilan de lecture initiale   */
    uint32_t command;                       /* Commande de la requête      */
    packed_buffer_t out_pbuf;               /* Tampon d'émission           */
    char *msg;                              /* Erreur à faire remonter     */

    base = G_SERVER_BACKEND(controller);

    fds[0].fd = base->stop_ctrl[0];
    fds[0].events = POLLIN | POLLPRI;

    fds[1].fd = base->refresh_ctrl[0];
    fds[1].events = POLLIN | POLLPRI;

    fds[2].fd = SSL_get_fd(controller->tls_fd);
    fds[2].events = POLLIN | POLLPRI;

    while (1)
    {
        /* Lancement d'une phase de surveillance */

        ret = poll(fds, 3, -1);
        if (ret == -1)
        {
            if (errno == EINTR) continue;

            LOG_ERROR_N("poll");
            break;

        }

        /* Demande expresse d'arrêt des procédures */
        if (fds[0].revents)
            break;

        /* Demande d'actualisation ?! */
        assert(fds[1].revents == 0);

        /* Le canal est fermé, une sortie doit être demandée... */
        if (fds[2].revents & POLLNVAL)
            goto closed_exchange;

        /**
         * Même chose, cf. "TCP: When is EPOLLHUP generated?"
         * https://stackoverflow.com/questions/52976152/tcp-when-is-epollhup-generated/52976327#52976327
         */

        if (fds[2].revents & (POLLHUP | POLLRDHUP))
            goto closed_exchange;

        /* Données présentes en entrée */
        if (fds[2].revents & (POLLIN | POLLPRI))
        {
            init_packed_buffer(&in_pbuf);

            status = ssl_recv_packed_buffer(&in_pbuf, controller->tls_fd);
            if (!status) goto bad_exchange;

 next_command:

            status = extract_packed_buffer(&in_pbuf, &command, sizeof(uint32_t), true);
            if (!status) goto bad_exchange;

            switch (command)
            {
                case DBC_LIST_BINARIES:

                    init_packed_buffer(&out_pbuf);

                    status = extend_packed_buffer(&out_pbuf, (uint32_t []) { DBC_EXISTING_BINARIES },
                                                  sizeof(uint32_t), true);
                    if (!status) goto reply_error;

                    status = g_cdb_controller_send_existing_binaries(controller, &out_pbuf);
                    if (!status) goto reply_error;

                    status = ssl_send_packed_buffer(&out_pbuf, controller->tls_fd);
                    if (!status) goto reply_error;

                    exit_packed_buffer(&out_pbuf);

                    break;

                default:
                    asprintf(&msg, _("Bad protocol command: 0x%08x"), command);
                    LOG_ERROR(LMT_ERROR, msg);
                    free(msg);
                    goto bad_exchange;
                    break;

            }

            if (has_more_data_in_packed_buffer(&in_pbuf))
                goto next_command;

            exit_packed_buffer(&in_pbuf);

            continue;

 reply_error:

            exit_packed_buffer(&out_pbuf);

 bad_exchange:

            LOG_ERROR(LMT_ERROR, _("Bad exchange"));

            assert(0);

            exit_packed_buffer(&in_pbuf);

 closed_exchange:

            break;

        }

    }

    /* On disparaît des écrans... */

    g_server_backend_stop(G_SERVER_BACKEND(controller));

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : controller = support pour le suivi d'une connexion.          *
*                fd         = canal de communication réseau ouvert.           *
*                peer_name  = désignation de la connexion.                    *
*                user       = désignation de l'utilisateur de la connexion.   *
*                                                                             *
*  Description : Prend en compte une connexion nouvelle d'un utilisateur.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_cdb_controller_add_client(GCdbController *controller, SSL *fd, const char *peer_name, const char *user)
{
    controller->tls_fd = fd;

    controller->peer_name = strdup(peer_name);
    controller->user = strdup(user);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : controller = administration d'archives d'analyse.            *
*                pbuf       = paquet à consituer pour un envoi unique. [OUT]  *
*                                                                             *
*  Description : Envoie au client la liste des binaires présents.             *
*                                                                             *
*  Retour      : Bilan de constitution de la réponse.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_cdb_controller_send_existing_binaries(GCdbController *controller, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    DIR *directory;                         /* Répertoire de travail       */
    uleb128_t count;                        /* Nombre d'éléments détectés  */
    packed_buffer_t items;                  /* Liste des éléments trouvés  */
    struct dirent *item;                    /* Propriétés d'un élément     */
    rle_string name;                        /* Nom à exporter              */
    bool status;                            /* Bilan d'une inscription     */
    int ret;                                /* Bilan de fermture           */

    result = false;

    directory = opendir(controller->basedir);
    if (directory == NULL)
    {
        LOG_ERROR_N("opendir");

        if (errno == ENOENT)
        {
            count = 0;
            result = pack_uleb128(&count, pbuf);
        }

        goto bad_dir;

    }

    count = 0;
    init_packed_buffer(&items);

    for (item = readdir(directory); item != NULL; item = readdir(directory))
    {
        if (item->d_type != DT_DIR)
            continue;

        if (strcmp(item->d_name, ".") == 0 || strcmp(item->d_name, "..") == 0)
            continue;

        init_static_rle_string(&name, item->d_name);

        status = pack_rle_string(&name, &items);

        exit_rle_string(&name);

        if (!status)
            goto reg_error;

        count++;

    }

    result = pack_uleb128(&count, pbuf);

    if (result)
        result = include_packed_buffer(pbuf, &items);

 reg_error:

    exit_packed_buffer(&items);

    ret = closedir(directory);
    if (ret == -1) LOG_ERROR_N("closedir");

 bad_dir:

    return result;

}
