
/* Chrysalide - Outil d'analyse de fichiers binaires
 * bookmarks.c - panneau d'affichage des signets d'un binaire
 *
 * Copyright (C) 2014-2019 Cyrille Bagard
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


#include "bookmarks.h"


#include <assert.h>
#include <cairo-gobject.h>
#include <malloc.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <gtk/gtk.h>


#include "../panel-int.h"
#include "../core/global.h"
#include "../../analysis/binary.h"
#include "../../analysis/db/items/bookmark.h"
#include "../../core/params.h"
#include "../../core/paths.h"
#include "../../core/queue.h"
#include "../../glibext/chrysamarshal.h"
#include "../../glibext/signal.h"
#include "../../gtkext/easygtk.h"
#include "../../gtkext/gtkdisplaypanel.h"
#include "../../gtkext/gtkdockable-int.h"
#include "../../gtkext/named.h"



/* -------------------------- PARTIE PRINCIPALE DU PANNEAU -------------------------- */


/* Panneau d'affichage des signets liés à un binaire (instance) */
struct _GBookmarksPanel
{
    GPanelItem parent;                      /* A laisser en premier        */

    const regex_t *filter;                  /* Filtre appliqué ou NULL     */

    GtkMenu *menu;                          /* Menu contextuel pour param. */

    GLoadedBinary *binary;                  /* Binaire en cours d'analyse  */

};

/* Panneau d'affichage des signets liés à un binaire (classe) */
struct _GBookmarksPanelClass
{
    GPanelItemClass parent;                 /* A laisser en premier        */

    cairo_surface_t *bookmark_img;          /* Image pour les signets      */

};


/* Colonnes de la liste visuelle */
typedef enum _BookmarkColumn
{
    BMC_BOOKMARK,                           /* Elément GLib représenté     */

    BMC_PICTURE,                            /* Image d'agrément            */
    BMC_PHYSICAL,                           /* Adresse phyisque            */
    BMC_VIRTUAL,                            /* Adresse virtuelle           */
    BMC_COMMENT,                            /* Commentaire associé         */

    BMC_COUNT                               /* Nombre de colonnes          */

} CfgParamColumn;




/* Initialise la classe des panneaux des paramètres de config. */
static void g_bookmarks_panel_class_init(GBookmarksPanelClass *);

/* Initialise une instance de panneau de paramètres de config. */
static void g_bookmarks_panel_init(GBookmarksPanel *);

/* Supprime toutes les références externes. */
static void g_bookmarks_panel_dispose(GBookmarksPanel *);

/* Procède à la libération totale de la mémoire. */
static void g_bookmarks_panel_finalize(GBookmarksPanel *);

/* Fournit le nom interne attribué à l'élément réactif. */
static char *g_bookmarks_panel_class_get_key(const GBookmarksPanelClass *);

/* Indique le chemin initial de la localisation d'un panneau. */
static char *g_bookmarks_panel_class_get_path(const GBookmarksPanelClass *);

/* Réagit à un changement d'affichage principal de contenu. */
static void change_bookmarks_panel_current_content(GBookmarksPanel *, GLoadedContent *, GLoadedContent *);


/* ------------------------- AFFICHAGE A L'AIDE D'UNE LISTE ------------------------- */


/* Recharge une collection de signets à l'affichage. */
static void reload_bookmarks_into_treeview(GBookmarksPanel *, GLoadedBinary *);

/* Met à jour une collection suite à une modification. */
static void on_collection_content_changed(GDbCollection *, ActiveItemChange, GDbBookmark *, GBookmarksPanel *);

/* Réagit au changement de sélection des signets. */
static void on_bookmarks_selection_change(GtkTreeSelection *, gpointer);

/* Etablit une comparaison entre deux lignes de paramètres. */
static gint compare_bookmarks_list_columns(GtkTreeModel *, GtkTreeIter *, GtkTreeIter *, gpointer);

/* Réagit à une pression sur <Shift+F2> et simule l'édition. */
static gboolean on_key_pressed_over_params(GtkTreeView *, GdkEventKey *, GBookmarksPanel *);

/* Réagit à une édition de la valeur d'un commentaire. */
static void on_comment_value_edited(GtkCellRendererText *, gchar *, gchar *, GBookmarksPanel *);



/* ------------------------- FILTRAGE DES SYMBOLES PRESENTS ------------------------- */


/* Démarre l'actualisation du filtrage des paramètres. */
static void update_filtered_bookmarks(GBookmarksPanel *);

/* Détermine si un signet doit être filtré ou non. */
static bool is_bookmark_filtered(GBookmarksPanel *, const char *, const char *, const char *);



/* ------------------------ ATTRIBUTION D'UN MENU CONTEXTUEL ------------------------ */


/* Assure la gestion des clics de souris sur les signets. */
static gboolean on_button_press_over_bookmarks(GtkWidget *, GdkEventButton *, GBookmarksPanel *);

/* Construit le menu contextuel pour les signets. */
static GtkMenu *build_bookmarks_panel_menu(GBookmarksPanel *);

/* Fournit le signet sélectionné dans la liste. */
static GDbBookmark *get_selected_panel_bookmark(GtkTreeView *, GtkTreeIter *);

/* Réagit avec le menu "Editer". */
static void mcb_bookmarks_panel_edit(GtkMenuItem *, GBookmarksPanel *);

/* Réagit avec le menu "Supprimer". */
static void mcb_bookmarks_panel_delete(GtkMenuItem *, GBookmarksPanel *);

/* Réagit avec le menu "Filtrer...". */
static void mcb_bookmarks_panel_filter(GtkMenuItem *, GBookmarksPanel *);



/* ---------------------------------------------------------------------------------- */
/*                            PARTIE PRINCIPALE DU PANNEAU                            */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un panneau d'affichage des signets liés à un binaire. */
G_DEFINE_TYPE(GBookmarksPanel, g_bookmarks_panel, G_TYPE_PANEL_ITEM);


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des panneaux des paramètres de config.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_bookmarks_panel_class_init(GBookmarksPanelClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GEditorItemClass *item;                 /* Encore une autre vision...  */
    GPanelItemClass *panel;                 /* Version parente de la classe*/
    gchar *filename;                        /* Chemin d'accès à utiliser   */

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_bookmarks_panel_dispose;
    object->finalize = (GObjectFinalizeFunc)g_bookmarks_panel_finalize;

    item = G_EDITOR_ITEM_CLASS(class);

    item->get_key = (get_item_key_fc)g_bookmarks_panel_class_get_key;

    item->change_content = (change_item_content_fc)change_bookmarks_panel_current_content;

    panel = G_PANEL_ITEM_CLASS(class);

    panel->dock_at_startup = gtk_panel_item_class_return_false;
    panel->can_search = gtk_panel_item_class_return_true;
    panel->get_path = (get_panel_path_fc)g_bookmarks_panel_class_get_path;

    panel->update_filtered = (update_filtered_fc)update_filtered_bookmarks;

    panel->gid = setup_tiny_global_work_group(1);

    filename = find_pixmap_file("bookmark.png");
    assert(filename != NULL);

    class->bookmark_img = cairo_image_surface_create_from_png(filename);

    g_free(filename);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance de panneau de paramètres de config.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_bookmarks_panel_init(GBookmarksPanel *panel)
{
    GPanelItem *pitem;                      /* Version parente du panneau  */
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GObject *crenderer;                     /* Moteur de rendu de colonne  */
    GtkTreeSortable *sortable;              /* Autre vision de la liste    */

    /* Eléments de base */

    pitem = G_PANEL_ITEM(panel);

    pitem->widget = G_NAMED_WIDGET(gtk_built_named_widget_new_for_panel(_("Bookmarks"),
                                                                        _("Bookmarks for the current binary"),
                                                                        PANEL_BOOKMARKS_ID));

    /* Représentation graphique */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(pitem->widget));

    crenderer = G_OBJECT(gtk_builder_get_object(builder, "crenderer"));

    g_object_set(crenderer, "editable", TRUE, NULL);

    /* Tri de la liste */

    sortable = GTK_TREE_SORTABLE(gtk_builder_get_object(builder, "store"));

    gtk_tree_sortable_set_sort_func(sortable, BMC_PHYSICAL, compare_bookmarks_list_columns,
                                    GINT_TO_POINTER(BMC_PHYSICAL), NULL);

    gtk_tree_sortable_set_sort_func(sortable, BMC_VIRTUAL, compare_bookmarks_list_columns,
                                    GINT_TO_POINTER(BMC_VIRTUAL), NULL);

    gtk_tree_sortable_set_sort_func(sortable, BMC_COMMENT, compare_bookmarks_list_columns,
                                    GINT_TO_POINTER(BMC_COMMENT), NULL);

    gtk_tree_sortable_set_sort_column_id(sortable, BMC_PHYSICAL, GTK_SORT_ASCENDING);

    /* Préparation du menu contextuel */

    panel->menu = build_bookmarks_panel_menu(panel);

    /* Connexion des signaux */

    gtk_builder_add_callback_symbols(builder,
                                     BUILDER_CALLBACK(on_button_press_over_bookmarks),
                                     BUILDER_CALLBACK(on_key_pressed_over_params),
                                     BUILDER_CALLBACK(on_comment_value_edited),
                                     BUILDER_CALLBACK(on_bookmarks_selection_change),
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

static void g_bookmarks_panel_dispose(GBookmarksPanel *panel)
{
    change_bookmarks_panel_current_content(panel, NULL, NULL);

    g_clear_object(&panel->binary);

    G_OBJECT_CLASS(g_bookmarks_panel_parent_class)->dispose(G_OBJECT(panel));

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

static void g_bookmarks_panel_finalize(GBookmarksPanel *panel)
{
    G_OBJECT_CLASS(g_bookmarks_panel_parent_class)->finalize(G_OBJECT(panel));

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

static char *g_bookmarks_panel_class_get_key(const GBookmarksPanelClass *class)
{
    char *result;                           /* Description à renvoyer      */

    result = strdup(PANEL_BOOKMARKS_ID);

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

static char *g_bookmarks_panel_class_get_path(const GBookmarksPanelClass *class)
{
    char *result;                           /* Emplacement à retourner     */

    result = strdup("Ms");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un panneau d'affichage des paramètres de configuration. *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GPanelItem *g_bookmarks_panel_new(void)
{
    GPanelItem *result;                     /* Structure à retourner       */

    result = g_object_new(G_TYPE_BOOKMARKS_PANEL, NULL);

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

static void change_bookmarks_panel_current_content(GBookmarksPanel *panel, GLoadedContent *old, GLoadedContent *new)
{
    GLoadedBinary *binary;                  /* Autre version de l'instance */
    GDbCollection *collec;                  /* Collection à lister ici     */

    if (G_IS_LOADED_BINARY(new))
        binary = G_LOADED_BINARY(new);
    else
        binary = NULL;

    /* Basculement du binaire utilisé */

    if (panel->binary != NULL)
    {
        collec = g_loaded_binary_find_collection(panel->binary, DBF_BOOKMARKS);
        g_signal_handlers_disconnect_by_func(collec, G_CALLBACK(on_collection_content_changed), panel);

        g_object_unref(G_OBJECT(panel->binary));

    }

    panel->binary = binary;

    if (panel->binary != NULL)
    {
        g_object_ref(G_OBJECT(binary));

        collec = g_loaded_binary_find_collection(binary, DBF_BOOKMARKS);
        g_signal_connect_to_main(collec, "active-changed", G_CALLBACK(on_collection_content_changed), panel,
                                 g_cclosure_user_marshal_VOID__ENUM_OBJECT);

    }

    reload_bookmarks_into_treeview(panel, binary);

}



/* ---------------------------------------------------------------------------------- */
/*                           AFFICHAGE A L'AIDE D'UNE LISTE                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : panel  = panneau d'affichage des signets liés à un binaire.  *
*                binary = propriétaire de la collection à présenter.          *
*                                                                             *
*  Description : Recharge une collection de signets à l'affichage.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void reload_bookmarks_into_treeview(GBookmarksPanel *panel, GLoadedBinary *binary)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkListStore *store;                    /* Modèle de gestion           */
    GArchProcessor *proc;                   /* Architecture du binaire     */
    MemoryDataSize msize;                   /* Taille par défaut           */
    GDbCollection *collec;                  /* Collection à lister ici     */
    size_t count;                           /* Taille de la liste obtenue  */
    GDbItem **items;                        /* Liste des éléments actifs   */
    size_t i;                               /* Boucle de parcours          */
    GDbBookmark *bookmark;                  /* Signet en cours d'étude     */
    const vmpa2t *addr;                     /* Adressse associée au signet */
    VMPA_BUFFER(phys);                      /* Position physique           */
    VMPA_BUFFER(virt);                      /* Adresse virtuelle           */
    const char *comment;                    /* Commentaire associé         */
    GtkTreeIter iter;                       /* Point d'insertion           */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    store = GTK_LIST_STORE(gtk_builder_get_object(builder, "store"));

    gtk_list_store_clear(store);

    /* Si le panneau actif ne représente pas un binaire... */

    if (panel->binary == NULL) return;

    /* Actualisation de l'affichage */

    proc = g_loaded_binary_get_processor(binary);
    msize = g_arch_processor_get_memory_size(proc);
    g_object_unref(G_OBJECT(proc));

    collec = g_loaded_binary_find_collection(panel->binary, DBF_BOOKMARKS);

    g_db_collection_rlock(collec);

    items = g_db_collection_get_last_items(collec, &count);

    for (i = 0; i < count; i++)
    {
        bookmark = G_DB_BOOKMARK(items[i]);

        addr = g_db_bookmark_get_address(bookmark);

        vmpa2_phys_to_string(addr, msize, phys, NULL);
        vmpa2_virt_to_string(addr, msize, virt, NULL);

        comment = g_db_bookmark_get_comment(bookmark);

        if (!is_bookmark_filtered(panel, phys, virt, comment))
        {
            gtk_list_store_append(store, &iter);
            gtk_list_store_set(store, &iter,
                               BMC_BOOKMARK, bookmark,
                               BMC_PICTURE, G_BOOKMARKS_PANEL_GET_CLASS(panel)->bookmark_img,
                               BMC_PHYSICAL, phys,
                               BMC_VIRTUAL, virt,
                               BMC_COMMENT, comment,
                               -1);

        }

        g_object_unref(G_OBJECT(bookmark));

    }

    if (items != NULL)
        free(items);

    g_db_collection_runlock(collec);

    g_object_unref(G_OBJECT(builder));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec   = collection dont le contenu vient de changer.      *
*                action   = type de modification notifiée par la collection.  *
*                bookmark = élément en cause dans le changement survenu.      *
*                panel    = structure contenant les informations maîtresses.  *
*                                                                             *
*  Description : Met à jour une collection suite à une modification.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_collection_content_changed(GDbCollection *collec, ActiveItemChange change, GDbBookmark *bookmark, GBookmarksPanel *panel)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkListStore *store;                    /* Modèle de gestion           */
    GtkTreeModel *model;                    /* Modèle de gestion courant   */
    GDbBookmark *displayed;                 /* Elément de collection       */
    gboolean status;                        /* Bilan d'une comparaison     */
    GArchProcessor *proc;                   /* Architecture du binaire     */
    MemoryDataSize msize;                   /* Taille par défaut           */
    const vmpa2t *addr;                     /* Adressse associée au signet */
    VMPA_BUFFER(phys);                      /* Position physique           */
    VMPA_BUFFER(virt);                      /* Adresse virtuelle           */
    GtkTreeIter iter;                       /* Point d'insertion           */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    store = GTK_LIST_STORE(gtk_builder_get_object(builder, "store"));

    switch (change)
    {
        case AIC_REMOVED:
        case AIC_UPDATED:

            model = GTK_TREE_MODEL(store);

            if (gtk_tree_model_get_iter_first(model, &iter))
            {
                status = TRUE;

                do
                {
                    gtk_tree_model_get(model, &iter, BMC_BOOKMARK, &displayed, -1);

                    status = g_db_item_cmp_key(G_DB_ITEM(bookmark), G_DB_ITEM(displayed));

                    if (status)
                        gtk_list_store_remove(store, &iter);

                    g_object_unref(G_OBJECT(displayed));

                    if (status)
                        break;

                }
                while (gtk_tree_model_iter_next(model, &iter));

                assert(status);

            }

            if (change == AIC_REMOVED)
                break;

        case AIC_ADDED:

            proc = g_loaded_binary_get_processor(panel->binary);
            msize = g_arch_processor_get_memory_size(proc);
            g_object_unref(G_OBJECT(proc));

            addr = g_db_bookmark_get_address(bookmark);

            vmpa2_phys_to_string(addr, msize, phys, NULL);
            vmpa2_virt_to_string(addr, msize, virt, NULL);

            gtk_list_store_append(store, &iter);
            gtk_list_store_set(store, &iter,
                               BMC_BOOKMARK, bookmark,
                               BMC_PICTURE, G_BOOKMARKS_PANEL_GET_CLASS(panel)->bookmark_img,
                               BMC_PHYSICAL, phys,
                               BMC_VIRTUAL, virt,
                               BMC_COMMENT, g_db_bookmark_get_comment(bookmark),
                               -1);

            break;

    }

    g_object_unref(G_OBJECT(builder));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : selection = sélection modifiée.                              *
*                unused    = adresse non utilisée ici.                        *
*                                                                             *
*  Description : Réagit au changement de sélection des signets.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_bookmarks_selection_change(GtkTreeSelection *selection, gpointer unused)
{
    GtkTreeIter iter;                       /* Point de sélection          */
    GtkTreeModel *model;                    /* Modèle de gestion           */
    GDbBookmark *bookmark;                  /* Signet en cours d'étude     */
    const vmpa2t *addr;                     /* Adressse associée au signet */
    GLoadedPanel *panel;                    /* Afficheur effectif de code  */

    if (gtk_tree_selection_get_selected(selection, &model, &iter))
    {
        gtk_tree_model_get(model, &iter, BMC_BOOKMARK, &bookmark, -1);

        addr = g_db_bookmark_get_address(bookmark);

        panel = get_current_view();

        if (GTK_IS_DISPLAY_PANEL(panel))
            gtk_display_panel_request_move(GTK_DISPLAY_PANEL(panel), addr);

        g_object_unref(G_OBJECT(panel));

        g_object_unref(G_OBJECT(bookmark));

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : model  = gestionnaire du tableau de données.                 *
*                a      = première ligne de données à traiter.                *
*                b      = seconde ligne de données à traiter.                 *
*                column = indice de la colonne à considérer, encodée.         *
*                                                                             *
*  Description : Etablit une comparaison entre deux lignes de signets.        *
*                                                                             *
*  Retour      : Indication de tri entre les deux lignes fournies.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gint compare_bookmarks_list_columns(GtkTreeModel *model, GtkTreeIter *a, GtkTreeIter *b, gpointer column)
{
    gint result;                            /* Valeur calculée à retourner */
    gchar *value_a;                         /* Cellule de la ligne 'a'     */
    gchar *value_b;                         /* Cellule de la ligne 'b'     */

    gtk_tree_model_get(model, a, GPOINTER_TO_INT(column), &value_a, -1);
    gtk_tree_model_get(model, b, GPOINTER_TO_INT(column), &value_b, -1);

    if (value_a == NULL || value_b == NULL)
    {
        if (value_a == NULL && value_b == NULL)
            result = 0;
        else
            result = (value_a == NULL ? -1 : 1);
    }
    else
        result = g_utf8_collate(value_a, value_b);

    g_free(value_a);
    g_free(value_b);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : treeview = composant graphique présentant les paramètres.    *
*                event    = informations liées à l'événement.                 *
*                panel    = panneau d'affichage sur lequel s'appuyer.         *
*                                                                             *
*  Description : Réagit à une pression sur <Shift+F2> et simule l'édition.    *
*                                                                             *
*  Retour      : FALSE pour poursuivre la propagation de l'événement.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean on_key_pressed_over_params(GtkTreeView *treeview, GdkEventKey *event, GBookmarksPanel *panel)
{
    const gchar *accelerator;               /* Combinaison de raccourci    */
    guint accel_key;                        /* Touche de raccourci         */
    GdkModifierType accel_mod;              /* Modifiateurs attendus aussi */

    if (event->keyval == GDK_KEY_Delete)
        mcb_bookmarks_panel_delete(NULL, panel);

    else
    {
        if (!g_generic_config_get_value(get_main_configuration(), MPK_KEYBINDINGS_EDIT, &accelerator))
            return FALSE;

        if (accelerator == NULL)
            return FALSE;

        gtk_accelerator_parse(accelerator, &accel_key, &accel_mod);

        if (event->keyval == accel_key && event->state == accel_mod)
            mcb_bookmarks_panel_edit(NULL, panel);

    }

    return FALSE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : renderer = moteur de rendu pour la cellule.                  *
*                path     = chemin d'accès vers la cellule éditée.            *
*                new      = nouvelle valeur sous forme de texte à valider.    *
*                panel    = panneau d'affichage sur lequel s'appuyer.         *
*                                                                             *
*  Description : Réagit à une édition de la valeur d'un commentaire.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_comment_value_edited(GtkCellRendererText *renderer, gchar *path, gchar *new, GBookmarksPanel *panel)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkListStore *store;                    /* Modèle de gestion           */
    GtkTreePath *tree_path;                 /* Chemin d'accès natif        */
    GtkTreeIter iter;                       /* Point de la modification    */
    GDbBookmark *mark;                      /* Signet sélectionné          */
    GDbBookmark *updater;                   /* Signet de mise à jour       */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    store = GTK_LIST_STORE(gtk_builder_get_object(builder, "store"));

    tree_path = gtk_tree_path_new_from_string(path);
    if (tree_path == NULL) goto bad_path;

    if (!gtk_tree_model_get_iter(GTK_TREE_MODEL(store), &iter, tree_path))
        goto bad_iter;

    gtk_tree_model_get(GTK_TREE_MODEL(store), &iter, BMC_BOOKMARK, &mark, -1);

    updater = g_db_bookmark_new(g_db_bookmark_get_address(mark), new);

    g_loaded_binary_add_to_collection(panel->binary, G_DB_ITEM(updater));

    g_object_unref(G_OBJECT(mark));

 bad_iter:

    gtk_tree_path_free(tree_path);

 bad_path:

    g_object_unref(G_OBJECT(builder));

}



/* ---------------------------------------------------------------------------------- */
/*                           FILTRAGE DES SYMBOLES PRESENTS                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau assurant l'affichage des paramètres.         *
*                                                                             *
*  Description : Démarre l'actualisation du filtrage des paramètres.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void update_filtered_bookmarks(GBookmarksPanel *panel)
{
    reload_bookmarks_into_treeview(panel, panel->binary);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel   = panneau assurant l'affichage des paramètres.       *
*                phys    = position physique du signet.                       *
*                virt    = adresse virtuelle du signet.                       *
*                comment = commentaire lisible associé au signet.             *
*                                                                             *
*  Description : Détermine si un signet doit être filtré ou non.              *
*                                                                             *
*  Retour      : true si le signet ne doit pas être affiché, false sinon.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool is_bookmark_filtered(GBookmarksPanel *panel, const char *phys, const char *virt, const char *comment)
{
    bool result;                            /* Bilan à retourner           */
    regmatch_t match;                       /* Récupération des trouvailles*/
    int ret;                                /* Bilan du filtrage           */

    if (panel->filter == NULL)
        return false;

    result = true;

    ret = regexec(panel->filter, phys, 1, &match, 0);
    result &= (ret == REG_NOMATCH);

    ret = regexec(panel->filter, virt, 1, &match, 0);
    result &= (ret == REG_NOMATCH);

    ret = regexec(panel->filter, comment, 1, &match, 0);
    result &= (ret == REG_NOMATCH);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                          ATTRIBUTION D'UN MENU CONTEXTUEL                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant GTK visé par l'opération.                 *
*                event  = informations liées à l'événement.                   *
*                panel  = informations liées au panneau associé.              *
*                                                                             *
*  Description : Assure la gestion des clics de souris sur les signets.       *
*                                                                             *
*  Retour      : FALSE pour poursuivre la propagation de l'événement.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean on_button_press_over_bookmarks(GtkWidget *widget, GdkEventButton *event, GBookmarksPanel *panel)
{
    GtkTreeSelection *selection;            /* Sélection courante          */
    GtkTreeIter iter;                       /* Point de sélection          */
    GtkTreeModel *model;                    /* Modèle de gestion           */
    GDbBookmark *bookmark;                  /* Signet en cours d'étude     */
    const vmpa2t *addr;                     /* Adressse associée au signet */
    GLoadedPanel *display;                  /* Afficheur effectif de code  */

    switch (event->button)
    {
        case 1:

            selection = gtk_tree_view_get_selection(GTK_TREE_VIEW(widget));

            if (gtk_tree_selection_get_selected(selection, &model, &iter))
            {
                gtk_tree_model_get(model, &iter, BMC_BOOKMARK, &bookmark, -1);

                addr = g_db_bookmark_get_address(bookmark);

                display = get_current_view();

                if (GTK_IS_DISPLAY_PANEL(display))
                    gtk_display_panel_request_move(GTK_DISPLAY_PANEL(display), addr);

                g_object_unref(G_OBJECT(display));

                g_object_unref(G_OBJECT(bookmark));

            }

            break;

        case 3:
            gtk_menu_popup_at_pointer(panel->menu, (GdkEvent *)event);
            break;

    }

    return FALSE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau d'affichage des signets liés à un binaire.   *
*                                                                             *
*  Description : Construit le menu contextuel pour les signets.               *
*                                                                             *
*  Retour      : Panneau de menus mis en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GtkMenu *build_bookmarks_panel_menu(GBookmarksPanel *panel)
{
    GtkWidget *result;                      /* Support à retourner         */
    GtkWidget *submenuitem;                 /* Sous-élément de menu        */

    result = qck_create_menu(NULL);

    submenuitem = qck_create_menu_item(NULL, NULL, _("Edit"), G_CALLBACK(mcb_bookmarks_panel_edit), panel);
    gtk_container_add(GTK_CONTAINER(result), submenuitem);

    submenuitem = qck_create_menu_item(NULL, NULL, _("Delete"), G_CALLBACK(mcb_bookmarks_panel_delete), panel);
    gtk_container_add(GTK_CONTAINER(result), submenuitem);

    submenuitem = qck_create_menu_separator();
    gtk_container_add(GTK_CONTAINER(result), submenuitem);

    submenuitem = qck_create_menu_item(NULL, NULL, _("Filter..."), G_CALLBACK(mcb_bookmarks_panel_filter), panel);
    gtk_container_add(GTK_CONTAINER(result), submenuitem);

    return GTK_MENU(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : treeview = liste d'affichage à consulter.                    *
*                save     = zone de conservation du point de trouvaille. [OUT]*
*                                                                             *
*  Description : Fournit le signet sélectionné dans la liste.                 *
*                                                                             *
*  Retour      : Signet en cours d'édition ou NULL en cas de soucis.          *
*                                                                             *
*  Remarques   : Le résultat non nul est à déréférencer après usage.          *
*                                                                             *
******************************************************************************/

static GDbBookmark *get_selected_panel_bookmark(GtkTreeView *treeview, GtkTreeIter *save)
{
    GDbBookmark *result;                    /* Paramètre à renvoyer        */
    GtkTreeSelection *selection;            /* Représentation de sélection */
    GtkTreeModel *model;                    /* Gestionnaire des données    */
    GtkTreeIter iter;                       /* Point de la sélection       */

    result = NULL;

    selection = gtk_tree_view_get_selection(treeview);

    if (gtk_tree_selection_get_selected(selection, &model, &iter))
        gtk_tree_model_get(model, &iter, BMC_BOOKMARK, &result, -1);

    if (save != NULL)
        *save = iter;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                panel    = panneau d'affichage des signets liés à un binaire.*
*                                                                             *
*  Description : Réagit avec le menu "Editer".                                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_bookmarks_panel_edit(GtkMenuItem *menuitem, GBookmarksPanel *panel)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeView *treeview;                  /* Arborescence manipulée      */
    GtkTreeIter iter;                       /* Point de la sélection       */
    GDbBookmark *mark;                      /* Signet sélectionné          */
    GtkTreeModel *model;                    /* Gestionnaire de données     */
    GtkTreePath *path;                      /* Chemin d'accès à ce point   */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    treeview = GTK_TREE_VIEW(gtk_builder_get_object(builder, "treeview"));

    mark = get_selected_panel_bookmark(treeview, &iter);
    if (mark == NULL) return;

    model = gtk_tree_view_get_model(treeview);
    path = gtk_tree_model_get_path(model, &iter);

    gtk_tree_view_set_cursor(treeview, path,
                             gtk_tree_view_get_column(treeview, BMC_COMMENT - BMC_PICTURE),
                             TRUE);

    gtk_tree_path_free(path);

    g_object_unref(G_OBJECT(mark));

    g_object_unref(G_OBJECT(builder));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                panel    = panneau d'affichage des signets liés à un binaire.*
*                                                                             *
*  Description : Réagit avec le menu "Supprimer".                             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_bookmarks_panel_delete(GtkMenuItem *menuitem, GBookmarksPanel *panel)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeView *treeview;                  /* Affichage de la liste       */
    GDbBookmark *mark;                      /* Signet sélectionné          */
    GDbBookmark *eraser;                    /* Signet de suppression       */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    treeview = GTK_TREE_VIEW(gtk_builder_get_object(builder, "treeview"));

    mark = get_selected_panel_bookmark(treeview, NULL);

    if (mark != NULL)
    {
        eraser = g_db_bookmark_new(g_db_bookmark_get_address(mark), NULL);
        g_db_item_add_flag(G_DB_ITEM(eraser), DIF_ERASER);

        g_loaded_binary_add_to_collection(panel->binary, G_DB_ITEM(eraser));

        g_object_unref(G_OBJECT(mark));

    }

    g_object_unref(G_OBJECT(builder));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                panel    = panneau d'affichage des signets liés à un binaire.*
*                                                                             *
*  Description : Réagit avec le menu "Filtrer...".                            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_bookmarks_panel_filter(GtkMenuItem *menuitem, GBookmarksPanel *panel)
{
#if 0
    GCfgParam *param;                       /* Paramètre sélectionné       */

    param = get_selected_panel_bookmark(panel->treeview, NULL);
    if (param == NULL) return;

    g_config_param_make_empty(param);

    g_object_unref(G_OBJECT(param));
#endif
}
