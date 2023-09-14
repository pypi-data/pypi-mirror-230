
/* Chrysalide - Outil d'analyse de fichiers binaires
 * regedit.c - panneau d'affichage des paramètres de configuration
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


#include "regedit.h"


#include <assert.h>
#include <malloc.h>
#include <regex.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <gtk/gtk.h>


#include "../agroup.h"
#include "../panel-int.h"
#include "../../core/params.h"
#include "../../common/cpp.h"
#include "../../common/extstr.h"
#include "../../gtkext/easygtk.h"
#include "../../gtkext/named.h"



/* -------------------------- PARTIE PRINCIPALE DU PANNEAU -------------------------- */


/* Panneau d'affichage des paramètres de configuration (instance) */
struct _GRegeditPanel
{
    GPanelItem parent;                      /* A laisser en premier        */

    GGenConfig *config;                     /* Configuration à afficher    */

    regex_t *filter;                        /* Filtre appliqué ou NULL     */

    GtkMenu *menu;                          /* Menu contextuel pour param. */

};

/* Panneau d'affichage des paramètres de configuration (classe) */
struct _GRegeditPanelClass
{
    GPanelItemClass parent;                 /* A laisser en premier        */

};


/* Colonnes de la liste des messages */
typedef enum _CfgParamColumn
{
    CPC_PARAM,                              /* Paramètre présenté          */
    CPC_BOLD,                               /* Visuel des changements      */

    CPC_PATH,                               /* Chemin d'accès à une valeur */
    CPC_STATUS,                             /* Etat de la définition       */
    CPC_TYPE,                               /* Type de paramètre           */
    CPC_VALUE,                              /* Valeur courante             */

    LGC_COUNT                               /* Nombre de colonnes          */

} CfgParamColumn;




/* Initialise la classe des panneaux des paramètres de config. */
static void g_regedit_panel_class_init(GRegeditPanelClass *);

/* Initialise une instance de panneau de paramètres de config. */
static void g_regedit_panel_init(GRegeditPanel *);

/* Supprime toutes les références externes. */
static void g_regedit_panel_dispose(GRegeditPanel *);

/* Procède à la libération totale de la mémoire. */
static void g_regedit_panel_finalize(GRegeditPanel *);

/* Fournit le nom interne attribué à l'élément réactif. */
static char *g_regedit_panel_class_get_key(const GRegeditPanelClass *);

/* Indique le chemin initial de la localisation d'un panneau. */
static char *g_regedit_panel_class_get_path(const GRegeditPanelClass *);



/* ------------------------- AFFICHAGE A L'AIDE D'UNE LISTE ------------------------- */


/* Recharge une configuration donnée à l'affichage. */
static void reload_config_into_treeview(GRegeditPanel *);

/* Actualise l'affichage des données d'un paramètre modifié. */
static void on_configuration_param_modified(GGenConfig *, GCfgParam *, GRegeditPanel *);

/* Actualise la valeur affichée d'un paramètre de configuration. */
static void update_config_param_value(GtkListStore *, GtkTreeIter *);

/* Etablit une comparaison entre deux lignes de paramètres. */
static gint compare_config_list_columns(GtkTreeModel *, GtkTreeIter *, GtkTreeIter *, gpointer);

/* Réagit à une pression sur <Shift+F2> et simule l'édition. */
static gboolean on_key_pressed_over_params(GtkTreeView *, GdkEventKey *, GRegeditPanel *);

/* Réagit à une édition de la valeur d'un paramètre. */
static void on_param_value_edited(GtkCellRendererText *, gchar *, gchar *, GRegeditPanel *);



/* ------------------------- FILTRAGE DES SYMBOLES PRESENTS ------------------------- */


/* Démarre l'actualisation du filtrage des paramètres. */
static void on_param_search_changed(GtkSearchEntry *, GRegeditPanel *);

/* Détermine si un paramètre doit être filtré ou non. */
static bool is_param_filtered(GRegeditPanel *, const char *);



/* ------------------------ ATTRIBUTION D'UN MENU CONTEXTUEL ------------------------ */


/* Assure la gestion des clics de souris sur les paramètres. */
static gboolean on_button_press_over_params(GtkWidget *, GdkEventButton *, GRegeditPanel *);

/* Construit le menu contextuel pour les paramètres. */
GtkMenu *build_param_panel_menu(GRegeditPanel *);

/* Fournit le paramètre sélectionné dans la liste. */
static GCfgParam *get_selected_panel_param(GtkTreeView *, GtkTreeIter *);

/* Réagit avec le menu "Copier le nom". */
static void mcb_param_panel_copy(GtkMenuItem *, GRegeditPanel *);

/* Réagit avec le menu "Valeur néant". */
static void mcb_param_panel_empty(GtkMenuItem *, GRegeditPanel *);

/* Réagit avec le menu "Réinitialiser la valeur". */
static void mcb_param_panel_reset(GtkMenuItem *, GRegeditPanel *);



/* ---------------------------------------------------------------------------------- */
/*                            PARTIE PRINCIPALE DU PANNEAU                            */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un panneau d'aperçu de graphiques. */
G_DEFINE_TYPE(GRegeditPanel, g_regedit_panel, G_TYPE_PANEL_ITEM);


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

static void g_regedit_panel_class_init(GRegeditPanelClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GEditorItemClass *item;                 /* Encore une autre vision...  */
    GPanelItemClass *panel;                 /* Version parente de la classe*/

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_regedit_panel_dispose;
    object->finalize = (GObjectFinalizeFunc)g_regedit_panel_finalize;

    item = G_EDITOR_ITEM_CLASS(class);

    item->get_key = (get_item_key_fc)g_regedit_panel_class_get_key;

    panel = G_PANEL_ITEM_CLASS(class);

    panel->dock_at_startup = gtk_panel_item_class_return_false;
    panel->get_path = (get_panel_path_fc)g_regedit_panel_class_get_path;

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

static void g_regedit_panel_init(GRegeditPanel *panel)
{
    GPanelItem *pitem;                      /* Version parente du panneau  */
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GObject *vrenderer;                     /* Moteur de rendu de colonne  */
    GtkTreeSortable *sortable;              /* Autre vision de la liste    */

    /* Eléments de base */

    pitem = G_PANEL_ITEM(panel);

    pitem->widget = G_NAMED_WIDGET(gtk_built_named_widget_new_for_panel(_("Configuration"),
                                                                        _("Configuration parameters"),
                                                                        PANEL_REGEDIT_ID));

    panel->config = get_main_configuration();
    g_object_ref(G_OBJECT(panel->config));

    /* Représentation graphique */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(pitem->widget));

    vrenderer = G_OBJECT(gtk_builder_get_object(builder, "vrenderer"));

    g_object_set(vrenderer, "editable", TRUE, NULL);

    /* Tri de la liste */

    sortable = GTK_TREE_SORTABLE(gtk_builder_get_object(builder, "store"));

    gtk_tree_sortable_set_sort_func(sortable, CPC_PATH, compare_config_list_columns,
                                    GINT_TO_POINTER(CPC_PATH), NULL);

    gtk_tree_sortable_set_sort_func(sortable, CPC_STATUS, compare_config_list_columns,
                                    GINT_TO_POINTER(CPC_STATUS), NULL);

    gtk_tree_sortable_set_sort_func(sortable, CPC_TYPE, compare_config_list_columns,
                                    GINT_TO_POINTER(CPC_TYPE), NULL);

    gtk_tree_sortable_set_sort_func(sortable, CPC_VALUE, compare_config_list_columns,
                                    GINT_TO_POINTER(CPC_VALUE), NULL);

    gtk_tree_sortable_set_sort_column_id(sortable, CPC_PATH, GTK_SORT_ASCENDING);

    /* Préparation du menu contextuel */

    panel->menu = build_param_panel_menu(panel);

    /* Connexion des signaux */

    gtk_builder_add_callback_symbols(builder,
                                     BUILDER_CALLBACK(on_param_search_changed),
                                     BUILDER_CALLBACK(track_focus_change_in_text_area),
                                     BUILDER_CALLBACK(on_button_press_over_params),
                                     BUILDER_CALLBACK(on_key_pressed_over_params),
                                     BUILDER_CALLBACK(on_param_value_edited),
                                     NULL);

    gtk_builder_connect_signals(builder, panel);

    g_object_unref(G_OBJECT(builder));

    /* Actualisation du contenu du panneau */

    reload_config_into_treeview(panel);

    g_signal_connect(panel->config, "modified", G_CALLBACK(on_configuration_param_modified), panel);

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

static void g_regedit_panel_dispose(GRegeditPanel *panel)
{
    if (panel->config != NULL)
        g_signal_handlers_disconnect_by_func(panel->config, G_CALLBACK(on_configuration_param_modified), panel);

    g_clear_object(&panel->config);

    G_OBJECT_CLASS(g_regedit_panel_parent_class)->dispose(G_OBJECT(panel));

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

static void g_regedit_panel_finalize(GRegeditPanel *panel)
{
    if (panel->filter != NULL)
    {
        regfree(panel->filter);
        free(panel->filter);
    }

    G_OBJECT_CLASS(g_regedit_panel_parent_class)->finalize(G_OBJECT(panel));

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

static char *g_regedit_panel_class_get_key(const GRegeditPanelClass *class)
{
    char *result;                           /* Description à renvoyer      */

    result = strdup(PANEL_REGEDIT_ID);

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

static char *g_regedit_panel_class_get_path(const GRegeditPanelClass *class)
{
    char *result;                           /* Emplacement à retourner     */

    result = strdup("M");

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

GPanelItem *g_regedit_panel_new(void)
{
    GPanelItem *result;                     /* Structure à retourner       */

    result = g_object_new(G_TYPE_REGEDIT_PANEL, NULL);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                           AFFICHAGE A L'AIDE D'UNE LISTE                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau d'affichage de paramètres de configuration.  *
*                                                                             *
*  Description : Recharge une configuration donnée à l'affichage.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void reload_config_into_treeview(GRegeditPanel *panel)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkListStore *store;                    /* Modèle de gestion           */
    GList *params;                          /* Paramètres de configuration */
    GCfgParam *param;                       /* Paramètre en cours d'étude  */
    GList *p;                               /* Boucle de parcours          */
    char *type_desc;                        /* Type de paramètre           */
    GtkTreeIter iter;                       /* Point d'insertion           */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    store = GTK_LIST_STORE(gtk_builder_get_object(builder, "store"));

    gtk_list_store_clear(store);

    g_generic_config_rlock(panel->config);

    params = g_generic_config_list_params(panel->config);

    for (p = g_list_first(params); p != NULL; p = g_list_next(p))
    {
        param = G_CFG_PARAM(p->data);

        if (is_param_filtered(panel, g_config_param_get_path(param)))
            continue;

        switch (g_config_param_get_ptype(param))
        {
            case CPT_BOOLEAN:
                type_desc = _("Boolean");
                break;

            case CPT_INTEGER:
                type_desc = _("Integer");
                break;

            case CPT_ULONG:
                type_desc = _("Unsigned long");
                break;

            case CPT_STRING:
                type_desc = _("String");
                break;

            case CPT_COLOR:
                type_desc = _("Color");
                break;

            default:
                type_desc = _("<Unknown type>");
                break;

        }

        gtk_list_store_append(store, &iter);
        gtk_list_store_set(store, &iter,
                           CPC_PARAM, param,
                           CPC_PATH, g_config_param_get_path(param),
                           CPC_TYPE, type_desc,
                           -1);

        update_config_param_value(store, &iter);

    }

    g_generic_config_runlock(panel->config);

    g_object_unref(G_OBJECT(builder));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : config = configuration changée dans son ensemble.            *
*                param  = instance dont le contenu a évolué.                  *
*                panel  = panneau d'affichage de paramètres à mettre à jour.  *
*                                                                             *
*  Description : Actualise l'affichage des données d'un paramètre modifié.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_configuration_param_modified(GGenConfig *config, GCfgParam *param, GRegeditPanel *panel)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeView *treeview;                  /* Affichage de la liste       */
    GtkTreeModel *model;                    /* Gestionnaire de données     */
    GtkTreeIter iter;                       /* Point de recherche          */
    gboolean looping;                       /* Autorisation de bouclage    */
    GCfgParam *item;                        /* Elément de la liste         */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    treeview = GTK_TREE_VIEW(gtk_builder_get_object(builder, "treeview"));

    model = gtk_tree_view_get_model(treeview);

    for (looping = gtk_tree_model_get_iter_first(model, &iter);
         looping;
         looping = gtk_tree_model_iter_next(model, &iter))
    {
        gtk_tree_model_get(model, &iter, CPC_PARAM, &item, -1);

        if (item == param)
        {
            update_config_param_value(GTK_LIST_STORE(model), &iter);
            break;
        }

    }

    g_object_unref(G_OBJECT(builder));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : store = gestionnaire du tableau de données.                  *
*                iter  = point de modification dans les lignes.               *
*                param = paramètre dont la valeur est à afficher.             *
*                                                                             *
*  Description : Actualise la valeur affichée d'un paramètre de configuration.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void update_config_param_value(GtkListStore *store, GtkTreeIter *iter)
{
    GCfgParam *param;                       /* Paramètre à consulter       */
    ConfigParamState state;                 /* Etat du paramètre           */
    char *state_desc;                       /* Version chaînée de l'état   */
    bool boolean;                           /* Valeur booléenne            */
    int integer;                            /* Valeur entière              */
    char int_val[sizeof(XSTR(INT_MIN)) + 1];/* Valeur en chaîne de carac.  */
    unsigned long ulong;                    /* Valeur entière positive     */
    char ul_val[sizeof(XSTR(ULONG_MAX)) + 1];/* Valeur en chaîne de carac. */
    char *string;                           /* Chaîne de caractères        */
    char *desc;                             /* Description à afficher      */

    gtk_tree_model_get(GTK_TREE_MODEL(store), iter, CPC_PARAM, &param, -1);

    state = g_config_param_get_state(param);

    if (state & CPS_DEFAULT)
        state_desc = strdup(_("By default"));
    else
        state_desc = strdup(_("Changed"));

    if (state & CPS_EMPTY)
        state_desc = stradd(state_desc, _(" + empty"));

    if (state & CPS_EMPTY)
        desc = "";

    else
        switch (g_config_param_get_ptype(param))
        {
            case CPT_BOOLEAN:
                g_config_param_get_value(param, &boolean);
                desc = (boolean ? _("true") : _("false"));
                break;

            case CPT_INTEGER:
                g_config_param_get_value(param, &integer);
                snprintf(int_val, sizeof(int_val), "%d", integer);
                desc = int_val;
                break;

            case CPT_ULONG:
                g_config_param_get_value(param, &ulong);
                snprintf(ul_val, sizeof(ul_val), "%lu", ulong);
                desc = ul_val;
                break;

            case CPT_STRING:
                g_config_param_get_value(param, &string);
                desc = (string != NULL ? string : "");
                break;

            case CPT_COLOR:
                desc = "<color>";
                break;

            default:
                assert(false);
                desc = "???";
                break;

        }

    gtk_list_store_set(store, iter,
                       CPC_BOLD, state & CPS_DEFAULT ? 400 : 800,
                       CPC_STATUS, state_desc,
                       CPC_VALUE, desc, -1);

    free(state_desc);

    g_object_unref(G_OBJECT(param));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : model  = gestionnaire du tableau de données.                 *
*                a      = première ligne de données à traiter.                *
*                b      = seconde ligne de données à traiter.                 *
*                column = indice de la colonne à considérer, encodée.         *
*                                                                             *
*  Description : Etablit une comparaison entre deux lignes de paramètres.     *
*                                                                             *
*  Retour      : Indication de tri entre les deux lignes fournies.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gint compare_config_list_columns(GtkTreeModel *model, GtkTreeIter *a, GtkTreeIter *b, gpointer column)
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

static gboolean on_key_pressed_over_params(GtkTreeView *treeview, GdkEventKey *event, GRegeditPanel *panel)
{
    const gchar *accelerator;               /* Combinaison de raccourci    */
    guint accel_key;                        /* Touche de raccourci         */
    GdkModifierType accel_mod;              /* Modifiateurs attendus aussi */
    GtkTreeIter iter;                       /* Point de la sélection       */
    GtkTreeModel *model;                    /* Gestionnaire de données     */
    GtkTreePath *path;                      /* Chemin d'accès à ce point   */

    if (!g_generic_config_get_value(get_main_configuration(), MPK_KEYBINDINGS_EDIT, &accelerator))
        return FALSE;

    if (accelerator == NULL)
        return FALSE;

    gtk_accelerator_parse(accelerator, &accel_key, &accel_mod);

    if (event->keyval == accel_key && event->state == accel_mod)
    {
        if (get_selected_panel_param(treeview, &iter) != NULL)
        {
            model = gtk_tree_view_get_model(treeview);
            path = gtk_tree_model_get_path(model, &iter);

            gtk_tree_view_set_cursor(treeview, path,
                                     gtk_tree_view_get_column(treeview, CPC_VALUE - CPC_PATH),
                                     TRUE);

            gtk_tree_path_free(path);

        }

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
*  Description : Réagit à une édition de la valeur d'un paramètre.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_param_value_edited(GtkCellRendererText *renderer, gchar *path, gchar *new, GRegeditPanel *panel)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkListStore *store;                    /* Modèle de gestion           */
    GtkTreePath *tree_path;                 /* Chemin d'accès natif        */
    GtkTreeIter iter;                       /* Point de la modification    */
    GCfgParam *param;                       /* Paramètre à actualiser      */
    bool boolean;                           /* Valeur booléenne            */
    int integer;                            /* Valeur entière              */
    int ulong;                              /* Valeur entière positive     */
    char *end;                              /* Pointeur vers '\0' final ?  */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    store = GTK_LIST_STORE(gtk_builder_get_object(builder, "store"));

    tree_path = gtk_tree_path_new_from_string(path);
    if (tree_path == NULL) goto bad_path;

    if (!gtk_tree_model_get_iter(GTK_TREE_MODEL(store), &iter, tree_path))
        goto opve_bad_iter;

    gtk_tree_model_get(GTK_TREE_MODEL(store), &iter, CPC_PARAM, &param, -1);

    switch (g_config_param_get_ptype(param))
    {
        case CPT_BOOLEAN:

            if (strcmp(new, "true") != 0 && strcmp(new, "false") != 0)
                goto opve_bad_value;

            boolean = (strcmp(new, "true") == 0);
            g_config_param_set_value(param, boolean);

            break;

        case CPT_INTEGER:

            integer = strtol(new, &end, 10);
            if (*end != '\0') goto opve_bad_value;
 
            g_config_param_set_value(param, integer);

            break;

        case CPT_ULONG:

            ulong = strtoul(new, &end, 10);
            if (*end != '\0') goto opve_bad_value;

            g_config_param_set_value(param, ulong);

            break;

        case CPT_STRING:
            g_config_param_set_value(param, new);
            break;

        case CPT_COLOR:
            break;

        default:
            assert(false);
            goto opve_bad_value;
            break;

    }

 opve_bad_value:

    g_object_unref(G_OBJECT(param));

 opve_bad_iter:

    gtk_tree_path_free(tree_path);

 bad_path:

    g_object_unref(G_OBJECT(builder));

}



/* ---------------------------------------------------------------------------------- */
/*                           FILTRAGE DES SYMBOLES PRESENTS                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : entry = entrée de texte contenant le filtre brut.            *
*                panel = panneau assurant l'affichage des paramètres.         *
*                                                                             *
*  Description : Démarre l'actualisation du filtrage des paramètres.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_param_search_changed(GtkSearchEntry *entry, GRegeditPanel *panel)
{
    const gchar *text;                      /* Texte de l'utilisateur      */
    GtkStyleContext *context;               /* Contexte du thème actuel    */
    int ret;                                /* Bilan de mise en place      */

    if (panel->filter != NULL)
    {
        regfree(panel->filter);
        free(panel->filter);
        panel->filter = NULL;
    }

    text = gtk_entry_get_text(GTK_ENTRY(entry));

    context = gtk_widget_get_style_context(GTK_WIDGET(entry));

    if (strlen(text) > 0)
    {
        panel->filter = (regex_t *)calloc(1, sizeof(regex_t));
        ret = regcomp(panel->filter, text, REG_EXTENDED);

        if (ret != 0)
        {
            free(panel->filter);
            panel->filter = NULL;

            gtk_style_context_add_class(context, "filter-error");
            return;

        }

    }

    gtk_style_context_remove_class(context, "filter-error");

    reload_config_into_treeview(panel);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau assurant l'affichage des paramètres.         *
*                name  = chemin d'accès au paramètre à traiter.               *
*                                                                             *
*  Description : Détermine si un paramètre doit être filtré ou non.           *
*                                                                             *
*  Retour      : true si le paramètre ne doit pas être affiché, false sinon.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool is_param_filtered(GRegeditPanel *panel, const char *name)
{
    regmatch_t match;                       /* Récupération des trouvailles*/
    int ret;                                /* Bilan du filtrage           */

    if (panel->filter == NULL)
        return false;

    ret = regexec(panel->filter, name, 1, &match, 0);
    if (ret == REG_NOMATCH)
        return true;

    return false;

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
*  Description : Assure la gestion des clics de souris sur les paramètres.    *
*                                                                             *
*  Retour      : FALSE pour poursuivre la propagation de l'événement.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean on_button_press_over_params(GtkWidget *widget, GdkEventButton *event, GRegeditPanel *panel)
{
    if (event->button == 3)
        gtk_menu_popup_at_pointer(panel->menu, (GdkEvent *)event);

    return FALSE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = panneau d'affichage des paramètres de configuration. *
*                                                                             *
*  Description : Construit le menu contextuel pour les paramètres.            *
*                                                                             *
*  Retour      : Panneau de menus mis en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkMenu *build_param_panel_menu(GRegeditPanel *panel)
{
    GtkWidget *result;                      /* Support à retourner         */
    GtkWidget *submenuitem;                 /* Sous-élément de menu        */

    result = qck_create_menu(NULL);

    submenuitem = qck_create_menu_item(NULL, NULL, _("Copy the name"), G_CALLBACK(mcb_param_panel_copy), panel);
    gtk_container_add(GTK_CONTAINER(result), submenuitem);

    submenuitem = qck_create_menu_separator();
    gtk_container_add(GTK_CONTAINER(result), submenuitem);

    submenuitem = qck_create_menu_item(NULL, NULL, _("Make empty"), G_CALLBACK(mcb_param_panel_empty), panel);
    gtk_container_add(GTK_CONTAINER(result), submenuitem);

    submenuitem = qck_create_menu_item(NULL, NULL, _("Reset"), G_CALLBACK(mcb_param_panel_reset), panel);
    gtk_container_add(GTK_CONTAINER(result), submenuitem);

    return GTK_MENU(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : treeview = liste d'affichage à consulter.                    *
*                save     = zone de conservation du point de trouvaille. [OUT]*
*                                                                             *
*  Description : Fournit le paramètre sélectionné dans la liste.              *
*                                                                             *
*  Retour      : Paramètre en cours d'édition ou NULL en cas de soucis.       *
*                                                                             *
*  Remarques   : Le résultat non nul est à déréférencer après usage.          *
*                                                                             *
******************************************************************************/

static GCfgParam *get_selected_panel_param(GtkTreeView *treeview, GtkTreeIter *save)
{
    GCfgParam *result;                      /* Paramètre à renvoyer        */
    GtkTreeSelection *selection;            /* Représentation de sélection */
    GtkTreeModel *model;                    /* Gestionnaire des données    */
    GtkTreeIter iter;                       /* Point de la sélection       */

    result = NULL;

    selection = gtk_tree_view_get_selection(treeview);

    if (gtk_tree_selection_get_selected(selection, &model, &iter))
        gtk_tree_model_get(model, &iter, CPC_PARAM, &result, -1);

    if (save != NULL)
        *save = iter;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                panel    = panneau d'affichage des paramètres de config.     *
*                                                                             *
*  Description : Réagit avec le menu "Copier le nom".                         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_param_panel_copy(GtkMenuItem *menuitem, GRegeditPanel *panel)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeView *treeview;                  /* Affichage de la liste       */
    GCfgParam *param;                       /* Paramètre sélectionné       */
    const char *content;                    /* Prochain contenu à diffuser */
    gint clen;                              /* Taille de ce contenu        */
    GtkClipboard *clipboard;                /* Presse-papiers à remplir    */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    treeview = GTK_TREE_VIEW(gtk_builder_get_object(builder, "treeview"));

    param = get_selected_panel_param(treeview, NULL);

    if (param == NULL)
    {
        content = g_config_param_get_path(param);
        clen = g_utf8_strlen(content, -1);

        clipboard = gtk_clipboard_get(GDK_SELECTION_CLIPBOARD);
        gtk_clipboard_set_text(clipboard, content, clen);

        clipboard = gtk_clipboard_get(GDK_SELECTION_PRIMARY);
        gtk_clipboard_set_text(clipboard, content, clen);

        g_object_unref(G_OBJECT(param));

    }

    g_object_unref(G_OBJECT(builder));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                panel    = panneau d'affichage des paramètres de config.     *
*                                                                             *
*  Description : Réagit avec le menu "Valeur néant".                          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_param_panel_empty(GtkMenuItem *menuitem, GRegeditPanel *panel)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeView *treeview;                  /* Affichage de la liste       */
    GCfgParam *param;                       /* Paramètre sélectionné       */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    treeview = GTK_TREE_VIEW(gtk_builder_get_object(builder, "treeview"));

    param = get_selected_panel_param(treeview, NULL);

    if (param == NULL)
    {
        g_config_param_make_empty(param);

        g_object_unref(G_OBJECT(param));

    }

    g_object_unref(G_OBJECT(builder));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                panel    = panneau d'affichage des paramètres de config.     *
*                                                                             *
*  Description : Réagit avec le menu "Réinitialiser".                         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_param_panel_reset(GtkMenuItem *menuitem, GRegeditPanel *panel)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeView *treeview;                  /* Affichage de la liste       */
    GCfgParam *param;                       /* Paramètre sélectionné       */

    builder = gtk_built_named_widget_get_builder(GTK_BUILT_NAMED_WIDGET(G_PANEL_ITEM(panel)->widget));

    treeview = GTK_TREE_VIEW(gtk_builder_get_object(builder, "treeview"));

    param = get_selected_panel_param(treeview, NULL);

    if (param == NULL)
    {
        g_config_param_reset(param);

        g_object_unref(G_OBJECT(param));

    }

    g_object_unref(G_OBJECT(builder));

}
