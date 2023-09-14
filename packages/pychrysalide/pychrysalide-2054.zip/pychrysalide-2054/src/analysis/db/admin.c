
/* Chrysalide - Outil d'analyse de fichiers binaires
 * admin.c - connexion en administrateur à un serveur Chrysalide
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


#include "admin.h"


#include <assert.h>
#include <malloc.h>
#include <poll.h>
#include <string.h>


#include "client-int.h"
#include "../../common/leb128.h"
#include "../../core/logs.h"



/* Description de client à l'écoute (instance) */
struct _GAdminClient
{
    GHubClient parent;                      /* A laisser en premier        */

    char **binaries;                        /* Liste  de binaires existants*/
    size_t binaries_count;                  /* Taille de cette liste       */
    GMutex binaries_lock;                   /* Concurrence des accès       */

};

/* Description de client à l'écoute (classe) */
struct _GAdminClientClass
{
    GHubClientClass parent;                 /* A laisser en premier        */

    /* Signaux */

    void (* existing_binaries_updated) (GAdminClient *);

};


/* Initialise la classe des descriptions de fichier binaire. */
static void g_admin_client_class_init(GAdminClientClass *);

/* Initialise une description de fichier binaire. */
static void g_admin_client_init(GAdminClient *);

/* Supprime toutes les références externes. */
static void g_admin_client_dispose(GAdminClient *);

/* Procède à la libération totale de la mémoire. */
static void g_admin_client_finalize(GAdminClient *);

/* Assure l'accueil des nouvelles mises à jour. */
static void *g_admin_client_update(GAdminClient *);

/* Met à jour la liste des binaires existants. */
static bool g_admin_client_update_existing_binaries(GAdminClient *, packed_buffer_t *);



/* Indique le type défini pour une description de client à l'écoute. */
G_DEFINE_TYPE(GAdminClient, g_admin_client, G_TYPE_HUB_CLIENT);


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

static void g_admin_client_class_init(GAdminClientClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GHubClientClass *client;                /* Classe parente              */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_admin_client_dispose;
    object->finalize = (GObjectFinalizeFunc)g_admin_client_finalize;

    client = G_HUB_CLIENT_CLASS(klass);

    client->role = CRL_ADMIN;
    client->recv_func = (GThreadFunc)g_admin_client_update;

    g_signal_new("existing-binaries-updated",
                 G_TYPE_ADMIN_CLIENT,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GAdminClientClass, existing_binaries_updated),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__VOID,
                 G_TYPE_NONE, 0);

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

static void g_admin_client_init(GAdminClient *client)
{
    client->binaries = NULL;
    client->binaries_count = 0;
    g_mutex_init(&client->binaries_lock);

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

static void g_admin_client_dispose(GAdminClient *client)
{
    g_hub_client_stop(G_HUB_CLIENT(client));

    G_OBJECT_CLASS(g_admin_client_parent_class)->dispose(G_OBJECT(client));

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

static void g_admin_client_finalize(GAdminClient *client)
{
    size_t i;                               /* Boucle de parcours          */

    if (client->binaries != NULL)
    {
        for (i = 0; i < client->binaries_count; i++)
            free(client->binaries[i]);

        free(client->binaries);

    }

    g_mutex_clear(&client->binaries_lock);

    G_OBJECT_CLASS(g_admin_client_parent_class)->finalize(G_OBJECT(client));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prépare un client pour une connexion à une BD.               *
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'échec.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GAdminClient *g_admin_client_new(void)
{
    GAdminClient *result;                     /* Adresse à retourner         */

    result = g_object_new(G_TYPE_ADMIN_CLIENT, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : client = client pour les accès distants à manipuler.         *
*                                                                             *
*  Description : Assure l'accueil des nouvelles mises à jour.                 *
*                                                                             *
*  Retour      : NULL.                                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void *g_admin_client_update(GAdminClient *client)
{
    GHubClient *base;                       /* Base de l'instance          */
    struct pollfd fds[2];                   /* Surveillance des flux       */
    packed_buffer_t in_pbuf;                /* Tampon de réception         */
    int ret;                                /* Bilan d'un appel            */
    bool status;                            /* Bilan d'une opération       */
    uint32_t command;                       /* Commande de la requête      */
    //packed_buffer_t out_pbuf;               /* Tampon d'émission           */
    char *msg;                              /* Message d'erreur à imprimer */

    base = G_HUB_CLIENT(client);

    /**
     * Phase d'écoute continue...
     */

    fds[0].fd = base->stop_ctrl[0];
    fds[0].events = POLLIN | POLLPRI;

    fds[1].fd = SSL_get_fd(base->tls_fd);
    fds[1].events = POLLIN | POLLPRI;

    init_packed_buffer(&in_pbuf);

    while (true)
    {
        ret = poll(fds, 2, -1);
        if (ret == -1)
        {
            LOG_ERROR_N("poll");
            break;
        }

        /* Demande expresse d'arrêt des procédures */
        if (fds[0].revents)
            break;

        /* Le canal est fermé, une sortie doit être demandée... */
        if (fds[1].revents & POLLNVAL)
            break;

        /**
         * Même chose, cf. "TCP: When is EPOLLHUP generated?"
         * https://stackoverflow.com/questions/52976152/tcp-when-is-epollhup-generated/52976327#52976327
         */

        if (fds[1].revents & (POLLHUP | POLLRDHUP))
            break;

        if (fds[1].revents & (POLLIN | POLLPRI))
        {
            reset_packed_buffer(&in_pbuf);

            status = ssl_recv_packed_buffer(&in_pbuf, base->tls_fd);
            if (!status) goto bad_exchange;

 next_command:

            status = extract_packed_buffer(&in_pbuf, &command, sizeof(uint32_t), true);
            if (!status) goto bad_exchange;

            switch (command)
            {
                case DBC_EXISTING_BINARIES:
                    status = g_admin_client_update_existing_binaries(client, &in_pbuf);
                    if (!status) goto bad_exchange;
                    break;

                default:
                    log_variadic_message(LMT_INFO,
                                         _("This command is not available on this side: 0x%08x"), command);
                    goto bad_exchange;
                    break;

            }

            if (has_more_data_in_packed_buffer(&in_pbuf))
                goto next_command;

            continue;

 bad_exchange:

            asprintf(&msg, _("Bad reception from %s"), base->desc);

            LOG_ERROR(LMT_ERROR, msg);

            free(msg);

            break;

        }

    }

    g_hub_client_stop(G_HUB_CLIENT(client));

    exit_packed_buffer(&in_pbuf);

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : client = client pour les accès distants à manipuler.         *
*                                                                             *
*  Description : Effectue une demande de liste de binaires existants.         *
*                                                                             *
*  Retour      : true si la commande a bien été envoyée, false sinon.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_admin_client_request_existing_binaries(GAdminClient *client)
{
    bool result;                            /* Bilan partiel à remonter    */
    packed_buffer_t out_pbuf;               /* Tampon d'émission           */
    SSL *tls_fd;                            /* Canal de communication SSL  */

    init_packed_buffer(&out_pbuf);

    tls_fd = g_hub_client_get_ssl_fd(G_HUB_CLIENT(client));

    if (tls_fd == NULL)
        result = false;

    else
    {
        result = extend_packed_buffer(&out_pbuf, (uint32_t []) { DBC_LIST_BINARIES }, sizeof(uint32_t), true);

        if (result)
            result = ssl_send_packed_buffer(&out_pbuf, tls_fd);

        g_hub_client_put_ssl_fd(G_HUB_CLIENT(client), tls_fd);

    }

    exit_packed_buffer(&out_pbuf);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : client = client pour les accès distants à manipuler.         *
*                pbuf   = données présentes à traiter.                        *
*                                                                             *
*  Description : Met à jour la liste des binaires existants.                  *
*                                                                             *
*  Retour      : true si l'opération s'est déroulée sans encombre, ou false.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_admin_client_update_existing_binaries(GAdminClient *client, packed_buffer_t *pbuf)
{
    bool result;                            /* Validité à retourner        */
    size_t i;                               /* Boucle de parcours          */
    uleb128_t count;                        /* Nombre d'éléments détectés  */
    rle_string name;                        /* Nom à exporter              */

    result = true;

    g_mutex_lock(&client->binaries_lock);

    if (client->binaries != NULL)
    {
        for (i = 0; i < client->binaries_count; i++)
            free(client->binaries[i]);

        free(client->binaries);

        client->binaries = NULL;
        client->binaries_count = 0;

    }

    result = unpack_uleb128(&count, pbuf);
    if (!result) goto exit;

    client->binaries_count = count;

    if (count > 0)
    {
        client->binaries = calloc(client->binaries_count, sizeof(char *));

        for (i = 0; i < client->binaries_count; i++)
        {
            result = unpack_rle_string(&name, pbuf);
            if (!result) break;

            client->binaries[i] = strdup(name.data);

            exit_rle_string(&name);

        }

        if (i < client->binaries_count)
        {
            for (i = 0; i < client->binaries_count; i++)
                if (client->binaries[i] != NULL)
                    free(client->binaries[i]);

            free(client->binaries);

            client->binaries = NULL;
            client->binaries_count = 0;

        }

    }

 exit:

    g_mutex_unlock(&client->binaries_lock);

    if (result)
        g_signal_emit_by_name(client, "existing-binaries-updated");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : client = client pour les accès distants à manipuler.         *
*                count  = taille de la liste retournée. [OUT]                 *
*                                                                             *
*  Description : Fournit la liste des instantanés existants.                  *
*                                                                             *
*  Retour      : Liste de binaires en place ou NULL si aucun.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char **g_admin_client_get_existing_binaries(GAdminClient *client, size_t *count)
{
    char **result;                          /* Liste à retourner           */
    size_t i;                               /* Boucle de parcours          */

    result = NULL;
    *count = 0;

    g_mutex_lock(&client->binaries_lock);

    if (client->binaries_count > 0)
    {
        result = malloc(client->binaries_count * sizeof(char *));
        *count = client->binaries_count;

        for (i = 0; i < client->binaries_count; i++)
            result[i] = strdup(client->binaries[i]);

    }

    g_mutex_unlock(&client->binaries_lock);

    return result;

}
