
/* Chrysalide - Outil d'analyse de fichiers binaires
 * build.h - prototypes pour la collecte des informations à enregistrer
 *
 * Copyright (C) 2009-2018 Cyrille Bagard
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


#ifndef _PLUGINS_GOVM_BUILD_H
#define _PLUGINS_GOVM_BUILD_H


#include <stdbool.h>


#include "instruction.h"



/* -------------------------- PROCEDURES POUR L'ASSEMBLAGE -------------------------- */


/* Regroupement des informations à enregistrer */
typedef struct _govm_info govm_info;


/* Met en place une future collecte d'informations. */
govm_info *create_govm_info(bool, bool);

/* Supprime de la mémoire toutes les informations collectées. */
void delete_govm_info(govm_info *);

/* Ajoute une instruction aux informations à enregistrer. */
bool encode_govm_instruction(govm_info *, GoVMOpcodes);

/* Ajoute une valeur entière dans le code même. */
bool encode_govm_number(govm_info *, uint16_t);

/* Enregistre un nouvel emplacement d'étiquette. */
bool register_govm_label(govm_info *, const char *);

/* Exécute un détournement de flot via une étiquette. */
bool encode_reference_to_govm_label(govm_info *, GoVMOpcodes, const char *);

/* Procède à l'enregistrement d'un shellcode pour GoVM. */
bool write_govm_info(govm_info *, int);



#endif  /* _PLUGINS_GOVM_BUILD_H */
