
/* Chrysalide - Outil d'analyse de fichiers binaires
 * plain-int.h - prototypes internes pour la recherche d'une chaîne de caractères brute
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


#ifndef _ANALYSIS_SCAN_PATTERNS_TOKENS_PLAIN_INT_H
#define _ANALYSIS_SCAN_PATTERNS_TOKENS_PLAIN_INT_H


#include "plain.h"


#include "atom.h"
#include "../token-int.h"



/* Encadrement d'une recherche de texte brut (instance) */
struct _GScanPlainBytes
{
    GStringToken parent;                    /* A laisser en premier        */

};

/* Encadrement d'une recherche de texte brut (classe) */
struct _GScanPlainBytesClass
{
    GStringTokenClass parent;               /* A laisser en premier        */

};


/* Met en place un gestionnaire de recherche de texte brut. */
bool g_scan_plain_bytes_create(GScanPlainBytes *, GScanTokenNode *);



#endif  /* _ANALYSIS_SCAN_PATTERNS_TOKENS_PLAIN_INT_H */
