
/* Chrysalide - Outil d'analyse de fichiers binaires
 * routines.h - prototypes pour l'étude des flots d'exécution dans les routines
 *
 * Copyright (C) 2016-2019 Cyrille Bagard
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
 *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _ANALYSIS_DISASS_ROUTINES_H
#define _ANALYSIS_DISASS_ROUTINES_H


#include "../binary.h"
#include "../routine.h"
#include "../../glibext/notifier.h"



#define G_TYPE_ROUTINES_STUDY               g_routines_study_get_type()
#define G_ROUTINES_STUDY(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), g_routines_study_get_type(), GRoutinesStudy))
#define G_IS_ROUTINES_STUDY(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_routines_study_get_type()))
#define G_ROUTINES_STUDY_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ROUTINES_STUDY, GRoutinesStudyClass))
#define G_IS_ROUTINES_STUDY_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ROUTINES_STUDY))
#define G_ROUTINES_STUDY_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ROUTINES_STUDY, GRoutinesStudyClass))


/* Fraction de routines à limiter (instance) */
typedef struct _GRoutinesStudy GRoutinesStudy;

/* Fraction de routines à limiter (classe) */
typedef struct _GRoutinesStudyClass GRoutinesStudyClass;


/* Assure l'étude des routines en différé. */
typedef void (* rtn_fallback_cb) (GRoutinesStudy *, GBinRoutine *, size_t);


/* Indique le type défini pour les tâches d'étude de routines. */
GType g_routines_study_get_type(void);

/* Crée une tâche d'étude de routines différée. */
GRoutinesStudy *g_routines_study_new(GLoadedBinary *, GBinPortion *, size_t, size_t, activity_id_t, rtn_fallback_cb);

/* Détermine si besoin est les bornes des routines. */
void g_routines_study_compute_limits(GRoutinesStudy *, GBinRoutine *, size_t);

/* Procède au traitement des blocs de routines. */
void g_routines_study_handle_blocks(GRoutinesStudy *, GBinRoutine *, size_t);



#endif  /* _ANALYSIS_DISASS_ROUTINES_H */
