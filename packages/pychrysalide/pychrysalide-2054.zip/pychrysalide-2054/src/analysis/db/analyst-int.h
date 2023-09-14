
/* Chrysalide - Outil d'analyse de fichiers binaires
 * analyst-int.h - prototypes pour la définition interne des connexions en analyste à un serveur Chrysalide
 *
 * Copyright (C) 2022 Cyrille Bagard
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


#ifndef _ANALYSIS_DB_ANALYST_INT_H
#define _ANALYSIS_DB_ANALYST_INT_H


#include "analyst.h"
#include "client-int.h"



/* Description de client à l'écoute (instance) */
struct _GAnalystClient
{
    GHubClient parent;                      /* A laisser en premier        */

    char *cnt_hash;                         /* Empreinte du binaire lié    */
    char *cnt_class;                        /* Interprétation du contenu   */

    GLoadedContent *loaded;                 /* Contenu chargé              */
    GList *collections;                     /* Collections d'un binaire    */

    bool can_get_updates;                   /* Réception de maj possibles ?*/

    snapshot_info_t *snapshots;             /* Liste des instantanés       */
    size_t snap_count;                      /* Taille de cette liste       */
    GMutex snap_lock;                       /* Concurrence des accès       */

    snapshot_id_t current;                  /* Instantané courant          */
    bool has_current;                       /* Validité de l'identifiant   */
    GMutex cur_lock;                        /* Concurrence des accès       */

};

/* Description de client à l'écoute (classe) */
struct _GAnalystClientClass
{
    GHubClientClass parent;                 /* A laisser en premier        */

    /* Signaux */

    void (* ready) (GAnalystClient *);
    void (* server_status_changed) (GAnalystClient *, LoadingStatusHint);
    void (* snapshots_updated) (GAnalystClient *);
    void (* snapshot_changed) (GAnalystClient *);

};


/* Prépare un client pour une connexion à une BD. */
bool g_analyst_client_setup(GAnalystClient *, const char *, const char *, GList *, GLoadedContent *);



#endif  /* _ANALYSIS_DB_ANALYST_INT_H */
