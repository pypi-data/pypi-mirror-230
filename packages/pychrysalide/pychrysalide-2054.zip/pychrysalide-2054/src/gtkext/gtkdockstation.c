
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gtkdockstation.c - manipulation et l'affichage de composants rassemblés
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
 *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.
 */


#include "gtkdockstation.h"


#include <malloc.h>
#include <string.h>


#include "easygtk.h"
#include "../core/params.h"
#include "../common/extstr.h"
#include "../glibext/chrysamarshal.h"



/* Procède à l'initialisation de l'afficheur concentré. */
static void gtk_dock_station_class_init(GtkDockStationClass *);

/* Procède à l'initialisation du support d'affichage concentré. */
static void gtk_dock_station_init(GtkDockStation *);

/* Met à jour le titre du support de panneaux concentrés. */
static gboolean gtk_dock_station_switch_panel(GtkNotebook *, gpointer *, guint, GtkDockStation *);




/* Révèle ou cache la zone de recherches. */
static void on_toggle_revealer(GtkToggleButton *, GtkDockStation *);

/* Demande l'apparition d'un menu pour inclure des composants. */
static void on_click_for_menu(GtkButton *, GtkDockStation *);

/* Demande la disparition du composant courant. */
static void on_click_for_close(GtkButton *, GtkDockStation *);






/* Détermine le type du composant d'affichage concentré. */
G_DEFINE_TYPE(GtkDockStation, gtk_dock_station, GTK_TYPE_NOTEBOOK)


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe GTK à initialiser.                            *
*                                                                             *
*  Description : Procède à l'initialisation de l'afficheur concentré.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_dock_station_class_init(GtkDockStationClass *class)
{
    g_signal_new("dock-widget",
                 GTK_TYPE_DOCK_STATION,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GtkDockStationClass, dock_widget),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__OBJECT,
                 G_TYPE_NONE, 1, GTK_TYPE_WIDGET);

    g_signal_new("undock-widget",
                 GTK_TYPE_DOCK_STATION,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GtkDockStationClass, undock_widget),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__OBJECT,
                 G_TYPE_NONE, 1, GTK_TYPE_WIDGET);

    g_signal_new("switch-widget",
                 GTK_TYPE_DOCK_STATION,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GtkDockStationClass, switch_widget),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__OBJECT,
                 G_TYPE_NONE, 1, GTK_TYPE_WIDGET);

    g_signal_new("menu-requested",
                 GTK_TYPE_DOCK_STATION,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GtkDockStationClass, menu_requested),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__OBJECT,
                 G_TYPE_NONE, 1, GTK_TYPE_WIDGET);

    g_signal_new("close-requested",
                 GTK_TYPE_DOCK_STATION,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GtkDockStationClass, close_requested),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__OBJECT,
                 G_TYPE_NONE, 1, GTK_TYPE_WIDGET);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : station = composant GTK à initialiser.                       *
*                                                                             *
*  Description : Procède à l'initialisation du support d'affichage concentré. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_dock_station_init(GtkDockStation *station)
{
    GtkNotebook *notebook;                  /* Autre version du composant  */
    GtkWidget *hbox;                        /* Division supérieure         */
    GtkWidget *button;                      /* Bouton de contrôle          */

    notebook = GTK_NOTEBOOK(station);

    gtk_notebook_set_show_border(notebook, FALSE);
    gtk_notebook_set_scrollable(notebook, TRUE);

    /* Définition de la zone de contrôle */

    hbox = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 0);
    gtk_widget_set_valign(hbox, GTK_ALIGN_CENTER);
    gtk_widget_set_margin_end(hbox, 8);
    gtk_widget_show(hbox);

    button = qck_create_toggle_button_with_named_img(G_OBJECT(station), "search",
                                                     "edit-find-symbolic", GTK_ICON_SIZE_MENU, NULL,
                                                     G_CALLBACK(on_toggle_revealer), station);
    gtk_button_set_relief(GTK_BUTTON(button), GTK_RELIEF_NONE);
    gtk_box_pack_start(GTK_BOX(hbox), button, FALSE, FALSE, 0);

    button = qck_create_button_with_named_img(G_OBJECT(station), "menu",
                                              "go-down-symbolic", GTK_ICON_SIZE_MENU, NULL,
                                              G_CALLBACK(on_click_for_menu), station);
    gtk_button_set_relief(GTK_BUTTON(button), GTK_RELIEF_NONE);
    gtk_box_pack_start(GTK_BOX(hbox), button, FALSE, FALSE, 0);

    button = qck_create_button_with_named_img(G_OBJECT(station), "close",
                                              "window-close-symbolic", GTK_ICON_SIZE_MENU, NULL,
                                              G_CALLBACK(on_click_for_close), station);
    gtk_button_set_relief(GTK_BUTTON(button), GTK_RELIEF_NONE);
    gtk_box_pack_start(GTK_BOX(hbox), button, FALSE, FALSE, 0);

    gtk_notebook_set_action_widget(notebook, hbox, GTK_PACK_END);

    g_signal_connect(notebook, "switch-page",
                     G_CALLBACK(gtk_dock_station_switch_panel), station);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un nouveau composant pour support d'affichage concentré.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *gtk_dock_station_new(void)
{
    return g_object_new(GTK_TYPE_DOCK_STATION, NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : notebook = support à l'origine de la mise à jour.            *
*                page     = onglet mis en avant.                              *
*                index    = indice de l'onglet actuellement actif.            *
*                station  = conteneur de gestion supérieur.                   *
*                                                                             *
*  Description : Met à jour le titre du support de panneaux concentrés.       *
*                                                                             *
*  Retour      : TRUE ?                                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean gtk_dock_station_switch_panel(GtkNotebook *notebook, gpointer *page, guint index, GtkDockStation *station)
{
    GtkWidget *widget;                      /* Panneau concerné            */
    GtkDockable *dockable;                  /* Elément encapsulé           */
    GtkWidget *button;                      /* Bouton de contrôle          */

    widget = gtk_notebook_get_nth_page(notebook, index);

    dockable = GTK_DOCKABLE(g_object_get_data(G_OBJECT(widget), "dockable"));

    /* Mise à jour des boutons utilisables */

    button = GTK_WIDGET(g_object_get_data(G_OBJECT(station), "search"));

    if (gtk_dockable_can_search(dockable))
        gtk_widget_show(button);
    else
        gtk_widget_hide(button);

    /* Remontée du changement d'onglet */

    g_signal_emit_by_name(station, "switch-widget", widget);

    return TRUE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : station  = plateforme GTK à compléter.                       *
*                dockable = nouvel élément à intégrer.                        *
*                                                                             *
*  Description : Ajoute un paquet d'informations à l'affichage centralisé.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/
#include "gtkdisplaypanel.h"
#include "../gui/panels/history.h"
void gtk_dock_station_add_dockable(GtkDockStation *station, GtkDockable *dockable)
{
    GtkWidget *widget;                      /* Composant GTK à intégrer    */
    char *name;                             /* Nom à donner à l'onglet     */
    char *desc;                             /* Description à y associer    */
    int max;                                /* Taille maximale des titres  */
    GtkWidget *label;                       /* Etiquette d'onglet          */
    GtkNotebook *notebook;                  /* Autre version du composant  */







    /* Récupération des éléments utiles */

    widget = gtk_dockable_build_widget(dockable);

    //widget = gtk_button_new_with_label("123");
    gtk_widget_show(widget);


    g_object_set_data(G_OBJECT(widget), "dockable", dockable);

    name = gtk_dockable_get_name(dockable);
    desc = gtk_dockable_get_desc(dockable);

    /* Mise en place de la page */

    if (!g_generic_config_get_value(get_main_configuration(), MPK_ELLIPSIS_TAB, &max))
        max = -1;

    name = ellipsis(name, max);
    label = qck_create_label(NULL, NULL, name);
    free(name);

    notebook = GTK_NOTEBOOK(station);

    if (gtk_notebook_get_n_pages(notebook) > 0)
    g_signal_handlers_disconnect_by_func(notebook,
                                         G_CALLBACK(gtk_dock_station_switch_panel), station);

    gtk_notebook_append_page(notebook, widget, label);

    gtk_widget_set_tooltip_text(label, desc);

    free(desc);

    if (gtk_notebook_get_n_pages(notebook) > 1)
    g_signal_connect(notebook, "switch-page",
                     G_CALLBACK(gtk_dock_station_switch_panel), station);

    /* Lancement des mises à jour */

    if (gtk_notebook_get_n_pages(notebook) > 1)
        gtk_notebook_set_current_page(notebook, -1);

    //g_signal_emit_by_name(station, "dock-widget", widget);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : station = plateforme GTK à compléter.                        *
*                widget  = nouvel élément à intégrer.                         *
*                                                                             *
*  Description : Change le contenu de l'onglet courant uniquement.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_dock_panel_change_active_widget(GtkDockStation *station, GtkWidget *widget)
{
    GtkNotebook *notebook;                  /* Autre version du composant  */
    gint index;                             /* Indice de l'onglet actif    */
    GtkWidget *old;                         /* Ancien composant            */
    GtkWidget *label;                       /* Etiquette d'onglet          */
    char *str;                              /* Titre des prochaines fois   */

    notebook = GTK_NOTEBOOK(station);

    index = gtk_notebook_get_current_page(notebook);

    g_signal_handlers_disconnect_by_func(notebook,
                                         G_CALLBACK(gtk_dock_station_switch_panel), station);

    old = gtk_notebook_get_nth_page(notebook, index);
    label = gtk_notebook_get_tab_label(notebook, old);

    g_object_ref(G_OBJECT(label));
    str = g_object_get_data(G_OBJECT(old), "title");

    gtk_notebook_remove_page(notebook, index);
    gtk_notebook_insert_page(notebook, widget, label, index);

    g_object_unref(G_OBJECT(label));
    g_object_set_data(G_OBJECT(widget), "title", str);

    gtk_notebook_set_current_page(notebook, index);

    g_signal_connect(notebook, "switch-page",
                     G_CALLBACK(gtk_dock_station_switch_panel), station);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : station = plateforme GTK à compléter.                        *
*                dockable = élément existant à retirer.                       *
*                                                                             *
*  Description : Retire un paquet d'informations de l'affichage centralisé.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_dock_station_remove_dockable(GtkDockStation *station, GtkDockable *dockable)
{
    GtkNotebook *notebook;                  /* Autre version du composant  */
    GtkWidget *widget;                      /* Composant GTK à retirer     */
    gint index;                             /* Indice de l'onglet visé     */

    notebook = GTK_NOTEBOOK(station);

    widget = gtk_dockable_decompose(dockable, NULL);

    index = gtk_notebook_page_num(notebook, widget);

    gtk_notebook_remove_page(notebook, index);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : button  = bouton à l'origine de la procédure.                *
*                station = station d'accueil pour différents composants.      *
*                                                                             *
*  Description : Révèle ou cache la zone de recherches.                       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_toggle_revealer(GtkToggleButton *button, GtkDockStation *station)
{
    GtkNotebook *notebook;                  /* Autre version du composant  */
    gint index;                             /* Indice de l'onglet courant  */
    GtkWidget *widget;                      /* Panneau concerné            */
    GtkDockable *dockable;                  /* Elément encapsulé           */

    notebook = GTK_NOTEBOOK(station);

    index = gtk_notebook_get_current_page(notebook);
    widget = gtk_notebook_get_nth_page(notebook, index);

    dockable = GTK_DOCKABLE(g_object_get_data(G_OBJECT(widget), "dockable"));

    gtk_dockable_toggle_revealer(dockable, widget, gtk_toggle_button_get_active(button));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : button  = bouton à l'origine de la procédure.                *
*                station = station d'accueil pour différents composants.      *
*                                                                             *
*  Description : Demande l'apparition d'un menu pour inclure des composants.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_click_for_menu(GtkButton *button, GtkDockStation *station)
{
    g_signal_emit_by_name(station, "menu-requested", button);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : button  = bouton à l'origine de la procédure.                *
*                station = station d'accueil pour différents composants.      *
*                                                                             *
*  Description : Demande la disparition du composant courant.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_click_for_close(GtkButton *button, GtkDockStation *station)
{
    g_signal_emit_by_name(station, "close-requested", button);

}
