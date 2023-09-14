
/* Chrysalide - Outil d'analyse de fichiers binaires
 * analyst.c - connexion en analyste à un serveur Chrysalide
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


#include "analyst.h"


#include <assert.h>
#include <poll.h>
#include <string.h>


#include "analyst-int.h"
#include "../storage/storage.h"
#include "../../core/logs.h"



/* ----------------------- DEFINITION D'ANALYSTE COMME CLIENT ----------------------- */


/* Initialise la classe des descriptions de fichier binaire. */
static void g_analyst_client_class_init(GAnalystClientClass *);

/* Initialise une description de fichier binaire. */
static void g_analyst_client_init(GAnalystClient *);

/* Supprime toutes les références externes. */
static void g_analyst_client_dispose(GAnalystClient *);

/* Procède à la libération totale de la mémoire. */
static void g_analyst_client_finalize(GAnalystClient *);

/* Termine la constitution des données initiales à présenter. */
static bool g_analyst_client_complete_hello(GAnalystClient *, packed_buffer_t *);

/* Assure l'accueil des nouvelles mises à jour. */
static void *g_analyst_client_update(GAnalystClient *);

/* Met à jour la liste des instantanés courants. */
static bool g_analyst_client_update_snapshots(GAnalystClient *, packed_buffer_t *);

/* Met à jour l'identifiant de l'instantané courant. */
static bool g_analyst_client_update_current_snapshot(GAnalystClient *, packed_buffer_t *);



/* ------------------------- PRISES EN COMPTE DES COMMANDES ------------------------- */


/* Prend en compte une évolution du statut côté serveur. */
static bool g_analyst_client_handle_loading_hints(GAnalystClient *, packed_buffer_t *);



/* ---------------------------------------------------------------------------------- */
/*                                 GLUES POUR LA GLIB                                 */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Définit un type GLib pour l'énumération "LoadingStatusHint". *
*                                                                             *
*  Retour      : Type GLib enregistré.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GType g_loading_status_hint_type(void)
{
    static GType result = 0;

    static const GEnumValue values[] = {
        { LSH_READY, "LSH_READY", "ready" },
        { LSH_ON_WAIT_LIST, "LSH_ON_WAIT_LIST", "on_wait_list" },
        { LSH_NEED_CONTENT, "LSH_NEED_CONTENT", "need_content" },
        { LSH_NEED_FORMAT, "LSH_NEED_FORMAT", "need_format" },
        { LSH_NEED_ARCH, "LSH_NEED_ARCH", "need_arch" },
        { 0, NULL, NULL }
    };

    if (result == 0)
        result = g_enum_register_static(g_intern_static_string("LoadingStatusHint"), values);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                         DEFINITION D'ANALYSTE COMME CLIENT                         */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une description de client à l'écoute. */
G_DEFINE_TYPE(GAnalystClient, g_analyst_client, G_TYPE_HUB_CLIENT);


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

static void g_analyst_client_class_init(GAnalystClientClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GHubClientClass *client;                /* Classe parente              */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_analyst_client_dispose;
    object->finalize = (GObjectFinalizeFunc)g_analyst_client_finalize;

    client = G_HUB_CLIENT_CLASS(klass);

    client->role = CRL_ANALYST;
    client->complete_hello = (complete_client_hello_fc)g_analyst_client_complete_hello;
    client->recv_func = (GThreadFunc)g_analyst_client_update;

    g_signal_new("ready",
                 G_TYPE_ANALYST_CLIENT,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GAnalystClientClass, ready),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__VOID,
                 G_TYPE_NONE, 0);

    g_signal_new("server-status-changed",
                 G_TYPE_ANALYST_CLIENT,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GAnalystClientClass, server_status_changed),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__ENUM,
                 G_TYPE_NONE, 1, G_TYPE_LOADING_STATUS_HINT);

    g_signal_new("snapshots-updated",
                 G_TYPE_ANALYST_CLIENT,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GAnalystClientClass, snapshots_updated),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__VOID,
                 G_TYPE_NONE, 0);

    g_signal_new("snapshot-changed",
                 G_TYPE_ANALYST_CLIENT,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GAnalystClientClass, snapshot_changed),
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

static void g_analyst_client_init(GAnalystClient *client)
{
    client->cnt_hash = NULL;
    client->cnt_class = NULL;

    client->loaded = NULL;
    client->collections = NULL;

    client->can_get_updates = false;

    client->snapshots = NULL;
    client->snap_count = 0;
    g_mutex_init(&client->snap_lock);

    setup_empty_snapshot_id(&client->current);
    client->has_current = false;
    g_mutex_init(&client->cur_lock);

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

static void g_analyst_client_dispose(GAnalystClient *client)
{
    g_hub_client_stop(G_HUB_CLIENT(client));

    g_mutex_clear(&client->cur_lock);

    g_mutex_clear(&client->snap_lock);

    g_clear_object(&client->loaded);

    G_OBJECT_CLASS(g_analyst_client_parent_class)->dispose(G_OBJECT(client));

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

static void g_analyst_client_finalize(GAnalystClient *client)
{
    size_t i;                               /* Boucle de parcours          */

    if (client->cnt_hash != NULL)
        free(client->cnt_hash);

    if (client->cnt_class != NULL)
        free(client->cnt_class);

    if (client->snapshots != NULL)
    {
        for (i = 0; i < client->snap_count; i++)
            exit_snapshot_info(&client->snapshots[i]);

        free(client->snapshots);

    }

    G_OBJECT_CLASS(g_analyst_client_parent_class)->finalize(G_OBJECT(client));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : hash        = empreinte d'un binaire en cours d'analyse.     *
*                class       = nature de l'interprétation de ce contenu.      *
*                collections = ensemble de collections existantes.            *
*                loaded      = éventuel élément local préchargé.              *
*                                                                             *
*  Description : Met en place un client pour une connexion à une BD.          *
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'échec.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GAnalystClient *g_analyst_client_new(const char *hash, const char *class, GList *collections, GLoadedContent *loaded)
{
    GAnalystClient *result;                     /* Adresse à retourner         */
    bool status;                                /* Bilan de l'initialisation   */

    result = g_object_new(G_TYPE_ANALYST_CLIENT, NULL);

    status = g_analyst_client_setup(result, hash, class, collections, loaded);

    assert(status);

    if (!status)
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : client      = client pour les accès distants à initialiser.  *
*                hash        = empreinte d'un binaire en cours d'analyse.     *
*                class       = nature de l'interprétation de ce contenu.      *
*                collections = ensemble de collections existantes.            *
*                loaded      = éventuel élément local préchargé.              *
*                                                                             *
*  Description : Prépare un client pour une connexion à une BD.               *
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'échec.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_analyst_client_setup(GAnalystClient *client, const char *hash, const char *class, GList *collections, GLoadedContent *loaded)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    client->cnt_hash = strdup(hash);
    client->cnt_class = strdup(class);

    client->loaded = loaded;
    if (loaded != NULL) g_object_ref(G_OBJECT(loaded));

    client->collections = collections;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : client = client pour les accès distants à manipuler.         *
*                pbuf   = tampon d'émission initial à compléter.              *
*                                                                             *
*  Description : Termine la constitution des données initiales à présenter.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_analyst_client_complete_hello(GAnalystClient *client, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    rle_string str;                         /* Chaîne à communiquer        */

    init_static_rle_string(&str, client->cnt_hash);

    result = pack_rle_string(&str, pbuf);

    exit_rle_string(&str);

    init_static_rle_string(&str, client->cnt_class);

    result = pack_rle_string(&str, pbuf);

    exit_rle_string(&str);

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

static void *g_analyst_client_update(GAnalystClient *client)
{
    GHubClient *base;                       /* Base de l'instance          */
    packed_buffer_t out_pbuf;               /* Tampon d'émission           */
    bool status;                            /* Bilan d'une opération       */
    struct pollfd fds[2];                   /* Surveillance des flux       */
    packed_buffer_t in_pbuf;                /* Tampon de réception         */
    int ret;                                /* Bilan d'un appel            */
    uint32_t tmp32;                         /* Valeur sur 32 bits          */
    uint32_t command;                       /* Commande de la requête      */
    DBError error;                          /* Bilan d'une commande passée */
    GDbCollection *collec;                  /* Collection visée au final   */
    uint8_t tmp8;                           /* Valeur sur 8 bits           */
    char *msg;                              /* Message d'erreur à imprimer */

    base = G_HUB_CLIENT(client);

    /**
     * Avant toute chose, on demande un stage d'actualisation !
     */

    init_packed_buffer(&out_pbuf);

    status = extend_packed_buffer(&out_pbuf, (uint32_t []) { DBC_GET_SNAPSHOTS }, sizeof(uint32_t), true);
    if (!status)
    {
        exit_packed_buffer(&out_pbuf);
        goto exit;
    }

    status = extend_packed_buffer(&out_pbuf, (uint32_t []) { DBC_GET_CUR_SNAPSHOT }, sizeof(uint32_t), true);
    if (!status)
    {
        exit_packed_buffer(&out_pbuf);
        goto exit;
    }

    status = extend_packed_buffer(&out_pbuf, (uint32_t []) { DBC_GET_ALL_ITEMS }, sizeof(uint32_t), true);
    if (!status)
    {
        exit_packed_buffer(&out_pbuf);
        goto exit;
    }

    status = ssl_send_packed_buffer(&out_pbuf, base->tls_fd);
    if (!status)
    {
        log_simple_message(LMT_INFO, _("Failed to get all updates"));
        exit_packed_buffer(&out_pbuf);
        goto exit;
    }

    exit_packed_buffer(&out_pbuf);

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
            if (!status) goto gdcu_bad_exchange;

 next_command:

            status = extract_packed_buffer(&in_pbuf, &command, sizeof(uint32_t), true);
            if (!status) goto gdcu_bad_exchange;

            switch (command)
            {
                case DBC_LOADING_STATUS:
                    status = g_analyst_client_handle_loading_hints(client, &in_pbuf);
                    if (!status) goto gdcu_bad_exchange;
                    break;

                case DBC_SAVE:

                    status = extract_packed_buffer(&in_pbuf, &tmp32, sizeof(uint32_t), true);
                    if (!status) goto gdcu_bad_exchange;

                    error = tmp32;

                    if (error == DBE_NONE)
                        log_variadic_message(LMT_INFO, _("Archive saved for binary '%s'"), client->cnt_hash);
                    else
                        log_variadic_message(LMT_ERROR, _("Failed to save the archive for binary '%s'"),
                                             client->cnt_hash);

                    break;

                case DBC_COLLECTION:

                    status = extract_packed_buffer(&in_pbuf, &tmp32, sizeof(uint32_t), true);
                    if (!status) goto gdcu_bad_exchange;

                    collec = find_collection_in_list(client->collections, tmp32);
                    if (collec == NULL) goto gdcu_bad_exchange;

                    if (client->can_get_updates)
                        status = g_db_collection_unpack(collec, &in_pbuf, NULL);
                    else
                        status = _g_db_collection_unpack(collec, &in_pbuf, (DBAction []) { 0 }, NULL);

                    if (!status) goto gdcu_bad_exchange;

                    break;

                case DBC_GET_ALL_ITEMS:
                    log_variadic_message(LMT_INFO,
                                         _("This command is not available on this side: 0x%08x"), command);
                    goto gdcu_bad_exchange;
                    break;

                case DBC_SET_ALL_ITEMS:

                    status = extract_packed_buffer(&in_pbuf, &tmp8, sizeof(uint8_t), true);
                    if (!status) goto gdcu_bad_exchange;

                    client->can_get_updates = (tmp8 == 0x1);
                    break;

                case DBC_GET_SNAPSHOTS:
                    log_variadic_message(LMT_INFO,
                                         _("This command is not available on this side: 0x%08x"), command);
                    goto gdcu_bad_exchange;
                    break;

                case DBC_SNAPSHOTS_UPDATED:

                    status = g_analyst_client_update_snapshots(client, &in_pbuf);
                    if (!status) goto gdcu_bad_exchange;

                    break;

                case DBC_GET_CUR_SNAPSHOT:
                    log_variadic_message(LMT_INFO,
                                         _("This command is not available on this side: 0x%08x"), command);
                    goto gdcu_bad_exchange;
                    break;

                case DBC_CUR_SNAPSHOT_UPDATED:

                    status = g_analyst_client_update_current_snapshot(client, &in_pbuf);
                    if (!status) goto gdcu_bad_exchange;

                    break;

                case DBC_SET_CUR_SNAPSHOT:
                case DBC_SET_SNAPSHOT_NAME:
                case DBC_SET_SNAPSHOT_DESC:
                case DBC_CREATE_SNAPSHOT:
                case DBC_REMOVE_SNAPSHOT:
                    log_variadic_message(LMT_INFO,
                                         _("This command is not available on this side: 0x%08x"), command);
                    goto gdcu_bad_exchange;
                    break;

            }

            if (has_more_data_in_packed_buffer(&in_pbuf))
                goto next_command;

            client->can_get_updates = true;
            continue;

 gdcu_bad_exchange:

            asprintf(&msg, _("Bad reception from %s"), base->desc);

            LOG_ERROR(LMT_ERROR, msg);

            free(msg);

            break;

        }

    }

 exit:

    g_hub_client_stop(G_HUB_CLIENT(client));

    exit_packed_buffer(&in_pbuf);

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : client = client pour les accès distants à manipuler.         *
*                pbuf   = données présentes à traiter.                        *
*                                                                             *
*  Description : Met à jour la liste des instantanés courants.                *
*                                                                             *
*  Retour      : true si l'opération s'est déroulée sans encombre, ou false.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_analyst_client_update_snapshots(GAnalystClient *client, packed_buffer_t *pbuf)
{
    bool result;                            /* Validité à retourner        */
    size_t i;                               /* Boucle de parcours          */
    char id[SNAP_ID_HEX_SZ];                /* Caractères hexadécimaux     */
    snapshot_info_t info;                   /* Description d'instantané    */
    snapshot_info_t *dest;                  /* Destination de description  */

    result = true;

    g_mutex_lock(&client->snap_lock);

    if (client->snapshots != NULL)
    {
        for (i = 0; i < client->snap_count; i++)
            exit_snapshot_info(&client->snapshots[i]);

        free(client->snapshots);

        client->snapshots = NULL;
        client->snap_count = 0;

    }

    do
    {
        result = peek_packed_buffer(pbuf, id, SNAP_ID_HEX_SZ, false);
        if (!result) break;

        if (strncmp(id, SNAPSHOT_END_MARK, SNAP_ID_HEX_SZ) == 0)
        {
            advance_packed_buffer(pbuf, SNAP_ID_HEX_SZ);
            break;
        }

        else
        {
            setup_empty_snapshot_info(&info);

            result = unpack_snapshot_info(&info, pbuf);
            if (!result) break;

            client->snapshots = realloc(client->snapshots, ++client->snap_count * sizeof(snapshot_info_t));

            dest = &client->snapshots[client->snap_count - 1];

            setup_empty_snapshot_info(dest);
            copy_snapshot_info(dest, &info);

            exit_snapshot_info(&info);

        }

    }
    while (true);

    g_mutex_unlock(&client->snap_lock);

    if (result)
        g_signal_emit_by_name(client, "snapshots-updated");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : client = client pour les accès distants à manipuler.         *
*                pbuf   = données présentes à traiter.                        *
*                                                                             *
*  Description : Met à jour l'identifiant de l'instantané courant.            *
*                                                                             *
*  Retour      : true si l'opération s'est déroulée sans encombre, ou false.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_analyst_client_update_current_snapshot(GAnalystClient *client, packed_buffer_t *pbuf)
{
    bool result;                            /* Validité à retourner        */
    snapshot_id_t id;                       /* Identifiant d'instantané    */

    setup_empty_snapshot_id(&id);

    result = unpack_snapshot_id(&id, pbuf);

    if (result)
    {
        g_mutex_lock(&client->cur_lock);

        copy_snapshot_id(&client->current, &id);
        client->has_current = true;

        g_mutex_unlock(&client->cur_lock);

        g_signal_emit_by_name(client, "snapshot-changed");

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : client  = client pour les accès distants à manipuler.        *
*                content = contenu binaire à envoyer.                         *
*                                                                             *
*  Description : Envoie un contenu binaire pour conservation côté serveur.    *
*                                                                             *
*  Retour      : true si la commande a bien été envoyée, false sinon.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_analyst_client_send_content(GAnalystClient *client, GBinContent *content)
{
    bool result;                            /* Bilan partiel à remonter    */
    const gchar *hash;                      /* Empreinte du contenu fourni */
    packed_buffer_t cnt_pbuf;               /* Tampon de stockage          */
    GObjectStorage *storage;                /* Gestionnaire de stockage    */
    off64_t pos;                            /* Emplacement du binaire      */
    SSL *tls_fd;                            /* Canal de communication SSL  */
    packed_buffer_t out_pbuf;               /* Tampon d'émission           */

    result = false;

    /* Validation de la conformité du contenu */

    hash = g_binary_content_get_checksum(content);

    if (strcmp(hash, client->cnt_hash) != 0)
    {
        log_variadic_message(LMT_ERROR, _("Provided ontent does not match client content (hash: '%s')"),
                             client->cnt_hash);
        goto exit;
    }

    /* Conversion en format de stockage */

    init_packed_buffer(&cnt_pbuf);

    storage = g_object_storage_new(client->cnt_hash);

    result = g_object_storage_store_object(storage, "contents", G_SERIALIZABLE_OBJECT(content), &pos);
    if (!result) goto exit_with_failure;

    result = pack_uleb128((uleb128_t []){ pos }, &cnt_pbuf);
    if (!result) goto exit_with_failure;

    result = g_object_storage_store(storage, &cnt_pbuf);
    if (!result) goto exit_with_failure;

    /* Transmission */

    tls_fd = g_hub_client_get_ssl_fd(G_HUB_CLIENT(client));

    if (tls_fd == NULL)
        result = false;

    else
    {
        init_packed_buffer(&out_pbuf);

        result = extend_packed_buffer(&out_pbuf, (uint32_t []) { DBC_SET_CONTENT }, sizeof(uint32_t), true);

        if (result)
            result = pack_uleb128((uleb128_t []){ get_packed_buffer_payload_length(&cnt_pbuf) }, &out_pbuf);

        if (result)
            result = include_packed_buffer(&out_pbuf, &cnt_pbuf);

        if (result)
            result = ssl_send_packed_buffer(&out_pbuf, tls_fd);

        g_hub_client_put_ssl_fd(G_HUB_CLIENT(client), tls_fd);

        exit_packed_buffer(&out_pbuf);

    }

 exit_with_failure:

    g_object_unref(G_OBJECT(storage));

    exit_packed_buffer(&cnt_pbuf);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : client = client pour les accès distants à manipuler.         *
*                                                                             *
*  Description : Effectue une demande de sauvegarde de l'état courant.        *
*                                                                             *
*  Retour      : true si la commande a bien été envoyée, false sinon.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_analyst_client_save(GAnalystClient *client)
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
        result = extend_packed_buffer(&out_pbuf, (uint32_t []) { DBC_SAVE }, sizeof(uint32_t), true);

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
*                item   = élémnent à pousser vers un serveur de collection.   *
*                                                                             *
*  Description : Ajoute un élément à la collection d'un serveur.              *
*                                                                             *
*  Retour      : true si la commande a bien été envoyée, false sinon.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_analyst_client_add_item(GAnalystClient *client, const GDbItem *item)
{
    bool result;                            /* Bilan partiel à remonter    */
    packed_buffer_t out_pbuf;               /* Tampon d'émission           */
    SSL *tls_fd;                            /* Canal de communication SSL  */
    DBFeatures feature;                     /* Domaine de fonctionnalité   */
    GDbCollection *collec;                  /* Collection visée au final   */

    init_packed_buffer(&out_pbuf);

    tls_fd = g_hub_client_get_ssl_fd(G_HUB_CLIENT(client));

    if (tls_fd == NULL)
        result = false;

    else
    {
        feature = g_db_item_get_feature(item);

        collec = find_collection_in_list(client->collections, feature);
        if (collec == NULL)
        {
            result = false;
            goto bad_item_feature;
        }

        result = g_db_collection_pack(collec, &out_pbuf, DBA_ADD_ITEM, item);

        if (result)
            result = ssl_send_packed_buffer(&out_pbuf, tls_fd);

 bad_item_feature:

        g_hub_client_put_ssl_fd(G_HUB_CLIENT(client), tls_fd);

    }

    exit_packed_buffer(&out_pbuf);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : client    = client pour les accès distants à manipuler.      *
*                timestamp = date du dernier élément à garder comme actif.    *
*                                                                             *
*  Description : Active les éléments en amont d'un horodatage donné.          *
*                                                                             *
*  Retour      : true si la commande a bien été envoyée, false sinon.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_analyst_client_set_last_active(GAnalystClient *client, timestamp_t timestamp)
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
        result = extend_packed_buffer(&out_pbuf, (uint32_t []) { DBC_SET_LAST_ACTIVE }, sizeof(uint32_t), true);

        if (result)
            result = pack_timestamp(&timestamp, &out_pbuf);

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
*                info   = description des instantanés présents. [OUT]         *
*                count  = taille de la liste retournée. [OUT]                 *
*                                                                             *
*  Description : Fournit la liste des instantanés existants.                  *
*                                                                             *
*  Retour      : true si la liste retournée est valide, false sinon.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_analyst_client_get_snapshots(GAnalystClient *client, snapshot_info_t **info, size_t *count)
{
    bool result;                            /* Validité à retourner        */
    size_t i;                               /* Boucle de parcours          */
    snapshot_info_t *dest;                  /* Destination de description  */

    g_mutex_lock(&client->snap_lock);

    result = (client->snap_count > 0);

    if (result)
    {
        *info = malloc(client->snap_count * sizeof(snapshot_info_t));
        *count = client->snap_count;

        for (i = 0; i < client->snap_count; i++)
        {
            dest = &(*info)[i];

            setup_empty_snapshot_info(dest);
            copy_snapshot_info(dest, &client->snapshots[i]);

        }

    }

    g_mutex_unlock(&client->snap_lock);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : client = client pour les accès distants à manipuler.         *
*                id     = identifiant d'instantané à renseigner. [OUT]        *
*                                                                             *
*  Description : Fournit l'identifiant de l'instantané courant.               *
*                                                                             *
*  Retour      : true si l'identifiant retourné est valide, false sinon.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_analyst_client_get_current_snapshot(GAnalystClient *client, snapshot_id_t *id)
{
    bool result;                            /* Validité à retourner        */

    g_mutex_lock(&client->cur_lock);

    result = client->has_current;

    if (result)
        copy_snapshot_id(id, &client->current);

    g_mutex_unlock(&client->cur_lock);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : client = client pour les accès distants à manipuler.         *
*                id     = identifiant d'instantané à activer.                 *
*                                                                             *
*  Description : Définit l'identifiant de l'instantané courant.               *
*                                                                             *
*  Retour      : true si la commande a bien été envoyée, false sinon.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_analyst_client_set_current_snapshot(GAnalystClient *client, const snapshot_id_t *id)
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
        result = extend_packed_buffer(&out_pbuf, (uint32_t []) { DBC_SET_CUR_SNAPSHOT }, sizeof(uint32_t), true);

        if (result)
            result = pack_snapshot_id(id, &out_pbuf);

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
*                id     = identifiant d'instantané à traiter.                 *
*                name   = désignation humaine pour l'instantané.              *
*                                                                             *
*  Description : Définit la désignation d'un instantané donné.                *
*                                                                             *
*  Retour      : true si la commande a bien été envoyée, false sinon.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_analyst_client_set_snapshot_name(GAnalystClient *client, const snapshot_id_t *id, const char *name)
{
    bool result;                            /* Bilan partiel à remonter    */
    packed_buffer_t out_pbuf;               /* Tampon d'émission           */
    SSL *tls_fd;                            /* Canal de communication SSL  */
    rle_string string;                      /* Chaîne à transmettre        */

    init_packed_buffer(&out_pbuf);

    tls_fd = g_hub_client_get_ssl_fd(G_HUB_CLIENT(client));

    if (tls_fd == NULL)
        result = false;

    else
    {
        result = extend_packed_buffer(&out_pbuf, (uint32_t []) { DBC_SET_SNAPSHOT_NAME }, sizeof(uint32_t), true);

        if (result)
            result = pack_snapshot_id(id, &out_pbuf);

        if (result)
        {
            init_static_rle_string(&string, name);

            result = pack_rle_string(&string, &out_pbuf);

            exit_rle_string(&string);

        }

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
*                id     = identifiant d'instantané à traiter.                 *
*                desc   = description humaine pour l'instantané.              *
*                                                                             *
*  Description : Définit la description d'un instantané donné.                *
*                                                                             *
*  Retour      : true si la commande a bien été envoyée, false sinon.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_analyst_client_set_snapshot_desc(GAnalystClient *client, const snapshot_id_t *id, const char *desc)
{
    bool result;                            /* Bilan partiel à remonter    */
    packed_buffer_t out_pbuf;               /* Tampon d'émission           */
    SSL *tls_fd;                            /* Canal de communication SSL  */
    rle_string string;                      /* Chaîne à transmettre        */

    init_packed_buffer(&out_pbuf);

    tls_fd = g_hub_client_get_ssl_fd(G_HUB_CLIENT(client));

    if (tls_fd == NULL)
        result = false;

    else
    {
        result = extend_packed_buffer(&out_pbuf, (uint32_t []) { DBC_SET_SNAPSHOT_DESC }, sizeof(uint32_t), true);

        if (result)
            result = pack_snapshot_id(id, &out_pbuf);

        if (result)
        {
            init_static_rle_string(&string, desc);

            result = pack_rle_string(&string, &out_pbuf);

            exit_rle_string(&string);

        }

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
*                id     = identifiant d'instantané à traiter.                 *
*                                                                             *
*  Description : Restaure un ancien instantané.                               *
*                                                                             *
*  Retour      : true si la commande a bien été envoyée, false sinon.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_analyst_client_restore_snapshot(GAnalystClient *client, const snapshot_id_t *id)
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
        result = extend_packed_buffer(&out_pbuf, (uint32_t []) { DBC_SET_CUR_SNAPSHOT }, sizeof(uint32_t), true);

        if (result)
            result = pack_snapshot_id(id, &out_pbuf);

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
*                                                                             *
*  Description : Crée un nouvel instantané à partir d'un autre.               *
*                                                                             *
*  Retour      : true si la commande a bien été envoyée, false sinon.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_analyst_client_create_snapshot(GAnalystClient *client)
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
        result = extend_packed_buffer(&out_pbuf, (uint32_t []) { DBC_CREATE_SNAPSHOT }, sizeof(uint32_t), true);

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
*                id     = identifiant d'instantané à traiter.                 *
*                rec    = programme une suppression récursive.                *
*                                                                             *
*  Description : Supprime un ancien instantané.                               *
*                                                                             *
*  Retour      : true si la commande a bien été envoyée, false sinon.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_analyst_client_remove_snapshot(GAnalystClient *client, const snapshot_id_t *id, bool rec)
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
        result = extend_packed_buffer(&out_pbuf, (uint32_t []) { DBC_REMOVE_SNAPSHOT }, sizeof(uint32_t), true);

        if (result)
            result = pack_snapshot_id(id, &out_pbuf);

        if (result)
            result = extend_packed_buffer(&out_pbuf, (uint8_t []) { rec ? 0x1 : 0x0 }, sizeof(uint8_t), false);

        if (result)
            result = ssl_send_packed_buffer(&out_pbuf, tls_fd);

        g_hub_client_put_ssl_fd(G_HUB_CLIENT(client), tls_fd);

    }

    exit_packed_buffer(&out_pbuf);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                           PRISES EN COMPTE DES COMMANDES                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : archive  = archive à connecter avec un utilisateur.          *
*                in_pbuf  = paquet à consulter.                               *
*                                                                             *
*  Description : Prend en compte une évolution du statut côté serveur.        *
*                                                                             *
*  Retour      : Indication pour le maintien de la communication.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_analyst_client_handle_loading_hints(GAnalystClient *client, packed_buffer_t *in_pbuf)
{
    bool result;                            /* Bilan à retourner           */
    uleb128_t hint;                         /* Indication du serveur       */

    result = unpack_uleb128(&hint, in_pbuf);

    switch (hint)
    {
        case LSH_READY:
            g_signal_emit_by_name(client, "ready");
            break;

        case LSH_ON_WAIT_LIST:
            log_simple_message(LMT_INFO, _("Waiting for content from server..."));
            break;

        case LSH_NEED_CONTENT:
        case LSH_NEED_FORMAT:
        case LSH_NEED_ARCH:
            g_signal_emit_by_name(client, "server-status-changed", hint);
            break;

        default:
            log_variadic_message(LMT_ERROR,
                                 _("Unknown loaded hint received (%x); unsupported newer protocol?"),
                                 hint);
            result = false;
            break;

    }

    return result;

}
