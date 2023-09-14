
/* Chrysalide - Outil d'analyse de fichiers binaires
 * analyst.h - prototypes pour la connexion en analyste à un serveur Chrysalide
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


#ifndef _ANALYSIS_DB_ANALYST_H
#define _ANALYSIS_DB_ANALYST_H


#include <glib-object.h>
#include <stdbool.h>
#include <openssl/ssl.h>


#include "client.h"
#include "collection.h"
#include "misc/snapshot.h"
#include "../content.h"
#include "../loaded.h"




/* ------------------------------- GLUES POUR LA GLIB ------------------------------- */


#define G_TYPE_LOADING_STATUS_HINT g_loading_status_hint_type()


/* Définit un type GLib pour l'énumération "LoadingStatusHint". */
GType g_loading_status_hint_type(void);



/* ----------------------- DEFINITION D'ANALYSTE COMME CLIENT ----------------------- */


#define G_TYPE_ANALYST_CLIENT            g_analyst_client_get_type()
#define G_ANALYST_CLIENT(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_ANALYST_CLIENT, GAnalystClient))
#define G_IS_ANALYST_CLIENT(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_ANALYST_CLIENT))
#define G_ANALYST_CLIENT_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ANALYST_CLIENT, GAnalystClientClass))
#define G_IS_ANALYST_CLIENT_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ANALYST_CLIENT))
#define G_ANALYST_CLIENT_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ANALYST_CLIENT, GAnalystClientClass))


/* Description de client à l'écoute (instance) */
typedef struct _GAnalystClient GAnalystClient;

/* Description de client à l'écoute (classe) */
typedef struct _GAnalystClientClass GAnalystClientClass;


/* Indique le type défini pour une description de client à l'écoute. */
GType g_analyst_client_get_type(void);

/* Met en place un client pour une connexion à une BD. */
GAnalystClient *g_analyst_client_new(const char *, const char *, GList *, GLoadedContent *);

/* Envoie un contenu binaire pour conservation côté serveur. */
bool g_analyst_client_send_content(GAnalystClient *, GBinContent *);

/* Effectue une demande de sauvegarde de l'état courant. */
bool g_analyst_client_save(GAnalystClient *);

/* Ajoute un élément à la collection d'un serveur. */
bool g_analyst_client_add_item(GAnalystClient *, const GDbItem *);

/* Active les éléments en amont d'un horodatage donné. */
bool g_analyst_client_set_last_active(GAnalystClient *, timestamp_t);

/* Fournit la liste des instantanés existants. */
bool g_analyst_client_get_snapshots(GAnalystClient *, snapshot_info_t **, size_t *);

/* Fournit l'identifiant de l'instantané courant. */
bool g_analyst_client_get_current_snapshot(GAnalystClient *, snapshot_id_t *);

/* Définit l'identifiant de l'instantané courant. */
bool g_analyst_client_set_current_snapshot(GAnalystClient *, const snapshot_id_t *);

/* Définit la désignation d'un instantané donné. */
bool g_analyst_client_set_snapshot_name(GAnalystClient *, const snapshot_id_t *, const char *);

/* Définit la description d'un instantané donné. */
bool g_analyst_client_set_snapshot_desc(GAnalystClient *, const snapshot_id_t *, const char *);

/* Restaure un ancien instantané. */
bool g_analyst_client_restore_snapshot(GAnalystClient *, const snapshot_id_t *);

/* Crée un nouvel instantané à partir d'un autre. */
bool g_analyst_client_create_snapshot(GAnalystClient *);

/* Supprime un ancien instantané. */
bool g_analyst_client_remove_snapshot(GAnalystClient *, const snapshot_id_t *, bool);



#endif  /* _ANALYSIS_DB_ANALYST_H */
