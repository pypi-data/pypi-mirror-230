
/* Chrysalide - Outil d'analyse de fichiers binaires
 * helpers.h - prototypes pour les fonctionnalités d'assitance à la compilation
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


#ifndef _TOOLS_D2C_HELPERS_H
#define _TOOLS_D2C_HELPERS_H


#include <ctype.h>
#include <stdbool.h>



/* ---------------------------- MANIPULATIONS DE CHAINES ---------------------------- */


/* Bascule toute une chaîne de caractères en (min|maj)uscules. */
char *_make_string_xxx(char *, int (* fn) (int));

#define make_string_lower(str) _make_string_xxx(str, tolower)
#define make_string_upper(str) _make_string_xxx(str, toupper)

/* Traduit une chaîne en élément de fonction C. */
char *make_callable(const char *raw, bool);



#endif  /* _TOOLS_D2C_HELPERS_H */
