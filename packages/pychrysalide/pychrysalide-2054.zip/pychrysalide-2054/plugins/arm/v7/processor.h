
/* Chrysalide - Outil d'analyse de fichiers binaires
 * processor.h - prototypes pour la manipulation du processeur ARMv7
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


#ifndef _PLUGINS_ARM_V7_PROCESSOR_H
#define _PLUGINS_ARM_V7_PROCESSOR_H


#include <glib-object.h>
#include <stdint.h>



#define G_TYPE_ARMV7_PROCESSOR               g_armv7_processor_get_type()
#define G_ARMV7_PROCESSOR(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), g_armv7_processor_get_type(), GArmV7Processor))
#define G_IS_ARMV7_PROCESSOR(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_armv7_processor_get_type()))
#define G_ARMV7_PROCESSOR_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ARMV7_PROCESSOR, GArmV7ProcessorClass))
#define G_IS_ARMV7_PROCESSOR_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ARMV7_PROCESSOR))
#define G_ARMV7_PROCESSOR_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ARMV7_PROCESSOR, GArmV7ProcessorClass))


/* Définition du processeur ARMv7 (instance) */
typedef struct _GArmV7Processor GArmV7Processor;

/* Définition du processeur ARMv7 (classe) */
typedef struct _GArmV7ProcessorClass GArmV7ProcessorClass;


/* Indique le type défini par la GLib pour le processeur ARMv7. */
GType g_armv7_processor_get_type(void);

/* Crée le support de l'architecture ARMv7. */
GArmV7Processor *g_armv7_processor_new(void);



#endif  /* _PLUGINS_ARM_V7_PROCESSOR_H */
