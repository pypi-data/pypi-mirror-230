
/* Chrysalide - Outil d'analyse de fichiers binaires
 * view.c - panneau d'affichage de contenu binaire
 *
 * Copyright (C) 2020 Cyrille Bagard
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


#include "view.h"


#include <string.h>


#include "../panel-int.h"
#include "../core/global.h"
#include "../core/items.h"
#include "../../gtkext/named.h"
#include "../../plugins/pglist.h"



/* Panneau d'affichage pour contenu binaire (instance) */
struct _GViewPanel
{
    GPanelItem parent;                      /* A laisser en premier        */

};

/* Panneau d'affichage pour contenu binaire (classe) */
struct _GViewPanelClass
{
    GPanelItemClass parent;                 /* A laisser en premier        */

};


/* Initialise la classe des panneaux de contenu binaire. */
static void g_view_panel_class_init(GViewPanelClass *);

/* Initialise une instance de panneau de contenu binaire. */
static void g_view_panel_init(GViewPanel *);

/* Supprime toutes les références externes. */
static void g_view_panel_dispose(GViewPanel *);

/* Procède à la libération totale de la mémoire. */
static void g_view_panel_finalize(GViewPanel *);

/* Fournit le nom interne attribué à l'élément réactif. */
static char *g_view_panel_class_get_key(const GViewPanelClass *);

/* Fournit une indication sur la personnalité du panneau. */
static PanelItemPersonality g_view_panel_class_get_personality(const GViewPanelClass *);

/* Indique le chemin initial de la localisation d'un panneau. */
static char *g_view_panel_class_get_path(const GViewPanelClass *);



/* Indique le type défini pour un panneau de contenu binaire. */
G_DEFINE_TYPE(GViewPanel, g_view_panel, G_TYPE_PANEL_ITEM);


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des panneaux de contenu binaire.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_view_panel_class_init(GViewPanelClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GEditorItemClass *item;                 /* Encore une autre vision...  */
    GPanelItemClass *panel;                 /* Version parente de classe   */

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_view_panel_dispose;
    object->finalize = (GObjectFinalizeFunc)g_view_panel_finalize;

    item = G_EDITOR_ITEM_CLASS(class);

    item->get_key = (get_item_key_fc)g_view_panel_class_get_key;

    panel = G_PANEL_ITEM_CLASS(class);

    panel->get_personality = (get_panel_personality_fc)g_view_panel_class_get_personality;
    panel->get_path = (get_panel_path_fc)g_view_panel_class_get_path;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance de panneau de contenu binaire.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_view_panel_init(GViewPanel *panel)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_view_panel_dispose(GViewPanel *panel)
{
    G_OBJECT_CLASS(g_view_panel_parent_class)->dispose(G_OBJECT(panel));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_view_panel_finalize(GViewPanel *panel)
{
    G_OBJECT_CLASS(g_view_panel_parent_class)->finalize(G_OBJECT(panel));

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

static char *g_view_panel_class_get_key(const GViewPanelClass *class)
{
    char *result;                           /* Description à renvoyer      */

    result = strdup(PANEL_VIEW_ID);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à consulter.                                  *
*                                                                             *
*  Description : Fournit une indication sur la personnalité du panneau.       *
*                                                                             *
*  Retour      : Identifiant lié à la nature unique du panneau.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PanelItemPersonality g_view_panel_class_get_personality(const GViewPanelClass *class)
{
    PanelItemPersonality result;            /* Personnalité à retourner    */

    result = PIP_BINARY_VIEW;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à consulter.                                  *
*                                                                             *
*  Description : Indique le chemin initial de la localisation d'un panneau.   *
*                                                                             *
*  Retour      : Chemin fixé associé à la position initiale.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_view_panel_class_get_path(const GViewPanelClass *class)
{
    char *result;                           /* Emplacement à retourner     */

    result = strdup("M");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget = composant avec noms à présenter à l'affichage.      *
*                                                                             *
*  Description : Crée un panneau pour l'affichage d'un contenu binaire.       *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GPanelItem *g_view_panel_new(GNamedWidget *widget)
{
    GPanelItem *result;                     /* Structure à retourner       */
    GtkTiledGrid *grid;                     /* Composant d'affichage       */

    result = g_object_new(G_TYPE_VIEW_PANEL, NULL);

    result->widget = widget;
    g_object_ref(G_OBJECT(widget));

    grid = get_tiled_grid();

    g_signal_connect_swapped(result, "dock-request", G_CALLBACK(gtk_tiled_grid_add), grid);
    g_signal_connect_swapped(result, "undock-request", G_CALLBACK(gtk_tiled_grid_remove), grid);

    gtk_dockable_setup_dnd(GTK_DOCKABLE(result));

    register_editor_item(G_EDITOR_ITEM(result));

    notify_panel_creation(result);

    return result;

}
