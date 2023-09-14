
/* Chrysalide - Outil d'analyse de fichiers binaires
 * ordinals.h - prototypes pour l'accès à l'ensemble des ordinaux enregistrés
 *
 * Copyright (C) 2021 Cyrille Bagard
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


#ifndef _PLUGINS_WINORDINALS_ORDINALS_H
#define _PLUGINS_WINORDINALS_ORDINALS_H


#include <stdint.h>



/* Indique la liste de bibliothèques enregistrées avec ordinaux. */
const char **list_register_dlls_for_ordinals(void);

/* Indique la liste de bibliothèques enregistrées avec ordinaux. */
const char *get_symbol_by_ordinal(const char *, uint16_t);



#endif  /* _PLUGINS_WINORDINALS_ORDINALS_H */
