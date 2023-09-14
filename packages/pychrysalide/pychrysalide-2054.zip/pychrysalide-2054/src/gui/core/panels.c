
/* Chrysalide - Outil d'analyse de fichiers binaires
 * panels.c - gestion d'ensemble de tous les panneaux pour l'éditeur
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
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#include "panels.h"


#include <assert.h>
#include <malloc.h>


#include "items.h"
#include "../panel-int.h"
#include "../panels/bintree.h"
#include "../panels/bookmarks.h"
#include "../panels/errors.h"
#include "../panels/glance.h"
#include "../panels/history.h"
#include "../panels/log.h"
#include "../panels/regedit.h"
#include "../panels/strings.h"
#include "../panels/symbols.h"
#include "../panels/welcome.h"
#include "../../core/params.h"



/* Liste des panneaux disponibles */
static GType *_panels_list = NULL;
static size_t _panels_count = 0;



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Charge les principaux panneaux de l'éditeur.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void load_main_panels(void)
{
    GGenConfig *config;                     /* Configuration globale       */
    GPanelItem *panel;                      /* Panneau à précharger        */

    config = get_main_configuration();

    register_panel_item(G_TYPE_LOG_PANEL, config);

    /* Chargement du panneau de rapport au plus tôt */
    panel = g_panel_item_new(G_TYPE_LOG_PANEL, NULL);
    g_object_unref(G_OBJECT(panel));

    register_panel_item(G_TYPE_WELCOME_PANEL, config);
    register_panel_item(G_TYPE_REGEDIT_PANEL, config);
    register_panel_item(G_TYPE_SYMBOLS_PANEL, config);
    register_panel_item(G_TYPE_HISTORY_PANEL, config);
    register_panel_item(G_TYPE_STRINGS_PANEL, config);
    register_panel_item(G_TYPE_GLANCE_PANEL, config);
    register_panel_item(G_TYPE_BOOKMARKS_PANEL, config);
    register_panel_item(G_TYPE_BINTREE_PANEL, config);
    register_panel_item(G_TYPE_ERROR_PANEL, config);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type   = type du composant à présenter à l'affichage.        *
*                config = configuration à compléter.                          *
*                                                                             *
*  Description : Enregistre un panneau comme partie intégrante de l'éditeur.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void register_panel_item(GType type, GGenConfig *config)
{
    GPanelItemClass *class;                 /* Classe associée au type     */
#ifndef NDEBUG
    bool status;                            /* Bilan de mise en place      */
#endif

    _panels_list = realloc(_panels_list, ++_panels_count * sizeof(GType));

    _panels_list[_panels_count - 1] = type;

    class = g_type_class_ref(type);

#ifndef NDEBUG
    status = gtk_panel_item_class_setup_configuration(class, config);
    assert(status);
#else
    gtk_panel_item_class_setup_configuration(class, config);
#endif

    g_type_class_unref(class);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : skip   = saute le panneau d'accueil lors du parcours ?       *
*                handle = routine à appeler pour chaque panneau.              *
*                data   = données fournies pour accompagner cet appel.        *
*                                                                             *
*  Description : Effectue le parcours de tous les panneaux chargés.           *
*                                                                             *
*  Retour      : true si le parcours a été total, false sinon.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool _browse_all_item_panels(bool skip, handle_panel_item_fc handle, void *data)
{
    bool result;                            /* Résultat à renvoyer         */
    GType type;                             /* Type de panneau à traiter   */
    size_t i;                               /* Boucle de parcours          */
    GPanelItemClass *class;                 /* Classe associée au type     */

    result = true;

    for (i = 0; i < _panels_count; i++)
    {
        type = _panels_list[i];

        if (skip && type == G_TYPE_WELCOME_PANEL)
            continue;

        class = g_type_class_ref(type);

        result = handle(class, data);

        g_type_class_unref(class);

        if (!result) break;

    }

    return result;

}
