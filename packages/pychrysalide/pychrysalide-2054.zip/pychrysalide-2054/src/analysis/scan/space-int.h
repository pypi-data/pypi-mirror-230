
/* Chrysalide - Outil d'analyse de fichiers binaires
 * space-int.h - prototypes internes pour la définition d'un espace de noms pour les fonctions de scan
 *
 * Copyright (C) 2022 Cyrille Bagard
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


#ifndef _ANALYSIS_SCAN_SPACE_INT_H
#define _ANALYSIS_SCAN_SPACE_INT_H


#include "space.h"


#include "item-int.h"



/* Espace de noms pour un groupe de fonctions (instance) */
struct _GScanNamespace
{
    GRegisteredItem parent;                 /* A laisser en premier        */

    char *name;                             /* Désignation de l'espace     */

    GRegisteredItem **children;             /* Sous-éléments inscrits      */
    char **names;                           /* Désignations correspondantes*/
    size_t count;                           /* Quantité de sous-éléments   */

};

/* Espace de noms pour un groupe de fonctions (classe) */
struct _GScanNamespaceClass
{
    GRegisteredItemClass parent;            /* A laisser en premier        */

};


/* Met en place un nouvel espace de noms pour scan. */
bool g_scan_namespace_create(GScanNamespace *, const char *);



#endif  /* _ANALYSIS_SCAN_SPACE_INT_H */
