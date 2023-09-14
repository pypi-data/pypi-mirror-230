
/* Chrysalide - Outil d'analyse de fichiers binaires
 * hex-int.h - prototypes internes pour la recherche de morceaux de binaire
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _ANALYSIS_SCAN_PATTERNS_TOKENS_HEX_INT_H
#define _ANALYSIS_SCAN_PATTERNS_TOKENS_HEX_INT_H


#include "hex.h"


#include "atom.h"
#include "../token-int.h"



/* Encadrement d'une recherche de morceaux de binaire (instance) */
struct _GScanHexBytes
{
    GStringToken parent;                    /* A laisser en premier        */

};

/* Encadrement d'une recherche de morceaux de binaire (classe) */
struct _GScanHexBytesClass
{
    GStringTokenClass parent;               /* A laisser en premier        */

};


/* Met en place un gestionnaire de recherche de binaire. */
bool g_scan_hex_bytes_create(GScanHexBytes *, GScanTokenNode *, bool);



#endif  /* _ANALYSIS_SCAN_PATTERNS_TOKENS_HEX_INT_H */
