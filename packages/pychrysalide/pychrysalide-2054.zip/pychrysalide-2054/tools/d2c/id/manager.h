
/* Chrysalide - Outil d'analyse de fichiers binaires
 * manager.h - prototypes pour l'enregistrement de la définition d'un identifiant
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


#ifndef _TOOLS_D2C_ID_MANAGER_H
#define _TOOLS_D2C_ID_MANAGER_H



/* Mémorisation de la définition d'un identifiant */
typedef struct _instr_id instr_id;


/* Crée un nouveau gestionnaire de définitions d'identifiant. */
instr_id *create_instruction_id(void);

/* Supprime de la mémoire un gestionnaire d'identifiant. */
void delete_instruction_id(instr_id *);

/* Associe une valeur unique à une instruction. */
void set_instruction_id_value(instr_id *, unsigned int);

/* Associe une valeur unique à une instruction. */
unsigned int get_instruction_id_value(const instr_id *);



#endif  /* _TOOLS_D2C_ID_MANAGER_H */
