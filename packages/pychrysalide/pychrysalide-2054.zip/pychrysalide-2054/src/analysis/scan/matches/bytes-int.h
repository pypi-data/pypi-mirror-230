
/* Chrysalide - Outil d'analyse de fichiers binaires
 * bytes-int.h - prototypes internes pour la sauvegarde d'une correspondance identifiée de suite d'octets
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


#ifndef _ANALYSIS_SCAN_MATCHES_BYTES_INT_H
#define _ANALYSIS_SCAN_MATCHES_BYTES_INT_H


#include "bytes.h"


#include "../match-int.h"



/* Correspondance trouvée avec une chaîne (instance) */
struct _GScanBytesMatch
{
    GScanMatch parent;                      /* A laisser en premier        */

    GBinContent *content;                   /* Contenu binaire de référence*/

    phys_t start;                           /* Début du motif représenté   */
    phys_t len;                             /* Taille du motif représenté  */

};

/* Correspondance trouvée avec une chaîne (classe) */
struct _GScanBytesMatchClass
{
    GScanMatchClass parent;                 /* A laisser en premier        */

};


/* Met en place une correspondance trouvée avec un motif. */
bool g_scan_bytes_match_create(GScanBytesMatch *, GSearchPattern *, GBinContent *, phys_t, phys_t);



#endif  /* _ANALYSIS_SCAN_MATCHES_BYTES_INT_H */
