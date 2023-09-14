
/* Chrysalide - Outil d'analyse de fichiers binaires
 * targetable-int.h - définitions internes propres aux opérandes ciblant une portion de désassemblage
 *
 * Copyright (C) 2020 Cyrille Bagard
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


#ifndef _ARCH_OPERANDS_TARGETABLE_INT_H
#define _ARCH_OPERANDS_TARGETABLE_INT_H


#include "targetable.h"



/* Obtient l'adresse de la cible visée par un opérande. */
typedef bool (* get_targetable_addr_fc) (const GTargetableOperand *, const vmpa2t *, GBinFormat *, GArchProcessor *, vmpa2t *);


/* Opérande ciblant une portion de désassemblage (interface) */
struct _GTargetableOperandIface
{
    GTypeInterface base_iface;              /* A laisser en premier        */

    get_targetable_addr_fc get_addr;        /* Obtention de la cible       */

};


/* Redéfinition */
typedef GTargetableOperandIface GTargetableOperandInterface;



#endif  /* _ARCH_OPERANDS_TARGETABLE_INT_H */
