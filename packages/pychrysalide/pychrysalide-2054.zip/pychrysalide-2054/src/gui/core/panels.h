
/* Chrysalide - Outil d'analyse de fichiers binaires
 * panels.h - prototypes pour la gestion d'ensemble de tous les panneaux pour l'éditeur
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


#ifndef _GUI_CORE_PANELS_H
#define _GUI_CORE_PANELS_H


#include <stdbool.h>


#include "../panel.h"
#include "../../glibext/configuration.h"



/* Charge les principaux panneaux de l'éditeur. */
void load_main_panels(void);

/* Enregistre un panneau comme partie intégrante de l'éditeur. */
void register_panel_item(GType, GGenConfig *);

/* Réalise un traitement sur un panneau de l'éditeur. */
typedef bool (* handle_panel_item_fc) (GPanelItemClass *, void *);

/* Effectue le parcours de tous les panneaux chargés. */
bool _browse_all_item_panels(bool, handle_panel_item_fc, void *);

#define browse_all_item_panels(h, d) \
    _browse_all_item_panels(false, h, d)



#endif  /* _GUI_CORE_PANELS_H */
