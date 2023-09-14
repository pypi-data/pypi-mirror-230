
/* Chrysalide - Outil d'analyse de fichiers binaires
 * any-int.h - prototypes internes pour une suite d'octets quelconques
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


#ifndef _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_ANY_INT_H
#define _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_ANY_INT_H


#include "any.h"


#include "../atom.h"
#include "../node-int.h"



/* Espace constitué d'un ou plusieurs octets quelconques (instance) */
struct _GScanTokenNodeAny
{
    GScanTokenNode parent;                  /* A laisser en premier        */

    phys_t min;                             /* Quantité minimale           */
    phys_t max;                             /* Quantité maximale           */
    bool has_max;                           /* Quantité définie ?          */

};

/* Espace constitué d'un ou plusieurs octets quelconques (classe) */
struct _GScanTokenNodeAnyClass
{
    GScanTokenNodeClass parent;             /* A laisser en premier        */

};


/* Met en place un un noeud pointant une série d'octets. */
bool g_scan_token_node_any_create(GScanTokenNodeAny *, const phys_t *, const phys_t *);



#endif  /* _ANALYSIS_SCAN_PATTERNS_TOKENS_NODES_ANY_INT_H */
