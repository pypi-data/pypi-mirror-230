
/* Chrysalide - Outil d'analyse de fichiers binaires
 * token-int.h - prototypes internes pour les bribes de recherche textuelle
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


#ifndef _ANALYSIS_SCAN_PATTERNS_TOKEN_INT_H
#define _ANALYSIS_SCAN_PATTERNS_TOKEN_INT_H


#include "token.h"


#include "../pattern-int.h"



/* Encadrement d'une bribe de recherche textuelle (instance) */
struct _GStringToken
{
    GSearchPattern parent;                  /* A laisser en premier        */

    GScanTokenNode *root;                   /* Motif à rechercher          */
    size_t slow;                            /* Surcoût du motif            */
    bool need_backward;                     /* Besoin d'une seconde passe  */

    bool fullword;                          /* Cible de mots entiers ?     */
    bool private;                           /* Vocation privée ?           */

};

/* Encadrement d'une bribe de recherche textuelle (classe) */
struct _GStringTokenClass
{
    GSearchPatternClass parent;             /* A laisser en premier        */

};


/* Met en place un gestionnaire de recherche de binaire. */
bool g_string_token_create(GStringToken *, GScanTokenNode *, bool, bool);



#endif  /* _ANALYSIS_SCAN_PATTERNS_TOKEN_INT_H */
