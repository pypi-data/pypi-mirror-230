
/* Chrysalide - Outil d'analyse de fichiers binaires
 * options.c - gestion du menu 'Options'
 *
 * Copyright (C) 2019-2020 Cyrille Bagard
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


#include "options.h"


#include <i18n.h>


#include "../item-int.h"
#include "../menubar.h"
#include "../core/global.h"
#include "../dialogs/identity.h"
#include "../dialogs/preferences.h"
#include "../../gtkext/easygtk.h"



/* Réagit au menu "Options -> Préférences". */
static void mcb_options_preferences(GtkMenuItem *, gpointer);

/* Réagit au menu "Options -> Identité". */
static void mcb_options_identity(GtkMenuItem *, gpointer);



/******************************************************************************
*                                                                             *
*  Paramètres  : builder = constructeur avec l'ensemble des références.       *
*                                                                             *
*  Description : Complète la définition du menu "Options".                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void setup_menu_options_callbacks(GtkBuilder *builder)
{
    gtk_builder_add_callback_symbols(builder,
                                     BUILDER_CALLBACK(mcb_options_preferences),
                                     BUILDER_CALLBACK(mcb_options_identity),
                                     NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                unused   = adresse non utilisée ici.                         *
*                                                                             *
*  Description : Réagit au menu "Options -> Préférences".                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_options_preferences(GtkMenuItem *menuitem, gpointer unused)
{
    GtkWindow *editor;                      /* Fenêtre graphique principale*/
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkWidget *dialog;                      /* Boîte de dialogue à montrer */

    editor = get_editor_window();

    dialog = create_preferences_dialog(editor, &builder);

    gtk_dialog_run(GTK_DIALOG(dialog));

    gtk_widget_destroy(dialog);

    g_object_unref(G_OBJECT(builder));

    g_object_unref(G_OBJECT(editor));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                unused   = adresse non utilisée ici.                         *
*                                                                             *
*  Description : Réagit au menu "Options -> Identité".                        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_options_identity(GtkMenuItem *menuitem, gpointer unused)
{
    GtkWindow *editor;                      /* Fenêtre graphique principale*/
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkWidget *dialog;                      /* Boîte de dialogue à montrer */

    editor = get_editor_window();

    dialog = create_identity_dialog(editor, &builder);

    gtk_dialog_run(GTK_DIALOG(dialog));

    gtk_widget_destroy(dialog);

    g_object_unref(G_OBJECT(builder));

    g_object_unref(G_OBJECT(editor));

}
