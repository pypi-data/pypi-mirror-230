
/* Chrysalide - Outil d'analyse de fichiers binaires
 * status.c - affichage d'informations de statut dans la fenêtre principale
 *
 * Copyright (C) 2013-2020 Cyrille Bagard
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


#include "status.h"


#include <assert.h>
#include <ctype.h>
#include <string.h>


#include <i18n.h>


#include "item-int.h"
#include "core/global.h"
#include "../common/extstr.h"
#include "../gtkext/gtkbufferdisplay.h"
#include "../gtkext/gtkstatusstack.h"



/* Barre de statut de la fenêtre principale (instance) */
struct _GStatusInfo
{
    GEditorItem parent;                     /* A laisser en premier        */

    GtkStatusStack *stack;                  /* Composant GTK associé       */

};


/* Barre de statut de la fenêtre principale (classe) */
struct _GStatusInfoClass
{
    GEditorItemClass parent;                /* A laisser en premier        */

};


/* Initialise la classe de la barre de statut de l'éditeur. */
static void g_status_info_class_init(GStatusInfoClass *);

/* Initialise une instance de la barre de statut pour l'éditeur. */
static void g_status_info_init(GStatusInfo *);

/* Supprime toutes les références externes. */
static void g_status_info_dispose(GStatusInfo *);

/* Procède à la libération totale de la mémoire. */
static void g_status_info_finalize(GStatusInfo *);

/* Fournit le nom interne attribué à l'élément réactif. */
static char *g_status_info_class_get_key(const GStatusInfoClass *);

/* Fournit le composant GTK associé à l'élément réactif. */
static GtkWidget *g_status_info_get_widget(const GStatusInfo *);

/* Imprime la position du parcours courant dans le statut. */
static void track_cursor_for_status_info(GStatusInfo *, GLoadedPanel *, const GLineCursor *);

/* Concentre l'attention de l'ensemble sur une adresse donnée. */
static void focus_cursor_in_status_info(GStatusInfo *, GLoadedContent *, const GLineCursor *);



/* Indique le type défini pour la barre de statut de la fenêtre principale. */
G_DEFINE_TYPE(GStatusInfo, g_status_info, G_TYPE_EDITOR_ITEM);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe de la barre de statut de l'éditeur.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_status_info_class_init(GStatusInfoClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GEditorItemClass *item;                 /* Encore une autre vision...  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_status_info_dispose;
    object->finalize = (GObjectFinalizeFunc)g_status_info_finalize;

    item = G_EDITOR_ITEM_CLASS(klass);

    item->get_key = (get_item_key_fc)g_status_info_class_get_key;
    item->get_widget = (get_item_widget_fc)g_status_info_get_widget;

    item->track_cursor = (track_cursor_in_view_fc)track_cursor_for_status_info;
    item->focus_cursor = (focus_cursor_fc)focus_cursor_in_status_info;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance de la barre de statut pour l'éditeur.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_status_info_init(GStatusInfo *info)
{
    info->stack = gtk_status_stack_new();
    gtk_widget_show(GTK_WIDGET(info->stack));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_status_info_dispose(GStatusInfo *info)
{
    g_clear_object(&info->stack);

    G_OBJECT_CLASS(g_status_info_parent_class)->dispose(G_OBJECT(info));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_status_info_finalize(GStatusInfo *info)
{
    G_OBJECT_CLASS(g_status_info_parent_class)->finalize(G_OBJECT(info));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Compose la barre de statut principale.                       *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GEditorItem *g_status_info_new(void)
{
    GStatusInfo *result;                    /* Structure à retourner       */

    result = g_object_new(G_TYPE_STATUS_INFO, NULL);

    set_global_status(result->stack);

    return G_EDITOR_ITEM(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à consulter.                                  *
*                                                                             *
*  Description : Fournit le nom interne attribué à l'élément réactif.         *
*                                                                             *
*  Retour      : Désignation (courte) de l'élément de l'éditeur.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_status_info_class_get_key(const GStatusInfoClass *class)
{
    char *result;                           /* Description à renvoyer      */

    result = strdup(STATUS_INFO_ID);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = instance à consulter.                                 *
*                                                                             *
*  Description : Fournit le composant GTK associé à l'élément réactif.        *
*                                                                             *
*  Retour      : Instance de composant graphique chargé.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GtkWidget *g_status_info_get_widget(const GStatusInfo *info)
{
    GtkWidget *result;                      /* Composant à retourner       */

    result = GTK_WIDGET(info->stack);

    g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info   = barre de statut présentant les informations.        *
*                panel  = composant d'affichage parcouru.                     *
*                cursor = nouvel emplacement du curseur courant.              *
*                                                                             *
*  Description : Imprime la position du parcours courant dans le statut.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void track_cursor_for_status_info(GStatusInfo *info, GLoadedPanel *panel, const GLineCursor *cursor)
{
    GLoadedContent *content;                /* Contenu courant             */

    content = g_loaded_panel_get_content(panel);

    focus_cursor_in_status_info(info, content, cursor);

    g_object_unref(G_OBJECT(content));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info    = composant réactif à mettre à jour.                 *
*                content = contenu contenant le curseur à représenter.        *
*                cursor  = nouvel emplacement du curseur courant.             *
*                                                                             *
*  Description : Concentre l'attention de l'ensemble sur une adresse donnée.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void focus_cursor_in_status_info(GStatusInfo *info, GLoadedContent *content, const GLineCursor *cursor)
{
    g_line_cursor_show_status(cursor, info->stack, content);

}
