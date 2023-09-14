
/* Chrysalide - Outil d'analyse de fichiers binaires
 * imphash.h - prototypes pour les calculs d'empreintes sur la base des importations
 *
 * Copyright (C) 2020 Cyrille Bagard
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


#ifndef _PLUGINS_BHASH_IMPHASH_H
#define _PLUGINS_BHASH_IMPHASH_H


#include <stdbool.h>


#include <plugins/pe/format.h>



/* Calcule l'empreinte des importations d'un format PE. */
char *compute_pe_import_hash(const GPeFormat *, bool);



#endif  /* _PLUGINS_BHASH_IMPHASH_H */
