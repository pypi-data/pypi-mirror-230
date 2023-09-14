
/* Chrysalide - Outil d'analyse de fichiers binaires
 * banked.h - prototypes pour les aides auxiliaires relatives aux registres de banque ARMv7
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


#ifndef _PLUGINS_ARM_V7_REGISTERS_BANKED_H
#define _PLUGINS_ARM_V7_REGISTERS_BANKED_H


#include <glib-object.h>
#include <stdint.h>


#include <arch/register.h>



/* ------------------------- GESTION UNITAIRE DES REGISTRES ------------------------- */


#define G_TYPE_ARMV7_BANKED_REGISTER            g_armv7_banked_register_get_type()
#define G_ARMV7_BANKED_REGISTER(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_ARMV7_BANKED_REGISTER, GArmV7BankedRegister))
#define G_IS_ARMV7_BANKED_REGISTER(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_ARMV7_BANKED_REGISTER))
#define G_ARMV7_BANKED_REGISTER_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ARMV7_BANKED_REGISTER, GArmV7BankedRegisterClass))
#define G_IS_ARMV7_BANKED_REGISTER_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ARMV7_BANKED_REGISTER))
#define G_ARMV7_BANKED_REGISTER_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ARMV7_BANKED_REGISTER, GArmV7BankedRegisterClass))


/* Représentation d'un registre de banque ARMv7 (instance) */
typedef struct _GArmV7BankedRegister GArmV7BankedRegister;

/* Représentation d'un registre de banque ARMv7 (classe) */
typedef struct _GArmV7BankedRegisterClass GArmV7BankedRegisterClass;


/* Liste des registres de banque */
typedef enum _BankedRegisterTarget
{
    BRT_R8_USR,
    BRT_R9_USR,
    BRT_R10_USR,
    BRT_R11_USR,
    BRT_R12_USR,
    BRT_SP_USR,
    BRT_LR_USR,

    BRT_R8_FIQ,
    BRT_R9_FIQ,
    BRT_R10_FIQ,
    BRT_R11_FIQ,
    BRT_R12_FIQ,
    BRT_SP_FIQ,
    BRT_LR_FIQ,

    BRT_LR_IRQ,
    BRT_SP_IRQ,
    BRT_LR_SVC,
    BRT_SP_SVC,
    BRT_LR_ABT,
    BRT_SP_ABT,
    BRT_LR_UND,
    BRT_SP_UND,

    BRT_LR_MON,
    BRT_SP_MON,
    BRT_ELR_HYP,
    BRT_SP_HYP,

    BRT_SPSR_IRQ,
    BRT_SPSR_SVC,

    BRT_COUNT

} BankedRegisterTarget;


/* Indique le type défini pour une représentation d'un registre de banque ARMv7. */
GType g_armv7_banked_register_get_type(void);

/* Crée une réprésentation de registre de banque ARMv7. */
GArchRegister *g_armv7_banked_register_new(uint8_t, uint8_t);

/* Fournit le registre de banque ciblé. */
BankedRegisterTarget g_armv7_banked_register_get_target(const GArmV7BankedRegister *);



/* ------------------------ GESTION SOUS FORME DE SINGLETONS ------------------------ */


/* Vide totalement le cache des registres de banque ARMv7. */
void clean_armv7_banked_register_cache(void);



#endif  /* _PLUGINS_ARM_V7_REGISTERS_BANKED_H */
