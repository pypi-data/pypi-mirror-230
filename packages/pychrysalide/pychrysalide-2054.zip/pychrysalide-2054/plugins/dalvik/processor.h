
/* Chrysalide - Outil d'analyse de fichiers binaires
 * processor.h - prototypes pour la manipulation du processeur de la VM Dalvik
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


#ifndef _PLUGINS_DALVIK_PROCESSOR_H
#define _PLUGINS_DALVIK_PROCESSOR_H


#include <arch/processor.h>



#define G_TYPE_DALVIK_PROCESSOR            g_dalvik_processor_get_type()
#define G_DALVIK_PROCESSOR(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_DALVIK_PROCESSOR, GDalvikProcessor))
#define G_IS_DALVIK_PROCESSOR(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_DALVIK_PROCESSOR))
#define G_DALVIK_PROCESSOR_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DALVIK_PROCESSOR, GDalvikProcessorClass))
#define G_IS_DALVIK_PROCESSOR_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DALVIK_PROCESSOR))
#define G_DALVIK_PROCESSOR_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DALVIK_PROCESSOR, GDalvikProcessorClass))


/* Définition du processeur de la VM Dalvik (instance) */
typedef struct _GDalvikProcessor GDalvikProcessor;

/* Définition du processeur de la VM Dalvik (classe) */
typedef struct _GDalvikProcessorClass GDalvikProcessorClass;


/* Indique le type défini par la GLib pour le processeur Dalvik. */
GType g_dalvik_processor_get_type(void);



#endif  /* _PLUGINS_DALVIK_PROCESSOR_H */
