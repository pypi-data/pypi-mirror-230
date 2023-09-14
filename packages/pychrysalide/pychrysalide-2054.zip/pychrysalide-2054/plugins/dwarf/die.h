
/* Chrysalide - Outil d'analyse de fichiers binaires
 * die.h - prototypes pour la gestion des entrées renvoyant à des informations de débogage
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#ifndef _PLUGINS_DWARF_DIE_H
#define _PLUGINS_DWARF_DIE_H


#include <stdbool.h>


#include <analysis/content.h>


#include "abbrev.h"
#include "def.h"
#include "format.h"



/* § 2.1 The Debugging Information Entry (DIE). */
typedef struct _dw_die dw_die;


/* Procède à la lecture d'un élément d'information de débogage. */
bool build_dwarf_die(GDwarfFormat *, GBinContent *, vmpa2t *, const dw_compil_unit_header *, const dw_abbrev_brotherhood *, dw_die **);

/* Supprime les éléments mis en place pour une entrée d'info. */
void delete_dwarf_die(dw_die *);



#endif  /* _PLUGINS_DWARF_DIE_H */
