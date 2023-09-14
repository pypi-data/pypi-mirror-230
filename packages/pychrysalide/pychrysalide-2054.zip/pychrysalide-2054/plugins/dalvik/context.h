
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


#ifndef _PLUGINS_DALVIK_CONTEXT_H
#define _PLUGINS_DALVIK_CONTEXT_H


#include <glib-object.h>
#include <stdbool.h>


#include "instruction.h"



/* ------------------------ MANIPULATION GLOBALE DU CONTEXTE ------------------------ */


#define G_TYPE_DALVIK_CONTEXT              g_dalvik_context_get_type()
#define G_DALVIK_CONTEXT(obj)              (G_TYPE_CHECK_INSTANCE_CAST((obj), g_dalvik_context_get_type(), GDalvikContext))
#define G_IS_DALVIK_CONTEXT(obj)           (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_dalvik_context_get_type()))
#define G_DALVIK_CONTEXT_CLASS(klass)      (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DALVIK_CONTEXT, GGDalvikContextClass))
#define G_IS_DALVIK_CONTEXT_CLASS(klass)   (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DALVIK_CONTEXT))
#define G_DALVIK_CONTEXT_GET_CLASS(obj)    (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DALVIK_CONTEXT, GGDalvikContextClass))


/* Définition d'un contexte pour processeur Dalkvik (instance) */
typedef struct _GDalvikContext GDalvikContext;

/* Définition d'un contexte pour processeur Dalkvik (classe) */
typedef struct _GDalvikContextClass GDalvikContextClass;


/* Indique le type défini par la GLib pour le contexte de processeur Dalkvik. */
GType g_dalvik_context_get_type(void);

/* Crée un contexte pour l'exécution du processeur Dalvik. */
GDalvikContext *g_dalvik_context_new(void);

/* Mémorise une zone comme étant des données de branchements. */
bool g_dalvik_context_register_switch_data(GDalvikContext *ctx, const vmpa2t *start, phys_t length);

/* Mémorise une zone comme étant des données d'un tableau. */
bool g_dalvik_context_register_array_data(GDalvikContext *, const vmpa2t *, uint16_t, phys_t);

/* Mémorise une zone comme étant un bourrage de fin de tableau. */
bool g_dalvik_context_register_array_data_padding(GDalvikContext *, const vmpa2t *);

/* Place une donnée en tant qu'instruction si besoin est. */
GArchInstruction *g_dalvik_context_get_raw_data(GDalvikContext *, const GBinContent *, vmpa2t *);



#endif  /* _PLUGINS_DALVIK_CONTEXT_H */
