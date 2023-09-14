
/* Chrysalide - Outil d'analyse de fichiers binaires
 * processor-int.h - prototypes pour la définition générique interne du processeur de la VM Dalvik
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


#ifndef _PLUGINS_DALVIK_PROCESSOR_INT_H
#define _PLUGINS_DALVIK_PROCESSOR_INT_H


#include "processor.h"


#include <arch/processor-int.h>


#include "context.h"



/* Définition du processeur de la VM Dalvik (instance) */
struct _GDalvikProcessor
{
    GArchProcessor parent;                  /* Instance parente            */

};


/* Définition du processeur de la VM Dalvik (classe) */
struct _GDalvikProcessorClass
{
    GArchProcessorClass parent;             /* Classe parente              */

};


/* Décode une pseudo-instruction dans un flux de données. */
GArchInstruction *g_dalvik_processor_disassemble_pseudo(const GArchProcessor *, GDalvikContext *, const GBinContent *, vmpa2t *, uint8_t, bool *);



#endif  /* _PLUGINS_DALVIK_PROCESSOR_INT_H */
