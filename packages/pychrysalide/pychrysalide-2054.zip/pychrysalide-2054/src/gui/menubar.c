
/* Chrysalide - Outil d'analyse de fichiers binaires
 * menubar.c - gestion des différents menus de la fenêtre principale
 *
 * Copyright (C) 2011-2020 Cyrille Bagard
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


#include "menubar.h"


#include <string.h>


#include "item-int.h"
#include "core/global.h"
#include "menus/binary.h"
#include "menus/debug.h"
#include "menus/edition.h"
#include "menus/file.h"
#include "menus/help.h"
#include "menus/options.h"
#include "menus/project.h"
#include "menus/view.h"



/* Barre de menus de la fenêtre principale (instance) */
struct _GMenuBar
{
    GEditorItem parent;                     /* A laisser en premier        */

    GtkBuilder *builder;                    /* Constructeur des menus      */

};


/* Barre de menus de la fenêtre principale (classe) */
struct _GMenuBarClass
{
    GEditorItemClass parent;                /* A laisser en premier        */

};


/* Initialise la classe de la barre de menus de l'éditeur. */
static void g_menu_bar_class_init(GMenuBarClass *);

/* Initialise une instance de la barre de menus pour l'éditeur. */
static void g_menu_bar_init(GMenuBar *);

/* Supprime toutes les références externes. */
static void g_menu_bar_dispose(GMenuBar *);

/* Procède à la libération totale de la mémoire. */
static void g_menu_bar_finalize(GMenuBar *);

/* Fournit le nom humain attribué à l'élément réactif. */
static char *g_menu_bar_class_get_key(const GMenuBarClass *);

/* Fournit le composant GTK associé à l'élément réactif. */
static GtkWidget *g_menu_bar_get_widget(GMenuBar *);

/* Réagit à un changement d'affichage principal de contenu. */
static void change_menubar_current_content(GMenuBar *, GLoadedContent *, GLoadedContent *);

/*  Lance une actualisation du fait d'un changement de support. */
static void change_menubar_current_view(GMenuBar *, GLoadedPanel *, GLoadedPanel *);

/* Met à jour les accès aux menus en fonction de la position. */
static void track_caret_address_for_menu_bar(GMenuBar *, GLoadedPanel *, const GLineCursor *);

/* Lance une actualisation relative à l'étendue du projet. */
static void update_menu_bar_for_project(GMenuBar *, GStudyProject *);



/* Indique le type défini pour la barre de menus de la fenêtre principale. */
G_DEFINE_TYPE(GMenuBar, g_menu_bar, G_TYPE_EDITOR_ITEM);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe de la barre de menus de l'éditeur.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_menu_bar_class_init(GMenuBarClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GEditorItemClass *item;               /* Encore une autre vision...  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_menu_bar_dispose;
    object->finalize = (GObjectFinalizeFunc)g_menu_bar_finalize;

    item = G_EDITOR_ITEM_CLASS(klass);

    item->get_key = (get_item_key_fc)g_menu_bar_class_get_key;
    item->get_widget = (get_item_widget_fc)g_menu_bar_get_widget;

    item->change_content = (change_item_content_fc)change_menubar_current_content;
    item->change_view = (change_item_view_fc)change_menubar_current_view;
    item->track_cursor = (track_cursor_in_view_fc)track_caret_address_for_menu_bar;
    item->update_project = (update_project_fc)update_menu_bar_for_project;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bar = instance à initialiser.                                *
*                                                                             *
*  Description : Initialise une instance de la barre de menus pour l'éditeur. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_menu_bar_init(GMenuBar *bar)
{
    bar->builder = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bar = instance d'objet GLib à traiter.                       *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_menu_bar_dispose(GMenuBar *bar)
{
    g_clear_object(&bar->builder);

    G_OBJECT_CLASS(g_menu_bar_parent_class)->dispose(G_OBJECT(bar));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bar = instance d'objet GLib à traiter.                       *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_menu_bar_finalize(GMenuBar *bar)
{
    G_OBJECT_CLASS(g_menu_bar_parent_class)->finalize(G_OBJECT(bar));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : builder = constructeur principal de l'éditeur.               *
*                                                                             *
*  Description : Compose la barre de menus principale.                        *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GEditorItem *g_menu_bar_new(GtkBuilder *builder)
{
    GMenuBar *result;                       /* Structure à retourner       */

    result = g_object_new(G_TYPE_MENU_BAR, NULL);

    result->builder = builder;
    g_object_ref(G_OBJECT(builder));

    setup_menu_file_callbacks(builder);
    setup_menu_edition_callbacks(builder);
    setup_menu_view_callbacks(builder);
    setup_menu_project_callbacks(builder);
    setup_menu_binary_callbacks(builder);
    setup_menu_debug_callbacks(builder);
    setup_menu_options_callbacks(builder);
    setup_menu_help_callbacks(builder);

    return G_EDITOR_ITEM(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à consulter.                                  *
*                                                                             *
*  Description : Fournit le nom humain attribué à l'élément réactif.          *
*                                                                             *
*  Retour      : Désignation (courte) de l'élément de l'éditeur.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_menu_bar_class_get_key(const GMenuBarClass *class)
{
    char *result;                           /* Description à renvoyer      */

    result = strdup("menubar");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bar = instance à consulter.                                  *
*                                                                             *
*  Description : Fournit le composant GTK associé à l'élément réactif.        *
*                                                                             *
*  Retour      : Instance de composant graphique chargé.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GtkWidget *g_menu_bar_get_widget(GMenuBar *bar)
{
    GtkWidget *result;                      /* Composant à retourner       */

    result = GTK_WIDGET(gtk_builder_get_object(bar->builder, "menubar"));

    g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bar = barre de menus à mettre à jour.                        *
*                old = ancien contenu chargé analysé.                         *
*                new = nouveau contenu chargé à analyser.                     *
*                                                                             *
*  Description : Réagit à un changement d'affichage principal de contenu.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void change_menubar_current_content(GMenuBar *bar, GLoadedContent *old, GLoadedContent *new)
{
    rebuild_menu_view_for_content(bar->builder, new);

    update_access_for_content_in_menu_binary(bar->builder, new);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bar = barre de menus à mettre à jour.                        *
*                old = ancienne vue du contenu chargé analysé.                *
*                new = nouvelle vue du contenu chargé analysé.                *
*                                                                             *
*  Description : Lance une actualisation du fait d'un changement de support.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void change_menubar_current_view(GMenuBar *bar, GLoadedPanel *old, GLoadedPanel *new)
{
    update_access_for_view_in_menu_edition(bar->builder, new);

    rebuild_menu_view_for_view(bar->builder, new);

    update_access_for_view_in_menu_view(bar->builder, new);

    update_access_for_view_in_menu_binary(bar->builder, new);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bar   = barre de menus à actualiser.                         *
*                panel  = composant d'affichage parcouru.                     *
*                cursor = nouvel emplacement du curseur courant.              *
*                                                                             *
*  Description : Met à jour les accès aux menus en fonction de la position.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void track_caret_address_for_menu_bar(GMenuBar *bar, GLoadedPanel *panel, const GLineCursor *cursor)
{
    update_access_for_cursor_in_menu_edition(bar->builder, panel, cursor);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bar     = barre de menus à actualiser.                       *
*                project = projet visé par la procédure.                      *
*                                                                             *
*  Description : Lance une actualisation relative à l'étendue du projet.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void update_menu_bar_for_project(GMenuBar *bar, GStudyProject *project)
{
    update_menu_project_for_project(bar->builder, project);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bar = instance à consulter.                                  *
*                                                                             *
*  Description : Fournit le constructeur associé à la barre de menus.         *
*                                                                             *
*  Retour      : Instance du constructeur (principal) associé à la barre.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkBuilder *g_menu_bar_get_builder(const GMenuBar *bar)
{
    GtkBuilder *result;                     /* Constructeur à renvoyer     */

    result = bar->builder;

    g_object_ref(G_OBJECT(result));

    return result;

}
