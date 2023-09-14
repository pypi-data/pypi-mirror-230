
/* Chrysalide - Outil d'analyse de fichiers binaires
 * cond-int.h - prototypes internes pour le parcours de contenus à la recherche de motifs
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


#ifndef _ANALYSIS_SCAN_COND_INT_H
#define _ANALYSIS_SCAN_COND_INT_H


#include "cond.h"



/* Indique le statut d'une condition de validation. */
typedef bool (* resolve_cond_fc) (const GMatchCondition *);

/* Indique le statut d'une condition de validation. */
typedef unsigned long long (* resolve_cond_as_number_fc) (const GMatchCondition *);

/* Avance vers la validation d'une condition, si besoin est. */
typedef void (* analyze_cond_fc) (const GMatchCondition *, const bin_t *, phys_t, phys_t, bool);



/* Expression conditionnelle manipulant des motifs (instance) */
struct _GMatchCondition
{
    GObject parent;                         /* A laisser en premier        */

};

/* Expression conditionnelle manipulant des motifs (classe) */
struct _GMatchConditionClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    resolve_cond_fc resolve;                /* Réduction en booléen        */
    resolve_cond_as_number_fc resolve_as_num;   /* Réduction en nombre     */
    analyze_cond_fc analyze;                /* Analyse selon une position  */

};



#endif  /* _ANALYSIS_SCAN_COND_INT_H */
