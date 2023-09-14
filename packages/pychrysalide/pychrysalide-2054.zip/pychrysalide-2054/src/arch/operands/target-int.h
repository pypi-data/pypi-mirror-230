
/* Chrysalide - Outil d'analyse de fichiers binaires
 * target-int.h - définitions internes propres aux opérandes ciblant un symbole
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


#ifndef _ARCH_OPERANDS_TARGET_INT_H
#define _ARCH_OPERANDS_TARGET_INT_H


#include "target.h"
#include "../operand-int.h"



/* Informations glissées dans la structure GObject de GArchOperand */
typedef struct _tarop_extra_data_t
{
    operand_extra_data_t parent;            /* A laisser en premier        */

    MemoryDataSize size;                    /* Taille de l'opérande        */

} tarop_extra_data_t;

/* Définition d'un opérande ciblant idéalement un symbole connu (instance) */
struct _GTargetOperand
{
    GArchOperand parent;                    /* Instance parente            */

    vmpa2t addr;                            /* Adresse de l'élément visé   */

    /* Référence circulaire */
    GBinSymbol *symbol;                     /* Eventuel symbole associé    */
    phys_t diff;                            /* Position dans le symbole    */

};


/* Définition d'un opérande ciblant idéalement un symbole connu (classe) */
struct _GTargetOperandClass
{
    GArchOperandClass parent;               /* Classe parente              */

};


/**
 * Accès aux informations éventuellement déportées.
 */

#if 1 //__SIZEOF_INT__ == __SIZEOF_LONG__

#   define GET_TARGET_OP_EXTRA(op) ((tarop_extra_data_t *)&((GArchOperand *)op)->extra)

#else

#   define GET_TARGET_OP_EXTRA(op) GET_GOBJECT_EXTRA(G_OBJECT(op), tarop_extra_data_t)

#endif



#endif  /* _ARCH_OPERANDS_TARGET_INT_H */
