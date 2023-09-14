
/* Chrysalide - Outil d'analyse de fichiers binaires
 * strings.c - panneau d'affichage des chaînes de caractères
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


#include "strings.h"


#include <assert.h>
#include <inttypes.h>
#include <malloc.h>
#include <string.h>


#include "updating-int.h"
#include "../panel-int.h"
#include "../core/global.h"
#include "../dialogs/gotox.h"
#include "../../common/extstr.h"
#include "../../core/params.h"
#include "../../core/queue.h"
#include "../../format/known.h"
#include "../../format/format.h"
#include "../../format/strsym.h"
#include "../../format/symiter.h"
#include "../../gtkext/easygtk.h"
#include "../../gtkext/gtkdisplaypanel.h"
#include "../../gtkext/gtkdockable-int.h"
#include "../../gtkext/named.h"
#include "../../gtkext/tmgt.h"



/* -------------------------- PARTIE PRINCIPALE DU PANNEAU -------------------------- */


/* Panneau d'aperçu de graphiques (instance) */
struct _GStringsPanel
{
    GPanelItem parent;                      /* A laisser en premier        */

    GLoadedBinary *binary;                  /* Binaire en cours d'analyse  */

    GtkMenu *menu;                          /* Menu contextuel pour param. */

    size_t count;                           /* Quantité de symboles utiles */

};

/* Panneau d'aperçu de graphiques (classe) */
struct _GStringsPanelClass
{
    GPanelItemClass parent;                 /* A laisser en premier        */

};


/* Colonnes de la liste des symboles */
typedef enum _StringsColumn
{
    STC_SYMBOL,                             /* Symbole représenté          */

    STC_PHYSICAL,                           /* Adresse phyisque            */
    STC_VIRTUAL,                            /* Adresse virtuelle           */
    STC_AREA,                               /* Zone de localisation        */
    STC_NAME,                               /* Désignation humaine         */
    STC_VALUE,                              /* Chaîne de caractères        */
    STC_ORIGINAL,                           /* Version brute d'origine     */

    STC_MATCHED,                            /* Correspondance établie ?    */

    STC_COUNT                               /* Nombre de colonnes          */

} StringsColumn;


/* Données utiles à la mise à jour */
typedef struct _strings_update_data strings_update_data;


/* Initialise la classe des panneaux d'affichage de chaînes. */
static void g_strings_panel_class_init(GStringsPanelClass *);

/* Initialise une instance de panneau d'affichage des chaînes. */
static void g_strings_panel_init(GStringsPanel *);

/* Procède à l'initialisation de l'interface de mise à jour. */
static void g_strings_panel_updatable_interface_init(GUpdatablePanelInterface *);

/* Supprime toutes les références externes. */
static void g_strings_panel_dispose(GStringsPanel *);

/* Procède à la libération totale de la mémoire. */
static void g_strings_panel_finalize(GStringsPanel *);

/* Fournit le nom interne attribué à l'élément réactif. */
static char *g_strings_panel_class_get_key(const GStringsPanelClass *);

/* Indique le chemin initial de la localisation d'un panneau. */
static char *g_strings_panel_class_get_path(const GStringsPanelClass *);

/* Indique la définition d'un éventuel raccourci clavier. */
static char *g_strings_panel_class_get_key_bindings(const GStringsPanelClass *);

/* Réagit au changement de sélection des chaînes textuelles. */
static void on_strings_selection_change(GtkTreeSelection *, gpointer);

/* Etablit une comparaison entre deux chaînes de caractères. */
static gint compare_strings_list_columns(GtkTreeModel *, GtkTreeIter *, GtkTreeIter *, gpointer);

/* Réagit à une pression sur <Shift+F2> et simule l'édition. */
static gboolean on_key_pressed_over_strings(GtkTreeView *, GdkEventKey *, GStringsPanel *);

/* Réagit à une édition de l'étiquette d'une chaîne textuelle. */
static void on_string_name_edited(GtkCellRendererText *, gchar *, gchar *, GtkTreeModel *);

/* Réagit à un changement d'affichage principal de contenu. */
static void change_strings_panel_current_content(GStringsPanel *, GLoadedContent *, GLoadedContent *);



/* ------------------------- AFFICHAGE A L'AIDE D'UNE LISTE ------------------------- */


/* Réagit à un changement d'affichage principal de contenu. */
static void reload_strings_for_new_list_view(const GStringsPanel *, GtkStatusStack *, activity_id_t, strings_update_data *);

/* Met en surbrillance les éléments recherchés dans les noms. */
static void update_string_label_in_list_view(GtkListStore *, GtkTreeIter *, const regmatch_t *);

/* Met en surbrillance les éléments recherchés dans les valeurs. */
static void update_string_value_in_list_view(GtkListStore *, GtkTreeIter *, const regmatch_t *);



/* ------------------------- FILTRAGE DES CHAINES PRESENTES ------------------------- */


/* Démarre l'actualisation du filtrage des chaînes. */
static void update_filtered_strings(GStringsPanel *);

/* Détermine si un noeud de l'arborescence doit être filtré. */
static void update_string_node(const strings_update_data *, GtkListStore *, GtkTreeIter *);

/* Exécute un nouveau filtrage des chaînes affichées. */
static void do_filtering_on_strings(const GStringsPanel *, GtkStatusStack *, activity_id_t, strings_update_data *);



/* ------------------------ ATTRIBUTION D'UN MENU CONTEXTUEL ------------------------ */


/* Assure la gestion des clics de souris sur les signets. */
static gboolean on_button_event_over_strings(GtkWidget *, GdkEventButton *, GStringsPanel *);

/* Construit le menu contextuel pour les signets. */
static GtkMenu *build_strings_panel_menu(GStringsPanel *);

/* Fournit le signet sélectionné dans la liste. */
static GBinSymbol *get_selected_panel_symbol(GStringsPanel *, GtkTreeIter *);

/* Réagit avec le menu "Editer le nom". */
static void mcb_strings_panel_edit(GtkMenuItem *, GStringsPanel *);

/* Réagit avec le menu "Copier dans le presse-papiers". */
static void mcb_strings_panel_copy(GtkMenuItem *, GStringsPanel *);

/* Réagit avec le menu "Trouver les références...". */
static void mcb_strings_panel_find_refs(GtkMenuItem *, GStringsPanel *);

/* Réagit avec le menu "Filtrer...". */
static void mcb_strings_panel_filter(GtkMenuItem *, GStringsPanel *);


/* ---------------------- MECANISMES DE MISE A JOUR DE PANNEAU ---------------------- */


/* Données utiles à la mise à jour */
struct _strings_update_data
{
    size_t count;                           /* Qté d'inscriptions réalisées*/

    regex_t *filter;                        /* Filtre appliqué ou NULL     */

};


/* Détermine si un nom de symbole doit être filtré ou non. */
static bool is_string_name_matching(const strings_update_data *, GtkTreeModel *, GtkTreeIter *, regmatch_t *);

/* Détermine si une valeur de symbole doit être filtrée ou non. */
static bool is_string_value_matching(const strings_update_data *, GtkTreeModel *, GtkTreeIter *, regmatch_t *);

/* Prépare une opération de mise à jour de panneau. */
static bool g_strings_panel_setup(const GStringsPanel *, unsigned int, size_t *, strings_update_data **, char **);

/* Bascule l'affichage d'un panneau avant mise à jour. */
static void g_strings_panel_introduce(const GStringsPanel *, unsigned int, strings_update_data *);

/* Réalise une opération de mise à jour de panneau. */
static void g_strings_panel_process(const GStringsPanel *, unsigned int, GtkStatusStack *, activity_id_t, strings_update_data *);

/* Bascule l'affichage d'un panneau après mise à jour. */
static void g_strings_panel_conclude(GStringsPanel *, unsigned int, strings_update_data *);

/* Supprime les données dynamiques utilisées à la mise à jour. */
static void g_strings_panel_clean_data(const GUpdatablePanel *, unsigned int, strings_update_data *);



/* ---------------------------------------------------------------------------------- */
/*                            PARTIE PRINCIPALE DU PANNEAU                            */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un panneau d'affichage des chaînes. */
G_DEFINE_TYPE_WITH_CODE(GStringsPanel, g_strings_panel, G_TYPE_PANEL_ITEM,
                        G_IMPLEMENT_INTERFACE(G_TYPE_UPDATABLE_PANEL, g_strings_panel_updatable_interface_init));


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des panneaux d'affichage de chaînes.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_strings_panel_class_init(GStringsPanelClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GEditorItemClass *item;                 /* Encore une autre vision...  */
    GPanelItemClass *panel;                 /* Version parente de la classe*/

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_strings_panel_dispose;
    object->finalize = (GObjectFinalizeFunc)g_strings_panel_finalize;

    item = G_EDITOR_ITEM_CLASS(class);

    item->get_key = (get_item_key_fc)g_strings_panel_class_get_key;

    item->change_content = (change_item_content_fc)change_strings_panel_current_content;

    panel = G_PANEL_ITEM_CLASS(class);

    panel->dock_at_startup = gtk_panel_item_class_return_false;
    panel->can_search = gtk_panel_item_class_return_true;
    panel->get_path = (get_panel_path_fc)g_strings_panel_class_get_path;
    panel->get_bindings = (get_panel_bindings_fc)g_strings_panel_class_get_key_bindings;

    panel->update_filtered = (update_filtered_fc)update_filtered_strings;

    panel->gid = setup_tiny_global_work_group(1);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance de panneau d'affichage des chaînes.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_strings_panel_init(GStringsPanel *panel)
{
    GPanelItem *pitem;                      /* Version parente du panneau  */
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeModelFilter *filter;             /* Filtre pour l'arborescence  */
    GtkTreeView *treeview;                  /* Affichage de la liste       */
    GtkCellRenderer *renderer;              /* Moteur de rendu de colonne  */
    GtkTreeViewColumn *column;              /* Colonne de la liste         */
    GtkTreeModel *model;                    /* Modèle de gestion de liste  */
    GtkTreeSortable *sortable;              /* Autre vision de la liste    */

    /* Eléments de base */

    pitem = G_PANEL_ITEM(panel);

    pitem->widget = G_NAMED_WIDGET(gtk_built_named_widget_new_for_panel(_("Strings"),
                                                                        _("Strings contained in the binary"),
                                                                        PANEL_STRINGS_ID));

    /* Représentation graphique */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(pitem->widget));

    filter = GTK_TREE_MODEL_FILTER(gtk_builder_get_object(builder, "filter"));
    gtk_tree_model_filter_set_visible_column(filter, STC_MATCHED);

    /* Cellules d'affichage */

    treeview = GTK_TREE_VIEW(gtk_builder_get_object(builder, "treeview"));

    renderer = gtk_cell_renderer_text_new();
    column = gtk_tree_view_column_new_with_attributes(_("Physical address"), renderer,
                                                      "text", STC_PHYSICAL,
                                                      NULL);
    gtk_tree_view_column_set_sort_column_id(column, STC_PHYSICAL);
    gtk_tree_view_append_column(GTK_TREE_VIEW(treeview), column);

    renderer = gtk_cell_renderer_text_new();
    column = gtk_tree_view_column_new_with_attributes(_("Virtual address"), renderer,
                                                      "text", STC_VIRTUAL,
                                                      NULL);
    gtk_tree_view_column_set_sort_column_id(column, STC_VIRTUAL);
    gtk_tree_view_append_column(GTK_TREE_VIEW(treeview), column);

    renderer = gtk_cell_renderer_text_new();
    g_object_set(renderer, "xpad", 16, NULL);
    column = gtk_tree_view_column_new_with_attributes(_("Area"), renderer,
                                                      "text", STC_AREA,
                                                      NULL);
    gtk_tree_view_column_set_sort_column_id(column, STC_AREA);
    gtk_tree_view_append_column(GTK_TREE_VIEW(treeview), column);

    model = GTK_TREE_MODEL(gtk_builder_get_object(builder, "store"));

    renderer = gtk_cell_renderer_text_new();
    g_object_set(G_OBJECT(renderer), "editable", TRUE, NULL);
    g_signal_connect(renderer, "edited", G_CALLBACK(on_string_name_edited), model);
    column = gtk_tree_view_column_new_with_attributes(_("Name"), renderer,
                                                      "text", STC_NAME,
                                                      NULL);
    gtk_tree_view_column_set_sort_column_id(column, STC_NAME);
    gtk_tree_view_append_column(GTK_TREE_VIEW(treeview), column);

    renderer = gtk_cell_renderer_text_new();
    column = gtk_tree_view_column_new_with_attributes(_("Value"), renderer,
                                                      "markup", STC_VALUE,
                                                      NULL);
    gtk_tree_view_column_set_sort_column_id(column, STC_VALUE);
    gtk_tree_view_append_column(GTK_TREE_VIEW(treeview), column);

    /* Tri de la liste */

    sortable = GTK_TREE_SORTABLE(gtk_builder_get_object(builder, "store"));

    gtk_tree_sortable_set_sort_func(sortable, STC_PHYSICAL, compare_strings_list_columns,
                                    GINT_TO_POINTER(STC_PHYSICAL), NULL);

    gtk_tree_sortable_set_sort_func(sortable, STC_VIRTUAL, compare_strings_list_columns,
                                    GINT_TO_POINTER(STC_VIRTUAL), NULL);

    gtk_tree_sortable_set_sort_func(sortable, STC_AREA, compare_strings_list_columns,
                                    GINT_TO_POINTER(STC_AREA), NULL);

    gtk_tree_sortable_set_sort_func(sortable, STC_NAME, compare_strings_list_columns,
                                    GINT_TO_POINTER(STC_NAME), NULL);

    gtk_tree_sortable_set_sort_func(sortable, STC_VALUE, compare_strings_list_columns,
                                    GINT_TO_POINTER(STC_VALUE), NULL);

    gtk_tree_sortable_set_sort_column_id(sortable, STC_VIRTUAL, GTK_SORT_ASCENDING);

    /* Connexion des signaux */

    gtk_builder_add_callback_symbols(builder,
                                     BUILDER_CALLBACK(on_button_event_over_strings),
                                     BUILDER_CALLBACK(on_key_pressed_over_strings),
                                     BUILDER_CALLBACK(on_strings_selection_change),
                                     NULL);

    gtk_builder_connect_signals(builder, panel);

    g_object_unref(G_OBJECT(builder));

    /* Préparation du menu contextuel */

    panel->menu = build_strings_panel_menu(panel);

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

static void g_strings_panel_updatable_interface_init(GUpdatablePanelInterface *iface)
{
    iface->setup = (setup_updatable_cb)g_strings_panel_setup;
    iface->get_group = (get_updatable_group_cb)g_panel_item_get_group;
    iface->introduce = (introduce_updatable_cb)g_strings_panel_introduce;
    iface->process = (process_updatable_cb)g_strings_panel_process;
    iface->conclude = (conclude_updatable_cb)g_strings_panel_conclude;
    iface->clean = (clean_updatable_data_cb)g_strings_panel_clean_data;

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

static void g_strings_panel_dispose(GStringsPanel *panel)
{
    if (panel->binary != NULL)
        g_object_unref(G_OBJECT(panel->binary));

    G_OBJECT_CLASS(g_strings_panel_parent_class)->dispose(G_OBJECT(panel));

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

static void g_strings_panel_finalize(GStringsPanel *panel)
{
    G_OBJECT_CLASS(g_strings_panel_parent_class)->finalize(G_OBJECT(panel));

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

static char *g_strings_panel_class_get_key(const GStringsPanelClass *class)
{
    char *result;                           /* Description à renvoyer      */

    result = strdup(PANEL_STRINGS_ID);

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

static char *g_strings_panel_class_get_path(const GStringsPanelClass *class)
{
    char *result;                           /* Emplacement à retourner     */

    result = strdup("Ms");

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

static char *g_strings_panel_class_get_key_bindings(const GStringsPanelClass *class)
{
    char *result;                           /* Emplacement à retourner     */

    result = strdup("<Shift>F12");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un panneau d'affichage des chaînes.                     *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GPanelItem *g_strings_panel_new(void)
{
    GPanelItem *result;                     /* Structure à retourner       */

    result = g_object_new(G_TYPE_STRINGS_PANEL, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : selection = sélection modifiée.                              *
*                unused    = adresse non utilisée ici.                        *
*                                                                             *
*  Description : Réagit au changement de sélection des chaînes textuelles.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_strings_selection_change(GtkTreeSelection *selection, gpointer unused)
{
    GtkTreeIter iter;                       /* Point de sélection          */
    GtkTreeModel *model;                    /* Modèle de gestion           */
    GBinSymbol *symbol;                     /* Symbole en cours d'étude    */
    const vmpa2t *addr;                     /* Adressse associée au signet */
    GLoadedPanel *panel;                    /* Afficheur effectif de code  */

    if (gtk_tree_selection_get_selected(selection, &model, &iter))
    {
        gtk_tree_model_get(model, &iter, STC_SYMBOL, &symbol, -1);

        addr = get_mrange_addr(g_binary_symbol_get_range(symbol));

        panel = get_current_view();

        if (GTK_IS_DISPLAY_PANEL(panel))
            gtk_display_panel_request_move(GTK_DISPLAY_PANEL(panel), addr);

        g_object_unref(G_OBJECT(panel));

        g_object_unref(G_OBJECT(symbol));

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : model  = gestionnaire du tableau de données.                 *
*                a      = première ligne de données à traiter.                *
*                b      = seconde ligne de données à traiter.                 *
*                column = indice de la colonne à considérer, encodée.         *
*                                                                             *
*  Description : Etablit une comparaison entre deux chaînes de caractères.    *
*                                                                             *
*  Retour      : Indication de tri entre les deux lignes fournies.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gint compare_strings_list_columns(GtkTreeModel *model, GtkTreeIter *a, GtkTreeIter *b, gpointer column)
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

static gboolean on_key_pressed_over_strings(GtkTreeView *treeview, GdkEventKey *event, GStringsPanel *panel)
{
    const gchar *accelerator;               /* Combinaison de raccourci    */
    guint accel_key;                        /* Touche de raccourci         */
    GdkModifierType accel_mod;              /* Modifiateurs attendus aussi */

    if (!g_generic_config_get_value(get_main_configuration(), MPK_KEYBINDINGS_EDIT, &accelerator))
        return FALSE;

    if (accelerator == NULL)
        return FALSE;

    gtk_accelerator_parse(accelerator, &accel_key, &accel_mod);

    if (event->keyval == accel_key && event->state == accel_mod)
        mcb_strings_panel_edit(NULL, panel);

    return FALSE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : renderer = moteur de rendu pour la cellule.                  *
*                path     = chemin d'accès vers la cellule éditée.            *
*                new      = nouvelle valeur sous forme de texte à valider.    *
*                model    = gestionnaire des données de la liste affichée.    *
*                                                                             *
*  Description : Réagit à une édition de l'étiquette d'une chaîne textuelle.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_string_name_edited(GtkCellRendererText *renderer, gchar *path, gchar *new, GtkTreeModel *model)
{
    GtkTreePath *tree_path;                 /* Chemin d'accès natif        */
    GtkTreeIter iter;                       /* Point de la modification    */
    GBinSymbol *symbol;                     /* Symbole à actualiser        */

    tree_path = gtk_tree_path_new_from_string(path);
    if (tree_path == NULL) return;

    if (!gtk_tree_model_get_iter(model, &iter, tree_path))
        goto opve_bad_iter;

    gtk_tree_model_get(model, &iter, STC_SYMBOL, &symbol, -1);

    g_binary_symbol_set_alt_label(symbol, new);

    g_object_unref(G_OBJECT(symbol));

 opve_bad_iter:

    gtk_tree_path_free(tree_path);

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

static void change_strings_panel_current_content(GStringsPanel *panel, GLoadedContent *old, GLoadedContent *new)
{
    GLoadedBinary *binary;                  /* Autre version de l'instance */
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkListStore *store;                    /* Modèle de gestion           */
    GtkTreeView *treeview;                  /* Affichage de la liste       */
    GtkTreeViewColumn *column;              /* Colonne de la liste         */
    GArchProcessor *proc;                   /* Architecture du binaire     */

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

    store = GTK_LIST_STORE(gtk_builder_get_object(builder, "store"));

    gtk_list_store_clear(store);

    g_object_unref(G_OBJECT(builder));

    /* Si le panneau actif représente un binaire, actualisation de l'affichage */

    if (binary != NULL)
    {
        treeview = GTK_TREE_VIEW(gtk_builder_get_object(builder, "treeview"));
        column = gtk_tree_view_get_column(treeview, 1);

        proc = g_loaded_binary_get_processor(binary);

        gtk_tree_view_column_set_visible(column, g_arch_processor_has_virtual_space(proc));

        g_object_unref(G_OBJECT(proc));

        run_panel_update(G_UPDATABLE_PANEL(panel), PUI_0);

    }

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

static void reload_strings_for_new_list_view(const GStringsPanel *panel, GtkStatusStack *status, activity_id_t id, strings_update_data *data)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkListStore *store;                    /* Modèle de gestion           */
    GArchProcessor *proc;                   /* Architecture utilisée       */
    MemoryDataSize size;                    /* Taille des localisations    */
    GExeFormat *format;                     /* Format associé au binaire   */
    GBinPortion *portions;                  /* Couche première de portions */
    GBinContent *content;                   /* Contenu binaire en mémoire  */
    sym_iter_t *siter;                      /* Parcours des symboles       */
    GBinSymbol *symbol;                     /* Symbole manipulé            */
    const mrange_t *range;                  /* Couverture mémoire          */
    const vmpa2t *addr;                     /* Adressse liée à la chaîne   */
    VMPA_BUFFER(phys);                      /* Position physique           */
    VMPA_BUFFER(virt);                      /* Adresse virtuelle           */
    GBinPortion *portion;                   /* Zone mémoire d'appartenance */
    const char *area;                       /* Description de la zone      */
    size_t len;                             /* Taille de la chaîne         */
    const char *text;                       /* Texte original référencé    */
    char *real_text;                        /* Texte avec octet nul final  */
    GtkTreeIter iter;                       /* Point d'insertion           */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    store = GTK_LIST_STORE(gtk_builder_get_object(builder, "store"));

    proc = g_loaded_binary_get_processor(panel->binary);
    size = g_arch_processor_get_memory_size(proc);
    g_object_unref(G_OBJECT(proc));

    format = g_loaded_binary_get_format(panel->binary);
    portions = g_exe_format_get_portions(format);
    content = g_known_format_get_content(G_KNOWN_FORMAT(format));

    siter = create_symbol_iterator(G_BIN_FORMAT(format), 0);

    for (symbol = get_symbol_iterator_current(siter);
         symbol != NULL;
         symbol = get_symbol_iterator_next(siter))
    {
        if (!G_IS_STR_SYMBOL(symbol))
            goto rsfnlv_next;

        if (g_string_symbol_is_structural(G_STR_SYMBOL(symbol)))
            goto rsfnlv_next;

        range = g_binary_symbol_get_range(symbol);
        addr = get_mrange_addr(range);

        vmpa2_phys_to_string(addr, size, phys, NULL);
        vmpa2_virt_to_string(addr, size, virt, NULL);

        portion = g_binary_portion_find_at_addr(portions, addr);
        area = g_binary_portion_get_desc(portion);
        g_object_unref(G_OBJECT(portion));

        text = g_string_symbol_get_utf8(G_STR_SYMBOL(symbol), &len);
        if (text == NULL) goto rsfnlv_next;

        real_text = strndup(text, len);

        gtk_list_store_append(store, &iter);
        gtk_list_store_set(store, &iter,
                           STC_SYMBOL, symbol,
                           STC_PHYSICAL, phys,
                           STC_VIRTUAL, virt,
                           STC_AREA, area,
                           STC_NAME, NULL,
                           STC_VALUE, NULL,
                           STC_ORIGINAL, real_text,
                           STC_MATCHED, false,
                           -1);

        free(real_text);

        update_string_node(data, store, &iter);

        data->count++;

 rsfnlv_next:

        g_object_unref(G_OBJECT(symbol));

        gtk_status_stack_update_activity_value(status, id, 1);

    }

    delete_symbol_iterator(siter);

    g_object_unref(G_OBJECT(content));
    g_object_unref(G_OBJECT(portions));
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

static void update_string_label_in_list_view(GtkListStore *store, GtkTreeIter *iter, const regmatch_t *match)
{
    GtkTreeModel *model;                    /* Autre vision du gestionnaire*/
    char *original;                         /* Etiquette brute d'origine   */
    char *value;                            /* Etiquette mise en relief    */

    model = GTK_TREE_MODEL(store);

    gtk_tree_model_get(model, iter, STC_ORIGINAL, &original, -1);

    original = strrpl(original, "&", "&amp;");
    original = strrpl(original, "<", "&lt;");
    original = strrpl(original, ">", "&gt;");
    original = strrpl(original, "\r", "<b>\\r</b>");
    original = strrpl(original, "\n", "<b>\\n</b>");

    value = build_highlighted_name(original, match, 0);

    gtk_list_store_set(store, iter, STC_VALUE, value, -1);

    free(original);
    free(value);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : store = gestionnaire de données pour une arborescence.       *
*                iter  = position des données traitées.                       *
*                match = correspondance avec un objet recherché.              *
*                                                                             *
*  Description : Met en surbrillance les éléments recherchés dans les valeurs.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void update_string_value_in_list_view(GtkListStore *store, GtkTreeIter *iter, const regmatch_t *match)
{
    GtkTreeModel *model;                    /* Autre vision du gestionnaire*/
    char *original;                         /* Etiquette brute d'origine   */
    char *value;                            /* Etiquette mise en relief    */

    model = GTK_TREE_MODEL(store);

    gtk_tree_model_get(model, iter, STC_ORIGINAL, &original, -1);

    original = strrpl(original, "&", "&amp;");
    original = strrpl(original, "<", "&lt;");
    original = strrpl(original, ">", "&gt;");
    original = strrpl(original, "\r", "<b>\\r</b>");
    original = strrpl(original, "\n", "<b>\\n</b>");

    value = build_highlighted_name(original, match, 0);

    gtk_list_store_set(store, iter, STC_VALUE, value, -1);

    free(original);
    free(value);

}



/* ---------------------------------------------------------------------------------- */
/*                           FILTRAGE DES CHAINES PRESENTES                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau assurant l'affichage des chaînes.            *
*                                                                             *
*  Description : Démarre l'actualisation du filtrage des chaînes.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void update_filtered_strings(GStringsPanel *panel)
{
    run_panel_update(G_UPDATABLE_PANEL(panel), PUI_1);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : data  = données complémentaire à manipuler.                  *
*                store = gestionnaire de l'ensemble des données.              *
*                iter  = localisation des données à analyser.                 *
*                                                                             *
*  Description : Détermine si un noeud de l'arborescence doit être filtré.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void update_string_node(const strings_update_data *data, GtkListStore *store, GtkTreeIter *iter)
{
    GtkTreeModel *model;                    /* Autre vision du gestionnaire*/
    regmatch_t match;                       /* Récupération des trouvailles*/
    bool name_matched;                      /* Correspondance de sélection */
    bool value_matched;                     /* Correspondance de sélection */

    model = GTK_TREE_MODEL(store);

    name_matched = is_string_name_matching(data, model, iter, &match);

    if (name_matched)
        update_string_label_in_list_view(store, iter, &match);

    value_matched = is_string_value_matching(data, model, iter, &match);

    if (value_matched)
        update_string_value_in_list_view(store, iter, &match);

    if (name_matched || value_matched)
        gtk_list_store_set(GTK_LIST_STORE(model), iter, STC_MATCHED, true, -1);
    else
        gtk_list_store_set(GTK_LIST_STORE(model), iter, STC_MATCHED, false, -1);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel  = panneau assurant l'affichage des chaînes.           *
*                status = barre de statut à tenir informée.                   *
*                id     = identifiant pour le suivi de la progression.        *
*                data   = données complémentaire à manipuler.                 *
*                                                                             *
*  Description : Exécute un nouveau filtrage des chaînes affichées.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void do_filtering_on_strings(const GStringsPanel *panel, GtkStatusStack *status, activity_id_t id, strings_update_data *data)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkListStore *store;                    /* Modèle de gestion           */


    gboolean filter_string_panel_iter(GtkTreeModel *model, GtkTreePath *path, GtkTreeIter *iter, gpointer unused)
    {
        update_string_node(data, store, iter);

        gtk_status_stack_update_activity_value(status, id, 1);

        return FALSE;

    }


    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    store = GTK_LIST_STORE(gtk_builder_get_object(builder, "store"));

    gtk_tree_model_foreach(GTK_TREE_MODEL(store), (GtkTreeModelForeachFunc)filter_string_panel_iter, NULL);

    g_object_unref(G_OBJECT(builder));

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

static gboolean on_button_event_over_strings(GtkWidget *widget, GdkEventButton *event, GStringsPanel *panel)
{
    GtkTreeSelection *selection;            /* Sélection courante          */
    GtkTreeIter iter;                       /* Point de sélection          */
    GtkTreeModel *model;                    /* Modèle de gestion           */
    GBinSymbol *symbol;                     /* Symbole en cours d'étude    */
    const vmpa2t *addr;                     /* Adressse associée au signet */
    GLoadedPanel *display;                  /* Afficheur effectif de code  */

    switch (event->button)
    {
        case 1:

            if (event->type != GDK_2BUTTON_PRESS)
                break;

            selection = gtk_tree_view_get_selection(GTK_TREE_VIEW(widget));

            if (gtk_tree_selection_get_selected(selection, &model, &iter))
            {
                gtk_tree_model_get(model, &iter, STC_SYMBOL, &symbol, -1);

                addr = get_mrange_addr(g_binary_symbol_get_range(symbol));

                display = get_current_view();

                if (GTK_IS_DISPLAY_PANEL(display))
                    gtk_display_panel_request_move(GTK_DISPLAY_PANEL(display), addr);

                g_object_unref(G_OBJECT(display));

                g_object_unref(G_OBJECT(symbol));

            }

            break;

        case 3:
            if (event->type == GDK_BUTTON_RELEASE)
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

static GtkMenu *build_strings_panel_menu(GStringsPanel *panel)
{
    GtkWidget *result;                      /* Support à retourner         */
    GtkWidget *submenuitem;                 /* Sous-élément de menu        */

    result = qck_create_menu(NULL);

    submenuitem = qck_create_menu_item(NULL, NULL, _("_Edit name"), NULL, NULL);
    gtk_container_add(GTK_CONTAINER(result), submenuitem);

    submenuitem = qck_create_menu_item(NULL, NULL, _("_Copy to clipboard"),
                                       G_CALLBACK(mcb_strings_panel_copy), panel);
    gtk_container_add(GTK_CONTAINER(result), submenuitem);

    submenuitem = qck_create_menu_item(NULL, NULL, _("_Find references..."),
                                       G_CALLBACK(mcb_strings_panel_find_refs), panel);
    gtk_container_add(GTK_CONTAINER(result), submenuitem);

    submenuitem = qck_create_menu_separator();
    gtk_container_add(GTK_CONTAINER(result), submenuitem);

    submenuitem = qck_create_menu_item(NULL, NULL, _("Filter..."),
                                       G_CALLBACK(mcb_strings_panel_filter), panel);
    gtk_container_add(GTK_CONTAINER(result), submenuitem);

    return GTK_MENU(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau concerné par l'opération.                    *
*                save  = zone de conservation du point de trouvaille. [OUT]   *
*                                                                             *
*  Description : Fournit le signet sélectionné dans la liste.                 *
*                                                                             *
*  Retour      : Signet en cours d'édition ou NULL en cas de soucis.          *
*                                                                             *
*  Remarques   : Le résultat non nul est à déréférencer après usage.          *
*                                                                             *
******************************************************************************/

static GBinSymbol *get_selected_panel_symbol(GStringsPanel *panel, GtkTreeIter *save)
{
    GBinSymbol *result;                     /* Chaîne textuelle à renvoyer */
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeView *treeview;                  /* Arborescence graphique      */
    GtkTreeSelection *selection;            /* Représentation de sélection */
    GtkTreeModel *model;                    /* Gestionnaire des données    */
    GtkTreeIter iter;                       /* Point de la sélection       */

    result = NULL;

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    treeview = GTK_TREE_VIEW(gtk_builder_get_object(builder, "treeview"));

    selection = gtk_tree_view_get_selection(treeview);

    if (gtk_tree_selection_get_selected(selection, &model, &iter))
        gtk_tree_model_get(model, &iter, STC_SYMBOL, &result, -1);

    if (save != NULL)
        *save = iter;

    g_object_unref(G_OBJECT(builder));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                panel    = panneau d'affichage des signets liés à un binaire.*
*                                                                             *
*  Description : Réagit avec le menu "Editer le nom".                         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_strings_panel_edit(GtkMenuItem *menuitem, GStringsPanel *panel)
{
    GtkTreeIter iter;                       /* Point de la sélection       */
    GBinSymbol *symbol;                     /* Symbole sélectionné         */
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeView *treeview;                  /* Arborescence graphique      */
    GtkTreeModel *model;                    /* Gestionnaire de données     */
    GtkTreePath *path;                      /* Chemin d'accès à ce point   */

    symbol = get_selected_panel_symbol(panel, &iter);
    if (symbol == NULL) return;

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    treeview = GTK_TREE_VIEW(gtk_builder_get_object(builder, "treeview"));

    model = gtk_tree_view_get_model(treeview);
    path = gtk_tree_model_get_path(model, &iter);

    gtk_tree_view_set_cursor(treeview, path,
                             gtk_tree_view_get_column(treeview, STC_NAME - STC_PHYSICAL),
                             TRUE);

    gtk_tree_path_free(path);

    g_object_unref(G_OBJECT(builder));

    g_object_unref(G_OBJECT(symbol));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                treeview = arbre contenant la sélection à exporter.          *
*                                                                             *
*  Description : Réagit avec le menu "Copier dans le presse-papiers".         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_strings_panel_copy(GtkMenuItem *menuitem, GStringsPanel *panel)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeView *treeview;                  /* Arborescence graphique      */
    GtkTreeSelection *selection;            /* Sélection de l'arbre        */
    GtkTreeIter iter;                       /* Point de sélection          */
    GtkTreeModel *model;                    /* Modèle de gestion           */
    gchar *string;                          /* Chaîne sélectionnée         */
    GtkClipboard *clipboard;                /* Presse-papiers d'arrivée    */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    treeview = GTK_TREE_VIEW(gtk_builder_get_object(builder, "treeview"));

    selection = gtk_tree_view_get_selection(treeview);

    if (gtk_tree_selection_get_selected(selection, &model, &iter))
    {
        gtk_tree_model_get(model, &iter, STC_VALUE, &string, -1);

        if (string != NULL)
        {
            clipboard = gtk_clipboard_get_for_display(gdk_display_get_default(),
                                                      GDK_SELECTION_PRIMARY);

            gtk_clipboard_set_text(clipboard, string, strlen(string));
            g_free(string);

        }

    }

    g_object_unref(G_OBJECT(builder));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                panel    = panneau d'affichage des signets liés à un binaire.*
*                                                                             *
*  Description : Réagit avec le menu "Trouver les références...".             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_strings_panel_find_refs(GtkMenuItem *menuitem, GStringsPanel *panel)
{
    GBinSymbol *symbol;                     /* Symbole sélectionné         */
    const mrange_t *range;                  /* Couverture en mémoire       */
    GArchProcessor *proc;                   /* Processeur de l'architecture*/
    GArchInstruction *instr;                /* Point de croisements        */
    GtkWindow *editor;                      /* Fenêtre graphique principale*/
    GtkWidget *dialog;                      /* Boîte de dialogue à montrer */
    vmpa2t *addr;                           /* Adresse de destination      */
    GLoadedPanel *display;                  /* Afficheur effectif de code  */

    symbol = get_selected_panel_symbol(panel, NULL);
    if (symbol == NULL) return;

    range = g_binary_symbol_get_range(symbol);

    proc = g_loaded_binary_get_processor(panel->binary);

    /**
     * Se rapporter aux commentaires de mcb_edition_list_xrefs() pour les questions
     * concernant l'usage d'une adresse d'instruction au lieu de son emplacement.
     */
    instr = g_arch_processor_find_instr_by_address(proc, get_mrange_addr(range));

    editor = get_editor_window();

    dialog = create_gotox_dialog_for_cross_references(editor, panel->binary, instr, true);

    if (gtk_dialog_run(GTK_DIALOG(dialog)) == GTK_RESPONSE_OK)
    {
        addr = get_address_from_gotox_dialog(dialog);

        display = get_current_view();

        if (GTK_IS_DISPLAY_PANEL(display))
            gtk_display_panel_request_move(GTK_DISPLAY_PANEL(display), addr);

        g_object_unref(G_OBJECT(display));

        delete_vmpa(addr);

    }

    gtk_widget_destroy(dialog);

    g_object_unref(G_OBJECT(editor));

    if (instr != NULL)
        g_object_unref(G_OBJECT(instr));

    g_object_unref(G_OBJECT(proc));

    g_object_unref(G_OBJECT(symbol));

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

static void mcb_strings_panel_filter(GtkMenuItem *menuitem, GStringsPanel *panel)
{
#if 0
    GCfgParam *param;                       /* Paramètre sélectionné       */

    param = get_selected_panel_symbol(panel, NULL);
    if (param == NULL) return;

    g_config_param_make_empty(param);

    g_object_unref(G_OBJECT(param));
#endif
}



/* ---------------------------------------------------------------------------------- */
/*                        MECANISMES DE MISE A JOUR DE PANNEAU                        */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : data  = données complémentaire à manipuler.                  *
*                model = gestionnaire de l'ensemble des données.              *
*                iter  = localisation des données à analyser.                 *
*                match = récupération des trouvailles. [OUT]                  *
*                                                                             *
*  Description : Détermine si un nom de symbole doit être filtré ou non.      *
*                                                                             *
*  Retour      : true si le symbol ne doit pas être affiché, false sinon.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool is_string_name_matching(const strings_update_data *data, GtkTreeModel *model, GtkTreeIter *iter, regmatch_t *match)
{
    bool result;                            /* Bilan à retourner           */
    GBinSymbol *symbol;                     /* Symbole manipulé            */
    char *label;                            /* Etiquette à analyser        */

    gtk_tree_model_get(model, iter, STC_SYMBOL, &symbol, -1);
    assert(G_IS_STR_SYMBOL(symbol));

    label = g_binary_symbol_get_label(symbol);

    if (label == NULL)
        result = false;

    else
    {
        result = is_content_matching(data->filter, label, match);
        free(label);
    }

    g_object_unref(G_OBJECT(symbol));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : data  = données complémentaire à manipuler.                  *
*                model = gestionnaire de l'ensemble des données.              *
*                iter  = localisation des données à analyser.                 *
*                match = récupération des trouvailles. [OUT]                  *
*                                                                             *
*  Description : Détermine si une valeur de symbole doit être filtrée ou non. *
*                                                                             *
*  Retour      : true si le symbol ne doit pas être affiché, false sinon.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool is_string_value_matching(const strings_update_data *data, GtkTreeModel *model, GtkTreeIter *iter, regmatch_t *match)
{
    bool result;                            /* Bilan à retourner           */
    char *original;                         /* Etiquette brute d'origine   */

    gtk_tree_model_get(model, iter, STC_ORIGINAL, &original, -1);

    result = is_content_matching(data->filter, original, match);

    free(original);

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

static bool g_strings_panel_setup(const GStringsPanel *panel, unsigned int uid, size_t *count, strings_update_data **data, char **msg)
{
    bool result;                            /* Bilan à retourner           */
    GBinFormat *format;                     /* Format du binaire           */
#ifndef NDEBUG
    int ret;                                /* Bilan de mise en place      */
#endif

    result = true;

    *data = malloc(sizeof(strings_update_data));

    switch (uid)
    {
        case PUI_0:

            format = G_BIN_FORMAT(g_loaded_binary_get_format(panel->binary));

            g_binary_format_lock_symbols_rd(format);
            *count = g_binary_format_count_symbols(format);
            g_binary_format_unlock_symbols_rd(format);

            g_object_unref(G_OBJECT(format));

            (*data)->count = 0;

            *msg = strdup(_("Loading strings available in the binary format..."));

            break;

        case PUI_1:

            *count = panel->count;
            (*data)->count = panel->count;

            *msg = strdup(_("Filtering strings available in the binary format..."));

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

static void g_strings_panel_introduce(const GStringsPanel *panel, unsigned int uid, strings_update_data *data)
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

static void g_strings_panel_process(const GStringsPanel *panel, unsigned int uid, GtkStatusStack *status, activity_id_t id, strings_update_data *data)
{
    switch (uid)
    {
        case PUI_0:
            reload_strings_for_new_list_view(panel, status, id, data);
            break;

        case PUI_1:
            do_filtering_on_strings(panel, status, id, data);
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

static void g_strings_panel_conclude(GStringsPanel *panel, unsigned int uid, strings_update_data *data)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeView *treeview;                  /* Arborescence graphique      */
    GtkTreeModel *model;                    /* Source de données associée  */

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

static void g_strings_panel_clean_data(const GUpdatablePanel *panel, unsigned int uid, strings_update_data *data)
{
    if (data->filter != NULL)
    {
        regfree(data->filter);
        free(data->filter);
    }

}
