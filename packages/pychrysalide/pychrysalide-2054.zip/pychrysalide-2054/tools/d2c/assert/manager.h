
/* Chrysalide - Outil d'analyse de fichiers binaires
 * manager.h - prototypes pour le désassemblage sous condition
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


#ifndef _TOOLS_D2C_ASSERT_MANAGER_H
#define _TOOLS_D2C_ASSERT_MANAGER_H


#include <stdbool.h>


#include "../bits/manager.h"



/* Définition d'opération conditionnelle */

typedef enum _DisassCondOp
{
    DCO_EQ,                                 /* Egalité                     */
    DCO_NE                                  /* Différence                  */

} DisassCondOp;

typedef enum _DisassCondGroup
{
    DCG_UNIQ,                               /* Condition unique            */
    DCG_AND,                                /* Obligation                  */
    DCG_OR                                  /* Complémentarité             */

} DisassCondGroup;


/* Représentation de l'ensemble de conditions préalables */
typedef struct _disass_assert disass_assert;


/* Crée un nouveau gestionnaire de conditions de désassemblage. */
disass_assert *create_disass_assert(void);

/* Supprime de la mémoire un gestionnaire de conditions. */
void delete_disass_assert(disass_assert *);

/* Initie une nouvelle condition à vérifier. */
void register_disass_assert(disass_assert *, DisassCondGroup, char *, DisassCondOp, char *);

/* Enregistre une nouvelle condition à vérifier. */
void extend_disass_assert(disass_assert *, char *, DisassCondOp, char *);

/* Indique la présence de conditions à vérifier. */
bool is_disass_assert_empty(const disass_assert *);

/* Marque les éléments de condition effectivement utilisés. */
bool mark_disass_assert(const disass_assert *, const coding_bits *);

/* Définit les éléments de condition à appliquer. */
bool define_disass_assert(const disass_assert *, int, const coding_bits *);



#endif  /* _TOOLS_D2C_ASSERT_MANAGER_H */
