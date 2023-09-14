
/* Chrysalide - Outil d'analyse de fichiers binaires
 * immediate-int.h - définitions internes propres aux opérandes représentant des valeurs numériques
 *
 * Copyright (C) 2021 Cyrille Bagard
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


#ifndef _ARCH_OPERANDS_IMMEDIATE_INT_H
#define _ARCH_OPERANDS_IMMEDIATE_INT_H


#include "immediate.h"
#include "../operand-int.h"



/* Informations glissées dans la structure GObject de GArchOperand */
typedef struct _immop_extra_data_t
{
    operand_extra_data_t parent;            /* A laisser en premier        */

    MemoryDataSize size;                    /* Taille de l'opérande        */

    /**
     * Les deux éléments suivants sont de type ImmOperandDisplay ;
     * leur espace de conservation est réduit au maximum afin d'éviter
     * un recouvrement .
     */

    unsigned int def_display : 3;           /* Type par défaut d'affichage */
    unsigned int display : 3;               /* Format général d'affichage  */

} immop_extra_data_t;


/* Définition d'un opérande de valeur numérique (instance) */
struct _GImmOperand
{
    GArchOperand parent;                    /* Instance parente            */

    uint64_t raw;                           /* Valeur transtypée           */

};

/* Définition d'un opérande de valeur numérique (classe) */
struct _GImmOperandClass
{
    GArchOperandClass parent;               /* Classe parente              */

};


/**
 * Accès aux informations éventuellement déportées.
 */

#if 1 //__SIZEOF_INT__ == __SIZEOF_LONG__

#   define GET_IMM_OP_EXTRA(op) ((immop_extra_data_t *)&((GArchOperand *)op)->extra)

#else

#   define GET_IMM_OP_EXTRA(op) GET_GOBJECT_EXTRA(G_OBJECT(op), immop_extra_data_t)

#endif



#endif  /* _ARCH_OPERANDS_IMMEDIATE_INT_H */
