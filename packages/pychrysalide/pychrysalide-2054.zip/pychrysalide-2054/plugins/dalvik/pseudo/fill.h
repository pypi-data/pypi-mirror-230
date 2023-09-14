
/* Chrysalide - Outil d'analyse de fichiers binaires
 * fill.h - prototypes pour la prise en charge de l'instruction spéciale fill-array-data
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


#ifndef _PLUGINS_DALVIK_PSEUDO_FILL_H
#define _PLUGINS_DALVIK_PSEUDO_FILL_H


#include "../context.h"
#include "../instruction.h"
#include "../processor.h"


#include <glib-object.h>



#define G_TYPE_DALVIK_FILL_INSTR        g_dalvik_fill_instr_get_type()
#define G_DALVIK_FILL_INSTR(obj)        (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_DALVIK_FILL_INSTR, GDalvikFillInstr))
#define G_IS_DALVIK_FILL_INSTR(obj)     (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_DALVIK_FILL_INSTR))
#define G_DALVIK_FILL_CLASS(klass)      (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DALVIK_FILL, GGDalvikFillClass))
#define G_IS_DALVIK_FILL_CLASS(klass)   (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DALVIK_FILL))
#define G_DALVIK_FILL_GET_CLASS(obj)    (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DALVIK_FILL, GGDalvikFillClass))


/* Définition générique d'une instruction d'architecture (instance) */
typedef struct _GDalvikFillInstr GDalvikFillInstr;

/* Définition générique d'une instruction d'architecture (classe) */
typedef struct _GDalvikFillInstrClass GDalvikFillInstrClass;


/* Indique le type défini pour une pseudo-instruction Dalvik de remplissage. */
GType g_dalvik_fill_instr_get_type(void);

/* Crée une pesudo-instruction Dalvik de remplissage. */
GArchInstruction *g_dalvik_fill_instr_new(uint16_t, GDalvikContext *, const GBinContent *, vmpa2t *);



#endif  /* _PLUGINS_DALVIK_PSEUDO_FILL_H */
