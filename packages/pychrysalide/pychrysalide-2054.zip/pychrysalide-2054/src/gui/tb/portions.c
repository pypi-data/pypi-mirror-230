
/* Chrysalide - Outil d'analyse de fichiers binaires
 * portions.c - navigation dans les portions de binaire
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


#include "portions.h"


#include <i18n.h>


#include "tbitem-int.h"
#include "../core/global.h"
#include "../core/items.h"
#include "../../format/format.h"
#include "../../glibext/gbinarycursor.h"
#include "../../gtkext/gtkbinarystrip.h"
#include "../../gtkext/gtkdisplaypanel.h"



/* Elément réactif présentant des portions de binaire (instance) */
struct _GPortionsTbItem
{
    GToolbarItem parent;                    /* A laisser en premier        */

    GtkWidget *support;                     /* Composant GTK de support    */

};


/* Elément réactif présentant des portions de binaire (classe) */
struct _GPortionsTbItemClass
{
    GToolbarItemClass parent;               /* A laisser en premier        */

};



/* Initialise la classe des éléments réactifs de l'éditeur. */
static void g_portions_tbitem_class_init(GPortionsTbItemClass *);

/* Initialise une instance d'élément réactif pour l'éditeur. */
static void g_portions_tbitem_init(GPortionsTbItem *);

/* Supprime toutes les références externes. */
static void g_portions_tbitem_dispose(GPortionsTbItem *);

/* Procède à la libération totale de la mémoire. */
static void g_portions_tbitem_finalize(GPortionsTbItem *);

/* Fournit le nom interne attribué à l'élément réactif. */
static char *g_portions_tbitem_class_get_key(const GPortionsTbItemClass *);

/* Fournit le composant GTK associé à l'élément réactif. */
static GtkWidget *g_portions_tbitem_get_widget(const GPortionsTbItem *);

/* Réagit à un changement du binaire courant. */
static void change_portions_tbitem_current_content(GPortionsTbItem *, GLoadedContent *, GLoadedContent *);

/* Fait suivre un changement d'adresse dans la barre. */
static void track_address_on_binary_strip(GtkBinaryStrip *, GEditorItem *);



/* Indique le type défini pour un affichage de portions destiné à une barre d'outils. */
G_DEFINE_TYPE(GPortionsTbItem, g_portions_tbitem, G_TYPE_TOOLBAR_ITEM);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des éléments réactifs de l'éditeur.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_portions_tbitem_class_init(GPortionsTbItemClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GEditorItemClass *item;                 /* Encore une autre vision     */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_portions_tbitem_dispose;
    object->finalize = (GObjectFinalizeFunc)g_portions_tbitem_finalize;

    item = G_EDITOR_ITEM_CLASS(klass);

    item->get_key = (get_item_key_fc)g_portions_tbitem_class_get_key;
    item->get_widget = (get_item_widget_fc)g_portions_tbitem_get_widget;

    item->change_content = (change_item_content_fc)change_portions_tbitem_current_content;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance d'élément réactif pour l'éditeur.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_portions_tbitem_init(GPortionsTbItem *item)
{
    GtkWidget *strip;                       /* Bande pour binaire          */

    item->support = GTK_WIDGET(gtk_tool_item_new());

    gtk_tool_item_set_expand(GTK_TOOL_ITEM(item->support), TRUE);
    gtk_widget_show(item->support);

    strip = gtk_binary_strip_new();
    gtk_widget_show(strip);
    gtk_container_add(GTK_CONTAINER(item->support), strip);

    g_object_set_data(G_OBJECT(item->support), "strip", strip);

    g_signal_connect(strip, "select-address",
                     G_CALLBACK(track_address_on_binary_strip),
                     item);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_portions_tbitem_dispose(GPortionsTbItem *item)
{
    g_clear_object(&item->support);

    G_OBJECT_CLASS(g_portions_tbitem_parent_class)->dispose(G_OBJECT(item));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_portions_tbitem_finalize(GPortionsTbItem *item)
{
    G_OBJECT_CLASS(g_portions_tbitem_parent_class)->finalize(G_OBJECT(item));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ref = espace de référencement global.                        *
*                                                                             *
*  Description : Crée un élément réactif présentant des portions de binaire.  *
*                                                                             *
*  Retour      : Adresse de la structure d'encadrement mise en place.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GEditorItem *g_portions_tbitem_new(GObject *ref)
{
    GPortionsTbItem *result;                /* Structure à retourner       */

    result = g_object_new(G_TYPE_PORTIONS_TBITEM, NULL);

    g_toolbar_item_setup(G_TOOLBAR_ITEM(result), ref);

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

static char *g_portions_tbitem_class_get_key(const GPortionsTbItemClass *item)
{
    char *result;                           /* Description à renvoyer      */

    result = strdup(PORTIONS_TBITEM_ID);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = instance à consulter.                                 *
*                                                                             *
*  Description : Fournit le composant GTK associé à l'élément réactif.        *
*                                                                             *
*  Retour      : Instance de composant graphique chargé.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GtkWidget *g_portions_tbitem_get_widget(const GPortionsTbItem *item)
{
    GtkWidget *result;                      /* Composant à retourner       */

    result = item->support;

    g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = élément réactif sollicité.                            *
*                old  = ancien contenu chargé analysé.                        *
*                new  = nouveau contenu chargé à analyser.                    *
*                                                                             *
*  Description : Réagit à un changement du binaire courant.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void change_portions_tbitem_current_content(GPortionsTbItem *item, GLoadedContent *old, GLoadedContent *new)
{
    GLoadedBinary *binary;                  /* Autre version de l'instance */
    GtkBinaryStrip *strip;                  /* Bande pour binaire          */

    if (G_IS_LOADED_BINARY(new))
        binary = G_LOADED_BINARY(new);
    else
        binary = NULL;

    strip = GTK_BINARY_STRIP(g_object_get_data(G_OBJECT(item->support), "strip"));

    if (binary != NULL)
    {
        gtk_binary_strip_attach(strip, binary);
        gtk_widget_show(item->support);
    }
    else
        gtk_widget_hide(item->support);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : strip = composant d'affichage parcouru.                      *
*                addr  = nouvelle adresse du curseur courant.                 *
*                item  = élément d'éditeur représenté ici.                    *
*                                                                             *
*  Description : Fait suivre un changement d'adresse dans la barre.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void track_address_on_binary_strip(GtkBinaryStrip *strip, GEditorItem *item)
{
    const vmpa2t *addr;                     /* Nouvelle destination        */
    GLoadedPanel *panel;                    /* Afficheur effectif de code  */
    GLoadedContent *content;                /* Contenu chargé et actif     */
    GLineCursor *cursor;                    /* Emplacement à afficher      */

    addr = gtk_binary_strip_get_location(strip);

    panel = get_current_view();
    content = get_current_content();

    if (GTK_IS_DISPLAY_PANEL(panel))
        gtk_display_panel_request_move(GTK_DISPLAY_PANEL(panel), addr);

    cursor = g_binary_cursor_new();
    g_binary_cursor_update(G_BINARY_CURSOR(cursor), addr);

    focus_cursor_in_editor_items(content, cursor, item);

    g_object_unref(G_OBJECT(cursor));

    g_object_unref(G_OBJECT(content));
    g_object_unref(G_OBJECT(panel));

}
