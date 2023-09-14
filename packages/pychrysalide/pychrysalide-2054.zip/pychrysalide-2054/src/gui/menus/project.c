
/* Chrysalide - Outil d'analyse de fichiers binaires
 * project.c - gestion du menu 'Projet'
 *
 * Copyright (C) 2012-2020 Cyrille Bagard
 *
 *  This project is part of Chrysalide.
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


#include "project.h"


#include <i18n.h>
#include <libgen.h>
#include <malloc.h>
#include <string.h>


#include "../item-int.h"
#include "../menubar.h"
#include "../core/global.h"
#include "../../analysis/loading.h"
#include "../../analysis/contents/file.h"
#include "../../core/global.h"
#include "../../gtkext/easygtk.h"



/* Affiche la boîte d'ajout d'un binaire au projet courant. */
static void mcb_project_add_binary_file(GtkMenuItem *, GMenuBar *);

/* Retire un contenu du projet indiqué. */
static void mcb_project_remove_content(GtkMenuItem *, GStudyProject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : builder = constructeur avec l'ensemble des références.       *
*                                                                             *
*  Description : Complète la définition du menu "Projet".                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void setup_menu_project_callbacks(GtkBuilder *builder)
{
    GObject *item;                          /* Elément à compléter         */

    gtk_builder_add_callback_symbols(builder,
                                     BUILDER_CALLBACK(mcb_project_add_binary_file),
                                     NULL);

    /* Projet -> Retirer un binaire */

    item = gtk_builder_get_object(builder, "project_remove");

    qck_create_menu(GTK_MENU_ITEM(item));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                bar      = barre de menu parente.                            *
*                                                                             *
*  Description : Affiche la boîte d'ajout d'un binaire au projet courant.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_project_add_binary_file(GtkMenuItem *menuitem, GMenuBar *bar)
{
    GtkWindow *editor;                      /* Fenêtre graphique principale*/
    GtkWidget *dialog;                      /* Boîte à afficher            */
    GStudyProject *project;                 /* Projet courant              */
    char *dir;                              /* Répertoire courant          */
    gchar *filename;                        /* Nom du fichier à intégrer   */
    GBinContent *content;                   /* Contenu binaire à charger   */

    editor = get_editor_window();

    dialog = gtk_file_chooser_dialog_new(_("Open a binary file"),
                                         editor,
                                         GTK_FILE_CHOOSER_ACTION_OPEN,
                                         _("_Cancel"), GTK_RESPONSE_CANCEL,
                                         _("_Open"), GTK_RESPONSE_ACCEPT,
                                         NULL);

    project = get_current_project();

    if (g_study_project_get_filename(project) != NULL)
    {
        dir = strdup(g_study_project_get_filename(project));
        dir = dirname(dir);
        gtk_file_chooser_set_current_folder(GTK_FILE_CHOOSER(dialog), dir);
        free(dir);
    }

    if (gtk_dialog_run(GTK_DIALOG(dialog)) == GTK_RESPONSE_ACCEPT)
    {
        filename = gtk_file_chooser_get_filename(GTK_FILE_CHOOSER(dialog));

        content = g_file_content_new(filename);

        if (content != NULL)
        {
            g_study_project_discover_binary_content(project, content, true, NULL, NULL);
            g_object_unref(G_OBJECT(content));
        }

        g_free(filename);

    }

    g_object_unref(G_OBJECT(project));

    gtk_widget_destroy(dialog);

    g_object_unref(G_OBJECT(editor));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                project  = projet d'appartenance du binaire à traiter.       *
*                                                                             *
*  Description : Retire un contenu du projet indiqué.                         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_project_remove_content(GtkMenuItem *menuitem, GStudyProject *project)
{
    GObject *ref;                           /* Espace de référencement     */
    GLoadedContent *content;                /* Contenu à retirer           */

    ref = G_OBJECT(menuitem);

    content = G_LOADED_CONTENT(g_object_get_data(ref, "content"));

    g_study_project_detach_content(project, content);

    g_object_set_data(ref, "content", NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : builder = constructeur avec l'ensemble des références.       *
*                project = projet visé par la procédure.                      *
*                                                                             *
*  Description : Lance une actualisation relative à l'étendue du projet.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void update_menu_project_for_project(GtkBuilder *builder, GStudyProject *project)
{
    GtkWidget *menuitem;                    /* Menu principal à compléter  */
    GtkWidget *submenu;                     /* Support pour éléments       */
    GList *list;                            /* Liste des éléments en place */
    GList *iter;                            /* Boucle de parcours #1       */
    size_t count;                           /* Nombre de contenus attachés */
    GLoadedContent **contents;              /* Liste de ces contenus       */
    size_t i;                               /* Boucle de parcours #2       */
    char *desc;                             /* Description à afficher      */
    GtkWidget *submenuitem;                 /* Sous-menu à ajouter         */

    menuitem = GTK_WIDGET(gtk_builder_get_object(builder, "project_remove"));
    submenu = gtk_menu_item_get_submenu(GTK_MENU_ITEM(menuitem));

    /* Remise à zéro */

    list = gtk_container_get_children(GTK_CONTAINER(submenu));

    for (iter = list; iter != NULL; iter = g_list_next(iter))
        gtk_container_remove(GTK_CONTAINER(submenu), GTK_WIDGET(iter->data));

    g_list_free(list);

    /* Ajout des entrées */ 

    contents = g_study_project_get_contents(project, &count);

    for (i = 0; i < count; i++)
    {
        desc = g_loaded_content_describe(contents[i], true);

        submenuitem = qck_create_menu_item(NULL, NULL, desc,
                                           G_CALLBACK(mcb_project_remove_content), project);
        g_object_set_data_full(G_OBJECT(submenuitem), "content", contents[i], g_object_unref);
        gtk_container_add(GTK_CONTAINER(submenu), submenuitem);

        free(desc);

        /**
         * Note : l'appel à g_object_unref() est réalisé lorsque la référence
         *        est retirée du menu.
         */

    }

    if (contents != NULL)
        free(contents);

    gtk_widget_set_sensitive(menuitem, count > 0);

}
