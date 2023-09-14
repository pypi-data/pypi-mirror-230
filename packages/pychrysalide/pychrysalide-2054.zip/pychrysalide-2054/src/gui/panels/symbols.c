
/* Chrysalide - Outil d'analyse de fichiers binaires
 * symbols.c - panneau d'affichage des symboles
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


#include "symbols.h"


#include <i18n.h>


#include <assert.h>
#include <cairo-gobject.h>
#include <malloc.h>
#include <regex.h>
#include <string.h>
#include <gdk/gdkkeysyms.h>


#include "updating-int.h"
#include "../agroup.h"
#include "../panel-int.h"
#include "../core/global.h"
#include "../../common/extstr.h"
#include "../../core/paths.h"
#include "../../core/queue.h"
#include "../../format/format.h"
#include "../../format/symiter.h"
#include "../../gtkext/easygtk.h"
#include "../../gtkext/gtkdisplaypanel.h"
#include "../../gtkext/named.h"
#include "../../gtkext/tmgt.h"
#include "../../mangling/demangler.h"



/* -------------------------- PARTIE PRINCIPALE DU PANNEAU -------------------------- */


/* Panneau d'affichage des symboles (instance) */
struct _GSymbolsPanel
{
    GPanelItem parent;                      /* A laisser en premier        */

    GLoadedBinary *binary;                  /* Binaire à prendre en compte */
    char *sep;                              /* Délimitateur à utiliser     */

    size_t count;                           /* Quantité de symboles utiles */

};

/* Panneau d'affichage des symboles (classe) */
struct _GSymbolsPanelClass
{
    GPanelItemClass parent;                 /* A laisser en premier        */

    cairo_surface_t *routine_img;           /* Image pour les routines     */
    cairo_surface_t *object_img;            /* Image pour les objets       */
    cairo_surface_t *package_img;           /* Image pour les paquets      */
    cairo_surface_t *class_img;             /* Image pour les classes      */

};


/* Colonnes de la liste des symboles */
typedef enum _SymbolsColumn
{
    SBC_SYMBOL,                             /* Symbole représenté          */

    SBC_PICTURE,                            /* Image de représentation     */
    SBC_NAME,                               /* Désignation humaine         */
    SBC_ORIGINAL,                           /* Version brute d'origine     */
    SBC_ADDRESS,                            /* Adresse mémoire du symbole  */
    SBC_SECTION,                            /* Section d'appartenance      */

    SBC_EXPAND,                             /* Affichage des classes       */
    SBC_MATCHED,                            /* Correspondance établie ?    */
    SBC_MATCH_POINTS,                       /* Nombre de demandeurs        */

    SBC_COUNT                               /* Nombre de colonnes          */

} SymbolsColumn;


/* Données utiles à la mise à jour */
typedef struct _symbols_update_data symbols_update_data;


/* Initialise la classe des panneaux d'affichage des symboles. */
static void g_symbols_panel_class_init(GSymbolsPanelClass *);

/* Initialise une instance de panneau d'affichage des symboles. */
static void g_symbols_panel_init(GSymbolsPanel *);

/* Procède à l'initialisation de l'interface de mise à jour. */
static void g_symbols_panel_updatable_interface_init(GUpdatablePanelInterface *);

/* Supprime toutes les références externes. */
static void g_symbols_panel_dispose(GSymbolsPanel *);

/* Procède à la libération totale de la mémoire. */
static void g_symbols_panel_finalize(GSymbolsPanel *);

/* Fournit le nom interne attribué à l'élément réactif. */
static char *g_symbols_panel_class_get_key(const GSymbolsPanelClass *);

/* Indique le chemin initial de la localisation d'un panneau. */
static char *g_symbols_panel_class_get_path(const GSymbolsPanelClass *);

/* Indique la définition d'un éventuel raccourci clavier. */
static char *g_symbols_panel_class_get_key_bindings(const GSymbolsPanelClass *);

/* Bascule d'affichage des symboles en liste. */
static void on_symbols_list_display_toggle(GtkToggleToolButton *, GSymbolsPanel *);

/* Bascule l'affichage des symboles en arborescence. */
static void on_symbols_tree_display_toggle(GtkToggleToolButton *, GSymbolsPanel *);

/* Réagit au changement de sélection des symboles. */
static void on_symbols_selection_change(GtkTreeSelection *, gpointer);

/* Réagit à un changement d'affichage principal de contenu. */
static void change_symbols_panel_current_content(GSymbolsPanel *, GLoadedContent *, GLoadedContent *);

/* Réagit à un changement d'affichage principal de contenu. */
static void reload_symbols_panel_content(const GSymbolsPanel *, GtkStatusStack *, activity_id_t, symbols_update_data *);



/* ------------------------- AFFICHAGE A L'AIDE D'UNE LISTE ------------------------- */


/* Réagit à un changement d'affichage principal de contenu. */
static void reload_symbols_for_new_list_view(const GSymbolsPanel *, GtkStatusStack *, activity_id_t, symbols_update_data *);

/* Met en surbrillance les éléments recherchés dans les noms. */
static void update_symbol_name_in_list_view(GtkTreeStore *, GtkTreeIter *, const regmatch_t *);



/* -------------------------- AFFICHAGE SOUS FORME D'ARBRE -------------------------- */


/* S'assure qu'un noeud donné existe bien. */
static GtkTreeIter ensure_symbol_node_exist(const GSymbolsPanel *, GtkTreeIter *, const char *, const regmatch_t *, size_t);

/* Détermine le point d'insertion parent d'une routine. */
static bool find_parent_for_symbol(const GSymbolsPanel *, const GBinSymbol *, GtkTreeIter *, const regmatch_t *, size_t *);

/* Réagit à un changement d'affichage principal de contenu. */
static void reload_symbols_for_new_tree_view(const GSymbolsPanel *, GtkStatusStack *, activity_id_t, symbols_update_data *);

/* Réagit à une nouvelle demande de réorganisation. */
static void reorganize_symbols_tree_view(GtkToolButton *, const GSymbolsPanel *);

/* Fait en sorte que toutes les classes soient affichées. */
static gboolean show_all_classes_in_tree_view(GtkTreeModel *, GtkTreePath *, GtkTreeIter *, GtkTreeView *);

/* Actualise une partie d'un nom de symbole éclaté en noeuds. */
static GtkTreeIter update_symbol_partial_name_in_tree_view(GtkTreeStore *, GtkTreeIter *, const char *, const regmatch_t *, size_t);

/* Met en surbrillance les éléments recherchés dans les noms. */
static void update_symbol_name_in_tree_view(const GSymbolsPanel *, GtkTreeStore *, const GBinSymbol *, const regmatch_t *);



/* ------------------------- FILTRAGE DES SYMBOLES PRESENTS ------------------------- */


/* Démarre l'actualisation du filtrage des symboles. */
static void on_symbols_filter_changed(GtkSearchEntry *, GSymbolsPanel *);

/* Exécute un nouveau filtrage des symboles affichés. */
static void do_filtering_on_symbols(const GSymbolsPanel *, GtkStatusStack *, activity_id_t, symbols_update_data *);



/* ---------------------- MECANISMES DE MISE A JOUR DE PANNEAU ---------------------- */


/* Données utiles à la mise à jour */
struct _symbols_update_data
{
    size_t count;                           /* Qté d'inscriptions réalisées*/

    regex_t *filter;                        /* Filtre appliqué ou NULL     */

    char **expanded;                        /* Chemins des noeuds ouverts  */
    size_t ecount;                          /* Nombre de ces chemins       */
    size_t eallocated;                      /* Espace alloué effectivement */

};


#define EXPAND_ALLOC_RANGE 10


/* Détermine si un nom de symbole doit être filtré ou non. */
static bool is_symbol_matching(const symbols_update_data *, const GBinSymbol *, regmatch_t *);

/* Prépare une opération de mise à jour de panneau. */
static bool g_symbols_panel_setup(const GSymbolsPanel *, unsigned int, size_t *, symbols_update_data **, char **);

/* Bascule l'affichage d'un panneau avant mise à jour. */
static void g_symbols_panel_introduce(const GSymbolsPanel *, unsigned int, symbols_update_data *);

/* Réalise une opération de mise à jour de panneau. */
static void g_symbols_panel_process(const GSymbolsPanel *, unsigned int, GtkStatusStack *, activity_id_t, symbols_update_data *);

/* Bascule l'affichage d'un panneau après mise à jour. */
static void g_symbols_panel_conclude(GSymbolsPanel *, unsigned int, symbols_update_data *);

/* Supprime les données dynamiques utilisées à la mise à jour. */
static void g_symbols_panel_clean_data(const GUpdatablePanel *, unsigned int, symbols_update_data *);



/* ---------------------------------------------------------------------------------- */
/*                            PARTIE PRINCIPALE DU PANNEAU                            */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un panneau d'affichage des symboles. */
G_DEFINE_TYPE_WITH_CODE(GSymbolsPanel, g_symbols_panel, G_TYPE_PANEL_ITEM,
                        G_IMPLEMENT_INTERFACE(G_TYPE_UPDATABLE_PANEL, g_symbols_panel_updatable_interface_init));


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des panneaux d'affichage des symboles.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_symbols_panel_class_init(GSymbolsPanelClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GEditorItemClass *item;                 /* Encore une autre vision...  */
    GPanelItemClass *panel;                 /* Version parente de la classe*/
    gchar *filename;                        /* Chemin d'accès à utiliser   */

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_symbols_panel_dispose;
    object->finalize = (GObjectFinalizeFunc)g_symbols_panel_finalize;

    item = G_EDITOR_ITEM_CLASS(class);

    item->get_key = (get_item_key_fc)g_symbols_panel_class_get_key;

    item->change_content = (change_item_content_fc)change_symbols_panel_current_content;

    panel = G_PANEL_ITEM_CLASS(class);

    panel->get_path = (get_panel_path_fc)g_symbols_panel_class_get_path;
    panel->get_bindings = (get_panel_bindings_fc)g_symbols_panel_class_get_key_bindings;

    panel->gid = setup_tiny_global_work_group(1);

    filename = find_pixmap_file("symbol_routine_classic.png");
    assert(filename != NULL);

    class->routine_img = cairo_image_surface_create_from_png(filename);

    g_free(filename);

    filename = find_pixmap_file("symbol_object_classic.png");
    assert(filename != NULL);

    class->object_img = cairo_image_surface_create_from_png(filename);

    g_free(filename);

    filename = find_pixmap_file("symbol_package.png");
    assert(filename != NULL);

    class->package_img = cairo_image_surface_create_from_png(filename);

    g_free(filename);

    filename = find_pixmap_file("symbol_class_classic.png");
    assert(filename != NULL);

    class->class_img = cairo_image_surface_create_from_png(filename);

    g_free(filename);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance de panneau d'affichage des symboles. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_symbols_panel_init(GSymbolsPanel *panel)
{
    GPanelItem *pitem;                      /* Version parente du panneau  */
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeModelFilter *filter;             /* Filtre pour l'arborescence  */
    GtkTreeView *treeview;                  /* Affichage de la liste       */
    GtkCellRenderer *renderer;              /* Moteur de rendu de colonne  */
    GtkTreeViewColumn *column;              /* Colonne de la liste         */

    /* Eléments de base */

    pitem = G_PANEL_ITEM(panel);

    pitem->widget = G_NAMED_WIDGET(gtk_built_named_widget_new_for_panel(_("Symbols"),
                                                                        _("Binary symbols"),
                                                                        PANEL_SYMBOLS_ID));

    /* Représentation graphique */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(pitem->widget));

    filter = GTK_TREE_MODEL_FILTER(gtk_builder_get_object(builder, "filter"));
    gtk_tree_model_filter_set_visible_column(filter, SBC_MATCHED);

    /* Cellules d'affichage */

    treeview = GTK_TREE_VIEW(gtk_builder_get_object(builder, "treeview"));

    column = gtk_tree_view_column_new();

    renderer = gtk_cell_renderer_pixbuf_new();
    gtk_tree_view_column_pack_start(column, renderer, FALSE);
    gtk_tree_view_column_add_attribute(column, renderer, "surface", SBC_PICTURE);

    renderer = gtk_cell_renderer_text_new();
    gtk_tree_view_column_pack_start(column, renderer, TRUE);
    gtk_tree_view_column_add_attribute(column, renderer, "markup", SBC_NAME);
    gtk_tree_view_column_set_sort_column_id(column, SBC_NAME);

    gtk_tree_view_column_set_title(column, _("Name"));
    gtk_tree_view_append_column(GTK_TREE_VIEW(treeview), column);

    renderer = gtk_cell_renderer_text_new();
    column = gtk_tree_view_column_new_with_attributes(_("Address"), renderer,
                                                      "text", SBC_ADDRESS,
                                                      NULL);
    gtk_tree_view_column_set_sort_column_id(column, SBC_ADDRESS);
    gtk_tree_view_append_column(GTK_TREE_VIEW(treeview), column);

    renderer = gtk_cell_renderer_text_new();
    column = gtk_tree_view_column_new_with_attributes(_("Section"), renderer,
                                                      "text", SBC_SECTION,
                                                      NULL);
    gtk_tree_view_column_set_sort_column_id(column, SBC_SECTION);
    gtk_tree_view_append_column(GTK_TREE_VIEW(treeview), column);

    /* Connexion des signaux */

    gtk_builder_add_callback_symbols(builder,
                                     BUILDER_CALLBACK(on_symbols_list_display_toggle),
                                     BUILDER_CALLBACK(on_symbols_tree_display_toggle),
                                     BUILDER_CALLBACK(reorganize_symbols_tree_view),
                                     BUILDER_CALLBACK(on_symbols_filter_changed),
                                     BUILDER_CALLBACK(on_symbols_selection_change),
                                     BUILDER_CALLBACK(track_focus_change_in_text_area),
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

static void g_symbols_panel_updatable_interface_init(GUpdatablePanelInterface *iface)
{
    iface->setup = (setup_updatable_cb)g_symbols_panel_setup;
    iface->get_group = (get_updatable_group_cb)g_panel_item_get_group;
    iface->introduce = (introduce_updatable_cb)g_symbols_panel_introduce;
    iface->process = (process_updatable_cb)g_symbols_panel_process;
    iface->conclude = (conclude_updatable_cb)g_symbols_panel_conclude;
    iface->clean = (clean_updatable_data_cb)g_symbols_panel_clean_data;

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

static void g_symbols_panel_dispose(GSymbolsPanel *panel)
{
    if (panel->binary != NULL)
        g_object_unref(G_OBJECT(panel->binary));

    G_OBJECT_CLASS(g_symbols_panel_parent_class)->dispose(G_OBJECT(panel));

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

static void g_symbols_panel_finalize(GSymbolsPanel *panel)
{
    G_OBJECT_CLASS(g_symbols_panel_parent_class)->finalize(G_OBJECT(panel));

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

static char *g_symbols_panel_class_get_key(const GSymbolsPanelClass *class)
{
    char *result;                           /* Description à renvoyer      */

    result = strdup(PANEL_SYMBOLS_ID);

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

static char *g_symbols_panel_class_get_path(const GSymbolsPanelClass *class)
{
    char *result;                           /* Emplacement à retourner     */

    result = strdup("MEN");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à consulter.                                  *
*                                                                             *
*  Description : Indique la définition d'un éventuel raccourci clavier.       *
*                                                                             *
*  Retour      : Description d'un raccourci ou NULL si aucun de défini.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_symbols_panel_class_get_key_bindings(const GSymbolsPanelClass *class)
{
    char *result;                           /* Emplacement à retourner     */

    result = strdup("<Shift>F3");

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

GPanelItem *g_symbols_panel_new(void)
{
    GPanelItem *result;                     /* Structure à retourner       */

    result = g_object_new(G_TYPE_SYMBOLS_PANEL, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : button = bouton de la barre activé.                          *
*                panel  = structure contenant les informations maîtresses.    *
*                                                                             *
*  Description : Bascule d'affichage des symboles en liste.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_symbols_list_display_toggle(GtkToggleToolButton *button, GSymbolsPanel *panel)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkWidget *other;                       /* Autre bouton de la barre    */
    GLoadedContent *content;                /* Autre version du binaire    */

    if (gtk_toggle_tool_button_get_active(button))
    {
        /* Accès aux boutons complémentaires */

        builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

        other = GTK_WIDGET(gtk_builder_get_object(builder, "collapse"));
        gtk_widget_set_sensitive(other, FALSE);

        other = GTK_WIDGET(gtk_builder_get_object(builder, "expand"));
        gtk_widget_set_sensitive(other, FALSE);

        other = GTK_WIDGET(gtk_builder_get_object(builder, "classes"));
        gtk_widget_set_sensitive(other, FALSE);

        g_object_unref(G_OBJECT(builder));

        /* Actualisation de l'affichage */

        if (panel->binary != NULL)
        {
            content = G_LOADED_CONTENT(panel->binary);

            g_object_ref(G_OBJECT(content));
            change_symbols_panel_current_content(panel, content, content);
            g_object_unref(G_OBJECT(content));

        }

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : button = bouton de la barre activé.                          *
*                panel  = structure contenant les informations maîtresses.    *
*                                                                             *
*  Description : Bascule l'affichage des symboles en arborescence.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_symbols_tree_display_toggle(GtkToggleToolButton *button, GSymbolsPanel *panel)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkWidget *other;                       /* Autre bouton de la barre    */
    GLoadedContent *content;                /* Autre version du binaire    */

    if (gtk_toggle_tool_button_get_active(button))
    {
        /* Accès aux boutons complémentaires */

        builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

        other = GTK_WIDGET(gtk_builder_get_object(builder, "collapse"));
        gtk_widget_set_sensitive(other, TRUE);

        other = GTK_WIDGET(gtk_builder_get_object(builder, "expand"));
        gtk_widget_set_sensitive(other, TRUE);

        other = GTK_WIDGET(gtk_builder_get_object(builder, "classes"));
        gtk_widget_set_sensitive(other, TRUE);

        g_object_unref(G_OBJECT(builder));

        /* Actualisation de l'affichage */

        if (panel->binary != NULL)
        {
            content = G_LOADED_CONTENT(panel->binary);

            g_object_ref(G_OBJECT(content));
            change_symbols_panel_current_content(panel, content, content);
            g_object_unref(G_OBJECT(content));

        }

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : selection = sélection modifiée.                              *
*                unused    = adresse non utilisée ici.                        *
*                                                                             *
*  Description : Réagit au changement de sélection des symboles.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_symbols_selection_change(GtkTreeSelection *selection, gpointer unused)
{
    GtkTreeIter iter;                       /* Point de sélection          */
    GtkTreeModel *model;                    /* Modèle de gestion           */
    GBinSymbol *symbol;                     /* Symbole à traiter           */
    const mrange_t *range;                  /* Couverture dudit symbole    */
    GLoadedPanel *panel;                    /* Afficheur effectif de code  */

    if (gtk_tree_selection_get_selected(selection, &model, &iter))
    {
        gtk_tree_model_get(model, &iter, SBC_SYMBOL, &symbol, -1);

        if (symbol != NULL)
        {
            range = g_binary_symbol_get_range(symbol);

            panel = get_current_view();

            if (GTK_IS_DISPLAY_PANEL(panel))
                gtk_display_panel_request_move(GTK_DISPLAY_PANEL(panel), get_mrange_addr(range));

            g_object_unref(G_OBJECT(panel));

            g_object_unref(G_OBJECT(symbol));

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

static void change_symbols_panel_current_content(GSymbolsPanel *panel, GLoadedContent *old, GLoadedContent *new)
{
    GLoadedBinary *binary;                  /* Autre version de l'instance */
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeStore *store;                    /* Modèle de gestion           */
    GBinFormat *format;                     /* Format du binaire           */
    GCompDemangler *demangler;              /* Décodeur privilégié associé */
    GtkToggleToolButton *button;            /* Bouton à encadrer           */

    if (G_IS_LOADED_BINARY(new))
        binary = G_LOADED_BINARY(new);
    else
        binary = NULL;

    /* Basculement du binaire utilisé */

    if (panel->binary != NULL)
        g_object_unref(G_OBJECT(panel->binary));

    if (panel->sep != NULL)
    {
        free(panel->sep);
        panel->sep = NULL;
    }

    panel->binary = binary;

    if (panel->binary != NULL)
        g_object_ref(G_OBJECT(panel->binary));

    /* Réinitialisation */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    store = GTK_TREE_STORE(gtk_builder_get_object(builder, "store"));

    gtk_tree_store_clear(store);

    /* Si le panneau actif représente un binaire, actualisation de l'affichage */

    if (binary != NULL)
    {
        format = G_BIN_FORMAT(g_loaded_binary_get_format(binary));

        demangler = g_binary_format_get_demangler(format);

        if (demangler == NULL)
            panel->sep = NULL;

        else
        {
            panel->sep = strdup(g_compiler_demangler_get_ns_separator(demangler));
            g_object_unref(G_OBJECT(demangler));
        }

        g_object_unref(G_OBJECT(format));

        if (panel->sep == NULL)
        {
            button = GTK_TOGGLE_TOOL_BUTTON(gtk_builder_get_object(builder, "tree_display"));
            gtk_widget_set_sensitive(GTK_WIDGET(button), FALSE);

            button = GTK_TOGGLE_TOOL_BUTTON(gtk_builder_get_object(builder, "list_display"));
            gtk_toggle_tool_button_set_active(button, TRUE);

        }
        else
        {
            button = GTK_TOGGLE_TOOL_BUTTON(gtk_builder_get_object(builder, "tree_display"));

            if (!gtk_widget_get_sensitive(GTK_WIDGET(button)))
            {
                gtk_widget_set_sensitive(GTK_WIDGET(button), TRUE);
                gtk_toggle_tool_button_set_active(button, TRUE);
            }

        }

        run_panel_update(G_UPDATABLE_PANEL(panel), PUI_0);

    }

    g_object_unref(G_OBJECT(builder));

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

static void reload_symbols_panel_content(const GSymbolsPanel *panel, GtkStatusStack *status, activity_id_t id, symbols_update_data *data)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkToggleToolButton *button;            /* Mode de représentation      */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    button = GTK_TOGGLE_TOOL_BUTTON(gtk_builder_get_object(builder, "list_display"));

    if (gtk_toggle_tool_button_get_active(button))
        reload_symbols_for_new_list_view(panel, status, id, data);

    else
        reload_symbols_for_new_tree_view(panel, status, id, data);

    g_object_unref(G_OBJECT(builder));

}



/* ---------------------------------------------------------------------------------- */
/*                           AFFICHAGE A L'AIDE D'UNE LISTE                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau à mettre à jour.                             *
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

static void reload_symbols_for_new_list_view(const GSymbolsPanel *panel, GtkStatusStack *status, activity_id_t id, symbols_update_data *data)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeStore *store;                    /* Modèle de gestion           */
    GExeFormat *format;                     /* Format associé au binaire   */
    GArchProcessor *proc;                   /* Architecture utilisée       */
    bool has_virt;                          /* Concept de virtuel présent ?*/
    sym_iter_t *siter;                      /* Parcours des symboles       */
    GBinSymbol *symbol;                     /* Symbole manipulé            */
    cairo_surface_t *icon;                  /* Image associée au symbole   */
    regmatch_t match;                       /* Récupération des trouvailles*/
    bool matched;                           /* Correspondance de sélection */
    char *original;                         /* Etiquette brute d'origine   */
    char *name;                             /* Etiquette mise en relief    */
    const vmpa2t *addr;                     /* Localisation d'un symbole   */
    VMPA_BUFFER(virt);                      /* Version humainement lisible */
    GtkTreeIter iter;                       /* Point d'insertion           */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    store = GTK_TREE_STORE(gtk_builder_get_object(builder, "store"));

    format = g_loaded_binary_get_format(panel->binary);

    proc = g_loaded_binary_get_processor(panel->binary);
    has_virt = g_arch_processor_has_virtual_space(proc);
    g_object_unref(G_OBJECT(proc));

    siter = create_symbol_iterator(G_BIN_FORMAT(format), 0);

    for (symbol = get_symbol_iterator_current(siter);
         symbol != NULL;
         symbol = get_symbol_iterator_next(siter))
    {
        switch (g_binary_symbol_get_stype(symbol))
        {
            case STP_ROUTINE:
            case STP_ENTRY_POINT:
                icon = G_SYMBOLS_PANEL_GET_CLASS(panel)->routine_img;
                break;
            case STP_OBJECT:
                icon = G_SYMBOLS_PANEL_GET_CLASS(panel)->object_img;
                break;
            default:
                icon = NULL;
                break;
        }

        if (icon == NULL)
            goto rsfnlv_next;

        matched = is_symbol_matching(data, symbol, &match);

        original = g_binary_symbol_get_label(symbol);

        if (matched)
            name = build_highlighted_name(original, &match, 0);
        else
            name = NULL;

        addr = get_mrange_addr(g_binary_symbol_get_range(symbol));

        if (has_virt)
            vmpa2_virt_to_string(addr, MDS_UNDEFINED, virt, NULL);
        else
            vmpa2_phys_to_string(addr, MDS_UNDEFINED, virt, NULL);

        gtk_tree_store_append(store, &iter, NULL);
        gtk_tree_store_set(store, &iter,
                           SBC_SYMBOL, symbol,
                           SBC_PICTURE, icon,
                           SBC_NAME, name,
                           SBC_ORIGINAL, original,
                           SBC_ADDRESS, virt,
                           SBC_MATCHED, false,
                           SBC_MATCH_POINTS, 0,
                           -1);

        if (matched)
            update_node_visibility(store, &iter, SBC_MATCHED, true);

        data->count++;

        if (name != NULL)
            free(name);

        free(original);

 rsfnlv_next:

        g_object_unref(G_OBJECT(symbol));

        gtk_status_stack_update_activity_value(status, id, 1);

    }

    delete_symbol_iterator(siter);

    g_object_unref(G_OBJECT(format));

    g_object_unref(G_OBJECT(builder));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : store = gestionnaire de données pour une arborescence.       *
*                iter  = position des données traitées.                       *
*                match = correspondance avec un objet recherché.              *
*                                                                             *
*  Description : Met en surbrillance les éléments recherchés dans les noms.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void update_symbol_name_in_list_view(GtkTreeStore *store, GtkTreeIter *iter, const regmatch_t *match)
{
    GtkTreeModel *model;                    /* Autre vision du gestionnaire*/
    char *original;                         /* Etiquette brute d'origine   */
    char *name;                             /* Etiquette mise en relief    */

    model = GTK_TREE_MODEL(store);

    gtk_tree_model_get(model, iter, SBC_ORIGINAL, &original, -1);

    name = build_highlighted_name(original, match, 0);

    gtk_tree_store_set(store, iter, SBC_NAME, name, -1);

    free(original);
    free(name);

}



/* ---------------------------------------------------------------------------------- */
/*                            AFFICHAGE SOUS FORME D'ARBRE                            */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : panel  = panneau en cours de mise à jour.                    *
*                parent = point d'insertion parent à retrouver. [OUT]         *
*                raw    = nom du noeud ciblé.                                 *
*                match  = portion de texte à mettre en évidence.              *
*                start  = position du texte brute dans l'étiquette complète.  *
*                                                                             *
*  Description : S'assure qu'un noeud donné existe bien.                      *
*                                                                             *
*  Retour      : Point d'insertion prochain.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GtkTreeIter ensure_symbol_node_exist(const GSymbolsPanel *panel, GtkTreeIter *parent, const char *raw, const regmatch_t *match, size_t start)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeStore *store;                    /* Gestionnaire de données     */
    GtkTreeModel *model;                    /* Autre vision du gestionnaire*/
    bool found;                             /* Bilan des recherches        */
    GtkTreeIter iter;                       /* Boucle de parcours          */
    gchar *string;                          /* Chaîne sélectionnée         */
    char *name;                             /* Etiquette mise en relief    */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    store = GTK_TREE_STORE(gtk_builder_get_object(builder, "store"));

    model = GTK_TREE_MODEL(store);

    found = false;

    if (gtk_tree_model_iter_children(model, &iter, parent))
        do
        {
            gtk_tree_model_get(model, &iter, SBC_ORIGINAL, &string, -1);
            found = (strcmp(string, raw) == 0);
            g_free(string);

            if (found) break;

        }
        while (gtk_tree_model_iter_next(model, &iter));

    if (!found) 
    {
        name = build_highlighted_name(raw, match, start);

        gtk_tree_store_append(store, &iter, parent);
        gtk_tree_store_set(store, &iter,
                           SBC_PICTURE, G_SYMBOLS_PANEL_GET_CLASS(panel)->package_img,
                           SBC_NAME, name,
                           SBC_ORIGINAL, raw,
                           SBC_MATCHED, false,
                           SBC_MATCH_POINTS, 0,
                           -1);

        free(name);

    }

    g_object_unref(G_OBJECT(builder));

    return iter;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel  = panneau en cours de mise à jour.                    *
*                symbol = routine ou objet à intégrer.                        *
*                parent = point d'insertion parent à constituer. [OUT]        *
*                match = portion de texte à mettre en évidence.               *
*                last   = position du dernier élément du nom de symbole. [OUT]*
*                                                                             *
*  Description : Détermine le point d'insertion parent d'une routine.         *
*                                                                             *
*  Retour      : true si le point n'est pas la racine, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool find_parent_for_symbol(const GSymbolsPanel *panel, const GBinSymbol *symbol, GtkTreeIter *parent, const regmatch_t *match, size_t *last)
{
    bool result;                            /* Bilan à retourner           */
    char *label;                            /* Etiquette modifiable        */
    char *start;                            /* Début de boucle de parcours */
    char *token;                            /* Partie de texte isolée      */ 
    char *next;                             /* Prochaine partie à traiter  */

    result = false;

    *last = 0;

    label = g_binary_symbol_get_label(symbol);
    if (label == NULL) return false;

    for (start = label, token = strtok_w(&start, panel->sep); ; token = next)
    {
        next = strtok_w(&start, panel->sep);
        if (next == NULL)
        {
            *last = (token - label);
            break;
        }

        *parent = ensure_symbol_node_exist(panel, (token == label ? NULL : parent), token, match, token - label);

        result = true;

    }

    free(label);

    return result;

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

static void reload_symbols_for_new_tree_view(const GSymbolsPanel *panel, GtkStatusStack *status, activity_id_t id, symbols_update_data *data)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeStore *store;                    /* Modèle de gestion           */
    GExeFormat *format;                     /* Format associé au binaire   */
    GArchProcessor *proc;                   /* Architecture utilisée       */
    bool has_virt;                          /* Concept de virtuel présent ?*/
    sym_iter_t *siter;                      /* Parcours des symboles       */
    GBinSymbol *symbol;                     /* Symbole manipulé            */
    cairo_surface_t *icon;                  /* Image associée au symbole   */
    regmatch_t match;                       /* Récupération des trouvailles*/
    bool matched;                           /* Correspondance de sélection */
    GtkTreeIter parent;                     /* Point d'insertion parent    */
    size_t last;                            /* Position du dernier élément */
    char *original;                         /* Etiquette brute d'origine   */
    char *name;                             /* Etiquette mise en relief    */
    const vmpa2t *addr;                     /* Localisation d'un symbole   */
    char virt[VMPA_MAX_LEN];                /* Version humainement lisible */
    GtkTreeIter iter;                       /* Point d'insertion           */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    store = GTK_TREE_STORE(gtk_builder_get_object(builder, "store"));

    format = g_loaded_binary_get_format(panel->binary);

    proc = g_loaded_binary_get_processor(panel->binary);
    has_virt = g_arch_processor_has_virtual_space(proc);
    g_object_unref(G_OBJECT(proc));

    siter = create_symbol_iterator(G_BIN_FORMAT(format), 0);

    for (symbol = get_symbol_iterator_current(siter);
         symbol != NULL;
         symbol = get_symbol_iterator_next(siter))
    {
        switch (g_binary_symbol_get_stype(symbol))
        {
            case STP_ROUTINE:
            case STP_ENTRY_POINT:
                icon = G_SYMBOLS_PANEL_GET_CLASS(panel)->routine_img;
                break;
            case STP_OBJECT:
                icon = G_SYMBOLS_PANEL_GET_CLASS(panel)->object_img;
                break;
            default:
                icon = NULL;
                break;
        }

        if (icon == NULL)
            goto rsfntv_next;

        matched = is_symbol_matching(data, symbol, &match);

        if (find_parent_for_symbol(panel, symbol, &parent, &match, &last))
        {
            gtk_tree_store_set(store, &parent,
                               SBC_PICTURE, G_SYMBOLS_PANEL_GET_CLASS(panel)->class_img,
                               SBC_EXPAND, TRUE,
                               -1);

            gtk_tree_store_append(store, &iter, &parent);

        }
        else
            gtk_tree_store_append(store, &iter, NULL);

        original = g_binary_symbol_get_label(symbol);

        if (matched)
            name = build_highlighted_name(original + last, &match, last);
        else
            name = NULL;

        addr = get_mrange_addr(g_binary_symbol_get_range(symbol));

        if (has_virt)
            vmpa2_virt_to_string(addr, MDS_UNDEFINED, virt, NULL);
        else
            vmpa2_phys_to_string(addr, MDS_UNDEFINED, virt, NULL);

        gtk_tree_store_set(store, &iter,
                           SBC_SYMBOL, symbol,
                           SBC_PICTURE, icon,
                           SBC_NAME, name,
                           SBC_ORIGINAL, original + last,
                           SBC_ADDRESS, virt,
                           SBC_MATCHED, false,
                           SBC_MATCH_POINTS, 0,
                           -1);

        if (matched)
            update_node_visibility(store, &iter, SBC_MATCHED, true);

        data->count++;

        if (name != NULL)
            free(name);

        free(original);

 rsfntv_next:

        g_object_unref(G_OBJECT(symbol));

        gtk_status_stack_update_activity_value(status, id, 1);

    }

    delete_symbol_iterator(siter);

    g_object_unref(G_OBJECT(format));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : button = bouton concerné par l'action.                       *
*                panel  = panneau à mettre à jour.                            *
*                                                                             *
*  Description : Réagit à une nouvelle demande de réorganisation.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void reorganize_symbols_tree_view(GtkToolButton *button, const GSymbolsPanel *panel)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeView *treeview;                  /* Arborescence graphique      */
    GtkToolButton *ref_collapse;            /* Bouton de référence #1      */
    GtkToolButton *ref_expand;              /* Bouton de référence #2      */
    GtkTreeStore *store;                    /* Modèle de gestion           */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    treeview = GTK_TREE_VIEW(gtk_builder_get_object(builder, "treeview"));

    ref_collapse = GTK_TOOL_BUTTON(gtk_builder_get_object(builder, "collapse"));
    ref_expand = GTK_TOOL_BUTTON(gtk_builder_get_object(builder, "expand"));

    if (button == ref_collapse)
        gtk_tree_view_collapse_all(treeview);

    else if (button == ref_expand)
        gtk_tree_view_expand_all(treeview);

    else
    {
        store = GTK_TREE_STORE(gtk_builder_get_object(builder, "store"));

        gtk_tree_model_foreach(GTK_TREE_MODEL(store),
                               (GtkTreeModelForeachFunc)show_all_classes_in_tree_view,
                               treeview);

    }

    g_object_unref(G_OBJECT(builder));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : model    = modèle de gestion des éléments.                   *
*                path     = chemin d'accès à l'élément courant.               *
*                iter     = itérateur courant.                                *
*                treeview = arborescence à manipuler ici.                     *
*                                                                             *
*  Description : Fait en sorte que toutes les classes soient affichées.       *
*                                                                             *
*  Retour      : FALSE pour continuer le parcours.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean show_all_classes_in_tree_view(GtkTreeModel *model, GtkTreePath *path, GtkTreeIter *iter, GtkTreeView *treeview)
{
    gboolean expand;                        /* Besoin en intervention      */
    GtkTreePath *tmp;                       /* Copie pour modification     */

    gtk_tree_model_get(model, iter, SBC_EXPAND, &expand, -1);

    if (expand)
    {
        tmp = gtk_tree_path_copy(path);

        if (gtk_tree_path_up(tmp))
            gtk_tree_view_expand_to_path(treeview, tmp);

        gtk_tree_path_free(tmp);

    }

    return FALSE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : store  = gestionnaire de données en arborescence.            *
*                parent = point d'insertion parent à retrouver. [OUT]         *
*                raw    = nom du noeud ciblé.                                 *
*                match  = portion de texte à mettre en évidence.              *
*                start  = position du texte brute dans l'étiquette complète.  *
*                                                                             *
*  Description : Actualise une partie d'un nom de symbole éclaté en noeuds.   *
*                                                                             *
*  Retour      : Point de mise à jour prochain.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GtkTreeIter update_symbol_partial_name_in_tree_view(GtkTreeStore *store, GtkTreeIter *parent, const char *raw, const regmatch_t *match, size_t start)
{
    GtkTreeModel *model;                    /* Autre vision du gestionnaire*/
    bool found;                             /* Bilan des recherches        */
    GtkTreeIter iter;                       /* Boucle de parcours          */
    gchar *string;                          /* Chaîne sélectionnée         */
    char *name;                             /* Etiquette mise en relief    */

    model = GTK_TREE_MODEL(store);

    found = false;

    if (gtk_tree_model_iter_children(model, &iter, parent))
        do
        {
            gtk_tree_model_get(model, &iter, SBC_ORIGINAL, &string, -1);

            found = (strcmp(string, raw) == 0);
            g_free(string);

            if (found) break;

        }
        while (gtk_tree_model_iter_next(model, &iter));

    assert(found);

    name = build_highlighted_name(raw, match, start);

    gtk_tree_store_set(store, &iter, SBC_NAME, name, -1);

    free(name);

    return iter;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel  = panneau à mettre à jour.                            *
*                store  = gestionnaire de données en arborescence.            *
*                symbol = routine ou objet à intégrer.                        *
*                match  = portion de texte à mettre en évidence.              *
*                                                                             *
*  Description : Met en surbrillance les éléments recherchés dans les noms.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void update_symbol_name_in_tree_view(const GSymbolsPanel *panel, GtkTreeStore *store, const GBinSymbol *symbol, const regmatch_t *match)
{
    char *label;                            /* Etiquette modifiable        */
    GtkTreeIter parent;                     /* Point d'analyse courant     */
    char *start;                            /* Début de boucle de parcours */
    char *token;                            /* Partie de texte isolée      */

    label = g_binary_symbol_get_label(symbol);

    if (label != NULL)
    {
        for (start = label, token = strtok_w(&start, panel->sep);
             token != NULL;
             token = strtok_w(&start, panel->sep))
        {
            parent = update_symbol_partial_name_in_tree_view(store, (token == label ? NULL : &parent),
                                                             token, match, token - label);
        }

        free(label);

    }

}



/* ---------------------------------------------------------------------------------- */
/*                           FILTRAGE DES SYMBOLES PRESENTS                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : entry = entrée de texte contenant le filtre brut.            *
*                panel = panneau assurant l'affichage des symboles.           *
*                                                                             *
*  Description : Démarre l'actualisation du filtrage des symboles.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_symbols_filter_changed(GtkSearchEntry *entry, GSymbolsPanel *panel)
{
    update_regex_on_search_entry_changed(entry, &G_PANEL_ITEM(panel)->filter);

    run_panel_update(G_UPDATABLE_PANEL(panel), PUI_1);

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

static void do_filtering_on_symbols(const GSymbolsPanel *panel, GtkStatusStack *status, activity_id_t id, symbols_update_data *data)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeStore *store;                    /* Modèle de gestion           */
    GtkToggleToolButton *button;            /* Mode de représentation      */
    gboolean as_list;                       /* Choix dudit mode            */


    gboolean filter_symbol_panel_iter(GtkTreeModel *model, GtkTreePath *path, GtkTreeIter *iter, gboolean *as_list)
    {
        GBinSymbol *symbol;                 /* Symbole manipulé            */
        regmatch_t match;                   /* Récupération des trouvailles*/
        bool matched;                       /* Correspondance de sélection */
        gboolean shown;                     /* Visibilité actuelle         */

        gtk_tree_model_get(model, iter, SBC_SYMBOL, &symbol, -1);

        if (symbol != NULL)
        {
            matched = is_symbol_matching(data, symbol, &match);

            if (matched)
            {
                if (*as_list)
                    update_symbol_name_in_list_view(store, iter, &match);
                else
                    update_symbol_name_in_tree_view(panel, store, symbol, &match);
            }

            gtk_tree_model_get(model, iter, SBC_MATCHED, &shown, -1);

            if (!matched)
            {
                if (shown)
                    update_node_visibility(store, iter, SBC_MATCHED, false);
            }

            else
            {
                if (!shown)
                    update_node_visibility(store, iter, SBC_MATCHED, true);
            }

            g_object_unref(G_OBJECT(symbol));

            gtk_status_stack_update_activity_value(status, id, 1);

        }

        return FALSE;

    }


    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    store = GTK_TREE_STORE(gtk_builder_get_object(builder, "store"));
    button = GTK_TOGGLE_TOOL_BUTTON(gtk_builder_get_object(builder, "list_display"));

    as_list = gtk_toggle_tool_button_get_active(button);

    gtk_tree_model_foreach(GTK_TREE_MODEL(store), (GtkTreeModelForeachFunc)filter_symbol_panel_iter, &as_list);

    g_object_unref(G_OBJECT(builder));

}



/* ---------------------------------------------------------------------------------- */
/*                        MECANISMES DE MISE A JOUR DE PANNEAU                        */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : data   = données complémentaire à manipuler.                 *
*                symbol = symbole à traiter.                                  *
*                match  = récupération des trouvailles. [OUT]                 *
*                                                                             *
*  Description : Détermine si un nom de symbole doit être filtré ou non.      *
*                                                                             *
*  Retour      : true si le symbol ne doit pas être affiché, false sinon.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool is_symbol_matching(const symbols_update_data *data, const GBinSymbol *symbol, regmatch_t *match)
{
    bool result;                            /* Bilan à retourner           */
#ifndef NDEBUG
    SymbolType type;                        /* Type associé au symbole     */
#endif
    char *label;                            /* Etiquette à analyser        */

#ifndef NDEBUG

    type = g_binary_symbol_get_stype(symbol);

    assert(type == STP_ROUTINE || type == STP_ENTRY_POINT || type == STP_OBJECT);

#endif

    label = g_binary_symbol_get_label(symbol);

    if (label == NULL)
        result = false;

    else
    {
        result = is_content_matching(data->filter, label, match);
        free(label);
    }

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
*  Retour      : Description du message d'information.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_symbols_panel_setup(const GSymbolsPanel *panel, unsigned int uid, size_t *count, symbols_update_data **data, char **msg)
{
    bool result;                            /* Bilan à retourner           */
    GBinFormat *format;                     /* Format du binaire           */
#ifndef NDEBUG
    int ret;                                /* Bilan de mise en place      */
#endif
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeView *treeview;                  /* Arborescence graphique      */

    result = true;

    *data = malloc(sizeof(symbols_update_data));

    switch (uid)
    {
        case PUI_0:

            format = G_BIN_FORMAT(g_loaded_binary_get_format(panel->binary));

            g_binary_format_lock_symbols_rd(format);
            *count = g_binary_format_count_symbols(format);
            g_binary_format_unlock_symbols_rd(format);

            g_object_unref(G_OBJECT(format));

            (*data)->count = 0;

            *msg = strdup(_("Loading symbols registered for the binary format..."));

            break;

        case PUI_1:

            *count = panel->count;
            (*data)->count = panel->count;

            *msg = strdup(_("Filtering symbols registered for the binary format..."));

            break;

        default:    /* Pour GCC... */
            assert(false);
            result = false;
            break;

    }

    if (G_PANEL_ITEM(panel)->filter != NULL)
    {
        (*data)->filter = (regex_t *)malloc(sizeof(regex_t));

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

    void keep_track_of_expanded(GtkTreeView *tv, GtkTreePath *path, symbols_update_data *sud)
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

static void g_symbols_panel_introduce(const GSymbolsPanel *panel, unsigned int uid, symbols_update_data *data)
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

static void g_symbols_panel_process(const GSymbolsPanel *panel, unsigned int uid, GtkStatusStack *status, activity_id_t id, symbols_update_data *data)
{
    switch (uid)
    {
        case PUI_0:
            reload_symbols_panel_content(panel, status, id, data);
            break;

        case PUI_1:
            do_filtering_on_symbols(panel, status, id, data);
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

static void g_symbols_panel_conclude(GSymbolsPanel *panel, unsigned int uid, symbols_update_data *data)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeView *treeview;                  /* Arborescence graphique      */
    GtkTreeModel *model;                    /* Source de données associée  */
    size_t i;                               /* Boucle de parcours          */
    GtkTreePath *path;                      /* Chemin d'accès à un noeud   */
    GtkToggleToolButton *button;            /* Mode de représentation      */

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

    /* Réorganisation des symboles ? */

    button = GTK_TOGGLE_TOOL_BUTTON(gtk_builder_get_object(builder, "list_display"));

    if (!gtk_toggle_tool_button_get_active(button))
        reorganize_symbols_tree_view(NULL, panel);

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

static void g_symbols_panel_clean_data(const GUpdatablePanel *panel, unsigned int uid, symbols_update_data *data)
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
