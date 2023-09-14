
/* Chrysalide - Outil d'analyse de fichiers binaires
 * setcounter.h - prototypes pour le décompte global de correspondances locales
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


#ifndef _ANALYSIS_SCAN_EXPRS_SETCOUNTER_H
#define _ANALYSIS_SCAN_EXPRS_SETCOUNTER_H


#include <glib-object.h>


#include "../expr.h"
#include "../pattern.h"



#define G_TYPE_SCAN_SET_MATCH_COUNTER            g_scan_set_match_counter_get_type()
#define G_SCAN_SET_MATCH_COUNTER(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_SET_MATCH_COUNTER, GScanSetMatchCounter))
#define G_IS_SCAN_SET_MATCH_COUNTER(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_SET_MATCH_COUNTER))
#define G_SCAN_SET_MATCH_COUNTER_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_SET_MATCH_COUNTER, GScanSetMatchCounterClass))
#define G_IS_SCAN_SET_MATCH_COUNTER_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_SET_MATCH_COUNTER))
#define G_SCAN_SET_MATCH_COUNTER_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_SET_MATCH_COUNTER, GScanSetMatchCounterClass))


/* Décompte global de correspondances locales (instance) */
typedef struct _GScanSetMatchCounter GScanSetMatchCounter;

/* Décompte global de correspondances locales (classe) */
typedef struct _GScanSetMatchCounterClass GScanSetMatchCounterClass;


/* Indique le type défini pour un décompte de résultats lors d'une recherche de motifs. */
GType g_scan_set_match_counter_get_type(void);

/* Met en place un décompte de correspondances obtenues. */
GScanExpression *g_scan_set_match_counter_new(GSearchPattern ** const, size_t);

/* Ajoute de nouveaux motifs à un ensemble à décompter. */
void g_scan_set_match_counter_add_extra_patterns(GScanSetMatchCounter *, GSearchPattern ** const, size_t);

/* Formes de volume de correspondances */
typedef enum _ScanSetCounterType
{
    SSCT_NONE,                              /* Aucun motif avec résultats  */
    SSCT_ANY,                               /* Au moins un motif trouvé    */
    SSCT_ALL,                               /* Tous les motifs présents    */
    SSCT_NUMBER,                            /* Au moins n motifs avec rés. */

} ScanSetCounterType;

/* Précise le volume de motifs avec correspondances à retrouver. */
bool g_scan_set_match_counter_define_expected_matches(GScanSetMatchCounter *, ScanSetCounterType, size_t *);



#endif  /* _ANALYSIS_SCAN_EXPRS_SETCOUNTER_H */
