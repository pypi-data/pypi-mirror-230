
/* Chrysalide - Outil d'analyse de fichiers binaires
 * core.h - prototypes pour le chargement et le déchargement du tronc commun pour l'éditeur graphique
 *
 * Copyright (C) 2016-2018 Cyrille Bagard
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


#ifndef _GUI_CORE_CORE_H
#define _GUI_CORE_CORE_H


#include <glib-object.h>
#include <stdbool.h>


#include "../../glibext/configuration.h"



/* Charge les éléments graphiques de l'éditeur. */
bool load_all_gui_components(void);

/* Finalise le chargement des éléments graphiques de l'éditeur. */
bool complete_loading_of_all_gui_components(GGenConfig *);

/* Décharge les éléments graphiques de l'éditeur. */
void unload_all_gui_components(void);



#endif  /* _GUI_CORE_CORE_H */
