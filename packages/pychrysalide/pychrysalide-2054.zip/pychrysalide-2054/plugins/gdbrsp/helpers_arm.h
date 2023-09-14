
/* Chrysalide - Outil d'analyse de fichiers binaires
 * helpers_arm.h - prototypes pour les compléments utiles à GDB pour l'architecture ARM
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


#ifndef _DEBUG_GDBRSP_HELPERS_ARM_H
#define _DEBUG_GDBRSP_HELPERS_ARM_H


#include "aops.h"



/* Fournit les fonctions adaptées aux opérations pour ARM. */
const gdb_arch_ops *get_arm_operations(void);



#endif  /* _DEBUG_GDBRSP_HELPERS_ARM_H */
