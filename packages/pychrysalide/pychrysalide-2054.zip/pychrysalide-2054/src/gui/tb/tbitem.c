
/* Chrysalide - Outil d'analyse de fichiers binaires
 * tbitem.c - gestion des éléments réactifs spécifiques à la barre d'outils
 *
 * Copyright (C) 2014-2020 Cyrille Bagard
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


#include "tbitem.h"


#include <gtk/gtkcontainer.h>


#include "tbitem-int.h"



/* Initialise la classe des éléments réactifs de l'éditeur. */
static void g_toolbar_item_class_init(GToolbarItemClass *);

/* Initialise une instance d'élément réactif pour l'éditeur. */
static void g_toolbar_item_init(GToolbarItem *);



/* Indique le type défini pour un élément destiné à une barre d'outils. */
G_DEFINE_TYPE(GToolbarItem, g_toolbar_item, G_TYPE_EDITOR_ITEM);


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

static void g_toolbar_item_class_init(GToolbarItemClass *klass)
{

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

static void g_toolbar_item_init(GToolbarItem *item)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tbitem = élément de barre d'outils à finaliser.              *
*                ref    = espace de référencement global.                     *
*                                                                             *
*  Description : Termine la préparation d'un élément de barre d'outils.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_toolbar_item_setup(GToolbarItem *tbitem, GObject *ref)
{
    GtkContainer *toolbar;                  /* Barre d'outils visée        */
    GtkWidget *widget;                      /* Composant GTK à intégrer    */

    /* Intégration dans la barre */

    toolbar = GTK_CONTAINER(g_object_get_data(ref, "toolbar"));

    widget = g_editor_item_get_widget(G_EDITOR_ITEM(tbitem));

    gtk_container_add(toolbar, widget);

}
