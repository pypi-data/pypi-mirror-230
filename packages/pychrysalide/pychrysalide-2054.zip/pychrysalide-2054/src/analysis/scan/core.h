
/* Chrysalide - Outil d'analyse de fichiers binaires
 * core.h - prototypes pour l'enregistrement des fonctions principales
 *
 * Copyright (C) 2022 Cyrille Bagard
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _ANALYSIS_SCAN_CORE_H
#define _ANALYSIS_SCAN_CORE_H


#include "space.h"
#include "patterns/modifier.h"



/* Inscrit un modificateur dans la liste des disponibles. */
bool register_scan_token_modifier(GScanTokenModifier *);

/* Charge tous les modificateurs de base. */
bool load_all_known_scan_token_modifiers(void);

/* Décharge tous les modificateurs inscrits. */
void unload_all_scan_token_modifiers(void);

/* Fournit le modificateur correspondant à un nom. */
GScanTokenModifier *find_scan_token_modifiers_for_name(const char *);

/* Inscrit les principales fonctions dans l'espace racine. */
bool populate_main_scan_namespace(GScanNamespace *);



#endif  /* _ANALYSIS_SCAN_CORE_H */
