
/* Chrysalide - Outil d'analyse de fichiers binaires
 * pattern-int.h - prototypes internes pour la définition de motif à rechercher
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


#ifndef _ANALYSIS_SCAN_PATTERN_INT_H
#define _ANALYSIS_SCAN_PATTERN_INT_H


#include "pattern.h"


#include "context.h"



/* Affiche un motif de recherche au format texte. */
typedef void (* output_pattern_to_text_fc) (const GSearchPattern *, GScanContext *, int);

/* Affiche un motif de recherche au format JSON. */
typedef void (* output_pattern_to_json_fc) (const GSearchPattern *, GScanContext *, const sized_string_t *, unsigned int, int);


/* Motif à rechercher au sein d'un contenu (instance) */
struct _GSearchPattern
{
    GObject parent;                         /* A laisser en premier        */

    char *name;                             /* Eventuelle désignation      */

};

/* Motif à rechercher au sein d'un contenu (classe) */
struct _GSearchPatternClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    output_pattern_to_text_fc to_text;      /* Impression au format texte  */
    output_pattern_to_json_fc to_json;      /* Impression au format JSON   */

};



#endif  /* _ANALYSIS_SCAN_PATTERN_INT_H */
