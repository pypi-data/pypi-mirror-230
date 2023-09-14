
/* Chrysalide - Outil d'analyse de fichiers binaires
 * welcome.c - panneau d'accueil par défaut
 *
 * Copyright (C) 2012-2019 Cyrille Bagard
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
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#include "welcome.h"


#include <assert.h>
#include <malloc.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>


#include <i18n.h>


#include "../panel-int.h"
#include "../core/global.h"
#include "../../common/cpp.h"
#include "../../common/io.h"
#include "../../common/net.h"
#include "../../common/shuffle.h"
#include "../../core/global.h"
#include "../../core/params.h"
#include "../../core/paths.h"
#include "../../gtkext/easygtk.h"
#include "../../gtkext/named.h"



/* Panneau d'accueil par défaut (instance) */
struct _GWelcomePanel
{
    GPanelItem parent;                      /* A laisser en premier        */

    cairo_surface_t *background;            /* Fond pour astuces           */

    char **tips;                            /* Liste de toutes les astuces */
    size_t count;                           /* Quantité d'astuces          */
    size_t current;                         /* Indice de l'astuce courante */

    bool uorigin;                           /* Origine de l'affichage      */

    gulong sig_id;                          /* Connexion par signal        */

};

/* Panneau d'accueil par défaut (classe) */
struct _GWelcomePanelClass
{
    GPanelItemClass parent;                 /* A laisser en premier        */

};


/* Colonnes de la liste des messages */
typedef enum _RecentProjectColumn
{
    RPC_VALID,                              /* Validité de l'entrée        */
    RPC_FULLPATH,                           /* Chemin d'accès à un projet  */

    RPC_COUNT                               /* Nombre de colonnes          */

} RecentProjectColumn;


/* Initialise la classe des panneaux d'accueil par défaut. */
static void g_welcome_panel_class_init(GWelcomePanelClass *);

/* Initialise une instance de panneau d'accueil par défaut. */
static void g_welcome_panel_init(GWelcomePanel *);

/* Supprime toutes les références externes. */
static void g_welcome_panel_dispose(GWelcomePanel *);

/* Procède à la libération totale de la mémoire. */
static void g_welcome_panel_finalize(GWelcomePanel *);

/* Fournit le nom interne attribué à l'élément réactif. */
static char *g_welcome_panel_class_get_key(const GWelcomePanelClass *);

/* Fournit une indication sur la personnalité du panneau. */
static PanelItemPersonality g_welcome_panel_class_get_personality(const GWelcomePanelClass *);

/* Indique le chemin initial de la localisation d'un panneau. */
static char *g_welcome_panel_class_get_path(const GWelcomePanelClass *);

/* Place un panneau dans l'ensemble affiché. */
static void g_welcome_panel_dock(GWelcomePanel *);

/* Charge l'ensemble des astuces. */
static void g_welcome_panel_load_tips(GWelcomePanel *);

/* Assure le dessin du fond de la bulle d'astuce. */
static gboolean on_tip_background_draw(GtkWidget *, cairo_t *, GWelcomePanel *);

/* Réagit à la demande d'étude d'un nouveau binaire. */
static void on_new_binary_clicked(GtkButton *, GWelcomePanel *);

/* Actualise au besoin la liste des projets récents. */
static void on_recent_list_changed(GtkRecentManager *, GWelcomePanel *);

/* Recharge une liste à jour des projets récents. */
static void g_welcome_panel_reload_project_list(GWelcomePanel *, GtkRecentManager *);

/* Réagit à une sélection décidée d'un projet particulier. */
static void on_row_activated_for_projects(GtkTreeView *, GtkTreePath *, GtkTreeViewColumn *, GWelcomePanel *);

/* Enregistre les conditions d'affichage du panneau d'accueil. */
static void on_startup_toggled(GtkToggleButton *, GWelcomePanel *);

/* Consulte les versions existantes et affiche une conclusion. */
static void g_welcome_panel_check_version(GWelcomePanel *);

/* Affiche l'astuce précédente dans la liste globale. */
static void on_tip_previous_clicked(GtkButton *, GWelcomePanel *);

/* Affiche l'astuce suivante dans la liste globale. */
static void on_tip_next_clicked(GtkButton *, GWelcomePanel *);

/* Actualise l'affichage des astuces. */
static void g_welcome_panel_refresh_tip(GWelcomePanel *);


/* Indique le type défini pour un panneau d'accueil. */
G_DEFINE_TYPE(GWelcomePanel, g_welcome_panel, G_TYPE_PANEL_ITEM);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des panneaux d'accueil par défaut.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_welcome_panel_class_init(GWelcomePanelClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GEditorItemClass *item;                 /* Encore une autre vision...  */
    GPanelItemClass *panel;                 /* Version parente de classe   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_welcome_panel_dispose;
    object->finalize = (GObjectFinalizeFunc)g_welcome_panel_finalize;

    item = G_EDITOR_ITEM_CLASS(klass);

    item->get_key = (get_item_key_fc)g_welcome_panel_class_get_key;

    panel = G_PANEL_ITEM_CLASS(klass);

    panel->get_personality = (get_panel_personality_fc)g_welcome_panel_class_get_personality;
    panel->dock_at_startup = gtk_panel_item_class_return_false;
    panel->get_path = (get_panel_path_fc)g_welcome_panel_class_get_path;

    panel->ack_dock = (ack_undock_process_fc)g_welcome_panel_dock;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance de panneau d'accueil par défaut.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_welcome_panel_init(GWelcomePanel *panel)
{
    GPanelItem *pitem;                      /* Version parente du panneau  */
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeView *treeview;                  /* Affichage de la liste       */
    GtkCellRenderer *renderer;              /* Moteur de rendu de colonne  */
    GtkTreeViewColumn *column;              /* Colonne de la liste         */
    GtkToggleButton *button;                /* Bouton à bascule à traiter  */
    bool state;                             /* Etat de la coche à définir  */
    gchar *filename;                        /* Chemin d'accès à une image  */
    GtkRecentManager *manager;              /* Gestionnaire global         */

    /* Eléments de base */

    pitem = G_PANEL_ITEM(panel);

    pitem->widget = G_NAMED_WIDGET(gtk_built_named_widget_new_for_panel(_("Welcome"),
                                                                        _("Welcome panel"),
                                                                        PANEL_WELCOME_ID));

    panel->uorigin = !gtk_panel_item_class_dock_at_startup(G_PANEL_ITEM_GET_CLASS(pitem));

    /* Représentation graphique */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(pitem->widget));

    /* Liste des projets récents */

    treeview = GTK_TREE_VIEW(gtk_builder_get_object(builder, "treeview"));

    column = gtk_tree_view_column_new();
    gtk_tree_view_append_column(treeview, column);
    gtk_tree_view_set_expander_column(treeview, column);

    renderer = gtk_cell_renderer_text_new();
    gtk_tree_view_column_pack_start(column, renderer, TRUE);
    gtk_tree_view_column_add_attribute(column, renderer, "markup", RPC_FULLPATH);

    /* Affichage au démarrage ? */

    button = GTK_TOGGLE_BUTTON(gtk_builder_get_object(builder, "startup"));

    g_generic_config_get_value(get_main_configuration(), MPK_WELCOME_STARTUP, &state);

    gtk_toggle_button_set_active(button, state);

    /* Chargement de l'image de fond */

    filename = find_pixmap_file("tipoftheday.png");

    panel->background = cairo_image_surface_create_from_png(filename);

    g_free(filename);

    /* Connexion des signaux */

    gtk_builder_add_callback_symbols(builder,
                                     BUILDER_CALLBACK(on_tip_background_draw),
                                     BUILDER_CALLBACK(on_new_binary_clicked),
                                     BUILDER_CALLBACK(on_row_activated_for_projects),
                                     BUILDER_CALLBACK(on_startup_toggled),
                                     BUILDER_CALLBACK(on_tip_previous_clicked),
                                     BUILDER_CALLBACK(on_tip_next_clicked),
                                     NULL);

    gtk_builder_connect_signals(builder, panel);

    g_object_unref(G_OBJECT(builder));

    /* Actualisation du contenu du panneau */

    manager = get_project_manager();

    panel->sig_id = g_signal_connect(manager, "changed", G_CALLBACK(on_recent_list_changed), panel);

    g_welcome_panel_reload_project_list(panel, manager);

    g_welcome_panel_load_tips(panel);

    g_welcome_panel_check_version(panel);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_welcome_panel_dispose(GWelcomePanel *panel)
{
    GtkRecentManager *manager;              /* Gestionnaire global         */

    if (panel->sig_id > 0)
    {
        manager = get_project_manager();

        g_signal_handler_disconnect(manager, panel->sig_id);
        panel->sig_id = 0;

    }

    G_OBJECT_CLASS(g_welcome_panel_parent_class)->dispose(G_OBJECT(panel));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_welcome_panel_finalize(GWelcomePanel *panel)
{
    cairo_surface_destroy(panel->background);

    free(panel->tips);

    G_OBJECT_CLASS(g_welcome_panel_parent_class)->finalize(G_OBJECT(panel));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à consulter.                                  *
*                                                                             *
*  Description : Fournit le nom interne attribué à l'élément réactif.         *
*                                                                             *
*  Retour      : Désignation (courte) de l'élément de l'éditeur.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_welcome_panel_class_get_key(const GWelcomePanelClass *class)
{
    char *result;                           /* Description à renvoyer      */

    result = strdup(PANEL_WELCOME_ID);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à consulter.                                  *
*                                                                             *
*  Description : Fournit une indication sur la personnalité du panneau.       *
*                                                                             *
*  Retour      : Identifiant lié à la nature unique du panneau.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PanelItemPersonality g_welcome_panel_class_get_personality(const GWelcomePanelClass *class)
{
    PanelItemPersonality result;            /* Personnalité à retourner    */

    result = PIP_PERSISTENT_SINGLETON;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à consulter.                                  *
*                                                                             *
*  Description : Indique le chemin initial de la localisation d'un panneau.   *
*                                                                             *
*  Retour      : Chemin fixé associé à la position initiale.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_welcome_panel_class_get_path(const GWelcomePanelClass *class)
{
    char *result;                           /* Emplacement à retourner     */

    result = strdup("M");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un panneau d'accueil par défaut.                        *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GPanelItem *g_welcome_panel_new(void)
{
    GPanelItem *result;                     /* Structure à retourner       */

    result = g_object_new(G_TYPE_WELCOME_PANEL, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = composant à présenter à l'affichage.                 *
*                                                                             *
*  Description : Place un panneau dans l'ensemble affiché.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_welcome_panel_dock(GWelcomePanel *panel)
{
    g_welcome_panel_set_user_origin(panel, true);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau d'accueil à mettre à jour.                   *
*                                                                             *
*  Description : Charge l'ensemble des astuces.                               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_welcome_panel_load_tips(GWelcomePanel *panel)
{
    size_t i;                               /* Boucle de parcours          */

    char *tips[] = {

        _("There is no need to install Chrysalide on your system if you only want to give it a try.\n\n"
          "Just compile the source code and run the program from there."),

        _("Chrysalide can be used in external Python scripts by setting PYTHONPATH to the directory "
          "containing the 'pychrysalide.so' file. For instance:\n\n"
          "  cd plugins/pychrysa/.libs/\n"
          "  export PYTHONPATH=$PWD\n\n"
          "Then run the interpreter suitable to your configuration (debug or release):\n\n"
          "  python3-dbg -c 'import pychrysalide ; print(pychrysalide.mod_version())'"),

        _("All the configuration files for Chrysalide are located in $HOME/.config/chrysalide/."),

        _("The behavior of the main menu bar is copied from the one of a well known browser "
          "with a fox mascot.\n\n"
          "To make the menu bar appear and disappear, just press and release the Alt key.")

    };

    panel->count = ARRAY_SIZE(tips);

    panel->tips = (char **)calloc(panel->count, sizeof(char *));

    for (i = 0; i < panel->count; i++)
        panel->tips[i] = tips[i];

    shuffle(panel->tips, panel->count, sizeof(char *));

    panel->current = 0;

    g_welcome_panel_refresh_tip(panel);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant graphique à redessiner.                   *
*                cr     = contexte graphique à utiliser.                      *
*                panel  = panneau associé comportant des informations utiles. *
*                                                                             *
*  Description : Assure le dessin du fond de la bulle d'astuce.               *
*                                                                             *
*  Retour      : FALSE pour poursuivre la propagation de l'événement.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean on_tip_background_draw(GtkWidget *widget, cairo_t *cr, GWelcomePanel *panel)
{
    int wgt_width;                          /* Largeur disponible totale   */
    int wgt_height;                         /* Hauteur disponible totale   */
    int img_width;                          /* Largeur de l'image de fond  */
    int img_height;                         /* Hauteur de l'image de fond  */
    double scale;                           /* Echelle à appliquer         */

    if (cairo_surface_status(panel->background) == CAIRO_STATUS_SUCCESS)
    {
        wgt_width = gtk_widget_get_allocated_width(widget);
        wgt_height = gtk_widget_get_allocated_height(widget);

        img_width = cairo_image_surface_get_width(panel->background);
        img_height = cairo_image_surface_get_height(panel->background);

        scale = wgt_height / (2.0 * img_height);

        cairo_scale(cr, scale, scale);

        cairo_set_source_surface(cr, panel->background,
                                 (wgt_width / scale) - img_width,
                                 ((wgt_height / scale) - img_height) / 2);

        cairo_paint(cr);

    }

    return FALSE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : button = bouton impliqué dans la procédure.                  *
*                panel  = panneau associé comportant des informations utiles. *
*                                                                             *
*  Description : Réagit à la demande d'étude d'un nouveau binaire.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_new_binary_clicked(GtkButton *button, GWelcomePanel *panel)
{
    GObject *ref;                           /* Espace de référencements    */
    GtkMenuItem *item;                      /* Elément de menu simulé      */

    ref = G_OBJECT(get_editor_window());

    item = GTK_MENU_ITEM(g_object_get_data(ref, "mnu_project_add_binary"));

    g_object_unref(ref);

    gtk_menu_item_activate(item);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : manager = gestion de fichiers récemment utilisés.            *
*                panel   = panneau associé comportant des informations utiles.*
*                                                                             *
*  Description : Actualise au besoin la liste des projets récents.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_recent_list_changed(GtkRecentManager *manager, GWelcomePanel *panel)
{
    g_welcome_panel_reload_project_list(panel, manager);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel   = panneau comportant des informations utiles.        *
*                manager = gestion de fichiers récemment utilisés.            *
*                                                                             *
*  Description : Recharge une liste à jour des projets récents.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_welcome_panel_reload_project_list(GWelcomePanel *panel, GtkRecentManager *manager)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkListStore *store;                    /* Modèle de gestion           */
    bool empty;                             /* Liste vide ?                */
    GList *recents;                         /* Liste des fichiers récents  */
    GList *recent;                          /* Elément à traiter           */
    GtkRecentInfo *info;                    /* Informations sur l'élément  */
    GtkTreeIter iter;                       /* Point d'insertion           */

    /* Réinitialisation */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    store = GTK_LIST_STORE(gtk_builder_get_object(builder, "store"));

    gtk_list_store_clear(store);

    empty = true;

    /* Chargement */

    recents = gtk_recent_manager_get_items(manager);

    if (recents != NULL)
    {
        for (recent = g_list_first(recents); recent != NULL; recent = g_list_next(recent))
        {
            info = recent->data;

            if (strcmp(gtk_recent_info_get_mime_type(info), "application/chrysalide.project") == 0)
            {
                gtk_list_store_append(store, &iter);

                gtk_list_store_set(store, &iter,
                                   RPC_VALID, true,
                                   RPC_FULLPATH, gtk_recent_info_get_uri_display(info),
                                   -1);

                empty = false;

            }

            gtk_recent_info_unref(info);

        }

        g_list_free(recents);

    }

    /* Indication par défaut */
    if (empty)
    {
        gtk_list_store_append(store, &iter);

        gtk_list_store_set(store, &iter,
                           RPC_VALID, false,
                           RPC_FULLPATH, _("<i>(No recent project)</i>"),
                           -1);

    }

    g_object_unref(G_OBJECT(builder));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : treeview = liste graphique concernée par la procédure.       *
*                path     = chemin d'accès à la ligne sélectionnée.           *
*                column   = colonne concernée par la sélection.               *
*                panel    = panneau associé avec des informations utiles.     *
*                                                                             *
*  Description : Réagit à une sélection décidée d'un projet particulier.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_row_activated_for_projects(GtkTreeView *treeview, GtkTreePath *path, GtkTreeViewColumn *column, GWelcomePanel *panel)
{
    GtkTreeModel *model;                    /* Modèle de gestion           */
    GtkTreeIter iter;                       /* Point de la consultation    */
    gboolean valid;                         /* Validité de l'entrée        */
    gchar *filename;                        /* Chemin d'accès au projet    */
    GStudyProject *project;                 /* Nouveau projet à ouvrir     */

    model = gtk_tree_view_get_model(treeview);

    if (gtk_tree_model_get_iter(model, &iter, path))
    {
        gtk_tree_model_get(model, &iter, RPC_VALID, &valid, RPC_FULLPATH, &filename, -1);

        if (valid)
        {
            project = g_study_project_open(filename, true);

            if (project != NULL)
            {
                set_current_project(project);

                push_project_into_recent_list(project);

            }

            g_free(filename);

        }

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : button = bouton de défilement des astuces activé;            *
*                panel  = panneau associé comportant des informations utiles. *
*                                                                             *
*  Description : Enregistre les conditions d'affichage du panneau d'accueil.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_startup_toggled(GtkToggleButton *button, GWelcomePanel *panel)
{
    g_generic_config_set_value(get_main_configuration(),
                               MPK_WELCOME_STARTUP, gtk_toggle_button_get_active(button));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau d'accueil à mettre à jour.                   *
*                                                                             *
*  Description : Consulte les versions existantes et affiche une conclusion.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_welcome_panel_check_version(GWelcomePanel *panel)
{
    bool skip;                              /* Saut de la vérification     */
    bool unknown;                           /* Impossibilité de comparaison*/
    int current;                            /* Version courante            */
    int sock;                               /* Canal de communication      */
    bool status;                            /* Bilan d'une communication   */
    char buffer[1024];                      /* Tampon de réception         */
    size_t got;                             /* Quantité de données reçues  */
    char *version;                          /* Version récupérée           */
    int available;                          /* Version disponible          */
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkLabel *label;                        /* Etiquette à éditer          */
    char *msg;                              /* Message à faire paraître    */

    g_generic_config_get_value(get_main_configuration(), MPK_WELCOME_CHECK, &skip);
    skip = !skip;

    unknown = true;

    current = atoi(VERSION);

    if (skip) goto check_process;

    /* Recherche en ligne */

    sock = connect_via_tcp("www.chrysalide.re", "80", NULL);
    if (sock == -1) goto check_process;

#define REQUEST "GET /version.last HTTP/1.1\r\nHost: www.chrysalide.re\r\n\r\n"

    status = safe_send(sock, REQUEST, strlen(REQUEST), 0);
    if (!status) goto check_done;

    status = recv_all(sock, buffer, sizeof(buffer), &got);
    if (!status) goto check_done;

    version = strstr(buffer, "\r\n\r\n");

    if (version != NULL)
    {
        available = atoi(version + 4);

        unknown = false;

    }

 check_done:

    close(sock);

 check_process:

    /* Affichage */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    label = GTK_LABEL(gtk_builder_get_object(builder, "version"));

    if (skip)
        asprintf(&msg,
                 "Your version is: <b>%d</b>\n\n"               \
                 "Automatic version check is disabled.",
                 current);

    else
    {
        if (unknown)
            asprintf(&msg,
                     "Your version is: <b>%d</b>\n\n"           \
                     "Lastest available version is unknown.",
                     current);

        else
        {
            if (current >= available)
                asprintf(&msg,
                         "Your version is: <b>%d</b>\n\n"       \
                         "Lastest version is: <b>%d</b>\n\n"    \
                         "Your software is <span color='green'><b>up-to-date</b></span>.",
                         current, available);

            else
                asprintf(&msg,
                         "Your version is: <b>%d</b>\n\n"       \
                         "Lastest version is: <b>%d</b>\n\n"    \
                         "Your software is <span color='red'><b>outdated</b></span>.",
                         current, available);

        }

    }

    gtk_label_set_markup(label, msg);

    free(msg);

    g_object_unref(G_OBJECT(builder));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : button = bouton de défilement des astuces activé;            *
*                panel  = panneau associé comportant des informations utiles. *
*                                                                             *
*  Description : Affiche l'astuce précédente dans la liste globale.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_tip_previous_clicked(GtkButton *button, GWelcomePanel *panel)
{
    if (panel->current > 0)
        panel->current--;
    else
        panel->current = panel->count - 1;

    g_welcome_panel_refresh_tip(panel);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : button = bouton de défilement des astuces activé;            *
*                panel  = panneau associé comportant des informations utiles. *
*                                                                             *
*  Description : Affiche l'astuce suivante dans la liste globale.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_tip_next_clicked(GtkButton *button, GWelcomePanel *panel)
{
    if ((panel->current + 1) < panel->count)
        panel->current++;
    else
        panel->current = 0;

    g_welcome_panel_refresh_tip(panel);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau associé comportant des informations utiles.  *
*                                                                             *
*  Description : Actualise l'affichage des astuces.                           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_welcome_panel_refresh_tip(GWelcomePanel *panel)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkLabel *label;                        /* Etiquette de présentation   */

    assert(panel->current < panel->count);

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    label = GTK_LABEL(gtk_builder_get_object(builder, "tip"));

    gtk_label_set_markup(label, panel->tips[panel->current]);

    g_object_unref(G_OBJECT(builder));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau associé comportant des informations utiles.  *
*                                                                             *
*  Description : Indique l'origine de l'affichage du panneau d'accueil.       *
*                                                                             *
*  Retour      : true si l'affichage est le fait de l'utilisateur.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_welcome_panel_get_user_origin(const GWelcomePanel *panel)
{
    return panel->uorigin;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel   = panneau associé comportant des informations utiles.*
*                uorigin = true si l'affichage est le fait de l'utilisateur.  *
*                                                                             *
*  Description : Détermine l'origine de l'affichage du panneau d'accueil.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_welcome_panel_set_user_origin(GWelcomePanel *panel, bool uorigin)
{
    panel->uorigin = uorigin;

}
