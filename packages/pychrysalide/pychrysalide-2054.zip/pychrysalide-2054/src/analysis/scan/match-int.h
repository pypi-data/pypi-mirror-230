
/* Chrysalide - Outil d'analyse de fichiers binaires
 * match-int.h - prototypes internes pour la sauvegarde d'une correspondance identifiée de motif
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


#ifndef _ANALYSIS_SCAN_MATCH_INT_H
#define _ANALYSIS_SCAN_MATCH_INT_H


#include "match.h"



/* Affiche une correspondance au format texte. */
typedef void (* output_scan_match_to_text_fc) (const GScanMatch *, int);

/* Affiche une correspondance au format JSON. */
typedef void (* output_scan_match_to_json_fc) (const GScanMatch *, const sized_string_t *, unsigned int, int);


/* Correspondance trouvée avec un motif (instance) */
struct _GScanMatch
{
    GObject parent;                         /* A laisser en premier        */

    GSearchPattern *source;                 /* Motif d'origine recherché   */

};

/* Correspondance trouvée avec un motif (classe) */
struct _GScanMatchClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    output_scan_match_to_text_fc to_text;   /* Impression au format texte  */
    output_scan_match_to_json_fc to_json;    /* Impression au format JSON   */

};



#endif  /* _ANALYSIS_SCAN_MATCH_INT_H */
