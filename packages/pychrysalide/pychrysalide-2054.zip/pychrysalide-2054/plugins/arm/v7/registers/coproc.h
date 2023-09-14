
/* Chrysalide - Outil d'analyse de fichiers binaires
 * coproc.h - prototypes pour les aides auxiliaires relatives aux registres de co-processeur ARMv7
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


#ifndef _PLUGINS_ARM_V7_REGISTERS_COPROC_H
#define _PLUGINS_ARM_V7_REGISTERS_COPROC_H


#include <glib-object.h>
#include <stdint.h>


#include <arch/register.h>



/* ------------------------- GESTION UNITAIRE DES REGISTRES ------------------------- */


#define G_TYPE_ARMV7_CP_REGISTER            g_armv7_cp_register_get_type()
#define G_ARMV7_CP_REGISTER(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_ARMV7_CP_REGISTER, GArmV7CpRegister))
#define G_IS_ARMV7_CP_REGISTER(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_ARMV7_CP_REGISTER))
#define G_ARMV7_CP_REGISTER_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ARMV7_CP_REGISTER, GArmV7CpRegisterClass))
#define G_IS_ARMV7_CP_REGISTER_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ARMV7_CP_REGISTER))
#define G_ARMV7_CP_REGISTER_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ARMV7_CP_REGISTER, GArmV7CpRegisterClass))


/* Représentation d'un registre de co-processeur ARMv7 (instance) */
typedef struct _GArmV7CpRegister GArmV7CpRegister;

/* Représentation d'un registre de co-processeur ARMv7 (classe) */
typedef struct _GArmV7CpRegisterClass GArmV7CpRegisterClass;


/* Indique le type défini pour une représentation d'un registre de co-processeur ARMv7. */
GType g_armv7_cp_register_get_type(void);

/* Crée une réprésentation de registre de co-processeur ARMv7. */
GArchRegister *g_armv7_cp_register_new(uint8_t);



/* ------------------------ GESTION SOUS FORME DE SINGLETONS ------------------------ */


/* Vide totalement le cache des registres de co-processeur ARMv7. */
void clean_armv7_cp_register_cache(void);



#endif  /* _PLUGINS_ARM_V7_REGISTERS_COPROC_H */
