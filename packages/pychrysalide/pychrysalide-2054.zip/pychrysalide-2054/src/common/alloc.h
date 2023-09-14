
/* Chrysalide - Outil d'analyse de fichiers binaires
 * alloc.h - prototypes pour une gestion particulière des allocations
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


#ifndef _COMMON_ALLOC_H
#define _COMMON_ALLOC_H


#include <sys/types.h>



/* Assure qu'une zone de mémoire allouée a la taille requise. */
void *ensure_allocation_size(void *, size_t *, size_t);



#endif  /* _COMMON_ALLOC_H */
