
/* Chrysalide - Outil d'analyse de fichiers binaires
 * registers.h - prototypes pour les aides auxiliaires relatives aux registres ARM
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


#ifndef _PLUGINS_ARM_REGISTER_H
#define _PLUGINS_ARM_REGISTER_H


#include <glib-object.h>
#include <stdint.h>



/* ------------------------- GESTION UNITAIRE DES REGISTRES ------------------------- */


#define G_TYPE_ARM_REGISTER            g_arm_register_get_type()
#define G_ARM_REGISTER(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_ARM_REGISTER, GArmRegister))
#define G_IS_ARM_REGISTER(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_ARM_REGISTER))
#define G_ARM_REGISTER_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ARM_REGISTER, GArmRegisterClass))
#define G_IS_ARM_REGISTER_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ARM_REGISTER))
#define G_ARM_REGISTER_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ARM_REGISTER, GArmRegisterClass))


/* Représentation d'un registre ARM (instance) */
typedef struct _GArmRegister GArmRegister;

/* Représentation d'un registre ARM (classe) */
typedef struct _GArmRegisterClass GArmRegisterClass;


/* Indique le type défini pour une représentation d'un registre ARM. */
GType g_arm_register_get_type(void);

/* Fournit l'indice d'un registre ARM. */
uint8_t g_arm_register_get_index(const GArmRegister *);



#endif  /* _PLUGINS_ARM_REGISTER_H */
