
/* Chrysalide - Outil d'analyse de fichiers binaires
 * itoa.h - prototypes pour la conversion d'un nombre en chaîne de caractères
 *
 * Copyright (C) 2023 Cyrille Bagard
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


#ifndef _COMMON_ITOA_H
#define _COMMON_ITOA_H



/* Convertit une valeur en une forme textuelle. */
char *itoa(long long, unsigned char);



#endif  /* _COMMON_ITOA_H */
