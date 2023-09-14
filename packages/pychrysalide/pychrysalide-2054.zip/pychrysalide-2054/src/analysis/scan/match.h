
/* Chrysalide - Outil d'analyse de fichiers binaires
 * match.h - prototypes pour la sauvegarde d'une correspondance identifiée de motif
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


#ifndef _ANALYSIS_SCAN_MATCH_H
#define _ANALYSIS_SCAN_MATCH_H


#include <glib-object.h>


#include "pattern.h"
#include "../../common/szstr.h"



#define G_TYPE_SCAN_MATCH            g_scan_match_get_type()
#define G_SCAN_MATCH(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_MATCH, GScanMatch))
#define G_IS_SCAN_MATCH(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_MATCH))
#define G_SCAN_MATCH_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_MATCH, GScanMatchClass))
#define G_IS_SCAN_MATCH_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_MATCH))
#define G_SCAN_MATCH_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_MATCH, GScanMatchClass))


/* Correspondance trouvée avec un motif (instance) */
typedef struct _GScanMatch GScanMatch;

/* Correspondance trouvée avec un motif (classe) */
typedef struct _GScanMatchClass GScanMatchClass;


/* Indique le type défini pour un correspondance de motif identifiée. */
GType g_scan_match_get_type(void);

/* Indique la source du motif d'origine recherché. */
GSearchPattern *g_scan_match_get_source(const GScanMatch *);

/* Affiche une correspondance au format texte. */
void g_scan_match_output_to_text(const GScanMatch *, int);

/* Convertit une correspondance en texte. */
void g_scan_match_convert_as_text(const GScanMatch *);

/* Affiche une correspondance au format JSON. */
void g_scan_match_output_to_json(const GScanMatch *, const sized_string_t *, unsigned int, int, bool);

/* Convertit une correspondance en JSON. */
void g_scan_match_convert_as_json(const GScanMatch *);



#endif  /* _ANALYSIS_SCAN_MATCH_H */
