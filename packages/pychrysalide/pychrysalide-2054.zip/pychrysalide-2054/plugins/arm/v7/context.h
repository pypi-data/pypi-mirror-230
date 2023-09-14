
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


#ifndef _PLUGINS_ARM_V7_CONTEXT_H
#define _PLUGINS_ARM_V7_CONTEXT_H


#include <glib-object.h>


#include <arch/vmpa.h>



/* ------------------------ MANIPULATION GLOBALE DU CONTEXTE ------------------------ */


#define G_TYPE_ARMV7_CONTEXT              g_armv7_context_get_type()
#define G_ARMV7_CONTEXT(obj)              (G_TYPE_CHECK_INSTANCE_CAST((obj), g_armv7_context_get_type(), GArmV7Context))
#define G_IS_ARMV7_CONTEXT(obj)           (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_armv7_context_get_type()))
#define G_ARMV7_CONTEXT_CLASS(klass)      (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ARMV7_CONTEXT, GGArmV7ContextClass))
#define G_IS_ARMV7_CONTEXT_CLASS(klass)   (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ARMV7_CONTEXT))
#define G_ARMV7_CONTEXT_GET_CLASS(obj)    (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ARMV7_CONTEXT, GGArmV7ContextClass))


/* Définition d'un contexte pour processeur ARM (instance) */
typedef struct _GArmV7Context GArmV7Context;

/* Définition d'un contexte pour processeur ARM (classe) */
typedef struct _GArmV7ContextClass GArmV7ContextClass;


/* Indique le type défini par la GLib pour le contexte de processeur ARM. */
GType g_armv7_context_get_type(void);

/* Crée un contexte pour l'exécution du processeur ARM. */
GArmV7Context *g_armv7_context_new(void);


/* Jeux d'instructions possibles avec ARM v7 */
typedef enum _ArmV7InstrSet
{
    AV7IS_ARM,                              /* Encodage classique          */
    AV7IS_THUMB,                            /* Encodage compressé          */
    AV7IS_JAZELLE,                          /* Encodage JVM                */
    AV7IS_THUMBEE,                          /* Encodage dense + JIT/AOT    */

    AV7IS_COUNT

} ArmV7InstrSet;


/* Enregistre l'encodage (générique) utilisé à une adresse. */
void g_armv7_context_define_encoding(GArmV7Context *, virt_t, ArmV7InstrSet);

/* Indique l'encodage (générique) utilisé à une adresse donnée. */
ArmV7InstrSet g_armv7_context_find_encoding(GArmV7Context *, virt_t);



#endif  /* _PLUGINS_ARM_V7_CONTEXT_H */
