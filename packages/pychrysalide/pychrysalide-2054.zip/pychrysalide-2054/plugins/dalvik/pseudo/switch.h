
/* Chrysalide - Outil d'analyse de fichiers binaires
 * switch.h - prototypes pour la prise en charge des instructions spéciales (packed|sparse)switch
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


#ifndef _PLUGINS_DALVIK_PSEUDO_SWITCH_H
#define _PLUGINS_DALVIK_PSEUDO_SWITCH_H


#include "../context.h"
#include "../instruction.h"
#include "../processor.h"


#include <glib-object.h>



#define G_TYPE_DALVIK_SWITCH_INSTR      g_dalvik_switch_instr_get_type()
#define G_DALVIK_SWITCH_INSTR(obj)      (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_DALVIK_SWITCH_INSTR, GDalvikSwitchInstr))
#define G_IS_DALVIK_SWITCH_INSTR(obj)   (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_DALVIK_SWITCH_INSTR))
#define G_DALVIK_SWITCH_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DALVIK_SWITCH, GGDalvikSwitchClass))
#define G_IS_DALVIK_SWITCH_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DALVIK_SWITCH))
#define G_DALVIK_SWITCH_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DALVIK_SWITCH, GGDalvikSwitchClass))


/* Définition générique d'une instruction d'architecture (instance) */
typedef struct _GDalvikSwitchInstr GDalvikSwitchInstr;

/* Définition générique d'une instruction d'architecture (classe) */
typedef struct _GDalvikSwitchInstrClass GDalvikSwitchInstrClass;


/* Indique le type défini pour une pseudo-instruction Dalvik de remplissage. */
GType g_dalvik_switch_instr_get_type(void);

/* Crée une pesudo-instruction Dalvik de branchement. */
GArchInstruction *g_dalvik_switch_instr_new(uint16_t, GDalvikContext *, const GBinContent *, vmpa2t *);

/* Fournit les données associées à un branchement Dalvik. */
uint16_t g_dalvik_switch_get_data(GDalvikSwitchInstr *, const int32_t **, const int32_t **);



#endif  /* _PLUGINS_DALVIK_PSEUDO_SWITCH_H */
