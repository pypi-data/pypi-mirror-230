
/* Chrysalide - Outil d'analyse de fichiers binaires
 * export_disass.c - assistant d'exportation de contenu binaire
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


#include "export_disass.h"


#include <assert.h>
#include <fcntl.h>
#include <malloc.h>
#include <stdio.h>
#include <unistd.h>


#include <i18n.h>


#include "../core/global.h"
#include "../../common/extstr.h"
#include "../../core/columns.h"
#include "../../core/global.h"
#include "../../core/logs.h"
#include "../../core/queue.h"
#include "../../glibext/seq.h"
#include "../../gtkext/easygtk.h"
#include "../../gtkext/gtkblockdisplay.h"



/* ------------------------ PARTIE PRINCIPALE DE L'ASSISTANT ------------------------ */


/* Ferme l'assistant sans dérouler la procédure. */
static void export_assistant_cancel(GtkAssistant *, gpointer);

/* Ferme l'assistant et déroule la procédure. */
static void export_assistant_close(GtkAssistant *, GObject *);

/* Condensé des informations d'exportation */
typedef struct _export_info_t
{
    GBufferCache *cache;                    /* Tampon à manipuler          */

    buffer_export_context *ctx;             /* Contexte d'exportation      */
    BufferExportType type;                  /* Type d'exportation menée    */
    GDisplayOptions *options;               /* Paramètres d'affichage      */

    activity_id_t msg;                      /* Message de progression      */

} export_info_t;

/* Lance l'exportation d'un contenu binaire comme demandé. */
static void start_binary_export(GBufferCache *, buffer_export_context *, BufferExportType, GDisplayOptions *);

/* Réalise l'exportation d'une ligne particulière. */
static void export_one_binary_line(const export_info_t *, size_t, GtkStatusStack *, activity_id_t);

/* Acquitte la fin d'une tâche d'exportation complète. */
static void on_binary_export_completed(GSeqWork *, export_info_t *);



/* ----------------------- DEFINITION DU FORMAT D'EXPORTATION ----------------------- */


/* Ajoute le panneau de choix du format d'exportation. */
static void register_format_panel(GtkAssistant *);

/* Réagit un changement du format pour l'exportation. */
static void on_export_format_changed(GtkComboBox *, GtkAssistant *);

/* Interdit un champ de texte vide pour les options de texte. */
static void forbid_text_empty_entry(GtkEntry *, GtkAssistant *);

/* Interdit un champ de texte vide pour les options HTML. */
static void forbid_html_empty_entry(GtkEntry *, GtkAssistant *);



/* ------------------------- SELECTION DU CONTENU A TRAITER ------------------------- */


/* Ajoute le panneau de sélection du contenu à exporter. */
static void register_content_panel(GtkAssistant *);



/* ------------------------ DEFINITION DE LA SORTIE ATTENDUE ------------------------ */


/* Ajoute le panneau de choix du type de sortie. */
static void register_output_panel(GtkAssistant *);

/* Réagit un changement du nom de fichier pour l'exportation. */
static void on_export_filename_changed(GtkEntry *, GtkAssistant *);

/* Sélectionne ou non un nouveau fichier de sortie. */
static void on_filename_browsing_clicked(GtkButton *, GObject *);



/* ---------------------------------------------------------------------------------- */
/*                          PARTIE PRINCIPALE DE L'ASSISTANT                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = binaire chargé en mémoire à traiter.                *
*                parent = fenêtre principale de l'éditeur.                    *
*                                                                             *
*  Description : Crée et affiche un assistant d'aide à l'exportation.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void run_export_assistant(GLoadedBinary *binary, GtkWindow *parent)
{
    GtkWidget *assistant;                   /* Fenêtre à afficher          */
    GObject *ref;                           /* Espace de référencement     */

    assistant = gtk_assistant_new();
    gtk_window_set_title(GTK_WINDOW(assistant), _("Export assistant"));
    gtk_widget_set_size_request(assistant, 500, 350);
    gtk_window_set_position(GTK_WINDOW(assistant), GTK_WIN_POS_CENTER);

    gtk_window_set_modal(GTK_WINDOW(assistant), TRUE);
    gtk_window_set_transient_for(GTK_WINDOW(assistant), parent);

    ref = G_OBJECT(assistant);
    g_object_set_data(ref, "binary", binary);

    register_format_panel(GTK_ASSISTANT(assistant));
    register_content_panel(GTK_ASSISTANT(assistant));
    register_output_panel(GTK_ASSISTANT(assistant));

    g_signal_connect(G_OBJECT(assistant), "cancel", G_CALLBACK(export_assistant_cancel), NULL);
    g_signal_connect(G_OBJECT(assistant), "close", G_CALLBACK(export_assistant_close), ref);

    gtk_widget_show_all(assistant);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : assistant = fenêtre à compléter et référencement global.     *
*                data      = adresse non utilisée ici.                        *
*                                                                             *
*  Description : Ferme l'assistant sans dérouler la procédure.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void export_assistant_cancel(GtkAssistant *assistant, gpointer data)
{
    GObject *support;                       /* Support interne à supprimer */

    support = G_OBJECT(g_object_get_data(G_OBJECT(assistant), "text_options"));
    if (support != NULL) g_object_unref(support);

    support = G_OBJECT(g_object_get_data(G_OBJECT(assistant), "html_options"));
    if (support != NULL) g_object_unref(support);

    gtk_widget_destroy(GTK_WIDGET(assistant));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : assistant = fenêtre à compléter et référencement global.     *
*                ref       = adresse de l'espace de référencement global.     *
*                                                                             *
*  Description : Ferme l'assistant et déroule la procédure.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void export_assistant_close(GtkAssistant *assistant, GObject *ref)
{
    GtkComboBox *combo;                     /* Selection du format         */
    BufferExportType type;                  /* Type d'exportation requise  */
    buffer_export_context ctx;              /* Contexte à constituer       */
    GtkEntry *entry;                        /* Zone de saisie              */
    const gchar *filename;                  /* Chemin d'accès du fichier   */
    GtkToggleButton *checkbutton;           /* Coche à retrouver           */
    GLoadedBinary *binary;                  /* Binaire chargé à parcourir  */
    GDisplayOptions *template;              /* Options courantes           */
    GDisplayOptions *options;               /* Options d'affichage         */
    GBufferCache *cache;                    /* Tampon de code à traiter    */
    GObject *support;                       /* Support interne à supprimer */

    /* Type d'exportation */

    combo = GTK_COMBO_BOX(g_object_get_data(ref, "format"));

    type = (BufferExportType)gtk_combo_box_get_active(combo);

    /* Fichier de sortie */

    entry = GTK_ENTRY(g_object_get_data(ref, "filename"));
    filename = gtk_entry_get_text(entry);

    ctx.fd = open(filename, O_CREAT | O_WRONLY | O_TRUNC, S_IRUSR | S_IWUSR);
    if (ctx.fd == -1)
    {
        perror("open");
        return;
    }

    /* Eléments à afficher */

    binary = G_LOADED_BINARY(g_object_get_data(ref, "binary"));

    template = g_loaded_content_get_display_options(G_LOADED_CONTENT(binary), BVW_BLOCK);
    options = g_display_options_dup(template);
    g_object_unref(G_OBJECT(template));

    checkbutton = GTK_TOGGLE_BUTTON(g_object_get_data(ref, "physical_off"));
    g_display_options_set(options, DLC_PHYSICAL, gtk_toggle_button_get_active(checkbutton));

    checkbutton = GTK_TOGGLE_BUTTON(g_object_get_data(ref, "virtual_addr"));
    g_display_options_set(options, DLC_VIRTUAL, gtk_toggle_button_get_active(checkbutton));

    checkbutton = GTK_TOGGLE_BUTTON(g_object_get_data(ref, "binary_code"));
    g_display_options_set(options, DLC_BINARY, gtk_toggle_button_get_active(checkbutton));

    /* Options éventuelles */

    switch (type)
    {
        case BET_TEXT:
            entry = GTK_ENTRY(g_object_get_data(ref, "text_separator"));
            ctx.sep = strdup(gtk_entry_get_text(entry));
            if (strcmp(ctx.sep, "\\t") == 0)
            {
                free(ctx.sep);
                ctx.sep = strdup("\t");
            }
            break;

        case BET_HTML:
            entry = GTK_ENTRY(g_object_get_data(ref, "html_font_name"));
            ctx.font_name = strdup(gtk_entry_get_text(entry));

            entry = GTK_ENTRY(g_object_get_data(ref, "html_bg_color"));
            ctx.bg_color = strdup(gtk_entry_get_text(entry));

            break;

        default:
            break;

    }

    /* Programmation de la tâche */

    cache = g_loaded_binary_get_disassembly_cache(binary);

    start_binary_export(cache, &ctx, type, options);

    g_object_unref(G_OBJECT(cache));

    /* Conclusion */

    support = G_OBJECT(g_object_get_data(G_OBJECT(assistant), "text_options"));
    if (support != NULL) g_object_unref(support);

    support = G_OBJECT(g_object_get_data(G_OBJECT(assistant), "html_options"));
    if (support != NULL) g_object_unref(support);

    gtk_widget_destroy(GTK_WIDGET(assistant));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cache    = tampon de données à utiliser.                     *
*                template = paramètres dont s'inspirer pour l'exportation.    *
*                type     = type d'exportation attendue.                      *
*                options  = règles d'affichage des colonnes modulables.       *
*                                                                             *
*  Description : Lance l'exportation d'un contenu binaire comme demandé.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void start_binary_export(GBufferCache *cache, buffer_export_context *template, BufferExportType type, GDisplayOptions *options)
{
    export_info_t *info;                    /* Infos à faire circuler      */
    GWorkQueue *queue;                      /* Gestionnaire de différés    */
    size_t count;                           /* Quantité de lignes à traiter*/
    GSeqWork *work;                         /* Tâche de chargement à lancer*/

    /* Copie des paramètres d'exportation */

    info = calloc(1, sizeof(export_info_t));

    info->cache = cache;
    g_object_ref(G_OBJECT(cache));

    info->ctx = malloc(sizeof(buffer_export_context));

    info->ctx->fd = template->fd;

    switch (type)
    {
        case BET_TEXT:
            info->ctx->sep = template->sep;
            break;

        case BET_HTML:
            info->ctx->font_name = template->font_name;
            info->ctx->bg_color = template->bg_color;
            break;

        default:
            break;

    }

    info->type = type;
    info->options = options;

    /* Données exportées initiales */

    switch (type)
    {
        case BET_HTML:
            dprintf(template->fd, "<HTML>\n");
            dprintf(template->fd, "<HEAD>\n");
            dprintf(template->fd, "\t<META http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\"/>\n");
            dprintf(template->fd, "</HEAD>\n");
            dprintf(template->fd, "<BODY>\n");
            dprintf(template->fd, "<STYLE  type=\"text/css\">\n");
            dprintf(template->fd, "TABLE {\n");
            dprintf(template->fd, "\tbackground-color: %s;\n", template->bg_color);
            dprintf(template->fd, "\tborder: 0px;\n");
            dprintf(template->fd, "\tfont-family: %s;\n", template->font_name);
            dprintf(template->fd, "}\n");
            dprintf(template->fd, "TD {\n");
            dprintf(template->fd, "\tborder: 0px;\n");
            dprintf(template->fd, "\tpadding-left: 8px;\n");
            dprintf(template->fd, "\tpadding-right: 8px;\n");
            dprintf(template->fd, "}\n");
            export_line_segment_style(template, type);
            dprintf(template->fd, "</STYLE>\n");
            dprintf(template->fd, "<TABLE>\n");
            break;

        default:
            break;

    }

    /* Poursuite de l'opération */

    queue = get_work_queue();

    g_buffer_cache_rlock(cache);
    count = g_buffer_cache_count_lines(cache);

    info->msg = gtk_status_stack_add_activity(get_global_status(), _("Exporting binary content..."), count);

    work = g_seq_work_new(info, 0, count, info->msg, (seq_work_cb)export_one_binary_line);

    g_signal_connect(work, "work-completed", G_CALLBACK(on_binary_export_completed), info);

    g_work_queue_schedule_work(queue, G_DELAYED_WORK(work), DEFAULT_WORK_GROUP);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info   = ensemble d'informations utiles à l'opération.       *
*                i      = indice des éléments à traiter.                      *
*                status = barre de statut à tenir informée.                   *
*                id     = identifiant du message affiché à l'utilisateur.     *
*                                                                             *
*  Description : Réalise l'exportation d'une ligne particulière.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void export_one_binary_line(const export_info_t *info, size_t i, GtkStatusStack *status, activity_id_t id)
{
    GBufferLine *line;                      /* Ligne particulière à traiter*/

    line = g_buffer_cache_find_line_by_index(info->cache, i);

    g_buffer_line_export(line, info->ctx, info->type, info->options);

    g_object_unref(G_OBJECT(line));

    gtk_status_stack_update_activity_value(status, id, 1);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : work = tâche de sauvegarde menée à son terme.                *
*  Paramètres  : info = ensemble d'informations liées à l'opération terminée. *
*                                                                             *
*  Description : Acquitte la fin d'une tâche d'exportation complète.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_binary_export_completed(GSeqWork *work, export_info_t *info)
{
    switch (info->type)
    {
        case BET_HTML:
            dprintf(info->ctx->fd, "</TABLE>\n");
            dprintf(info->ctx->fd, "</BODY>\n");
            dprintf(info->ctx->fd, "</HTML>\n");
            break;

        default:
            break;

    }

    log_simple_message(LMT_INFO, "Binary content exported!");

    g_buffer_cache_runlock(info->cache);
    g_object_unref(G_OBJECT(info->cache));

    g_object_unref(G_OBJECT(info->options));

    close(info->ctx->fd);

    switch (info->type)
    {
        case BET_TEXT:
            free(info->ctx->sep);
            break;

        case BET_HTML:
            free(info->ctx->font_name);
            free(info->ctx->bg_color);
            break;

        default:
            break;

    }

    gtk_status_stack_remove_activity(get_global_status(), info->msg);

    free(info->ctx);
    free(info);

}



/* ---------------------------------------------------------------------------------- */
/*                         DEFINITION DU FORMAT D'EXPORTATION                         */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : assistant = fenêtre à compléter et référencement global.     *
*                                                                             *
*  Description : Ajoute le panneau de choix du format d'exportation.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void register_format_panel(GtkAssistant *assistant)
{
    GtkWidget *vbox;                        /* Support principal #1        */
    GtkWidget *hbox;                        /* Support principal #2        */
    GtkWidget *label;                       /* Etiquette d'indication      */
    GtkWidget *combobox;                    /* Sélection du format         */
    GtkWidget *options;                     /* Zone d'options              */
    GtkWidget *content;                     /* Accueil desdites options    */

    vbox = gtk_box_new(GTK_ORIENTATION_VERTICAL, 8);
    qck_set_margins(vbox, 8, 8, 8, 8);
    gtk_widget_show(vbox);

    /* Format de sortie */

    hbox = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 8);
    gtk_widget_show(hbox);
    gtk_box_pack_start(GTK_BOX(vbox), hbox, FALSE, FALSE, 0);

    label = qck_create_label(NULL, NULL, _("Format: "));
    gtk_box_pack_start(GTK_BOX(hbox), label, FALSE, FALSE, 0);

    combobox = qck_create_combobox(G_OBJECT(assistant), "format", G_CALLBACK(on_export_format_changed), assistant);
    gtk_box_pack_start(GTK_BOX(hbox), combobox, TRUE, TRUE, 0);

    gtk_combo_box_text_append_text(GTK_COMBO_BOX_TEXT(combobox), _("Simple text"));
    gtk_combo_box_text_append_text(GTK_COMBO_BOX_TEXT(combobox), _("HTML"));

    /* Eventuelles options */

    content = gtk_event_box_new();
    gtk_widget_show(content);

    options = qck_create_frame(_("<b>Options</b>"), content, 0, 12, 12, 0);
    gtk_box_pack_start(GTK_BOX(vbox), options, FALSE, FALSE, 0);

    g_object_set_data(G_OBJECT(assistant), "options", content);

    /* Intégration */

    gtk_combo_box_set_active(GTK_COMBO_BOX(combobox), 1);

    gtk_assistant_append_page(assistant, vbox);
    gtk_assistant_set_page_title(assistant, vbox, _("Format"));
    gtk_assistant_set_page_type(assistant, vbox, GTK_ASSISTANT_PAGE_INTRO);

    gtk_assistant_set_page_complete(assistant, vbox, TRUE);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : combo     = liste dont la sélection vient de changer.        *
*                assistant = fenêtre affichée et référencement global.        *
*                                                                             *
*  Description : Réagit un changement du format pour l'exportation.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_export_format_changed(GtkComboBox *combo, GtkAssistant *assistant)
{
    BufferExportType selected;              /* Format attendu              */
    GtkContainer *content;                  /* Accueil des options         */
    GtkWidget *old;                         /* Ancien support à remplacer  */
    GtkWidget *vbox;                        /* Support principal #1        */
    GtkWidget *hbox;                        /* Support principal #2        */
    GtkWidget *label;                       /* Etiquette d'indication      */
    GtkWidget *entry;                       /* Zone de saisie de valeur    */
    char *filename;                         /* Chemin à venir modifier     */
    char *dot;                              /* Dernière occurence de point */

    selected = (BufferExportType)gtk_combo_box_get_active(combo);

    content = GTK_CONTAINER(g_object_get_data(G_OBJECT(assistant), "options"));

    old = gtk_bin_get_child(GTK_BIN(content));
    if (old != NULL)
    {
        g_object_ref(G_OBJECT(old));
        gtk_container_remove(content, old);
    }

    switch (selected)
    {
        case BET_TEXT:

            hbox = GTK_WIDGET(g_object_get_data(G_OBJECT(assistant), "text_options"));

            if (hbox == NULL)
            {
                hbox = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 8);
                g_object_ref(G_OBJECT(hbox));
                gtk_widget_show(hbox);
                g_object_set_data(G_OBJECT(assistant), "text_options", hbox);

                label = qck_create_label(NULL, NULL, _("String between columns: "));
                gtk_box_pack_start(GTK_BOX(hbox), label, FALSE, FALSE, 0);

                entry = qck_create_entry(G_OBJECT(assistant), "text_separator", NULL);
                g_signal_connect(G_OBJECT(entry), "changed", G_CALLBACK(forbid_text_empty_entry), assistant);
                gtk_box_pack_start(GTK_BOX(hbox), entry, TRUE, TRUE, 0);
                gtk_entry_set_text(GTK_ENTRY(entry), "\\t");

            }

            gtk_container_add(content, hbox);

            break;

        case BET_HTML:

            vbox = GTK_WIDGET(g_object_get_data(G_OBJECT(assistant), "html_options"));

            if (vbox == NULL)
            {
                vbox = gtk_box_new(GTK_ORIENTATION_VERTICAL, 8);
                g_object_ref(G_OBJECT(vbox));
                gtk_widget_show(vbox);
                g_object_set_data(G_OBJECT(assistant), "html_options", vbox);

                hbox = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 8);
                gtk_widget_show(hbox);
                gtk_box_pack_start(GTK_BOX(vbox), hbox, FALSE, FALSE, 0);

                label = qck_create_label(NULL, NULL, _("HTML table font name: "));
                gtk_box_pack_start(GTK_BOX(hbox), label, FALSE, FALSE, 0);

                entry = qck_create_entry(G_OBJECT(assistant), "html_font_name", NULL);
                g_signal_connect(G_OBJECT(entry), "changed", G_CALLBACK(forbid_html_empty_entry), assistant);
                gtk_box_pack_start(GTK_BOX(hbox), entry, TRUE, TRUE, 0);
                gtk_entry_set_text(GTK_ENTRY(entry), "monospace");

                hbox = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 8);
                gtk_widget_show(hbox);
                gtk_box_pack_start(GTK_BOX(vbox), hbox, FALSE, FALSE, 0);

                label = qck_create_label(NULL, NULL, _("HTML table background color: "));
                gtk_box_pack_start(GTK_BOX(hbox), label, FALSE, FALSE, 0);

                entry = qck_create_entry(G_OBJECT(assistant), "html_bg_color", NULL);
                g_signal_connect(G_OBJECT(entry), "changed", G_CALLBACK(forbid_html_empty_entry), assistant);
                gtk_box_pack_start(GTK_BOX(hbox), entry, TRUE, TRUE, 0);
                gtk_entry_set_text(GTK_ENTRY(entry), "#2c2c2c");

            }

            gtk_container_add(content, vbox);

            break;

        default:
            break;

    }

    /* Mise à jour de l'extension du fichier de sortie, si possible */

    entry = GTK_WIDGET(g_object_get_data(G_OBJECT(assistant), "filename"));

    if (entry != NULL)
    {
        filename = strdup(gtk_entry_get_text(GTK_ENTRY(entry)));

        dot = strrchr(filename, '.');
        if (dot == NULL) goto oefc_no_dot;

        *dot = '\0';

        switch (selected)
        {
            case BET_TEXT:
                filename = stradd(filename, ".txt");
                break;
            case BET_HTML:
                filename = stradd(filename, ".html");
                break;
            default:
                break;
        }

        gtk_entry_set_text(GTK_ENTRY(entry), filename);

 oefc_no_dot:

        free(filename);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : entry     = zone de texte dont le contenu vient de changer.  *
*                assistant = fenêtre affichée et référencement global.        *
*                                                                             *
*  Description : Interdit un champ de texte vide pour les options HTML.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void forbid_text_empty_entry(GtkEntry *entry, GtkAssistant *assistant)
{
    const gchar *text;                      /* Texte saisi dans la zone    */
    gint num;                               /* Etape courante              */
    GtkWidget *page;                        /* Support de cette étape      */

    text = gtk_entry_get_text(entry);

    num = gtk_assistant_get_current_page(assistant);
    page = gtk_assistant_get_nth_page(assistant, num);

    gtk_assistant_set_page_complete(assistant, page, (strlen(text) > 0));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : _entry    = zone de texte dont le contenu vient de changer.  *
*                assistant = fenêtre affichée et référencement global.        *
*                                                                             *
*  Description : Interdit un champ de texte vide pour les options de texte.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void forbid_html_empty_entry(GtkEntry *_entry, GtkAssistant *assistant)
{
    bool status;                            /* Etat final à remonter       */
    GtkEntry *entry;                        /* Zone de texte générique     */
    const gchar *text;                      /* Texte saisi dans la zone    */
    gint num;                               /* Etape courante              */
    GtkWidget *page;                        /* Support de cette étape      */

    status = true;

    /* Police de caractère */

    entry = GTK_ENTRY(g_object_get_data(G_OBJECT(assistant), "html_font_name"));
    text = gtk_entry_get_text(entry);

    status &= (strlen(text) > 0);

    /* Couleur de fond */

    entry = GTK_ENTRY(g_object_get_data(G_OBJECT(assistant), "html_bg_color"));

    if (entry != NULL)
    {
        text = gtk_entry_get_text(entry);

        status &= (strlen(text) > 0);

    }

    /* Mise à jour graphique */

    num = gtk_assistant_get_current_page(assistant);

    if (num != -1)
    {
        page = gtk_assistant_get_nth_page(assistant, num);

        gtk_assistant_set_page_complete(assistant, page, status);

    }

}



/* ---------------------------------------------------------------------------------- */
/*                           SELECTION DU CONTENU A TRAITER                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : assistant = fenêtre à compléter et référencement global.     *
*                                                                             *
*  Description : Ajoute le panneau de sélection du contenu à exporter.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void register_content_panel(GtkAssistant *assistant)
{
    GtkWidget *vbox;                        /* Support principal           */
    GtkWidget *frame;                       /* Support avec encadrement    */
    GtkWidget *sub_vbox;                    /* Division verticale          */
    GtkWidget *checkbutton;                 /* Coche pour une option       */

    vbox = gtk_box_new(GTK_ORIENTATION_VERTICAL, 8);
    qck_set_margins(vbox, 8, 8, 8, 8);
    gtk_widget_show(vbox);

    /* Eléments à afficher */

    sub_vbox = gtk_box_new(GTK_ORIENTATION_VERTICAL, 8);
    gtk_widget_show(sub_vbox);

    frame = qck_create_frame(_("<b>Items to display</b>"), sub_vbox, 0, 12, 12, 0);
    gtk_box_pack_start(GTK_BOX(vbox), frame, FALSE, FALSE, 0);

    checkbutton = qck_create_check_button(G_OBJECT(assistant), "physical_off", _("Physical offset"), NULL, NULL);
    gtk_box_pack_start(GTK_BOX(sub_vbox), checkbutton, FALSE, FALSE, 0);
    gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton), TRUE);

    checkbutton = qck_create_check_button(G_OBJECT(assistant), "virtual_addr", _("Virtual address"), NULL, NULL);
    gtk_box_pack_start(GTK_BOX(sub_vbox), checkbutton, FALSE, FALSE, 0);
    gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton), TRUE);

    checkbutton = qck_create_check_button(G_OBJECT(assistant), "binary_code", _("Binary code"), NULL, NULL);
    gtk_box_pack_start(GTK_BOX(sub_vbox), checkbutton, FALSE, FALSE, 0);
    gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton), TRUE);

    /* Intégration */

    gtk_assistant_append_page(assistant, vbox);
    gtk_assistant_set_page_title(assistant, vbox, _("Exported content"));
    gtk_assistant_set_page_type(assistant, vbox, GTK_ASSISTANT_PAGE_CONTENT);

    gtk_assistant_set_page_complete(assistant, vbox, TRUE);

}



/* ---------------------------------------------------------------------------------- */
/*                          DEFINITION DE LA SORTIE ATTENDUE                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : assistant = fenêtre à compléter et référencement global.     *
*                                                                             *
*  Description : Ajoute le panneau de choix du type de sortie.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void register_output_panel(GtkAssistant *assistant)
{
    GtkWidget *vbox;                        /* Support principal #1        */
    GtkWidget *label;                       /* Etiquette d'indication      */
    GtkWidget *hbox;                        /* Support principal #2        */
    GtkWidget *entry;                       /* Zone de saisie de texte     */
    GtkWidget *button;                      /* Sélection de fichier        */
    GLoadedBinary *binary;                  /* Binaire chargé à parcourir  */
    char *filename;                         /* Chemin d'accès par défaut   */

    vbox = gtk_box_new(GTK_ORIENTATION_VERTICAL, 8);
    qck_set_margins(vbox, 8, 8, 8, 8);
    gtk_widget_show(vbox);

    /* Fichier de sortie */

    label = qck_create_label(NULL, NULL, _("File: "));
    gtk_box_pack_start(GTK_BOX(vbox), label, FALSE, FALSE, 0);

    hbox = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 8);
    gtk_widget_show(hbox);
    gtk_box_pack_start(GTK_BOX(vbox), hbox, FALSE, FALSE, 0);

    entry = qck_create_entry(G_OBJECT(assistant), "filename", NULL);
    gtk_box_pack_start(GTK_BOX(hbox), entry, TRUE, TRUE, 0);

    button = qck_create_button(NULL, NULL, "...", G_CALLBACK(on_filename_browsing_clicked), assistant);
    gtk_box_pack_start(GTK_BOX(hbox), button, FALSE, FALSE, 0);

    /* Intégration */

    gtk_assistant_append_page(assistant, vbox);
    gtk_assistant_set_page_title(assistant, vbox, _("Output"));
    gtk_assistant_set_page_type(assistant, vbox, GTK_ASSISTANT_PAGE_CONFIRM);

    gtk_assistant_set_page_complete(assistant, vbox, TRUE);

    /* Choix par défaut */

    binary = G_LOADED_BINARY(g_object_get_data(G_OBJECT(assistant), "binary"));
    filename = g_loaded_content_describe(G_LOADED_CONTENT(binary), true);

    gtk_entry_set_text(GTK_ENTRY(entry), filename);
    gtk_editable_insert_text(GTK_EDITABLE(entry), ".html", -1, (gint []) { strlen(filename) });

    free(filename);

    g_signal_connect(G_OBJECT(entry), "changed", G_CALLBACK(on_export_filename_changed), assistant);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : entry     = zone de texte dont le contenu vient de changer.  *
*                assistant = fenêtre affichée et référencement global.        *
*                                                                             *
*  Description : Réagit un changement du nom de fichier pour l'exportation.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_export_filename_changed(GtkEntry *entry, GtkAssistant *assistant)
{
    const gchar *text;                      /* Texte saisi dans la zone    */
    gint num;                               /* Etape courante              */
    GtkWidget *page;                        /* Support de cette étape      */

    text = gtk_entry_get_text(entry);

    num = gtk_assistant_get_current_page(assistant);
    page = gtk_assistant_get_nth_page(assistant, num);

    gtk_assistant_set_page_complete(assistant, page, (strlen(text) > 0));

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

static void on_filename_browsing_clicked(GtkButton *button, GObject *ref)
{
    GtkWidget *dialog;                      /* Boîte à afficher            */
    gchar *filename;                        /* Nom du fichier à intégrer   */
    GtkEntry *entry;                        /* Zone de saisie à maj.       */

    dialog = gtk_file_chooser_dialog_new(_("Choose an output filename"), GTK_WINDOW(ref),
                                         GTK_FILE_CHOOSER_ACTION_SAVE,
                                         _("_Cancel"), GTK_RESPONSE_CANCEL,
                                         _("_Save"), GTK_RESPONSE_ACCEPT,
                                         NULL);

    entry = GTK_ENTRY(g_object_get_data(ref, "filename"));
    gtk_file_chooser_set_filename(GTK_FILE_CHOOSER(dialog), gtk_entry_get_text(entry));

    if (gtk_dialog_run(GTK_DIALOG(dialog)) == GTK_RESPONSE_ACCEPT)
    {
        filename = gtk_file_chooser_get_filename(GTK_FILE_CHOOSER(dialog));

        gtk_entry_set_text(GTK_ENTRY(entry), filename);

        g_free(filename);

    }

    gtk_widget_destroy(dialog);

}
