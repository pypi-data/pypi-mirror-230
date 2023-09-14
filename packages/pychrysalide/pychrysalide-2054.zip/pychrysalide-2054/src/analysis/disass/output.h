
/* Chrysalide - Outil d'analyse de fichiers binaires
 * output.h - prototypes pour l'impression des instructions désassemblées
 *
 * Copyright (C) 2010-2018 Cyrille Bagard
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


#ifndef _ANALYSIS_DISASS_OUTPUT_H
#define _ANALYSIS_DISASS_OUTPUT_H


#include "../binary.h"
#include "../human/lang.h"
#include "../../format/preload.h"
#include "../../glibext/buffercache.h"
#include "../../glibext/notifier.h"



/* Transcrit du code désassemblé en texte humainement lisible. */
void print_disassembled_instructions(GBufferCache *, GCodingLanguage *, GLoadedBinary *, GPreloadInfo *, GtkStatusStack *);



#endif  /* _ANALYSIS_DISASS_OUTPUT_H */
