
/* Chrysalide - Outil d'analyse de fichiers binaires
 * hops_armv7.h - prototypes pour la recherche d'appels système spécifiques à ARMv7
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


#ifndef _PLUGINS_LNXSYSCALLS_HOPS_ARMV7_H
#define _PLUGINS_LNXSYSCALLS_HOPS_ARMV7_H


#include "hops.h"



/* Fournit les opérations spécifiques à ARMv7 pour une chasse. */
const hunting_ops *get_armv7_hunting_ops(void);



#endif  /* _PLUGINS_LNXSYSCALLS_HOPS_ARMV7_H */
