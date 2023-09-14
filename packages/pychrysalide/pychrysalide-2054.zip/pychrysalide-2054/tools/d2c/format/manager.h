
/* Chrysalide - Outil d'analyse de fichiers binaires
 * manager.h - prototypes pour l'enregistrement de la définition des opérandes attendus
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


#ifndef _TOOLS_D2C_FORMAT_MANAGER_H
#define _TOOLS_D2C_FORMAT_MANAGER_H


#include <stdbool.h>



/* Mémorisation de la définition d'opérandes */
typedef struct _operands_format operands_format;


/* Crée un nouveau gestionnaire de définitions d'opérandes. */
operands_format *create_operands_format(void);

/* Supprime de la mémoire un gestionnaire de définitions. */
void delete_operands_format(operands_format *);

/* Précise le type d'opérandes dont la définition est à charger. */
void add_operands_format_type(operands_format *, char *);

/* Définit le chargement des opérandes prévus par la définition. */
bool define_operands_loading(const operands_format *, int, const char *, const char *, bool *);



#endif  /* _TOOLS_D2C_FORMAT_MANAGER_H */
