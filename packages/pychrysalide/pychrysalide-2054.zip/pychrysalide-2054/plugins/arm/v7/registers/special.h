
/* Chrysalide - Outil d'analyse de fichiers binaires
 * special.h - prototypes pour les aides auxiliaires relatives aux registres spéciaux ARMv7
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


#ifndef _PLUGINS_ARM_V7_REGISTERS_SPECIAL_H
#define _PLUGINS_ARM_V7_REGISTERS_SPECIAL_H


#include <glib-object.h>
#include <stdint.h>


#include <arch/register.h>



/* ------------------------- GESTION UNITAIRE DES REGISTRES ------------------------- */


#define G_TYPE_ARMV7_SPECIAL_REGISTER            g_armv7_special_register_get_type()
#define G_ARMV7_SPECIAL_REGISTER(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_ARMV7_SPECIAL_REGISTER, GArmV7SpecialRegister))
#define G_IS_ARMV7_SPECIAL_REGISTER(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_ARMV7_SPECIAL_REGISTER))
#define G_ARMV7_SPECIAL_REGISTER_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ARMV7_SPECIAL_REGISTER, GArmV7SpecialRegisterClass))
#define G_IS_ARMV7_SPECIAL_REGISTER_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ARMV7_SPECIAL_REGISTER))
#define G_ARMV7_SPECIAL_REGISTER_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ARMV7_SPECIAL_REGISTER, GArmV7SpecialRegisterClass))


/* Représentation d'un registre spécial ARMv7 (instance) */
typedef struct _GArmV7SpecialRegister GArmV7SpecialRegister;

/* Représentation d'un registre spécial ARMv7 (classe) */
typedef struct _GArmV7SpecialRegisterClass GArmV7SpecialRegisterClass;


/* Désignation des registres spéciaux */
typedef enum _SpecRegTarget
{
    SRT_APSR,
    SRT_CPSR,
    SRT_SPSR,
    SRT_APSR_NZCVQ,
    SRT_APSR_G,
    SRT_APSR_NZCVQG,
    SRT_FPSID,
    SRT_FPSCR,
    SRT_MVFR1,
    SRT_MVFR0,
    SRT_FPEXC,

    SRT_COUNT

} SpecRegTarget;


/* Indique le type défini pour une représentation d'un registre spécial ARMv7. */
GType g_armv7_special_register_get_type(void);

/* Crée une réprésentation de registre spécial ARMv7. */
GArchRegister *g_armv7_special_register_new(SpecRegTarget);



/* ------------------------ GESTION SOUS FORME DE SINGLETONS ------------------------ */


/* Vide totalement le cache des registres spéciaux ARMv7. */
void clean_armv7_special_register_cache(void);



#endif  /* _PLUGINS_ARM_V7_REGISTERS_SPECIAL_H */
