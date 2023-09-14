
/* Chrysalide - Outil d'analyse de fichiers binaires
 * cond.h - prototypes pour l'expression conditionnelle validant la présence de motifs donnés
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


#ifndef _ANALYSIS_SCAN_COND_H
#define _ANALYSIS_SCAN_COND_H


#include <glib-object.h>


#include "../../arch/archbase.h"
#include "../../arch/vmpa.h"



#define G_TYPE_MATCH_CONDITION            g_match_condition_get_type()
#define G_MATCH_CONDITION(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_MATCH_CONDITION, GMatchCondition))
#define G_IS_MATCH_CONDITION(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_MATCH_CONDITION))
#define G_MATCH_CONDITION_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_MATCH_CONDITION, GMatchConditionClass))
#define G_IS_MATCH_CONDITION_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_MATCH_CONDITION))
#define G_MATCH_CONDITION_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_MATCH_CONDITION, GMatchConditionClass))


/* Expression conditionnelle manipulant des motifs (instance) */
typedef struct _GMatchCondition GMatchCondition;

/* Expression conditionnelle manipulant des motifs (classe) */
typedef struct _GMatchConditionClass GMatchConditionClass;


/* Indique le type défini pour une expression de validation. */
GType g_match_condition_get_type(void);

/* Indique le statut d'une condition de validation. */
bool g_match_condition_resolve(const GMatchCondition *);

/* Indique le statut d'une condition de validation. */
unsigned long long g_match_condition_resolve_as_number(const GMatchCondition *);

/* Avance vers la validation d'une condition, si besoin est. */
void g_match_condition_analyze(const GMatchCondition *, const bin_t *, phys_t, phys_t, bool);



#endif  /* _ANALYSIS_SCAN_COND_H */
