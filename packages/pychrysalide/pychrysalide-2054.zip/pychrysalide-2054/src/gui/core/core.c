
/* Chrysalide - Outil d'analyse de fichiers binaires
 * core.c - chargement et le déchargement du tronc commun pour l'éditeur graphique
 *
 * Copyright (C) 2016-2019 Cyrille Bagard
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


#include "core.h"


#include "global.h"
#include "items.h"
#include "panels.h"
#include "theme.h"
#include "../menubar.h"
#include "../menus/view.h"
#include "../panels/welcome.h"
#include "../../core/params.h"
#include "../../glibext/linesegment.h"
#include "../../gtkext/tiledgrid.h"



/* Charge les panneaux sur la base de la configuration fournie. */
static bool apply_panel_items_configuration(GPanelItemClass *, GGenConfig *);



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Charge les éléments graphiques de l'éditeur.                 *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_all_gui_components(void)
{
    bool result;                            /* Bilan à retourner           */
    GMenuBar *bar;                          /* Gestion des menus           */
    GtkBuilder *builder;                    /* Constructeur principal      */
    GtkMenuItem *submenuitem;               /* Sous-élément de menu        */

    result = true;

    load_main_panels();

    /**
     * Charge une liste initiale pour activer les raccourcis clavier.
     */

    bar = G_MENU_BAR(find_editor_item_by_type(G_TYPE_MENU_BAR));

    builder = get_editor_builder();

    submenuitem = GTK_MENU_ITEM(gtk_builder_get_object(builder, "view_side_panels"));

    mcb_view_update_side_panels_list(submenuitem, bar);

    g_object_unref(G_OBJECT(builder));

    g_object_unref(G_OBJECT(bar));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class  = classe de panneau enregistré comme existant.        *
*                config = configuration à charger.                            *
*                                                                             *
*  Description : Charge les panneaux sur la base de la configuration fournie. *
*                                                                             *
*  Retour      : true, par conformité avec browse_all_item_panels().          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool apply_panel_items_configuration(GPanelItemClass *class, GGenConfig *config)
{
    GPanelItem *panel;                      /* Panneau à mettre en place   */

    if (gtk_panel_item_class_dock_at_startup(class))
    {
        panel = g_panel_item_new(G_TYPE_FROM_CLASS(class), "");
        g_object_unref(G_OBJECT(panel));
    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : config = configuration globale à utiliser.                   *
*                                                                             *
*  Description : Finalise le chargement des éléments graphiques de l'éditeur. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool complete_loading_of_all_gui_components(GGenConfig *config)
{
    bool result;                            /* Bilan à faire remonter      */
    const char *name;                       /* Nom du thème recherché      */
    GtkTiledGrid *grid;                     /* Composant d'affichage       */
    GPanelItem *welcome;                    /* Panneau d'accueil           */

    result = g_generic_config_get_value(config, MPK_INTERNAL_THEME, &name);
    if (!result) goto no_theme;

    load_all_themes();

    apply_gtk_theme(name);

    result = load_segment_rendering_parameters();

    grid = get_tiled_grid();

    welcome = g_panel_item_new(G_TYPE_WELCOME_PANEL, NULL);
    gtk_tiled_grid_set_default_main_panel(grid, welcome);
    g_object_unref(G_OBJECT(welcome));

    /**
     * Le fait d'avoir défini le panneau d'accueil par défaut va l'afficher,
     * comme il n'y a encore aucun autre panneau. Ce qui va mémoriser son
     * paramètre d'affichage par défaut au démarrage à vrai.
     *
     * Or gtk_panel_item_apply_configuration() s'occupe précisément de
     * restaurer les affichages de panneaux au démarrage.
     *
     * Donc on doit sauter ce panneau d'accueil lors de l'appel suivant.
     */

    if (result)
        result = _browse_all_item_panels(true, (handle_panel_item_fc)apply_panel_items_configuration, config);

    /**
     * Comme la boucle de traitements GTK n'est pas encore lancée, tous les
     * traitements opérant sur la fenêtre principale n'ont pas abouti.
     *
     * Les dimensions finales ne sont ainsi pas encore appliquées, or la
     * restauration des positions s'appuie dessus.
     *
     * On actualise donc les espaces disponibles manuellement avant cette phase
     * de restauration.
     */

    while (gtk_events_pending())
        gtk_main_iteration();

    gtk_tiled_grid_restore_positions(grid, config);

 no_theme:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Décharge les éléments graphiques de l'éditeur.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void unload_all_gui_components(void)
{
    exit_segment_content_hash_table();

    unload_all_themes();

}
