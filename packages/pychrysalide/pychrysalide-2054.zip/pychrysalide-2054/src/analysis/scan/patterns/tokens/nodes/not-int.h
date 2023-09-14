
/* Chrysalide - Outil d'analyse de fichiers binaires
 * not-int.h - prototypes internes pour l'inversion de résultats de correspondances établis
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


#ifndef _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_NOT_INT_H
#define _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_NOT_INT_H


#include "not.h"


#include "../node-int.h"



/* Inversion de résultats de correspondances établis (instance) */
struct _GScanTokenNodeNot
{
    GScanTokenNode parent;                  /* A laisser en premier        */

    GScanTokenNode *child;                  /* Sous-noeud à considérer     */

};

/* Inversion de résultats de correspondances établis (classe) */
struct _GScanTokenNodeNotClass
{
    GScanTokenNodeClass parent;             /* A laisser en premier        */

};


/* Met en place une inversion de résultats de correspondances. */
bool g_scan_token_node_not_create(GScanTokenNodeNot *, GScanTokenNode *);



#endif  /* _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_NOT_INT_H */
