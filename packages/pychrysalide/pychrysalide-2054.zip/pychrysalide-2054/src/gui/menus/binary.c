
/* Chrysalide - Outil d'analyse de fichiers binaires
 * binary.c - gestion du menu 'Binaire'
 *
 * Copyright (C) 2012-2020 Cyrille Bagard
 *
 *  This binary is part of Chrysalide.
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


#include "binary.h"


#include <i18n.h>


#include "../item-int.h"
#include "../menubar.h"
#include "../core/global.h"
#include "../dialogs/export_disass.h"
#include "../dialogs/export_graph.h"
#include "../dialogs/gotox.h"
#include "../dialogs/snapshots.h"
#include "../dialogs/storage.h"
#include "../../gtkext/easygtk.h"
#include "../../gtkext/gtkdisplaypanel.h"
#include "../../gtkext/gtkgraphdisplay.h"



/* Réagit au menu "Binaire -> Points d'entrée". */
static void mcb_binary_entry_points(GtkMenuItem *, GMenuBar *);

/* Réagit au menu "Binaire -> Attacher un débogueur". */
static void mcb_binary_attach_debugger(GtkMenuItem *, GMenuBar *);

/* Réagit au menu "Binaire -> Enregistrements". */
static void mcb_binary_storage(GtkMenuItem *, GMenuBar *);

/* Réagit au menu "Binaire -> Instantanés". */
static void mcb_binary_snapshots(GtkMenuItem *, GMenuBar *);

/* Réagit au menu "Binaire -> Exporter -> Désassemblage". */
static void mcb_binary_export_disass(GtkMenuItem *, gpointer);

/* Réagit au menu "Binaire -> Exporter -> Vue graphique". */
static void mcb_binary_export_graph(GtkMenuItem *, gpointer);



/******************************************************************************
*                                                                             *
*  Paramètres  : builder = constructeur avec l'ensemble des références.       *
*                                                                             *
*  Description : Complète la définition du menu "Binaire".                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void setup_menu_binary_callbacks(GtkBuilder *builder)
{
    gtk_builder_add_callback_symbols(builder,
                                     BUILDER_CALLBACK(mcb_binary_entry_points),
                                     BUILDER_CALLBACK(mcb_binary_attach_debugger),
                                     BUILDER_CALLBACK(mcb_binary_storage),
                                     BUILDER_CALLBACK(mcb_binary_snapshots),
                                     BUILDER_CALLBACK(mcb_binary_export_disass),
                                     BUILDER_CALLBACK(mcb_binary_export_graph),
                                     NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                bar      = barre de menu parente.                            *
*                                                                             *
*  Description : Réagit au menu "Binaire -> Points d'entrée".                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_binary_entry_points(GtkMenuItem *menuitem, GMenuBar *bar)
{
    GLoadedBinary *binary;                  /* Binaire présenté à l'écran  */
    GtkWindow *editor;                      /* Fenêtre graphique principale*/
    GtkWidget *dialog;                      /* Boîte de dialogue à montrer */
    vmpa2t *addr;                           /* Adresse de destination      */
    GLoadedPanel *panel;                    /* Afficheur effectif de code  */

    binary = G_LOADED_BINARY(get_current_content());

    editor = get_editor_window();

    dialog = create_gotox_dialog_for_entry_points(editor, binary);

    if (gtk_dialog_run(GTK_DIALOG(dialog)) == GTK_RESPONSE_OK)
    {
        addr = get_address_from_gotox_dialog(dialog);

        panel = get_current_view();

        if (GTK_IS_DISPLAY_PANEL(panel))
            gtk_display_panel_request_move(GTK_DISPLAY_PANEL(panel), addr);

        g_object_unref(G_OBJECT(panel));

        delete_vmpa(addr);

    }

    gtk_widget_destroy(dialog);

    g_object_unref(G_OBJECT(editor));

    g_object_unref(G_OBJECT(binary));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                bar      = barre de menu parente.                            *
*                                                                             *
*  Description : Réagit au menu "Binaire -> Attacher un débogueur".           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_binary_attach_debugger(GtkMenuItem *menuitem, GMenuBar *bar)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                bar      = barre de menu parente.                            *
*                                                                             *
*  Description : Réagit au menu "Binaire -> Enregistrements".                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_binary_storage(GtkMenuItem *menuitem, GMenuBar *bar)
{
    GLoadedBinary *binary;                  /* Edition courante            */
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkWindow *editor;                      /* Fenêtre graphique principale*/
    GtkWidget *dialog;                      /* Boîte de dialogue à montrer */
    gint ret;                               /* Retour de confirmation      */

    binary = G_LOADED_BINARY(get_current_content());

    editor = get_editor_window();

    dialog = create_storage_dialog(binary, editor, &builder);

    ret = gtk_dialog_run(GTK_DIALOG(dialog));

    if (ret == GTK_RESPONSE_APPLY)
        update_binary_storage(builder, binary);

    gtk_widget_destroy(dialog);

    g_object_unref(G_OBJECT(builder));

    g_object_unref(G_OBJECT(editor));

    g_object_unref(G_OBJECT(binary));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                bar      = barre de menu parente.                            *
*                                                                             *
*  Description : Réagit au menu "Binaire -> Instantanés".                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_binary_snapshots(GtkMenuItem *menuitem, GMenuBar *bar)
{
    GLoadedBinary *binary;                  /* Edition courante            */
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkWindow *editor;                      /* Fenêtre graphique principale*/
    GtkWidget *dialog;                      /* Boîte de dialogue à montrer */

    binary = G_LOADED_BINARY(get_current_content());

    editor = get_editor_window();

    dialog = create_snapshots_dialog(binary, editor, &builder);

    gtk_dialog_run(GTK_DIALOG(dialog));

    gtk_widget_destroy(dialog);

    g_object_unref(G_OBJECT(builder));

    g_object_unref(G_OBJECT(editor));

    g_object_unref(G_OBJECT(binary));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                unused   = adresse non utilisée ici.                         *
*                                                                             *
*  Description : Réagit au menu "Binaire -> Exporter -> Désassemblage".       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_binary_export_disass(GtkMenuItem *menuitem, gpointer unused)
{
    GLoadedBinary *binary;                  /* Edition courante            */
    GtkWindow *editor;                      /* Fenêtre graphique principale*/

    binary = G_LOADED_BINARY(get_current_content());

    editor = get_editor_window();

    run_export_assistant(binary, editor);

    g_object_unref(G_OBJECT(editor));

    g_object_unref(G_OBJECT(binary));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                unused   = adresse non utilisée ici.                         *
*                                                                             *
*  Description : Réagit au menu "Binaire -> Exporter -> Vue graphique".       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_binary_export_graph(GtkMenuItem *menuitem, gpointer unused)
{
    GtkGraphDisplay *panel;                 /* Panneau de code courant     */
    GLoadedBinary *binary;                  /* Edition courante            */
    GtkWindow *editor;                      /* Fenêtre graphique principale*/

    binary = G_LOADED_BINARY(get_current_content());

    panel = GTK_GRAPH_DISPLAY(get_current_view());

    editor = get_editor_window();

    run_graph_export_assistant(binary, panel, editor);

    g_object_unref(G_OBJECT(editor));

    g_object_unref(G_OBJECT(panel));

    g_object_unref(G_OBJECT(binary));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : builder = constructeur avec l'ensemble des références.       *
*                new     = nouveau contenu chargé à analyser.                 *
*                                                                             *
*  Description : Réagit à un changement d'affichage principal de contenu.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void update_access_for_content_in_menu_binary(GtkBuilder *builder, GLoadedContent *new)
{
    gboolean access;                        /* Accès à déterminer          */
    GtkWidget *item;                        /* Elément de menu à traiter   */

    access = G_IS_LOADED_BINARY(new);

    item = GTK_WIDGET(gtk_builder_get_object(builder, "binary_entry_points"));
    gtk_widget_set_sensitive(item, access);

    item = GTK_WIDGET(gtk_builder_get_object(builder, "binary_storage"));
    gtk_widget_set_sensitive(item, access);

    item = GTK_WIDGET(gtk_builder_get_object(builder, "binary_export_disass"));
    gtk_widget_set_sensitive(item, access);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : builder = constructeur avec l'ensemble des références.       *
*                new     = nouvelle vue du contenu chargé analysé.            *
*                                                                             *
*  Description : Lance une actualisation du fait d'un changement de support.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void update_access_for_view_in_menu_binary(GtkBuilder *builder, GLoadedPanel *new)
{
    gboolean access;                        /* Accès à déterminer          */
    GtkWidget *item;                        /* Elément de menu à traiter   */

    access = GTK_IS_GRAPH_DISPLAY(new);

    item = GTK_WIDGET(gtk_builder_get_object(builder, "binary_export_graph"));
    gtk_widget_set_sensitive(item, access);

}
