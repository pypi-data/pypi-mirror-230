
/* Chrysalide - Outil d'analyse de fichiers binaires
 * limit.h - prototypes pour la détermination des bornes des routines
 *
 * Copyright (C) 2012-2018 Cyrille Bagard
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


#ifndef _ANALYSIS_DISASS_LIMIT_H
#define _ANALYSIS_DISASS_LIMIT_H


#include "../../arch/processor.h"
#include "../../format/executable.h"
#include "../../format/symbol.h"



/* S'assure qu'une routine est bien bornée. */
void compute_routine_limit(GBinSymbol *, const vmpa2t *, GArchProcessor *, GBinPortion *);



#endif  /* _ANALYSIS_DISASS_LIMIT_H */
