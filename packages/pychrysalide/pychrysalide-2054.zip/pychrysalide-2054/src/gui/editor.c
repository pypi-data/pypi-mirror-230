
/* Chrysalide - Outil d'analyse de fichiers binaires
 * editor.c - fenêtre principale de l'interface graphique
 *
 * Copyright (C) 2015-2020 Cyrille Bagard
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


#include "editor.h"


#include <assert.h>
#include <ctype.h>
#include <malloc.h>
#include <string.h>


#include <i18n.h>


#include "agroup.h"
#include "menubar.h"
#include "status.h"
#include "dialogs/loading.h"
#include "menus/file.h"
#include "core/core.h"
#include "core/panels.h"
#include "core/global.h"
#include "core/items.h"
#include "panels/view.h"
#include "tb/portions.h"
#include "../analysis/binary.h"
#include "../common/extstr.h"
#include "../core/global.h"
#include "../core/logs.h"
#include "../core/params.h"
#include "../glibext/chrysamarshal.h"
#include "../glibext/named.h"
#include "../glibext/signal.h"
#include "../gtkext/easygtk.h"
#include "../gtkext/gtkdisplaypanel.h"
#include "../gtkext/gtkdockable.h"
#include "../gtkext/gtkdockstation.h"
#include "../gtkext/tiledgrid.h"
#include "../gtkext/support.h"
#include "../plugins/dt.h"



/* Fenêtre de chargement de binaires */
static GtkWidget *_load_dialog = NULL;
static GtkBuilder *_load_dialog_builder = NULL;



/* Met en place la liste des icônes de l'éditeur. */
static GList *build_editor_icons_list(void);

/* Construit la fenêtre de l'éditeur. */
GtkWidget *create_editor(void);

/* Applique tous les enregistrements de signaux. */
static void connect_all_editor_signals(GtkBuilder *, GObject *, const gchar *, const gchar *, GObject *, GConnectFlags, gpointer);

/* Quitte le programme en sortie de la boucle de GTK. */
static gboolean on_delete_editor(GtkWidget *, GdkEvent *, gpointer);

/* Quitte le programme en sortie de la boucle de GTK. */
static void on_destroy_editor(GtkWidget *, gpointer);



/* ------------------------- AFFICHAGE DE LA BARRE DE MENUS ------------------------- */


/* Réagit à un changement d'état pour l'éditeur. */
static gboolean on_window_state_changed(GtkWidget *, GdkEvent *, GtkBuilder *);

/* Suit la frappe de touches sur la fenêtre principale. */
static gboolean on_key_event(GtkWidget *, GdkEventKey *, GtkBuilder *);



/* ------------------------ INTEGRATION DE LA BARRE D'OUTILS ------------------------ */


/* Suit les évolutions d'affichage dans la barre d'outils. */
static void on_toolbar_item_visibility_change(GtkWidget *, GtkToolbar *);

/* Construit la barre d'outils de l'éditeur. */
static GtkWidget *build_editor_toolbar(GObject *);



/* ------------------- INTERACTIONS GRAPHIQUES LIEES AUX PANNEAUX ------------------- */


/* Réagit à la mise en place d'une nouvelle station d'accueil. */
static void on_dock_station_created(GtkTiledGrid *, GtkDockStation *, gpointer);

/* Réagit au changement d'onglet d'un panneau quelconque. */
static void on_dock_item_switch(GtkDockStation *, GtkWidget *, gpointer);

/* Encastre comme demandé un panneau dans l'éditeur. */
static void dock_panel_into_current_station(GtkCheckMenuItem *, gpointer);

/* Ajout d'un panneau dans la liste adaptée des menus. */
static bool add_side_panel_to_menu(GPanelItemClass *, GtkContainer *);

/* Réagit à une demande de menu pour rajouter des panneaux. */
static void on_dock_menu_request(GtkDockStation *, GtkWidget *, gpointer);

/* Réagit à une demande de fermeture du panneau courant. */
static void on_dock_close_request(GtkDockStation *, GtkWidget *, gpointer);



/* ------------------------- INTEGRATION ET SUIVI DE PROJET ------------------------- */


/* Réagit à un changement du projet principal. */
static void notify_editor_project_change(GStudyProject *, bool);

/* Assure un positionnement initial idéal. */
static gboolean scroll_for_the_first_time(GtkWidget *, GdkEvent *, GLoadedContent *);

/* Présente une possibilité de sélection des contenus chargés. */
static void on_editor_content_available(GStudyProject *, GLoadedContent *, void *);

/* Affiche le contenu qui vient de rejoindre un projet donné. */
static void on_editor_loaded_content_added(GStudyProject *, GLoadedContent *, void *);

/* Recherche et retirer de l'affichage un contenu chargé. */
static void remove_loaded_content_from_editor(GtkWidget *, GLoadedContent *);





/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Met en place la liste des icônes de l'éditeur.               *
*                                                                             *
*  Retour      : Liste d'images dimensionnées.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GList *build_editor_icons_list(void)
{
    GList *result;                          /* Liste à retourner           */
    GdkPixbuf *pixbuf;                      /* Image chargée en mémoire    */

    result = NULL;

    pixbuf = get_pixbuf_from_file("chrysalide-32.png");
    if (pixbuf != NULL)
        result = g_list_append(result, pixbuf);

    pixbuf = get_pixbuf_from_file("chrysalide-64.png");
    if (pixbuf != NULL)
        result = g_list_append(result, pixbuf);

    pixbuf = get_pixbuf_from_file("chrysalide-128.png");
    if (pixbuf != NULL)
        result = g_list_append(result, pixbuf);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Construit la fenêtre de l'éditeur.                           *
*                                                                             *
*  Retour      : Adresse de la fenêtre mise en place.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *create_editor(void)
{
    GtkWidget *result;                      /* Fenêtre à renvoyer          */
    GtkBuilder *builder;                    /* Constructeur principal      */
    bool hide;                              /* Cachette de la barre ?      */
    bool maximized;                         /* Affichage en plein écran ?  */
    GList *icons;                           /* Liste d'images dimensionnées*/
    GtkBox *vbox;                           /* Rangements verticaux        */
    GEditorItem *editem;                    /* Menus réactifs principaux   */
    GtkWidget *toolbar;                     /* Barre d'outils              */
    GtkWidget *grid;                        /* Affichage en tuiles         */
    GtkWidget *widget;                      /* Composant à intégrer        */

    /* Mise en place des premières pierres */

    builder = gtk_builder_new_from_resource("/org/chrysalide/gui/editor.ui");

    set_editor_builder(builder);

    result = GTK_WIDGET(gtk_builder_get_object(builder, "window"));

    g_generic_config_get_value(get_main_configuration(), MPK_TITLE_BAR, &hide);
    gtk_window_set_hide_titlebar_when_maximized(GTK_WINDOW(result), hide);

    g_generic_config_get_value(get_main_configuration(), MPK_MAXIMIZED, &maximized);
    gtk_window_maximize(GTK_WINDOW(result));

    icons = build_editor_icons_list();
    gtk_window_set_icon_list(GTK_WINDOW(result), icons);
    g_list_free_full(icons, (GDestroyNotify)g_object_unref);

    gtk_builder_add_callback_symbols(builder,
                                     BUILDER_CALLBACK(on_delete_editor),
                                     BUILDER_CALLBACK(on_destroy_editor),
                                     BUILDER_CALLBACK(on_window_state_changed),
                                     BUILDER_CALLBACK(on_key_event),
                                     NULL);

    setup_accel_group_callbacks(builder);

    /* Constitution du corps */

    vbox = GTK_BOX(gtk_builder_get_object(builder, "vbox"));

    /* Intégration des menus */

    editem = g_menu_bar_new(builder);
    register_editor_item(editem);

    /* Barre d'outils */

    toolbar = build_editor_toolbar(G_OBJECT(result));
    gtk_box_pack_start(vbox, toolbar, FALSE, FALSE, 0);

    /* Coeur de la fenêtre principale */

    grid = gtk_tiled_grid_new();
    gtk_widget_show(grid);

    set_tiled_grid(GTK_TILED_GRID(grid));

    g_signal_connect(grid, "station-created", G_CALLBACK(on_dock_station_created), NULL);

    gtk_box_pack_start(vbox, grid, TRUE, TRUE, 0);

    /* Barre de statut générale */

    editem = g_status_info_new();
    register_editor_item(editem);

    widget = g_editor_item_get_widget(editem);
    gtk_box_pack_start(vbox, widget, FALSE, FALSE, 0);

    /* Autre */

    /* ... = */prepare_drag_and_drop_window();

    /* Actualisation des contenus */

    register_project_change_notification(notify_editor_project_change);

    change_editor_items_current_content(NULL);
    change_editor_items_current_view(NULL);

    /* Préparation des fenêtres complémentaires */

    _load_dialog = create_loading_dialog(GTK_WINDOW(result), &_load_dialog_builder);

    /* Connexions finales */

    gtk_builder_connect_signals_full(builder, connect_all_editor_signals, NULL);

    g_object_unref(G_OBJECT(builder));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : builder  = constructeur (principal) visé par l'opération.    *
*                obj      = objet à traiter.                                  *
*                sig_name = désignation du signal à traiter.                  *
*                hdl_name = désignation du gestionnaire à employer.           *
*                conn_obj = approche alternative si différent de NULL.        *
*                flags    = indications à prendre en compte.                  *
*                unused   = adresse non utilisée ici.                         *
*                                                                             *
*  Description : Applique tous les enregistrements de signaux.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void connect_all_editor_signals(GtkBuilder *builder, GObject *obj, const gchar *sig_name, const gchar *hdl_name, GObject *conn_obj, GConnectFlags flags, gpointer unused)
{
    GCallback func;                         /* Gestionnaire effectif       */
    GModule *module;                        /* Module courant en soutien   */
    GMenuBar *bar;                          /* Gestion des menus           */
    void *arg;                              /* Données utilisateur choisie */

    /* Recherche de l'adresse de renvoi */

    func = gtk_builder_lookup_callback_symbol(builder, hdl_name);

    if (!func)
    {
        if (g_module_supported())
            module = g_module_open(NULL, G_MODULE_BIND_LAZY);
        else
            module = NULL;

        if (module == NULL)
        {
            log_simple_message(LMT_ERROR, _("A working GModule is required!"));
            goto exit;
        }

        if (!g_module_symbol(module, hdl_name, (gpointer)&func))
        {
            log_variadic_message(LMT_ERROR, _("Could not find signal handler '%s'"), hdl_name);
            g_module_close(module);
            goto exit;
        }

        g_module_close(module);

    }

    /* Connexion du signal à son gestionnaire */

    if (conn_obj != NULL)
        g_signal_connect_object(obj, sig_name, func, conn_obj, flags);

    else
    {
        if (strncmp(hdl_name, "mcb_", 4) == 0)
        {
            bar = G_MENU_BAR(find_editor_item_by_type(G_TYPE_MENU_BAR));
            arg = bar;
            g_object_unref(G_OBJECT(bar));
        }

        else
            arg = builder;

        g_signal_connect_data(obj, sig_name, func, arg, NULL, flags);

    }

 exit:

    ;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = fenêtre de l'éditeur de préférences.                *
*                event  = informations liées à l'événement.                   *
*                unused = adresse non utilisée ici.                           *
*                                                                             *
*  Description : Quitte le programme en sortie de la boucle de GTK.           *
*                                                                             *
*  Retour      : TRUE pour éviter la fermeture, FALSE sinon.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean on_delete_editor(GtkWidget *widget, GdkEvent *event, gpointer unused)
{
    gboolean result;                        /* Continuation à retourner    */
    bool skip;                              /* Saut de la vérification ?   */
    GStudyProject *project;                 /* Projet courant              */
    GtkWidget *dialog;                      /* Boîte à afficher            */

    result = FALSE;

    g_generic_config_get_value(get_main_configuration(), MPK_SKIP_EXIT_MSG, &skip);

    if (skip)
        goto skip_warning;

    project = get_current_project();

    if (g_study_project_get_filename(project) == NULL && g_study_project_count_contents(project) > 0)
    {
        dialog = gtk_message_dialog_new(GTK_WINDOW(widget),
                                        GTK_DIALOG_DESTROY_WITH_PARENT,
                                        GTK_MESSAGE_QUESTION,
                                        GTK_BUTTONS_NONE,
                                        _("The current project will be lost. Do you you want to save it ?"));

        gtk_dialog_add_button(GTK_DIALOG(dialog), _("_Yes"), GTK_RESPONSE_YES);
        gtk_dialog_add_button(GTK_DIALOG(dialog), _("_No"), GTK_RESPONSE_NO);
        gtk_dialog_add_button(GTK_DIALOG(dialog), _("_Cancel"), GTK_RESPONSE_CANCEL);

        switch (gtk_dialog_run(GTK_DIALOG(dialog)))
        {
            case GTK_RESPONSE_YES:
                mcb_file_save_project(NULL, NULL);
                result = (g_study_project_get_filename(project) == NULL);
                break;

            case GTK_RESPONSE_NO:
                break;

            case GTK_RESPONSE_CANCEL:
            default:
                result = TRUE;
                break;

        }

        gtk_widget_destroy(dialog);

    }

    g_object_unref(G_OBJECT(project));

 skip_warning:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = fenêtre de l'éditeur de préférences.                *
*                unused = adresse non utilisée ici.                           *
*                                                                             *
*  Description : Quitte le programme en sortie de la boucle de GTK.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_destroy_editor(GtkWidget *widget, gpointer unused)
{
    /* Fermeture propre */

    gtk_tiled_grid_save_positions(get_tiled_grid(), get_main_configuration());

    /* On évite de mettre à jour un affichage disparu... */
    register_project_change_notification(NULL);

    set_editor_builder(NULL);

    /* Si la boucle principale est bien lancée, on en sort ! */
    if (gtk_main_level() > 0)
        gtk_main_quit();

}



/* ---------------------------------------------------------------------------------- */
/*                           AFFICHAGE DE LA BARRE DE MENUS                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : widget  = fenêtre principale de l'éditeur.                   *
*                event   = informations liées à l'événement.                  *
*                builder = constructeur principal de l'interface.             *
*                                                                             *
*  Description : Réagit à un changement d'état pour l'éditeur.                *
*                                                                             *
*  Retour      : TRUE pour arrêter la propagation du signal, FALSE sinon.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean on_window_state_changed(GtkWidget *widget, GdkEvent *event, GtkBuilder *builder)
{
    gboolean result;                        /* Consommation à retourner    */
    GdkWindow *window;                      /* Fenêtre principale          */
    GdkWindowState state;                   /* Statut courant d'affichage  */
    GtkWidget *menubar;                     /* Planche de menu à traiter   */

    result = FALSE;

    window = gtk_widget_get_window(widget);

    state = gdk_window_get_state(window);

    if ((state & GDK_WINDOW_STATE_FOCUSED) == 0)
    {
        menubar = GTK_WIDGET(gtk_builder_get_object(builder, "menubar"));

        if (gtk_widget_get_visible(menubar))
            gtk_widget_hide(menubar);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget  = fenêtre principale de l'éditeur.                   *
*                event   = informations liées à l'événement.                  *
*                builder = constructeur principal de l'interface.             *
*                                                                             *
*  Description : Suit la frappe de touches sur la fenêtre principale.         *
*                                                                             *
*  Retour      : FALSE pour poursuivre la propagation de l'événement.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean on_key_event(GtkWidget *widget, GdkEventKey *event, GtkBuilder *builder)
{
    gboolean result;                        /* Consommation à retourner    */
    GtkWidget *menubar;                     /* Planche de menu à traiter   */

    result = FALSE;

    result = (event->keyval == GDK_KEY_Alt_L);

    menubar = GTK_WIDGET(gtk_builder_get_object(builder, "menubar"));

    if (gtk_widget_get_visible(menubar))
    {
        if (event->type == GDK_KEY_PRESS && event->keyval == GDK_KEY_Alt_L)
            gtk_widget_hide(menubar);

    }
    else
    {
        if (event->type == GDK_KEY_PRESS && event->keyval == GDK_KEY_Alt_L)
            gtk_widget_show(menubar);

    }

    return result;

}


/* ---------------------------------------------------------------------------------- */
/*                          INTEGRATION DE LA BARRE D'OUTILS                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : widget  = composant graphique dont l'affichage a basculé.    *
*                toolbar = barre d'outils à mettre à jour.                    *
*                                                                             *
*  Description : Suit les évolutions d'affichage dans la barre d'outils.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_toolbar_item_visibility_change(GtkWidget *widget, GtkToolbar *toolbar)
{
    bool show;                              /* Impose un affichage         */

    show = false;

    void visit_all_tb_items(GtkWidget *w, gpointer unused)
    {
        show |= gtk_widget_get_visible(w);
    }

    gtk_container_foreach(GTK_CONTAINER(toolbar), visit_all_tb_items, NULL);

    if (show)
        gtk_widget_show(GTK_WIDGET(toolbar));
    else
        gtk_widget_hide(GTK_WIDGET(toolbar));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ref = espace de référencement global.                        *
*                                                                             *
*  Description : Construit la barre d'outils de l'éditeur.                    *
*                                                                             *
*  Retour      : Adresse du composant mis en place.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GtkWidget *build_editor_toolbar(GObject *ref)
{
    GtkWidget *result;                      /* Support à retourner         */
    GEditorItem *item;                      /* Elément de barre d'outils   */

    result = gtk_toolbar_new();
    gtk_widget_show(result);
    g_object_set_data(ref, "toolbar", result);

    item = g_portions_tbitem_new(ref);
    register_editor_item(item);

    void track_tb_items_visibility(GtkWidget *widget, gpointer unused)
    {
        g_signal_connect(widget, "hide", G_CALLBACK(on_toolbar_item_visibility_change), result);
        g_signal_connect(widget, "show", G_CALLBACK(on_toolbar_item_visibility_change), result);
    }

    gtk_container_foreach(GTK_CONTAINER(result), track_tb_items_visibility, NULL);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                     INTERACTIONS GRAPHIQUES LIEES AUX PANNEAUX                     */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : grid    = composant d'affichage en tuiles concerné.          *
*                station = nouvelle station créée.                            *
*                unused  = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Réagit à la mise en place d'une nouvelle station d'accueil.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_dock_station_created(GtkTiledGrid *grid, GtkDockStation *station, gpointer unused)
{
    g_signal_connect(station, "switch-widget", G_CALLBACK(on_dock_item_switch), NULL);
    g_signal_connect(station, "menu-requested", G_CALLBACK(on_dock_menu_request), NULL);
    g_signal_connect(station, "close-requested", G_CALLBACK(on_dock_close_request), NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : station = panneau de support des éléments concerné.          *
*                item    = nouvel élément présenté à l'affichage.             *
*                unused  = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Réagit au changement d'onglet d'un panneau quelconque.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_dock_item_switch(GtkDockStation *station, GtkWidget *widget, gpointer unused)
{
    GLoadedPanel *panel;                    /* Vue du contenu chargé       */
    GLoadedContent *content;                /* Contenu en cours d'édition  */
    char *path;                             /* Chemin d'accueil concerné   */

    if (!G_IS_LOADED_PANEL(widget) && GTK_IS_SCROLLED_WINDOW(widget))
        widget = gtk_bin_get_child(GTK_BIN(widget));

    if (!G_IS_LOADED_PANEL(widget) && GTK_IS_VIEWPORT(widget))
        widget = gtk_bin_get_child(GTK_BIN(widget));

    if (G_IS_LOADED_PANEL(widget))
    {
        panel = G_LOADED_PANEL(widget);

        content = g_loaded_panel_get_content(panel);

        change_editor_items_current_content(content);

        g_object_unref(G_OBJECT(content));

        change_editor_items_current_view(panel);

    }

    else
    {
        path = gtk_tiled_grid_get_path_for_station(get_tiled_grid(), station);
        assert(path != NULL);

        if (strcmp(path, "M") == 0)
        {
            change_editor_items_current_content(NULL);
            change_editor_items_current_view(NULL);
        }

        free(path);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élement de menu actionné.                         *
*                type_ptr = type de panneau à mettre en place.                *
*                                                                             *
*  Description : Encastre comme demandé un panneau dans l'éditeur.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void dock_panel_into_current_station(GtkCheckMenuItem *menuitem, gpointer type_ptr)
{
    GType type;                             /* Type de panneau considérée  */
    GtkWidget *parent;                      /* Menu parent avec chemin     */
    const char *new_path;                   /* Nouveau chemin à appliquer  */
    GPanelItem *panel;                      /* Panneau à mettre en place   */

    type = GPOINTER_TO_SIZE(type_ptr);

    parent = gtk_widget_get_parent(GTK_WIDGET(menuitem));

    new_path = g_object_get_data(G_OBJECT(parent), "path");

    panel = g_panel_item_new(type, new_path);
    g_object_unref(G_OBJECT(panel));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel n = panneau de support des éléments concerné.          *
*                button  = bouton à l'origine de la procédure.                *
*                unsued  = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Ajout d'un panneau dans la liste adaptée des menus.          *
*                                                                             *
*  Retour      : true, par conformité avec browse_all_item_panels().          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool add_side_panel_to_menu(GPanelItemClass *class, GtkContainer *support)
{
    GEditorItem *item;                      /* Instance de panneau en place*/
    GType type;                             /* Type de panneau traité      */
    gpointer type_ptr;                      /* Autre forme d'encodage      */
    GPanelItem *panel;                      /* Panneau à manipuler         */
    GNamedWidget *named;                    /* Composant nommé associé     */
    char *label;                            /* Désignation de l'entrée     */
    GtkWidget *submenuitem;                 /* Sous-élément de menu        */
    char *bindings;                         /* Raccourcis clavier bruts    */
    GtkBuilder *builder;                    /* Constructeur principal      */

    /* Profil qui ne cadre pas ? */

    if (gtk_panel_item_class_get_personality(class) != PIP_SINGLETON)
        goto exit;

    item = find_editor_item_by_type(G_TYPE_FROM_CLASS(class));

    if (item != NULL)
    {
        if (g_panel_item_is_docked(G_PANEL_ITEM(item)))
            goto exit_ref;
    }

    /* Elément de menu */

    type = G_TYPE_FROM_CLASS(class);
    type_ptr = GSIZE_TO_POINTER(type);

    panel = create_object_from_type(type);
    named = gtk_panel_item_get_named_widget(panel);

    label = g_named_widget_get_name(named, false);

    submenuitem = qck_create_menu_item(NULL, NULL, label,
                                       G_CALLBACK(dock_panel_into_current_station), type_ptr);

    free(label);

    bindings = gtk_panel_item_class_get_key_bindings(class);

    if (bindings != NULL)
    {
        builder = get_editor_builder();
        add_accelerator_to_widget(builder, submenuitem, bindings);
        g_object_unref(G_OBJECT(builder));

        free(bindings);

    }

    gtk_container_add(support, submenuitem);

 exit_ref:

    if (item != NULL)
        g_object_unref(G_OBJECT(item));

 exit:

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : station = panneau de support des éléments concerné.          *
*                button  = bouton à l'origine de la procédure.                *
*                unsued  = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Réagit à une demande de menu pour rajouter des panneaux.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_dock_menu_request(GtkDockStation *station, GtkWidget *button, gpointer unused)
{
    GtkWidget *active;                      /* Composant actif modèle      */
    GPanelItemClass *model;                 /* Panneau encapsulé           */
    GtkContainer *menu;                     /* Support à retourner         */
    GList *children;                        /* Composants mis en place     */
    GtkWidget *nopanel;                     /* Sous-élément de menu        */

    menu = GTK_CONTAINER(qck_create_menu(NULL));

    active = gtk_notebook_get_nth_page(GTK_NOTEBOOK(station), 0);

    model = G_PANEL_ITEM_GET_CLASS(g_object_get_data(G_OBJECT(active), "dockable"));

    g_object_set_data_full(G_OBJECT(menu), "path", gtk_panel_item_class_get_path(model), free);

    /* Ajout des panneaux uniques */

    browse_all_item_panels((handle_panel_item_fc)add_side_panel_to_menu, menu);

    /* Avertissement en cas d'indisponibilité */

    children = gtk_container_get_children(GTK_CONTAINER(menu));

    if (children == NULL)
    {
        nopanel = qck_create_menu_item(NULL, NULL, "No available free panel", NULL, NULL);
        gtk_widget_set_sensitive(nopanel, FALSE);
        gtk_container_add(GTK_CONTAINER(menu), nopanel);
    }
    else
        g_list_free(children);

    /* Affichage du menu */

    gtk_menu_popup_at_widget(GTK_MENU(menu), button, GDK_GRAVITY_SOUTH_WEST, GDK_GRAVITY_NORTH_WEST, NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : station = panneau de support des éléments concerné.          *
*                button  = bouton à l'origine de la procédure.                *
*                unused  = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Réagit à une demande de fermeture du panneau courant.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_dock_close_request(GtkDockStation *station, GtkWidget *button, gpointer unused)
{
    gint index;                             /* Indice de la page courante  */
    GtkWidget *active;                      /* Composant actif modèle      */
    GPanelItem *panel;                      /* Panneau encapsulé           */

    index = gtk_notebook_get_current_page(GTK_NOTEBOOK(station));

    active = gtk_notebook_get_nth_page(GTK_NOTEBOOK(station), index);

    panel = G_PANEL_ITEM(g_object_get_data(G_OBJECT(active), "dockable"));

    g_panel_item_undock(panel);

}



/* ---------------------------------------------------------------------------------- */
/*                           INTEGRATION ET SUIVI DE PROJET                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : project = projet concerné par la procédure.                  *
*                new     = indique si le projet est le nouvel actif ou non.   *
*                                                                             *
*  Description : Réagit à un changement du projet principal.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void notify_editor_project_change(GStudyProject *project, bool new)
{
    GLoadedContent **contents;              /* Contenus chargés à traiter  */
    size_t count;                           /* Quantité de ces contenus    */
    size_t i;                               /* Boucle de parcours          */
    GtkContainer *root;                     /* Racine des panneaux         */

    g_study_project_lock_contents(project);

    contents = _g_study_project_get_contents(project, &count);

    if (new)
    {
        g_signal_connect_to_main(project, "content-available", G_CALLBACK(on_editor_content_available), NULL,
                                 g_cclosure_marshal_VOID__OBJECT);

        g_signal_connect_to_main(project, "content-added", G_CALLBACK(on_editor_loaded_content_added), NULL,
                                 g_cclosure_marshal_VOID__OBJECT);

    }

    g_study_project_unlock_contents(project);

    if (new)
    {
        for (i = 0; i < count; i++)
            on_editor_loaded_content_added(project, contents[i], NULL);

    }

    else
    {
        root = GTK_CONTAINER(get_tiled_grid());

        for (i = 0; i < count; i++)
            gtk_container_foreach(root, (GtkCallback)remove_loaded_content_from_editor, contents[i]);

    }

    if (contents != NULL)
        free(contents);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : project = project impliqué dans l'opération.                 *
*                content = nouveau contenu à éventuellement charger.          *
*                unused  = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Présente une possibilité de sélection des contenus chargés.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_editor_content_available(GStudyProject *project, GLoadedContent *content, void *unused)
{
    add_content_to_loading_dialog(_load_dialog_builder, content, project);

    gtk_widget_show(_load_dialog);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : project = project impliqué dans l'opération.                 *
*                content = nouveau contenu à présenter dans l'éditeur.        *
*                unused  = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Affiche le contenu qui vient de rejoindre un projet donné.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_editor_loaded_content_added(GStudyProject *project, GLoadedContent *content, void *unused)
{
    GPanelItem *panel;                      /* Nouveau panneau à integrer  */
    GPanelItemClass *class;                 /* Classe associée au panneau  */
#ifndef NDEBUG
    bool status;                            /* Bilan de mise en place      */
#endif
    GtkWidget *selected;                    /* Interface de prédilection   */

    panel = g_view_panel_new(G_NAMED_WIDGET(content));

    class = G_PANEL_ITEM_GET_CLASS(panel);

#ifndef NDEBUG
    status = gtk_panel_item_class_setup_configuration(class, get_main_configuration());
    assert(status);
#else
    gtk_panel_item_class_setup_configuration(class, get_main_configuration());
#endif

    selected = g_editor_item_get_widget(G_EDITOR_ITEM(panel));

    g_signal_connect(selected, "size-allocate", G_CALLBACK(scroll_for_the_first_time), content);

    g_object_unref(G_OBJECT(selected));

    g_panel_item_dock(panel);

    update_project_area(project);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget  = composant d'affichage nouvellement porté à l'écran.*
*                event   = informations liées à l'événement.                  *
*                content = contenu chargé associé au composant d'affichage.   *
*                                                                             *
*  Description : Assure un positionnement initial idéal.                      *
*                                                                             *
*  Retour      : FALSE.                                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean scroll_for_the_first_time(GtkWidget *widget, GdkEvent *event, GLoadedContent *content)
{
    GExeFormat *format;                 /* Format associé au binaire       */
    vmpa2t target;                      /* Position initiale à viser       */
    GtkWidget *panel;                   /* Panneau à dérouler              */

    g_signal_handlers_disconnect_by_func(widget, G_CALLBACK(scroll_for_the_first_time), content);

    if (G_IS_LOADED_BINARY(content))
    {
        format = g_loaded_binary_get_format(G_LOADED_BINARY(content));

        if (g_exe_format_get_main_address(format, &target))
        {
            panel = get_loaded_panel_from_built_view(widget);
            gtk_display_panel_request_move(GTK_DISPLAY_PANEL(panel), &target);
        }

        g_object_unref(G_OBJECT(format));

    }

    return FALSE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget  = composant d'affichage nouvellement porté à l'écran.*
*                content = contenu chargé associé à un composant d'affichage. *
*                                                                             *
*  Description : Recherche et retirer de l'affichage un contenu chargé.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void remove_loaded_content_from_editor(GtkWidget *widget, GLoadedContent *content)
{
    GtkNotebook *notebook;                  /* Série d'onglets à considérer*/
    gint count;                             /* Quantité de ces onglets     */
    gint i;                                 /* Boucle de parcours          */
    GtkWidget *tab;                         /* Composant d'un onglet       */
    GPanelItem *panel;                      /* Panneau encapsulé           */
    GLoadedContent *loaded;                 /* Contenu chargé à comparer   */
    GtkWidget *built;                       /* Composant construit         */

    if (GTK_IS_DOCK_STATION(widget))
    {
        /**
         * On considère qu'on est le seul à s'exécuter dans le thread d'affichage,
         * et que donc aucun ajout ne peut venir modifier la constitution des
         * onglets en cours de parcours !
         */

        notebook = GTK_NOTEBOOK(widget);

        count = gtk_notebook_get_n_pages(notebook);

        for (i = 0; i < count; i++)
        {
            tab = gtk_notebook_get_nth_page(notebook, i);

            panel = G_PANEL_ITEM(g_object_get_data(G_OBJECT(tab), "dockable"));

            if (gtk_panel_item_class_get_personality(G_PANEL_ITEM_GET_CLASS(panel)) != PIP_BINARY_VIEW)
                continue;

            built = get_loaded_panel_from_built_view(tab);

            assert(G_IS_LOADED_PANEL(built));

            loaded = g_loaded_panel_get_content(G_LOADED_PANEL(built));

            if (loaded == content)
                g_panel_item_undock(panel);

            g_object_unref(G_OBJECT(loaded));

        }

    }

    else if (GTK_IS_CONTAINER(widget))
        gtk_container_foreach(GTK_CONTAINER(widget), (GtkCallback)remove_loaded_content_from_editor, content);

}
