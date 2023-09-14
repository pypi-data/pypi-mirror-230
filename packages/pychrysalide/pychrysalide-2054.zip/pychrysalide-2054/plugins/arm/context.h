
/* Chrysalide - Outil d'analyse de fichiers binaires
 * context.h - prototypes pour le contexte lié à l'exécution d'un processeur
 *
 * Copyright (C) 2017-2018 Cyrille Bagard
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


#ifndef _PLUGINS_ARM_CONTEXT_H
#define _PLUGINS_ARM_CONTEXT_H


#include <glib-object.h>



/* ------------------------ MANIPULATION GLOBALE DU CONTEXTE ------------------------ */


#define G_TYPE_ARM_CONTEXT              g_arm_context_get_type()
#define G_ARM_CONTEXT(obj)              (G_TYPE_CHECK_INSTANCE_CAST((obj), g_arm_context_get_type(), GArmContext))
#define G_IS_ARM_CONTEXT(obj)           (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_arm_context_get_type()))
#define G_ARM_CONTEXT_CLASS(klass)      (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ARM_CONTEXT, GGArmContextClass))
#define G_IS_ARM_CONTEXT_CLASS(klass)   (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ARM_CONTEXT))
#define G_ARM_CONTEXT_GET_CLASS(obj)    (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ARM_CONTEXT, GGArmContextClass))


/* Définition d'un contexte pour processeur ARM (instance) */
typedef struct _GArmContext GArmContext;

/* Définition d'un contexte pour processeur ARM (classe) */
typedef struct _GArmContextClass GArmContextClass;


/* Indique le type défini par la GLib pour le contexte de processeur ARM. */
GType g_arm_context_get_type(void);

/* Crée un contexte pour l'exécution du processeur ARM. */
GArmContext *g_arm_context_new(void);



#endif  /* _PLUGINS_ARM_CONTEXT_H */
