
/* Chrysalide - Outil d'analyse de fichiers binaires
 * edition.c - gestion du menu 'Edition'
 *
 * Copyright (C) 2012-2020 Cyrille Bagard
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


#include "edition.h"


#include <assert.h>


#include <i18n.h>


#include "../menubar.h"
#include "../core/global.h"
#include "../dialogs/bookmark.h"
#include "../dialogs/goto.h"
#include "../dialogs/gotox.h"
#include "../../analysis/binary.h"
#include "../../analysis/db/items/switcher.h"
#include "../../arch/operands/targetable.h"
#include "../../glibext/gbinarycursor.h"
#include "../../gtkext/easygtk.h"
#include "../../gtkext/gtkblockdisplay.h"
#include "../../gtkext/gtkdisplaypanel.h"
#include "../../gtkext/gtkgraphdisplay.h"
#include "../../gtkext/hexdisplay.h"



/* Réagit avec le menu "Edition -> Aller à l'adresse...". */
static void mcb_edition_goto(GtkMenuItem *, GMenuBar *);

/* Réagit avec le menu "Edition -> Operande numérique -> ...". */
static void mcb_edition_switch_numeric_operand(GtkMenuItem *, gpointer);

/* Réagit avec le menu "Edition -> Revenir en arrière". */
static void mcb_edition_go_back(GtkMenuItem *, GMenuBar *);

/* Réagit avec le menu "Edition -> Suivre la référence". */
static void mcb_edition_follow_ref(GtkMenuItem *, gpointer);

/* Réagit avec le menu "Edition -> Lister toutes les réfs...". */
static void mcb_edition_list_xrefs(GtkMenuItem *, GMenuBar *);

/* Réagit avec le menu "Edition -> Signets -> Basculer...". */
static void mcb_edition_bookmarks_toggle(GtkMenuItem *, GMenuBar *);

/* Réagit avec le menu "Edition -> Signets -> Effacer tous...". */
static void mcb_edition_bookmarks_delete_all(GtkMenuItem *, GMenuBar *);

/* Réagit avec le menu "Edition -> Commentaires -> Inscrire...". */
static void mcb_edition_comment_enter(GtkMenuItem *, GMenuBar *);

/* Réagit avec le menu "Edition -> Commentaires -> Ins. rep...". */
static void mcb_edition_comment_enter_repeatable(GtkMenuItem *, GMenuBar *);

/* Réagit avec le menu "Edition -> Commentaires -> Ins. av...". */
static void mcb_edition_comment_enter_previous(GtkMenuItem *, GMenuBar *);

/* Réagit avec le menu "Edition -> Commentaires -> Ins. ap...". */
static void mcb_edition_comment_enter_next(GtkMenuItem *, GMenuBar *);



/******************************************************************************
*                                                                             *
*  Paramètres  : builder = constructeur avec l'ensemble des références.       *
*                                                                             *
*  Description : Complète la définition du menu "Edition".                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void setup_menu_edition_callbacks(GtkBuilder *builder)
{
    GObject *item;                          /* Elément à compléter         */

    gtk_builder_add_callback_symbols(builder,
                                     BUILDER_CALLBACK(mcb_edition_goto),
                                     BUILDER_CALLBACK(mcb_edition_switch_numeric_operand),
                                     BUILDER_CALLBACK(mcb_edition_go_back),
                                     BUILDER_CALLBACK(mcb_edition_follow_ref),
                                     BUILDER_CALLBACK(mcb_edition_list_xrefs),
                                     BUILDER_CALLBACK(mcb_edition_bookmarks_toggle),
                                     BUILDER_CALLBACK(mcb_edition_bookmarks_delete_all),
                                     BUILDER_CALLBACK(mcb_edition_comment_enter),
                                     BUILDER_CALLBACK(mcb_edition_comment_enter_repeatable),
                                     BUILDER_CALLBACK(mcb_edition_comment_enter_previous),
                                     BUILDER_CALLBACK(mcb_edition_comment_enter_next),
                                     NULL);

    /* Bascule des opérandes numériques */

    item = gtk_builder_get_object(builder, "edition_switch_hex");
    g_object_set_data(item, "kind_of_switch", GUINT_TO_POINTER(IOD_HEX));

    item = gtk_builder_get_object(builder, "edition_switch_dec");
    g_object_set_data(item, "kind_of_switch", GUINT_TO_POINTER(IOD_DEC));

    item = gtk_builder_get_object(builder, "edition_switch_oct");
    g_object_set_data(item, "kind_of_switch", GUINT_TO_POINTER(IOD_OCT));

    item = gtk_builder_get_object(builder, "edition_switch_bin");
    g_object_set_data(item, "kind_of_switch", GUINT_TO_POINTER(IOD_BIN));

    item = gtk_builder_get_object(builder, "edition_switch_def");
    g_object_set_data(item, "kind_of_switch", GUINT_TO_POINTER(IOD_COUNT));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                bar      = barre de menu parente.                            *
*                                                                             *
*  Description : Réagit avec le menu "Edition -> Aller à l'adresse...".       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_edition_goto(GtkMenuItem *menuitem, GMenuBar *bar)
{
    GtkWindow *editor;                      /* Fenêtre graphique principale*/
    GtkWidget *dialog;                      /* Boîte de dialogue à montrer */
    vmpa2t *addr;                           /* Adresse de destination      */
    GLoadedPanel *panel;                    /* Afficheur effectif de code  */
    GLoadedBinary *binary;                  /* Binaire en cours d'édition  */

    editor = get_editor_window();

    dialog = create_goto_dialog(editor);

    if (gtk_dialog_run(GTK_DIALOG(dialog)) == GTK_RESPONSE_OK)
    {
        addr = get_address_from_goto_dialog(dialog);

        panel = get_current_view();
        assert(GTK_IS_HEX_DISPLAY(panel) || GTK_IS_BLOCK_DISPLAY(panel) || GTK_IS_GRAPH_DISPLAY(panel));

        binary = G_LOADED_BINARY(g_loaded_panel_get_content(panel));
        g_loaded_binary_remember_new_goto(binary, addr);
        g_object_unref(G_OBJECT(binary));

        gtk_display_panel_request_move(GTK_DISPLAY_PANEL(panel), addr);

        g_object_unref(G_OBJECT(panel));

        delete_vmpa(addr);

    }

    gtk_widget_destroy(dialog);

    g_object_unref(G_OBJECT(editor));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                unused   = adresse non utilisée ici.                         *
*                                                                             *
*  Description : Réagit avec le menu "Edition -> Operande numérique -> ...".  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_edition_switch_numeric_operand(GtkMenuItem *menuitem, gpointer unused)
{
    ImmOperandDisplay display;              /* Type de basculement         */
    GLoadedPanel *panel;                    /* Afficheur effectif de code  */
    GObject *creator;                       /* Créateur à l'orgine du seg. */
    GLineCursor *cursor;                    /* Position courante           */
    vmpa2t addr;                            /* Adresse courante            */
    GLoadedBinary *binary;                  /* Binaire en cours d'étude    */
    GArchProcessor *proc;                   /* Propriétaire d'instructions */
    GArchInstruction *instr;                /* Instruction liée à la ligne */
    GDbSwitcher *switcher;                  /* Bascule à mettre en place   */

    display = GPOINTER_TO_UINT(g_object_get_data(G_OBJECT(menuitem), "kind_of_switch"));

    panel = get_current_view();
    assert(GTK_IS_BLOCK_DISPLAY(panel) || GTK_IS_GRAPH_DISPLAY(panel));

    creator = gtk_display_panel_get_active_object(GTK_DISPLAY_PANEL(panel));
    assert(G_IS_IMM_OPERAND(creator));

    cursor = g_loaded_panel_get_cursor(panel);
    g_binary_cursor_retrieve(G_BINARY_CURSOR(cursor), &addr);
    g_object_unref(G_OBJECT(cursor));

    binary = G_LOADED_BINARY(get_current_content());
    proc = g_loaded_binary_get_processor(binary);

    instr = g_arch_processor_find_instr_by_address(proc, &addr);
    assert(instr != NULL);

    switcher = g_db_switcher_new(instr, G_IMM_OPERAND(creator), display);

    g_object_unref(G_OBJECT(instr));

    if (switcher != NULL)
        g_loaded_binary_add_to_collection(binary, G_DB_ITEM(switcher));

    g_object_unref(G_OBJECT(proc));
    g_object_unref(G_OBJECT(binary));

    g_object_unref(creator);

    g_object_unref(G_OBJECT(panel));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                bar      = barre de menu parente.                            *
*                                                                             *
*  Description : Réagit avec le menu "Edition -> Revenir en arrière".         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_edition_go_back(GtkMenuItem *menuitem, GMenuBar *bar)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                unused   = adresse non utilisée ici.                         *
*                                                                             *
*  Description : Réagit avec le menu "Edition -> Suivre la référence".        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_edition_follow_ref(GtkMenuItem *menuitem, gpointer unused)
{
    GLoadedPanel *panel;                    /* Afficheur effectif de code  */
    GObject *creator;                       /* Créateur à l'orgine du seg. */
    GLoadedBinary *binary;                  /* Binaire en cours d'étude    */
    GBinFormat *format;                     /* Format binaire associé      */
    GArchProcessor *proc;                   /* Architecture associée       */
    GLineCursor *cursor;                    /* Curseur courant             */
    vmpa2t iaddr;                           /* Emplacement de l'instruction*/
    bool defined;                           /* Adresse définie ?           */
    vmpa2t addr;                            /* Adresse de destination      */

    panel = get_current_view();
    assert(GTK_IS_BLOCK_DISPLAY(panel) || GTK_IS_GRAPH_DISPLAY(panel));

    creator = gtk_display_panel_get_active_object(GTK_DISPLAY_PANEL(panel));
    assert(creator != NULL);

    if (G_IS_TARGETABLE_OPERAND(creator))
    {
        binary = G_LOADED_BINARY(get_current_content());

        format = G_BIN_FORMAT(g_loaded_binary_get_format(binary));
        proc = g_loaded_binary_get_processor(binary);

        cursor = g_loaded_panel_get_cursor(panel);
        g_binary_cursor_retrieve(G_BINARY_CURSOR(cursor), &iaddr);
        g_object_unref(G_OBJECT(cursor));

        defined = g_targetable_operand_get_addr(G_TARGETABLE_OPERAND(creator), &iaddr, format, proc, &addr);

        g_object_unref(G_OBJECT(proc));
        g_object_unref(G_OBJECT(format));

        g_object_unref(G_OBJECT(binary));

    }

    else
        defined = false;

    if (defined)
        gtk_display_panel_request_move(GTK_DISPLAY_PANEL(panel), &addr);

    g_object_unref(creator);

    g_object_unref(G_OBJECT(panel));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                bar      = barre de menu parente.                            *
*                                                                             *
*  Description : Réagit avec le menu "Edition -> Lister toutes les réfs...".  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_edition_list_xrefs(GtkMenuItem *menuitem, GMenuBar *bar)
{
    GLoadedPanel *panel;                    /* Afficheur effectif de code  */
    GLineCursor *cursor;                    /* Position courante           */
    vmpa2t addr;                            /* Adresse courante            */
    GLoadedBinary *binary;                  /* Représentation binaire      */
    GArchProcessor *proc;                   /* Processeur de l'architecture*/
    GArchInstruction *instr;                /* Point de croisements        */
    GtkWindow *editor;                      /* Fenêtre graphique principale*/
    GtkWidget *dialog;                      /* Boîte de dialogue à montrer */
    vmpa2t *dest;                           /* Adresse de destination      */

    panel = get_current_view();
    assert(GTK_IS_BLOCK_DISPLAY(panel) || GTK_IS_GRAPH_DISPLAY(panel));

    cursor = g_loaded_panel_get_cursor(panel);
    g_binary_cursor_retrieve(G_BINARY_CURSOR(cursor), &addr);
    g_object_unref(G_OBJECT(cursor));

    binary = G_LOADED_BINARY(get_current_content());
    proc = g_loaded_binary_get_processor(binary);

    /**
     * On ne peut pas se reposer sur l'espace couvert par une ligne, car il peut
     * être de taille nulle (cas d'une étiquette, par exemple), à la différence
     * de la taille d'une instruction.
     *
     * Il faut ainsi être plus souple, et se baser sur l'espace couvert par
     * une ligne mais sur l'adresse uniquement.
     */
    instr = g_arch_processor_find_instr_by_address(proc, &addr);

    if (instr != NULL)
    {
        editor = get_editor_window();

        dialog = create_gotox_dialog_for_cross_references(editor, binary, instr, true);

        if (gtk_dialog_run(GTK_DIALOG(dialog)) == GTK_RESPONSE_OK)
        {
            dest = get_address_from_gotox_dialog(dialog);

            gtk_display_panel_request_move(GTK_DISPLAY_PANEL(panel), dest);

            delete_vmpa(dest);

        }

        gtk_widget_destroy(dialog);

        g_object_unref(G_OBJECT(editor));

        g_object_unref(G_OBJECT(instr));

    }

    g_object_unref(G_OBJECT(proc));
    g_object_unref(G_OBJECT(binary));

    g_object_unref(G_OBJECT(panel));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                bar      = barre de menu parente.                            *
*                                                                             *
*  Description : Réagit avec le menu "Edition -> Signets -> Basculer...".     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_edition_bookmarks_toggle(GtkMenuItem *menuitem, GMenuBar *bar)
{
    GLoadedPanel *panel;                    /* Vue offrant l'affichage     */
    GLineCursor *cursor;                    /* Position courante           */
    vmpa2t addr;                            /* Adresse courante            */
    GLoadedBinary *binary;                  /* Binaire en cours d'étude    */
    GDbCollection *collec;                  /* Collection à manipuler      */
    GDbItem *exist;                         /* Sens du basculement courant */
    GtkWindow *editor;                      /* Fenêtre graphique principale*/
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkWidget *dialog;                      /* Boîte de dialogue à montrer */
    GDbItem *bookmark;                      /* Nouveau signet défini       */
    gint ret;                               /* Retour de confirmation      */

    /* Détermination de l'adresse visée */

    panel = get_current_view();
    assert(GTK_IS_BLOCK_DISPLAY(panel) || GTK_IS_GRAPH_DISPLAY(panel));

    cursor = g_loaded_panel_get_cursor(panel);
    g_binary_cursor_retrieve(G_BINARY_CURSOR(cursor), &addr);
    g_object_unref(G_OBJECT(cursor));

    /* Accès à la collection */

    binary = G_LOADED_BINARY(get_current_content());
    collec = g_loaded_binary_find_collection(binary, DBF_BOOKMARKS);

    /**
     * On choisit de se passer de verrou ici :
     *  - si l'élément existe, la suppression prend en compte le fait
     *    que l'élément puisse disparaître entre temps.
     *  - si l'élément n'existe pas, une boîte de dialogue est prévue
     *    au moment de l'insertion finale. Dans ce cas, l'utilisateur
     *    peut de plus modifier la position pendant la définition.
     */

    exist = NULL;//g_db_collection_has_key(collec, &addr);

    if (exist != NULL)
        ;//g_loaded_binary_remove_from_collection(binary, DBF_BOOKMARKS, exist);

    else
    {
        editor = get_editor_window();

        dialog = create_bookmark_dialog(editor, &builder);

        ret = gtk_dialog_run(GTK_DIALOG(dialog));

        if (ret == GTK_RESPONSE_OK)
        {
            bookmark = get_item_from_bookmark_dialog(builder, &addr);

            g_loaded_binary_add_to_collection(binary, G_DB_ITEM(bookmark));

        }

        gtk_widget_destroy(dialog);

        g_object_unref(G_OBJECT(builder));

        g_object_unref(G_OBJECT(editor));

    }

    g_object_unref(G_OBJECT(collec));
    g_object_unref(G_OBJECT(binary));

    g_object_unref(G_OBJECT(panel));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                bar      = barre de menu parente.                            *
*                                                                             *
*  Description : Réagit avec le menu "Edition -> Signets -> Effacer tous...". *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_edition_bookmarks_delete_all(GtkMenuItem *menuitem, GMenuBar *bar)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                bar      = barre de menu parente.                            *
*                                                                             *
*  Description : Réagit avec le menu "Edition -> Commentaires -> Inscrire...".*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_edition_comment_enter(GtkMenuItem *menuitem, GMenuBar *bar)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                bar      = barre de menu parente.                            *
*                                                                             *
*  Description : Réagit avec le menu "Edition -> Commentaires -> Ins. rep...".*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_edition_comment_enter_repeatable(GtkMenuItem *menuitem, GMenuBar *bar)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                bar      = barre de menu parente.                            *
*                                                                             *
*  Description : Réagit avec le menu "Edition -> Commentaires -> Ins. av...". *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_edition_comment_enter_previous(GtkMenuItem *menuitem, GMenuBar *bar)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                bar      = barre de menu parente.                            *
*                                                                             *
*  Description : Réagit avec le menu "Edition -> Commentaires -> Ins. ap...". *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_edition_comment_enter_next(GtkMenuItem *menuitem, GMenuBar *bar)
{

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

void update_access_for_view_in_menu_edition(GtkBuilder *builder, GLoadedPanel *new)
{
    gboolean access;                        /* Accès à déterminer          */
    GtkWidget *item;                        /* Elément de menu à traiter   */

    /* Déplacements ciblés */

    access = GTK_IS_BLOCK_DISPLAY(new) || GTK_IS_GRAPH_DISPLAY(new);

    item = GTK_WIDGET(gtk_builder_get_object(builder, "edition_goto"));
    gtk_widget_set_sensitive(item, access);

    /* Bascule des opérandes numériques */

    access = GTK_IS_BLOCK_DISPLAY(new) || GTK_IS_GRAPH_DISPLAY(new);

    item = GTK_WIDGET(gtk_builder_get_object(builder, "edition_switch_hex"));
    gtk_widget_set_sensitive(item, access);

    item = GTK_WIDGET(gtk_builder_get_object(builder, "edition_switch_dec"));
    gtk_widget_set_sensitive(item, access);

    item = GTK_WIDGET(gtk_builder_get_object(builder, "edition_switch_oct"));
    gtk_widget_set_sensitive(item, access);

    item = GTK_WIDGET(gtk_builder_get_object(builder, "edition_switch_bin"));
    gtk_widget_set_sensitive(item, access);

    item = GTK_WIDGET(gtk_builder_get_object(builder, "edition_switch_def"));
    gtk_widget_set_sensitive(item, access);

    /* Suivi de cibles */

    access = GTK_IS_BLOCK_DISPLAY(new) || GTK_IS_GRAPH_DISPLAY(new);

    item = GTK_WIDGET(gtk_builder_get_object(builder, "edition_go_back"));
    gtk_widget_set_sensitive(item, access);

    item = GTK_WIDGET(gtk_builder_get_object(builder, "edition_follow_ref"));
    gtk_widget_set_sensitive(item, access);

    item = GTK_WIDGET(gtk_builder_get_object(builder, "edition_list_xrefs"));
    gtk_widget_set_sensitive(item, access);

    /* Signets */

    access = GTK_IS_BLOCK_DISPLAY(new) || GTK_IS_GRAPH_DISPLAY(new);

    item = GTK_WIDGET(gtk_builder_get_object(builder, "edition_bookmarks_toggle"));
    gtk_widget_set_sensitive(item, access);

    item = GTK_WIDGET(gtk_builder_get_object(builder, "edition_bookmarks_delete_all"));
    gtk_widget_set_sensitive(item, access);

    /* Commentaires */

    access = GTK_IS_BLOCK_DISPLAY(new) || GTK_IS_GRAPH_DISPLAY(new);

    item = GTK_WIDGET(gtk_builder_get_object(builder, "edition_comment_enter"));
    gtk_widget_set_sensitive(item, access);

    item = GTK_WIDGET(gtk_builder_get_object(builder, "edition_comment_enter_rep"));
    gtk_widget_set_sensitive(item, access);

    item = GTK_WIDGET(gtk_builder_get_object(builder, "edition_comment_enter_prev"));
    gtk_widget_set_sensitive(item, access);

    item = GTK_WIDGET(gtk_builder_get_object(builder, "edition_comment_enter_next"));
    gtk_widget_set_sensitive(item, access);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : builder = constructeur avec l'ensemble des références.       *
*                panel   = vue d'affichage active ou NULL si aucune.          *
*                cursor  = suivi des positions à consulter.                   *
*                                                                             *
*  Description : Met à jour les accès du menu "Edition" selon une position.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void update_access_for_cursor_in_menu_edition(GtkBuilder *builder, GLoadedPanel *panel, const GLineCursor *cursor)
{
    GObject *creator;                       /* Créateur à l'orgine du seg. */
    gboolean access;                        /* Accès à déterminer          */
    GtkWidget *item;                        /* Elément de menu à traiter   */

    /* Préliminaire */

    /**
     * Seuls les affichages de blocs (en graphique ou non) distribuent ce
     * genre de curseur. Donc on valide dans le même temps la nature de la vue.
     */

    if (G_IS_BINARY_CURSOR(cursor))
    {
        assert(GTK_IS_HEX_DISPLAY(panel) || GTK_IS_BLOCK_DISPLAY(panel) || GTK_IS_GRAPH_DISPLAY(panel));

        if (g_line_cursor_is_valid(cursor))
            creator = gtk_display_panel_get_active_object(GTK_DISPLAY_PANEL(panel));
        else
            creator = NULL;

    }

    else
        creator = NULL;

    /* Bascule des opérandes numériques */

    access = G_IS_IMM_OPERAND(creator);

    item = GTK_WIDGET(gtk_builder_get_object(builder, "edition_switch_hex"));
    gtk_widget_set_sensitive(item, access);

    item = GTK_WIDGET(gtk_builder_get_object(builder, "edition_switch_dec"));
    gtk_widget_set_sensitive(item, access);

    item = GTK_WIDGET(gtk_builder_get_object(builder, "edition_switch_oct"));
    gtk_widget_set_sensitive(item, access);

    item = GTK_WIDGET(gtk_builder_get_object(builder, "edition_switch_bin"));
    gtk_widget_set_sensitive(item, access);

    item = GTK_WIDGET(gtk_builder_get_object(builder, "edition_switch_def"));
    gtk_widget_set_sensitive(item, access);

    /* Suivi de cibles */

    access = G_IS_TARGETABLE_OPERAND(creator);

    item = GTK_WIDGET(gtk_builder_get_object(builder, "edition_follow_ref"));
    gtk_widget_set_sensitive(item, access);

    access = g_line_cursor_is_valid(cursor);

    item = GTK_WIDGET(gtk_builder_get_object(builder, "edition_list_xrefs"));
    gtk_widget_set_sensitive(item, access);

    /* Nettoyage et sortie finale */

    if (creator != NULL)
        g_object_unref(G_OBJECT(creator));

}
