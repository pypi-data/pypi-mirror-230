
/* Chrysalide - Outil d'analyse de fichiers binaires
 * registers.h - prototypes pour les aides auxiliaires relatives aux registres Dalvik
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


#ifndef _PLUGINS_DALVIK_REGISTERS_H
#define _PLUGINS_DALVIK_REGISTERS_H


#include <glib-object.h>
#include <stdint.h>


#include <arch/register.h>



/* ------------------------- GESTION UNITAIRE DES REGISTRES ------------------------- */


#define G_TYPE_DALVIK_REGISTER            g_dalvik_register_get_type()
#define G_DALVIK_REGISTER(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_DALVIK_REGISTER, GDalvikRegister))
#define G_IS_DALVIK_REGISTER(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_DALVIK_REGISTER))
#define G_DALVIK_REGISTER_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DALVIK_REGISTER, GDalvikRegisterClass))
#define G_IS_DALVIK_REGISTER_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DALVIK_REGISTER))
#define G_DALVIK_REGISTER_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DALVIK_REGISTER, GDalvikRegisterClass))


/* Représentation d'un registre Dalvik (instance) */
typedef struct _GDalvikRegister GDalvikRegister;

/* Représentation d'un registre Dalvik (classe) */
typedef struct _GDalvikRegisterClass GDalvikRegisterClass;


/* Indique le type défini pour une représentation d'un registre Dalvik. */
GType g_dalvik_register_get_type(void);

/* Crée une réprésentation de registre Dalvik. */
GArchRegister *g_dalvik_register_new(uint16_t);

/* Fournit l'indice d'un registre Dalvik. */
uint16_t g_dalvik_register_get_index(const GDalvikRegister *);



/* ------------------------ GESTION SOUS FORME DE SINGLETONS ------------------------ */


/* Vide totalement le cache des registres Dalvik. */
void clean_dalvik_register_cache(void);



#endif  /* _PLUGINS_DALVIK_REGISTERS_H */
