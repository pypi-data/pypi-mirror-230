
/* Chrysalide - Outil d'analyse de fichiers binaires
 * processor.h - prototypes pour la manipulation du processeur de la VM Dalvik
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


#ifndef _PLUGINS_DALVIK_V35_PROCESSOR_H
#define _PLUGINS_DALVIK_V35_PROCESSOR_H


#include <arch/processor.h>



#define G_TYPE_DALVIK35_PROCESSOR            g_dalvik35_processor_get_type()
#define G_DALVIK35_PROCESSOR(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_DALVIK35_PROCESSOR, GDalvik35Processor))
#define G_IS_DALVIK35_PROCESSOR(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_DALVIK35_PROCESSOR))
#define G_DALVIK35_PROCESSOR_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DALVIK35_PROCESSOR, GDalvik35ProcessorClass))
#define G_IS_DALVIK35_PROCESSOR_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DALVIK35_PROCESSOR))
#define G_DALVIK35_PROCESSOR_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DALVIK35_PROCESSOR, GDalvik35ProcessorClass))


/* Définition du processeur de la VM Dalvik v35 (instance) */
typedef struct _GDalvik35Processor GDalvik35Processor;

/* Définition du processeur de la VM Dalvik v35 (classe) */
typedef struct _GDalvik35ProcessorClass GDalvik35ProcessorClass;


/* Indique le type défini par la GLib pour le processeur Dalvik v35. */
GType g_dalvik35_processor_get_type(void);

/* Crée le support de l'architecture Dalvik v35. */
GArchProcessor *g_dalvik35_processor_new(void);



#endif  /* _PLUGINS_DALVIK_V35_PROCESSOR_H */
