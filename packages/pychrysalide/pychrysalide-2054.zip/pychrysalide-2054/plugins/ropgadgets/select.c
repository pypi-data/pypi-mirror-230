
/* Chrysalide - Outil d'analyse de fichiers binaires
 * goto.c - boîte de dialogue pour les sauts à une adresse donnée
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
 *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.
 */


#include "select.h"


#include <fcntl.h>
#include <malloc.h>
#include <regex.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>


#include <i18n.h>


#include <analysis/binary.h>
#include <analysis/contents/file.h>
#include <core/global.h>
#include <common/cpp.h>
#include <common/extstr.h>
#include <core/columns.h>
#include <core/processors.h>
#include <format/known.h>
#include <gui/core/global.h>
#include <gtkext/easygtk.h>
#include <gtkext/gtkblockdisplay.h>


#include "finder.h"



/* ------------------------ PARTIE PRINCIPALE DE L'ASSISTANT ------------------------ */


/* Colonnes de la liste des binaires */
typedef enum _CurrentProjectBinaries
{
    CPB_BINARY,                             /* Instance GLib du bianire    */
    CPB_FILENAME,                           /* Chemin d'accès au fichier   */

    CPB_COUNT                               /* Nombre de colonnes          */

} CurrentProjectBinaries;


/* Ferme l'assistant sans dérouler la procédure. */
static void rop_finder_assistant_cancel(GtkAssistant *, gpointer);

/* Ferme l'assistant et déroule la procédure. */
static void rop_finder_assistant_apply(GtkAssistant *, GObject *);

/* Accompagne le chargement de certaines pages de l'assistant. */
static void rop_finder_assistant_prepare(GtkAssistant *, GtkWidget *, GObject *);



/* ------------------------ DEFINITION DES ENTREES / SORTIES ------------------------ */


/* Ajoute le panneau de choix quant aux fichiers d'E/S. */
static void register_input_output_panel(GtkAssistant *, GObject *);

/* Construit la sélection d'un binaire déjà chargé. */
static GtkWidget *load_and_populate_current_project_binaries(GObject *, gint *);

/* Réagit à un changement de sélection du binaire d'entrée. */
static void on_loaded_binary_selection_change(GtkComboBox *, GObject *);

/* Met à jour l'accès à la définition d'un fichier de sortie. */
static void on_output_need_toggle(GtkToggleButton *, GObject *);

/* Sélectionne ou non un nouveau fichier de sortie. */
static void on_output_filename_browsing_clicked(GtkButton *, GObject *);



/* ------------------------- SUIVI DE LA PHASE DE RECHERCHE ------------------------- */


/* Ajoute le panneau de suivi des opérations de recherche. */
static void register_search_display_panel(GtkAssistant *, GObject *);

/* Initialise une ligne de rapport quant aux opérations menées. */
static void init_rop_search_step(GtkGrid *, gint, GObject *, const char *, const char *, GtkWidget *);

/* Réinitialise tous les rapports de recherches imprimés. */
static void reset_rop_search_steps(GObject *);


/* Description d'une évolution du processus */
typedef struct _search_step
{
    GObject *ref;                           /* Espace de référencements    */

    union
    {
        struct
        {
            const char *key;                /* Clef d'accès partielle      */
            bool dynamic;                   /* Mémoire à libérer ?         */
            union
            {
                const char *msg;            /* Message de conclusion       */
                char *dmsg;                 /* Message de conclusion       */
            };
            bool success;                   /* Indication claire           */
        };

        gdouble fraction;                   /* Avancée du désasssemblage   */

        struct
        {
            GExeFormat *format;             /* Format binaire chargé       */
            found_rop_list *list;           /* Liste de gadgets ROP trouvés*/
            size_t count;                   /* Nombre de gadgets trouvés   */
        };

    };

} search_step;


/* Affiche un message de statut quant aux recherches en cours. */
static gboolean print_status_of_rop_search_step(search_step *);

/* Affiche un message de statut quant aux recherches en cours. */
static void push_status_printing_of_rop_search_step(GObject *, const char *, const char *, bool);

/* Affiche un message de statut quant aux recherches en cours. */
static void push_dyn_status_printing_of_rop_search_step(GObject *, const char *, char *, bool);

/* Actualise la barre de progression affichée. */
static gboolean update_progress_bar_fraction(search_step *);

/* Lance l'actualisation de la barre de progression affichée. */
static void push_new_progress_fraction(GObject *, gdouble);

/* Enregistre une référence vers les gadgets trouvés. */
static gboolean register_found_rop_gadgets(search_step *);

/* Lance une conservation des gadgets trouvés. */
static void push_found_rop_gadgets(GObject *, GExeFormat *, found_rop_list *, size_t);

/* Charge un format binaire interne déjà chargé. */
static GExeFormat *load_internal_format_for_rop_gadgets(GObject *);

/* Procède à la recherche de gadgets de façon séparée. */
static gpointer look_for_rop_gadgets(GObject *);



/* ----------------------- MISE EN FORME DES GADGETS PRESENTS ----------------------- */


/* Colonnes de la liste des symboles */
typedef enum _FoundROPGadget
{
    FRG_CATEGORY,                           /* Catégorie d'appartenance    */
    FRG_RAW_VIRTUAL,                        /* Correspondance virtuelle    */
    FRG_RAW,                                /* Brut pour recherche         */

    FRG_VIRTUAL,                            /* Correspondance virtuelle    */
    FRG_CONTENT,                            /* Contenu des lignes visées   */

    FRG_COUNT                               /* Nombre de colonnes          */

} FoundROPGadget;


/* Ajoute le panneau de sélection des gadgets ROP identifiés. */
static void register_rop_list_panel(GtkAssistant *, GObject *);

/* Lance l'actualisation du filtrage des gadgets ROP. */
static void on_rop_gadgets_category_changed(GtkComboBox *, GObject *);

/* Lance l'actualisation du filtrage des gadgets ROP. */
static void on_rop_gadgets_filter_changed(GtkSearchEntry *, GObject *);

/* Détermine la visibilité de tel ou tel gadget ROP. */
static gboolean filter_visible_rop_gadgets(GtkTreeModel *, GtkTreeIter *, GObject *);

/* Ajoute de nouvelles chaînes de gadgets localisées. */
static void add_new_gadgets_for_category(GExeFormat *, GtkComboBoxText *, GtkTreeStore *, const char *, rop_chain **, size_t);



/* ---------------------------------------------------------------------------------- */
/*                          PARTIE PRINCIPALE DE L'ASSISTANT                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : parent = fenêtre principale de l'éditeur.                    *
*                                                                             *
*  Description : Crée et affiche un assistant de sélection de gadgets ROP.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void run_rop_finder_assistant(GtkWindow *parent)
{
    GtkWidget *assistant;                   /* Fenêtre à afficher          */
    GObject *ref;                           /* Espace de référencement     */

    assistant = gtk_assistant_new();
    gtk_widget_set_size_request(assistant, 900, 550);
    gtk_window_set_position(GTK_WINDOW(assistant), GTK_WIN_POS_CENTER);
    gtk_window_set_title(GTK_WINDOW(assistant), _("Export assistant"));

    gtk_window_set_modal(GTK_WINDOW(assistant), TRUE);
    gtk_window_set_transient_for(GTK_WINDOW(assistant), parent);

    ref = G_OBJECT(assistant);

    register_input_output_panel(GTK_ASSISTANT(assistant), ref);
    register_search_display_panel(GTK_ASSISTANT(assistant), ref);
    register_rop_list_panel(GTK_ASSISTANT(assistant), ref);

    g_signal_connect(G_OBJECT(assistant), "cancel", G_CALLBACK(rop_finder_assistant_cancel), NULL);
    g_signal_connect(G_OBJECT(assistant), "close", G_CALLBACK(rop_finder_assistant_cancel), NULL);
    g_signal_connect(G_OBJECT(assistant), "apply", G_CALLBACK(rop_finder_assistant_apply), ref);
    g_signal_connect(G_OBJECT(assistant), "prepare", G_CALLBACK(rop_finder_assistant_prepare), ref);

    gtk_widget_show_all(assistant);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : assistant = fenêtre d'assistance à traiter.                  *
*                data      = adresse non utilisée ici.                        *
*                                                                             *
*  Description : Ferme l'assistant sans dérouler la procédure.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void rop_finder_assistant_cancel(GtkAssistant *assistant, gpointer data)
{
    gtk_widget_destroy(GTK_WIDGET(assistant));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : assistant = fenêtre d'assistance à traiter.                  *
*                ref       = adresse de l'espace de référencement global.     *
*                                                                             *
*  Description : Ferme l'assistant et déroule la procédure.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void rop_finder_assistant_apply(GtkAssistant *assistant, GObject *ref)
{
    GtkEntry *entry;                        /* Zone de saisie              */
    const gchar *filename;                  /* Chemin d'accès du fichier   */
    int fd;                                 /* Flux ouvert en écriture     */
    GtkTreeView *treeview;                  /* Arborescence à actualiser   */
    GtkTreeModel *model;                    /* Modèle de gestion           */
    GtkTreeIter iter;                       /* Boucle de parcours          */
    gboolean loop;                          /* Poursuite de la boucle ?    */
    gchar *virtual;                         /* Adresse correspondante      */
    gchar *raw;                             /* ROP en format texte simple  */

    /* Fichier de sortie */

    entry = GTK_ENTRY(g_object_get_data(ref, "output_filename"));
    filename = gtk_entry_get_text(entry);

    fd = open(filename, O_CREAT | O_WRONLY | O_TRUNC, S_IRUSR | S_IWUSR);
    if (fd == -1)
    {
        perror("open");
        return;
    }

    /* Boucle de parcours */

    treeview = GTK_TREE_VIEW(g_object_get_data(ref, "treeview"));
    model = gtk_tree_view_get_model(treeview);

    for (loop = gtk_tree_model_get_iter_first(model, &iter);
         loop;
         loop = gtk_tree_model_iter_next(model, &iter))
    {
        gtk_tree_model_get(model, &iter, FRG_RAW_VIRTUAL, &virtual, FRG_RAW, &raw, -1);

        dprintf(fd, "%s\t%s\n", virtual, raw);

        g_free(virtual);
        g_free(raw);

    }

    /* Conclusion */

    close(fd);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : assistant = fenêtre d'assistance à traiter.                  *
*                page      = élément de l'assistant à préparer.               *
*                ref       = adresse de l'espace de référencement global.     *
*                                                                             *
*  Description : Accompagne le chargement de certaines pages de l'assistant.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void rop_finder_assistant_prepare(GtkAssistant *assistant, GtkWidget *page, GObject *ref)
{
    GtkWidget *test;                        /* Reconnaissance à l'aveugle  */
    GThread *thread;                        /* Tâche de fond à programmer  */

    test = gtk_assistant_get_nth_page(assistant, 1);

    if (test == page)
    {
        reset_rop_search_steps(ref);

        thread = g_thread_new("gadgets_finder", (GThreadFunc)look_for_rop_gadgets, ref);
        g_thread_unref(thread);

    }

}



/* ---------------------------------------------------------------------------------- */
/*                          DEFINITION DES ENTREES / SORTIES                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : assistant = fenêtre d'assistance à compléter.                *
*                ref       = espace de référencements inter-panneaux.         *
*                                                                             *
*  Description : Ajoute le panneau de choix quant aux fichiers d'E/S.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void register_input_output_panel(GtkAssistant *assistant, GObject *ref)
{
    GtkWidget *vbox;                        /* Support principal           */
    GtkWidget *frame;                       /* Support avec encadrement    */
    GtkWidget *sub_vbox;                    /* Division verticale          */
    gint selected;                          /* Indice à sélectionner       */
    GtkWidget *combobox;                    /* Sélection du binaire interne*/
    GtkWidget *sub_hbox;                    /* Division horizontale        */
    GtkWidget *entry;                       /* Zone de saisie de texte     */
    GtkWidget *button;                      /* Sélection de fichier        */
    GtkWidget *checkbutton;                 /* Coche pour une option       */

    vbox = gtk_box_new(GTK_ORIENTATION_VERTICAL, 16);
    gtk_widget_show(vbox);

    /* Fichier de sortie */

    sub_vbox = gtk_box_new(GTK_ORIENTATION_VERTICAL, 0);
    gtk_widget_show(sub_vbox);

    frame = qck_create_frame(_("<b>Input binary</b>"), sub_vbox, 0, 0, 12, 8);
    gtk_box_pack_start(GTK_BOX(vbox), frame, FALSE, TRUE, 0);

    combobox = load_and_populate_current_project_binaries(ref, &selected);
    gtk_box_pack_start(GTK_BOX(sub_vbox), combobox, TRUE, TRUE, 0);

    /* Fichier de sortie */

    sub_vbox = gtk_box_new(GTK_ORIENTATION_VERTICAL, 0);
    gtk_widget_show(sub_vbox);

    frame = qck_create_frame(_("<b>Ouput results</b>"), sub_vbox, 0, 0, 12, 8);
    gtk_box_pack_start(GTK_BOX(vbox), frame, FALSE, TRUE, 0);

    checkbutton = qck_create_check_button(ref, "use_output",
                                          _("Save selected ROP gadgets in a file:"),
                                          G_CALLBACK(on_output_need_toggle), ref);
    gtk_widget_show(checkbutton);

    gtk_box_pack_start(GTK_BOX(sub_vbox), checkbutton, FALSE, FALSE, 0);

    sub_hbox = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 8);
    gtk_widget_show(sub_hbox);
    gtk_box_pack_start(GTK_BOX(sub_vbox), sub_hbox, FALSE, TRUE, 0);

    entry = qck_create_entry(ref, "output_filename", NULL);
    gtk_box_pack_start(GTK_BOX(sub_hbox), entry, TRUE, TRUE, 0);

    button = qck_create_button(ref, "output_browser", _("Browse..."),
                               G_CALLBACK(on_output_filename_browsing_clicked), assistant);
    gtk_box_pack_start(GTK_BOX(sub_hbox), button, FALSE, FALSE, 0);

    /* Actualisation des accès */

    gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton), FALSE);
    on_output_need_toggle(GTK_TOGGLE_BUTTON(checkbutton), ref);

    /* Intégration */

    gtk_assistant_append_page(assistant, vbox);
    gtk_assistant_set_page_title(assistant, vbox, _("Input / output"));
    gtk_assistant_set_page_type(assistant, vbox, GTK_ASSISTANT_PAGE_INTRO);

    gtk_combo_box_set_active(GTK_COMBO_BOX(combobox), selected);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ref      = espace de référencements inter-panneaux.          *
*                selected = éventuel indice de binaire à sélectionner. [OUT]  *
*                                                                             *
*  Description : Construit la sélection d'un binaire déjà chargé.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GtkWidget *load_and_populate_current_project_binaries(GObject *ref, gint *selected)
{
    GtkWidget *result;                      /* Composant à retourner       */
    GStudyProject *project;                 /* Projet courant              */
    GLoadedContent *current;                /* Contenu actif courant       */
    GtkListStore *store;                    /* Modèle de gestion en liste  */
    GLoadedContent **contents;              /* Liste de contenus chargés   */
    size_t count;                           /* Taille de cette liste       */
    size_t i;                               /* Boucle de parcours          */
    char *desc;                             /* Description de contenu      */
    GtkTreeIter iter;                       /* Point d'insertion           */
    GtkCellRenderer *renderer;              /* Moteur de rendu de colonne  */

    /* Récupération des éléments courants */

    project = get_current_project();

    current = get_current_content();

    /* Constitution d'une liste de binaires courants */

    *selected = -1;

    store = gtk_list_store_new(CPB_COUNT, G_TYPE_OBJECT, G_TYPE_STRING);

    contents = g_study_project_get_contents(project, &count);

    if (contents != NULL)
    {
        for (i = 0; i < count; i++)
        {
            if (G_IS_LOADED_BINARY(contents[i]))
            {
                desc = g_loaded_content_describe(contents[i], true);

                gtk_list_store_append(store, &iter);
                gtk_list_store_set(store, &iter,
                                   CPB_BINARY, contents[i],
                                   CPB_FILENAME, desc,
                                   -1);

                free(desc);

                if (contents[i] == current)
                    *selected = i;

            }

            g_object_unref(G_OBJECT(contents[i]));

        }

        free(contents);

    }

    /* Mise en place d'un affichage graphique */

    result = gtk_combo_box_new_with_model(GTK_TREE_MODEL(store));
    g_object_set_data(ref, "input_binary", result);

    g_signal_connect(result, "changed", G_CALLBACK(on_loaded_binary_selection_change), ref);

    gtk_widget_show(result);

    renderer = gtk_cell_renderer_text_new();
    gtk_cell_layout_pack_start(GTK_CELL_LAYOUT(result), renderer, TRUE);
    gtk_cell_layout_set_attributes(GTK_CELL_LAYOUT(result), renderer,
                                   "text", CPB_FILENAME,
                                   NULL);

    g_object_unref(G_OBJECT(store));

    /* Sortie propre */

    g_object_unref(G_OBJECT(current));

    g_object_unref(G_OBJECT(project));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : combo = composant graphique de sélection concerné.           *
*                ref   = espace de référencement principal.                   *
*                                                                             *
*  Description : Réagit à un changement de sélection du binaire d'entrée.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_loaded_binary_selection_change(GtkComboBox *combo, GObject *ref)
{
    gint selected;                          /* Indice sélectionné          */
    GtkWidget *page;                        /* Page de la partie terminée  */

    selected = gtk_combo_box_get_active(combo);

    page = gtk_assistant_get_nth_page(GTK_ASSISTANT(ref), 0);

    if (page != NULL)
        gtk_assistant_set_page_complete(GTK_ASSISTANT(ref), page, selected != -1);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : button = coche dont le status vient de changer.              *
*                ref    = espace de référencements inter-panneaux.            *
*                                                                             *
*  Description : Met à jour l'accès à la définition d'un fichier de sortie.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_output_need_toggle(GtkToggleButton *button, GObject *ref)
{
    gboolean state;                         /* Etat du bouton courant      */
    GtkWidget *widget;                      /* Element dont l'accès change */

    state = gtk_toggle_button_get_active(button);

    widget = GTK_WIDGET(g_object_get_data(ref, "output_filename"));
    if (widget != NULL)
        gtk_widget_set_sensitive(widget, state);

    widget = GTK_WIDGET(g_object_get_data(ref, "output_browser"));
    if (widget != NULL)
        gtk_widget_set_sensitive(widget, state);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : button = bouton d'édition de la sélection.                   *
*                ref    = espace de référencement principal.                  *
*                                                                             *
*  Description : Sélectionne ou non un nouveau fichier de sortie.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_output_filename_browsing_clicked(GtkButton *button, GObject *ref)
{
    GtkWidget *dialog;                      /* Boîte à afficher            */
    gchar *filename;                        /* Nom du fichier à intégrer   */
    GtkEntry *entry;                        /* Zone de saisie à maj.       */

    dialog = gtk_file_chooser_dialog_new(_("Choose an output filename"), GTK_WINDOW(ref),
                                         GTK_FILE_CHOOSER_ACTION_SAVE,
                                         _("_Cancel"), GTK_RESPONSE_CANCEL,
                                         _("_Save"), GTK_RESPONSE_ACCEPT,
                                         NULL);

    entry = GTK_ENTRY(g_object_get_data(ref, "output_filename"));
    gtk_file_chooser_set_filename(GTK_FILE_CHOOSER(dialog), gtk_entry_get_text(entry));

    if (gtk_dialog_run(GTK_DIALOG(dialog)) == GTK_RESPONSE_ACCEPT)
    {
        filename = gtk_file_chooser_get_filename(GTK_FILE_CHOOSER(dialog));

        gtk_entry_set_text(GTK_ENTRY(entry), filename);

        g_free(filename);

    }

    gtk_widget_destroy(dialog);

}



/* ---------------------------------------------------------------------------------- */
/*                           SUIVI DE LA PHASE DE RECHERCHE                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : assistant = fenêtre d'assistance à compléter.                *
*                ref       = espace de référencements inter-panneaux.         *
*                                                                             *
*  Description : Ajoute le panneau de suivi des opérations de recherche.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void register_search_display_panel(GtkAssistant *assistant, GObject *ref)
{
    GtkGrid *grid;                          /* Table de résumé             */
    GtkWidget *pbar;                        /* barre de progression        */

    grid = GTK_GRID(gtk_grid_new());
    gtk_grid_set_column_spacing(grid, 8);
    gtk_grid_set_row_spacing(grid, 8);

    g_object_set(G_OBJECT(grid),
                 "halign", GTK_ALIGN_CENTER,
                 "valign", GTK_ALIGN_CENTER,
                 "margin-bottom", 100, NULL);

    /* Représentation des étapes */

    init_rop_search_step(grid, 0, ref, "loading", _("Loading the input binary..."), NULL);

    init_rop_search_step(grid, 1, ref, "format", _("Detecting the proper format..."), NULL);

    pbar = gtk_progress_bar_new();
    g_object_set(G_OBJECT(pbar), "valign", GTK_ALIGN_CENTER, NULL);
    gtk_widget_show(pbar);

    init_rop_search_step(grid, 2, ref, "gadgets", _("Looking for all ROP gadgets..."), pbar);

    init_rop_search_step(grid, 3, ref, "final", _("Results:"), NULL);

    /* Intégration */

    gtk_assistant_append_page(assistant, GTK_WIDGET(grid));
    gtk_assistant_set_page_title(assistant, GTK_WIDGET(grid), _("Search process"));
    gtk_assistant_set_page_type(assistant, GTK_WIDGET(grid), GTK_ASSISTANT_PAGE_PROGRESS);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ref  = espace de référencements inter-panneaux.              *
*                key  = clef partielle d'accès aux composants concernés.      *
*                info = message d'information annonçant la conclusion.        *
*                pbar = éventuel composant de statut ou NULL.                 *
*                                                                             *
*  Description : Initialise une ligne de rapport quant aux opérations menées. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void init_rop_search_step(GtkGrid *grid, gint top, GObject *ref, const char *key, const char *info, GtkWidget *pbar)
{
    char *access;                           /* Chemin d'accès final        */
    GtkWidget *render;                      /* Image de statut à afficher  */
    GtkWidget *label;                       /* Etiquette d'indication      */

    /* Icone de représentation */

    access = strdup("process_");
    access = stradd(access, key);
    access = stradd(access, "_icon");

    render = gtk_image_new_from_icon_name("dialog-question", GTK_ICON_SIZE_DND);
    g_object_set_data(ref, access, render);
    gtk_widget_show(render);
    gtk_grid_attach(grid, render, 0, top, 1, 1);

    free(access);

    /* Désignation humaine d'indicatif */

    access = strdup("process_");
    access = stradd(access, key);
    access = stradd(access, "_caption");

    label = qck_create_label(ref, access, info);
    gtk_grid_attach(grid, label, 1, top, 1, 1);

    free(access);

    /* Statut final */

    access = strdup("process_");
    access = stradd(access, key);
    access = stradd(access, "_status");

    if (pbar == NULL)
    {
        label = qck_create_label(ref, access, "done");
        gtk_grid_attach(grid, label, 2, top, 1, 1);
    }
    else
    {
        g_object_set_data(ref, access, pbar);
        gtk_grid_attach(grid, pbar, 2, top, 1, 1);
    }

    free(access);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ref = espace de référencements inter-panneaux.               *
*                                                                             *
*  Description : Réinitialise tous les rapports de recherches imprimés.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void reset_rop_search_steps(GObject *ref)
{
    size_t i;                               /* Boucle de parcours          */
    char *access;                           /* Chemin d'accès final        */
    GObject *render;                        /* Image de statut à afficher  */
    GtkLabel *label;                        /* Etiquette d'indication      */
    GtkProgressBar *pbar;                   /* Barre à mettre à jour       */

    static const char *icon_keys[] = { "loading", "format", "gadgets", "final" };
    static const char *status_keys[] = { "loading", "format", "final" };

    /* Réinitialisation des images */

    for (i = 0; i < ARRAY_SIZE(icon_keys); i++)
    {
        access = strdup("process_");
        access = stradd(access, icon_keys[i]);
        access = stradd(access, "_icon");

        render = G_OBJECT(g_object_get_data(ref, access));
        g_object_set(render, "icon-name", "dialog-question", NULL);

        free(access);

    }

    /* Statut final */

    for (i = 0; i < ARRAY_SIZE(status_keys); i++)
    {
        access = strdup("process_");
        access = stradd(access, status_keys[i]);
        access = stradd(access, "_status");

        label = GTK_LABEL(g_object_get_data(ref, access));
        gtk_label_set_text(label, "");

        free(access);

    }

    /* Progression des recherches */

    pbar = GTK_PROGRESS_BAR(g_object_get_data(ref, "process_gadgets_status"));

    gtk_progress_bar_set_fraction(pbar, 0.0);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : step = informations quant à l'étape avancée.                 *
*                                                                             *
*  Description : Affiche un message de statut quant aux recherches en cours.  *
*                                                                             *
*  Retour      : FALSE pour ne pas reprogrammer l'exécution de la tâche.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean print_status_of_rop_search_step(search_step *step)
{
    char *access;                           /* Chemin d'accès final        */
    GObject *render;                        /* Image de statut à afficher  */
    GtkLabel *status;                       /* Bilan à faire paraître      */

    /* Icone de représentation */

    access = strdup("process_");
    access = stradd(access, step->key);
    access = stradd(access, "_icon");

    render = G_OBJECT(g_object_get_data(step->ref, access));
    g_object_set(render, "icon-name", step->success ? "face-smile" : "face-sad", NULL);

    free(access);

    /* Mot de la fin */

    if (step->msg != NULL)
    {
        access = strdup("process_");
        access = stradd(access, step->key);
        access = stradd(access, "_status");

        status = GTK_LABEL(g_object_get_data(step->ref, access));
        gtk_label_set_text(status, step->msg);

        free(access);

    }

    /* Nettoyage final */

    if (step->dynamic)
        free(step->dmsg);

    free(step);

    return FALSE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ref     = espace de référencements inter-panneaux.           *
*                key     = clef partielle d'accès aux composants concernés.   *
*                msg     = message d'information accompagnant la conclusion.  *
*                success = indication quant à la réussite de l'opération.     *
*                                                                             *
*  Description : Affiche un message de statut quant aux recherches en cours.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void push_dyn_status_printing_of_rop_search_step(GObject *ref, const char *key, char *dmsg, bool success)
{
    search_step *step;                      /* Informations d'étape        */

    step = (search_step *)calloc(1, sizeof(search_step));

    step->ref = ref;

    step->key = key;
    step->dynamic = true;
    step->dmsg = dmsg;
    step->success = success;

    g_idle_add((GSourceFunc)print_status_of_rop_search_step, step);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ref     = espace de référencements inter-panneaux.           *
*                key     = clef partielle d'accès aux composants concernés.   *
*                msg     = message d'information accompagnant la conclusion.  *
*                success = indication quant à la réussite de l'opération.     *
*                                                                             *
*  Description : Affiche un message de statut quant aux recherches en cours.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void push_status_printing_of_rop_search_step(GObject *ref, const char *key, const char *msg, bool success)
{
    search_step *step;                      /* Informations d'étape        */

    step = (search_step *)calloc(1, sizeof(search_step));

    step->ref = ref;

    step->key = key;
    step->dynamic = false;
    step->msg = msg;
    step->success = success;

    g_idle_add((GSourceFunc)print_status_of_rop_search_step, step);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : step = informations quant à l'étape avancée.                 *
*                                                                             *
*  Description : Actualise la barre de progression affichée.                  *
*                                                                             *
*  Retour      : FALSE pour ne pas reprogrammer l'exécution de la tâche.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean update_progress_bar_fraction(search_step *step)
{
    GtkProgressBar *pbar;                   /* Barre à mettre à jour       */

    pbar = GTK_PROGRESS_BAR(g_object_get_data(step->ref, "process_gadgets_status"));

    gtk_progress_bar_set_fraction(pbar, step->fraction);

    /* Nettoyage final */

    free(step);

    return FALSE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ref      = espace de référencements inter-panneaux.          *
*                fraction = avancée globale du désassemblage en cours.        *
*                                                                             *
*  Description : Lance l'actualisation de la barre de progression affichée.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void push_new_progress_fraction(GObject *ref, gdouble fraction)
{
    search_step *step;                      /* Informations d'étape        */

    step = (search_step *)calloc(1, sizeof(search_step));

    step->ref = ref;

    step->fraction = fraction;

    g_idle_add((GSourceFunc)update_progress_bar_fraction, step);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : step = informations quant à l'étape avancée.                 *
*                                                                             *
*  Description : Enregistre une référence vers les gadgets trouvés.           *
*                                                                             *
*  Retour      : FALSE pour ne pas reprogrammer l'exécution de la tâche.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean register_found_rop_gadgets(search_step *step)
{
    GtkComboBoxText *combo;                 /* Sélection d'une catégorie   */
    GtkTreeView *treeview;                  /* Arborescence à actualiser   */
    GtkTreeModelFilter *filter;             /* Modèle de gestion associé   */
    size_t i;                               /* Boucle de parcours          */
    GtkWidget *page;                        /* Page de la partie terminée  */

    /* Affichage des résulats */

    if (step->format != NULL)
    {
        combo = GTK_COMBO_BOX_TEXT(g_object_get_data(step->ref, "filter_cat"));

        treeview = GTK_TREE_VIEW(g_object_get_data(step->ref, "treeview"));
        filter = GTK_TREE_MODEL_FILTER(gtk_tree_view_get_model(treeview));

        for (i = 0; i < step->count; i++)
            add_new_gadgets_for_category(step->format,
                                         combo, GTK_TREE_STORE(gtk_tree_model_filter_get_model(filter)),
                                         step->list[i].category, step->list[i].gadgets, step->list[i].count);

        if (step->list != NULL)
            free_rop_list(step->list);

    }

    /* Déverrouillage des accès à la suite */

    page = gtk_assistant_get_nth_page(GTK_ASSISTANT(step->ref), 1);

    gtk_assistant_set_page_complete(GTK_ASSISTANT(step->ref), page, TRUE);

    /* Nettoyage final */

    free(step);

    return FALSE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ref    = espace de référencements inter-panneaux.            *
*                format = format binaire chargé.                              *
*                list   = liste de liste de gadgets pour ROP.                 *
*                count  = taille de cette liste.                              *
*                                                                             *
*  Description : Lance une conservation des gadgets trouvés.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void push_found_rop_gadgets(GObject *ref, GExeFormat *format, found_rop_list *list, size_t count)
{
    search_step *step;                      /* Informations d'étape        */

    step = (search_step *)calloc(1, sizeof(search_step));

    step->ref = ref;

    step->format = format;
    step->list = list;
    step->count = count;

    g_idle_add((GSourceFunc)register_found_rop_gadgets, step);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ref = espace de référencements inter-panneaux.               *
*                                                                             *
*  Description : Charge un format binaire interne déjà chargé.                *
*                                                                             *
*  Retour      : Nouveau format au contenu à fouiller ou NULL en cas d'échec. *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GExeFormat *load_internal_format_for_rop_gadgets(GObject *ref)
{
    GExeFormat *result;                     /* Format chargé à retourner   */
    GtkComboBox *combo;                     /* Composant de sélection      */
    GtkTreeIter iter;                       /* Tête de lecture à placer    */
    GtkTreeModel *model;                    /* Modèle de gestion           */
    GLoadedBinary *binary;                  /* Binaire chargé à utiliser   */

    combo = GTK_COMBO_BOX(g_object_get_data(ref, "input_binary"));

    if (!gtk_combo_box_get_active_iter(combo, &iter))
    {
        push_status_printing_of_rop_search_step(ref, "loading", _("unable to get the current binary"), false);
        return NULL;
    }

    model = gtk_combo_box_get_model(combo);
    gtk_tree_model_get(model, &iter, CPB_BINARY, &binary, -1);

    push_status_printing_of_rop_search_step(ref, "loading", _("done"), true);

    result = g_loaded_binary_get_format(binary);

    push_status_printing_of_rop_search_step(ref, "format", _("already loaded"), true);

    g_object_unref(G_OBJECT(binary));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ref = espace de référencements inter-panneaux.               *
*                                                                             *
*  Description : Procède à la recherche de gadgets de façon séparée.          *
*                                                                             *
*  Retour      : ?                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gpointer look_for_rop_gadgets(GObject *ref)
{
    GExeFormat *format;                     /* Format du binaire à traiter */
    found_rop_list *list;                   /* Liste de gadgets ROP trouvés*/
    size_t count;                           /* Nombre de ces listes        */
    size_t found;                           /* Nombre de gadgets trouvés   */
    size_t i;                               /* Boucle de parcours          */
    char *msg;                              /* Message final à faire passer*/

    format = load_internal_format_for_rop_gadgets(ref);
    if (format == NULL) goto lfrg_unlock;

    list = list_all_gadgets(format, 7, push_new_progress_fraction, ref, &count);

    push_status_printing_of_rop_search_step(ref, "gadgets", NULL, true);

    found = 0;

    for (i = 0; i < count; i++)
        found += list[i].count;

    switch (found)
    {
        case 0:
            msg = strdup(_("No ROP gadget has been found."));
            break;

        case 1:
            msg = strdup(_("1 ROP gadget has been found."));
            break;

        default:
            asprintf(&msg, _("%zu gadgets have been found."), found);
            break;

    }

    push_dyn_status_printing_of_rop_search_step(ref, "final", msg, count > 0);

    push_found_rop_gadgets(ref, format, list, count);

 lfrg_unlock:

    return NULL;

}



/* ---------------------------------------------------------------------------------- */
/*                         MISE EN FORME DES GADGETS PRESENTS                         */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : assistant = fenêtre d'assistance à compléter.                *
*                ref       = espace de référencements inter-panneaux.         *
*                                                                             *
*  Description : Ajoute le panneau de sélection des gadgets ROP identifiés.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void register_rop_list_panel(GtkAssistant *assistant, GObject *ref)
{
    GtkWidget *vbox;                        /* Support principal           */
    GtkWidget *hbox;                        /* Petite barre supérieure     */
    GtkWidget *label;                       /* Etiquette d'indication      */
    GtkWidget *comboboxentry;               /* Liste de sélection simple   */
    GtkWidget *vseparator;                  /* Barre de séparation         */
    GtkWidget *filter;                      /* Zone de recherche           */
    GtkWidget *scrollwnd;                   /* Support défilant            */
    GtkTreeStore *store;                    /* Modèle de gestion           */
    GtkTreeModel *model;                    /* Modèle de gestion supérieur */
    GtkWidget *treeview;                    /* Affichage de la liste       */
    GtkCellRenderer *renderer;              /* Moteur de rendu de colonne  */
    GtkTreeViewColumn *column;              /* Colonne de la liste         */

    vbox = gtk_box_new(GTK_ORIENTATION_VERTICAL, 8);
    gtk_widget_show(vbox);
    gtk_container_set_border_width(GTK_CONTAINER(vbox), 8);

    hbox = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 8);
    gtk_widget_show(hbox);
    gtk_box_pack_start(GTK_BOX(vbox), hbox, FALSE, TRUE, 0);

    /* Choix de la catégorie */

    label = gtk_label_new(_("ROP selection:"));
    gtk_widget_show(label);
    gtk_box_pack_start(GTK_BOX(hbox), label, FALSE, FALSE, 0);

    comboboxentry = qck_create_combobox(ref, "filter_cat", G_CALLBACK(on_rop_gadgets_category_changed), ref);
    gtk_box_pack_start(GTK_BOX(hbox), comboboxentry, FALSE, TRUE, 0);

    /* Séparation fine */

    vseparator = gtk_separator_new(GTK_ORIENTATION_VERTICAL);
    gtk_widget_show(vseparator);
    gtk_box_pack_start(GTK_BOX(hbox), vseparator, FALSE, FALSE, 0);

    /* Espace de recherche */

    label = gtk_label_new(_("Filter:"));
    gtk_widget_show(label);
    gtk_box_pack_start(GTK_BOX(hbox), label, FALSE, FALSE, 0);

    filter = gtk_search_entry_new();
    g_object_set_data(ref, "filter_rop", filter);
    gtk_widget_set_tooltip_text(filter, _("Filter gadgets using POSIX extended regular expressions"));

    g_signal_connect(filter, "search-changed", G_CALLBACK(on_rop_gadgets_filter_changed), ref);
    gtk_widget_show(filter);
    gtk_widget_set_hexpand(filter, TRUE);

    gtk_box_pack_start(GTK_BOX(hbox), filter, TRUE, TRUE, 0);

    /* Liste arborescente ou linéaire */

    scrollwnd = gtk_scrolled_window_new(NULL, NULL);
    gtk_widget_show(scrollwnd);
    gtk_box_pack_start(GTK_BOX(vbox), scrollwnd, TRUE, TRUE, 0);

    gtk_scrolled_window_set_policy(GTK_SCROLLED_WINDOW(scrollwnd), GTK_POLICY_AUTOMATIC, GTK_POLICY_AUTOMATIC);
    gtk_scrolled_window_set_shadow_type(GTK_SCROLLED_WINDOW(scrollwnd), GTK_SHADOW_IN);

    store = gtk_tree_store_new(FRG_COUNT, G_TYPE_STRING, G_TYPE_STRING, G_TYPE_STRING,
                               G_TYPE_STRING, G_TYPE_STRING);

    model = gtk_tree_model_filter_new(GTK_TREE_MODEL(store), NULL);

    gtk_tree_model_filter_set_visible_func(GTK_TREE_MODEL_FILTER(model),
                                           (GtkTreeModelFilterVisibleFunc)filter_visible_rop_gadgets,
                                           ref, NULL);

    treeview = gtk_tree_view_new_with_model(model);
    gtk_tree_view_set_headers_visible(GTK_TREE_VIEW(treeview), TRUE);
    gtk_tree_view_set_enable_tree_lines(GTK_TREE_VIEW(treeview), TRUE);

    g_object_set_data(ref, "treeview", treeview);

    gtk_widget_show(treeview);
    gtk_container_add(GTK_CONTAINER(scrollwnd), treeview);

    /* Cellules d'affichage */

    renderer = gtk_cell_renderer_text_new();
    column = gtk_tree_view_column_new_with_attributes(_("Address"), renderer,
                                                      "markup", FRG_VIRTUAL,
                                                      NULL);
    gtk_tree_view_column_set_sort_column_id(column, FRG_VIRTUAL);
    gtk_tree_view_append_column(GTK_TREE_VIEW(treeview), column);

    renderer = gtk_cell_renderer_text_new();
    column = gtk_tree_view_column_new_with_attributes(_("Gadgets"), renderer,
                                                      "markup", FRG_CONTENT,
                                                      NULL);
    gtk_tree_view_column_set_sort_column_id(column, FRG_CONTENT);
    gtk_tree_view_append_column(GTK_TREE_VIEW(treeview), column);

    /* Intégration */

    gtk_assistant_append_page(assistant, vbox);
    gtk_assistant_set_page_title(assistant, vbox, _("ROP Gadgets"));
    gtk_assistant_set_page_type(assistant, vbox, GTK_ASSISTANT_PAGE_CONFIRM);

    gtk_assistant_set_page_complete(assistant, vbox, TRUE);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : combo = composant de choix contenant le filtre brut.         *
*                ref   = espace de référencements inter-panneaux.             *
*                                                                             *
*  Description : Lance l'actualisation du filtrage des gadgets ROP.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_rop_gadgets_category_changed(GtkComboBox *combo, GObject *ref)
{
    GtkTreeView *treeview;                  /* Arborescence à actualiser   */
    GtkTreeModelFilter *filter;             /* Modèle de gestion associé   */

    treeview = GTK_TREE_VIEW(g_object_get_data(ref, "treeview"));

    filter = GTK_TREE_MODEL_FILTER(gtk_tree_view_get_model(treeview));

    gtk_tree_model_filter_refilter(filter);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : entry = entrée de texte contenant le filtre brut.            *
*                ref   = espace de référencements inter-panneaux.             *
*                                                                             *
*  Description : Lance l'actualisation du filtrage des gadgets ROP.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_rop_gadgets_filter_changed(GtkSearchEntry *entry, GObject *ref)
{
    regex_t preg;                           /* Expression régulière de test*/
    const gchar *text;                      /* Texte de l'utilisateur      */
    GtkStyleContext *context;               /* Contexte du thème actuel    */
    int ret;                                /* Bilan de mise en place      */
    GtkTreeView *treeview;                  /* Arborescence à actualiser   */
    GtkTreeModelFilter *filter;             /* Modèle de gestion associé   */

    text = gtk_entry_get_text(GTK_ENTRY(entry));

    context = gtk_widget_get_style_context(GTK_WIDGET(entry));

    if (text[0] != '\0')
    {
        ret = regcomp(&preg, text, REG_EXTENDED);

        if (ret != 0)
        {
            gtk_style_context_add_class(context, "filter-error");
            return;
        }

        regfree(&preg);

    }

    gtk_style_context_remove_class(context, "filter-error");

    treeview = GTK_TREE_VIEW(g_object_get_data(ref, "treeview"));

    filter = GTK_TREE_MODEL_FILTER(gtk_tree_view_get_model(treeview));

    gtk_tree_model_filter_refilter(filter);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : model = gestionnaire des lignes et colonnes affichées.       *
*                iter  = ligne concernée par l'analyse à mener.               *
*                ref   = espace de référencements inter-panneaux.             *
*                                                                             *
*  Description : Détermine la visibilité de tel ou tel gadget ROP.            *
*                                                                             *
*  Retour      : Indication d'affichage pour une ligne donnée.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean filter_visible_rop_gadgets(GtkTreeModel *model, GtkTreeIter *iter, GObject *ref)
{
    gboolean result;                        /* Visibilité à retourner      */
    gchar *category;                        /* Catégorie d'appartenance    */
    gchar *raw;                             /* Brut pour recherche         */
    GtkComboBoxText *combo;                 /* Sélection à choix multiples */
    gchar *selected;                        /* Texte de l'utilisateur #1   */
    GtkEntry *entry;                        /* Zone de texte à utiliser    */
    const gchar *text;                      /* Texte de l'utilisateur #2   */
    regex_t preg;                           /* Expression régulière de test*/
    int ret;                                /* Bilan de mise en place      */
    regmatch_t match;                       /* Récupération des trouvailles*/

    result = TRUE;

    gtk_tree_model_get(model, iter, FRG_CATEGORY, &category, FRG_RAW, &raw, -1);

    if (category == NULL || raw == NULL) return FALSE;

    /* Filtre sur les catégories */

    combo = g_object_get_data(ref, "filter_cat");

 	selected = gtk_combo_box_text_get_active_text(combo);

    result &= (g_strcmp0(category, selected) == 0);

    g_free(selected);

    /* Filtre sur les gadgets ROP */

    entry = g_object_get_data(ref, "filter_rop");

    text = gtk_entry_get_text(GTK_ENTRY(entry));

    ret = regcomp(&preg, text, REG_EXTENDED);
    result &= (ret == 0);

    if (ret == 0)
    {
        ret = regexec(&preg, raw, 1, &match, 0);
        result &= (ret != REG_NOMATCH);

        regfree(&preg);

    }

    /* Nettoyages finaux */

    g_free(category);
    g_free(raw);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format   = format binaire chargé sur lequel se reposer.      *
*                combo    = composant de sélection des catégories à compléter.*
*                store    = modèle de gestionnaire pour la liste affichée.    *
*                category = représentation du binaire chargé en mémoire.      *
*                gadgets  = liste de listes d'instructions de ROP.            *
*                count    = taille de cette liste.                            *
*                                                                             *
*  Description : Ajoute de nouvelles chaînes de gadgets localisées.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void add_new_gadgets_for_category(GExeFormat *format, GtkComboBoxText *combo, GtkTreeStore *store, const char *category, rop_chain **gadgets, size_t count)
{
    const GBinContent *content;             /* Contenu binaire global      */
    size_t i;                               /* Boucle de parcours #1       */
    char *raw_virtual;                      /* Transcription pour export   */
    char *virtual;                          /* Transcription d'adresse     */
    char *content_raw;                      /* Contenu assemblé de chaîne  */
    char *content_markup;                   /* Contenu assemblé de chaîne  */
    rop_chain *chain;                       /* Accès direct à une chaîne   */
    size_t j;                               /* Boucle de parcours #2       */
    GArchInstruction *instr;                /* Elément de liste de gadgets */
    GBufferLine *line;                      /* Ligne présente à l'adresse  */
    char *partial_raw;                      /* Contenu de la ligne visée   */
    char *partial_markup;                   /* Contenu de la ligne visée   */
    GtkTreeIter iter;                       /* Point d'insertion           */

    content = g_known_format_get_content(G_KNOWN_FORMAT(format));

    /* Conversion en contenu textuel */

    for (i = 0; i < count; i++)
    {
        /* Parcours des différentes lignes */

        raw_virtual = NULL;
        virtual = NULL;
        content_raw = NULL;
        content_markup = NULL;

        chain = gadgets[i];

        for (j = 0; j < chain->count; j++)
        {
            instr = chain->instrs[j];

            line = g_buffer_line_new(DLC_COUNT);
            g_line_generator_print(G_LINE_GENERATOR(instr), line, -1, 0, content);

            if (j == 0)
            {
                raw_virtual = g_buffer_line_get_text(line, DLC_VIRTUAL, DLC_VIRTUAL + 1, false);
                virtual = g_buffer_line_get_text(line, DLC_VIRTUAL, DLC_VIRTUAL + 1, true);
            }

            partial_raw = g_buffer_line_get_text(line, DLC_ASSEMBLY_HEAD, DLC_COUNT, false);
            partial_markup = g_buffer_line_get_text(line, DLC_ASSEMBLY_HEAD, DLC_COUNT, true);

            g_object_unref(G_OBJECT(line));

            if (content_raw != NULL)
                content_raw = stradd(content_raw, " ; ");

            content_raw = stradd(content_raw, partial_raw);

            if (content_markup != NULL)
                content_markup = stradd(content_markup, " ; ");

            content_markup = stradd(content_markup, partial_markup);

            free(partial_raw);
            free(partial_markup);

        }

        /* Insertion finale */

        gtk_tree_store_append(store, &iter, NULL);

        gtk_tree_store_set(store, &iter,
                           FRG_CATEGORY, category,
                           FRG_RAW_VIRTUAL, raw_virtual,
                           FRG_RAW, content_raw,
                           FRG_VIRTUAL, virtual,
                           FRG_CONTENT, content_markup,
                           -1);

        /* Nettoyage de la mémoire */

        free(raw_virtual);
        free(virtual);
        free(content_raw);
        free(content_markup);

    }

    g_object_unref(G_OBJECT(content));

    /* Rajout de la catégorie et filtre au besoin */

    gtk_combo_box_text_append_text(combo, category);

    if (gtk_combo_box_get_active(GTK_COMBO_BOX(combo)) == -1)
        gtk_combo_box_set_active(GTK_COMBO_BOX(combo), 0);

}
