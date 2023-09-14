
/* Chrysalide - Outil d'analyse de fichiers binaires
 * counter.h - prototypes pour le décompte de correspondances identifiées dans du contenu binaire
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


#ifndef _ANALYSIS_SCAN_EXPRS_COUNTER_H
#define _ANALYSIS_SCAN_EXPRS_COUNTER_H


#include <glib-object.h>


#include "../expr.h"
#include "../pattern.h"



#define G_TYPE_SCAN_MATCH_COUNTER            g_scan_match_counter_get_type()
#define G_SCAN_MATCH_COUNTER(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_MATCH_COUNTER, GScanMatchCounter))
#define G_IS_SCAN_MATCH_COUNTER(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_MATCH_COUNTER))
#define G_SCAN_MATCH_COUNTER_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_MATCH_COUNTER, GScanMatchCounterClass))
#define G_IS_SCAN_MATCH_COUNTER_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_MATCH_COUNTER))
#define G_SCAN_MATCH_COUNTER_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_MATCH_COUNTER, GScanMatchCounterClass))


/* Décompte des identifications de motifs (instance) */
typedef struct _GScanMatchCounter GScanMatchCounter;

/* Décompte des identifications de motifs (classe) */
typedef struct _GScanMatchCounterClass GScanMatchCounterClass;


/* Indique le type défini pour un décompte de résultats lors d'une recherche de motifs. */
GType g_scan_match_counter_get_type(void);

/* Met en place un décompte de correspondances obtenues. */
GScanExpression *g_scan_match_counter_new(GSearchPattern *);



#endif  /* _ANALYSIS_SCAN_EXPRS_COUNTER_H */
