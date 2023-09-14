
/* Chrysalide - Outil d'analyse de fichiers binaires
 * history.c - panneau de la liste des évolutions d'utilisateur(s)
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
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#include "history.h"


#include <string.h>
#include <cairo-gobject.h>


#include <i18n.h>


#include "../panel-int.h"
#include "../../analysis/binary.h"
#include "../../glibext/chrysamarshal.h"
#include "../../glibext/signal.h"
#include "../../gtkext/easygtk.h"
#include "../../gtkext/named.h"



/* Panneau de la liste des évolutions utilisateur(s) (instance) */
struct _GHistoryPanel
{
    GPanelItem parent;                      /* A laisser en premier        */

    GLoadedBinary *binary;                  /* Binaire à prendre en compte */

};

/* Panneau de la liste des évolutions utilisateur(s) (classe) */
struct _GHistoryPanelClass
{
    GPanelItemClass parent;                 /* A laisser en premier        */

};


/* Colonnes de la liste des évolutions */
typedef enum _HistoryColumn
{
    HTC_ITEM,                               /* Elément d'évolution         */

    HTC_PICTURE,                            /* Image de représentation     */
    HTC_FOREGROUND,                         /* Couleur d'impression        */
    HTC_LABEL,                              /* Désignation humaine         */

    HTC_COUNT                               /* Nombre de colonnes          */

} HistoryColumn;


/* Initialise la classe des panneaux de la liste des évolutions utilisateur(s). */
static void g_history_panel_class_init(GHistoryPanelClass *);

/* Initialise une instance de panneau d'aperçu de graphiques. */
static void g_history_panel_init(GHistoryPanel *);

/* Supprime toutes les références externes. */
static void g_history_panel_dispose(GHistoryPanel *);

/* Procède à la libération totale de la mémoire. */
static void g_history_panel_finalize(GHistoryPanel *);

/* Fournit le nom interne attribué à l'élément réactif. */
static char *g_history_panel_class_get_key(const GHistoryPanelClass *);

/* Indique le chemin initial de la localisation d'un panneau. */
static char *g_history_panel_class_get_path(const GHistoryPanelClass *);

/* Réagit à un changement d'affichage principal de contenu. */
static void change_history_panel_current_content(GHistoryPanel *, GLoadedContent *, GLoadedContent *);

/* Réagit à une modification au sein d'une collection donnée. */
static void on_history_changed(GDbCollection *, DBAction, GDbItem *, GHistoryPanel *);

/* Compare deux lignes entre elles pour le tri des évolutions. */
static gint sort_history_lines(GtkTreeModel *, GtkTreeIter *, GtkTreeIter *, gpointer);

/* Réagit au changement de sélection des éléments d'historique. */
static void on_history_selection_change(GtkTreeSelection *, GHistoryPanel *);

/* Annule l'élément d'évolution courant. */
static void do_history_undo(GtkButton *, GHistoryPanel *);

/* Restaure l'élément d'évolution suivant. */
static void do_history_redo(GtkButton *, GHistoryPanel *);

/* Effectue un nettoyage de l'historique. */
static void do_history_clean(GtkButton *, GHistoryPanel *);



/* Indique le type défini pour un panneau d'aperçu de graphiques. */
G_DEFINE_TYPE(GHistoryPanel, g_history_panel, G_TYPE_PANEL_ITEM);


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des panneaux d'aperçu de graphiques.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_history_panel_class_init(GHistoryPanelClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GEditorItemClass *item;                 /* Encore une autre vision...  */
    GPanelItemClass *panel;                 /* Version parente de la classe*/

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_history_panel_dispose;
    object->finalize = (GObjectFinalizeFunc)g_history_panel_finalize;

    item = G_EDITOR_ITEM_CLASS(class);

    item->get_key = (get_item_key_fc)g_history_panel_class_get_key;

    item->change_content = (change_item_content_fc)change_history_panel_current_content;

    panel = G_PANEL_ITEM_CLASS(class);

    panel->get_path = (get_panel_path_fc)g_history_panel_class_get_path;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance de panneau d'aperçu de graphiques.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_history_panel_init(GHistoryPanel *panel)
{
    GPanelItem *pitem;                      /* Version parente du panneau  */
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkListStore *store;                    /* Modèle de gestion           */

    /* Eléments de base */

    pitem = G_PANEL_ITEM(panel);

    pitem->widget = G_NAMED_WIDGET(gtk_built_named_widget_new_for_panel(_("History"),
                                                                        _("Change history"),
                                                                        PANEL_HISTORY_ID));

    /* Représentation graphique */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(pitem->widget));

    store = GTK_LIST_STORE(gtk_builder_get_object(builder, "store"));

    gtk_tree_sortable_set_default_sort_func(GTK_TREE_SORTABLE(store), sort_history_lines, NULL, NULL);

    /* Connexion des signaux */

    gtk_builder_add_callback_symbols(builder,
                                     BUILDER_CALLBACK(on_history_selection_change),
                                     BUILDER_CALLBACK(do_history_undo),
                                     BUILDER_CALLBACK(do_history_redo),
                                     BUILDER_CALLBACK(do_history_clean),
                                     NULL);

    gtk_builder_connect_signals(builder, panel);

    g_object_unref(G_OBJECT(builder));

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

static void g_history_panel_dispose(GHistoryPanel *panel)
{
    g_clear_object(&panel->binary);

    G_OBJECT_CLASS(g_history_panel_parent_class)->dispose(G_OBJECT(panel));

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

static void g_history_panel_finalize(GHistoryPanel *panel)
{
    G_OBJECT_CLASS(g_history_panel_parent_class)->finalize(G_OBJECT(panel));

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

static char *g_history_panel_class_get_key(const GHistoryPanelClass *class)
{
    char *result;                           /* Description à renvoyer      */

    result = strdup(PANEL_HISTORY_ID);

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

static char *g_history_panel_class_get_path(const GHistoryPanelClass *class)
{
    char *result;                           /* Emplacement à retourner     */

    result = strdup("MEN");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un panneau d'affichage des symboles.                    *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GPanelItem *g_history_panel_new(void)
{
    GPanelItem *result;                     /* Structure à retourner       */

    result = g_object_new(G_TYPE_HISTORY_PANEL, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau à mettre à jour.                             *
*                old   = ancien contenu chargé analysé.                       *
*                new   = nouveau contenu chargé à analyser.                   *
*                                                                             *
*  Description : Réagit à un changement d'affichage principal de contenu.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void change_history_panel_current_content(GHistoryPanel *panel, GLoadedContent *old, GLoadedContent *new)
{
    GLoadedBinary *binary;                  /* Autre version de l'instance */
    GDbCollection **collections;            /* Ensemble de collections     */
    size_t count;                           /* Taille de cet ensemble      */
    size_t k;                               /* Boucle de parcours #1       */
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkListStore *store;                    /* Modèle de gestion           */
    GList *items;                           /* Liste des éléments groupés  */
    GList *i;                               /* Boucle de parcours #2       */
    GDbItem *item;                          /* Elément à intégrer          */
    char *label;                            /* Etiquette de représentation */
    GtkTreeIter iter;                       /* Point d'insertion           */

    if (G_IS_LOADED_BINARY(new))
        binary = G_LOADED_BINARY(new);
    else
        binary = NULL;

    /* Basculement du binaire utilisé */

    if (panel->binary != NULL)
    {
        collections = g_loaded_binary_get_collections(panel->binary, &count);

        for (k = 0; k < count; k++)
        {
            g_signal_handlers_disconnect_by_func(collections[k], G_CALLBACK(on_history_changed), panel);
            g_object_unref(G_OBJECT(collections[k]));
        }

        if (collections != NULL)
            free(collections);

        g_object_unref(G_OBJECT(panel->binary));

    }

    panel->binary = binary;

    if (panel->binary != NULL)
        g_object_ref(G_OBJECT(binary));

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    store = GTK_LIST_STORE(gtk_builder_get_object(builder, "store"));

    gtk_list_store_clear(store);

    g_object_unref(G_OBJECT(builder));

    /* Si le panneau actif ne représente pas un binaire... */

    if (binary == NULL) return;

    /* Actualisation de l'affichage */

    collections = g_loaded_binary_get_collections(binary, &count);

    for (k = 0; k < count; k++)
    {
        g_db_collection_rlock(collections[k]);

        /*
        items = g_db_collection_get_items(collections[k]);

        for (i = g_list_first(items); i != NULL; i = g_list_next(i))
        {
            item = G_DB_ITEM(i->data);

            label = g_db_item_get_label(item);

            gtk_list_store_append(store, &iter);
            gtk_list_store_set(store, &iter,
                               HTC_ITEM, item,
                               //HTC_PICTURE, G_BOOKMARKS_PANEL_GET_CLASS(panel)->bookmark_img,
                               HTC_FOREGROUND, g_db_item_is_enabled(item) ? NULL : "grey",
                               HTC_LABEL, label,
                               -1);

            free(label);

        }
        */

        //g_signal_connect_to_main(collections[k], "content-changed", G_CALLBACK(on_history_changed), panel,
        //                         g_cclosure_user_marshal_VOID__ENUM_OBJECT);

        g_db_collection_runlock(collections[k]);

        g_object_unref(G_OBJECT(collections[k]));

    }

    if (collections != NULL)
        free(collections);

    /* Force une sélection initiale */
    on_history_changed(NULL, DBA_COUNT, NULL, panel);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = collection dont le contenu a évolué.                *
*                action = type d'évolution rencontrée.                        *
*                item   = élément ajouté, modifié ou supprimé.                *
*                panel  = panneau d'historique concerné par la procédure.     *
*                                                                             *
*  Description : Réagit à une modification au sein d'une collection donnée.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_history_changed(GDbCollection *collec, DBAction action, GDbItem *item, GHistoryPanel *panel)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeView *treeview;                  /* Arborescence manipulée      */
    GtkListStore *store;                    /* Modèle de gestion courant   */
    GtkTreeModel *model;                    /* Modèle de gestion générique */
    GtkTreeSelection *selection;            /* Nouvelle sélection à établir*/
    char *label;                            /* Etiquette de représentation */
    GtkTreeIter iter;                       /* Boucle de parcours          */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    treeview = GTK_TREE_VIEW(gtk_builder_get_object(builder, "treeview"));

    store = GTK_LIST_STORE(gtk_builder_get_object(builder, "store"));
    model = GTK_TREE_MODEL(store);

    selection = gtk_tree_view_get_selection(treeview);

    /* Mise à jour de la liste affichée */

    bool find_changed_item(GtkTreeModel *_model, GDbItem *target, GtkTreeIter *_found)
    {
        bool status;
        GtkTreeIter candidate;
        GDbItem *displayed;

        status = false;

        if (gtk_tree_model_get_iter_first(_model, &candidate))
            do
            {
                gtk_tree_model_get(_model, &candidate, HTC_ITEM, &displayed, -1);

                if (target == displayed)
                {
                    *_found = candidate;
                    status = true;
                }

                g_object_unref(G_OBJECT(displayed));

            }
            while (!status && gtk_tree_model_iter_next(_model, &candidate));

        return status;

    }

    switch (action)
    {
        case DBA_ADD_ITEM:

            label = g_db_item_get_label(item);

            gtk_list_store_append(store, &iter);
            gtk_list_store_set(store, &iter,
                               HTC_ITEM, item,
                               //HTC_PICTURE, G_BOOKMARKS_PANEL_GET_CLASS(panel)->bookmark_img,
                               HTC_FOREGROUND, g_db_item_has_flag(item, DIF_DISABLED) ? "grey" : NULL,
                               HTC_LABEL, label,
                               -1);

            free(label);

            break;

        case DBA_REM_ITEM:

            if (find_changed_item(model, item, &iter))
                gtk_list_store_remove(store, &iter);

            break;

        case DBA_CHANGE_STATE:

            if (find_changed_item(model, item, &iter))
                gtk_list_store_set(store, &iter,
                                   HTC_FOREGROUND, g_db_item_has_flag(item, DIF_DISABLED) ? "grey" : NULL,
                                   -1);
            break;

        case DBA_COUNT:
            /* Actualisation artificielle de la sélection */
            break;

    }

    /* Redéfinition de la sélection */

    if (gtk_tree_model_get_iter_first(model, &iter))
    {
        gboolean find_last_active(GtkTreeModel *_model, GtkTreePath *_path, GtkTreeIter *_iter, GtkTreeIter *last)
        {
            GDbItem *item;
            gboolean active;

            gtk_tree_model_get(_model, _iter, HTC_ITEM, &item, -1);

            active = !g_db_item_has_flag(item, DIF_DISABLED);

            g_object_unref(G_OBJECT(item));

            if (active)
                *last = *_iter;

            return !active;

        }

        gtk_tree_model_foreach(model, (GtkTreeModelForeachFunc)find_last_active, &iter);

        gtk_tree_selection_select_iter(selection, &iter);

    }

    /* Actualisation des accès */

    on_history_selection_change(selection, panel);

    g_object_unref(G_OBJECT(builder));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : model = gestionnaire de données pour la liste traitée.       *
*                a     = premier point de comparaison.                        *
*                b     = second point de comparaison.                         *
*                dummy = adresse non utilisée ici.                            *
*                                                                             *
*  Description : Compare deux lignes entre elles pour le tri des évolutions.  *
*                                                                             *
*  Retour      : -1, 0 ou 1 selon le résultat de la comparaison.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gint sort_history_lines(GtkTreeModel *model, GtkTreeIter *a, GtkTreeIter *b, gpointer dummy)
{
    gint result;                            /* Bilan à retourner           */
    GDbItem *item_a;                        /* Elément de collection A     */
    GDbItem *item_b;                        /* Elément de collection B     */

    gtk_tree_model_get(model, a, HTC_ITEM, &item_a, -1);
    gtk_tree_model_get(model, b, HTC_ITEM, &item_b, -1);

    result = g_db_item_cmp(item_a, item_b);

    g_object_unref(G_OBJECT(item_a));
    g_object_unref(G_OBJECT(item_b));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : selection = sélection modifiée.                              *
*                panel     = structure contenant les informations maîtresses. *
*                                                                             *
*  Description : Réagit au changement de sélection des éléments d'historique. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_history_selection_change(GtkTreeSelection *selection, GHistoryPanel *panel)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeIter iter;                       /* Point de sélection          */
    GtkTreeModel *model;                    /* Modèle de gestion           */
    GDbItem *item;                          /* Elément de collection       */
    GtkWidget *button;                      /* Bouton de barre de contrôle */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    if (gtk_tree_selection_get_selected(selection, &model, &iter))
    {
        gtk_tree_model_get(model, &iter, HTC_ITEM, &item, -1);

        button = GTK_WIDGET(gtk_builder_get_object(builder, "undo"));
        gtk_widget_set_sensitive(button, !g_db_item_has_flag(item, DIF_DISABLED));

        button = GTK_WIDGET(gtk_builder_get_object(builder, "redo"));
        gtk_widget_set_sensitive(button, g_db_item_has_flag(item, DIF_DISABLED));

        g_object_unref(G_OBJECT(item));

    }

    else
    {
        button = GTK_WIDGET(gtk_builder_get_object(builder, "undo"));
        gtk_widget_set_sensitive(button, FALSE);

        button = GTK_WIDGET(gtk_builder_get_object(builder, "redo"));
        gtk_widget_set_sensitive(button, FALSE);

    }

    g_object_unref(G_OBJECT(builder));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : button = bouton d'édition de l'historique d'évolution.       *
*                panel  = panneau d'affichage de l'historique.                *
*                                                                             *
*  Description : Annule l'élément d'évolution courant.                        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void do_history_undo(GtkButton *button, GHistoryPanel *panel)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeView *treeview;                  /* Arborescence manipulée      */
    GtkTreeSelection *selection;            /* Sélection courante          */
    GtkTreeModel *model;                    /* Modèle de gestion de données*/
    GtkTreeIter iter;                       /* Pointeur vers la ligne visée*/
    GDbItem *item;                          /* Elément de collection       */
    GAnalystClient *client;                 /* Connexion vers la base      */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    treeview = GTK_TREE_VIEW(gtk_builder_get_object(builder, "treeview"));

    selection = gtk_tree_view_get_selection(treeview);

    if (gtk_tree_selection_get_selected(selection, &model, &iter))
    {
        if (gtk_tree_model_iter_previous(model, &iter))
        {
            gtk_tree_model_get(model, &iter, HTC_ITEM, &item, -1);

            client = g_loaded_binary_get_client(panel->binary);
            g_analyst_client_set_last_active(client, g_db_item_get_timestamp(item));
            g_object_unref(G_OBJECT(client));

            g_object_unref(G_OBJECT(item));

        }

    }

    g_object_unref(G_OBJECT(builder));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : button = bouton d'édition de l'historique d'évolution.       *
*                panel  = panneau d'affichage de l'historique.                *
*                                                                             *
*  Description : Restaure l'élément d'évolution suivant.                      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void do_history_redo(GtkButton *button, GHistoryPanel *panel)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeView *treeview;                  /* Arborescence manipulée      */
    GtkTreeSelection *selection;            /* Sélection courante          */
    GtkTreeModel *model;                    /* Modèle de gestion de données*/
    GtkTreeIter iter;                       /* Pointeur vers la ligne visée*/
    GDbItem *item;                          /* Elément de collection       */
    GAnalystClient *client;                 /* Connexion vers la base      */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    treeview = GTK_TREE_VIEW(gtk_builder_get_object(builder, "treeview"));

    selection = gtk_tree_view_get_selection(treeview);

    if (gtk_tree_selection_get_selected(selection, &model, &iter))
    {
        gtk_tree_model_get(model, &iter, HTC_ITEM, &item, -1);

        client = g_loaded_binary_get_client(panel->binary);
        g_analyst_client_set_last_active(client, g_db_item_get_timestamp(item));
        g_object_unref(G_OBJECT(client));

        g_object_unref(G_OBJECT(item));

    }

    g_object_unref(G_OBJECT(builder));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : button = bouton d'édition de l'historique d'évolution.       *
*                panel  = panneau d'affichage de l'historique.                *
*                                                                             *
*  Description : Effectue un nettoyage de l'historique.                       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void do_history_clean(GtkButton *button, GHistoryPanel *panel)
{
    /* TODO */

}
