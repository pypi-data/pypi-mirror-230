
/* Chrysalide - Outil d'analyse de fichiers binaires
 * manager.h - prototypes pour l'enregistrement d'une description complète
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


#ifndef _TOOLS_D2C_DESC_MANAGER_H
#define _TOOLS_D2C_DESC_MANAGER_H



/* Mémorisation de la description d'un identifiant */
typedef struct _instr_desc instr_desc;


/* Crée un nouveau gestionnaire de définitions d'identifiant. */
instr_desc *create_instruction_description(void);

/* Supprime de la mémoire un gestionnaire de description. */
void delete_instruction_description(instr_desc *);

/* Définit le contenu textuel d'une description. */
void set_instruction_description(instr_desc *, const char *);

/* Imprime la description associée à une instruction. */
void write_instruction_description(const instr_desc *, int);



#endif  /* _TOOLS_D2C_DESC_MANAGER_H  */
