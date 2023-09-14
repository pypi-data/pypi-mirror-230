
/* Chrysalide - Outil d'analyse de fichiers binaires
 * demanglers.h - prototypes pour l'enregistrement et la fourniture des décodeurs proprosés
 *
 * Copyright (C) 2018-2020 Cyrille Bagard
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


#ifndef _CORE_DEMANGLERS_H
#define _CORE_DEMANGLERS_H


#include <stdbool.h>


#include "../mangling/demangler.h"



/* Enregistre un décodeur répondant à une appellation donnée. */
bool register_demangler_type(GType);

/* Décharge toutes les définitions de décodeurs. */
void unload_demanglers_definitions(void);

/* Fournit le décodeur de désignations correspondant à un type. */
GCompDemangler *get_compiler_demangler_for_key(const char *);



#endif  /* _CORE_DEMANGLERS_H */
