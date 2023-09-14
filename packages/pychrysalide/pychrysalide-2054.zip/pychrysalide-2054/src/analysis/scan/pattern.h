
/* Chrysalide - Outil d'analyse de fichiers binaires
 * pattern.h - prototypes pour la définition de motif à localiser dans du contenu binaire
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


#ifndef _ANALYSIS_SCAN_PATTERN_H
#define _ANALYSIS_SCAN_PATTERN_H


#include <glib-object.h>


#include "../../arch/archbase.h"
#include "../../arch/vmpa.h"
#include "../../common/szstr.h"



/* Depuis context.h: contexte de suivi d'une analyse en cours (instance) */
typedef struct _GScanContext GScanContext;
;

#define G_TYPE_SEARCH_PATTERN            g_search_pattern_get_type()
#define G_SEARCH_PATTERN(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SEARCH_PATTERN, GSearchPattern))
#define G_IS_SEARCH_PATTERN(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SEARCH_PATTERN))
#define G_SEARCH_PATTERN_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SEARCH_PATTERN, GSearchPatternClass))
#define G_IS_SEARCH_PATTERN_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SEARCH_PATTERN))
#define G_SEARCH_PATTERN_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SEARCH_PATTERN, GSearchPatternClass))


/* Motif à rechercher au sein d'un contenu (instance) */
typedef struct _GSearchPattern GSearchPattern;

/* Motif à rechercher au sein d'un contenu (classe) */
typedef struct _GSearchPatternClass GSearchPatternClass;


/* Indique le type défini pour un motif à localiser. */
GType g_search_pattern_get_type(void);

/* Fournit la désignation attribuée à un motif de recherche. */
const char *g_search_pattern_get_name(const GSearchPattern *);

/* Inscrit la désignation attribuée à un motif de recherche. */
void g_search_pattern_set_name(GSearchPattern *, const char *, size_t);

/* Affiche un motif de recherche au format texte. */
void g_search_pattern_output_to_text(const GSearchPattern *, GScanContext *, int);

/* Convertit un motif de recherche en texte. */
char *g_search_pattern_convert_as_text(const GSearchPattern *, GScanContext *);

/* Affiche un motif de recherche au format JSON. */
void g_search_pattern_output_to_json(const GSearchPattern *, GScanContext *, const sized_string_t *, unsigned int, int, bool);

/* Convertit un motif de recherche en JSON. */
char *g_search_pattern_convert_as_json(const GSearchPattern *, GScanContext *);



#endif  /* _ANALYSIS_SCAN_PATTERN_H */
