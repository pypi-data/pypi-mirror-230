
/* Chrysalide - Outil d'analyse de fichiers binaires
 * bintree.c - panneau d'accueil par défaut
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
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#include "bintree.h"


#include <assert.h>
#include <malloc.h>
#include <regex.h>


#include <i18n.h>


#include "updating-int.h"
#include "../agroup.h"
#include "../panel-int.h"
#include "../core/global.h"
#include "../../analysis/binary.h"
#include "../../core/queue.h"
#include "../../gtkext/easygtk.h"
#include "../../gtkext/gtkdisplaypanel.h"
#include "../../gtkext/named.h"
#include "../../gtkext/tmgt.h"



/* -------------------------- PARTIE PRINCIPALE DU PANNEAU -------------------------- */


/* Origine de la dernière ouverture/fermeture reproductible */
typedef enum _UserActionType
{
    UAT_COLLAPSE,                           /* Fermeture totale            */
    UAT_EXPAND,                             /* Ouverture totale            */
    UAT_DEPTH,                              /* Descente contrôlée          */

} UserActionType;

/* Panneau de présentation des portions (instance) */
struct _GBintreePanel
{
    GPanelItem parent;                      /* A laisser en premier        */

    GLoadedBinary *binary;                  /* Binaire représenté          */

    UserActionType last;                    /* Dernière action             */

    size_t count;                           /* Quantité de portions utiles */

};

/* Panneau de présentation des portions (classe) */
struct _GBintreePanelClass
{
    GPanelItemClass parent;                 /* A laisser en premier        */

};


/* Colonnes de la liste des messages */
typedef enum _BinaryTreeColumn
{
    BTC_PORTION,                            /* Elément interne représenté  */

    BTC_ICON,                               /* Image de représentation     */
    BTC_CAPTION,                            /* Désignation de l'élément    */
    BTC_START,                              /* Position de départ          */
    BTC_END,                                /* Position d'arrivée          */
    BTC_RIGHTS,                             /* Droits d'accès              */

    BTC_MATCHED,                            /* Correspondance établie ?    */
    BTC_MATCH_POINTS,                       /* Nombre de demandeurs        */

    BTC_COUNT                               /* Nombre de colonnes          */

} BinaryTreeColumn;


/* Données utiles à la mise à jour */
typedef struct _bintree_update_data bintree_update_data;


/* Initialise la classe des panneaux d'affichage des portions. */
static void g_bintree_panel_class_init(GBintreePanelClass *);

/* Initialise une instance de panneau d'affichage des portions. */
static void g_bintree_panel_init(GBintreePanel *);

/* Procède à l'initialisation de l'interface de mise à jour. */
static void g_bintree_panel_updatable_interface_init(GUpdatablePanelInterface *);

/* Supprime toutes les références externes. */
static void g_bintree_panel_dispose(GBintreePanel *);

/* Procède à la libération totale de la mémoire. */
static void g_bintree_panel_finalize(GBintreePanel *);

/* Fournit le nom interne attribué à l'élément réactif. */
static char *g_bintree_panel_class_get_key(const GBintreePanelClass *);

/* Indique le chemin initial de la localisation d'un panneau. */
static char *g_bintree_panel_class_get_path(const GBintreePanelClass *);

/* Modifie la profondeur affichée des portions présentes. */
static void on_depth_spin_value_changed(GtkSpinButton *, const GBintreePanel *);

/* Réagit au changement de sélection des portions. */
static void on_bintree_selection_changed(GtkTreeSelection *, gpointer);

/* Réagit à un changement d'affichage principal de contenu. */
static void change_bintree_panel_current_content(GBintreePanel *, GLoadedContent *, GLoadedContent *);



/* -------------------------- AFFICHAGE SOUS FORME D'ARBRE -------------------------- */


/* Parcourt un ensemble de portions. */
static bool populate_tree_with_portion(GBinPortion *, GBinPortion *, BinaryPortionVisit, bintree_update_data *);

/* Réagit à un changement d'affichage principal de contenu. */
static void reload_portions_for_new_tree_view(const GBintreePanel *, GtkStatusStack *, activity_id_t, bintree_update_data *);

/* Met en surbrillance les éléments recherchés dans les noms. */
static void update_bintree_column_in_tree_view(GtkTreeStore *, GtkTreeIter *, GBinPortion *, BinaryTreeColumn, const regmatch_t *);



/* ------------------------- FILTRAGE DES SYMBOLES PRESENTS ------------------------- */


/* Prend note du changement de filtre sur les portions. */
static void on_search_entry_changed(GtkSearchEntry *, GBintreePanel *);

/* Détermine si un noeud de l'arborescence doit être filtré. */
static bool update_bintree_node(const bintree_update_data *, GtkTreeStore *, GtkTreeIter *, GBinPortion *);

/* Exécute un nouveau filtrage des symboles affichés. */
static void do_filtering_on_portions(const GBintreePanel *, GtkStatusStack *, activity_id_t, bintree_update_data *);



/* ---------------------- MECANISMES DE MISE A JOUR DE PANNEAU ---------------------- */


/* Données utiles à la mise à jour */
struct _bintree_update_data
{
    size_t count;                           /* Qté d'inscriptions réalisées*/

    regex_t *filter;                        /* Filtre appliqué ou NULL     */

    char **expanded;                        /* Chemins des noeuds ouverts  */
    size_t ecount;                          /* Nombre de ces chemins       */
    size_t eallocated;                      /* Espace alloué effectivement */

    const GBintreePanel *panel;             /* Transfert de panneau        */
    GtkTreeIter *top;                       /* Transfert de racine         */
    GtkStatusStack *status;                 /* Transfert de statut         */
    activity_id_t id;                       /* Transfert d'activité        */

};


#define EXPAND_ALLOC_RANGE 10


/* Détermine si une valeur de portion doit être filtrée ou non. */
static bool is_bintree_column_matching(const bintree_update_data *, GBinPortion *, gint, regmatch_t *);

/* Prépare une opération de mise à jour de panneau. */
static bool g_bintree_panel_setup(const GBintreePanel *, unsigned int, size_t *, bintree_update_data **, char **);

/* Bascule l'affichage d'un panneau avant mise à jour. */
static void g_bintree_panel_introduce(const GBintreePanel *, unsigned int, bintree_update_data *);

/* Réalise une opération de mise à jour de panneau. */
static void g_bintree_panel_process(const GBintreePanel *, unsigned int, GtkStatusStack *, activity_id_t, bintree_update_data *);

/* Bascule l'affichage d'un panneau après mise à jour. */
static void g_bintree_panel_conclude(GBintreePanel *, unsigned int, bintree_update_data *);

/* Supprime les données dynamiques utilisées à la mise à jour. */
static void g_bintree_panel_clean_data(const GUpdatablePanel *, unsigned int, bintree_update_data *);



/* ---------------------------------------------------------------------------------- */
/*                            PARTIE PRINCIPALE DU PANNEAU                            */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un panneau d'affichage des portions. */
G_DEFINE_TYPE_WITH_CODE(GBintreePanel, g_bintree_panel, G_TYPE_PANEL_ITEM,
                        G_IMPLEMENT_INTERFACE(G_TYPE_UPDATABLE_PANEL, g_bintree_panel_updatable_interface_init));


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des panneaux d'affichage des portions.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_bintree_panel_class_init(GBintreePanelClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GEditorItemClass *item;                 /* Encore une autre vision...  */
    GPanelItemClass *panel;                 /* Version parente de la classe*/

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_bintree_panel_dispose;
    object->finalize = (GObjectFinalizeFunc)g_bintree_panel_finalize;

    item = G_EDITOR_ITEM_CLASS(class);

    item->get_key = (get_item_key_fc)g_bintree_panel_class_get_key;

    item->change_content = (change_item_content_fc)change_bintree_panel_current_content;

    panel = G_PANEL_ITEM_CLASS(class);

    panel->get_path = (get_panel_path_fc)g_bintree_panel_class_get_path;

    panel->gid = setup_tiny_global_work_group(1);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance de panneau d'affichage des portions. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_bintree_panel_init(GBintreePanel *panel)
{
    GPanelItem *pitem;                      /* Version parente du panneau  */
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeView *treeview;                  /* Affichage de la liste       */
    GtkCellRenderer *renderer;              /* Moteur de rendu de colonne  */
    GtkTreeViewColumn *column;              /* Colonne de la liste         */

    /* Eléments de base */

    pitem = G_PANEL_ITEM(panel);

    pitem->widget = G_NAMED_WIDGET(gtk_built_named_widget_new_for_panel(_("Binary tree"),
                                                                        _("Tree of the binary layout"),
                                                                        PANEL_BINTREE_ID));

    /* Compléments propres */

    panel->binary = NULL;

    panel->last = UAT_EXPAND;

    /* Représentation graphique */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(pitem->widget));

    /* Liste des portions binaires */

    treeview = GTK_TREE_VIEW(gtk_builder_get_object(builder, "treeview"));

    column = gtk_tree_view_column_new();
    gtk_tree_view_append_column(treeview, column);
    gtk_tree_view_set_expander_column(treeview, column);

    renderer = gtk_cell_renderer_pixbuf_new();
    gtk_tree_view_column_pack_start(column, renderer, FALSE);
    gtk_tree_view_column_add_attribute(column, renderer, "surface", BTC_ICON);

    renderer = gtk_cell_renderer_text_new();
    gtk_tree_view_column_pack_start(column, renderer, TRUE);
    gtk_tree_view_column_add_attribute(column, renderer, "markup", BTC_CAPTION);

    column = gtk_tree_view_column_new();
    gtk_tree_view_append_column(treeview, column);

    renderer = gtk_cell_renderer_text_new();
    g_object_set(G_OBJECT(renderer), "xalign", 1.0, NULL);
    gtk_tree_view_column_pack_start(column, renderer, TRUE);
    gtk_tree_view_column_add_attribute(column, renderer, "markup", BTC_START);

    column = gtk_tree_view_column_new();
    gtk_tree_view_append_column(treeview, column);

    renderer = gtk_cell_renderer_text_new();
    g_object_set(G_OBJECT(renderer), "xalign", 1.0, NULL);
    gtk_tree_view_column_pack_start(column, renderer, TRUE);
    gtk_tree_view_column_add_attribute(column, renderer, "markup", BTC_END);

    column = gtk_tree_view_column_new();
    gtk_tree_view_append_column(treeview, column);

    renderer = gtk_cell_renderer_text_new();
    gtk_tree_view_column_pack_start(column, renderer, TRUE);
    gtk_tree_view_column_add_attribute(column, renderer, "markup", BTC_RIGHTS);

    /* Connexion des signaux */

    gtk_builder_add_callback_symbols(builder,
                                     BUILDER_CALLBACK(gtk_tree_view_collapse_all),
                                     BUILDER_CALLBACK(gtk_tree_view_expand_all),
                                     BUILDER_CALLBACK(on_depth_spin_value_changed),
                                     BUILDER_CALLBACK(on_search_entry_changed),
                                     BUILDER_CALLBACK(on_bintree_selection_changed),
                                     NULL);

    gtk_builder_connect_signals(builder, panel);

    g_object_unref(G_OBJECT(builder));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de mise à jour.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_bintree_panel_updatable_interface_init(GUpdatablePanelInterface *iface)
{
    iface->setup = (setup_updatable_cb)g_bintree_panel_setup;
    iface->get_group = (get_updatable_group_cb)g_panel_item_get_group;
    iface->introduce = (introduce_updatable_cb)g_bintree_panel_introduce;
    iface->process = (process_updatable_cb)g_bintree_panel_process;
    iface->conclude = (conclude_updatable_cb)g_bintree_panel_conclude;
    iface->clean = (clean_updatable_data_cb)g_bintree_panel_clean_data;

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

static void g_bintree_panel_dispose(GBintreePanel *panel)
{
    if (panel->binary != NULL)
        g_object_unref(G_OBJECT(panel->binary));

    G_OBJECT_CLASS(g_bintree_panel_parent_class)->dispose(G_OBJECT(panel));

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

static void g_bintree_panel_finalize(GBintreePanel *panel)
{
    G_OBJECT_CLASS(g_bintree_panel_parent_class)->finalize(G_OBJECT(panel));

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

static char *g_bintree_panel_class_get_key(const GBintreePanelClass *class)
{
    char *result;                           /* Description à renvoyer      */

    result = strdup(PANEL_BINTREE_ID);

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

static char *g_bintree_panel_class_get_path(const GBintreePanelClass *class)
{
    char *result;                           /* Emplacement à retourner     */

    result = strdup("MEN");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un panneau présentant l'arborescence des portions.      *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GPanelItem *g_bintree_panel_new(void)
{
    GBintreePanel *result;                  /* Structure à retourner       */

    result = g_object_new(G_TYPE_BINTREE_PANEL, NULL);

    return G_PANEL_ITEM(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : button   = bouton de réglage de l'affichage.                 *
*                treeview = arborescence dont l'affichage est à moduler.      *
*                                                                             *
*  Description : Modifie la profondeur affichée des portions présentes.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_depth_spin_value_changed(GtkSpinButton *button, const GBintreePanel *panel)
{
    gint max_depth;                         /* Profondeur maximale         */
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeView *treeview;                  /* Arborescence constituée     */
    GtkTreeStore *store;                    /* Modèle de gestion           */

    max_depth = gtk_spin_button_get_value_as_int(button);

    gboolean apply_max_depth(GtkTreeModel *model, GtkTreePath *path, GtkTreeIter *iter, gpointer unused)
    {
        gint depth;                         /* Profondeur du point courant */

        depth = gtk_tree_store_iter_depth(GTK_TREE_STORE(model), iter);

        if (depth < max_depth)
            gtk_tree_view_expand_to_path(treeview, path);

        return FALSE;

    }

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    treeview = GTK_TREE_VIEW(gtk_builder_get_object(builder, "treeview"));

    gtk_tree_view_collapse_all(treeview);

    store = GTK_TREE_STORE(gtk_builder_get_object(builder, "store"));

    gtk_tree_model_foreach(GTK_TREE_MODEL(store), (GtkTreeModelForeachFunc)apply_max_depth, NULL);

    g_object_unref(G_OBJECT(builder));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : selection = sélection modifiée.                              *
*                unused    = adresse non utilisée ici.                        *
*                                                                             *
*  Description : Réagit au changement de sélection des portions.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_bintree_selection_changed(GtkTreeSelection *selection, gpointer unused)
{
    GtkTreeIter iter;                       /* Point de sélection          */
    GtkTreeModel *model;                    /* Modèle de gestion           */
    GBinPortion *portion;                   /* Portion à traiter           */
    const mrange_t *range;                  /* Couverture dudit symbole    */
    GLoadedPanel *panel;                    /* Afficheur effectif de code  */

    if (gtk_tree_selection_get_selected(selection, &model, &iter))
    {
        gtk_tree_model_get(model, &iter, BTC_PORTION, &portion, -1);

        if (portion != NULL)
        {
            range = g_binary_portion_get_range(portion);

            panel = get_current_view();

            if (GTK_IS_DISPLAY_PANEL(panel))
                gtk_display_panel_request_move(GTK_DISPLAY_PANEL(panel), get_mrange_addr(range));

            g_object_unref(G_OBJECT(panel));

            g_object_unref(G_OBJECT(portion));

        }

    }

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

static void change_bintree_panel_current_content(GBintreePanel *panel, GLoadedContent *old, GLoadedContent *new)
{
    GLoadedBinary *binary;                  /* Autre version de l'instance */
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeStore *store;                    /* Modèle de gestion           */

    if (G_IS_LOADED_BINARY(new))
        binary = G_LOADED_BINARY(new);
    else
        binary = NULL;

    /* Basculement du binaire utilisé */

    if (panel->binary != NULL)
        g_object_unref(G_OBJECT(panel->binary));

    panel->binary = binary;

    if (panel->binary != NULL)
        g_object_ref(G_OBJECT(panel->binary));

    /* Réinitialisation */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    store = GTK_TREE_STORE(gtk_builder_get_object(builder, "store"));

    gtk_tree_store_clear(store);

    g_object_unref(G_OBJECT(builder));

    /* Si le panneau actif représente un binaire, actualisation de l'affichage */

    if (binary != NULL)
        run_panel_update(G_UPDATABLE_PANEL(panel), PUI_0);

}



/* ---------------------------------------------------------------------------------- */
/*                            AFFICHAGE SOUS FORME D'ARBRE                            */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : panel  = portion de binaire à traiter.                       *
*                parent = portion parent de la portion visitée.               *
*                visit  = indication sur le sens de la visite.                *
*                panel  = lien vers toutes les autres informations utiles.    *
*                                                                             *
*  Description : Parcourt un ensemble de portions.                            *
*                                                                             *
*  Retour      : true pour continuer la visite.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool populate_tree_with_portion(GBinPortion *portion, GBinPortion *parent, BinaryPortionVisit visit, bintree_update_data *data)
{
    const GBintreePanel *panel;             /* Panneau à compléter         */
    cairo_surface_t *icon;                  /* Miniature de décoration     */
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeStore *store;                    /* Modèle de gestion           */
    GtkTreeIter iter;                       /* Point d'insertion           */
    GtkTreeIter *save;                      /* Sauvegarde d'une position   */

    if (parent == NULL)
        return true;

    panel = data->panel;

    /* Insertion de la portion courante */

    if (visit == BPV_ENTER || visit == BPV_SHOW)
    {
        icon = NULL;

        builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

        store = GTK_TREE_STORE(gtk_builder_get_object(builder, "store"));

        gtk_tree_store_append(store, &iter, data->top);

        gtk_tree_store_set(store, &iter,
                           BTC_PORTION, portion,
                           BTC_ICON, icon,
                           BTC_CAPTION, NULL,
                           BTC_START, NULL,
                           BTC_END, NULL,
                           BTC_RIGHTS, NULL,
                           BTC_MATCHED, false,
                           BTC_MATCH_POINTS, 0,
                           -1);

        if (icon != NULL)
            cairo_surface_destroy(icon);

        update_bintree_node(data, store, &iter, portion);

        g_object_unref(G_OBJECT(builder));

        gtk_status_stack_update_activity_value(data->status, data->id, 1);

    }

    /* Définition de la hiérarchie */

    if (visit == BPV_ENTER)
    {
        save = gtk_tree_iter_copy(data->top);

        g_object_set_data_full(G_OBJECT(portion), "_save", save, (GDestroyNotify)gtk_tree_iter_free);

        *data->top = iter;

    }

    else if (visit == BPV_EXIT)
    {
        save = g_object_get_data(G_OBJECT(portion), "_save");

        *data->top = *save;

        g_object_set_data(G_OBJECT(portion), "_save", NULL);

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel  = panneau à mettre à jour.                            *
*                status = barre de statut à tenir informée.                   *
*                id     = identifiant pour le suivi de la progression.        *
*                data   = données complémentaire à manipuler.                 *
*                                                                             *
*  Description : Réagit à un changement d'affichage principal de contenu.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void reload_portions_for_new_tree_view(const GBintreePanel *panel, GtkStatusStack *status, activity_id_t id, bintree_update_data *data)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeStore *store;                    /* Modèle de gestion           */
    GExeFormat *format;                     /* Format du binaire           */
    GBinPortion *portions;                  /* Couche première de portions */
    size_t count;                           /* Compteur de portions        */
    GtkTreeIter top;                        /* Racine de l'arborescence    */
    char *desc;                             /* Description de contenu      */
    gint max_depth;                         /* Profondeur maximale         */
    GtkSpinButton *depth_spin;              /* Bouton de variation         */
    GtkTreeView *treeview;                  /* Arborescence constituée     */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    store = GTK_TREE_STORE(gtk_builder_get_object(builder, "store"));

    /* Constitution de l'arborescence */

    format = g_loaded_binary_get_format(panel->binary);

    portions = g_exe_format_get_portions(format);

    count = g_binary_portion_count(portions);

    gtk_status_stack_extend_activity(status, id, count);

    gtk_tree_store_append(store, &top, NULL);

    desc = g_loaded_content_describe(G_LOADED_CONTENT(panel->binary), false);

    gtk_tree_store_set(store, &top,
                       BTC_ICON, NULL,
                       BTC_CAPTION, desc,
                       -1);

    free(desc);

    data->panel = panel;
    data->top = &top;
    data->status = status;
    data->id = id;

    g_binary_portion_visit(portions, (visit_portion_fc)populate_tree_with_portion, data);

    g_object_unref(G_OBJECT(portions));

    g_object_unref(G_OBJECT(format));

    /* Détermination de la profondeur maximale */

    gboolean compute_max_depth(GtkTreeModel *model, GtkTreePath *path, GtkTreeIter *iter, gint *max)
    {
        gint depth;                         /* Profondeur du point courant */

        depth = gtk_tree_store_iter_depth(GTK_TREE_STORE(model), iter);

        if (depth > *max)
            *max = depth;

        return FALSE;

    }

    max_depth = 0;

    gtk_tree_model_foreach(GTK_TREE_MODEL(store), (GtkTreeModelForeachFunc)compute_max_depth, &max_depth);

    depth_spin = GTK_SPIN_BUTTON(gtk_builder_get_object(builder, "depth_spin"));

    gtk_spin_button_set_range(depth_spin, 0, max_depth);

    /* Restauration au mieux de l'affichage */

    treeview = GTK_TREE_VIEW(gtk_builder_get_object(builder, "treeview"));

    switch (panel->last)
    {
        case UAT_COLLAPSE:
            gtk_tree_view_collapse_all(treeview);
            break;

        case UAT_EXPAND:
            gtk_tree_view_expand_all(treeview);
            break;

        case UAT_DEPTH:
            on_depth_spin_value_changed(depth_spin, panel);
            break;

    }

    g_object_unref(G_OBJECT(builder));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : store   = gestionnaire de l'ensemble des données.            *
*                iter    = localisation des données à analyser.               *
*                portion = portion de binaire concernée par l'analyse.        *
*                column  = colonne visée par l'analyse.                       *
*                match  = portion de texte à mettre en évidence.              *
*                                                                             *
*  Description : Met en surbrillance les éléments recherchés dans les noms.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void update_bintree_column_in_tree_view(GtkTreeStore *store, GtkTreeIter *iter, GBinPortion *portion, BinaryTreeColumn column, const regmatch_t *match)
{
    const char *content;                    /* Contenu brut d'origine      */
    const mrange_t *range;                  /* Espace de portion à traiter */
    VMPA_BUFFER(offset);                    /* Localisation quelconque     */
    vmpa2t end;                             /* Zone de construction temp.  */
    PortionAccessRights rights;             /* Droits d'accès à analyser   */
    char hrights[4];                        /* Version humainement lisible */
    char *value;                            /* Etiquette mise en relief    */

    switch (column)
    {
        case BTC_CAPTION:
            content = g_binary_portion_get_desc(portion);
            break;

        case BTC_START:
            range = g_binary_portion_get_range(portion);
            vmpa2_phys_to_string(get_mrange_addr(range), MDS_UNDEFINED, offset, NULL);
            content = offset;
            break;

        case BTC_END:
            range = g_binary_portion_get_range(portion);
            compute_mrange_end_addr(range, &end);
            vmpa2_phys_to_string(&end, MDS_UNDEFINED, offset, NULL);
            content = offset;
            break;

        case BTC_RIGHTS:
            rights = g_binary_portion_get_rights(portion);
            hrights[0] = (rights & PAC_READ ? 'r' : '-');
            hrights[1] = (rights & PAC_WRITE ? 'w' : '-');
            hrights[2] = (rights & PAC_EXEC ? 'x' : '-');
            hrights[3] = '\0';
            content = hrights;
            break;

        default:
            assert(false);
            content = NULL;
            break;

    }

    value = build_highlighted_name(content, match, 0);

    gtk_tree_store_set(store, iter, column, value, -1);

    free(value);

}



/* ---------------------------------------------------------------------------------- */
/*                           FILTRAGE DES SYMBOLES PRESENTS                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : entry = zone de texte avec un nouveau filtre d'affichage.    *
*                panel = panneau contenant les informations globales.         *
*                                                                             *
*  Description : Prend note du changement de filtre sur les portions.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_search_entry_changed(GtkSearchEntry *entry, GBintreePanel *panel)
{
    update_regex_on_search_entry_changed(entry, &G_PANEL_ITEM(panel)->filter);

    run_panel_update(G_UPDATABLE_PANEL(panel), PUI_1);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : data    = données complémentaire à manipuler.                *
*                store   = gestionnaire de l'ensemble des données.            *
*                iter    = localisation des données à analyser.               *
*                portion = portion binaire présente à la position courante.   *
*                                                                             *
*  Description : Détermine si un noeud de l'arborescence doit être filtré.    *
*                                                                             *
*  Retour      : Bilan du filtrage.                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool update_bintree_node(const bintree_update_data *data, GtkTreeStore *store, GtkTreeIter *iter, GBinPortion *portion)
{
    bool result;                            /* Bilan à retourner           */
    regmatch_t match;                       /* Récupération des trouvailles*/
    bool caption_matched;                   /* Correspondance de sélection */
    bool start_matched;                     /* Correspondance de sélection */
    bool end_matched;                       /* Correspondance de sélection */
    bool rights_matched;                    /* Correspondance de sélection */

    caption_matched = is_bintree_column_matching(data, portion, BTC_CAPTION, &match);

    if (caption_matched)
        update_bintree_column_in_tree_view(store, iter, portion, BTC_CAPTION, &match);

    start_matched = is_bintree_column_matching(data, portion, BTC_START, &match);

    if (start_matched)
        update_bintree_column_in_tree_view(store, iter, portion, BTC_START, &match);

    end_matched = is_bintree_column_matching(data, portion, BTC_END, &match);

    if (end_matched)
        update_bintree_column_in_tree_view(store, iter, portion, BTC_END, &match);

    rights_matched = is_bintree_column_matching(data, portion, BTC_RIGHTS, &match);

    if (rights_matched)
        update_bintree_column_in_tree_view(store, iter, portion, BTC_RIGHTS, &match);

    result = (caption_matched || start_matched || end_matched || rights_matched);

    gtk_tree_store_set(store, iter, BTC_MATCHED, result, -1);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel  = panneau assurant l'affichage des symboles.          *
*                status = barre de statut à tenir informée.                   *
*                id     = identifiant pour le suivi de la progression.        *
*                data   = données complémentaire à manipuler.                 *
*                                                                             *
*  Description : Exécute un nouveau filtrage des symboles affichés.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void do_filtering_on_portions(const GBintreePanel *panel, GtkStatusStack *status, activity_id_t id, bintree_update_data *data)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeStore *store;                    /* Modèle de gestion           */


    gboolean filter_portion_panel_iter(GtkTreeModel *model, GtkTreePath *path, GtkTreeIter *iter, gpointer unused)
    {
        GBinPortion *portion;               /* Portion à traiter           */
        bool matched;                       /* Correspondance de sélection */
        gboolean shown;                     /* Visibilité actuelle         */

        gtk_tree_model_get(model, iter, BTC_PORTION, &portion, -1);

        if (portion != NULL)
        {
            matched = update_bintree_node(data, store, iter, portion);

            gtk_tree_model_get(model, iter, BTC_MATCHED, &shown, -1);

            if (!matched)
            {
                if (shown)
                    update_node_visibility(store, iter, BTC_MATCHED, false);
            }

            else
            {
                if (!shown)
                    update_node_visibility(store, iter, BTC_MATCHED, true);
            }

            g_object_unref(G_OBJECT(portion));

            gtk_status_stack_update_activity_value(status, id, 1);

        }

        return FALSE;

    }


    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    store = GTK_TREE_STORE(gtk_builder_get_object(builder, "store"));

    gtk_tree_model_foreach(GTK_TREE_MODEL(store), (GtkTreeModelForeachFunc)filter_portion_panel_iter, NULL);

    g_object_unref(G_OBJECT(builder));

}



/* ---------------------------------------------------------------------------------- */
/*                        MECANISMES DE MISE A JOUR DE PANNEAU                        */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : data    = données complémentaire à manipuler.                *
*                portion = portion de binaire concernée par l'analyse.        *
*                column  = colonne visée par l'analyse.                       *
*                match   = récupération des trouvailles. [OUT]                *
*                                                                             *
*  Description : Détermine si une valeur de portion doit être filtrée ou non. *
*                                                                             *
*  Retour      : true si le symbol ne doit pas être affiché, false sinon.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool is_bintree_column_matching(const bintree_update_data *data, GBinPortion *portion, gint column, regmatch_t *match)
{
    bool result;                            /* Bilan à retourner           */
    const char *content;                    /* Contenu à analyser          */
    const mrange_t *range;                  /* Espace de portion à traiter */
    VMPA_BUFFER(offset);                    /* Localisation quelconque     */
    vmpa2t end;                             /* Zone de construction temp.  */
    PortionAccessRights rights;             /* Droits d'accès à analyser   */
    char hrights[4];                        /* Version humainement lisible */

    switch (column)
    {
        case BTC_CAPTION:
            content = g_binary_portion_get_desc(portion);
            break;

        case BTC_START:
            range = g_binary_portion_get_range(portion);
            vmpa2_phys_to_string(get_mrange_addr(range), MDS_UNDEFINED, offset, NULL);
            content = offset;
            break;

        case BTC_END:
            range = g_binary_portion_get_range(portion);
            compute_mrange_end_addr(range, &end);
            vmpa2_phys_to_string(&end, MDS_UNDEFINED, offset, NULL);
            content = offset;
            break;

        case BTC_RIGHTS:
            rights = g_binary_portion_get_rights(portion);
            hrights[0] = (rights & PAC_READ ? 'r' : '-');
            hrights[1] = (rights & PAC_WRITE ? 'w' : '-');
            hrights[2] = (rights & PAC_EXEC ? 'x' : '-');
            hrights[3] = '\0';
            content = hrights;
            break;

    }

    result = is_content_matching(data->filter, content, match);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau ciblé par une mise à jour.                   *
*                uid   = identifiant de la phase de traitement.               *
*                count = nombre d'étapes à prévoir dans le traitement. [OUT]  *
*                data  = données sur lesquelles s'appuyer ensuite. [OUT]      *
*                msg   = description du message d'information. [OUT]          *
*                                                                             *
*  Description : Prépare une opération de mise à jour de panneau.             *
*                                                                             *
*  Retour      : Bilan de la préparation.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_bintree_panel_setup(const GBintreePanel *panel, unsigned int uid, size_t *count, bintree_update_data **data, char **msg)
{
    bool result;                            /* Bilan à retourner           */
#ifndef NDEBUG
    int ret;                                /* Bilan de mise en place      */
#endif
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeView *treeview;                  /* Arborescence graphique      */

    result = true;

    *data = malloc(sizeof(bintree_update_data));

    switch (uid)
    {
        case PUI_0:

            *count = 0;
            (*data)->count = 0;

            *msg = strdup(_("Loading portions contained in the binary format..."));

            break;

        case PUI_1:

            *count = panel->count;
            (*data)->count = panel->count;

            *msg = strdup(_("Filtering portions contained in the binary format..."));

            break;

        default:    /* Pour GCC... */
            assert(false);
            result = false;
            break;

    }

    if (G_PANEL_ITEM(panel)->filter != NULL)
    {
        (*data)->filter = malloc(sizeof(regex_t));

#ifndef NDEBUG
        ret = regcomp((*data)->filter, G_PANEL_ITEM(panel)->filter, REG_EXTENDED | REG_ICASE);
        assert(ret == 0);
#else
        regcomp((*data)->filter, G_PANEL_ITEM(panel)->filter, REG_EXTENDED | REG_ICASE);
#endif

    }

    else
        (*data)->filter = NULL;

    /* Mémorisation de tous les noeuds ouverts */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    treeview = GTK_TREE_VIEW(gtk_builder_get_object(builder, "treeview"));

    void keep_track_of_expanded(GtkTreeView *tv, GtkTreePath *path, bintree_update_data *sud)
    {
        if (sud->ecount == sud->eallocated)
        {
            sud->eallocated += EXPAND_ALLOC_RANGE;
            sud->expanded = (char **)realloc(sud->expanded, sud->eallocated * sizeof(char *));
        }

        sud->expanded[sud->ecount] = gtk_tree_path_to_string(path);

        sud->ecount++;

    }

    (*data)->expanded = NULL;
    (*data)->ecount = 0;
    (*data)->eallocated = 0;

    gtk_tree_view_map_expanded_rows(treeview, (GtkTreeViewMappingFunc)keep_track_of_expanded, *data);

    g_object_unref(G_OBJECT(builder));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau ciblé par une mise à jour.                   *
*                uid   = identifiant de la phase de traitement.               *
*                data  = données préparées par l'appelant.                    *
*                                                                             *
*  Description : Bascule l'affichage d'un panneau avant mise à jour.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : Cette fonction est appelée depuis le contexte principal.     *
*                                                                             *
******************************************************************************/

static void g_bintree_panel_introduce(const GBintreePanel *panel, unsigned int uid, bintree_update_data *data)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeView *treeview;                  /* Arborescence graphique      */
    GtkTreeModel *model;                    /* Source de données associée  */

    /* Basculement de l'affichage hors ligne */

    g_panel_item_switch_to_updating_mask(G_PANEL_ITEM(panel));

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    treeview = GTK_TREE_VIEW(gtk_builder_get_object(builder, "treeview"));

    model = gtk_tree_view_get_model(treeview);

    if (model != NULL)
    {
        g_object_ref(G_OBJECT(model));
        gtk_tree_view_set_model(treeview, NULL);
    }

    g_object_unref(G_OBJECT(builder));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel  = panneau ciblé par une mise à jour.                  *
*                uid    = identifiant de la phase de traitement.              *
*                status = barre de statut à tenir informée.                   *
*                id     = identifiant pour le suivi de la progression.        *
*                data   = données préparées par l'appelant.                   *
*                                                                             *
*  Description : Réalise une opération de mise à jour de panneau.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_bintree_panel_process(const GBintreePanel *panel, unsigned int uid, GtkStatusStack *status, activity_id_t id, bintree_update_data *data)
{
    switch (uid)
    {
        case PUI_0:
            reload_portions_for_new_tree_view(panel, status, id, data);
            break;

        case PUI_1:
            do_filtering_on_portions(panel, status, id, data);
            break;

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau ciblé par une mise à jour.                   *
*                uid   = identifiant de la phase de traitement.               *
*                data  = données préparées par l'appelant.                    *
*                                                                             *
*  Description : Bascule l'affichage d'un panneau après mise à jour.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : Cette fonction est appelée depuis le contexte principal.     *
*                                                                             *
******************************************************************************/

static void g_bintree_panel_conclude(GBintreePanel *panel, unsigned int uid, bintree_update_data *data)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeView *treeview;                  /* Arborescence graphique      */
    GtkTreeModel *model;                    /* Source de données associée  */
    size_t i;                               /* Boucle de parcours          */
    GtkTreePath *path;                      /* Chemin d'accès à un noeud   */

    if (g_atomic_int_get(&G_PANEL_ITEM(panel)->switched) > 1)
        goto skip_this_step;

    /* Mise à jour des compteurs */

    panel->count = data->count;

    /* Basculement de l'affichage en ligne */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    treeview = GTK_TREE_VIEW(gtk_builder_get_object(builder, "treeview"));

    model = GTK_TREE_MODEL(gtk_builder_get_object(builder, "filter"));

    g_object_ref(G_OBJECT(model));
    gtk_tree_view_set_model(treeview, model);

    for (i = 0; i < data->ecount; i++)
    {
        path = gtk_tree_path_new_from_string(data->expanded[i]);

        gtk_tree_view_expand_to_path(treeview, path);

        gtk_tree_path_free(path);

    }

    g_object_unref(G_OBJECT(builder));

 skip_this_step:

    g_panel_item_switch_to_updated_content(G_PANEL_ITEM(panel));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau ciblé par une mise à jour.                   *
*                uid   = identifiant de la phase de traitement.               *
*                data  = données en place à nettoyer avant suppression.       *
*                                                                             *
*  Description : Supprime les données dynamiques utilisées à la mise à jour.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_bintree_panel_clean_data(const GUpdatablePanel *panel, unsigned int uid, bintree_update_data *data)
{
    size_t i;                               /* Boucle de parcours          */

    if (data->filter != NULL)
    {
        regfree(data->filter);
        free(data->filter);
    }

    for (i = 0; i < data->ecount; i++)
        g_free(data->expanded[i]);

    if (data->expanded != NULL)
        free(data->expanded);

}
