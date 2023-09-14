
/* Chrysalide - Outil d'analyse de fichiers binaires
 * project.c - gestion d'un groupe de fichiers binaires
 *
 * Copyright (C) 2015-2019 Cyrille Bagard
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


#include "project.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>


#include <i18n.h>


#include "loading.h"
#include "../common/xml.h"
#include "../core/global.h"
#include "../core/logs.h"
#include "../core/params.h"
#include "../core/queue.h"
#include "../glibext/chrysamarshal.h"
#include "../glibext/delayed-int.h"



/* ------------------------- DEFINITION D'UN PROJET INTERNE ------------------------- */


/* Projet d'étude regroupant les binaires analysés (instance) */
struct _GStudyProject
{
    GObject parent;                         /* A laisser en premier        */

    char *filename;                         /* Lieu d'enregistrement       */

    GLoadedContent **contents;              /* Contenus chargés et intégrés*/
    size_t count;                           /* Quantité de ces contenus    */
    GMutex mutex;                           /* Encadrement des accès       */

};


/* Projet d'étude regroupant les binaires analysés  (classe) */
struct _GStudyProjectClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    /* Signaux */

    void (* contents_available) (GStudyProject, GLoadedContent *);
    void (* content_added) (GStudyProject *, GLoadedContent *);
    void (* content_removed) (GStudyProject *, GLoadedContent *);

};


/* Initialise la classe des projets d'étude. */
static void g_study_project_class_init(GStudyProjectClass *);

/*Initialise une instance de projet d'étude. */
static void g_study_project_init(GStudyProject *);

/* Supprime toutes les références externes. */
static void g_study_project_dispose(GStudyProject *);

/* Procède à la libération totale de la mémoire. */
static void g_study_project_finalize(GStudyProject *);



/* ------------------------ INTEGRATION DE CONTENUS BINAIRES ------------------------ */


/* Assure l'intégration de contenus listés dans du XML. */
static void g_study_project_recover_binary_contents(GStudyProject *, xmlDoc *, xmlXPathContext *, bool);



/* ------------------------ CHARGEMENTS DE CONTENUS BINAIRES ------------------------ */


#define G_TYPE_LOADING_HANDLER            g_loading_handler_get_type()
#define G_LOADING_HANDLER(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_LOADING_HANDLER, GLoadingHandler))
#define G_IS_LOADING_HANDLER(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_LOADING_HANDLER))
#define G_LOADING_HANDLER_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_LOADING_HANDLER, GLoadingHandlerClass))
#define G_IS_LOADING_HANDLER_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_LOADING_HANDLER))
#define G_LOADING_HANDLER_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_LOADING_HANDLER, GLoadingHandlerClass))


/* Chargement de contenus binaires (instance) */
typedef struct _GLoadingHandler
{
    GDelayedWork parent;                    /* A laisser en premier        */

    GStudyProject *project;                 /* Projet à compléter          */
    bool cache;                             /* Degré d'opération à mener   */

    xmlDoc *xdoc;                           /* Structure XML chargée ?     */
    xmlXPathContext *context;               /* Eventuel contexte XML       */

    wgroup_id_t *exp_wids;                  /* Identifiants d'exploration  */
    size_t exp_count;                       /* Quantitié d'identifiants    */
    size_t resolved;                        /* Compteur de résolutions     */
    GCond wait_cond;                        /* Réveil d'attente de fin     */
    GMutex mutex;                           /* Encadrement des accès       */

    filter_loadable_cb filter;              /* Filtre des contenus ?       */
    void *data;                             /* Données utiles au filtrage  */

} GLoadingHandler;

/* Chargement de contenus binaires (classe) */
typedef struct _GLoadingHandlerClass
{
    GDelayedWorkClass parent;               /* A laisser en premier        */

} GLoadingHandlerClass;


/* Indique le type défini pour les tâches de chargement de contenus binaires. */
GType g_loading_handler_get_type(void);

/* Initialise la classe des tâches de chargement de contenus. */
static void g_loading_handler_class_init(GLoadingHandlerClass *);

/* Initialise une tâche de chargement de contenus binaires. */
static void g_loading_handler_init(GLoadingHandler *);

/* Supprime toutes les références externes. */
static void g_loading_handler_dispose(GLoadingHandler *);

/* Procède à la libération totale de la mémoire. */
static void g_loading_handler_finalize(GLoadingHandler *);

/* Crée une tâche de chargement de contenu bianire. */
static GLoadingHandler *g_loading_handler_new_discovering(GStudyProject *, GBinContent *, bool, filter_loadable_cb, void *);

/* Crée une tâche de chargement de contenu bianire. */
static GLoadingHandler *g_loading_handler_new_recovering(GStudyProject *, xmlDoc *, xmlXPathContext *, bool);

/* Assure le chargement de contenus binaires en différé. */
static void g_loading_handler_process(GLoadingHandler *, GtkStatusStack *);

/* Détermine si un encadrement est adapté pour un identifiant. */
static bool g_loading_handler_check(GLoadingHandler *, wgroup_id_t);

/* Note la fin d'une phase d'exploration de contenu. */
static void on_new_content_explored(GContentExplorer *, wgroup_id_t, GLoadingHandler *);

/* Note la fin d'une phase de resolution de contenu. */
static void on_new_content_resolved(GContentResolver *, wgroup_id_t, GLoadingHandler *);



/* ---------------------------------------------------------------------------------- */
/*                           DEFINITION D'UN PROJET INTERNE                           */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un projet d'étude. */
G_DEFINE_TYPE(GStudyProject, g_study_project, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des projets d'étude.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_study_project_class_init(GStudyProjectClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_study_project_dispose;
    object->finalize = (GObjectFinalizeFunc)g_study_project_finalize;

    g_signal_new("content-available",
                 G_TYPE_STUDY_PROJECT,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GStudyProjectClass, contents_available),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__OBJECT,
                 G_TYPE_NONE, 1, G_TYPE_OBJECT);

    g_signal_new("content-added",
                 G_TYPE_STUDY_PROJECT,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GStudyProjectClass, content_added),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__OBJECT,
                 G_TYPE_NONE, 1, G_TYPE_OBJECT);

    g_signal_new("content-removed",
                 G_TYPE_STUDY_PROJECT,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GStudyProjectClass, content_removed),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__OBJECT,
                 G_TYPE_NONE, 1, G_TYPE_OBJECT);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : project = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance de projet d'étude.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_study_project_init(GStudyProject *project)
{
    project->filename = NULL;

    project->contents = NULL;
    project->count = 0;
    g_mutex_init(&project->mutex);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : project = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_study_project_dispose(GStudyProject *project)
{
    size_t i;                               /* Boucle de parcours          */

    g_study_project_lock_contents(project);

    for (i = 0; i < project->count; i++)
        g_clear_object(&project->contents[i]);

    g_study_project_unlock_contents(project);

    g_mutex_clear(&project->mutex);

    G_OBJECT_CLASS(g_study_project_parent_class)->dispose(G_OBJECT(project));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : project = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_study_project_finalize(GStudyProject *project)
{
    if (project->filename != NULL)
        free(project->filename);

    if (project->contents != NULL)
        free(project->contents);

    G_OBJECT_CLASS(g_study_project_parent_class)->finalize(G_OBJECT(project));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un nouveau projet vierge.                               *
*                                                                             *
*  Retour      : Instance mise en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GStudyProject *g_study_project_new(void)
{
    GStudyProject *result;                  /* Composant à retourner       */

    result = g_object_new(G_TYPE_STUDY_PROJECT, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : filename = chemin d'accès au fichier à charger.              *
*                cache    = précise si la préparation d'un rendu est demandée.*
*                                                                             *
*  Description : Crée un projet à partir du contenu XML d'un fichier.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GStudyProject *g_study_project_open(const char *filename, bool cache)
{
    GStudyProject *result;                  /* Adresse à retourner         */
    xmlDoc *xdoc;                           /* Structure XML chargée       */
    xmlXPathContext *context;               /* Contexte pour les XPath     */

    if (!open_xml_file(filename, &xdoc, &context)) return NULL;

    result = g_study_project_new();

    result->filename = strdup(filename);

    g_study_project_recover_binary_contents(result, xdoc, context, cache);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : project  = project à sauvegarder.                            *
*                filename = nom de fichier à utiliser ou NULL pour l'existant.*
*                                                                             *
*  Description : Procède à l'enregistrement d'un projet donné.                *
*                                                                             *
*  Retour      : true si l'enregistrement s'est déroule sans encombre.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_study_project_save(GStudyProject *project, const char *filename)
{
    bool result;                            /* Bilan à retourner           */
    xmlDocPtr xdoc;                         /* Document XML à créer        */
    xmlXPathContextPtr context;             /* Contexte pour les recherches*/
    const char *final;                      /* Lieu d'enregistrement final */
    size_t i;                               /* Boucle de parcours          */
    char *access;                           /* Chemin pour une sous-config.*/

    /* Forme générale */

    result = create_new_xml_file(&xdoc, &context);

    if (result)
        result = (ensure_node_exist(xdoc, context, "/ChrysalideProject") != NULL);

    if (result)
        result = add_string_attribute_to_node(xdoc, context, "/ChrysalideProject", "version", PROJECT_XML_VERSION);

    if (result)
        result = (ensure_node_exist(xdoc, context, "/ChrysalideProject/LoadedContents") != NULL);

    final = filename != NULL ? filename : project->filename;

    /* Inscriptions des contenus */

    g_study_project_lock_contents(project);

    for (i = 0; i < project->count && result; i++)
    {
        asprintf(&access, "/ChrysalideProject/LoadedContents/Content[position()=%zu]", i + 1);

        if (result)
            result = (ensure_node_exist(xdoc, context, access) != NULL);

        if (result)
            result = g_loaded_content_save(project->contents[i], xdoc, context, access);

        free(access);

    }

    g_study_project_unlock_contents(project);

    /* Sauvegarde finale */

    if (result)
        result = save_xml_file(xdoc, final);

    if (result && filename != NULL)
    {
        if (project->filename != NULL) free(project->filename);
        project->filename = strdup(filename);

    }

    close_xml_file(xdoc, context);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : project = project à consulter.                               *
*                                                                             *
*  Description : Indique le chemin du fichier destiné à la sauvegarde.        *
*                                                                             *
*  Retour      : Chemin de fichier pour l'enregistrement ou NULL si indéfini. *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_study_project_get_filename(const GStudyProject *project)
{
    return project->filename;

}



/* ---------------------------------------------------------------------------------- */
/*                          INTEGRATION DE CONTENUS BINAIRES                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : project = projet dont le contenu est à compléter.            *
*                xdoc    = structure XML en cours d'édition.                  *
*                context = contexte à utiliser pour les recherches.           *
*                cache   = précise si la préparation d'un rendu est demandée. *
*                                                                             *
*  Description : Assure l'intégration de contenus listés dans du XML.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_study_project_recover_binary_contents(GStudyProject *project, xmlDoc *xdoc, xmlXPathContext *context, bool cache)
{
    GLoadingHandler *handler;               /* Encadrement du chargement   */

    handler = g_loading_handler_new_recovering(project, xdoc, context, cache);

    if (handler != NULL)
        g_work_queue_schedule_work(get_work_queue(), G_DELAYED_WORK(handler), LOADING_WORK_GROUP);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : project = projet dont le contenu est à compléter.            *
*                content = contenu binaire à mémoriser pour le projet.        *
*                cache   = précise si la préparation d'un rendu est demandée. *
*                filter  = procédure de filtrage de contenus chargés.         *
*                data    = données utiles à la procédure de filtre.           *
*                                                                             *
*  Description : Assure l'intégration de contenus binaires dans un projet.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_study_project_discover_binary_content(GStudyProject *project, GBinContent *content, bool cache, filter_loadable_cb filter, void *data)
{
    GLoadingHandler *handler;               /* Encadrement du chargement   */

    handler = g_loading_handler_new_discovering(project, content, cache, filter, data);

    g_work_queue_schedule_work(get_work_queue(), G_DELAYED_WORK(handler), LOADING_WORK_GROUP);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu chargé et analysé.                         *
*                success = bilan d'une analyse menée.                         *
*                project = projet avide des résultats des opérations.         *
*                                                                             *
*  Description : Réceptionne la recette d'une analyse de contenu.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void on_loaded_content_analyzed(GLoadedContent *content, gboolean success, GStudyProject *project)
{
    char *desc;                             /* Description du contenu      */

    desc = g_loaded_content_describe(content, true);

    if (success)
    {
        g_study_project_attach_content(project, content);
        log_variadic_message(LMT_INFO, _("Content from '%s' has been analyzed successfully!"), desc);
    }

    else
        log_variadic_message(LMT_ERROR, _("Failed to load '%s'"), desc);

    free(desc);

    /**
     * Le contenu a normalement été sur-référencé pour ne pas disparaître
     * en cours d'analyse.
     *
     * On revient donc à une situation nominale ici.
     */

    g_object_unref(G_OBJECT(content));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : project = project à manipuler.                               *
*                lock    = sélection du type de traitement à opérer.          *
*                                                                             *
*  Description : Verrouille ou déverrouille l'accès aux contenus chargés.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void _g_study_project_lock_unlock_contents(GStudyProject *project, bool lock)
{
    if (lock)
        g_mutex_lock(&project->mutex);
    else
        g_mutex_unlock(&project->mutex);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : project = project à manipuler.                               *
*                content = contenu chargé à associer au projet actuel.        *
*                                                                             *
*  Description : Attache un contenu donné à un projet donné.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_study_project_attach_content(GStudyProject *project, GLoadedContent *content)
{
    g_study_project_lock_contents(project);

    project->contents = realloc(project->contents, ++project->count * sizeof(GLoadedContent *));

    project->contents[project->count - 1] = content;
    g_object_ref(G_OBJECT(content));

    g_study_project_unlock_contents(project);

    g_signal_emit_by_name(project, "content-added", content);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : project = project à manipuler.                               *
*                content = contenu chargé à dissocier du projet actuel.       *
*                                                                             *
*  Description : Détache un contenu donné d'un projet donné.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_study_project_detach_content(GStudyProject *project, GLoadedContent *content)
{
    size_t i;                               /* Boucle de parcours          */

    g_study_project_lock_contents(project);

    for (i = 0; i < project->count; i++)
        if (project->contents[i] == content) break;

    if ((i + 1) < project->count)
        memmove(&project->contents[i], &project->contents[i + 1],
                (project->count - i - 1) * sizeof(GLoadedContent *));

    project->contents = realloc(project->contents, --project->count * sizeof(GLoadedContent *));

    g_study_project_unlock_contents(project);

    g_signal_emit_by_name(project, "content-removed", content);

    g_object_unref(G_OBJECT(content));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : project = projet dont le contenu est à afficher.             *
*                                                                             *
*  Description : Dénombre les contenus associés à un projet.                  *
*                                                                             *
*  Retour      : Nombre de contenus pris en compte.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t _g_study_project_count_contents(GStudyProject *project)
{
    size_t result;                          /* Quantité à retourner        */

    assert(!g_mutex_trylock(&project->mutex));

    result = project->count;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : project = projet dont le contenu est à afficher.             *
*                                                                             *
*  Description : Dénombre les contenus associés à un projet.                  *
*                                                                             *
*  Retour      : Nombre de contenus pris en compte.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_study_project_count_contents(GStudyProject *project)
{
    size_t result;                          /* Quantité à retourner        */

    g_study_project_lock_contents(project);

    result = _g_study_project_count_contents(project);

    g_study_project_unlock_contents(project);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : project = projet dont le contenu est à afficher.             *
*                count = nombre de contenus pris en compte. [OUT]             *
*                                                                             *
*  Description : Fournit l'ensemble des contenus associés à un projet.        *
*                                                                             *
*  Retour      : Liste à libérer de la mémoire.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GLoadedContent **_g_study_project_get_contents(GStudyProject *project, size_t *count)
{
    GLoadedContent **result;                /* Tableau à retourner         */
    size_t i;                               /* Boucle de parcours          */

    assert(!g_mutex_trylock(&project->mutex));

    *count = project->count;
    result = malloc(*count * sizeof(GLoadedContent *));

    for (i = 0; i < *count; i++)
    {
        result[i] = project->contents[i];
        g_object_ref(G_OBJECT(result[i]));
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : project = projet dont le contenu est à afficher.             *
*                count = nombre de contenus pris en compte. [OUT]             *
*                                                                             *
*  Description : Fournit l'ensemble des contenus associés à un projet.        *
*                                                                             *
*  Retour      : Liste à libérer de la mémoire.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GLoadedContent **g_study_project_get_contents(GStudyProject *project, size_t *count)
{
    GLoadedContent **result;                /* Tableau à retourner         */

    g_study_project_lock_contents(project);

    result = _g_study_project_get_contents(project, count);

    g_study_project_unlock_contents(project);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                          CHARGEMENTS DE CONTENUS BINAIRES                          */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour les tâches de chargement de contenus binaires. */
G_DEFINE_TYPE(GLoadingHandler, g_loading_handler, G_TYPE_DELAYED_WORK);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des tâches de chargement de contenus.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_loading_handler_class_init(GLoadingHandlerClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDelayedWorkClass *work;                /* Version en classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_loading_handler_dispose;
    object->finalize = (GObjectFinalizeFunc)g_loading_handler_finalize;

    work = G_DELAYED_WORK_CLASS(klass);

    work->run = (run_task_fc)g_loading_handler_process;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : handler = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une tâche de chargement de contenus binaires.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_loading_handler_init(GLoadingHandler *handler)
{
    GContentExplorer *explorer;             /* Explorateur de contenus     */
    GContentResolver *resolver;             /* Resolveur de contenus       */

    g_cond_init(&handler->wait_cond);
    g_mutex_init(&handler->mutex);

    explorer = get_current_content_explorer();
    g_signal_connect(explorer, "explored", G_CALLBACK(on_new_content_explored), handler);
    g_object_unref(G_OBJECT(explorer));

    resolver = get_current_content_resolver();
    g_signal_connect(resolver, "resolved", G_CALLBACK(on_new_content_resolved), handler);
    g_object_unref(G_OBJECT(resolver));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : handler = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_loading_handler_dispose(GLoadingHandler *handler)
{
    GContentExplorer *explorer;             /* Explorateur de contenus     */
    GContentResolver *resolver;             /* Resolveur de contenus       */
    size_t i;                               /* Boucle de parcours          */

    /**
     * On se sert du projet comme sentinelle pour la validité des
     * identifiants handler->exp_wids[i].
     */

    if (handler->project != NULL)
    {
        /* Supression des groupes de travail */

        explorer = get_current_content_explorer();
        resolver = get_current_content_resolver();

        g_signal_handlers_disconnect_by_func(explorer, G_CALLBACK(on_new_content_explored), handler);
        g_signal_handlers_disconnect_by_func(resolver, G_CALLBACK(on_new_content_resolved), handler);

        for (i = 0; i < handler->exp_count; i++)
        {
            g_content_resolver_delete_group(resolver, handler->exp_wids[i]);
            g_content_explorer_delete_group(explorer, handler->exp_wids[i]);
        }

        g_object_unref(G_OBJECT(explorer));
        g_object_unref(G_OBJECT(resolver));

        /* Nettoyage plus général */

        g_mutex_clear(&handler->mutex);
        g_cond_clear(&handler->wait_cond);

        g_clear_object(&handler->project);

    }

    G_OBJECT_CLASS(g_loading_handler_parent_class)->dispose(G_OBJECT(handler));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : handler = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_loading_handler_finalize(GLoadingHandler *handler)
{
    free(handler->exp_wids);

    /* Fermture de l'éventuel fichier XML de chargement */

    if (handler->xdoc != NULL)
        close_xml_file(handler->xdoc, handler->context);

    G_OBJECT_CLASS(g_loading_handler_parent_class)->finalize(G_OBJECT(handler));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : project = projet dont le contenu est à compléter.            *
*                content = contenu binaire à mémoriser pour le projet.        *
*                cache   = précise si la préparation d'un rendu est demandée. *
*                filter  = procédure de filtrage de contenus chargés.         *
*                data    = données utiles à la procédure de filtre.           *
*                                                                             *
*  Description : Crée une tâche de chargement de contenu bianire.             *
*                                                                             *
*  Retour      : Tâche créée.                                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GLoadingHandler *g_loading_handler_new_discovering(GStudyProject *project, GBinContent *content, bool cache, filter_loadable_cb filter, void *data)
{
    GLoadingHandler *result;                /* Tâche à retourner           */
    GContentExplorer *explorer;             /* Explorateur de contenus     */

    result = g_object_new(G_TYPE_LOADING_HANDLER, NULL);

    result->project = project;
    g_object_ref(G_OBJECT(result->project));

    result->cache = cache;

    result->xdoc = NULL;
    result->context = NULL;

    result->exp_wids = (wgroup_id_t *)malloc(sizeof(wgroup_id_t));
    result->exp_count = 1;

    result->resolved = 0;

    result->filter = filter;
    result->data = data;

    explorer = get_current_content_explorer();

    g_mutex_lock(&result->mutex);

    result->exp_wids[0] = g_content_explorer_create_group(explorer, content);

    g_mutex_unlock(&result->mutex);

    g_object_unref(G_OBJECT(explorer));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : project = projet dont le contenu est à compléter.            *
*                xdoc    = structure XML en cours d'édition.                  *
*                context = contexte à utiliser pour les recherches.           *
*                cache   = précise si la préparation d'un rendu est demandée. *
*                                                                             *
*  Description : Crée une tâche de chargement de contenu bianire.             *
*                                                                             *
*  Retour      : Tâche créée.                                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GLoadingHandler *g_loading_handler_new_recovering(GStudyProject *project, xmlDoc *xdoc, xmlXPathContext *context, bool cache)
{
    GLoadingHandler *result;                /* Tâche à retourner           */
    xmlXPathObjectPtr xobject;              /* Cible d'une recherche       */
    size_t count;                           /* Nombre de contenus premiers */
    GContentExplorer *explorer;             /* Explorateur de contenus     */
    size_t explored;                        /* Qté. d'explorations lancées */
    size_t i;                               /* Boucle de parcours          */
    char *access;                           /* Chemin pour un contenu      */
    GBinContent *content;                   /* Contenu binaire retrouvé    */

    xobject = get_node_xpath_object(context, "/ChrysalideProject/RootContents/Content");

    count = XPATH_OBJ_NODES_COUNT(xobject);

    if (count > 0)
    {
        result = g_object_new(G_TYPE_LOADING_HANDLER, NULL);

        result->project = project;
        g_object_ref(G_OBJECT(result->project));

        result->cache = cache;

        result->xdoc = xdoc;
        result->context = context;

        result->exp_wids = (wgroup_id_t *)malloc(count * sizeof(wgroup_id_t));

        result->resolved = 0;

        result->filter = NULL;
        result->data = NULL;

        explorer = get_current_content_explorer();

        explored = 0;

        g_mutex_lock(&result->mutex);

        for (i = 0; i < XPATH_OBJ_NODES_COUNT(xobject); i++)
        {
            asprintf(&access, "/ChrysalideProject/RootContents/Content[position()=%zu]", i + 1);

            content = NULL;//g_binary_content_new_from_xml(context, access, project->filename);

            free(access);

            if (content == NULL)
            {
                log_variadic_message(LMT_ERROR, _("Unable to load the root content #%zu ; skipping..."), i);
                continue;
            }

            result->exp_wids[explored++] = g_content_explorer_create_group(explorer, content);

            g_object_unref(G_OBJECT(content));

        }

        result->exp_count = explored;

        g_mutex_unlock(&result->mutex);

        g_object_unref(G_OBJECT(explorer));

    }

    else
        result = NULL;

    if(xobject != NULL)
        xmlXPathFreeObject(xobject);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : handler = opération de chargement à menuer.                  *
*                status  = barre de statut à tenir informée.                  *
*                                                                             *
*  Description : Assure le chargement de contenus binaires en différé.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_loading_handler_process(GLoadingHandler *handler, GtkStatusStack *status)
{
    g_mutex_lock(&handler->mutex);

    while (handler->resolved < handler->exp_count)
        g_cond_wait(&handler->wait_cond, &handler->mutex);

    g_mutex_unlock(&handler->mutex);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : handler = gestionnaire dont contenu est à consulter.         *
*                wid     = identifiant du groupe d'exploration recherché.     *
*                                                                             *
*  Description : Détermine si un encadrement est adapté pour un identifiant.  *
*                                                                             *
*  Retour      : Bilan d'adéquation.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_loading_handler_check(GLoadingHandler *handler, wgroup_id_t wid)
{
    bool result;                        /* Bilan à retourner           */
    size_t i;                           /* Boucle de parcours          */

    /**
     * Les deux appelants on_new_content_explored() et on_new_content_resolved()
     * ne doivent absolument pas poser un large verrou en filtrant les identifiants
     * via cette fonction.
     *
     * On pose donc ce verrou ici.
     *
     * La raison mineure est que les deux appelants n'accèdent qu'en lecture
     * (à peu de chose près) aux propriétés de l'objet handler.
     *
     * La raison principale est la suivante :
     *
     *    - on_new_content_explored() crée un groupe de tâches via l'appel
     *      g_content_resolver_create_group().
     *
     *    - on_new_content_resolved() peut conduire à une libération de l'objet
     *      handler, procédure qui va libérer ensuite le groupe de tâches associé.
     *
     * Ce qui peut conduire à un dead lock avec un large verrou :
     *
     *    - un thread T1 termine une résolution wid=3 ; il va donc appeler
     *      tous les handlers via le signal "resolved".
     *
     *    - T1 va rencontrer le handler qui gère wid=3. C'était la dernière
     *      résolution, donc un broadcast sur le compteur "resolved" va
     *      être émis.
     *
     *    - un thread T2 en attente dans g_loading_handler_process() va donc
     *      terminer sa tâche. Depuis la fonction g_loading_handler_dispose(),
     *      cette tâche va libérer le groupe associé, dont l'exécution est
     *      assurée par T1.
     *
     *    - le thread T2 va donc terminer sur un g_thread_join() dans la fonction
     *      g_work_group_dispose(), en attandant que T1 remarque l'ordre d'arrêt.
     *
     *    - or T1 va continuer la propagation du signal "resolved" aux autres
     *      résolveurs (par exemple, celui gérant wid=4).
     *
     *    - nouvelle exécution de on_new_content_resolved(), qui bloque cette
     *      fois, car le handler wid=4 est occupé dans un thread T3 à la fonction
     *      on_new_content_explored(), suite à un signal "explored" avec wid=4.
     *
     *    - si le verrou handler->mutex est posé en même temps que la modification
     *      des groupes de tâches, alors T1, T2 et T3 vont se bloquer mutuellement.
     */

    g_mutex_lock(&handler->mutex);

    result = false;

    for (i = 0; i < handler->exp_count && !result; i++)
        result = (handler->exp_wids[i] == wid);

    g_mutex_unlock(&handler->mutex);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : explorer = gestionnaire d'explorations à consulter.          *
*                wid      = groupe d'exploration concerné.                    *
*                handler  = gestionnaire avide des résultats des opérations.  *
*                                                                             *
*  Description : Note la fin d'une phase d'exploration de contenu.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_new_content_explored(GContentExplorer *explorer, wgroup_id_t wid, GLoadingHandler *handler)
{
    GBinContent **available;                /* Contenus binaires présents  */
    size_t count;                           /* Quantité de ces contenus    */
    GContentResolver *resolver;             /* Resolveur de contenus       */
    size_t i;                               /* Boucle de parcours          */

    if (g_loading_handler_check(handler, wid))
    {
        available = g_content_explorer_get_all(explorer, wid, &count);
        assert(count > 0);

        resolver = get_current_content_resolver();

        g_content_resolver_create_group(resolver, wid, available, count);

        g_object_unref(G_OBJECT(resolver));

        for (i = 0; i < count; i++)
            g_object_unref(G_OBJECT(available[i]));

        free(available);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : resolver = gestionnaire de résolutions à consulter.          *
*                wid      = groupe d'exploration concerné.                    *
*                handler  = gestionnaire avide des résultats des opérations.  *
*                                                                             *
*  Description : Note la fin d'une phase de resolution de contenu.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_new_content_resolved(GContentResolver *resolver, wgroup_id_t wid, GLoadingHandler *handler)
{
    GLoadedContent **available;             /* Contenus chargés valables   */
    size_t count;                           /* Quantité de ces contenus    */
    size_t i;                               /* Boucle de parcours          */
    GBinContent *content;                   /* Contenu brut à manipuler    */
    const gchar *hash;                      /* Empreinte d'un contenu      */
    char *format;                           /* Format associé à un élément */
    char *access;                           /* Chemin pour une sous-config.*/
    xmlXPathObjectPtr xobject;              /* Cible d'une recherche       */
    bool status;                            /* Bilan d'une restauration    */

    if (g_loading_handler_check(handler, wid))
    {
        available = g_content_resolver_get_all(resolver, wid, &count);

        /* Rechargement à partir d'XML ? */
        if (handler->xdoc != NULL)
        {
            assert(handler->context != NULL);

            for (i = 0; i < count; i++)
            {
                content = g_loaded_content_get_content(available[i]);
                hash = g_binary_content_get_checksum(content);
                g_object_unref(G_OBJECT(content));

                format = "FIXME";//g_loaded_content_get_format_name(available[i]);

                asprintf(&access, "/ChrysalideProject/LoadedContents/Content[@hash='%s' and @format='%s']",
                         hash, format);

                //free(format);

                xobject = get_node_xpath_object(handler->context, access);

                if (XPATH_OBJ_NODES_COUNT(xobject) > 0)
                {
                    status = g_loaded_content_restore(available[i], handler->xdoc, handler->context, access);

                    if (!status)
                        log_variadic_message(LMT_ERROR,
                                             _("Unable to reload binary from XML (hash=%s) ; skipping..."), hash);

                    else
                    {
                        /**
                         * S'il s'agit des résultats de la dernière exploration,
                         * alors les groupes contenant les éléments chargés vont
                         * être libéré, potentiellement pendant l'analyse.
                         *
                         * On temporise en incrémentant les références.
                         */
                        g_object_ref(G_OBJECT(available[i]));

                        g_signal_connect(available[i], "analyzed",
                                         G_CALLBACK(on_loaded_content_analyzed), handler->project);

                        g_loaded_content_analyze(available[i], !is_batch_mode(), handler->cache);

                    }

                }

                free(access);

                if(xobject != NULL)
                    xmlXPathFreeObject(xobject);

                g_object_unref(G_OBJECT(available[i]));

            }

        }

        /* Découverte(s) initiale(s) ? */
        else
        {
            if (is_batch_mode())
            {
                for (i = 0; i < count; i++)
                {
                    if (handler->filter == NULL || handler->filter(available[i], handler->data))
                    {
                        /**
                         * S'il s'agit des résultats de la dernière exploration,
                         * alors les groupes contenant les éléments chargés vont
                         * être libérés, potentiellement pendant l'analyse.
                         *
                         * On temporise en incrémentant les références.
                         */
                        g_object_ref(G_OBJECT(available[i]));

                        g_signal_connect(available[i], "analyzed",
                                         G_CALLBACK(on_loaded_content_analyzed), handler->project);

                        g_loaded_content_analyze(available[i], !is_batch_mode(), handler->cache);

                    }

                    g_object_unref(G_OBJECT(available[i]));

                }

                if (handler->filter != NULL)
                    handler->filter(NULL, handler->data);

            }

            else
                for (i = 0; i < count; i++)
                {
                    g_signal_emit_by_name(handler->project, "content-available", available[i]);
                    g_object_unref(G_OBJECT(available[i]));
                }

        }

        /* Dans tous les cas... */
        if (available != NULL)
            free(available);

        /* Si c'était la dernière résolution... */

        g_mutex_lock(&handler->mutex);

        handler->resolved++;

        g_cond_broadcast(&handler->wait_cond);

        g_mutex_unlock(&handler->mutex);

    }

}



/* ---------------------------------------------------------------------------------- */
/*                           GESTION GLOBALISEE DES PROJETS                           */
/* ---------------------------------------------------------------------------------- */


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Fournit le gestionnaire des projets connus.                  *
*                                                                             *
*  Retour      : Instance de gestion unique.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkRecentManager *get_project_manager(void)
{
    static GtkRecentManager *result = NULL; /* Singleton à retourner       */

    if (result == NULL)
    {
        result = gtk_recent_manager_get_default();
        //gtk_recent_manager_purge_items(result, NULL);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : project = projet à traiter.                                  *
*                                                                             *
*  Description : Place un projet au sommet de la pile des projets récents.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void push_project_into_recent_list(const GStudyProject *project)
{
    GtkRecentManager *manager;              /* Gestionnaire global         */
    char *qualified;                        /* Chemin avec 'file://'       */
    GtkRecentData recent;                   /* Données complètes           */

    if (project->filename == NULL)
        return;

    /* Constitution de la liste des projets récents */

    manager = get_project_manager();

    qualified = (char *)calloc(strlen("file://") + strlen(project->filename) + 1, sizeof(char));

    strcpy(qualified, "file://");
    strcat(qualified, project->filename);

    memset(&recent, 0, sizeof(GtkRecentData));

    recent.mime_type = "application/chrysalide.project";
    recent.app_name = "Chrysalide";
    recent.app_exec = "chrysalide -p %f";

    gtk_recent_manager_add_full(manager, qualified, &recent);

    free(qualified);

    /* Pour la prochaine ouverture du programme... */

    g_generic_config_set_value(get_main_configuration(), MPK_LAST_PROJECT, project->filename);

}


#endif
