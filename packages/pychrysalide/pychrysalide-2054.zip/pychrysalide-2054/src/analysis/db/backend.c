
/* Chrysalide - Outil d'analyse de fichiers binaires
 * backend.c - suivi d'une connexion à un serveur
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


#include "backend.h"


#include <unistd.h>


#include "backend-int.h"
#include "../../core/logs.h"



/* Initialise la classe des supports pour suivi de connexion. */
static void g_server_backend_class_init(GServerBackendClass *);

/* Initialise un support pour suivi de connexion. */
static void g_server_backend_init(GServerBackend *);

/* Supprime toutes les références externes. */
static void g_server_backend_dispose(GServerBackend *);

/* Procède à la libération totale de la mémoire. */
static void g_server_backend_finalize(GServerBackend *);



/* Indique le type défini pour un Support de suivi de connexion. */
G_DEFINE_TYPE(GServerBackend, g_server_backend, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des supports pour suivi de connexion.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_server_backend_class_init(GServerBackendClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_server_backend_dispose;
    object->finalize = (GObjectFinalizeFunc)g_server_backend_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise un support pour suivi de connexion.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_server_backend_init(GServerBackend *backend)
{
    backend->stop_ctrl[0] = -1;
    backend->stop_ctrl[1] = -1;
    backend->refresh_ctrl[0] = -1;
    backend->refresh_ctrl[1] = -1;
    backend->process = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_server_backend_dispose(GServerBackend *backend)
{
    G_OBJECT_CLASS(g_server_backend_parent_class)->dispose(G_OBJECT(backend));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_server_backend_finalize(GServerBackend *backend)
{
    G_OBJECT_CLASS(g_server_backend_parent_class)->finalize(G_OBJECT(backend));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend   = support pour le suivi d'une connexion.           *
*                fd        = canal de communication réseau ouvert.            *
*                peer_name = désignation de la connexion.                     *
*                                                                             *
*  Description : Prend en compte une connexion nouvelle d'un utilisateur.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_server_backend_add_client(GServerBackend *backend, SSL *fd, const char *peer_name)
{
    GServerBackendClass *class;             /* Classe du support manipulé  */
    X509 *peer_cert;                        /* Certificat présenté         */
    char *user;                             /* Nom d'utilisateur associé   */
    int ret;                                /* Bilan d'un appel            */
    ssize_t sent;                           /* Quantité de données émises  */

    class = G_SERVER_BACKEND_GET_CLASS(backend);

    /* Ajout dans la liste officielle */

    peer_cert = SSL_get_peer_certificate(fd);

    user = X509_NAME_oneline(X509_get_subject_name(peer_cert), NULL, -1);

    X509_free(peer_cert);

    class->add_client(backend, fd, peer_name, user);

    free(user);

    /* Démarrage ou redémarrage du processus d'écoute */

    if (backend->process == NULL)
    {
        ret = pipe(backend->stop_ctrl);
        if (ret != 0)
        {
            LOG_ERROR_N("pipe");
            g_object_unref(G_OBJECT(backend));
            goto sys_error;
        }

        ret = pipe(backend->refresh_ctrl);
        if (ret != 0)
        {
            LOG_ERROR_N("pipe");
            g_object_unref(G_OBJECT(backend));
            goto sys_error;
        }

        backend->process = g_thread_new(class->thread_name, class->thread_func, backend);

 sys_error:

        ;

    }

    else
    {
        sent = write(backend->refresh_ctrl[1], "\xf0", 1);
        if (sent != 1) LOG_ERROR_N("write");
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = support pour le suivi d'une connexion.             *
*                                                                             *
*  Description : Met fin à un support de suivi.                               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_server_backend_stop(GServerBackend *backend)
{
    GThread *process;                       /* Procédure à terminer        */
    int ret;                                /* Bilan d'un appel            */
    ssize_t sent;                           /* Quantité de données émises  */

    /* Gestion du double appel */

    if (backend->process == NULL)
        return;

    process = backend->process;

    backend->process = NULL;

    /* Ordre d'arrêt */

    if (g_thread_self() != process)
    {
        sent = write(backend->stop_ctrl[1], "\xf0", 1);
        if (sent != 1) LOG_ERROR_N("write");

        g_thread_join(process);

    }

    /* Fermeture des flux */

    ret = close(backend->stop_ctrl[0]);
    if (ret == -1) LOG_ERROR_N("close");
    backend->stop_ctrl[0] = -1;

    ret = close(backend->stop_ctrl[1]);
    if (ret == -1) LOG_ERROR_N("close");
    backend->stop_ctrl[1] = -1;

    ret = close(backend->refresh_ctrl[0]);
    if (ret == -1) LOG_ERROR_N("close");
    backend->refresh_ctrl[0] = -1;

    ret = close(backend->refresh_ctrl[1]);
    if (ret == -1) LOG_ERROR_N("close");
    backend->refresh_ctrl[1] = -1;

}
