
/* Chrysalide - Outil d'analyse de fichiers binaires
 * register-int.h - définitions internes pour la représentation générique d'un registre
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


#ifndef _ARCH_OPERANDS_REGISTER_INT_H
#define _ARCH_OPERANDS_REGISTER_INT_H


#include "register.h"


#include "../operand-int.h"



/* Définition d'un opérande visant un registre (instance) */
struct _GRegisterOperand
{
    GArchOperand parent;                    /* Instance parente            */

    GArchRegister *reg;                     /* Registre représenté         */

};

/* Définition d'un opérande visant un registre (classe) */
struct _GRegisterOperandClass
{
    GArchOperandClass parent;               /* Classe parente              */

};



#endif  /* _ARCH_OPERANDS_REGISTER_INT_H */
