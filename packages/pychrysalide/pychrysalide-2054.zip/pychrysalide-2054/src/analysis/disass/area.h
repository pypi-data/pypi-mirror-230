
/* Chrysalide - Outil d'analyse de fichiers binaires
 * area.h - prototypes pour la définition et la manipulation des aires à désassembler
 *
 * Copyright (C) 2014-2018 Cyrille Bagard
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


#ifndef _ANALYSIS_DISASS_AREA_H
#define _ANALYSIS_DISASS_AREA_H


#include "../binary.h"
#include "../../arch/instruction.h"
#include "../../format/preload.h"
#include "../../format/symbol.h"
#include "../../glibext/delayed.h"
#include "../../glibext/notifier.h"



/* ------------------------- TRAITEMENT DES ZONES DE DONNES ------------------------- */


/* Zone mémoire bien bornée */
typedef struct _mem_area mem_area;


/* Procède au désassemblage d'un contenu binaire exécutable. */
void load_code_from_mem_area(mem_area *, mem_area *, size_t, GProcContext *, const vmpa2t *, bool, GtkStatusStack *, activity_id_t);



/* -------------------------- TRAITEMENT DE ZONES PAR LOTS -------------------------- */


/* Détermine une liste de zones contigües à traiter. */
mem_area *find_memory_area_by_addr(mem_area *, size_t, const vmpa2t *);



/* ----------------------- MANIPULATIONS PARALLELES DES ZONES ----------------------- */


/* Détermine une liste de zones contigües à traiter. */
mem_area *collect_memory_areas(wgroup_id_t, GtkStatusStack *, GLoadedBinary *, phys_t, size_t *);

/* Intègre toutes les instructions préchargées dans des zones. */
void populate_fresh_memory_areas(wgroup_id_t, GtkStatusStack *, mem_area *, size_t, GPreloadInfo *);

/* Remplit les espaces vacants des zones à désassembler. */
void ensure_all_mem_areas_are_filled(wgroup_id_t, GtkStatusStack *, activity_id_t, mem_area *, size_t, GProcContext *);

/* Rassemble les instructions conservées dans des zones données. */
GArchInstruction **collect_disassembled_instructions(wgroup_id_t, GtkStatusStack *, mem_area *, size_t, size_t *);



#endif  /* _ANALYSIS_DISASS_AREA_H */
