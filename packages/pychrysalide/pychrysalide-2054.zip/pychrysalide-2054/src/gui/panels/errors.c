
/* Chrysalide - Outil d'analyse de fichiers binaires
 * errors.c - panneau listant les erreurs au désassemblage
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


#include "errors.h"


#include <assert.h>
#include <malloc.h>
#include <stdio.h>


#include <i18n.h>


#include "updating-int.h"
#include "../panel-int.h"
#include "../core/global.h"
#include "../../analysis/binary.h"
#include "../../core/global.h"
#include "../../core/paths.h"
#include "../../core/queue.h"
#include "../../format/format.h"
#include "../../glibext/signal.h"
#include "../../gtkext/easygtk.h"
#include "../../gtkext/gtkdisplaypanel.h"
#include "../../gtkext/named.h"



/* ----------------------- PRESENTATION GRAPHIQUE DES ERREURS ----------------------- */


/* Origine de la dernière ouverture/fermeture reproductible */
typedef enum _UserActionType
{
    UAT_COLLAPSE,                           /* Fermeture totale            */
    UAT_EXPAND,                             /* Ouverture totale            */
    UAT_DEPTH,                              /* Descente contrôlée          */

} UserActionType;


/* Panneau de présentation des erreurs recontrées (instance) */
struct _GErrorPanel
{
    GPanelItem parent;                      /* A laisser en premier        */

    GLoadedBinary *binary;                  /* Binaire représenté          */

    size_t count;                           /* Nombre de soucis présents   */
    size_t kept;                            /* Nombre d'éléments affichés  */

};

/* Panneau de présentation des erreurs recontrées (classe) */
struct _GErrorPanelClass
{
    GPanelItemClass parent;                 /* A laisser en premier        */

    cairo_surface_t *format_img;            /* Image pour les formats      */
    cairo_surface_t *disass_img;            /* Image pour les architectures*/
    cairo_surface_t *output_img;            /* Image pour les impressions  */

};


/* Colonnes de la liste des messages */
typedef enum _ErrorTreeColumn
{
    ETC_ICON,                               /* Image de représentation     */
    ETC_PHYS,                               /* Position physique           */
    ETC_VIRT,                               /* Position virtuelle          */
    ETC_DESC,                               /* Description humaine         */

    ETC_VISIBLE,                            /* Correspondance établie ?    */
    ETC_ORIGIN,                             /* Source du soucis remonté    */
    ETC_ERROR_TYPE,                         /* Code d'erreur associé       */
    ETC_ADDRESS                             /* Position représentée        */

} BinaryTreeColumn;


/* Manipulation des erreurs de façon générique */
typedef struct _error_desc_t
{
    union
    {
        unsigned int type;                  /* Type de soucis #0           */
        BinaryFormatError ftype;            /* Type de soucis #1           */
        ArchProcessingError ptype;          /* Type de soucis #2           */

    };

    vmpa2t addr;                            /* Localisation d'un problème  */
    char *desc;                             /* Description dudit problème  */

} error_desc_t;


/* Données utiles à la mise à jour */
typedef struct _error_update_data error_update_data;


/* Initialise la classe des panneaux d'affichage des erreurs. */
static void g_error_panel_class_init(GErrorPanelClass *);

/* Initialise une instance de panneau d'affichage des erreurs. */
static void g_error_panel_init(GErrorPanel *);

/* Procède à l'initialisation de l'interface de mise à jour. */
static void g_error_panel_updatable_interface_init(GUpdatablePanelInterface *);

/* Supprime toutes les références externes. */
static void g_error_panel_dispose(GErrorPanel *);

/* Procède à la libération totale de la mémoire. */
static void g_error_panel_finalize(GErrorPanel *);

/* Fournit le nom interne attribué à l'élément réactif. */
static char *g_error_panel_class_get_key(const GErrorPanelClass *);

/* Indique le chemin initial de la localisation d'un panneau. */
static char *g_error_panel_class_get_path(const GErrorPanelClass *);

/* Organise le tri des erreurs présentées. */
static gint sort_errors_in_panel(GtkTreeModel *, GtkTreeIter *, GtkTreeIter *, gpointer);

/* Réagit à un changement d'affichage principal de contenu. */
static void change_error_panel_current_content(GErrorPanel *, GLoadedContent *, GLoadedContent *);

/* Effectue la mise à jour du contenu du panneau d'erreurs. */
static void update_error_panel(const GErrorPanel *, GtkStatusStack *, activity_id_t, error_update_data *);

/* Actualise l'affichage des erreurs sur la base des filtres. */
static void on_error_filter_toggled(GtkToggleButton *, GErrorPanel *);

/* Filtre l'affichage du contenu du panneau d'erreurs. */
static void filter_error_panel(const GErrorPanel *, GtkStatusStack *, activity_id_t, error_update_data *);

/* Affiche un petit résumé concis des soucis remontés. */
static void update_error_panel_summary(const GErrorPanel *);

/* Réagit au changement de sélection des portions. */
static void on_error_selection_changed(GtkTreeSelection *, gpointer);



/* ---------------------- MECANISMES DE MISE A JOUR DE PANNEAU ---------------------- */


/* Données utiles à la mise à jour */
struct _error_update_data
{
    size_t count;                           /* Nombre de soucis présents   */
    size_t kept;                            /* Nombre d'éléments affichés  */

};


/* Prépare une opération de mise à jour de panneau. */
static bool g_error_panel_setup(const GErrorPanel *, unsigned int, size_t *, error_update_data **, char **);

/* Bascule l'affichage d'un panneau avant mise à jour. */
static void g_error_panel_introduce(const GErrorPanel *, unsigned int, error_update_data *);

/* Réalise une opération de mise à jour de panneau. */
static void g_error_panel_process(const GErrorPanel *, unsigned int, GtkStatusStack *, activity_id_t, error_update_data *);

/* Bascule l'affichage d'un panneau après mise à jour. */
static void g_error_panel_conclude(GErrorPanel *, unsigned int, error_update_data *);



/* ---------------------------------------------------------------------------------- */
/*                         PRESENTATION GRAPHIQUE DES ERREURS                         */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un panneau d'affichage des erreurs. */
G_DEFINE_TYPE_WITH_CODE(GErrorPanel, g_error_panel, G_TYPE_PANEL_ITEM,
                        G_IMPLEMENT_INTERFACE(G_TYPE_UPDATABLE_PANEL, g_error_panel_updatable_interface_init));


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des panneaux d'affichage des erreurs.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_error_panel_class_init(GErrorPanelClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GEditorItemClass *item;                 /* Encore une autre vision...  */
    GPanelItemClass *panel;                 /* Version parente de la classe*/
    gchar *filename;                        /* Chemin d'accès à utiliser   */

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_error_panel_dispose;
    object->finalize = (GObjectFinalizeFunc)g_error_panel_finalize;

    item = G_EDITOR_ITEM_CLASS(class);

    item->get_key = (get_item_key_fc)g_error_panel_class_get_key;

    item->change_content = (change_item_content_fc)change_error_panel_current_content;

    panel = G_PANEL_ITEM_CLASS(class);

    panel->get_path = (get_panel_path_fc)g_error_panel_class_get_path;

    panel->gid = setup_tiny_global_work_group(1);

    filename = find_pixmap_file("error_file.png");
    assert(filename != NULL);

    class->format_img = cairo_image_surface_create_from_png(filename);

    filename = find_pixmap_file("error_cpu.png");
    assert(filename != NULL);

    class->disass_img = cairo_image_surface_create_from_png(filename);

    filename = find_pixmap_file("error_display.png");
    assert(filename != NULL);

    class->output_img = cairo_image_surface_create_from_png(filename);

    g_free(filename);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance de panneau d'affichage des erreurs.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_error_panel_init(GErrorPanel *panel)
{
    GPanelItem *pitem;                      /* Version parente du panneau  */
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeSortable *store;                 /* Gestionnaire des données    */
    GtkTreeModelFilter *filter;             /* Filtre pour l'arborescence  */
    GtkTreeView *treeview;                  /* Affichage de la liste       */
    GtkCellRenderer *renderer;              /* Moteur de rendu de colonne  */
    GtkTreeViewColumn *column;              /* Colonne de la liste         */

    /* Eléments de base */

    pitem = G_PANEL_ITEM(panel);

    pitem->widget = G_NAMED_WIDGET(gtk_built_named_widget_new_for_panel(_("Errors"),
                                                                        _("Disassembling errors"),
                                                                        PANEL_ERRORS_ID));

    /* Compléments propres */

    panel->binary = NULL;

    /* Représentation graphique */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(pitem->widget));

    store = GTK_TREE_SORTABLE(gtk_builder_get_object(builder, "store"));
    gtk_tree_sortable_set_sort_func(store, ETC_ADDRESS, sort_errors_in_panel, NULL, NULL);
    gtk_tree_sortable_set_sort_column_id(store, ETC_ADDRESS, GTK_SORT_ASCENDING);

    filter = GTK_TREE_MODEL_FILTER(gtk_builder_get_object(builder, "filter"));
    gtk_tree_model_filter_set_visible_column(filter, ETC_VISIBLE);

    /* Liste des erreurs relevées */

    treeview = GTK_TREE_VIEW(gtk_builder_get_object(builder, "treeview"));

    column = gtk_tree_view_column_new();
    gtk_tree_view_append_column(treeview, column);

    renderer = gtk_cell_renderer_text_new();
    g_object_set(G_OBJECT(renderer), "xalign", 1.0, NULL);
    gtk_tree_view_column_pack_start(column, renderer, TRUE);
    gtk_tree_view_column_add_attribute(column, renderer, "markup", ETC_PHYS);

    column = gtk_tree_view_column_new();
    gtk_tree_view_append_column(treeview, column);

    renderer = gtk_cell_renderer_text_new();
    g_object_set(G_OBJECT(renderer), "xalign", 1.0, NULL);
    gtk_tree_view_column_pack_start(column, renderer, TRUE);
    gtk_tree_view_column_add_attribute(column, renderer, "markup", ETC_VIRT);

    column = gtk_tree_view_column_new();
    gtk_tree_view_append_column(treeview, column);

    renderer = gtk_cell_renderer_pixbuf_new();
    gtk_tree_view_column_pack_start(column, renderer, FALSE);
    gtk_tree_view_column_add_attribute(column, renderer, "surface", ETC_ICON);

    renderer = gtk_cell_renderer_text_new();
    gtk_tree_view_column_pack_end(column, renderer, TRUE);
    gtk_tree_view_column_add_attribute(column, renderer, "markup", ETC_DESC);

    /* Connexion des signaux */

    gtk_builder_add_callback_symbols(builder,
                                     BUILDER_CALLBACK(gtk_tree_view_collapse_all),
                                     BUILDER_CALLBACK(gtk_tree_view_expand_all),
                                     BUILDER_CALLBACK(on_error_filter_toggled),
                                     BUILDER_CALLBACK(on_error_selection_changed),
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

static void g_error_panel_updatable_interface_init(GUpdatablePanelInterface *iface)
{
    iface->setup = (setup_updatable_cb)g_error_panel_setup;
    iface->get_group = (get_updatable_group_cb)g_panel_item_get_group;
    iface->introduce = (introduce_updatable_cb)g_error_panel_introduce;
    iface->process = (process_updatable_cb)g_error_panel_process;
    iface->conclude = (conclude_updatable_cb)g_error_panel_conclude;

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

static void g_error_panel_dispose(GErrorPanel *panel)
{
    if (panel->binary != NULL)
        g_object_unref(G_OBJECT(panel->binary));

    G_OBJECT_CLASS(g_error_panel_parent_class)->dispose(G_OBJECT(panel));

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

static void g_error_panel_finalize(GErrorPanel *panel)
{
    G_OBJECT_CLASS(g_error_panel_parent_class)->finalize(G_OBJECT(panel));

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

static char *g_error_panel_class_get_key(const GErrorPanelClass *class)
{
    char *result;                           /* Description à renvoyer      */

    result = strdup(PANEL_ERRORS_ID);

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

static char *g_error_panel_class_get_path(const GErrorPanelClass *class)
{
    char *result;                           /* Emplacement à retourner     */

    result = strdup("Ms");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un panneau présentant la liste des erreurs rencontrées. *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GPanelItem *g_error_panel_new(void)
{
    GPanelItem *result;                     /* Structure à retourner       */

    result = g_object_new(G_TYPE_ERROR_PANEL, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : model = gestionnaire de données.                             *
*                a     = premier élément à traiter.                           *
*                b     = second élément à traiter.                            *
*                data  = donnée non utilisée ici.                             *
*                                                                             *
*  Description : Organise le tri des erreurs présentées.                      *
*                                                                             *
*  Retour      : Bilan de comparaison.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gint sort_errors_in_panel(GtkTreeModel *model, GtkTreeIter *a, GtkTreeIter *b, gpointer data)
{
    gint result;                            /* Bilan à faire remonter      */
    vmpa2t *addr_a;                         /* Localisation de A           */
    vmpa2t *addr_b;                         /* Localisation de B           */

    gtk_tree_model_get(model, a, ETC_ADDRESS, &addr_a, -1);
    gtk_tree_model_get(model, b, ETC_ADDRESS, &addr_b, -1);

    result = cmp_vmpa(addr_a, addr_b);

    delete_vmpa(addr_a);
    delete_vmpa(addr_b);

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

static void change_error_panel_current_content(GErrorPanel *panel, GLoadedContent *old, GLoadedContent *new)
{
    GLoadedBinary *binary;                  /* Autre version de l'instance */
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkListStore *store;                    /* Modèle de gestion           */

    if (G_IS_LOADED_BINARY(new))
        binary = G_LOADED_BINARY(new);
    else
        binary = NULL;

    /* Réinitialisation */

    if (panel->binary != NULL)
        g_object_unref(G_OBJECT(panel->binary));

    panel->binary = binary;

    if (panel->binary != NULL)
        g_object_ref(G_OBJECT(panel->binary));

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    store = GTK_LIST_STORE(gtk_builder_get_object(builder, "store"));

    gtk_list_store_clear(store);

    g_object_unref(G_OBJECT(builder));

    /* Actualisation de l'affichage */

    panel->count = 0;
    panel->kept = 0;

    if (binary != NULL)
        run_panel_update(G_UPDATABLE_PANEL(panel), PUI_0);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel  = panneau à mettre à jour.                            *
*                status = barre de statut à tenir informée.                   *
*                id     = identifiant pour le suivi de la progression.        *
*                data   = données complémentaire à manipuler.                 *
*                                                                             *
*  Description : Effectue la mise à jour du contenu du panneau d'erreurs.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void update_error_panel(const GErrorPanel *panel, GtkStatusStack *status, activity_id_t id, error_update_data *data)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkListStore *store;                    /* Modèle de gestion           */
    GBinFormat *format;                     /* Format du binaire           */
    size_t fcount;                          /* Quantité d'erreurs #1       */
    GArchProcessor *proc;                   /* Architecture du binaire     */
    size_t pcount;                          /* Quantité d'erreurs #2       */
    GtkToggleButton *button;                /* Bouton à manipuler          */
    gboolean show_format;                   /* Affichages liés au format   */
    gboolean show_disass;                   /* Affichages liés à l'arch.   */
    gboolean show_output;                   /* Affichages liés à la sortie */
    GtkTreeIter iter;                       /* Point d'insertion           */
    size_t i;                               /* Boucle de parcours          */
    error_desc_t error;                     /* Description de soucis       */
#ifndef NDEBUG
    bool ret;                               /* Bilan d'une récupération    */
#endif

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    store = GTK_LIST_STORE(gtk_builder_get_object(builder, "store"));

    /* Recensement initial */

    if (panel->binary != NULL)
    {
        format = G_BIN_FORMAT(g_loaded_binary_get_format(panel->binary));

        g_binary_format_lock_errors(format);

        fcount = g_binary_format_count_errors(format);

        proc = g_loaded_binary_get_processor(panel->binary);

        g_arch_processor_lock_errors(proc);

        pcount = g_arch_processor_count_errors(proc);

    }

    else
    {
        /* Pour GCC... */
        format = NULL;
        proc = NULL;

        fcount = 0;
        pcount = 0;

    }

    /* S'il n'y a aucun soucis à remonter... */

    if (panel->binary == NULL || (fcount + pcount) == 0)
    {
        button = GTK_TOGGLE_BUTTON(gtk_builder_get_object(builder, "format"));
        gtk_widget_set_sensitive(GTK_WIDGET(button), FALSE);

        button = GTK_TOGGLE_BUTTON(gtk_builder_get_object(builder, "disass"));
        gtk_widget_set_sensitive(GTK_WIDGET(button), FALSE);

        button = GTK_TOGGLE_BUTTON(gtk_builder_get_object(builder, "output"));
        gtk_widget_set_sensitive(GTK_WIDGET(button), FALSE);

        gtk_list_store_append(store, &iter);

        gtk_list_store_set(store, &iter,
                           ETC_ICON, NULL,
                           ETC_PHYS, _("<i>There is no error to display here.</i>"),
                           ETC_VIRT, NULL,
                           ETC_DESC, NULL,
                           ETC_VISIBLE, TRUE,
                           -1);

        data->count = 0;
        data->kept = 0;

    }

    /* Sinon on dresse la liste des doléances ! */

    else
    {
        button = GTK_TOGGLE_BUTTON(gtk_builder_get_object(builder, "format"));
        gtk_widget_set_sensitive(GTK_WIDGET(button), TRUE);
        show_format = gtk_toggle_button_get_active(button);

        button = GTK_TOGGLE_BUTTON(gtk_builder_get_object(builder, "disass"));
        gtk_widget_set_sensitive(GTK_WIDGET(button), TRUE);
        show_disass = gtk_toggle_button_get_active(button);

        button = GTK_TOGGLE_BUTTON(gtk_builder_get_object(builder, "output"));
        gtk_widget_set_sensitive(GTK_WIDGET(button), TRUE);
        show_output = gtk_toggle_button_get_active(button);


        gboolean is_error_visible(const error_desc_t *e, bool fmt)
        {
            gboolean visible;               /* Etat à retourner            */

            visible = FALSE;

            if (fmt)
            {
                if (show_format && e->ftype == BFE_SPECIFICATION)
                    visible = TRUE;

                else if (show_format && e->ftype == BFE_STRUCTURE)
                    visible = TRUE;

            }

            else
            {
                if (show_disass && e->ptype == APE_DISASSEMBLY)
                    visible = TRUE;

                else if (show_output && e->ptype == APE_LABEL)
                    visible = TRUE;

            }

            return visible;

        }

        cairo_surface_t *get_error_icon(const error_desc_t *e, bool fmt)
        {
            cairo_surface_t *icon;          /* Image associée à renvoyer   */

            icon = NULL;

            if (fmt)
            {
                if (show_format && e->ftype == BFE_SPECIFICATION)
                    icon = G_ERROR_PANEL_GET_CLASS(panel)->format_img;

                else if (show_format && e->ftype == BFE_STRUCTURE)
                    icon = G_ERROR_PANEL_GET_CLASS(panel)->format_img;

            }

            else
            {
                if (show_disass && e->ptype == APE_DISASSEMBLY)
                    icon = G_ERROR_PANEL_GET_CLASS(panel)->disass_img;

                else if (show_output && e->ptype == APE_LABEL)
                    icon = G_ERROR_PANEL_GET_CLASS(panel)->output_img;

            }

            return icon;

        }

        void add_error(const error_desc_t *e, bool fmt)
        {
            VMPA_BUFFER(phys);              /* Décalage physique           */
            VMPA_BUFFER(virt);              /* Position virtuelle          */
            gboolean state;                 /* Bilan d'un filtrage         */

            vmpa2_phys_to_string(&e->addr, MDS_UNDEFINED, phys, NULL);
            vmpa2_virt_to_string(&e->addr, MDS_UNDEFINED, virt, NULL);

            state = is_error_visible(e, fmt);

            gtk_list_store_append(store, &iter);

            gtk_list_store_set(store, &iter,
                               ETC_ICON, get_error_icon(e, fmt),
                               ETC_PHYS, phys,
                               ETC_VIRT, virt,
                               ETC_DESC, e->desc,
                               ETC_VISIBLE, state,
                               ETC_ORIGIN, fmt,
                               ETC_ERROR_TYPE, e->type,
                               ETC_ADDRESS, &e->addr,
                               -1);

            if (state)
                data->kept++;

        }


        for (i = 0; i < fcount; i++)
        {
            /* On remet à zéro tous les octets de l'union ! */
            error.type = 0;

#ifndef NDEBUG
            ret = g_binary_format_get_error(format, i, &error.ftype, &error.addr, &error.desc);
            assert(ret);
#else
            g_binary_format_get_error(format, i, &error.ftype, &error.addr, &error.desc);
#endif

            add_error(&error, true);

            free(error.desc);

            gtk_status_stack_update_activity_value(status, id, 1);

        }

        for (i = 0; i < pcount; i++)
        {
            /* On remet à zéro tous les octets de l'union ! */
            error.type = 0;

#ifndef NDEBUG
            ret = g_arch_processor_get_error(proc, i, &error.ptype, &error.addr, &error.desc);
            assert(ret);
#else
            g_arch_processor_get_error(proc, i, &error.ptype, &error.addr, &error.desc);
#endif

            add_error(&error, false);

            free(error.desc);

            gtk_status_stack_update_activity_value(status, id, 1);

        }

    }

    if (panel->binary != NULL)
    {
        g_arch_processor_unlock_errors(proc);

        g_object_unref(G_OBJECT(proc));

        g_binary_format_unlock_errors(format);

        g_object_unref(G_OBJECT(format));

    }

    g_object_unref(G_OBJECT(builder));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : button = bouton à l'origine de l'opération.                  *
*                panel  = panneau contenant les informations globales.        *
*                                                                             *
*  Description : Actualise l'affichage des erreurs sur la base des filtres.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_error_filter_toggled(GtkToggleButton *button, GErrorPanel *panel)
{
    run_panel_update(G_UPDATABLE_PANEL(panel), PUI_1);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel  = panneau à mettre à jour.                            *
*                status = barre de statut à tenir informée.                   *
*                id     = identifiant pour le suivi de la progression.        *
*                data   = données complémentaire à manipuler.                 *
*                                                                             *
*  Description : Filtre l'affichage du contenu du panneau d'erreurs.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void filter_error_panel(const GErrorPanel *panel, GtkStatusStack *status, activity_id_t id, error_update_data *data)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeModel *store;                    /* Modèle de gestion           */
    GtkToggleButton *button;                /* Bouton à manipuler          */
    gboolean show_format;                   /* Affichages liés au format   */
    gboolean show_disass;                   /* Affichages liés à l'arch.   */
    gboolean show_output;                   /* Affichages liés à la sortie */
    GtkTreeIter iter;                       /* Boucle de parcours          */
    gboolean valid;                         /* Validité du point courant   */
    gboolean format;                        /* Origine du soucis remonté   */
    guint error_type;                       /* Code d'erreur associé       */
    gboolean state;                         /* Bilan d'un filtrage         */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    store = GTK_TREE_MODEL(gtk_builder_get_object(builder, "store"));

    /* Actualisation des données */

    button = GTK_TOGGLE_BUTTON(gtk_builder_get_object(builder, "format"));
    show_format = gtk_toggle_button_get_active(button);

    button = GTK_TOGGLE_BUTTON(gtk_builder_get_object(builder, "disass"));
    show_disass = gtk_toggle_button_get_active(button);

    button = GTK_TOGGLE_BUTTON(gtk_builder_get_object(builder, "output"));
    show_output = gtk_toggle_button_get_active(button);


    gboolean is_error_visible(bool fmt, unsigned int type)
    {
        gboolean visible;                   /* Etat à retourner            */

        visible = FALSE;

        if (fmt)
        {
            if (show_format && type == BFE_SPECIFICATION)
                visible = TRUE;

            else if (show_format && type == BFE_STRUCTURE)
                visible = TRUE;

        }

        else
        {
            if (show_disass && type == APE_DISASSEMBLY)
                visible = TRUE;

            else if (show_output && type == APE_LABEL)
                visible = TRUE;

        }

        return visible;

    }


    for (valid = gtk_tree_model_get_iter_first(store, &iter);
         valid;
         valid = gtk_tree_model_iter_next(store, &iter))
    {
        gtk_tree_model_get(store, &iter, ETC_ORIGIN, &format, ETC_ERROR_TYPE, &error_type, -1);

        state = is_error_visible(format, error_type);

        gtk_list_store_set(GTK_LIST_STORE(store), &iter,
                           ETC_VISIBLE, state,
                           -1);

        if (state)
            data->kept++;

        gtk_status_stack_update_activity_value(status, id, 1);

    }

    g_object_unref(G_OBJECT(builder));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = structure contenant les informations maîtresses.     *
*                                                                             *
*  Description : Affiche un petit résumé concis des soucis remontés.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void update_error_panel_summary(const GErrorPanel *panel)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkLabel *summary;                      /* Etiquette à mettre à jour   */
    char *msg;                              /* Bilan à faire afficher      */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    summary = GTK_LABEL(gtk_builder_get_object(builder, "summary"));

    if (panel->count == 0)
        gtk_label_set_markup(summary, NULL);

    else
    {
        asprintf(&msg, _("<b>%zu</b> registered error%s, <b>%zu</b> displayed"),
                 panel->count, panel->count > 1 ? "s" : "", panel->kept);

        gtk_label_set_markup(summary, msg);

        free(msg);

    }

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

static void on_error_selection_changed(GtkTreeSelection *selection, gpointer unused)
{
    GtkTreeIter iter;                       /* Point de sélection          */
    GtkTreeModel *model;                    /* Modèle de gestion           */
    vmpa2t *addr;                           /* Localisation à suivre       */
    GLoadedPanel *panel;                    /* Afficheur effectif de code  */

    if (gtk_tree_selection_get_selected(selection, &model, &iter))
    {
        gtk_tree_model_get(model, &iter, ETC_ADDRESS, &addr, -1);

        if (addr != NULL)
        {
            panel = get_current_view();

            if (GTK_IS_DISPLAY_PANEL(panel))
                gtk_display_panel_request_move(GTK_DISPLAY_PANEL(panel), addr);

            g_object_unref(G_OBJECT(panel));

            delete_vmpa(addr);

        }

    }

}



/* ---------------------------------------------------------------------------------- */
/*                        MECANISMES DE MISE A JOUR DE PANNEAU                        */
/* ---------------------------------------------------------------------------------- */


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

static bool g_error_panel_setup(const GErrorPanel *panel, unsigned int uid, size_t *count, error_update_data **data, char **msg)
{
    bool result;                            /* Bilan à retourner           */
    GBinFormat *format;                     /* Format du binaire           */
    size_t fcount;                          /* Quantité d'erreurs #1       */
    GArchProcessor *proc;                   /* Architecture du binaire     */
    size_t pcount;                          /* Quantité d'erreurs #2       */

    result = true;

    *data = malloc(sizeof(error_update_data));

    switch (uid)
    {
        case PUI_0:

            format = G_BIN_FORMAT(g_loaded_binary_get_format(panel->binary));

            g_binary_format_lock_errors(format);
            fcount = g_binary_format_count_errors(format);
            g_binary_format_unlock_errors(format);

            g_object_unref(G_OBJECT(format));

            proc = g_loaded_binary_get_processor(panel->binary);

            g_arch_processor_lock_errors(proc);
            pcount = g_arch_processor_count_errors(proc);
            g_arch_processor_unlock_errors(proc);

            g_object_unref(G_OBJECT(proc));

            *count = fcount + pcount;

            *msg = strdup(_("Loading errors occurred during the disassembling process..."));

            (*data)->count = *count;
            (*data)->kept = 0;

            break;

        case PUI_1:

            *count = panel->count;

            *msg = strdup(_("Filtering errors occurred during the disassembling process..."));

            (*data)->count = panel->count;
            (*data)->kept = 0;

            break;

        default:    /* Pour GCC... */
            assert(false);
            result = false;
            break;

    }

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

static void g_error_panel_introduce(const GErrorPanel *panel, unsigned int uid, error_update_data *data)
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

static void g_error_panel_process(const GErrorPanel *panel, unsigned int uid, GtkStatusStack *status, activity_id_t id, error_update_data *data)
{
    switch (uid)
    {
        case PUI_0:
            update_error_panel(panel, status, id, data);
            break;

        case PUI_1:
            filter_error_panel(panel, status, id, data);
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

static void g_error_panel_conclude(GErrorPanel *panel, unsigned int uid, error_update_data *data)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeView *treeview;                  /* Arborescence graphique      */
    GArchProcessor *proc;                   /* Architecture du binaire     */
    GtkTreeViewColumn *virt_col;            /* Colonne des espaces virtuels*/
    GtkTreeModel *model;                    /* Source de données associée  */

    if (g_atomic_int_get(&G_PANEL_ITEM(panel)->switched) > 1)
        goto skip_this_step;

    /* Mise à jour des statistiques */

    panel->count = data->count;
    panel->kept = data->kept;

    update_error_panel_summary(panel);

    /* Basculement de l'affichage en ligne */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    treeview = GTK_TREE_VIEW(gtk_builder_get_object(builder, "treeview"));

    if (panel->binary != NULL)
    {
        proc = g_loaded_binary_get_processor(panel->binary);

        virt_col = gtk_tree_view_get_column(treeview, 1);

        gtk_tree_view_column_set_visible(virt_col, g_arch_processor_has_virtual_space(proc));

        g_object_unref(G_OBJECT(proc));

    }

    model = GTK_TREE_MODEL(gtk_builder_get_object(builder, "filter"));

    g_object_ref(G_OBJECT(model));
    gtk_tree_view_set_model(treeview, model);

    g_object_unref(G_OBJECT(builder));

 skip_this_step:

    g_panel_item_switch_to_updated_content(G_PANEL_ITEM(panel));

}
