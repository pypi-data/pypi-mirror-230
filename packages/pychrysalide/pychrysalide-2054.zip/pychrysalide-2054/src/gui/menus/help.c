
/* Chrysalide - Outil d'analyse de fichiers binaires
 * help.c - gestion du menu 'Aide'
 *
 * Copyright (C) 2011-2018 Cyrille Bagard
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


#include "help.h"


#include <i18n.h>


#include "../core/global.h"
#include "../dialogs/about.h"
#include "../../gtkext/easygtk.h"



/* Réagit avec le menu "Aide -> Site Web". */
static void mcb_help_website(GtkMenuItem *, gpointer);

/* Réagit avec le menu "Aide -> Documentation de l'API Python". */
static void mcb_help_python_api_documentation(GtkMenuItem *, gpointer);

/* Réagit avec le menu "Aide -> Rapport d'anomalie". */
static void mcb_help_bug_report(GtkMenuItem *, gpointer);

/* Réagit avec le menu "Aide -> A propos de...". */
static void mcb_help_about(GtkMenuItem *, gpointer);



/******************************************************************************
*                                                                             *
*  Paramètres  : builder = constructeur avec l'ensemble des références.       *
*                                                                             *
*  Description : Complète la définition du menu "Aide".                       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void setup_menu_help_callbacks(GtkBuilder *builder)
{
    gtk_builder_add_callback_symbols(builder,
                                     BUILDER_CALLBACK(mcb_help_website),
                                     BUILDER_CALLBACK(mcb_help_python_api_documentation),
                                     BUILDER_CALLBACK(mcb_help_bug_report),
                                     BUILDER_CALLBACK(mcb_help_about),
                                     NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                unused   = adresse non utilisée ici.                         *
*                                                                             *
*  Description : Réagit avec le menu "Aide -> Site Web".                      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_help_website(GtkMenuItem *menuitem, gpointer unused)
{
    GtkWindow *parent;                      /* Fenêtre principale          */

    parent = get_editor_window();

    gtk_show_uri_on_window(parent, "https://www.chrysalide.re/", GDK_CURRENT_TIME, NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                unused   = adresse non utilisée ici.                         *
*                                                                             *
*  Description : Réagit avec le menu "Aide -> Documentation de l'API Python". *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_help_python_api_documentation(GtkMenuItem *menuitem, gpointer unused)
{
    GtkWindow *parent;                      /* Fenêtre principale          */

    parent = get_editor_window();

    gtk_show_uri_on_window(parent, "https://www.chrysalide.re/api/python/pychrysalide", GDK_CURRENT_TIME, NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                unused   = adresse non utilisée ici.                         *
*                                                                             *
*  Description : Réagit avec le menu "Aide -> Rapport d'anomalie".            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_help_bug_report(GtkMenuItem *menuitem, gpointer unused)
{
    GtkWindow *parent;                      /* Fenêtre principale          */

    parent = get_editor_window();

    gtk_show_uri_on_window(parent, "https://bugs.chrysalide.re/", GDK_CURRENT_TIME, NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                unused   = adresse non utilisée ici.                         *
*                                                                             *
*  Description : Réagit avec le menu "Aide -> A propos de...".                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_help_about(GtkMenuItem *menuitem, gpointer unused)
{
    GtkWindow *editor;                      /* Fenêtre graphique principale*/
    GtkBuilder *builder;                    /* Constructeur utilisé        */
    GtkWidget *dialog;                      /* Boîte de dialogue à montrer */

    editor = get_editor_window();

    dialog = create_about_dialog(editor, &builder);

    g_signal_connect_swapped(dialog, "destroy", G_CALLBACK(g_object_unref), builder);

    gtk_widget_show(dialog);

    g_object_unref(G_OBJECT(editor));

}
