
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gloadedpanel.c - affichage de contenus chargés
 *
 * Copyright (C) 2017-2018 Cyrille Bagard
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


#include "gloadedpanel.h"


#include "chrysamarshal.h"
#include "gloadedpanel-int.h"



/* Procède à l'initialisation de l'interface d'affichage. */
static void g_loaded_panel_default_init(GLoadedPanelInterface *);



/* Détermine le type du composant d'affichage basique. */
G_DEFINE_INTERFACE(GLoadedPanel, g_loaded_panel, G_TYPE_OBJECT)


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface d'affichage.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_loaded_panel_default_init(GLoadedPanelInterface *iface)
{
    g_signal_new("move-request",
                 G_TYPE_LOADED_PANEL,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GLoadedPanelIface, move_request),
                 NULL, NULL,
                 g_cclosure_user_marshal_VOID__OBJECT_BOOLEAN,
                 G_TYPE_NONE, 2, G_TYPE_LINE_CURSOR, G_TYPE_BOOLEAN);

    g_signal_new("cursor-moved",
                 G_TYPE_LOADED_PANEL,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GLoadedPanelIface, cursor_moved),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__OBJECT,
                 G_TYPE_NONE, 1, G_TYPE_LINE_CURSOR);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel   = composant GTK à compléter.                         *
*                content = contenu quelconque chargé en mémoire.              *
*                                                                             *
*  Description : Définit le contenu associé à un panneau de chargement.       *
*                                                                             *
*  Retour      :                                                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_loaded_panel_set_content(GLoadedPanel *panel, GLoadedContent *content)
{
    GLoadedPanelIface *iface;               /* Interface utilisée          */

    g_object_ref(G_OBJECT(content));

    iface = G_LOADED_PANEL_GET_IFACE(panel);

    iface->set_content(panel, content);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = composant GTK à consulter.                           *
*                                                                             *
*  Description : Fournit le contenu associé à un panneau de chargement.       *
*                                                                             *
*  Retour      : Contenu quelconque chargé en mémoire.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GLoadedContent *g_loaded_panel_get_content(const GLoadedPanel *panel)
{
    GLoadedContent *result;                 /* Contenu à retourner         */
    GLoadedPanelIface *iface;               /* Interface utilisée          */

    iface = G_LOADED_PANEL_GET_IFACE(panel);

    result = iface->get_content(panel);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = composant GTK à consulter.                           *
*                                                                             *
*  Description : Fournit le position courante dans un panneau de chargement.  *
*                                                                             *
*  Retour      : Informations relatives à la position du curseur.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GLineCursor *g_loaded_panel_get_cursor(const GLoadedPanel *panel)
{
    GLineCursor *result;                    /* Contenu à retourner         */
    GLoadedPanelIface *iface;               /* Interface utilisée          */

    iface = G_LOADED_PANEL_GET_IFACE(panel);

    result = iface->get_cursor(panel);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel  = composant GTK à manipuler.                          *
*                cursor = emplacement à cibler pour un déplacement.           *
*                save   = le changement est-il majeur ?                       *
*                                                                             *
*  Description : Demande à qui veut répondre un déplacement du curseur.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_loaded_panel_request_move(GLoadedPanel *panel, const GLineCursor *cursor, gboolean save)
{
    g_signal_emit_by_name(panel, "move-request", cursor, save);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel  = composant GTK à manipuler.                          *
*                cursor = emplacement à présenter à l'écran.                  *
*                tweak  = adaptation finale à effectuer.                      *
*                move   = doit-on déplacer le curseur à l'adresse indiquée ?  *
*                                                                             *
*  Description : S'assure qu'un emplacement donné est visible à l'écran.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_loaded_panel_scroll_to_cursor(GLoadedPanel *panel, const GLineCursor *cursor, ScrollPositionTweak tweak, bool move)
{
    GLoadedPanelIface *iface;               /* Interface utilisée          */

    iface = G_LOADED_PANEL_GET_IFACE(panel);

    iface->scroll(panel, cursor, tweak, move);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = composant GTK à manipuler.                           *
*                cairo = assistant pour la création de rendus.                *
*                area  = taille de la surface réduite à disposition.          *
*                scale = échelle vis à vis de la taille réelle.               *
*                                                                             *
*  Description : Place en cache un rendu destiné à l'aperçu graphique rapide. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_loaded_panel_cache_glance(GLoadedPanel *panel, cairo_t *cairo, const GtkAllocation *area, double scale)
{
    GLoadedPanelIface *iface;               /* Interface utilisée          */

    iface = G_LOADED_PANEL_GET_IFACE(panel);

    iface->cache_glance(panel, cairo, area, scale);

}
