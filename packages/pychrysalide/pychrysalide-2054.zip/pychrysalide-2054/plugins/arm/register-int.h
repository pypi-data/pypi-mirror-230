
/* Chrysalide - Outil d'analyse de fichiers binaires
 * register-int.h - définitions internes pour la représentation d'un registre ARM
 *
 * Copyright (C) 2017-2018 Cyrille Bagard
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


#ifndef _PLUGINS_ARM_REGISTER_INT_H
#define _PLUGINS_ARM_REGISTER_INT_H


#include <arch/register-int.h>


#include "register.h"



/* Représentation d'un registre ARM (instance) */
struct _GArmRegister
{
    GArchRegister parent;                   /* A laisser en premier        */

    uint8_t index;                          /* Indice du registre          */

};


/* Représentation d'un registre ARM (classe) */
struct _GArmRegisterClass
{
    GArchRegisterClass parent;              /* A laisser en premier        */

};



#endif  /* _PLUGINS_ARM_REGISTER_INT_H */
