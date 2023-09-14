
/* Chrysalide - Outil d'analyse de fichiers binaires
 * processor.h - prototypes pour la manipulation du processeur de la JVM
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#ifndef _ARCH_JVM_PROCESSOR_H
#define _ARCH_JVM_PROCESSOR_H


#include "../processor.h"



#define G_TYPE_JVM_PROCESSOR            g_jvm_processor_get_type()
#define G_JVM_PROCESSOR(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_JVM_PROCESSOR, GJvmProcessor))
#define G_IS_JVM_PROCESSOR(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_JVM_PROCESSOR))
#define G_JVM_PROCESSOR_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_JVM_PROCESSOR, GJvmProcessorClass))
#define G_IS_JVM_PROCESSOR_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_JVM_PROCESSOR))
#define G_JVM_PROCESSOR_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_JVM_PROCESSOR, GJvmProcessorClass))


/* Définition du processeur de la JVM (instance) */
typedef struct _GJvmProcessor GJvmProcessor;

/* Définition du processeur de la JVM (classe) */
typedef struct _GJvmProcessorClass GJvmProcessorClass;


/* Indique le type défini par la GLib pour le processeur JVM. */
GType g_jvm_processor_get_type(void);

/* Crée le support de l'architecture JVM. */
GArchProcessor *g_jvm_processor_new(void);



#endif  /* _ARCH_JVM_PROCESSOR_H */
