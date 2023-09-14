
/* Chrysalide - Outil d'analyse de fichiers binaires
 * fetch.h - prototypes pour la récupération d'instructions à partir de binaire brut
 *
 * Copyright (C) 2010-2018 Cyrille Bagard
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


#ifndef _ANALYSIS_DISASS_FETCH_H
#define _ANALYSIS_DISASS_FETCH_H


#include "../binary.h"
#include "../../glibext/delayed.h"
#include "../../glibext/notifier.h"



/* Procède au désassemblage basique d'un contenu binaire. */
GArchInstruction **disassemble_binary_content(GLoadedBinary *, GProcContext *, wgroup_id_t, GtkStatusStack *, size_t *);



#endif  /* _ANALYSIS_DISASS_FETCH_H */
