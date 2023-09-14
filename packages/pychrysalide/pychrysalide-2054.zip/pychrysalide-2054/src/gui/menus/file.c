
/* Chrysalide - Outil d'analyse de fichiers binaires
 * file.c - gestion du menu 'Fichier'
 *
 * Copyright (C) 2011-2019 Cyrille Bagard
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


#include "file.h"


#include <i18n.h>


#include "../core/global.h"
#include "../../analysis/project.h"
#include "../../core/global.h"
#include "../../gtkext/easygtk.h"



/* Réagit au menu "Fichier -> Nouveau projet". */
static void mcb_file_new_project(GtkMenuItem *, gpointer);

/* Réagit au menu "Fichier -> Ouvrir un projet". */
static void mcb_file_open_project(GtkMenuItem *, gpointer);

/* Réagit au menu "Fichier -> Enregistrer le projet sous...". */
static void mcb_file_save_project_as(GtkMenuItem *, gpointer);

/* Réagit avec le menu "Fichier -> Quitter". */
static void mcb_file_quit(GtkMenuItem *, gpointer);



/******************************************************************************
*                                                                             *
*  Paramètres  : builder = constructeur avec l'ensemble des références.       *
*                                                                             *
*  Description : Complète la définition du menu "Fichier".                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void setup_menu_file_callbacks(GtkBuilder *builder)
{
    gtk_builder_add_callback_symbols(builder,
                                     BUILDER_CALLBACK(mcb_file_new_project),
                                     BUILDER_CALLBACK(mcb_file_open_project),
                                     BUILDER_CALLBACK(mcb_file_save_project),
                                     BUILDER_CALLBACK(mcb_file_save_project_as),
                                     BUILDER_CALLBACK(mcb_file_quit),
                                     NULL);


#if 0
    GtkWidget *result;                      /* Support à retourner         */
    GtkWidget *menubar;                     /* Support pour éléments       */
    GtkWidget *submenuitem;                 /* Sous-élément de menu #1     */
    GtkWidget *deepmenuitem;                /* Sous-élément de menu #2     */
    GtkRecentFilter *filter;                /* Filtre gardant les projets  */


    submenuitem = qck_create_menu_item(NULL, NULL, _("Recent projects..."), NULL, NULL);
    gtk_container_add(GTK_CONTAINER(menubar), submenuitem);

    deepmenuitem = gtk_recent_chooser_menu_new_for_manager(get_project_manager());
    gtk_recent_chooser_set_sort_type(GTK_RECENT_CHOOSER(deepmenuitem), GTK_RECENT_SORT_MRU);
    gtk_recent_chooser_set_show_tips(GTK_RECENT_CHOOSER(deepmenuitem), TRUE);
    gtk_recent_chooser_set_show_icons(GTK_RECENT_CHOOSER(deepmenuitem), FALSE);
    gtk_menu_item_set_submenu(GTK_MENU_ITEM(submenuitem), deepmenuitem);

    filter = gtk_recent_filter_new();
    gtk_recent_filter_add_mime_type(filter, "application/chrysalide.project");
    gtk_recent_chooser_add_filter(GTK_RECENT_CHOOSER(deepmenuitem), filter);
#endif


}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                unused   = adresse non utilisée ici.                         *
*                                                                             *
*  Description : Réagit au menu "Fichier -> Nouveau projet".                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_file_new_project(GtkMenuItem *menuitem, gpointer unused)
{
    GStudyProject *project;                 /* Nouveau projet courant      */

    project = g_study_project_new();

    set_current_project(project);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                unused   = adresse non utilisée ici.                         *
*                                                                             *
*  Description : Réagit au menu "Fichier -> Ouvrir un projet".                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_file_open_project(GtkMenuItem *menuitem, gpointer unused)
{
    GtkWindow *editor;                      /* Fenêtre graphique principale*/
    GtkWidget *dialog;                      /* Boîte à afficher            */
    GStudyProject *project;                 /* Projet chargé               */
    gchar *filename;                        /* Nom du fichier à intégrer   */

    editor = get_editor_window();

    dialog = gtk_file_chooser_dialog_new(_("Open a project"), editor,
                                         GTK_FILE_CHOOSER_ACTION_OPEN,
                                         _("_Cancel"), GTK_RESPONSE_CANCEL,
                                         _("_Open"), GTK_RESPONSE_ACCEPT,
                                         NULL);

    project = get_current_project();

    if (g_study_project_get_filename(project) != NULL)
        gtk_file_chooser_set_filename(GTK_FILE_CHOOSER(dialog),
                                      g_study_project_get_filename(project));

    g_object_unref(G_OBJECT(project));

    if (gtk_dialog_run(GTK_DIALOG(dialog)) == GTK_RESPONSE_ACCEPT)
    {
        filename = gtk_file_chooser_get_filename(GTK_FILE_CHOOSER(dialog));

        project = g_study_project_open(filename, true);

        if (project != NULL)
        {
            set_current_project(project);
            push_project_into_recent_list(project);
        }

        g_free(filename);

    }

    gtk_widget_destroy(dialog);

    g_object_unref(G_OBJECT(editor));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                unused   = adresse non utilisée ici.                         *
*                                                                             *
*  Description : Réagit au menu "Fichier -> Enregistrer le projet".           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void mcb_file_save_project(GtkMenuItem *menuitem, gpointer unused)
{
    GStudyProject *project;                 /* Projet courant              */

    project = get_current_project();

    if (g_study_project_get_filename(project) != NULL)
    {
        if (g_study_project_save(project, NULL))
            push_project_into_recent_list(project);
    }

    else
        mcb_file_save_project_as(menuitem, NULL);

    g_object_unref(G_OBJECT(project));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                unused   = adresse non utilisée ici.                         *
*                                                                             *
*  Description : Réagit au menu "Fichier -> Enregistrer le projet sous...".   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_file_save_project_as(GtkMenuItem *menuitem, gpointer unused)
{
    GtkWindow *editor;                      /* Fenêtre graphique principale*/
    GtkWidget *dialog;                      /* Boîte à afficher            */
    GStudyProject *project;                 /* Projet courant              */
    gchar *filename;                        /* Nom du fichier à intégrer   */

    editor = get_editor_window();

    dialog = gtk_file_chooser_dialog_new(_("Save the project as..."), editor,
                                         GTK_FILE_CHOOSER_ACTION_SAVE,
                                         _("_Cancel"), GTK_RESPONSE_CANCEL,
                                         _("_Save"), GTK_RESPONSE_ACCEPT,
                                         NULL);

    project = get_current_project();

    if (g_study_project_get_filename(project) != NULL)
        gtk_file_chooser_set_filename(GTK_FILE_CHOOSER(dialog),
                                      g_study_project_get_filename(project));

    if (gtk_dialog_run(GTK_DIALOG(dialog)) == GTK_RESPONSE_ACCEPT)
    {
        filename = gtk_file_chooser_get_filename(GTK_FILE_CHOOSER(dialog));

        if (g_study_project_save(project, filename))
            push_project_into_recent_list(project);

        g_free(filename);

    }

    g_object_unref(G_OBJECT(project));

    gtk_widget_destroy(dialog);

    g_object_unref(G_OBJECT(editor));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                unused   = adresse non utilisée ici.                         *
*                                                                             *
*  Description : Réagit avec le menu "Fichier -> Quitter".                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_file_quit(GtkMenuItem *menuitem, gpointer unused)
{
    GtkWindow *editor;                      /* Fenêtre principale          */

    editor = get_editor_window();

    gtk_window_close(editor);

    g_object_unref(G_OBJECT(editor));

}
