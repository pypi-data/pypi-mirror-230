
/* Chrysalide - Outil d'analyse de fichiers binaires
 * binary.c - traitement des flots de code binaire
 *
 * Copyright (C) 2009-2019 Cyrille Bagard
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


#include "binary.h"


#include <assert.h>
#include <malloc.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>


#include <i18n.h>


#include "loaded-int.h"
#include "routine.h"
#include "disass/disassembler.h"
#include "../arch/storage.h"
#include "../common/extstr.h"
#include "../common/cpp.h"
#include "../common/xdg.h"
#include "../core/collections.h"
#include "../core/columns.h"
#include "../core/logs.h"
#include "../core/params.h"
#include "../core/processors.h"
#include "../format/known.h"
#include "../glibext/gbinarycursor.h"
#ifdef INCLUDE_GTK_SUPPORT
#   include "../glibext/gloadedpanel.h"
#   include "../gtkext/easygtk.h"
#   include "../gtkext/gtkblockdisplay.h"
#   include "../gtkext/gtkdisplaypanel.h"
#   include "../gtkext/gtkgraphdisplay.h"
#   include "../gtkext/gtkstatusstack.h"
#   include "../gtkext/hexdisplay.h"
#endif



/* ------------------------ ENCADREMENTS D'UN BINAIRE CHARGE ------------------------ */


/* Description de fichier binaire (instance) */
struct _GLoadedBinary
{
    GLoadedContent parent;                  /* A laisser en premier        */

    bool use_remote;                        /* Enregistrements distants ?  */
    char *remote_host;                      /* Nom du serveur distant      */
    char *remote_port;                      /* Port du serveur distant     */
    GAnalystClient *client;                 /* Enregistrements courants    */

    GList *collections;                     /* Ensemble de modifications   */

    GExeFormat *format;                     /* Format du binaire           */
    GArchProcessor *proc;                   /* Architecture du binaire     */

    GBufferCache *disass_cache;             /* Instructions lisibles       */
    //GCodeBuffer **dec_buffers;              /* Sources sous forme de texte */
    size_t decbuf_count;                    /* Taille des tableaux         */
    size_t defsrc;                          /* Fichier source principal    */

    GDisplayOptions *options[BVW_COUNT];    /* Options d'affichage         */

    vmpa2t *old_gotos;                      /* Conservation de destinations*/
    size_t goto_count;                      /* Taille de cette liste       */
    GMutex goto_access;                     /* Encadrement des accès       */

};

/* Description de fichier binaire (classe) */
struct _GLoadedBinaryClass
{
    GLoadedContentClass parent;             /* A laisser en premier        */

};


/* Initialise la classe des descriptions de fichier binaire. */
static void g_loaded_binary_class_init(GLoadedBinaryClass *);

/* Initialise une description de fichier binaire. */
static void g_loaded_binary_init(GLoadedBinary *);

/* Supprime toutes les références externes. */
static void g_loaded_binary_dispose(GLoadedBinary *);

/* Procède à la libération totale de la mémoire. */
static void g_loaded_binary_finalize(GLoadedBinary *);



/* ------------------------- INFORMATIONS D'ENREGISTREMENTS ------------------------- */


/* Charge en mémoire les formes d'enregistrement du XML. */
static bool g_loaded_binary_load_storage(GLoadedBinary *, xmlXPathContext *, const char *);

/* Ecrit les formes d'enregistrement du binaire dans du XML. */
static bool g_loaded_binary_save_storage(const GLoadedBinary *, xmlDoc *, xmlXPathContext *, const char *);

/* Etablit une connexion au serveur interne en tant que client. */
static bool g_loaded_binary_connect_internal(GLoadedBinary *);

/* Etablit une connexion à un serveur distant comme client. */
static bool g_loaded_binary_connect_remote(GLoadedBinary *);



/* -------------------------- MANIPULATION DES COLLECTIONS -------------------------- */





/* -------------------- SAUVEGARDE ET RESTAURATION DE PARAMETRES -------------------- */


/* Charge en mémoire les anciennes destinations visitées. */
static bool g_loaded_binary_load_old_gotos(GLoadedBinary *, xmlXPathContext *, const char *);

/* Ecrit les anciennes destinations visitées dans du XML. */
static bool g_loaded_binary_save_old_gotos(GLoadedBinary *, xmlDoc *, xmlXPathContext *, const char *);



/* ---------------------- GESTION SOUS FORME DE CONTENU CHARGE ---------------------- */


/* Interprète un contenu binaire chargé avec un appui XML. */
static bool g_loaded_binary_restore(GLoadedBinary *, xmlDoc *, xmlXPathContext *, const char *);

/* Ecrit une sauvegarde du binaire dans un fichier XML. */
static bool g_loaded_binary_save(GLoadedBinary *, xmlDoc *, xmlXPathContext *, const char *);

/* Fournit le contenu représenté de l'élément chargé. */
static GBinContent *g_loaded_binary_get_content(const GLoadedBinary *);

/* Décrit la nature du contenu reconnu pour l'élément chargé. */
static char *g_loaded_binary_get_content_class(const GLoadedBinary *, bool);

/* Assure le désassemblage en différé. */
static bool g_loaded_binary_analyze(GLoadedBinary *, bool, bool, wgroup_id_t, GtkStatusStack *);

/* Prend note d'une variation des instructions désassemblées. */
static void on_binary_processor_changed(GArchProcessor *, GArchInstruction *, gboolean, GLoadedBinary *);

/* Fournit le désignation associée à l'élément chargé. */
static char *g_loaded_binary_describe(const GLoadedBinary *, bool);

#ifdef INCLUDE_GTK_SUPPORT

/* Détermine le nombre de vues disponibles pour un contenu. */
static unsigned int g_loaded_binary_count_views(const GLoadedBinary *);

/* Fournit le nom d'une vue donnée d'un contenu chargé. */
static char *g_loaded_binary_get_view_name(const GLoadedBinary *, unsigned int);

/* Met en place la vue initiale pour un contenu binaire. */
static GtkWidget *g_loaded_binary_build_default_view(GLoadedBinary *);

/* Met en place la vue demandée pour un contenu binaire. */
static GtkWidget *g_loaded_binary_build_view(GLoadedBinary *, unsigned int);

/* Retrouve l'indice correspondant à la vue donnée d'un contenu. */
static unsigned int g_loaded_binary_get_view_index(GLoadedBinary *, GtkWidget *);

/* Fournit toutes les options d'affichage pour un contenu. */
static GDisplayOptions *g_loaded_binary_get_display_options(const GLoadedBinary *, unsigned int);

#endif



/* ---------------------------------------------------------------------------------- */
/*                          ENCADREMENTS D'UN BINAIRE CHARGE                          */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une description de fichier binaire. */
G_DEFINE_TYPE(GLoadedBinary, g_loaded_binary, G_TYPE_LOADED_CONTENT);


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

static void g_loaded_binary_class_init(GLoadedBinaryClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GLoadedContentClass *loaded;            /* Forme parente de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_loaded_binary_dispose;
    object->finalize = (GObjectFinalizeFunc)g_loaded_binary_finalize;

    loaded = G_LOADED_CONTENT_CLASS(klass);

    loaded->restore = (restore_content_fc)g_loaded_binary_restore;
    loaded->save = (save_content_fc)g_loaded_binary_save;

    loaded->get_content = (get_content_fc)g_loaded_binary_get_content;
    loaded->get_content_class = (get_content_class_fc)g_loaded_binary_get_content_class;

    loaded->analyze = (analyze_loaded_fc)g_loaded_binary_analyze;

    loaded->describe = (describe_loaded_fc)g_loaded_binary_describe;

#ifdef INCLUDE_GTK_SUPPORT

    loaded->count_views = (count_loaded_views_fc)g_loaded_binary_count_views;
    loaded->get_view_name = (get_loaded_view_name_fc)g_loaded_binary_get_view_name;
    loaded->build_def_view = (build_loaded_def_view_fc)g_loaded_binary_build_default_view;
    loaded->build_view = (build_loaded_view_fc)g_loaded_binary_build_view;
    loaded->get_view_index = (get_loaded_view_index_fc)g_loaded_binary_get_view_index;

    loaded->get_options = (get_loaded_options_fc)g_loaded_binary_get_display_options;

#endif

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une description de fichier binaire.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_loaded_binary_init(GLoadedBinary *binary)
{
    binary->use_remote = false;
    binary->remote_host = strdup("localhost");
    binary->remote_port = strdup("1337");

    binary->collections = create_collections_list();
    attach_binary_to_collections(binary->collections, binary);

    binary->options[BVW_HEX] = g_display_options_new();

    g_display_options_add(binary->options[BVW_HEX], _("Physical offset"), true);

    binary->options[BVW_BLOCK] = g_display_options_new();

    g_display_options_add(binary->options[BVW_BLOCK], _("Physical offset"), true);
    g_display_options_add(binary->options[BVW_BLOCK], _("Virtual address"), true);
    g_display_options_add(binary->options[BVW_BLOCK], _("Binary code"), false);

    binary->options[BVW_GRAPH] = g_display_options_new();

    g_display_options_add(binary->options[BVW_GRAPH], _("Physical offset"), false);
    g_display_options_add(binary->options[BVW_GRAPH], _("Virtual address"), false);
    g_display_options_add(binary->options[BVW_GRAPH], _("Binary code"), false);

    g_mutex_init(&binary->goto_access);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_loaded_binary_dispose(GLoadedBinary *binary)
{
    BinaryView i;                           /* Boucle de parcours          */

    g_clear_object(&binary->client);

    delete_collections_list(&binary->collections);

    g_clear_object(&binary->format);
    g_clear_object(&binary->proc);

    g_clear_object(&binary->disass_cache);

    for (i = 0; i < BVW_COUNT; i++)
        g_clear_object(&binary->options[i]);

    g_mutex_clear(&binary->goto_access);

    G_OBJECT_CLASS(g_loaded_binary_parent_class)->dispose(G_OBJECT(binary));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_loaded_binary_finalize(GLoadedBinary *binary)
{
    free(binary->remote_host);
    free(binary->remote_port);

    G_OBJECT_CLASS(g_loaded_binary_parent_class)->finalize(G_OBJECT(binary));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format d'exécutable établi.                         *
*                                                                             *
*  Description : Interprète un contenu binaire chargé.                        *
*                                                                             *
*  Retour      : Adresse de la représentation ou NULL en cas d'échec.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GLoadedContent *g_loaded_binary_new(GExeFormat *format)
{
    GLoadedBinary *result;                  /* Adresse à retourner         */
    const char *arch;                       /* Architecture d'exécution    */
    GArchProcessor *proc;                   /* Architecture du binaire     */

    result = NULL;

    /* Architecture visée */

    arch = g_exe_format_get_target_machine(format);

    if (arch == NULL)
    {
        log_simple_message(LMT_INFO, _("Unknown architecture"));
        goto exit;
    }

    proc = get_arch_processor_for_key(arch);

    if (proc == NULL)
    {
        log_variadic_message(LMT_ERROR, _("Unable to load the required processor (%s)"), arch);
        goto exit;
    }

    /* Mise en place complète */

    result = g_object_new(G_TYPE_LOADED_BINARY, NULL);

    result->format = format;

    result->proc = proc;

 exit:

    return G_LOADED_CONTENT(result);

}



/* ---------------------------------------------------------------------------------- */
/*                           INFORMATIONS D'ENREGISTREMENTS                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : binary  = élément binaire à traiter.                         *
*                context = contexte pour les recherches XPath.                *
*                path    = chemin d'accès au noeud XML à lire.                *
*                                                                             *
*  Description : Charge en mémoire les formes d'enregistrement du XML.        *
*                                                                             *
*  Retour      : true si l'opération a bien tourné, false sinon.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_loaded_binary_load_storage(GLoadedBinary *binary, xmlXPathContext *context, const char *path)
{
    bool result;                            /* Bilan à faire remonter      */
    char *storage_path;                     /* Partie "Enregistrement"     */
    char *value;                            /* Valeur lue à partie du XML  */
    char *access;                           /* Chemin d'accès à un élément */
    char *port;                             /* Port de communication       */

    result = true;

    storage_path = strdup(path);
    storage_path = stradd(storage_path, "/Storage");

    value = get_node_prop_value(context, storage_path, "remote");
    if (value == NULL) goto glbls_no_storage_config;

    binary->use_remote = (strcmp(value, "true") == 0);

    free(value);

    /* Serveur distant */

    access = strdup(storage_path);
    access = stradd(access, "/RemoteServer");

    value = get_node_prop_value(context, access, "port");
    if (value == NULL) goto glbls_features;

    port = value;

    value = get_node_prop_value(context, access, "host");
    if (value == NULL)
    {
        free(port);
        goto glbls_features;
    }

    g_loaded_binary_set_remote_server(binary, value, port);

    free(value);

    free(port);

 glbls_features:

    free(access);

    if (binary->use_remote)
        g_loaded_binary_set_remote_storage_usage(binary, true);

 glbls_no_storage_config:

    free(storage_path);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary  = élément binaire à traiter.                         *
*                xdoc    = structure XML en cours d'édition.                  *
*                context = contexte à utiliser pour les recherches.           *
*                path    = chemin d'accès réservé au binaire.                 *
*                                                                             *
*  Description : Ecrit les formes d'enregistrement du binaire dans du XML.    *
*                                                                             *
*  Retour      : true si l'opération a bien tourné, false sinon.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_loaded_binary_save_storage(const GLoadedBinary *binary, xmlDoc *xdoc, xmlXPathContext *context, const char *path)
{
    bool result;                            /* Bilan à faire remonter      */
    char *storage_path;                     /* Partie "Enregistrement"     */
    char *access;                           /* Chemin d'accès à un élément */

    result = true;

    storage_path = strdup(path);
    storage_path = stradd(storage_path, "/Storage");

    result &= add_string_attribute_to_node(xdoc, context, storage_path, "remote",
                                           binary->use_remote ? "true" : "false");

    /* Serveur distant */

    access = strdup(storage_path);
    access = stradd(access, "/RemoteServer");

    result &= add_string_attribute_to_node(xdoc, context, access, "host", binary->remote_host);

    result &= add_string_attribute_to_node(xdoc, context, access, "port", binary->remote_port);

    free(access);

    free(storage_path);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = élément binaire à consulter.                        *
*                                                                             *
*  Description : Détermine si tous les enregistrements sont locaux ou non.    *
*                                                                             *
*  Retour      : Statut de l'utilisation du serveur local.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_loaded_binary_use_remote_storage(const GLoadedBinary *binary)
{
    return binary->use_remote;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = élément binaire à consulter.                        *
*                use    = statut de l'utilisation du serveur distant.         *
*                                                                             *
*  Description : Définit si tous les enregistrements sont locaux ou non.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_loaded_binary_set_remote_storage_usage(GLoadedBinary *binary, bool use)
{
    binary->use_remote = use;

    g_clear_object(&binary->client);

    if (use)
        g_loaded_binary_connect_remote(binary);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = élément binaire à consulter.                        *
*                host   = nom du serveur distant à contacter. [OUT]           *
*                port   = port de communication avec le serveur distant. [OUT]*
*                                                                             *
*  Description : Identifie le serveur distant associé au binaire courant.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_loaded_binary_get_remote_server(const GLoadedBinary *binary, const char **host, const char **port)
{
    *host = binary->remote_host;
    *port = binary->remote_port;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = élément binaire à consulter.                        *
*                host   = nom du serveur distant à contacter.                 *
*                port   = port de communication avec le serveur distant.      *
*                                                                             *
*  Description : Définit le serveur distant associé au binaire courant.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_loaded_binary_set_remote_server(GLoadedBinary *binary, const char *host, const char *port)
{
    free(binary->remote_host);
    binary->remote_host = strdup(host);

    free(binary->remote_port);
    binary->remote_port = strdup(port);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = élément binaire à manipuler.                        *
*                                                                             *
*  Description : Etablit une connexion au serveur interne en tant que client. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_loaded_binary_connect_internal(GLoadedBinary *binary)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu bianire manipulé    */
    const gchar *checksum;                  /* Identifiant de binaire      */

    /* Détermination de l'identifiant */

    content = g_known_format_get_content(G_KNOWN_FORMAT(binary->format));
    checksum = g_binary_content_get_checksum(content);
    g_object_unref(G_OBJECT(content));

    /* Tentative de connexion */

    binary->client = g_analyst_client_new(checksum, "NULL", binary->collections, NULL);

    result = g_hub_client_start_internal(G_HUB_CLIENT(binary->client));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = élément binaire à manipuler.                        *
*                                                                             *
*  Description : Etablit une connexion à un serveur distant comme client.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_loaded_binary_connect_remote(GLoadedBinary *binary)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu bianire manipulé    */
    const gchar *checksum;                  /* Identifiant de binaire      */

    assert(binary->client == NULL);

    /* Détermination de l'identifiant */

    content = g_known_format_get_content(G_KNOWN_FORMAT(binary->format));
    checksum = g_binary_content_get_checksum(content);
    g_object_unref(G_OBJECT(content));

    /* Tentative de connexion */

    binary->client = g_analyst_client_new(checksum, "NULL", binary->collections, NULL);

    result = g_hub_client_start_remote(G_HUB_CLIENT(binary->client),
                                       binary->remote_host, binary->remote_port, true);

    if (!result)
    {
        log_variadic_message(LMT_ERROR, _("Failed to connect to remote host '%s:%s'"),
                             binary->remote_host, binary->remote_port);

        g_clear_object(&binary->client);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = élément binaire à manipuler.                        *
*                                                                             *
*  Description : Sauvegarde le cache des instructions désassemblées.          *
*                                                                             *
*  Retour      : Bilan préliminaire de l'opération.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_loaded_binary_save_cache(const GLoadedBinary *binary)
{
    bool result;                            /* Bilan à faire remonter      */
    GArchProcessor *proc;                   /* Processeur concerné         */
    GBinContent *content;                   /* Contenu brut représenté     */
    const gchar *id;                        /* Identifiant court et unique */
    GAsmStorage *storage;                   /* Cache propre à constituer   */

    proc = g_loaded_binary_get_processor(binary);
    content = g_loaded_binary_get_content(binary);

    id = g_binary_content_get_checksum(content);

    storage = g_asm_storage_new_compressed(proc, id);

    g_object_unref(G_OBJECT(content));
    g_object_unref(G_OBJECT(proc));

    if (storage != NULL)
    {
        g_signal_connect(G_OBJECT(storage), "saved", G_CALLBACK(g_object_unref), NULL);

        g_asm_storage_save(storage);

        result = true;

    }
    else
        result = false;

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                            MANIPULATION DES COLLECTIONS                            */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = élément binaire à consulter.                        *
*                                                                             *
*  Description : Fournit un client assurant la liaison avec un serveur.       *
*                                                                             *
*  Retour      : Client connecté ou NULL.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GAnalystClient *g_loaded_binary_get_client(const GLoadedBinary *binary)
{
    GAnalystClient *result;                 /* Instance à retourner        */

    result = binary->client;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}

/******************************************************************************
*                                                                             *
*  Paramètres  : binary = élément binaire à consulter.                        *
*                count  = taille de la liste constituée. [OUT]                *
*                                                                             *
*  Description : Fournit l'ensemble des collections utilisées par un binaire. *
*                                                                             *
*  Retour      : Liste de collections en place à libérer après usage.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDbCollection **g_loaded_binary_get_collections(const GLoadedBinary *binary, size_t *count)
{
    GDbCollection **result;                 /* Liste à retourner           */
    GList *c;                               /* Boucle de parcours #1       */
    size_t i;                               /* Boucle de parcours #2       */

    *count = g_list_length(binary->collections);

    if (*count == 0)
        result = NULL;

    else
    {
        result = malloc(*count * sizeof(GDbCollection *));

        for (c = g_list_first(binary->collections), i = 0; c != NULL; c = g_list_next(c), i++)
        {
            assert(i < *count);

            result[i] = G_DB_COLLECTION(c->data);
            g_object_ref(G_OBJECT(result[i]));

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary  = élément binaire à consulter.                       *
*                feature = fonctionnalité assurée par la collection visée.    *
*                                                                             *
*  Description : Trouve une collection assurant une fonctionnalité donnée.    *
*                                                                             *
*  Retour      : Collection trouvée ou NULL.                                  *
*                                                                             *
*  Remarques   : Le résultat est à déréfrencer après usage.                   *
*                                                                             *
******************************************************************************/

GDbCollection *g_loaded_binary_find_collection(const GLoadedBinary *binary, DBFeatures feature)
{
    GDbCollection *result;                  /* Collection à retourner      */

    result = find_collection_in_list(binary->collections, feature);

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = élément binaire à consulter.                        *
*                item   = élémnent à pousser vers un serveur de collection.   *
*                                                                             *
*  Description : Demande l'intégration d'une modification dans une collection.*
*                                                                             *
*  Retour      : Bilan partiel de l'opération demandée.                       *
*                                                                             *
*  Remarques   : L'appelant perd la propriété de l'élément à ajouté.          *
*                                                                             *
******************************************************************************/

bool g_loaded_binary_add_to_collection(GLoadedBinary *binary, GDbItem *item)
{
    bool result;                            /* Bilan à faire remonter      */
    GAnalystClient *client;                 /* Liaison à utiliser          */

    client = g_loaded_binary_get_client(binary);

    if (client == NULL)
    {
        log_simple_message(LMT_ERROR, _("No connection to a server in order to forward the item"));
        result = false;
    }

    else
    {
        result = g_analyst_client_add_item(client, item);
        g_object_unref(G_OBJECT(client));
    }

    g_object_unref(G_OBJECT(item));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary    = élément binaire à consulter.                     *
*                timestamp = date du dernier élément à garder comme actif.    *
*                                                                             *
*  Description : Spécifie la bordure temporelle limite des activations.       *
*                                                                             *
*  Retour      : true si la commande a bien été envoyée, false sinon.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_loaded_binary_set_last_active(GLoadedBinary *binary, timestamp_t timestamp)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    if (binary->client != NULL)
        result = g_analyst_client_set_last_active(binary->client, timestamp);

    else
    {
        log_simple_message(LMT_ERROR, _("No connection to a server found in order to set timestamp"));
        result = false;
    }

    return result;

}





















/******************************************************************************
*                                                                             *
*  Paramètres  : binary = élément binaire à consulter.                        *
*                                                                             *
*  Description : Fournit le format de fichier reconnu dans le contenu binaire.*
*                                                                             *
*  Retour      : Instance du format reconnu.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GExeFormat *g_loaded_binary_get_format(const GLoadedBinary *binary)
{
    GExeFormat *result;                     /* Instance à retourner        */

    result = binary->format;

    g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = élément binaire à consulter.                        *
*                                                                             *
*  Description : Fournit le processeur de l'architecture liée au binaire.     *
*                                                                             *
*  Retour      : Instance du processeur associé.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchProcessor *g_loaded_binary_get_processor(const GLoadedBinary *binary)
{
    GArchProcessor *result;                 /* Instance à retourner        */

    result = binary->proc;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = élément binaire à consulter.                        *
*                                                                             *
*  Description : Fournit le tampon associé au contenu assembleur d'un binaire.*
*                                                                             *
*  Retour      : Tampon mis en place ou NULL si aucun (!).                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBufferCache *g_loaded_binary_get_disassembly_cache(const GLoadedBinary *binary)
{
    GBufferCache *result;                   /* Instance à retourner        */

    result = binary->disass_cache;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                      SAUVEGARDE ET RESTAURATION DE PARAMETRES                      */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : binary  = élément binaire à traiter.                         *
*                context = contexte pour les recherches XPath.                *
*                path    = chemin d'accès au noeud XML à lire.                *
*                                                                             *
*  Description : Charge en mémoire les anciennes destinations visitées.       *
*                                                                             *
*  Retour      : true si l'opération a bien tourné, false sinon.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_loaded_binary_load_old_gotos(GLoadedBinary *binary, xmlXPathContext *context, const char *path)
{
    bool result;                            /* Bilan à faire remonter      */
    char *top_access;                       /* Chemin d'accès principal    */
    xmlXPathObjectPtr xobject;              /* Cible d'une recherche       */
    size_t count;                           /* Nombre de contenus premiers */
    size_t i;                               /* Boucle de parcours          */
    char *access;                           /* Chemin d'accès à un élément */
    char *value;                            /* Valeur lue à partie du XML  */
    bool is_virt;                           /* Détermination de l'utile    */
    vmpa2t *new;                            /* Nouvelle destination        */

    result = true;

    asprintf(&top_access, "%s/OldGotos/Target", path);

    xobject = get_node_xpath_object(context, top_access);

    count = XPATH_OBJ_NODES_COUNT(xobject);

    for (i = 0; i < count; i++)
    {
        asprintf(&access, "%s/OldGotos/Target[position()=%zu]", path, i + 1);

        /* Type de destination */

        value = get_node_prop_value(context, access, "type");
        if (value == NULL)
        {
            result = false;
            break;
        }

        is_virt = (strcmp(value, "virt") == 0);

        free(value);

        /* Adresse de destination */

        value = get_node_prop_value(context, access, "location");
        if (value == NULL)
        {
            result = false;
            break;
        }

        if (is_virt)
            new = string_to_vmpa_virt(value);
        else
            new = string_to_vmpa_phy(value);

        free(value);

        /* Intégration */

        binary->old_gotos = realloc(binary->old_gotos, ++binary->goto_count * sizeof(vmpa2t));

        copy_vmpa(&binary->old_gotos[binary->goto_count - 1], new);

        delete_vmpa(new);

        free(access);

    }

    if(xobject != NULL)
        xmlXPathFreeObject(xobject);

    free(top_access);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary  = élément binaire à traiter.                         *
*                xdoc    = structure XML en cours d'édition.                  *
*                context = contexte à utiliser pour les recherches.           *
*                path    = chemin d'accès réservé au binaire.                 *
*                                                                             *
*  Description : Ecrit les anciennes destinations visitées dans du XML.       *
*                                                                             *
*  Retour      : true si l'opération a bien tourné, false sinon.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_loaded_binary_save_old_gotos(GLoadedBinary *binary, xmlDoc *xdoc, xmlXPathContext *context, const char *path)
{
    bool result;                            /* Bilan à faire remonter      */
    size_t i;                               /* Boucle de parcours          */
    char *access;                           /* Chemin d'accès à un élément */
    const vmpa2t *addr;                     /* Adresse de destination      */
    bool is_virt;                           /* Détermination de l'utile    */
    VMPA_BUFFER(loc);                       /* Version humaintement lisible*/

    result = true;

    g_mutex_lock(&binary->goto_access);

    for (i = 0; i < binary->goto_count && result; i++)
    {
        asprintf(&access, "%s/OldGotos/Target[position()=%zu]", path, i + 1);

        result = (ensure_node_exist(xdoc, context, access) != NULL);

        addr = &binary->old_gotos[i];

        is_virt = has_virt_addr(addr);

        if (result)
            result = add_string_attribute_to_node(xdoc, context, access, "type", is_virt ? "virt" : "phys");

        if (result)
        {
            if (is_virt)
                vmpa2_virt_to_string(addr, MDS_UNDEFINED, loc, NULL);
            else
                vmpa2_phys_to_string(addr, MDS_UNDEFINED, loc, NULL);

            result = add_string_attribute_to_node(xdoc, context, access, "location", loc);

        }

        free(access);

    }

    g_mutex_unlock(&binary->goto_access);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = élément binaire à consulter.                        *
*                new    = nouvelle destination à conserver en mémoire.        *
*                                                                             *
*  Description : Complète la liste des destinations déjà visitées.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_loaded_binary_remember_new_goto(GLoadedBinary *binary, const vmpa2t *new)
{
    size_t previous_count;                  /* Sauvegarde de la taille     */
    size_t i;                               /* Boucle de parcours          */

    g_mutex_lock(&binary->goto_access);

    /* Mise en avant de la nouvelle ancienne destination */

    binary->old_gotos = realloc(binary->old_gotos, ++binary->goto_count * sizeof(vmpa2t));

    if (binary->goto_count > 1)
        memmove(&binary->old_gotos[1], &binary->old_gotos[0], (binary->goto_count - 1) * sizeof(vmpa2t));

    copy_vmpa(&binary->old_gotos[0], new);

    /* Suppression de la même destination à une autre position */

    previous_count = binary->goto_count;

    for (i = 1; i < binary->goto_count; i++)
        if (cmp_vmpa(&binary->old_gotos[i], new) == 0)
        {
            if ((i + 1) < binary->goto_count)
                memmove(&binary->old_gotos[i], &binary->old_gotos[i + 1],
                        (binary->goto_count - i - 1) * sizeof(vmpa2t));

            binary->goto_count--;
            i--;

        }

    if (previous_count != binary->goto_count)
        binary->old_gotos = realloc(binary->old_gotos, binary->goto_count * sizeof(vmpa2t));

    g_mutex_unlock(&binary->goto_access);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = élément binaire à consulter.                        *
*                count  = nombre d'éléments dans la liste renvoyée.           *
*                                                                             *
*  Description : Fournit la liste des anciennes destinations déjà visitées.   *
*                                                                             *
*  Retour      : Liste de destinations à libérer de la mémoire ou NULL.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

vmpa2t *g_loaded_binary_get_old_gotos(GLoadedBinary *binary, size_t *count)
{
    vmpa2t *result;                         /* Liste à renvoyer            */
    size_t i;                               /* Boucle de parcours          */

    g_mutex_lock(&binary->goto_access);

    *count = binary->goto_count;

    if (*count == 0)
        result = NULL;

    else
    {
        result = malloc(*count * sizeof(vmpa2t));

        for (i = 0; i < *count; i++)
            copy_vmpa(&result[i], &binary->old_gotos[i]);

    }

    g_mutex_unlock(&binary->goto_access);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                        GESTION SOUS FORME DE CONTENU CHARGE                        */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : binary  = élément binaire à traiter.                         *
*                xdoc    = structure XML en cours d'édition.                  *
*                context = contexte à utiliser pour les recherches.           *
*                path    = chemin d'accès réservé au binaire.                 *
*                                                                             *
*  Description : Interprète un contenu binaire chargé avec un appui XML.      *
*                                                                             *
*  Retour      : true si l'opération a bien tourné, false sinon.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_loaded_binary_restore(GLoadedBinary *binary, xmlDoc *xdoc, xmlXPathContext *context, const char *path)
{
    bool result;                            /* Bilan à faire remonter      */

    /* Elément divers associés au binaire */

    result = g_loaded_binary_load_storage(binary, context, path);

    if (result)
        result = g_loaded_binary_load_old_gotos(binary, context, path);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary  = élément binaire à traiter.                         *
*                xdoc    = structure XML en cours d'édition.                  *
*                context = contexte à utiliser pour les recherches.           *
*                path    = chemin d'accès réservé au binaire.                 *
*                                                                             *
*  Description : Ecrit une sauvegarde du binaire dans un fichier XML.         *
*                                                                             *
*  Retour      : true si l'opération a bien tourné, false sinon.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_loaded_binary_save(GLoadedBinary *binary, xmlDoc *xdoc, xmlXPathContext *context, const char *path)
{
    bool result;                            /* Bilan à faire remonter      */
    GBinContent *content;                   /* Contenu brut à manipuler    */
    const gchar *hash;                      /* Empreinte d'un contenu      */
    char *key;                              /* Support associé au contenu  */

    /* Mise en cache des instructions */

    result = g_loaded_binary_save_cache(binary);

    /* Elément divers associés au binaire */

    if (result)
    {
        content = g_loaded_content_get_content(G_LOADED_CONTENT(binary));

        hash = g_binary_content_get_checksum(content);
        result = add_string_attribute_to_node(xdoc, context, path, "hash", hash);

        g_object_unref(G_OBJECT(content));

    }

    /*
    if (result)
    {
        key = g_loaded_content_get_content_class(G_LOADED_CONTENT(binary));
        result = add_string_attribute_to_node(xdoc, context, path, "format", key);
        free(key);
    }

    if (result)
    {
        key = g_arch_processor_get_key(binary->proc);
        result = add_string_attribute_to_node(xdoc, context, path, "arch", key);
        free(key);
    }
    */

    if (result)
        result = g_loaded_binary_save_storage(binary, xdoc, context, path);

    if (result)
        result = g_loaded_binary_save_old_gotos(binary, xdoc, context, path);

    /* Sauvegarde côté serveur */

    if (result)
        g_analyst_client_save(binary->client);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = élément chargé à manipuler.                         *
*                                                                             *
*  Description : Fournit le contenu représenté de l'élément chargé.           *
*                                                                             *
*  Retour      : Contenu représenté.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GBinContent *g_loaded_binary_get_content(const GLoadedBinary *binary)
{
    GBinContent *result;                    /* Contenu interne à renvoyer  */

    result = g_known_format_get_content(G_KNOWN_FORMAT(binary->format));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = élément chargé à manipuler.                         *
*                human  = description humaine attendue ?                      *
*                                                                             *
*  Description : Décrit la nature du contenu reconnu pour l'élément chargé.   *
*                                                                             *
*  Retour      : Classe de contenu associée à l'élément chargé.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_loaded_binary_get_content_class(const GLoadedBinary *binary, bool human)
{
    char *result;                           /* Désignation à retourner     */
    char *part;                             /* Partie à intégrer           */

    if (human)
    {
        result = g_known_format_get_description(G_KNOWN_FORMAT(binary->format));

        result = stradd(result, ", ");

        part = g_arch_processor_get_desc(binary->proc);

        result = stradd(result, part);

        free(part);

    }
    else
    {
        result = g_known_format_get_key(G_KNOWN_FORMAT(binary->format));

        result = stradd(result, "-");

        part = g_arch_processor_get_key(binary->proc);

        result = stradd(result, part);

        free(part);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary  = élément chargé dont l'analyse est lancée.          *
*                connect = organise le lancement des connexions aux serveurs. *
*                cache   = précise si la préparation d'un rendu est demandée. *
*                gid     = groupe de travail dédié.                           *
*                status  = barre de statut à tenir informée.                  *
*                                                                             *
*  Description : Assure le désassemblage en différé.                          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_loaded_binary_analyze(GLoadedBinary *binary, bool connect, bool cache, wgroup_id_t gid, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    GBinFormat *format;                     /* Format lié au binaire       */
    char *desc;                             /* Description humaine associée*/
    bool has_virt;                          /* Présence de virtuel ?       */
    GProcContext *context;                  /* Contexte de suivi dédié     */
#ifdef INCLUDE_GTK_SUPPORT
    GWidthTracker *tracker;                 /* Gestionnaire de largeur     */
#endif

    /* Interprétation du format associé */

    format = G_BIN_FORMAT(binary->format);

    desc = g_known_format_get_description(G_KNOWN_FORMAT(format));
    assert(desc != NULL);

    log_variadic_message(LMT_INFO, _("Selected format: %s"), desc);

    free(desc);

    result = g_known_format_analyze(G_KNOWN_FORMAT(format), gid, status);
    if (!result) goto glba_exit;

    /* Interprétation de l'architecture associée */

    desc = g_arch_processor_get_desc(binary->proc);
    assert(desc != NULL);

    log_variadic_message(LMT_INFO, _("Detected architecture: %s"), desc);

    free(desc);

    g_signal_connect(binary->proc, "changed", G_CALLBACK(on_binary_processor_changed), binary);

    has_virt = g_arch_processor_has_virtual_space(binary->proc);

    g_display_options_set(binary->options[BVW_HEX], HLC_PHYSICAL, false);
    g_display_options_set(binary->options[BVW_BLOCK], DLC_VIRTUAL, has_virt);
    g_display_options_set(binary->options[BVW_GRAPH], DLC_VIRTUAL, has_virt);

    /* Phase de désassemblage pur */

    if (connect)
        g_loaded_binary_connect_internal(binary);

    disassemble_binary(binary, gid, status, &context);

    g_known_format_complete_analysis(G_KNOWN_FORMAT(format), gid, status);

    if (cache)
    {
        output_disassembly(binary, context, status, &binary->disass_cache);

#ifdef INCLUDE_GTK_SUPPORT

        tracker = g_buffer_cache_get_width_tracker(binary->disass_cache);

        g_width_tracker_build_initial_cache(tracker, gid, status);

        g_object_unref(G_OBJECT(tracker));

#endif

    }

    g_object_unref(G_OBJECT(context));

 glba_exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc   = processeur dont l'ensemble des instructions a varié.*
*                instr  = instruction à l'origine de la procédure.            *
*                added  = précise s'il s'agit d'un ajout ou d'un retrait.     *
*                binary = élément chargé à consulter.                         *
*                                                                             *
*  Description : Prend note d'une variation des instructions désassemblées.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_binary_processor_changed(GArchProcessor *proc, GArchInstruction *instr, gboolean added, GLoadedBinary *binary)
{
    const mrange_t *range;                  /* Emplacement de l'instruction*/
    BufferLineFlags flags;                  /* Propriétés pour la ligne    */
    GBinSymbol *symbol;                     /* Symbole présent à l'adresse */
    SymbolType stype;                       /* Type de symbole rencontré   */
    instr_iter_t *iter;                     /* Boucle de parcours          */
    GArchInstruction *next;                 /* Instruction suivante        */
    GLineCursor *cursor;                    /* Emplacement dans un tampon  */
    size_t index;                           /* Indice de ligne à traiter   */

    if (binary->disass_cache != NULL)
    {
        g_buffer_cache_wlock(binary->disass_cache);

        range = g_arch_instruction_get_range(instr);

        if (added)
        {
            flags = BLF_NONE;

            if (g_binary_format_find_symbol_at(G_BIN_FORMAT(binary->format), get_mrange_addr(range), &symbol))
            {
                /**
                 * Pour le choix des fanions, se référer au code similaire de
                 * la fonction print_disassembled_instructions().
                 */

                stype = g_binary_symbol_get_stype(symbol);

                if (stype == STP_ENTRY_POINT)
                    flags |= BLF_ENTRYPOINT;

                if (stype != STP_DYN_STRING)
                    flags |= BLF_WIDTH_MANAGER;

                g_object_unref(G_OBJECT(symbol));

            }

            iter = g_arch_processor_get_iter_from_address(proc, get_mrange_addr(range));

            next = get_instruction_iterator_next(iter);

            delete_instruction_iterator(iter);

            if (next == NULL)
                g_buffer_cache_append(binary->disass_cache, G_LINE_GENERATOR(instr), flags);

            else
            {
                range = g_arch_instruction_get_range(next);

                cursor = g_binary_cursor_new();
                g_binary_cursor_update(G_BINARY_CURSOR(cursor), get_mrange_addr(range));

                index = g_buffer_cache_find_index_by_cursor(binary->disass_cache, cursor, true);

                g_object_unref(G_OBJECT(cursor));

                g_object_unref(G_OBJECT(next));

                g_buffer_cache_insert_at(binary->disass_cache, index, G_LINE_GENERATOR(instr), flags, true, false);

            }

        }

        else
        {
            cursor = g_binary_cursor_new();
            g_binary_cursor_update(G_BINARY_CURSOR(cursor), get_mrange_addr(range));

            index = g_buffer_cache_find_index_by_cursor(binary->disass_cache, cursor, true);

            g_object_unref(G_OBJECT(cursor));

            g_buffer_cache_delete_at(binary->disass_cache, index);

        }

        g_buffer_cache_wunlock(binary->disass_cache);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = élément chargé à consulter.                         *
*                full   = précise s'il s'agit d'une version longue ou non.    *
*                                                                             *
*  Description : Fournit le désignation associée à l'élément chargé.          *
*                                                                             *
*  Retour      : Description courante.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_loaded_binary_describe(const GLoadedBinary *binary, bool full)
{
    char *result;                           /* Description à retourner     */
    GBinContent *content;                   /* Contenu binaire mannipulé   */

    content = g_known_format_get_content(G_KNOWN_FORMAT(binary->format));

    result = g_binary_content_describe(content, full);

    g_object_unref(G_OBJECT(content));

    return result;

}


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = contenu chargé à consulter.                         *
*                                                                             *
*  Description : Détermine le nombre de vues disponibles pour un contenu.     *
*                                                                             *
*  Retour      : Quantité strictement positive.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static unsigned int g_loaded_binary_count_views(const GLoadedBinary *binary)
{
    unsigned int result;                    /* Quantité de vues à renvoyer */

    result = BVW_COUNT;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = contenu chargé à consulter.                         *
*                index  = indice de la vue ciblée.                            *
*                                                                             *
*  Description : Fournit le nom d'une vue donnée d'un contenu chargé.         *
*                                                                             *
*  Retour      : Désignation humainement lisible.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_loaded_binary_get_view_name(const GLoadedBinary *binary, unsigned int index)
{
    char *result;                           /* Désignation à retourner     */

    switch (index)
    {
        case BVW_HEX:
            result = strdup(_("Hex view"));
            break;

        case BVW_BLOCK:
            result = strdup(_("Text view"));
            break;

        case BVW_GRAPH:
            result = strdup(_("Graph view"));
            break;

        default:
            assert(false);
            result = NULL;
            break;
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = contenu chargé à consulter.                         *
*                index  = indice de la vue ciblée.                            *
*                                                                             *
*  Description : Met en place la vue initiale pour un contenu binaire.        *
*                                                                             *
*  Retour      : Composant graphique nouveau.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GtkWidget *g_loaded_binary_build_default_view(GLoadedBinary *binary)
{
    GtkWidget *result;                      /* Support à retourner         */

    result = g_loaded_binary_build_view(binary, BVW_BLOCK);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = contenu chargé à consulter.                         *
*                index  = indice de la vue ciblée.                            *
*                                                                             *
*  Description : Met en place la vue demandée pour un contenu binaire.        *
*                                                                             *
*  Retour      : Composant graphique nouveau.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GtkWidget *g_loaded_binary_build_view(GLoadedBinary *binary, unsigned int index)
{
    GtkWidget *result;                      /* Support à retourner         */
    GBinContent *content;                   /* Contenu à représenter       */
    GtkWidget *display;                     /* Composant d'affichage       */
    GBufferCache *cache;                    /* Tampon par défaut           */
    GBufferView *view;                      /* Vue sur ce même tampon      */

    switch (index)
    {
        case BVW_HEX:
            content = g_known_format_get_content(G_KNOWN_FORMAT(binary->format));
            display = gtk_hex_display_new(content);
            g_object_unref(G_OBJECT(content));
            break;

        case BVW_BLOCK:
            cache = g_loaded_binary_get_disassembly_cache(binary);
            view = g_buffer_view_new(cache, NULL);
            display = gtk_block_display_new(view);
            break;

        case BVW_GRAPH:
            display = gtk_graph_display_new();
            break;

        default:
            assert(false);
            display = NULL;
            break;
    }

    gtk_widget_show(display);

    g_loaded_panel_set_content(G_LOADED_PANEL(display), G_LOADED_CONTENT(binary));

    result = qck_create_scrolled_window(NULL, NULL);
    gtk_container_add(GTK_CONTAINER(result), display);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = contenu chargé à consulter.                         *
*                index  = composant graphique en place.                       *
*                                                                             *
*  Description : Retrouve l'indice correspondant à la vue donnée d'un contenu.*
*                                                                             *
*  Retour      : Indice de la vue représentée, ou -1 en cas d'erreur.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static unsigned int g_loaded_binary_get_view_index(GLoadedBinary *binary, GtkWidget *view)
{
    unsigned int result;                    /* Indice à retourner          */

    if (GTK_IS_HEX_DISPLAY(view))
        result = BVW_HEX;

    else if (GTK_IS_BLOCK_DISPLAY(view))
        result = BVW_BLOCK;

    else if (GTK_IS_GRAPH_DISPLAY(view))
        result = BVW_GRAPH;

    else
    {
        assert(false);
        result = -1;
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = contenu chargé à consulter.                         *
*                index  = composant graphique à cibler.                       *
*                                                                             *
*  Description : Fournit toutes les options d'affichage pour un contenu.      *
*                                                                             *
*  Retour      : Tableau de paramètres en accès libre.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GDisplayOptions *g_loaded_binary_get_display_options(const GLoadedBinary *binary, unsigned int index)
{
    GDisplayOptions *result;                /* Instance à renvoyer         */

    if (index < BVW_COUNT)
        result = binary->options[index];
    else
        result = NULL;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


#endif
