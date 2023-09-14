
/* Chrysalide - Outil d'analyse de fichiers binaires
 * snapshot.c - prototypes gestion des instantanés de bases de données
 *
 * Copyright (C) 2019 Cyrille Bagard
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


#include "snapshot.h"


#include <assert.h>
#include <malloc.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>


#include <i18n.h>


#include "collection.h"
#include "../../common/compression.h"
#include "../../common/extstr.h"
#include "../../common/sqlite.h"
#include "../../common/xml.h"
#include "../../core/logs.h"



/* ------------------------ GESTION UNITAIRE DES INSTANTANES ------------------------ */


/* Caractéristiques d'un instantané */
typedef struct _snapshot_node_t
{
    struct _snapshot_node_t *parent;        /* Parent hiérarchique         */

    snapshot_info_t info;                   /* Détails de l'instantané     */

    char *path;                             /* Fichier extrait             */

    struct _snapshot_node_t **children;     /* Sous-noeuds rattachés       */
    size_t count;                           /* Quantité de ces noeuds      */

} snapshot_node_t;


/* Constitue un nouveau noeud d'instantané. */
static snapshot_node_t *create_snapshot_node(const char *, uint64_t, const char *, const char *);

/* Libère la mémoire occupée par un noeud d'instantané. */
static void destroy_snapshot_node(snapshot_node_t *);

/* Définit le chemin vers une base de données pour un noeud. */
static bool setup_snapshot_node_db_path(snapshot_node_t *, const GCdbArchive *);

/* Valide la présence d'une base de données pour chaque noeud. */
static bool check_snapshot_nodes(const snapshot_node_t *);

/* Enregistre tous les éléments associés aux instantanés. */
static DBError save_snapshot_node(const snapshot_node_t *, xmlDocPtr, xmlXPathContextPtr, struct archive *);

/* Recherche le noeud d'instantané lié à un identifiant. */
static snapshot_node_t *find_snapshot_node(snapshot_node_t *, const snapshot_id_t *);

/* Détermine si un instantané est compris dans une branche. */
static bool contain_snapshot_node(const snapshot_node_t *, const snapshot_node_t *);

/* Ajoute un instantané comme prolongement d'un instantané. */
static void add_snapshot_node(snapshot_node_t *, snapshot_node_t *);

/* Fait disparaître un instantané dans une arborescence. */
static void remove_snapshot_node(snapshot_node_t *, bool);

/* Collecte les descriptions d'une arborescence d'instantanés. */
static bool pack_snapshot_node(const snapshot_node_t *, packed_buffer_t *);



/* --------------------- MANIPULATIONS D'ENSEMBLE D'INSTANTANES --------------------- */


/* Gestionnaire d'instantanés de bases de données (instance) */
struct _GDbSnapshot
{
    GObject parent;                         /* A laisser en premier        */

    snapshot_node_t *nodes;                 /* Instantanés présents        */
    snapshot_node_t *current;               /* Instantané courant          */

    char *current_db;                       /* Base de données SQLite      */

};

/* Gestionnaire d'instantanés de bases de données (classe) */
struct _GDbSnapshotClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};


/* Initialise la classe des gestionnaires d'instantanés. */
static void g_db_snapshot_class_init(GDbSnapshotClass *);

/* Initialise un gestionnaire d'instantanés de base de données. */
static void g_db_snapshot_init(GDbSnapshot *);

/* Supprime toutes les références externes. */
static void g_db_snapshot_dispose(GDbSnapshot *);

/* Procède à la libération totale de la mémoire. */
static void g_db_snapshot_finalize(GDbSnapshot *);

/* Prépare un gestionnaire d'instantanés de bases de données. */
static GDbSnapshot *g_db_snapshot_new(const GCdbArchive *);



/* ---------------------------------------------------------------------------------- */
/*                          GESTION UNITAIRE DES INSTANTANES                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : id      = source de données éventuelle pour l'identifiant.   *
*                created = source de données pour la date de création.        *
*                name    = source de données éventuelle pour le nom.          *
*                desc    = source de données éventuelle pour la description.  *
*                                                                             *
*  Description : Constitue un nouveau noeud d'instantané.                     *
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'échec.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static snapshot_node_t *create_snapshot_node(const char *id, uint64_t created, const char *name, const char *desc)
{
    snapshot_node_t *result;                /* Nouvel instantané à renvoyer*/
    bool status;                            /* Bilan d'une génération      */

    result = malloc(sizeof(snapshot_node_t));

    result->parent = NULL;

    if (id == NULL)
        status = init_snapshot_info(&result->info);
    else
        status = init_snapshot_info_from_text(&result->info, id, created, name, desc);

    if (!status)
    {
        free(result);
        result = NULL;
        goto exit;
    }

    result->path = NULL;

    result->children = NULL;
    result->count = 0;

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node = noeud d'instantané à traiter.                         *
*                                                                             *
*  Description : Libère la mémoire occupée par un noeud d'instantané.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void destroy_snapshot_node(snapshot_node_t *node)
{
    size_t i;                               /* Boucle de parcours          */
    int ret;                                /* Bilan d'un appel            */

    for (i = 0; i < node->count; i++)
        destroy_snapshot_node(node->children[i]);

    exit_snapshot_info(&node->info);

    if (node->path != NULL)
    {
        ret = unlink(node->path);
        if (ret != 0) LOG_ERROR_N("unlink");

        free(node->path);

    }

    if (node->children != NULL)
        free(node->children);

    free(node);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node    = noeud d'instantané à traiter.                      *
*                archive = archive concernée par l'instantané.                *
*                                                                             *
*  Description : Définit le chemin vers une base de données pour un noeud.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool setup_snapshot_node_db_path(snapshot_node_t *node, const GCdbArchive *archive)
{
    bool result;                            /* Bilan à retourner           */
    snapshot_id_t *id;                      /* Identifiant attribué        */
    char *suffix;                           /* Fin du fichier temporaire   */
    int ret;                                /* Bilan d'une génération      */

    id = get_snapshot_info_id(&node->info);

    ret = asprintf(&suffix, "%s_db.sql", snapshot_id_as_string(id));
    result = (ret > 0);

    if (result)
    {
        node->path = g_cdb_archive_get_tmp_filename(archive, suffix);

        free(suffix);

        result = (node->path != NULL);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node = départ du parcours de vérification.                   *
*                                                                             *
*  Description : Valide la présence d'une base de données pour chaque noeud.  *
*                                                                             *
*  Retour      : true si l'ensemble de noeuds est dans un état cohérent.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool check_snapshot_nodes(const snapshot_node_t *node)
{
    bool result;                            /* Bilan à retourner           */
    const snapshot_id_t *id;                /* Identifiant attribué        */
    size_t i;                               /* Boucle de parcours          */

    result = (node->path != NULL);

    if (!result)
    {
        id = get_snapshot_info_id(&node->info);
        log_variadic_message(LMT_ERROR, _("Database is missing for snapshot '%s'"), snapshot_id_as_string(id));
    }

    for (i = 0; i < node->count && result; i++)
        result = check_snapshot_nodes(node->children[i]);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node = départ du parcours.                                   *
*                xdoc    = document XML à compléter.                          *
*                context = contexte pour les recherches.                      *
*                archive = archive en cours de constitution.                  *
*                                                                             *
*  Description : Enregistre tous les éléments associés aux instantanés.       *
*                                                                             *
*  Retour      : Identifiant de l'instantané courant.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static DBError save_snapshot_node(const snapshot_node_t *node, xmlDocPtr xdoc, xmlXPathContextPtr context, struct archive *archive)
{
    DBError result;                         /* Conclusion à retourner      */
    const snapshot_id_t *id;                /* Identifiant attribué        */
    char *name;                             /* Désignation d'une entrée    */
    int ret;                                /* Bilan d'un appel            */
    CPError error;                          /* Bilan d'une compression     */
    xmlNodePtr xml_node;                    /* Nouveau noeud XML           */
    bool status;                            /* Bilan d'un ajout XML        */
    timestamp_t created;                    /* Date de création            */
    const char *value;                      /* Valeur éventuelle à inscrire*/
    size_t i;                               /* Boucle de parcours          */

    /* Sauvegarde de la base de données */

    id = get_snapshot_info_id(&node->info);

    ret = asprintf(&name, "%s.db", snapshot_id_as_string(id));

    if (ret < 0)
    {
        result = DBE_SYS_ERROR;
        goto exit;
    }

    assert(node->path != NULL);

    error = add_file_into_archive(archive, node->path, name);

    free(name);

    switch (error)
    {
        case CPE_NO_ERROR:
            break;

        case CPE_SYSTEM_ERROR:
            result = DBE_SYS_ERROR;
            goto exit;
            break;

        case CPE_ARCHIVE_ERROR:
            result = DBE_ARCHIVE_ERROR;
            goto exit;
            break;

    }

    /* Inscription dans le document XML */

    xml_node = ensure_node_exist(xdoc, context, "/ChrysalideBinary/Snapshots");

    if (xml_node == NULL)
    {
        result = DBE_XML_ERROR;
        goto exit;
    }

    xml_node = add_node_to_xpath(xdoc, context, "/ChrysalideBinary/Snapshots", "Snapshot");

    if (xml_node == NULL)
    {
        result = DBE_XML_ERROR;
        goto exit;
    }

    status = _add_string_attribute_to_node(xml_node, "id", snapshot_id_as_string(id));

    if (!status)
    {
        result = DBE_XML_ERROR;
        goto exit;
    }

    created = get_snapshot_info_created(&node->info);

    status = _add_uint64_attribute_to_node(xml_node, "created", created);

    if (!status)
    {
        result = DBE_XML_ERROR;
        goto exit;
    }

    value = get_snapshot_info_name(&node->info);

    if (value != NULL)
    {
        status = _add_string_attribute_to_node(xml_node, "name", value);

        if (!status)
        {
            result = DBE_XML_ERROR;
            goto exit;
        }

    }

    value = get_snapshot_info_desc(&node->info);

    if (value != NULL)
    {
        status = _add_string_attribute_to_node(xml_node, "desc", value);

        if (!status)
        {
            result = DBE_XML_ERROR;
            goto exit;
        }

    }

    if (node->parent != NULL)
    {
        id = get_snapshot_info_id(&node->parent->info);

        status = _add_string_attribute_to_node(xml_node, "parent", snapshot_id_as_string(id));

        if (!status)
        {
            result = DBE_XML_ERROR;
            goto exit;
        }

    }

    /* Poursuite des enregistrement */

    result = DBE_NONE;

    for (i = 0; i < node->count && result == DBE_NONE; i++)
        result = save_snapshot_node(node->children[i], xdoc, context, archive);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node = départ du parcours de recherche.                      *
*                id   = identifiant de l'instantané visé.                     *
*                                                                             *
*  Description : Recherche le noeud d'instantané lié à un identifiant.        *
*                                                                             *
*  Retour      : Noeud trouvé ou NULL en cas d'échec.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static snapshot_node_t *find_snapshot_node(snapshot_node_t *node, const snapshot_id_t *id)
{
    snapshot_node_t *result;                /* Noeud trouvé à renvoyer     */
    snapshot_id_t *node_id;                 /* Identifiant attribué        */
    size_t i;                               /* Boucle de parcours          */

    node_id = get_snapshot_info_id(&node->info);

    if (cmp_snapshot_id(node_id, id) == 0)
        result = node;

    else
    {
        result = NULL;

        for (i = 0; i < node->count && result == NULL; i++)
            result = find_snapshot_node(node->children[i], id);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node   = départ du parcours de recherche.                    *
*                target = instantané recherché.                               *
*                                                                             *
*  Description : Détermine si un instantané est compris dans une branche.     *
*                                                                             *
*  Retour      : Noeud trouvé ou NULL en cas d'échec.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool contain_snapshot_node(const snapshot_node_t *node, const snapshot_node_t *target)
{
    bool result;                            /* Bilan à faire remonter      */
    size_t i;                               /* Boucle de parcours          */

    result = (node == target);

    for (i = 0; i < node->count && !result; i++)
        result = contain_snapshot_node(node->children[i], target);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node  = instantané de rattachement.                          *
*                child = instantané à attacher.                               *
*                                                                             *
*  Description : Ajoute un instantané comme prolongement d'un instantané.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void add_snapshot_node(snapshot_node_t *node, snapshot_node_t *child)
{
    snapshot_id_t *src;                     /* Identifiant d'instantané #0 */
    snapshot_id_t *dest;                    /* Identifiant d'instantané #1 */

    node->children = realloc(node->children, ++node->count * sizeof(snapshot_node_t *));

    node->children[node->count - 1] = child;

    child->parent = node;

    src = get_snapshot_info_id(&node->info);
    dest = get_snapshot_info_parent_id(&child->info);

    copy_snapshot_id(dest, src);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node = instantané à traiter.                                 *
*                rec  = précise si les enfants sont à rattacher au parent.    *
*                                                                             *
*  Description : Fait disparaître un instantané dans une arborescence.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void remove_snapshot_node(snapshot_node_t *node, bool rec)
{
    snapshot_node_t *parent;                /* Accès direct                */
    size_t i;                               /* Boucle de parcours          */

    parent = node->parent;

    assert(parent != NULL);

    /* Coupe de la branche */

    assert(parent->count > 0);

    if (parent->count == 1)
    {
        free(parent->children);

        parent->children = NULL;
        parent->count = 0;

    }

    else
    {
        for (i = 0; i < parent->count; i++)
            if (parent->children[i] == node)
                break;

        assert(i < parent->count);

        if ((i + 1) < parent->count)
            memmove(&parent->children[i], &parent->children[i + 1],
                    (parent->count - i - 1) * sizeof(snapshot_node_t *));

        parent->children = realloc(parent->children, --parent->count * sizeof(snapshot_node_t *));

    }

    /* Rattachement des enfants ? */

    if (!rec)
    {
        for (i = 0; i < node->count; i++)
            add_snapshot_node(parent, node->children[i]);

        free(node->children);

        node->children = NULL;
        node->count = 0;

    }

    /* Suppression */

    destroy_snapshot_node(node);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node = définition d'instantané à consulter.                  *
*                pbuf = paquet de données où venir inscrire des infos.        *
*                                                                             *
*  Description : Collecte les descriptions d'une arborescence d'instantanés.  *
*                                                                             *
*  Retour      : Bilan du déroulement des opérations.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool pack_snapshot_node(const snapshot_node_t *node, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours          */

    result = pack_snapshot_info(&node->info, pbuf);

    for (i = 0; i < node->count && result; i++)
        result = pack_snapshot_node(node->children[i], pbuf);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       MANIPULATIONS D'ENSEMBLE D'INSTANTANES                       */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un gestionnaire d'instantanés de bases de données. */
G_DEFINE_TYPE(GDbSnapshot, g_db_snapshot, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des gestionnaires d'instantanés.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_snapshot_class_init(GDbSnapshotClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_db_snapshot_dispose;
    object->finalize = (GObjectFinalizeFunc)g_db_snapshot_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : snap = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise un gestionnaire d'instantanés de base de données. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_snapshot_init(GDbSnapshot *snap)
{
    snap->nodes = NULL;
    snap->current = NULL;

    snap->current_db = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : snap = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_snapshot_dispose(GDbSnapshot *snap)
{
    G_OBJECT_CLASS(g_db_snapshot_parent_class)->dispose(G_OBJECT(snap));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : snap = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_snapshot_finalize(GDbSnapshot *snap)
{
    if (snap->nodes != NULL)
        destroy_snapshot_node(snap->nodes);

    if (snap->current_db != NULL)
        free(snap->current_db);

    G_OBJECT_CLASS(g_db_snapshot_parent_class)->finalize(G_OBJECT(snap));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : archive = archive associée à l'instantané.                   *
*                                                                             *
*  Description : Prépare un gestionnaire d'instantanés de bases de données.   *
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'échec.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GDbSnapshot *g_db_snapshot_new(const GCdbArchive *archive)
{
    GDbSnapshot *result;                    /* Adresse à retourner         */

    result = g_object_new(G_TYPE_DB_SNAPSHOT, NULL);

    result->current_db = g_cdb_archive_get_tmp_filename(archive, "current_db.sql");

    if (result->current_db == NULL)
    {
        g_object_unref(G_OBJECT(result));
        result = NULL;
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : archive     = archive associée à l'instantané.               *
*                collections = ensemble de modifications par catégories.      *
*                                                                             *
*  Description : Prépare un gestionnaire d'instantanés de bases de données.   *
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'échec.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDbSnapshot *g_db_snapshot_new_empty(const GCdbArchive *archive, GList *collections)
{
    GDbSnapshot *result;                    /* Adresse à retourner         */
    sqlite3 *db;                            /* Base de données à manipuler */
    int ret;                                /* Bilan de la création        */
    bool status;                            /* Bilan d'une mise en place   */
    GList *iter;                            /* Boucle de parcours          */
    GDbCollection *collec;                  /* Collection visée manipulée  */

    result = g_db_snapshot_new(archive);
    if (result == NULL) goto exit;

    result->nodes = create_snapshot_node(NULL, 0, NULL, NULL);

    status = setup_snapshot_node_db_path(result->nodes, archive);
    if (!status) goto error;

    result->current = result->nodes;

    ret = sqlite3_open(result->nodes->path, &db);

    if (ret != SQLITE_OK)
    {
        LOG_ERROR_SQLITE(db, "sqlite3_open");
        goto error_db;
    }

    for (iter = g_list_first(collections);
         iter != NULL;
         iter = g_list_next(iter))
    {
        collec = G_DB_COLLECTION(iter->data);

        status = g_db_collection_create_db_table(collec, db);
        if (!status) goto error_db;

    }

    sqlite3_close(db);

    status = copy_file(result->current_db, result->nodes->path);

    if (!status)
        goto error;

    return result;

 error_db:

    sqlite3_close(db);

 error:

    g_object_unref(G_OBJECT(result));

 exit:

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : archive = archive associée à l'instantané.                   *
*                xdoc    = document XML à compléter.                          *
*                context = contexte pour les recherches.                      *
*                                                                             *
*  Description : Charge un gestionnaire d'instantanés de bases de données.    *
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'échec.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDbSnapshot *g_db_snapshot_new_from_xml(const GCdbArchive *archive, xmlDocPtr xdoc, xmlXPathContextPtr context)
{
    GDbSnapshot *result;                    /* Adresse à retourner         */
    xmlXPathObjectPtr xobject;              /* Cible d'une recherche       */
    size_t count;                           /* Nombre de contenus premiers */
    size_t i;                               /* Boucle de parcours          */
    xmlNodePtr xml_node;                    /* Noeud XML avec propriétés   */
    char *raw_id;                           /* Identifiant brut à convertir*/
    bool status;                            /* Bilan d'une conversion      */
    snapshot_id_t parent_id;                /* Identifiant de noeud parent */
    snapshot_node_t *parent;                /* Instantané parent trouvé    */
    uint64_t created;                       /* Date de création            */
    char *name;                             /* Nom d'instantané            */
    char *desc;                             /* Description d'instantané    */
    snapshot_node_t *node;                  /* Instantané nouveau constitué*/
    snapshot_id_t node_id;                  /* Identifiant de noeud courant*/

    result = g_db_snapshot_new(archive);
    if (result == NULL) goto exit;

    /* Chargement de l'ensemble des instantanés */

    xobject = get_node_xpath_object(context, "/ChrysalideBinary/Snapshots/Snapshot");

    count = XPATH_OBJ_NODES_COUNT(xobject);

    for (i = 0; i < count; i++)
    {
        xml_node = NODE_FROM_PATH_OBJ(xobject, i);

        raw_id = qck_get_node_prop_value(xml_node, "parent");

        if (raw_id == NULL)
            parent = NULL;

        else
        {
            if (result->nodes == NULL)
                parent = NULL;

            else
            {
                status = init_snapshot_id_from_text(&parent_id, raw_id);

                if (status)
                    parent = find_snapshot_node(result->nodes, &parent_id);
                else
                    parent = NULL;

            }

            free(raw_id);

            if (parent == NULL)
                goto bad_xml;

        }

        raw_id = qck_get_node_prop_value(xml_node, "id");

        if (raw_id == NULL)
            goto bad_xml;

        status = qck_get_node_prop_uint64_value(xml_node, "created", &created);

        if (!status)
            goto bad_xml;

        name = qck_get_node_prop_value(xml_node, "name");

        desc = qck_get_node_prop_value(xml_node, "desc");

        node = create_snapshot_node(raw_id, created, name, desc);

        free(raw_id);

        if (name != NULL)
            free(name);

        if (desc != NULL)
            free(desc);

        if (node == NULL)
            goto bad_xml;

        if (parent == NULL)
        {
            if (result->nodes != NULL)
                goto bad_xml;

            result->nodes = node;

        }
        else
            add_snapshot_node(parent, node);

    }

    if(xobject != NULL)
        xmlXPathFreeObject(xobject);

    /* Détermination de l'instantané courant */

    raw_id = get_node_text_value(context, "/ChrysalideBinary/CurrentSnapshot");

    if (raw_id == NULL)
        result->current = result->nodes;

    else
    {
        status = init_snapshot_id_from_text(&node_id, raw_id);

        free(raw_id);

        if (status)
            result->current = find_snapshot_node(result->nodes, &node_id);

    }

    if (result->current == NULL)
        goto no_current;

    return result;

 bad_xml:

    if(xobject != NULL)
        xmlXPathFreeObject(xobject);

 no_current:

    g_object_unref(G_OBJECT(result));

 exit:

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : snap    = gestionnaire d'instantanés à constituer.           *
*                ar      = archive en cours de lecture.                       *
*                archive = archive associée à l'instantané.                   *
*                                                                             *
*  Description : Associe une base de données aux instantanés chargés.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_db_snapshot_fill(GDbSnapshot *snap, struct archive *ar, const GCdbArchive *archive)
{
    bool result;                            /* Bilan à retourner           */
    struct archive_entry *entry;            /* Elément de l'archive        */
    int ret;                                /* Bilan d'un appel            */
    const char *path;                       /* Désignation d'un fichier    */
    const char *dot;                        /* Début de l'extension        */
    char *raw_id;                           /* Identifiant brut à convertir*/
    snapshot_id_t node_id;                  /* Identifiant de noeud courant*/
    bool status;                            /* Bilan d'une conversion      */
    snapshot_node_t *node;                  /* Instantané trouvé           */

    result = false;

    for (ret = archive_read_next_header(ar, &entry);
         ret == ARCHIVE_OK;
         ret = archive_read_next_header(ar, &entry))
    {
        path = archive_entry_pathname(entry);

        if (!_endswith(path, ".db", &dot))
            continue;

        if (strcmp(path, "current.db") == 0)
        {
            if (!dump_archive_entry_into_file(ar, entry, snap->current_db))
                break;

            continue;

        }

        raw_id = strndup(path, dot - path);

        status = init_snapshot_id_from_text(&node_id, raw_id);

        free(raw_id);

        if (!status)
            break;

        node = find_snapshot_node(snap->nodes, &node_id);

        if (node == NULL)
            break;

        if (!setup_snapshot_node_db_path(node, archive))
            break;

        if (!dump_archive_entry_into_file(ar, entry, node->path))
            break;

    }

    if (ret != ARCHIVE_EOF)
        goto exit;

    if (!check_snapshot_nodes(snap->nodes))
        goto exit;

    result = true;

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : snap    = gestionnaire d'instantanés à consulter.            *
*                xdoc    = document XML à compléter.                          *
*                context = contexte pour les recherches.                      *
*                archive = archive en cours de constitution.                  *
*                                                                             *
*  Description : Enregistre tous les éléments associés aux instantanés.       *
*                                                                             *
*  Retour      : Bilan de l'opération sous forme de code d'erreur.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

DBError g_db_snapshot_save(const GDbSnapshot *snap, xmlDocPtr xdoc, xmlXPathContextPtr context, struct archive *archive)
{
    DBError result;                         /* Conclusion à retourner      */
    const snapshot_id_t *id;                /* Identifiant attribué        */
    bool status;                            /* Bilan d'un ajout XML        */
    CPError ret;                            /* Bilan d'une compression     */

    assert(snap->current != NULL);

    id = get_snapshot_info_id(&snap->current->info);

    status = add_content_to_node(xdoc, context, "/ChrysalideBinary/CurrentSnapshot", snapshot_id_as_string(id));

    if (!status)
        result = DBE_XML_ERROR;

    else
    {
        ret = add_file_into_archive(archive, snap->current_db, "current.db");

        switch (ret)
        {
            case CPE_NO_ERROR:
                break;

            case CPE_SYSTEM_ERROR:
                result = DBE_SYS_ERROR;
                goto exit;
                break;

            case CPE_ARCHIVE_ERROR:
                result = DBE_ARCHIVE_ERROR;
                goto exit;
                break;

        }

        result = save_snapshot_node(snap->nodes, xdoc, context, archive);

    }

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : snap = gestionnaire d'instantanés à consulter.               *
*                id   = identifiant de l'instantané courant. [OUT]            *
*                                                                             *
*  Description : Fournit l'identifiant de l'instanné courant.                 *
*                                                                             *
*  Retour      : Validité de la trouvaille.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_db_snapshot_get_current_id(const GDbSnapshot *snap, snapshot_id_t *id)
{
    bool result;                            /* Bilan à retourner           */

    assert(snap->current != NULL);

    if (snap->current == NULL)
        result = false;

    else
    {
        copy_snapshot_id(id, get_snapshot_info_id(&snap->current->info));
        result = true;
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : snap = gestionnaire d'instantanés à consulter.               *
*                                                                             *
*  Description : Fournit la base de données correspondant à instanné donné.   *
*                                                                             *
*  Retour      : Base de données liée à l'instantané demandé ou NULL.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

sqlite3 *g_db_snapshot_get_database(const GDbSnapshot *snap)
{
    sqlite3 *result;                        /* Base SQLite à retourner     */
    int ret;                                /* Bilan d'un appel            */

    ret = sqlite3_open(snap->current_db, &result);

    if (ret != SQLITE_OK)
    {
        if (result != NULL)
            sqlite3_close(result);

        result = NULL;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : snap = gestionnaire d'instantanés à consulter.               *
*                pbuf = paquet de données où venir inscrire des infos.        *
*                                                                             *
*  Description : Collecte les descriptions de l'ensemble des instantanés.     *
*                                                                             *
*  Retour      : Bilan du déroulement des opérations.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_db_snapshot_pack_all(const GDbSnapshot *snap, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    result = pack_snapshot_node(snap->nodes, pbuf);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : snap = gestionnaire d'instantanés à consulter.               *
*                pbuf = paquet de données où venir puiser les infos.          *
*                                                                             *
*  Description : Actualise la désignation d'un instantané donné.              *
*                                                                             *
*  Retour      : Bilan de l'opération sous forme de code d'erreur.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

DBError g_db_snapshot_set_name(const GDbSnapshot *snap, packed_buffer_t *pbuf)
{
    DBError result;                         /* Conclusion à retourner      */
    snapshot_id_t id;                       /* Identifiant d'instantané    */
    bool status;                            /* Bilan d'une récupération    */
    rle_string string;                      /* Chaîne à transmettre        */
    snapshot_node_t *node;                  /* Instantané trouvé           */

    result = DBE_NONE;

    /* Lecture des arguments */

    setup_empty_snapshot_id(&id);

    status = unpack_snapshot_id(&id, pbuf);
    if (!status)
    {
        result = DBE_BAD_EXCHANGE;
        goto bad_exchange;
    }

    setup_empty_rle_string(&string);

    status = unpack_rle_string(&string, pbuf);
    if (!status)
    {
        result = DBE_BAD_EXCHANGE;
        goto bad_exchange;
    }

    /* Traitement */

    node = find_snapshot_node(snap->nodes, &id);

    if (node == NULL)
    {
        log_variadic_message(LMT_ERROR, _("Snapshot not found for id '%s'"), snapshot_id_as_string(&id));
        result = DBE_SNAPSHOT_NOT_FOUND;
    }

    else
        set_snapshot_info_name(&node->info, get_rle_string(&string));

    exit_rle_string(&string);

 bad_exchange:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : snap = gestionnaire d'instantanés à consulter.               *
*                pbuf = paquet de données où venir puiser les infos.          *
*                                                                             *
*  Description : Actualise la description d'un instantané donné.              *
*                                                                             *
*  Retour      : Bilan de l'opération sous forme de code d'erreur.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

DBError g_db_snapshot_set_desc(const GDbSnapshot *snap, packed_buffer_t *pbuf)
{
    DBError result;                         /* Conclusion à retourner      */
    snapshot_id_t id;                       /* Identifiant d'instantané    */
    bool status;                            /* Bilan d'une récupération    */
    rle_string string;                      /* Chaîne à transmettre        */
    snapshot_node_t *node;                  /* Instantané trouvé           */

    result = DBE_NONE;

    /* Lecture des arguments */

    setup_empty_snapshot_id(&id);

    status = unpack_snapshot_id(&id, pbuf);
    if (!status)
    {
        result = DBE_BAD_EXCHANGE;
        goto bad_exchange;
    }

    setup_empty_rle_string(&string);

    status = unpack_rle_string(&string, pbuf);
    if (!status)
    {
        result = DBE_BAD_EXCHANGE;
        goto bad_exchange;
    }

    /* Traitement */

    node = find_snapshot_node(snap->nodes, &id);

    if (node == NULL)
    {
        log_variadic_message(LMT_ERROR, _("Snapshot not found for id '%s'"), snapshot_id_as_string(&id));
        result = DBE_SNAPSHOT_NOT_FOUND;
    }

    else
        set_snapshot_info_desc(&node->info, get_rle_string(&string));

    exit_rle_string(&string);

 bad_exchange:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : snap   = gestionnaire d'instantanés à consulter.             *
*                pbuf   = paquet de données où venir puiser les infos.        *
*                reload = indique un besoin de rechargement de la base. [OUT] *
*                                                                             *
*  Description : Restaure un instantané de l'arborescence.                    *
*                                                                             *
*  Retour      : Bilan de l'opération sous forme de code d'erreur.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

DBError g_db_snapshot_restore(GDbSnapshot *snap, packed_buffer_t *pbuf, bool *reload)
{
    DBError result;                         /* Conclusion à retourner      */
    snapshot_id_t id;                       /* Identifiant d'instantané    */
    bool status;                            /* Bilan d'une récupération    */
    snapshot_node_t *node;                  /* Instantané trouvé           */

    result = DBE_NONE;

    /* Lecture des arguments */

    setup_empty_snapshot_id(&id);

    status = unpack_snapshot_id(&id, pbuf);
    if (!status)
    {
        result = DBE_BAD_EXCHANGE;
        goto bad_exchange;
    }

    /* Traitement */

    node = find_snapshot_node(snap->nodes, &id);

    if (node == NULL)
    {
        log_variadic_message(LMT_ERROR, _("Snapshot not found for id '%s'"), snapshot_id_as_string(&id));
        result = DBE_SNAPSHOT_NOT_FOUND;
    }

    else if (node == snap->current)
    {
        log_simple_message(LMT_WARNING, _("No need to restore the current snapshot"));
        *reload = false;
    }

    else
    {
        status = copy_file(snap->current_db, node->path);

        if (!status)
        {
            log_variadic_message(LMT_ERROR, _("Failed to restore snapshot from '%s' to '%s'"),
                                 node->path, snap->current_db);
            result = DBE_SNAPSHOT_RESTORE_FAILURE;
        }

        else
        {
            snap->current = node;
            *reload = true;
        }

    }

 bad_exchange:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : snap    = gestionnaire d'instantanés à consulter.            *
*                db      = base de données courante.                          *
*                archive = archive associée à l'instantané.                   *
*                                                                             *
*  Description : Crée un nouvel instantanés dans l'arborescence.              *
*                                                                             *
*  Retour      : Bilan de l'opération sous forme de code d'erreur.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

DBError g_db_snapshot_create(GDbSnapshot *snap, sqlite3 *db, const GCdbArchive *archive)
{
    DBError result;                         /* Conclusion à retourner      */
    snapshot_node_t *new;                   /* Nouvel instantané           */
    bool status;                            /* Bilan d'une récupération    */

    result = DBE_NONE;

    new = create_snapshot_node(NULL, 0, NULL, NULL);

    status = setup_snapshot_node_db_path(new, archive);
    if (!status)
    {
        result = DBE_SYS_ERROR;
        destroy_snapshot_node(new);
        goto error;
    }

    status = backup_db(db, new->path);
    if (!status)
    {
        result = DBE_SYS_ERROR;
        destroy_snapshot_node(new);
        goto error;
    }

    add_snapshot_node(snap->current, new);

    snap->current = new;

 error:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : snap    = gestionnaire d'instantanés à consulter.            *
*                pbuf    = paquet de données où venir puiser les infos.       *
*                changed = indique si l'instantané courant a bougé. [OUT]     *
*                                                                             *
*  Description : Supprime un instantané dans l'arborescence.                  *
*                                                                             *
*  Retour      : Bilan de l'opération sous forme de code d'erreur.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

DBError g_db_snapshot_remove(GDbSnapshot *snap, packed_buffer_t *pbuf, bool *changed)
{
    DBError result;                         /* Conclusion à retourner      */
    snapshot_id_t id;                       /* Identifiant d'instantané    */
    bool status;                            /* Bilan d'une récupération    */
    uint8_t tmp;                            /* Stockage temporaire         */
    bool rec;                               /* Indicateur de récursivité   */
    snapshot_node_t *node;                  /* Instantané trouvé           */

    result = DBE_NONE;

    *changed = false;

    /* Lecture des arguments */

    setup_empty_snapshot_id(&id);

    status = unpack_snapshot_id(&id, pbuf);
    if (!status)
    {
        result = DBE_BAD_EXCHANGE;
        goto bad_exchange;
    }

    status = extract_packed_buffer(pbuf, &tmp, sizeof(uint8_t), false);
    if (!status)
    {
        result = DBE_BAD_EXCHANGE;
        goto bad_exchange;
    }

    rec = (tmp == 0x1);

    /* Traitement */

    node = find_snapshot_node(snap->nodes, &id);

    if (node == NULL)
    {
        log_variadic_message(LMT_ERROR, _("Snapshot not found for id '%s'"), snapshot_id_as_string(&id));
        result = DBE_SNAPSHOT_NOT_FOUND;
    }

    else if (node == snap->nodes)
    {
        log_simple_message(LMT_ERROR, _("Root snapshot can not be removed"));
        result = DBE_SNAPSHOT_ROOT_REMOVAL;
    }

    else
    {
        /* Réassignation éventuelle */
        if ((rec && contain_snapshot_node(node, snap->current)) || (!rec && node == snap->current))
        {
            snap->current = node->parent;
            *changed = true;
        }

        remove_snapshot_node(node, rec);

    }

 bad_exchange:

    return result;

}
