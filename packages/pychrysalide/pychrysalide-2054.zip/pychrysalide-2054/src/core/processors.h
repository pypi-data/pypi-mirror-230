
/* Chrysalide - Outil d'analyse de fichiers binaires
 * processors.h - prototypes pour l'enregistrement et la fourniture des architectures supportées
 *
 * Copyright (C) 2015-2019 Cyrille Bagard
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


#ifndef _CORE_PROCESSORS_H
#define _CORE_PROCESSORS_H


#include <glib-object.h>
#include <stdbool.h>


#include "../arch/processor.h"
#include "../glibext/singleton.h"



/* Assure l'enregistrement de types pour les caches à charger. */
void register_arch_gtypes(void);

/* Met en place le fournisseur d'instances uniques d'opérandes. */
void init_operands_factory(void);

/* Fournit l'usine à opérandes pour toutes les instructions. */
GSingletonFactory *get_operands_factory(void);

/* Supprime le fournisseur d'instances uniques d'opérandes. */
void exit_operands_factory(void);

/* Enregistre un processeur pour une architecture donnée. */
bool register_processor_type(GType);

/* Décharge toutes les définitions de processeurs. */
void unload_processors_definitions(void);

/* Fournit la liste des processeurs d'architecture disponibles. */
char **get_all_processor_keys(size_t *);

/* Fournit le processeur d'architecture correspondant à un nom. */
GArchProcessor *get_arch_processor_for_key(const char *);



#endif  /* _CORE_PROCESSORS_H */
