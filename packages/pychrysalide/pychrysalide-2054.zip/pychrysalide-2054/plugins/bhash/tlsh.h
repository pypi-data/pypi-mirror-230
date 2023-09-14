
/* Chrysalide - Outil d'analyse de fichiers binaires
 * tlsh.h - prototypes pour les calculs d'empreintes selon l'algorithme TLSH
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


#ifndef _PLUGINS_BHASH_TLSH_H
#define _PLUGINS_BHASH_TLSH_H


#include <stdbool.h>


#include <analysis/content.h>



/* Calcule l'empreinte TLSH d'un contenu binaire. */
char *compute_content_tlsh_hash(const GBinContent *, bool);

/* Indique si une chaîne représente à priori une empreinte TLSH. */
bool is_valid_tlsh_hash(const char *);

/* Détermine la similarité entre deux empreintes TLSH. */
bool compare_tlsh_hash(const char *, const char *, bool, int32_t *);



#endif  /* _PLUGINS_BHASH_TLSH_H */
