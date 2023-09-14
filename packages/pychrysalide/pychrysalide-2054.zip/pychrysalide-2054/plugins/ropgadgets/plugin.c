
/* Chrysalide - Outil d'analyse de fichiers binaires
 * plugin.c - description et intégration du présent greffon
 *
 * Copyright (C) 2015-2019 Cyrille Bagard
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
 *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.
 */


#include "plugin.h"


#include <i18n.h>


#include <gui/core/global.h>
#include <gtkext/easygtk.h>
#include <plugins/self.h>


#include "select.h"


#ifdef INCLUDE_PYTHON3_BINDINGS
#   define PG_REQ RL("PyChrysalide")
#else
#   define PG_REQ NO_REQ
#endif



DEFINE_CHRYSALIDE_PLUGIN("RopGadgets", "Gadgets finder for a ROP chain",
                         PACKAGE_VERSION, CHRYSALIDE_WEBSITE(""),
                         PG_REQ, AL(PGA_PLUGIN_INIT));



/* Réagit avec le menu "Greffons -> Lister les gadgets ROP". */
static void mcb_plugins_list_rop_gadgets(GtkMenuItem *, gpointer);



/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à manipuler.                                *
*                                                                             *
*  Description : Prend acte du chargement du greffon.                         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

G_MODULE_EXPORT bool chrysalide_plugin_init(GPluginModule *plugin)
{
    bool result;                            /* Bilan à retourner           */
    GtkBuilder *builder;                    /* Constructeur principal      */
    GtkMenuItem *item;                      /* Menu à compléter            */
    GtkContainer *menu;                     /* Support pour éléments       */
    GtkWidget *submenuitem;                 /* Sous-élément de menu        */

    result = false;

    builder = get_editor_builder();
    if (builder == NULL)
    {
        result = true;
        goto no_editor;
    }

    item = GTK_MENU_ITEM(gtk_builder_get_object(builder, "binary"));
    if (item == NULL) goto no_binary_menu;

    menu = GTK_CONTAINER(gtk_menu_item_get_submenu(item));

    submenuitem = qck_create_menu_item(G_OBJECT(item), "binary_ropgadgets", _("List ROP gadgets"),
                                       G_CALLBACK(mcb_plugins_list_rop_gadgets), NULL);
    gtk_container_add(GTK_CONTAINER(menu), submenuitem);

    result = true;

 no_binary_menu:

    g_object_unref(G_OBJECT(builder));

 no_editor:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                unused   = adresse non utilisée ici.                         *
*                                                                             *
*  Description : Réagit avec le menu "Greffons -> Lister les gadgets ROP".    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_plugins_list_rop_gadgets(GtkMenuItem *menuitem, gpointer unused)
{
    GtkWindow *editor;                      /* Fenêtre graphique principale*/

    editor = get_editor_window();

    run_rop_finder_assistant(editor);

    g_object_unref(G_OBJECT(editor));

}
