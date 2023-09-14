
/* Chrysalide - Outil d'analyse de fichiers binaires
 * collect.h - prototypes pour la collecte de différents registres en remontant le flot d'exécution
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


#ifndef _PLUGINS_LNXSYSCALLS_COLLECT_H
#define _PLUGINS_LNXSYSCALLS_COLLECT_H


#include <arch/instriter.h>
#include <arch/register.h>



/* Depuis hops.h : opérations adaptées pour une chasse donnée */
typedef struct _hunting_ops hunting_ops;

/* Collection de registres */
typedef struct _tracked_path tracked_path;


/* Crée une structure de suivi de registres vide. */
tracked_path *create_register_tracker(instr_iter_t *);

/* Crée une structure de suivi de registres initialisée. */
tracked_path *create_register_tracker_from(const tracked_path *, size_t);

/* Efface une structure de suivi de registres. */
void delete_register_tracker(tracked_path *);

/* Dénombre les piles d'exécutions différentes conservées. */
size_t count_register_tracker_stacks(const tracked_path *);

/* Note le besoin ou l'usage d'un registre donné. */
void mark_register_in_tracker(tracked_path *, size_t, GArchRegister *, GArchInstruction *);

/* Se lance à la recherche de la définition de registres. */
bool look_for_registers(tracked_path *, size_t, GArchProcessor *, const hunting_ops *);

/* Retrouve la dernière modification d'un registre donné. */
GArchInstruction *get_register_write_location(const tracked_path *, size_t, const GArchRegister *);



#endif  /* _PLUGINS_LNXSYSCALLS_COLLECT_H */
