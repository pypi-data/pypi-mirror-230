
/* Chrysalide - Outil d'analyse de fichiers binaires
 * symbols.h - prototypes pour la gestion des symboles d'un MCLF
 *
 * Copyright (C) 2015-2018 Cyrille Bagard
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


#ifndef _PLUGINS_MOBICORE_SYMBOLS_H
#define _PLUGINS_MOBICORE_SYMBOLS_H


#include <stdbool.h>


#include "mclf.h"



/* Charge en mémoire la liste humaine des symboles. */
bool load_mclf_symbols(GMCLFFormat *);



#endif  /* _PLUGINS_MOBICORE_SYMBOLS_H */
