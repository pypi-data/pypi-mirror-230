
/* Chrysalide - Outil d'analyse de fichiers binaires
 * manager.h - prototypes pour la prise en compte d'une hookse du langage d'assemblage
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


#ifndef _TOOLS_D2C_HOOKS_MANAGER_H
#define _TOOLS_D2C_HOOKS_MANAGER_H


#include <stdbool.h>



/* Liste des fonctions de renvoi pour une instruction */
typedef struct _instr_hooks instr_hooks;



/* Crée une liste de fonctions à lier à une instruction. */
instr_hooks *create_instr_hooks(void);

/* Supprime de la mémoire une liste de fonctions liées. */
void delete_instr_hooks(instr_hooks *);

/* Enregistre l'utilité d'une fonction pour une instruction. */
void register_hook_function(instr_hooks *, char *, char *);

/* Indique si des décrochages sont définis. */
bool has_hook_functions(const instr_hooks *);

/* Imprime une liste de décrochages spécifiés. */
bool write_hook_functions(const instr_hooks *, int);



#endif  /* _TOOLS_D2C_HOOKS_MANAGER_H */
