
/* Chrysalide - Outil d'analyse de fichiers binaires
 * preferences.c - (re)définition de l'identité de l'utilisateur
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


#include "preferences.h"


#include <i18n.h>


#include "prefs_fgraph.h"
#include "prefs_labels.h"
#include "../../core/params.h"
#include "../../gtkext/easygtk.h"



/* Constructeur de panneau de paramétrage */
typedef GtkWidget * (* prefs_panel_creation_cb) (GtkBuilder **);

/* Chargement de la configuration */
typedef void (* prefs_config_update_cb) (GtkBuilder *, GGenConfig *);

/* Description d'un noeud de préférences */
typedef struct _pref_node_desc_t
{
    prefs_panel_creation_cb create;         /* Procédure de création       */
    prefs_config_update_cb load;            /* Procédure de chargement     */
    prefs_config_update_cb store;           /* Procédure d'enregistrement  */

    const char *name;                       /* Désignation interne         */
    const char *title;                      /* Désignation humaine         */

    GtkBuilder *builder;                    /* Constructeur GTK            */
    GtkWidget *panel;                       /* Panneau GTK                 */

    struct _pref_node_desc_t *children;     /* Sous-arborescence           */

} pref_node_desc_t;


#define PREF_NODE_NULL_ENTRY { .title = NULL }


/* Liste des paramétrages à afficher */
static pref_node_desc_t _prefs_nodes[] = {

    {
        .create = NULL,

        .title = "Analysis",

        .children = (pref_node_desc_t []){

            {
                .create = create_labels_preferences,
                .load = load_labels_configuration,
                .store = store_labels_configuration,

                .name = "labels",
                .title = "Colored labels",

            },

            PREF_NODE_NULL_ENTRY

        }

    },

    {
        .create = NULL,

        .title = "Editor",

        .children = (pref_node_desc_t []){

            {
                .create = create_fgraph_preferences,
                .load = load_fgraph_configuration,
                .store = store_fgraph_configuration,

                .name = "fgraph",
                .title = "Function graph",

            },

            PREF_NODE_NULL_ENTRY

        }

    },

    PREF_NODE_NULL_ENTRY

};


/* Eléments de la liste de sections */
typedef enum _PrefListItem
{
    PLI_TITLE,                              /* Etiquette de la section     */
    PLI_PANEL,                              /* Panneau graphique associé   */

} PrefListItem;


/* Ajoute un panneau de paramétrage à la boîte de dialogue. */
static void add_preferences_node(GtkTreeStore *, GtkTreeIter *, GGenConfig *, GtkStack *, pref_node_desc_t *);

/* Affiche le panneau correspondant au noeud sélectionné. */
static void on_prefs_selection_changed(GtkTreeSelection *, GtkBuilder *);

/* Lance la sauvegarde d'éléments de paramétrage. */
static void store_preferences_node(GGenConfig *, pref_node_desc_t *);

/* Sauvegarde l'ensemble des paramètres de configuration. */
static void on_prefs_apply_button_clicked(GtkButton *, GtkBuilder *);



/******************************************************************************
*                                                                             *
*  Paramètres  : store  = arborescence des sections à compléter.              *
*                parent = point d'insertion du parent.                        *
*                config = configuration globale à charger.                    *
*                stack  = pile de composants GTK à constituer.                *
*                node   = noeud de description courant à traiter.             *
*                                                                             *
*  Description : Ajoute un panneau de paramétrage à la boîte de dialogue.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void add_preferences_node(GtkTreeStore *store, GtkTreeIter *parent, GGenConfig *config, GtkStack *stack, pref_node_desc_t *node)
{
    GtkTreeIter iter;                       /* Point d'insertion           */
    pref_node_desc_t *child;                /* Sous-élément à traiter      */

    if (node->create == NULL)
    {
        node->builder = NULL;
        node->panel = NULL;
    }
    else
    {
        node->panel = node->create(&node->builder);

        node->load(node->builder, config);

        gtk_widget_show(node->panel);

        gtk_stack_add_named(stack, node->panel, node->name);

    }

    gtk_tree_store_append(store, &iter, parent);

    gtk_tree_store_set(store, &iter,
                       PLI_TITLE, _(node->title),
                       PLI_PANEL, node->panel,
                       -1);

    if (node->children != NULL)
        for (child = node->children; child->title != NULL; child++)
            add_preferences_node(store, &iter, config, stack, child);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : parent = fenêtre principale de l'éditeur.                    *
*                outb   = constructeur à détruire après usage. [OUT]          *
*                                                                             *
*  Description : Propose une boîte de dialogue pour la configuration générale.*
*                                                                             *
*  Retour      : Adresse de la fenêtre mise en place.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *create_preferences_dialog(GtkWindow *parent, GtkBuilder **outb)
{
    GtkWidget *result;                      /* Fenêtre à renvoyer          */
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GGenConfig *config;                     /* Configuration globale       */
    GtkStack *stack;                        /* Pile à mettre à jour        */
    GtkTreeStore *store;                    /* Arborescence des sections   */
    pref_node_desc_t *iter;                 /* Boucle de parcours          */
    GtkTreeView *treeview;                  /* Arborescence principale     */

    builder = gtk_builder_new_from_resource("/org/chrysalide/gui/dialogs/preferences.ui");
    *outb = builder;

    result = GTK_WIDGET(gtk_builder_get_object(builder, "window"));

    gtk_window_set_transient_for(GTK_WINDOW(result), parent);

    /* Intégration des différentes sections */

    config = get_main_configuration();

    stack = GTK_STACK(gtk_builder_get_object(builder, "stack"));

    store = GTK_TREE_STORE(gtk_builder_get_object(builder, "pref_list"));

    for (iter = _prefs_nodes; iter->title != NULL; iter++)
        add_preferences_node(store, NULL, config, stack, iter);

    treeview = GTK_TREE_VIEW(gtk_builder_get_object(builder, "treeview"));

    gtk_tree_view_expand_all(treeview);

    /* Connexion des signaux */

    gtk_builder_add_callback_symbols(builder,
                                     BUILDER_CALLBACK(on_prefs_selection_changed),
                                     BUILDER_CALLBACK(on_prefs_apply_button_clicked),
                                     NULL);

    gtk_builder_connect_signals(builder, builder);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : selection = sélection courante de l'arborescence des options.*
*                builder = constructeur GTK avec toutes les références.       *
*                                                                             *
*  Description : Affiche le panneau correspondant au noeud sélectionné.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_prefs_selection_changed(GtkTreeSelection *selection, GtkBuilder *builder)
{
    GtkTreeModel *model;                    /* Gestionnaire de données     */
    GtkTreeIter iter;                       /* Position courante           */
    GtkWidget *panel;                       /* Panneau à mettre en avant   */
    GtkStack *stack;                        /* Pile à mettre à jour        */

    if (gtk_tree_selection_get_selected(selection, &model, &iter))
    {
        gtk_tree_model_get(model, &iter, PLI_PANEL, &panel, -1);

        stack = GTK_STACK(gtk_builder_get_object(builder, "stack"));

        if (panel == NULL)
            gtk_stack_set_visible_child_name(stack, "empty");

        else
        {
            gtk_stack_set_visible_child(stack, panel);

            g_object_unref(G_OBJECT(panel));

        }

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : config = configuration globale à actualiser.                 *
*                node   = noeud de description courant à traiter.             *
*                                                                             *
*  Description : Lance la sauvegarde d'éléments de paramétrage.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void store_preferences_node(GGenConfig *config, pref_node_desc_t *node)
{
    pref_node_desc_t *child;                /* Sous-élément à traiter      */

    if (node->create != NULL)
        node->store(node->builder, config);

    if (node->children != NULL)
        for (child = node->children; child->title != NULL; child++)
            store_preferences_node(config, child);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : button  = bouton GTK à l'origine de l'opération.             *
*                builder = constructeur GTK avec toutes les références.       *
*                                                                             *
*  Description : Sauvegarde l'ensemble des paramètres de configuration.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_prefs_apply_button_clicked(GtkButton *button, GtkBuilder *builder)
{
    GGenConfig *config;                     /* Configuration globale       */
    pref_node_desc_t *iter;                 /* Boucle de parcours          */

    config = get_main_configuration();

    for (iter = _prefs_nodes; iter->title != NULL; iter++)
        store_preferences_node(config, iter);

}
