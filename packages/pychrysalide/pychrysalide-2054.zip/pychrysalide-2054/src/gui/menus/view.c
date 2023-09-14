
/* Chrysalide - Outil d'analyse de fichiers binaires
 * view.c - gestion du menu 'Affichage'
 *
 * Copyright (C) 2012-2020 Cyrille Bagard
 *
 *  This view is part of Chrysalide.
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


#include "view.h"


#include <assert.h>
#include <malloc.h>
#include <stdio.h>


#include <i18n.h>


#include "../agroup.h"
#include "../item-int.h"
#include "../core/global.h"
#include "../core/items.h"
#include "../core/panels.h"
#include "../../analysis/loaded.h"
#include "../../gtkext/easygtk.h"
#include "../../gtkext/gtkdisplaypanel.h"
#include "../../gtkext/gtkgraphdisplay.h"
#include "../../plugins/dt.h"



/* Retire un sous-menu d'un menu. */
static void remove_panel_menu_item(GtkWidget *, GtkContainer *);

/* Filtre pour parcours de panneaux */
typedef struct _panels_loading_filter
{
    GMenuBar *bar;                          /* Barre de menus principale   */
    GtkContainer *support;                  /* Support pour éléments       */

    PanelItemPersonality personality;       /* Nature des éléments attendus*/
    bool first;                             /* Premier ajout ?             */

} panels_loading_filter;

/* Ajoute un panneau à la liste des panneaux existants. */
static bool add_side_panel_to_list(GPanelItemClass *, panels_loading_filter *);

/* Réagit avec le menu "Affichage -> Panneaux latéraux -> ...". */
static void mcb_view_change_panel_docking(GtkCheckMenuItem *, gpointer);

/* Réagit avec le menu "Affichage -> Vue xxx". */
static void mcb_view_change_support(GtkRadioMenuItem *, gpointer);

/* Réagit avec le menu "Affichage -> Basculer vers le suivant". */
static void mcb_view_switch_to_next_support(GtkRadioMenuItem *, GMenuBar *);

/* Réagit avec le menu "Affichage -> Basculer vers le précédent". */
static void mcb_view_switch_to_prev_support(GtkRadioMenuItem *, GMenuBar *);

/* Accompagne la première allocation d'un panneau d'affichage. */
static void handle_loaded_panel_first_allocation(GtkWidget *, GdkRectangle *, GLineCursor *);

/* Effectue la bascule d'un panneau de chargement à un autre. */
static void change_current_view_support(unsigned int);

/* Réagit avec le menu "Affichage -> Zoom *". */
static void mcb_view_zoom(GtkCheckMenuItem *, gpointer );

/* Réagit avec le menu "Affichage -> (colonne xxx)". */
static void mcb_view_display_column(GtkCheckMenuItem *, gpointer);

/* Réagit avec le menu "Affichage -> Plein écran". */
static void mcb_view_show_full_screen(GtkCheckMenuItem *, gpointer);

/* Met à jour les accès du menu "Affichage -> Basculer...". */
static void update_switch_access_in_menu_view(GtkBuilder *);



/******************************************************************************
*                                                                             *
*  Paramètres  : builder = constructeur avec l'ensemble des références.       *
*                                                                             *
*  Description : Complète la définition du menu "Affichage".                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void setup_menu_view_callbacks(GtkBuilder *builder)
{
    GObject *item;                          /* Elément à compléter         */

    gtk_builder_add_callback_symbols(builder,
                                     BUILDER_CALLBACK(mcb_view_update_side_panels_list),
                                     BUILDER_CALLBACK(mcb_view_switch_to_next_support),
                                     BUILDER_CALLBACK(mcb_view_switch_to_prev_support),
                                     BUILDER_CALLBACK(mcb_view_zoom),
                                     BUILDER_CALLBACK(mcb_view_show_full_screen),
                                     NULL);

    /* Affichage -> Panneaux latéraux */

    item = gtk_builder_get_object(builder, "view_side_panels");

    qck_create_menu(GTK_MENU_ITEM(item));

    /* Zooms */

    item = gtk_builder_get_object(builder, "view_zoom_in");
    g_object_set_data(item, "kind_of_zoom", GINT_TO_POINTER(0));

    item = gtk_builder_get_object(builder, "view_zoom_out");
    g_object_set_data(item, "kind_of_zoom", GINT_TO_POINTER(1));

    item = gtk_builder_get_object(builder, "view_zoom_reset");
    g_object_set_data(item, "kind_of_zoom", GINT_TO_POINTER(2));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget    = composant graphique à retirer de l'affichage.    *
*                container = conteneur graphique à vider.                     *
*                                                                             *
*  Description : Retire un sous-menu d'un menu.                               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void remove_panel_menu_item(GtkWidget *widget, GtkContainer *container)
{
    gtk_container_remove(container, widget);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class  = classe de panneau à traiter.                        *
*                filter = filtre pour le parcours de l'ensemble des panneaux. *
*                                                                             *
*  Description : Ajoute un panneau à la liste des panneaux existants.         *
*                                                                             *
*  Retour      : true, par conformité avec browse_all_item_panels().          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool add_side_panel_to_list(GPanelItemClass *class, panels_loading_filter *filter)
{
    GType type;                             /* Type de panneau traité      */
    gpointer type_ptr;                      /* Autre forme d'encodage      */
    GPanelItem *panel;                      /* Panneau à manipuler         */
    GNamedWidget *named;                    /* Composant nommé associé     */
    char *label;                            /* Désignation de l'entrée     */
    GtkWidget *submenuitem;                 /* Sous-élément de menu        */
    char *bindings;                         /* Raccourcis clavier bruts    */
    GtkBuilder *builder;                    /* Constructeur principal      */
    GEditorItem *item;                      /* Instance de panneau en place*/

    if (gtk_panel_item_class_get_personality(class) != filter->personality)
        goto exit;

    /* Séparation */

    if (filter->first)
    {
        filter->first = false;

        submenuitem = qck_create_menu_separator();
        gtk_container_add(filter->support, submenuitem);

    }

    /* Elément de menu */

    type = G_TYPE_FROM_CLASS(class);
    type_ptr = GSIZE_TO_POINTER(type);

    panel = create_object_from_type(type);
    named = gtk_panel_item_get_named_widget(panel);

    label = g_named_widget_get_name(named, false);

    submenuitem = qck_create_check_menu_item(NULL, NULL, label,
                                             G_CALLBACK(mcb_view_change_panel_docking), type_ptr);

    free(label);

    g_object_unref(G_OBJECT(named));
    g_object_unref(G_OBJECT(panel));

    bindings = gtk_panel_item_class_get_key_bindings(class);

    if (bindings != NULL)
    {
        builder = g_menu_bar_get_builder(filter->bar);
        add_accelerator_to_widget(builder, submenuitem, bindings);
        g_object_unref(G_OBJECT(builder));

        free(bindings);

    }

    gtk_container_add(filter->support, submenuitem);

    /* Statut de la coche */

    item = find_editor_item_by_type(type);

    if (item != NULL)
    {
        if (g_panel_item_is_docked(G_PANEL_ITEM(item)))
        {
            g_signal_handlers_disconnect_by_func(submenuitem, G_CALLBACK(mcb_view_change_panel_docking), type_ptr);

            gtk_check_menu_item_set_active(GTK_CHECK_MENU_ITEM(submenuitem), TRUE);

            g_signal_connect(submenuitem, "toggled", G_CALLBACK(mcb_view_change_panel_docking), type_ptr);

        }

        g_object_unref(G_OBJECT(item));

    }

 exit:

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                bar      = barre de menu parente.                            *
*                                                                             *
*  Description : Réagit avec le menu "Affichage -> Panneaux latéraux".        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void mcb_view_update_side_panels_list(GtkMenuItem *menuitem, GMenuBar *bar)
{
    GtkWidget *menu;                        /* Support pour éléments       */
    panels_loading_filter pfilter;          /* Mécanismes de filtrage      */

    menu = gtk_menu_item_get_submenu(menuitem);

    /* Réinitialisation */

    gtk_container_foreach(GTK_CONTAINER(menu), (GtkCallback)remove_panel_menu_item, menu);

    /* Ajout des panneaux uniques */

    pfilter.bar = bar;
    pfilter.support = GTK_CONTAINER(menu);

    pfilter.personality = PIP_PERSISTENT_SINGLETON;
    pfilter.first = false;

    browse_all_item_panels((handle_panel_item_fc)add_side_panel_to_list, &pfilter);

    pfilter.personality = PIP_SINGLETON;
    pfilter.first = true;

    browse_all_item_panels((handle_panel_item_fc)add_side_panel_to_list, &pfilter);

    pfilter.personality = PIP_OTHER;
    pfilter.first = true;

    browse_all_item_panels((handle_panel_item_fc)add_side_panel_to_list, &pfilter);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu ayant basculé.                    *
*                type_ptr = type de panneau à mettre en place.                *
*                                                                             *
*  Description : Réagit avec le menu "Affichage -> Panneaux latéraux -> ...". *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_view_change_panel_docking(GtkCheckMenuItem *menuitem, gpointer type_ptr)
{
    GType type;                             /* Type de panneau considérée  */
    GEditorItem *item;                      /* Instance de panneau en place*/
    GPanelItem *panel;                      /* Instance de panneau créée   */

    /**
     * Comme l'accrochage et le décrochage d'un panneau peuvent se réaliser
     * sans l'aide de ce menu (via les menus des stations d'accueil par exemple),
     * on ne peut se baser sur l'état de ce menu, mis à jour uniquement à
     * l'affichage, pour basculer lors de l'activation dudit menu via les raccourcis.
     *
     * L'appel suivant peut donc conduire à des erreurs, ie on réaccroche un
     * panneau déjà accroché ou l'inverse :
     *
     *    active = gtk_check_menu_item_get_active(menuitem);
     *
     * On préfèrera donc se baser sur l'état courant du panneau.
     */

    type = GPOINTER_TO_SIZE(type_ptr);

    item = find_editor_item_by_type(type);

    if (item == NULL)
    {
        panel = g_panel_item_new(type, "");
        g_object_unref(G_OBJECT(panel));
    }

    else
    {
        panel = G_PANEL_ITEM(item);

        if (g_panel_item_is_docked(panel))
            g_panel_item_undock(panel);
        else
            g_panel_item_dock(panel);

        g_object_unref(G_OBJECT(item));

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu ayant basculé.                    *
*                unused   = adresse non utilisée ici.                         *
*                                                                             *
*  Description : Réagit avec le menu "Affichage -> Vue xxx".                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_view_change_support(GtkRadioMenuItem *menuitem, gpointer unused)
{
    GSList *group;                          /* Liste de menus radio        */
    GSList *iter;                           /* Boucle de parcours          */
    unsigned int wanted;                    /* Nouvelle vue à présenter    */

    /* On ne traite qu'une seule fois ! */
    if (!gtk_check_menu_item_get_active(GTK_CHECK_MENU_ITEM(menuitem))) return;

    group = gtk_radio_menu_item_get_group(menuitem);

    for (iter = group; iter != NULL; iter = g_slist_next(iter))
    {
        if (!gtk_check_menu_item_get_active(GTK_CHECK_MENU_ITEM(iter->data))) continue;

        wanted = GPOINTER_TO_UINT(g_object_get_data(G_OBJECT(iter->data), "kind_of_view"));

        change_current_view_support(wanted);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu ayant basculé.                    *
*                bar      = barre de menu parente.                            *
*                                                                             *
*  Description : Réagit avec le menu "Affichage -> Basculer vers le suivant". *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_view_switch_to_next_support(GtkRadioMenuItem *menuitem, GMenuBar *bar)
{
    GLoadedPanel *panel;                    /* Afficheur effectif de code  */
    GLoadedContent *content;                /* Contenu représenté          */
    unsigned int index;                     /* Indice de la vue courante   */
#ifndef NDEBUG
    unsigned int count;                     /* Nombre de vues possibles    */
#endif
    GtkBuilder *builder;                    /* Constructeur lié au menu    */

    panel = get_current_view();
    content = g_loaded_panel_get_content(panel);

    index = g_loaded_content_get_view_index(content, GTK_WIDGET(panel));

#ifndef NDEBUG
    count = g_loaded_content_count_views(content);

    assert((index + 1) < count);
#endif

    change_current_view_support(index + 1);

    g_object_unref(G_OBJECT(content));
    g_object_unref(G_OBJECT(panel));

    builder = g_menu_bar_get_builder(bar);

    update_switch_access_in_menu_view(builder);

    g_object_unref(G_OBJECT(builder));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu ayant basculé.                    *
*                bar      = barre de menu parente.                            *
*                                                                             *
*  Description : Réagit avec le menu "Affichage -> Basculer ... précédent".   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_view_switch_to_prev_support(GtkRadioMenuItem *menuitem, GMenuBar *bar)
{
    GLoadedPanel *panel;                    /* Afficheur effectif de code  */
    GLoadedContent *content;                /* Contenu représenté          */
    unsigned int index;                     /* Indice de la vue courante   */
    GtkBuilder *builder;                    /* Constructeur lié au menu    */

    panel = get_current_view();
    content = g_loaded_panel_get_content(panel);

    index = g_loaded_content_get_view_index(content, GTK_WIDGET(panel));

    assert(index > 0);

    change_current_view_support(index - 1);

    g_object_unref(G_OBJECT(content));
    g_object_unref(G_OBJECT(panel));

    builder = g_menu_bar_get_builder(bar);

    update_switch_access_in_menu_view(builder);

    g_object_unref(G_OBJECT(builder));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant graphique visé par la procédure.          *
*                alloc  = emplacement accordé à ce composant.                 *
*                cursor = emplacement transmis à présenter en premier lieu.   *
*                                                                             *
*  Description : Accompagne la première allocation d'un panneau d'affichage.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void handle_loaded_panel_first_allocation(GtkWidget *widget, GdkRectangle *alloc, GLineCursor *cursor)
{
    /* On ne réagit que la première fois */
    g_signal_handlers_disconnect_by_func(widget, G_CALLBACK(handle_loaded_panel_first_allocation), cursor);

    g_loaded_panel_scroll_to_cursor(G_LOADED_PANEL(widget), cursor, SPT_TOP, true);

    g_object_unref(G_OBJECT(cursor));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : wanted = indice de la vue désirée.                           *
*                                                                             *
*  Description : Effectue la bascule d'un panneau de chargement à un autre.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void change_current_view_support(unsigned int wanted)
{
    GLoadedPanel *panel;                    /* Afficheur effectif de code  */
    GtkDockStation *station;                /* Base du remplacement        */
    GLoadedContent *content;                /* Contenu représenté          */
    GtkWidget *support;                     /* Nouvel afficheur généraliste*/
    GLoadedPanel *new;                      /* Panneau encapsulé           */
    GLineCursor *cursor;                    /* Position à transmettre      */

    panel = get_current_view();

    station = get_dock_station_for_view_panel(GTK_WIDGET(panel));

    content = g_loaded_panel_get_content(panel);

    support = g_loaded_content_build_view(content, wanted);

    g_object_unref(G_OBJECT(content));

    gtk_dock_panel_change_active_widget(station, support);

    new = G_LOADED_PANEL(get_loaded_panel_from_built_view(support));

    cursor = g_loaded_panel_get_cursor(panel);

    change_editor_items_current_view(new);

    if (cursor != NULL)
    {
        /**
         * A ce stade, le nouveau composant d'affichage n'a pas encore connu son
         * premier gtk_widget_size_allocate(). Cela viendra avec un événement ultérieur
         * à celui déclenché pour ce menu.
         *
         * Dans les faits, cette situation est notable pour la vue en graphique :
         * tous les blocs basiques chargés et intégrés dedans ont une position
         * égale à -1 et une dimension d'un pixel.
         *
         * La recherche du bloc présent à une position donnée échoue donc dans la
         * fonction gtk_graph_display_move_caret_to(), appelée in fine par
         * g_loaded_panel_scroll_to_cursor().
         *
         * Et au final, le curseur d'origine n'est pas transmis, et donc pas
         * transmissible non plus par la suite.
         *
         * On se doit ainsi d'attendre l'attribution des emplacements avant de déplacer
         * le curseur et de terminer de cet fait les opérations.
         */

        g_signal_connect(new, "size-allocate", G_CALLBACK(handle_loaded_panel_first_allocation), cursor);

    }

    g_object_unref(G_OBJECT(new));

    g_object_unref(G_OBJECT(panel));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                unused   = adresse non utilisée ici.                         *
*                                                                             *
*  Description : Réagit avec le menu "Affichage -> Zoom *".                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_view_zoom(GtkCheckMenuItem *menuitem, gpointer unused)
{
    GtkDisplayPanel *panel;                 /* Afficheur effectif de code  */
    double scale;                           /* Echelle à appliquer         */
    int zoom_kind;                          /* Type de zoom à appliquer    */

    panel = GTK_DISPLAY_PANEL(get_current_view());

    scale = gtk_display_panel_get_scale(panel);

    zoom_kind = GPOINTER_TO_INT(g_object_get_data(G_OBJECT(menuitem), "kind_of_zoom"));

    switch (zoom_kind)
    {
        case 0:
            scale /= 1.25;
            break;

        case 1:
            scale *= 1.25;
            break;

        case 2:
            scale = 1.0;
            break;

        default:
            assert(false);
            scale = 1.0;
            break;

    }

    gtk_display_panel_set_scale(panel, scale);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu ayant basculé.                    *
*                unused   = adresse non utilisée ici.                         *
*                                                                             *
*  Description : Réagit avec le menu "Affichage -> (colonne xxx)".            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_view_display_column(GtkCheckMenuItem *menuitem, gpointer unused)
{
    unsigned int option;                    /* Paramètre à traiter         */
    gboolean active;                        /* Etat de sélection du menu   */
    GLoadedPanel *panel;                    /* Afficheur effectif de code  */
    GLoadedContent *content;                /* Contenu représenté          */
    unsigned int index;                     /* Indice de la vue courante   */
    GDisplayOptions *options;               /* Ensemble à mettre à jour    */

    option = GPOINTER_TO_UINT(g_object_get_data(G_OBJECT(menuitem), "kind_of_opt"));

    active = gtk_check_menu_item_get_active(menuitem);

    panel = get_current_view();
    content = g_loaded_panel_get_content(panel);

    index = g_loaded_content_get_view_index(content, GTK_WIDGET(panel));

    options = g_loaded_content_get_display_options(content, index);

    g_display_options_set(options, option, active);

    g_object_unref(G_OBJECT(options));

    g_object_unref(G_OBJECT(content));
    g_object_unref(G_OBJECT(panel));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                unused   = adresse non utilisée ici.                         *
*                                                                             *
*  Description : Réagit avec le menu "Affichage -> Plein écran".              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_view_show_full_screen(GtkCheckMenuItem *menuitem, gpointer unused)
{
    GtkWindow *editor;                      /* Fenêtre graphique principale*/
    gboolean active;                        /* Etat de sélection du menu   */

    editor = get_editor_window();

    active = gtk_check_menu_item_get_active(menuitem);

    if (active)
        gtk_window_fullscreen(editor);
    else
        gtk_window_unfullscreen(editor);

    g_object_unref(G_OBJECT(editor));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : builder = constructeur avec l'ensemble des références.       *
*                new     = nouveau contenu chargé à analyser.                 *
*                                                                             *
*  Description : Réagit à un changement d'affichage principal de contenu.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void rebuild_menu_view_for_content(GtkBuilder *builder, GLoadedContent *new)
{
    GObject *menuitem;                      /* Menu d'affichage            */
    GtkWidget *menu;                        /* Support pour éléments       */
    unsigned int i;                         /* Boucle de parcours          */
    char *key;                              /* Clef pour accès ultérieurs  */
    GtkWidget *submenuitem;                 /* Sous-élément de menu        */
    void *marker;                           /* Menu de référence           */
    GList *list;                            /* Liste des éléments en place */
    gint position;                          /* Point d'insertion           */
    GList *iter;                            /* Boucle de parcours          */
    unsigned int count;                     /* Nombre d'itérations à mener */
    GSList *rgroup;                         /* Groupe des boutons radio    */
    char *caption;                          /* Etiquette pour un menu      */

    /* Retrait d'éventuels anciens menus */

    menuitem = gtk_builder_get_object(builder, "view");

    menu = gtk_menu_item_get_submenu(GTK_MENU_ITEM(menuitem));

    for (i = 0; ; i++)
    {
        asprintf(&key, "view_panel_%u", i);

        submenuitem = g_object_get_data(menuitem, key);

        free(key);

        if (submenuitem == NULL)
            break;
        else
            gtk_container_remove(GTK_CONTAINER(menu), GTK_WIDGET(submenuitem));

    }

    if (new != NULL)
    {
        /* Insertion des différentes vues */

        marker = gtk_builder_get_object(builder, "view_sep_0");

        list = gtk_container_get_children(GTK_CONTAINER(menu));

        position = 0;

        for (iter = list; iter != NULL; iter = g_list_next(iter))
        {
            position++;

            if (marker == iter->data)
                break;

        }

        g_list_free(list);

        count = g_loaded_content_count_views(new);

        rgroup = NULL;

        for (i = 0; i < count; i++)
        {
            asprintf(&key, "view_panel_%u", i);
            caption = g_loaded_content_get_view_name(new, i);

            submenuitem = qck_create_radio_menu_item(menuitem, key, rgroup, caption,
                                                     G_CALLBACK(mcb_view_change_support), NULL);
            g_object_set_data(G_OBJECT(submenuitem), "kind_of_view", GUINT_TO_POINTER(i));

            free(caption);
            free(key);

            asprintf(&key, "F%u", 3 + i);

            add_accelerator_to_widget(builder, submenuitem, key);

            free(key);

            if (rgroup == NULL)
                rgroup = gtk_radio_menu_item_get_group(GTK_RADIO_MENU_ITEM(submenuitem));

            gtk_menu_shell_insert(GTK_MENU_SHELL(menu), submenuitem, position + i);

        }

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : builder = constructeur avec l'ensemble des références.       *
*                new     = nouvelle vue du contenu chargé analysé.            *
*                                                                             *
*  Description : Lance une actualisation du fait d'un changement de support.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void rebuild_menu_view_for_view(GtkBuilder *builder, GLoadedPanel *new)
{
    GObject *menuitem;                      /* Menu d'affichage            */
    GLoadedContent *content;                /* Contenu en cours d'analyse  */
    unsigned int index;                     /* Indice de la vue            */
    GtkWidget *menu;                        /* Support pour éléments       */
    void *marker;                           /* Menu de référence           */
    size_t i;                               /* Boucle de parcours          */
    char *key;                              /* Clef pour accès ultérieurs  */
    GtkWidget *submenuitem;                 /* Sous-élément de menu        */
    GtkRadioMenuItem *item;                 /* Elément de menu arbitraire  */
    GSList *radios;                         /* Liste des menus d'affichage */
    GList *list;                            /* Liste des éléments en place */
    gint position;                          /* Point d'insertion           */
    GList *iter;                            /* Boucle de parcours          */
    GDisplayOptions *options;               /* Paramètres de rendus        */
    size_t count;                           /* Nombre d'itérations à mener */
    bool status;                            /* Consigne d'affichage        */

    menuitem = gtk_builder_get_object(builder, "view");

    content = get_current_content();
    assert((content == NULL && new == NULL) || (content != NULL && new != NULL));

    /* Retrait d'éventuels anciens menus */

    menu = gtk_menu_item_get_submenu(GTK_MENU_ITEM(menuitem));

    marker = gtk_builder_get_object(builder, "view_sep_2");

    for (i = 0; ; i++)
    {
        asprintf(&key, "view_display_option_%zu", i);

        submenuitem = g_object_get_data(menuitem, key);

        free(key);

        if (submenuitem == NULL)
            break;
        else
            gtk_container_remove(GTK_CONTAINER(menu), GTK_WIDGET(submenuitem));

    }

    if (content != NULL)
    {
        index = g_loaded_content_get_view_index(content, GTK_WIDGET(new));

        /* Mise à jour du choix de la vue */

        item = GTK_RADIO_MENU_ITEM(g_object_get_data(menuitem, "view_panel_0"));

        radios = gtk_radio_menu_item_get_group(item);

        void disconnect_display_radio(GtkWidget *wgt, gpointer unused)
        {
            g_signal_handlers_disconnect_by_func(wgt, G_CALLBACK(mcb_view_change_support), NULL);
        }

        g_slist_foreach(radios, (GFunc)disconnect_display_radio, NULL);

        asprintf(&key, "view_panel_%u", index);

        item = GTK_RADIO_MENU_ITEM(g_object_get_data(menuitem, key));
        gtk_check_menu_item_set_active(GTK_CHECK_MENU_ITEM(item), TRUE);

        free(key);

        void reconnect_display_radio(GtkWidget *wgt, gpointer unused)
        {
            g_signal_connect(wgt, "toggled", G_CALLBACK(mcb_view_change_support), NULL);
        }

        g_slist_foreach(radios, (GFunc)reconnect_display_radio, NULL);

        /* Insertion des options de rendu */

        list = gtk_container_get_children(GTK_CONTAINER(menu));

        position = 0;

        for (iter = list; iter != NULL; iter = g_list_next(iter))
        {
            position++;

            if (marker == iter->data)
                break;

        }

        g_list_free(list);

        options = g_loaded_content_get_display_options(content, index);

        count = g_display_options_count(options);

        for (i = 0; i < count; i++)
        {
            asprintf(&key, "view_display_option_%zu", i);

            submenuitem = qck_create_check_menu_item(menuitem, key,
                                                     g_display_options_get_name(options, i),
                                                     G_CALLBACK(mcb_view_display_column), NULL);
            g_object_set_data(G_OBJECT(submenuitem), "kind_of_opt", GUINT_TO_POINTER(i));

            gtk_menu_shell_insert(GTK_MENU_SHELL(menu), submenuitem, position + i);

            free(key);

            /**
             * Un signal va être émis pour le menu, mais il n'ira pas très loin :
             * l'ensemble des options ne notifie un changement que si changement il y a !
             */

            status = g_display_options_get(options, i);
            gtk_check_menu_item_set_active(GTK_CHECK_MENU_ITEM(submenuitem), status);

        }

        g_object_unref(G_OBJECT(options));

        g_object_unref(G_OBJECT(content));

    }

    else
        count = 0;

    /* Utilité de la séparation ? */

    gtk_widget_set_visible(GTK_WIDGET(marker), count > 0);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : builder = constructeur avec l'ensemble des références.       *
*                new     = nouvelle vue du contenu chargé analysé.            *
*                                                                             *
*  Description : Met à jour les accès du menu "Affichage" selon le contenu.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void update_access_for_view_in_menu_view(GtkBuilder *builder, GLoadedPanel *new)
{
    gboolean access;                        /* Accès à déterminer          */
    GtkWidget *item;                        /* Elément de menu à traiter   */

    /* Bascules */

    update_switch_access_in_menu_view(builder);

    /* Zooms */

    access = GTK_IS_GRAPH_DISPLAY(new);

    item = GTK_WIDGET(gtk_builder_get_object(builder, "view_zoom_in"));
    gtk_widget_set_sensitive(item, access);

    item = GTK_WIDGET(gtk_builder_get_object(builder, "view_zoom_out"));
    gtk_widget_set_sensitive(item, access);

    item = GTK_WIDGET(gtk_builder_get_object(builder, "view_zoom_reset"));
    gtk_widget_set_sensitive(item, access);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : builder = constructeur avec l'ensemble des références.       *
*                                                                             *
*  Description : Met à jour les accès du menu "Affichage -> Basculer...".     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void update_switch_access_in_menu_view(GtkBuilder *builder)
{
    GLoadedPanel *panel;                    /* Afficheur effectif de code  */
    GLoadedContent *content;                /* Contenu représenté          */
    unsigned int count;                     /* Nombre de vues possibles    */
    unsigned int index;                     /* Indice de la vue courante   */
    gboolean access;                        /* Accès à déterminer          */
    GtkWidget *item;                        /* Elément de menu à traiter   */

    panel = get_current_view();

    if (panel == NULL)
        content = NULL;

    else
    {
        content = g_loaded_panel_get_content(panel);

        count = g_loaded_content_count_views(content);
        index = g_loaded_content_get_view_index(content, GTK_WIDGET(panel));

    }

    access = (panel != NULL && (index + 1) < count);

    item = GTK_WIDGET(gtk_builder_get_object(builder, "view_switch_to_next"));
    gtk_widget_set_sensitive(item, access);

    access = (panel != NULL && index > 0);

    item = GTK_WIDGET(gtk_builder_get_object(builder, "view_switch_to_prev"));
    gtk_widget_set_sensitive(item, access);

    if (panel != NULL)
    {
        g_object_unref(G_OBJECT(content));
        g_object_unref(G_OBJECT(panel));
    }

}
