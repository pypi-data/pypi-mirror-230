
/* Chrysalide - Outil d'analyse de fichiers binaires
 * instructions.h - prototypes pour l'étude complémentaire des instructions désassemblées
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


#ifndef _ANALYSIS_DISASS_INSTRUCTIONS_H
#define _ANALYSIS_DISASS_INSTRUCTIONS_H


#include "../routine.h"
#include "../../arch/processor.h"
#include "../../format/executable.h"
#include "../../glibext/notifier.h"



#define G_TYPE_INSTRUCTIONS_STUDY               g_instructions_study_get_type()
#define G_INSTRUCTIONS_STUDY(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), g_instructions_study_get_type(), GInstructionsStudy))
#define G_IS_INSTRUCTIONS_STUDY(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_instructions_study_get_type()))
#define G_INSTRUCTIONS_STUDY_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_INSTRUCTIONS_STUDY, GInstructionsStudyClass))
#define G_IS_INSTRUCTIONS_STUDY_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_INSTRUCTIONS_STUDY))
#define G_INSTRUCTIONS_STUDY_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_INSTRUCTIONS_STUDY, GInstructionsStudyClass))


/* Fraction d'instructions à limiter (instance) */
typedef struct _GInstructionsStudy GInstructionsStudy;

/* Fraction d'instructions à limiter (classe) */
typedef struct _GInstructionsStudyClass GInstructionsStudyClass;


/* Assure l'étude d'instructions en différé. */
typedef void (* ins_fallback_cb) (GInstructionsStudy *, size_t);


/* Indique le type défini pour les tâches d'étude d'instructions. */
GType g_instructions_study_get_type(void);

/* Crée une tâche d'étude de instructions différée. */
GInstructionsStudy *g_instructions_study_new(GArchProcessor *, GProcContext *, GExeFormat *, size_t, size_t, activity_id_t, ins_fallback_cb);

/* Réalise l'appel de type IPH_LINK sur une instruction. */
void g_instructions_study_do_link_operation(GInstructionsStudy *, size_t);

/* Réalise l'appel de type IPH_POST sur une instruction. */
void g_instructions_study_do_post_operation(GInstructionsStudy *, size_t);

/* Etablit les liens entres les différentes instructions. */
void g_instructions_study_establish_links(GInstructionsStudy *, size_t);



#endif  /* _ANALYSIS_DISASS_INSTRUCTIONS_H */
