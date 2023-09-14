
/* Chrysalide - Outil d'analyse de fichiers binaires
 * export_graph.c - assistant d'exportation de vues graphiques
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


#include "export_graph.h"


#include <assert.h>
#include <cairo-pdf.h>
#include <cairo-svg.h>
#include <cairo-ps.h>
#include <malloc.h>
#include <stdio.h>
#include <string.h>
#include <strings.h>


#include "../../common/extstr.h"
#include "../../core/logs.h"
#include "../../glibext/gbinarycursor.h"
#include "../../glibext/gloadedpanel.h"
#include "../../gtkext/easygtk.h"
#include "../../gtkext/gtkdisplaypanel.h"



/* Ferme l'assistant sans dérouler la procédure. */
static void graph_export_assistant_cancel(GtkAssistant *, GtkBuilder *);

/* Réalise l'exportation du contenu sous la forme choisie. */
static void graph_export_assistant_close(GtkAssistant *, GtkBuilder *);

/* Actualise l'extension du fichier de sortie. */
static void on_output_format_toggled(GtkToggleButton *, GtkBuilder *);

/* Prend note d'un changement dans la saisie du fichier final. */
static void on_output_filename_changed(GtkEditable *, GtkBuilder *);

/* Réagit à la demande de sélection d'un nouveau fichier final. */
static void on_output_filename_selection(GtkButton *, GtkBuilder *);



/******************************************************************************
*                                                                             *
*  Paramètres  : binary  = contenu bnaire chargé en mémoire.                  *
*                display = vue graphique à traiter.                           *
*                parent  = fenêtre principale de l'éditeur.                   *
*                                                                             *
*  Description : Crée et affiche un assistant d'aide à l'exportation.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void run_graph_export_assistant(GLoadedBinary *binary, GtkGraphDisplay *display, GtkWindow *parent)
{
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkWidget *assistant;                   /* Fenêtre à afficher          */
#if !defined CAIRO_HAS_PDF_SURFACE || !defined CAIRO_HAS_PS_SURFACE || !defined CAIRO_HAS_SVG_SURFACE
    GtkWIdget *button;                      /* Bouton de sélection         */
#endif
    GLineCursor *cursor;                    /* Position dans la vue        */
    vmpa2t target;                          /* Localisation ciblée         */
    GBinFormat *format;                     /* Format de fichier reconnu   */
    bool status;                            /* Bilan d'un appel            */
    GBinSymbol *symbol;                     /* Symbole affiché             */
    char *label;                            /* Etiquette humaine associée  */
    GtkEntry *entry;                        /* Zone de texte               */

    builder = gtk_builder_new_from_resource("/org/chrysalide/gui/dialogs/export_graph.ui");

    assistant = GTK_WIDGET(gtk_builder_get_object(builder, "window"));

    gtk_window_set_transient_for(GTK_WINDOW(assistant), parent);

    /* Validation des formats de sortie */

#ifndef CAIRO_HAS_PDF_SURFACE
    button = GTK_TOGGLE_BUTTON(gtk_builder_get_object(builder, "as_pdf"));
    gtk_widget_set_sensitive(button, FALSE);
#endif

#ifndef CAIRO_HAS_PS_SURFACE
    button = GTK_TOGGLE_BUTTON(gtk_builder_get_object(builder, "as_ps"));
    gtk_widget_set_sensitive(button, FALSE);
#endif

#ifndef CAIRO_HAS_SVG_SURFACE
    button = GTK_TOGGLE_BUTTON(gtk_builder_get_object(builder, "as_svg"));
    gtk_widget_set_sensitive(button, FALSE);
#endif

    /* Choix du fichier d'exportation par défaut */

    cursor = g_loaded_panel_get_cursor(G_LOADED_PANEL(display));

    if (cursor != NULL)
    {
        g_binary_cursor_retrieve(G_BINARY_CURSOR(cursor), &target);

        g_object_unref(G_OBJECT(cursor));

        format = G_BIN_FORMAT(g_loaded_binary_get_format(binary));

        status = g_binary_format_find_symbol_for(format, &target, &symbol);

        g_object_unref(G_OBJECT(format));

        if (status)
        {
            label = g_binary_symbol_get_label(symbol);

            entry = GTK_ENTRY(gtk_builder_get_object(builder, "output"));

            gtk_entry_set_text(entry, label);

            free(label);

            g_object_unref(G_OBJECT(symbol));

        }

    }

    on_output_format_toggled(NULL, builder);

    /* Mémorisation pour les traitement */

    g_object_ref(G_OBJECT(display));
    g_object_set_data_full(G_OBJECT(assistant), "display", display, g_object_unref);

    /* Connexion des signaux */

    gtk_builder_add_callback_symbols(builder,
                                     BUILDER_CALLBACK(graph_export_assistant_cancel),
                                     BUILDER_CALLBACK(graph_export_assistant_close),
                                     BUILDER_CALLBACK(on_output_format_toggled),
                                     BUILDER_CALLBACK(on_output_filename_changed),
                                     BUILDER_CALLBACK(on_output_filename_selection),
                                     NULL);

    gtk_builder_connect_signals(builder, builder);

    gtk_widget_show_all(assistant);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : assistant = fenêtre à compléter et référencement global.     *
*                builder = espace de référencement global.                    *
*                                                                             *
*  Description : Ferme l'assistant sans dérouler la procédure.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void graph_export_assistant_cancel(GtkAssistant *assistant, GtkBuilder *builder)
{
    g_object_set_data(G_OBJECT(assistant), "binary", NULL);
    g_object_set_data(G_OBJECT(assistant), "display", NULL);

    g_object_ref(G_OBJECT(assistant));
    gtk_widget_destroy(GTK_WIDGET(assistant));

    g_object_unref(G_OBJECT(builder));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : button  = bouton à l'origine de la procédure.                *
*                builder = espace de référencement global.                    *
*                                                                             *
*  Description : Réalise l'exportation du contenu sous la forme choisie.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void graph_export_assistant_close(GtkAssistant *assistant, GtkBuilder *builder)
{
    GtkEntry *entry;                        /* Zone de texte               */
    const gchar *cur_filename;              /* Fichier de sortie courant   */
    GtkGraphDisplay *display;               /* Vue grahique associée       */
    GtkRequisition size;                    /* Taille idéale associée      */
    bool as_png;                            /* Exportation en PNG ?        */
    GtkToggleButton *button;                /* Bouton de sélection         */
    gboolean state;                         /* Etat de la sélection        */
    cairo_surface_t *surface;               /* Zone de dessin nouvelle     */
    cairo_t *cr;                            /* Contexte de rendu           */
    GtkWidget *widget;                      /* Composant GTK à dessiner    */
    cairo_status_t status;                  /* Bilan de l'écriture         */

    /* Collecte des informations de base */

    entry = GTK_ENTRY(gtk_builder_get_object(builder, "output"));

    cur_filename = gtk_entry_get_text(entry);

    display = GTK_GRAPH_DISPLAY(g_object_get_data(G_OBJECT(assistant), "display"));

    gtk_widget_get_preferred_size(GTK_WIDGET(display), &size, NULL);

    /* Préparation du fichier de sortie */

    as_png = false;

    button = GTK_TOGGLE_BUTTON(gtk_builder_get_object(builder, "as_pdf"));
    state = gtk_toggle_button_get_active(button);

    if (state)
    {
        surface = cairo_pdf_surface_create(cur_filename, size.width, size.height);
        goto do_export;
    }

    button = GTK_TOGGLE_BUTTON(gtk_builder_get_object(builder, "as_ps"));
    state = gtk_toggle_button_get_active(button);

    if (state)
    {
        surface = cairo_ps_surface_create(cur_filename, size.width, size.height);
        goto do_export;
    }

    button = GTK_TOGGLE_BUTTON(gtk_builder_get_object(builder, "as_svg"));
    state = gtk_toggle_button_get_active(button);

    if (state)
    {
        surface = cairo_svg_surface_create(cur_filename, size.width, size.height);
        goto do_export;
    }

    surface = cairo_image_surface_create(CAIRO_FORMAT_ARGB32, size.width, size.height);
    as_png = true;

    /* Exportation du rendu */

 do_export:

    cr = cairo_create(surface);

    gtk_display_panel_prepare_export(GTK_DISPLAY_PANEL(display), true);

    widget = gtk_graph_display_get_support(display);

    gtk_widget_draw(widget, cr);

    g_object_unref(G_OBJECT(widget));

    gtk_display_panel_prepare_export(GTK_DISPLAY_PANEL(display), false);

    if (as_png)
    {
        status = cairo_surface_write_to_png(surface, cur_filename);

        if (status != CAIRO_STATUS_SUCCESS)
            log_variadic_message(LMT_ERROR, "Export error: %s (%u)", cairo_status_to_string(status), status);

    }
    else
        cairo_show_page(cr);

    cairo_destroy(cr);

    cairo_surface_destroy(surface);

    graph_export_assistant_cancel(assistant, builder);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tbutton = bouton à l'origine de la procédure.                *
*                builder = espace de référencement global.                    *
*                                                                             *
*  Description : Actualise l'extension du fichier de sortie.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_output_format_toggled(GtkToggleButton *tbutton, GtkBuilder *builder)
{
    GtkToggleButton *button;                /* Bouton de sélection         */
    gboolean state;                         /* Etat de la sélection        */
    const char *ext;                        /* Extension attendue          */
    GtkEntry *entry;                        /* Zone de texte               */
    const gchar *cur_filename;              /* Fichier de sortie courant   */
    char *found;                            /* Point final trouvé          */
    char *new_filename;                     /* Nouveau fichier de sortie   */

    button = GTK_TOGGLE_BUTTON(gtk_builder_get_object(builder, "as_pdf"));
    state = gtk_toggle_button_get_active(button);

    if (state)
    {
        ext = "pdf";
        goto do_update;
    }

    button = GTK_TOGGLE_BUTTON(gtk_builder_get_object(builder, "as_ps"));
    state = gtk_toggle_button_get_active(button);

    if (state)
    {
        ext = "ps";
        goto do_update;
    }

    button = GTK_TOGGLE_BUTTON(gtk_builder_get_object(builder, "as_svg"));
    state = gtk_toggle_button_get_active(button);

    if (state)
    {
        ext = "svg";
        goto do_update;
    }

    ext = "png";

 do_update:

    entry = GTK_ENTRY(gtk_builder_get_object(builder, "output"));

    cur_filename = gtk_entry_get_text(entry);

    found = rindex(cur_filename, '.');

    if (found == NULL)
        asprintf(&new_filename, "%s.%s", cur_filename, ext);

    else
    {
        new_filename = strndup(cur_filename, found - cur_filename);

        new_filename = stradd(new_filename, ".");
        new_filename = stradd(new_filename, ext);

    }

    gtk_entry_set_text(entry, new_filename);

    free(new_filename);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : editable = zone de texte à l'origine de la procédure.        *
*                builder  = espace de référencement global.                   *
*                                                                             *
*  Description : Prend note d'un changement dans la saisie du fichier final.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_output_filename_changed(GtkEditable *editable, GtkBuilder *builder)
{
    const gchar *cur_filename;              /* Fichier de sortie courant   */
    GtkAssistant *assistant;                /* Fenêtre affichée            */
    GtkWidget *page;                        /* Composant associé à une page*/

    cur_filename = gtk_entry_get_text(GTK_ENTRY(editable));

    assistant = GTK_ASSISTANT(gtk_builder_get_object(builder, "window"));

    page = gtk_assistant_get_nth_page(assistant, 1);

    gtk_assistant_set_page_complete(assistant, page, strlen(cur_filename) > 0);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : button  = bouton à l'origine de la procédure.                *
*                builder = espace de référencement global.                    *
*                                                                             *
*  Description : Réagit à la demande de sélection d'un nouveau fichier final. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_output_filename_selection(GtkButton *button, GtkBuilder *builder)
{
    GtkWindow *assistant;                   /* Fenêtre affichée            */
    GtkEntry *entry;                        /* Zone de texte               */
    const gchar *cur_filename;              /* Fichier de sortie courant   */
    GtkWidget *dialog;                      /* Boîte à afficher            */
    gchar *new_filename;                    /* Nouveau fichier de sortie   */

    assistant = GTK_WINDOW(gtk_builder_get_object(builder, "window"));

    entry = GTK_ENTRY(gtk_builder_get_object(builder, "output"));

    cur_filename = gtk_entry_get_text(entry);

    dialog = gtk_file_chooser_dialog_new(_("Save the output as..."), assistant,
                                         GTK_FILE_CHOOSER_ACTION_SAVE,
                                         _("_Cancel"), GTK_RESPONSE_CANCEL,
                                         _("_Save"), GTK_RESPONSE_ACCEPT,
                                         NULL);

    gtk_file_chooser_set_filename(GTK_FILE_CHOOSER(dialog), cur_filename);

    if (gtk_dialog_run(GTK_DIALOG(dialog)) == GTK_RESPONSE_ACCEPT)
    {
        new_filename = gtk_file_chooser_get_filename(GTK_FILE_CHOOSER(dialog));

        gtk_entry_set_text(entry, new_filename);

        g_free(new_filename);

    }

    gtk_widget_destroy(dialog);

}
