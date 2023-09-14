
/* Chrysalide - Outil d'analyse de fichiers binaires
 * processor.h - prototypes pour la manipulation du processeur ARM
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


#ifndef _PLUGINS_ARM_PROCESSOR_H
#define _PLUGINS_ARM_PROCESSOR_H


#include <glib-object.h>
#include <stdint.h>



#define G_TYPE_ARM_PROCESSOR               g_arm_processor_get_type()
#define G_ARM_PROCESSOR(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), g_arm_processor_get_type(), GArmProcessor))
#define G_IS_ARM_PROCESSOR(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_arm_processor_get_type()))
#define G_ARM_PROCESSOR_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ARM_PROCESSOR, GArmProcessorClass))
#define G_IS_ARM_PROCESSOR_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ARM_PROCESSOR))
#define G_ARM_PROCESSOR_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ARM_PROCESSOR, GArmProcessorClass))


/* Définition du processeur ARM (instance) */
typedef struct _GArmProcessor GArmProcessor;

/* Définition du processeur ARM (classe) */
typedef struct _GArmProcessorClass GArmProcessorClass;


/* Indique le type défini par la GLib pour le processeur ARM. */
GType g_arm_processor_get_type(void);



#endif  /* _PLUGINS_ARM_PROCESSOR_H */
