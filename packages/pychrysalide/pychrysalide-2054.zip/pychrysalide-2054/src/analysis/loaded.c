
/* Chrysalide - Outil d'analyse de fichiers binaires
 * loaded.c - intégration des contenus chargés
 *
 * Copyright (C) 2017-2019 Cyrille Bagard
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


#include "loaded.h"


#include <assert.h>
#include <malloc.h>


#include "loaded-int.h"
#include "../core/global.h"
#include "../core/queue.h"
#include "../glibext/chrysamarshal.h"
#ifdef INCLUDE_GTK_SUPPORT
#   include "../glibext/gloadedpanel.h"
#   include "../glibext/named-int.h"
#endif
#include "../glibext/seq.h"
#include "../plugins/pglist.h"



/* ---------------------- GESTION SOUS FORME DE CONTENU CHARGE ---------------------- */


/* Données de travail */
typedef struct _analysis_data_t
{
    GLoadedContent *content;                /* Cible de l'analyse à mener  */
    bool connect;                           /* Lancement de connexions ?   */
    bool cache;                             /* Degré d'opération à mener   */

    bool success;                           /* Bilan de l'opération        */

} analysis_data_t;


/* Initialise la classe des contenus chargés. */
static void g_loaded_content_class_init(GLoadedContentClass *);

/* Initialise un contenu chargé. */
static void g_loaded_content_init(GLoadedContent *);

#ifdef INCLUDE_GTK_SUPPORT

/* Procède à l'initialisation de l'interface de composant nommé. */
static void g_loaded_content_named_init(GNamedWidgetIface *);

#endif

/* Supprime toutes les références externes. */
static void g_loaded_content_dispose(GLoadedContent *);

/* Procède à la libération totale de la mémoire. */
static void g_loaded_content_finalize(GLoadedContent *);

/* Crée une structure pour accompagner une tâche d'analyse. */
static analysis_data_t *create_analysis_data(GLoadedContent *, bool, bool);

/* Assure l'analyse d'un contenu chargé en différé. */
static bool process_analysis_with_data(analysis_data_t *, size_t, GtkStatusStack *, activity_id_t);

/* Efface une structure d'accompagnement de tâche d'analyse. */
static void delete_analysis_data(analysis_data_t *);

/* Acquitte la fin d'une tâche d'analyse différée et complète. */
static void on_loaded_content_analysis_completed(GSeqWork *, analysis_data_t *);



/* ---------------------------------------------------------------------------------- */
/*                        GESTION SOUS FORME DE CONTENU CHARGE                        */
/* ---------------------------------------------------------------------------------- */


/* Détermine le type d'une interface pour l'intégration de contenu chargé. */
#ifdef INCLUDE_GTK_SUPPORT
G_DEFINE_TYPE_WITH_CODE(GLoadedContent, g_loaded_content, G_TYPE_OBJECT,
                        G_IMPLEMENT_INTERFACE(G_TYPE_NAMED_WIDGET, g_loaded_content_named_init));
#else
G_DEFINE_TYPE(GLoadedContent, g_loaded_content, G_TYPE_OBJECT);
#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des contenus chargés.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_loaded_content_class_init(GLoadedContentClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_loaded_content_dispose;
    object->finalize = (GObjectFinalizeFunc)g_loaded_content_finalize;

    g_signal_new("analyzed",
                 G_TYPE_LOADED_CONTENT,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GLoadedContentClass, analyzed),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__BOOLEAN,
                 G_TYPE_NONE, 1, G_TYPE_BOOLEAN);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise un contenu chargé.                                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_loaded_content_init(GLoadedContent *content)
{

}


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de composant nommé.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_loaded_content_named_init(GNamedWidgetIface *iface)
{
    iface->get_name = (get_named_widget_name_fc)g_loaded_content_describe;
    iface->get_widget = (get_named_widget_widget_fc)g_loaded_content_build_default_view;

}


#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : content = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_loaded_content_dispose(GLoadedContent *content)
{
    G_OBJECT_CLASS(g_loaded_content_parent_class)->dispose(G_OBJECT(content));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_loaded_content_finalize(GLoadedContent *content)
{
    G_OBJECT_CLASS(g_loaded_content_parent_class)->finalize(G_OBJECT(content));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = élément chargé à traiter.                          *
*                xdoc    = structure XML en cours d'édition.                  *
*                context = contexte à utiliser pour les recherches.           *
*                path    = chemin d'accès réservé au binaire.                 *
*                                                                             *
*  Description : Interprète un contenu chargé avec un appui XML.              *
*                                                                             *
*  Retour      : true si l'opération a bien tourné, false sinon.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_loaded_content_restore(GLoadedContent *content, xmlDocPtr xdoc, xmlXPathContextPtr context, const char *path)
{
    bool result;                            /* Bilan à faire remonter      */
    GLoadedContentClass *class;             /* Classe de l'instance        */

    class = G_LOADED_CONTENT_GET_CLASS(content);

    if (class->restore != NULL)
        result = class->restore(content, xdoc, context, path);

    else
        result = true;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = élément chargé à traiter.                          *
*                xdoc    = structure XML en cours d'édition.                  *
*                context = contexte à utiliser pour les recherches.           *
*                path    = chemin d'accès réservé à l'élément.                *
*                                                                             *
*  Description : Ecrit une sauvegarde de l'élément dans un fichier XML.       *
*                                                                             *
*  Retour      : true si l'opération a bien tourné, false sinon.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_loaded_content_save(GLoadedContent *content, xmlDocPtr xdoc, xmlXPathContextPtr context, const char *path)
{
    bool result;                            /* Bilan à faire remonter      */
    GLoadedContentClass *class;             /* Classe de l'instance        */

    class = G_LOADED_CONTENT_GET_CLASS(content);

    if (class->save != NULL)
        result = class->save(content, xdoc, context, path);

    else
        result = true;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = élément chargé à manipuler.                        *
*                                                                             *
*  Description : Fournit le contenu représenté de l'élément chargé.           *
*                                                                             *
*  Retour      : Contenu représenté.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinContent *g_loaded_content_get_content(const GLoadedContent *content)
{
    GBinContent *result;                    /* Contenu interne à renvoyer  */
    GLoadedContentClass *class;             /* Classe de l'instance        */

    class = G_LOADED_CONTENT_GET_CLASS(content);

    result = class->get_content(content);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = élément chargé à manipuler.                        *
*                human   = description humaine attendue ?                     *
*                                                                             *
*  Description : Décrit la nature du contenu reconnu pour l'élément chargé.   *
*                                                                             *
*  Retour      : Classe de contenu associée à l'élément chargé.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_loaded_content_get_content_class(const GLoadedContent *content, bool human)
{
    char *result;                           /* Contenu interne à renvoyer  */
    GLoadedContentClass *class;             /* Classe de l'instance        */

    class = G_LOADED_CONTENT_GET_CLASS(content);

    result = class->get_content_class(content, human);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu chargé à traiter.                          *
*                connect = organise le lancement des connexions aux serveurs. *
*                cache   = précise si la préparation d'un rendu est demandée. *
*                                                                             *
*  Description : Crée une structure pour accompagner une tâche d'analyse.     *
*                                                                             *
*  Retour      : Structure d'accompagnement initialisée.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static analysis_data_t *create_analysis_data(GLoadedContent *content, bool connect, bool cache)
{
    analysis_data_t *result;            /* Structure à retourner       */

    result = malloc(sizeof(analysis_data_t));

    result->content = content;
    g_object_ref(G_OBJECT(content));

    result->connect = connect;
    result->cache = cache;

    result->success = true;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : data   = ensemble d'informations utiles à l'opération.       *
*                i      = indice des éléments à traiter.                      *
*                status = barre de statut à tenir informée.                   *
*                id     = identifiant du message affiché à l'utilisateur.     *
*                                                                             *
*  Description : Assure l'analyse d'un contenu chargé en différé.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool process_analysis_with_data(analysis_data_t *data, size_t i, GtkStatusStack *status, activity_id_t id)
{
    GLoadedContentClass *class;             /* Classe de l'instance        */
    GWorkQueue *queue;                      /* Gestionnaire de différés    */
    wgroup_id_t gid;                        /* Identifiant pour les tâches */

    class = G_LOADED_CONTENT_GET_CLASS(data->content);

    queue = get_work_queue();

    gid = g_work_queue_define_work_group(queue);

    data->success = class->analyze(data->content, data->connect, data->cache, gid, status);

    if (data->success)
        handle_loaded_content(PGA_CONTENT_ANALYZED, data->content, gid, status);

    g_work_queue_delete_work_group(queue, gid);

    return data->success;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : data = données à supprimer de la mémoire.                    *
*                                                                             *
*  Description : Efface une structure d'accompagnement de tâche d'analyse.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void delete_analysis_data(analysis_data_t *data)
{
    g_clear_object(&data->content);

    free(data);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = élément chargé à manipuler.                        *
*                connect = organise le lancement des connexions aux serveurs. *
*                cache   = précise si la préparation d'un rendu est demandée. *
*                                                                             *
*  Description : Lance l'analyse propre à l'élément chargé.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_loaded_content_analyze(GLoadedContent *content, bool connect, bool cache)
{
    analysis_data_t *data;                  /* Données d'accompagnement    */
    GSeqWork *analysis;                     /* Analyse à mener             */
    GWorkQueue *queue;                      /* Gestionnaire de différés    */

    data = create_analysis_data(content, connect, cache);

    analysis = g_gen_work_new_boolean(data, NO_ACTIVITY_ID,
                                      (seq_work_bool_cb)process_analysis_with_data, &data->success);

    g_object_set_data_full(G_OBJECT(analysis), "analysis_data", data, (GDestroyNotify)delete_analysis_data);

    g_signal_connect(analysis, "work-completed",
                     G_CALLBACK(on_loaded_content_analysis_completed), data);

    queue = get_work_queue();

    g_work_queue_schedule_work(queue, G_DELAYED_WORK(analysis), DEFAULT_WORK_GROUP);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : analysis = tâche d'analyse menée à bien.                     *
*                data     = données associées à l'opération.                  *
*                                                                             *
*  Description : Acquitte la fin d'une tâche d'analyse différée et complète.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_loaded_content_analysis_completed(GSeqWork *analysis, analysis_data_t *data)
{
    g_signal_emit_by_name(data->content, "analyzed", data->success);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = élément chargé à manipuler.                        *
*                connect = organise le lancement des connexions aux serveurs. *
*                cache   = précise si la préparation d'un rendu est demandée. *
*                                                                             *
*  Description : Lance l'analyse de l'élément chargé et attend sa conclusion. *
*                                                                             *
*  Retour      : Conclusion obtenue suite à l'analyse.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_loaded_content_analyze_and_wait(GLoadedContent *content, bool connect, bool cache)
{
    bool result;                            /* Bilan à retourner           */
    analysis_data_t *data;                  /* Données d'accompagnement    */
    GSeqWork *analysis;                     /* Analyse à mener             */
    GWorkQueue *queue;                      /* Gestionnaire de différés    */
    wgroup_id_t gid;                        /* Identifiant pour les tâches */

    data = create_analysis_data(content, connect, cache);

    analysis = g_gen_work_new_boolean(data, NO_ACTIVITY_ID,
                                      (seq_work_bool_cb)process_analysis_with_data, &data->success);

    queue = get_work_queue();

    gid = g_work_queue_define_work_group(queue);

    g_work_queue_schedule_work(queue, G_DELAYED_WORK(analysis), gid);

    g_work_queue_wait_for_completion(queue, gid);

    g_work_queue_delete_work_group(queue, gid);

    result = data->success;

    delete_analysis_data(data);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = élément chargé à consulter.                        *
*                full    = précise s'il s'agit d'une version longue ou non.   *
*                                                                             *
*  Description : Fournit le désignation associée à l'élément chargé.          *
*                                                                             *
*  Retour      : Description courante.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_loaded_content_describe(const GLoadedContent *content, bool full)
{
    char *result;                           /* Description à retourner     */
    GLoadedContentClass *class;             /* Classe de l'instance        */

    class = G_LOADED_CONTENT_GET_CLASS(content);

    result = class->describe(content, full);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = élément chargé à consulter.                        *
*                version = précise si les versions doivent être recherchées.  *
*                count   = nombre de types d'obscurcissement trouvés. [OUT]   *
*                                                                             *
*  Description : Etablit une liste d'obscurcissements présents.               *
*                                                                             *
*  Retour      : Désignations humaines correspondantes à libérer après usage  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char **g_loaded_content_detect_obfuscators(const GLoadedContent *content, bool version, size_t *count)
{
    char **result;                          /* Liste à retourner           */

    result = NULL;
    *count = 0;

    detect_external_tools(PGA_DETECTION_OBFUSCATORS, content, version, &result, count);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                             GESTION DYNAMIQUE DES VUES                             */
/* ---------------------------------------------------------------------------------- */


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu chargé à consulter.                        *
*                                                                             *
*  Description : Détermine le nombre de vues disponibles pour un contenu.     *
*                                                                             *
*  Retour      : Quantité strictement positive.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

unsigned int g_loaded_content_count_views(const GLoadedContent *content)
{
    unsigned int result;                    /* Quantité de vues à renvoyer */
    GLoadedContentClass *class;             /* Classe de l'instance        */

    class = G_LOADED_CONTENT_GET_CLASS(content);

    result = class->count_views(content);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu chargé à consulter.                        *
*                index   = indice de la vue ciblée.                           *
*                                                                             *
*  Description : Fournit le nom d'une vue donnée d'un contenu chargé.         *
*                                                                             *
*  Retour      : Désignation humainement lisible.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_loaded_content_get_view_name(const GLoadedContent *content, unsigned int index)
{
    char *result;                           /* Désignation à retourner     */
    GLoadedContentClass *class;             /* Classe de l'instance        */

    class = G_LOADED_CONTENT_GET_CLASS(content);

    assert(index <= g_loaded_content_count_views(content));

    result = class->get_view_name(content, index);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu chargé à consulter.                        *
*                                                                             *
*  Description : Met en place la vue initiale pour un contenu chargé.         *
*                                                                             *
*  Retour      : Composant graphique nouveau.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *g_loaded_content_build_default_view(GLoadedContent *content)
{
    GtkWidget *result;                      /* Support à retourner         */
    GLoadedContentClass *class;             /* Classe de l'instance        */

    class = G_LOADED_CONTENT_GET_CLASS(content);

    result = class->build_def_view(content);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu chargé à consulter.                        *
*                index   = indice de la vue ciblée.                           *
*                                                                             *
*  Description : Met en place la vue demandée pour un contenu chargé.         *
*                                                                             *
*  Retour      : Composant graphique nouveau.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *g_loaded_content_build_view(GLoadedContent *content, unsigned int index)
{
    GtkWidget *result;                      /* Support à retourner         */
    GLoadedContentClass *class;             /* Classe de l'instance        */

    class = G_LOADED_CONTENT_GET_CLASS(content);

    assert(index <= g_loaded_content_count_views(content));

    result = class->build_view(content, index);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu chargé à consulter.                        *
*                index   = composant graphique en place.                      *
*                                                                             *
*  Description : Retrouve l'indice correspondant à la vue donnée d'un contenu.*
*                                                                             *
*  Retour      : Indice de la vue représentée, ou -1 en cas d'erreur.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

unsigned int g_loaded_content_get_view_index(GLoadedContent *content, GtkWidget *view)
{
    unsigned int result;                    /* Indice à retourner          */
    GLoadedContentClass *class;             /* Classe de l'instance        */

    class = G_LOADED_CONTENT_GET_CLASS(content);

    result = class->get_view_index(content, view);

    assert(result == -1 || result <= g_loaded_content_count_views(content));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu chargé à consulter.                        *
*                index   = composant graphique à cibler.                      *
*                                                                             *
*  Description : Fournit toutes les options d'affichage pour un contenu.      *
*                                                                             *
*  Retour      : Gestionnaire de paramètres.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDisplayOptions *g_loaded_content_get_display_options(const GLoadedContent *content, unsigned int index)
{
    GDisplayOptions *result;                /* Accès aux options à renvoyer*/
    GLoadedContentClass *class;             /* Classe de l'instance        */

    assert(index <= g_loaded_content_count_views(content));

    class = G_LOADED_CONTENT_GET_CLASS(content);

    result = class->get_options(content, index);

    return result;

}


#endif



/* ---------------------------------------------------------------------------------- */
/*                         VUES ET BASCULEMENT ENTRE LES VUES                         */
/* ---------------------------------------------------------------------------------- */


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau affichant un contenu binaire.                *
*                                                                             *
*  Description : Fournit la station d'accueil d'un panneau d'affichage.       *
*                                                                             *
*  Retour      : Composant GTK fourni sans transfert de propriété.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkDockStation *get_dock_station_for_view_panel(GtkWidget *panel)
{
    GtkWidget *result;                      /* Support trouvé à retourner  */

    /**
     * La hiérarchie des composants empilés est la suivante :
     *
     *  - GtkBlockView / GtkGraphView / GtkSourceView (avec GtkViewport intégré)
     *  - GtkScrolledWindow
     *  - GtkDockStation
     *
     */

    result = gtk_widget_get_parent(panel);  /* ScrolledWindow */
    result = gtk_widget_get_parent(result);             /* DockStation */

    return GTK_DOCK_STATION(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau affichant un contenu binaire.                *
*                                                                             *
*  Description : Fournit le support défilant d'un panneau d'affichage.        *
*                                                                             *
*  Retour      : Composant GTK fourni sans transfert de propriété.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *get_scroll_window_for_view_panel(GtkWidget *panel)
{
    GtkWidget *result;                      /* Support trouvé à retourner  */

    /**
     * La hiérarchie des composants empilés est la suivante :
     *
     *  - GtkBlockView / GtkGraphView / GtkSourceView (avec GtkViewport intégré)
     *  - GtkScrolledWindow
     *  - GtkDockStation
     *
     */

    result = gtk_widget_get_parent(panel);  /* ScrolledWindow */

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : view = composant retourné par un contenu chargé.             *
*                                                                             *
*  Description : Fournit le panneau chargé inclus dans un affichage.          *
*                                                                             *
*  Retour      : Composant GTK fourni sans transfert de propriété.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *get_loaded_panel_from_built_view(GtkWidget *view)
{
    GtkWidget *result;                      /* Support trouvé à retourner  */

    if (G_IS_LOADED_PANEL(view))
        result = view;

    else
    {
        assert(GTK_IS_CONTAINER(view));

        result = NULL;

        void track_loaded_panel(GtkWidget *widget, GtkWidget **found)
        {
            if (*found == NULL)
            {
                if (G_IS_LOADED_PANEL(widget))
                    *found = widget;

                else if (GTK_IS_CONTAINER(widget))
                    gtk_container_foreach(GTK_CONTAINER(widget), (GtkCallback)track_loaded_panel, found);

            }

        }

        gtk_container_foreach(GTK_CONTAINER(view), (GtkCallback)track_loaded_panel, &result);

        assert(result != NULL);

    }

    g_object_ref(G_OBJECT(result));

    return result;

}


#endif
