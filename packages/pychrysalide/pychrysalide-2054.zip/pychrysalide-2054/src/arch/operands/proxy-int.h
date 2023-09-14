
/* Chrysalide - Outil d'analyse de fichiers binaires
 * proxy-int.h - définitions internes pour les opérandes renvoyant vers des éléments non architecturaux
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


#ifndef _ARCH_OPERANDS_PROXY_INT_H
#define _ARCH_OPERANDS_PROXY_INT_H


#include "proxy.h"
#include "../operand-int.h"



/* Définition d'un opérande renvoyant vers un élément (instance) */
struct _GProxyOperand
{
    GArchOperand parent;                    /* Instance parente            */

    GProxyFeeder *feeder;                   /* Fournisseur de contenu      */

};

/* Définition d'un opérande renvoyant vers un élément (classe) */
struct _GProxyOperandClass
{
    GArchOperandClass parent;               /* Classe parente              */

};



#endif  /* _ARCH_OPERANDS_PROXY_INT_H */
