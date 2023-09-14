
/* Chrysalide - Outil d'analyse de fichiers binaires
 * loading.c - fenêtre de chargement de nouveaux contenus
 *
 * Copyright (C) 2020 Cyrille Bagard
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


#include "loading.h"


#include <assert.h>
#include <malloc.h>
#include <stdio.h>
#include <gdk/gdkkeysyms.h>


#include <i18n.h>


#include "../../analysis/binary.h"
#include "../../core/processors.h"
#include "../../gtkext/easygtk.h"



/* Colonnes de la liste des contenus chargés */
typedef enum _LoadedContentColumn
{
    LCC_NAME,                               /* Désignation humaine         */
    LCC_CONTENT,                            /* Contenu chargé              */
    LCC_PROJECT,                            /* Cadre du chargement         */
    LCC_RECOGNIZED,                       /* Binaire brut ?              */

} LoadedContentColumn;


/* Réagit à un changement de sélection des contenus chargés. */
static void on_loaded_selection_changed(GtkTreeSelection *, GtkBuilder *);

/* Réagit à un changement de mode de chargement. */
static void on_load_mode_toggled(GtkToggleButton *, GtkBuilder *);

/* Réagit à une pression de la touche "Echappe". */
static gboolean on_key_press_event(GtkWidget *, GdkEventKey *, GtkBuilder *);

/* Réagit à un clic sur la bouton "Annuler". */
static void on_cancel_clicked(GtkButton *, GtkBuilder *);

/* Réagit à un clic sur la bouton "Valider". */
static void on_validate_clicked(GtkButton *, GtkBuilder *);

/* Actualise les moyens affichés dans la boîte de chargement. */
static void update_loading_dialog(GtkBuilder *);

/* Actualise le décompte des différents types de binaires. */
static void update_loading_dialog_counter(GtkBuilder *);



/******************************************************************************
*                                                                             *
*  Paramètres  : parent = fenêtre principale de l'éditeur.                    *
*                outb   = constructeur à détruire après usage. [OUT]          *
*                                                                             *
*  Description : Construit une boîte de dialogue dédiée aux chargements.      *
*                                                                             *
*  Retour      : Adresse de la fenêtre mise en place.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *create_loading_dialog(GtkWindow *parent, GtkBuilder **outb)
{
    GtkWidget *result;                      /* Fenêtre à renvoyer          */
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkTreeModelFilter *filter;             /* Modèle filtrant             */

    builder = gtk_builder_new_from_resource("/org/chrysalide/gui/dialogs/loading.ui");
    *outb = builder;

    result = GTK_WIDGET(gtk_builder_get_object(builder, "window"));

    gtk_window_set_transient_for(GTK_WINDOW(result), parent);

    filter = GTK_TREE_MODEL_FILTER(gtk_builder_get_object(builder, "filtered_store"));
    gtk_tree_model_filter_set_visible_column(filter, LCC_RECOGNIZED);

    /* Connexion des signaux */

    gtk_builder_add_callback_symbols(builder,
                                     BUILDER_CALLBACK(on_loaded_selection_changed),
                                     BUILDER_CALLBACK(on_load_mode_toggled),
                                     BUILDER_CALLBACK(on_key_press_event),
                                     BUILDER_CALLBACK(on_cancel_clicked),
                                     BUILDER_CALLBACK(on_validate_clicked),
                                     NULL);

    gtk_builder_connect_signals(builder, builder);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : selection = gestionnaire de sélection impacté.               *
*                builder   = constructeur à utiliser.                         *
*                                                                             *
*  Description : Réagit à un changement de sélection des contenus chargés.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_loaded_selection_changed(GtkTreeSelection *selection, GtkBuilder *builder)
{
    GtkTreeModel *model;                    /* Modèle de gestion           */
    GtkTreeIter iter;                       /* Point de sélection          */
    gboolean state;                         /* Présence d'une sélection    */
    GtkWidget *widget;                      /* Composant à actualiser      */
    const char *id;                         /* Identifiant d'architecture  */
    GLoadedContent *loaded;                 /* Contenu chargé              */
    GExeFormat *format;                     /* Format binaire reconnu      */
    GtkComboBox *combobox;                  /* Sélection d'architecture    */

    /* Mise à jour des accès */

    state = gtk_tree_selection_get_selected(selection, &model, &iter);

    widget = GTK_WIDGET(gtk_builder_get_object(builder, "load_all"));
    gtk_widget_set_sensitive(widget, state);

    widget = GTK_WIDGET(gtk_builder_get_object(builder, "load_one"));
    gtk_widget_set_sensitive(widget, state);

    on_load_mode_toggled(NULL, builder);

    widget = GTK_WIDGET(gtk_builder_get_object(builder, "ok_button"));
    gtk_widget_set_sensitive(widget, state);

    /* Mise à jour de l'architecture */

    id = "none";

    if (state)
    {
        gtk_tree_model_get(model, &iter, LCC_CONTENT, &loaded, -1);

        if (G_IS_LOADED_BINARY(loaded))
        {
            format = g_loaded_binary_get_format(G_LOADED_BINARY(loaded));

            id = g_exe_format_get_target_machine(format);

            g_object_unref(G_OBJECT(format));

        }

        g_object_unref(G_OBJECT(loaded));

    }

    combobox = GTK_COMBO_BOX(gtk_builder_get_object(builder, "arch_sel"));

    gtk_combo_box_set_active_id(combobox, id);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : button  = bouton à l'origine de la procédure.                *
*                builder = espace de référencement global.                    *
*                                                                             *
*  Description : Réagit à un changement de mode de chargement.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_load_mode_toggled(GtkToggleButton *button, GtkBuilder *builder)
{
    GtkToggleButton *all_button;            /* Selection de mode           */
    gboolean state;                         /* Chargement fin ?            */
    GtkTreeView *treeview;                  /* Vue en arboresence          */
    GtkTreeSelection *selection;            /* Sélection associée          */
    GtkWidget *widget;                      /* Composant à actualiser      */

    all_button = GTK_TOGGLE_BUTTON(gtk_builder_get_object(builder, "load_all"));

    state = !gtk_toggle_button_get_active(all_button);

    if (state)
    {
        treeview = GTK_TREE_VIEW(gtk_builder_get_object(builder, "treeview"));
        selection = gtk_tree_view_get_selection(treeview);

        state = gtk_tree_selection_get_selected(selection, NULL, NULL);

    }

    widget = GTK_WIDGET(gtk_builder_get_object(builder, "arch_label"));
    gtk_widget_set_sensitive(widget, state);

    widget = GTK_WIDGET(gtk_builder_get_object(builder, "arch_sel"));
    gtk_widget_set_sensitive(widget, state);

    widget = GTK_WIDGET(gtk_builder_get_object(builder, "config_and_run"));
    gtk_widget_set_sensitive(widget, state);

    widget = GTK_WIDGET(gtk_builder_get_object(builder, "process_remaining"));
    gtk_widget_set_sensitive(widget, state);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget  = composant graphique visé par la procédure.         *
*                event   = informations liées à l'événement.                  *
*                builder = espace de référencement global.                    *
*                                                                             *
*  Description : Réagit à une pression de la touche "Echappe".                *
*                                                                             *
*  Retour      : TRUE pour indiquer une prise en compte, FALSE sinon.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean on_key_press_event(GtkWidget *widget, GdkEventKey *event, GtkBuilder *builder)
{
    gboolean result;                        /* Bilan à retourner           */

    if (event->keyval == GDK_KEY_Escape)
    {
        on_cancel_clicked(NULL, builder);
        result = TRUE;
    }

    else
        result = FALSE;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : button  = bouton à l'origine de la procédure.                *
*                builder = espace de référencement global.                    *
*                                                                             *
*  Description : Réagit à un clic sur la bouton "Annuler".                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_cancel_clicked(GtkButton *button, GtkBuilder *builder)
{
    GtkWidget *window;                      /* Fenêtre à cacher            */

    /* Disparition de la fenêtre */

    window = GTK_WIDGET(gtk_builder_get_object(builder, "window"));

    gtk_widget_hide(window);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : button  = bouton à l'origine de la procédure.                *
*                builder = espace de référencement global.                    *
*                                                                             *
*  Description : Réagit à un clic sur la bouton "Valider".                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_validate_clicked(GtkButton *button, GtkBuilder *builder)
{
    GtkTreeView *treeview;                  /* Vue en arboresence          */
    GtkTreeSelection *selection;            /* Sélection associée          */
    GtkTreeModel *model;                    /* Modèle de gestion           */
    GtkTreeIter iter;                       /* Point de sélection          */
    GLoadedContent *loaded;                 /* Contenu chargé              */
    GStudyProject *project;                 /* projet associé              */

    treeview = GTK_TREE_VIEW(gtk_builder_get_object(builder, "treeview"));
    selection = gtk_tree_view_get_selection(treeview);

    if (gtk_tree_selection_get_selected(selection, &model, &iter))
    {
        gtk_tree_model_get(model, &iter, LCC_CONTENT, &loaded, LCC_PROJECT, &project, -1);

        g_signal_connect(loaded, "analyzed", G_CALLBACK(on_loaded_content_analyzed), project);

        g_loaded_content_analyze(loaded, true, true);

        g_object_unref(G_OBJECT(loaded));

    }

    /* Disparition de la fenêtre ? */

    if (true)
        on_cancel_clicked(NULL, builder);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : builder = constructeur à utiliser.                           *
*                                                                             *
*  Description : Actualise les moyens affichés dans la boîte de chargement.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void update_loading_dialog(GtkBuilder *builder)
{
    GtkComboBoxText *combobox;              /* Sélection d'architecture    */
    char **keys;                            /* Liste des architectures     */
    size_t count;                           /* Taille de cette liste       */
    size_t i;                               /* Boucle de parcours          */
    GArchProcessor *proc;                   /* Processeur à consulter      */
    char *desc;                             /* Description humaine         */

    /* Mise à jour de la liste des architectures */

    combobox = GTK_COMBO_BOX_TEXT(gtk_builder_get_object(builder, "arch_sel"));

    gtk_combo_box_text_remove_all(combobox);

    gtk_combo_box_text_append(combobox, "none", _("None"));

    keys = get_all_processor_keys(&count);

    for (i = 0; i < count; i++)
    {
        proc = get_arch_processor_for_key(keys[i]);

        desc = g_arch_processor_get_desc(proc);

        gtk_combo_box_text_append(combobox, keys[i], desc);

        g_object_unref(G_OBJECT(proc));
        free(keys[i]);

    }

    if (keys != NULL)
        free(keys);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : builder = constructeur à utiliser.                           *
*                                                                             *
*  Description : Actualise le décompte des différents types de binaires.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void update_loading_dialog_counter(GtkBuilder *builder)
{

    unsigned int recognized_counter;        /* Compteur de reconnus        */
    unsigned int total_counter;             /* Compteur de binaires        */
    GtkTreeModel *model;                    /* Modèle de gestion           */
    GtkTreeIter iter;                       /* Point de sélection          */
    gboolean valid;                         /* Validité de l'itérateur     */
    gboolean recognized;                    /* Nature du contenu           */
    char *msg;                              /* Message à faire apparaître  */
    GtkLabel *label;                        /* Etiquette à mettre à jour   */

    recognized_counter = 0;
    total_counter = 0;

    model = GTK_TREE_MODEL(gtk_builder_get_object(builder, "store"));

    for (valid = gtk_tree_model_get_iter_first(model, &iter);
         valid;
         valid = gtk_tree_model_iter_next(model, &iter))
    {
        gtk_tree_model_get(model, &iter, LCC_RECOGNIZED, &recognized, -1);

        if (recognized)
            recognized_counter++;

        total_counter++;

    }

    asprintf(&msg, "(%u / %u)", total_counter - recognized_counter, total_counter);

    label = GTK_LABEL(gtk_builder_get_object(builder, "hidden_counter"));
    gtk_label_set_text(label, msg);

    free(msg);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : builder = constructeur à utiliser.                           *
*                content = nouveau contenu chargé à intégrer.                 *
*                project = project impliqué dans l'opération.                 *
*                                                                             *
*  Description : Ajoute un binaire à la liste à charger.                      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void add_content_to_loading_dialog(GtkBuilder *builder, GLoadedContent *content, GStudyProject *project)
{
    GtkListStore *store;                    /* Modèle de gestion           */
    char *desc;                             /* Description d'un contenu    */
    char *class;                            /* Format associé à un contenu */
    char *name;                             /* Désignation complète        */
    gboolean recognized;                    /* Nature du contenu           */
    GtkTreeIter iter;                       /* Point d'insertion           */
    GtkTreeView *treeview;                  /* Vue en arboresence          */
    GtkTreeSelection *selection;            /* Gestionnaire de sélection   */
    GtkTreeModelFilter *filter;             /* Modèle filtrant             */
    GtkTreeIter filtered_iter;              /* Point d'insertion           */
    gboolean status;                        /* Bilan d'une conversion      */

    /* Mise à jour de l'interface (#0) */

    update_loading_dialog(builder);

    /* Inscription */

    desc = g_loaded_content_describe(content, false);
    class = g_loaded_content_get_content_class(content, true);

    asprintf(&name, "%s (%s)", desc, class);

    free(class);
    free(desc);

    recognized = TRUE;

    store = GTK_LIST_STORE(gtk_builder_get_object(builder, "store"));

    gtk_list_store_append(store, &iter);
    gtk_list_store_set(store, &iter,
                       LCC_NAME, name,
                       LCC_CONTENT, content,
                       LCC_PROJECT, project,
                       LCC_RECOGNIZED, recognized,
                       -1);

    free(name);

    treeview = GTK_TREE_VIEW(gtk_builder_get_object(builder, "treeview"));
    selection = gtk_tree_view_get_selection(treeview);

    if (!gtk_tree_selection_get_selected(selection, NULL, NULL))
    {
        filter = GTK_TREE_MODEL_FILTER(gtk_builder_get_object(builder, "filtered_store"));

        status = gtk_tree_model_filter_convert_child_iter_to_iter(filter, &filtered_iter, &iter);
        assert(status);

        if (status)
            gtk_tree_selection_select_iter(selection, &filtered_iter);

    }

    /* Mise à jour de l'interface (#1) */

    update_loading_dialog_counter(builder);

}
