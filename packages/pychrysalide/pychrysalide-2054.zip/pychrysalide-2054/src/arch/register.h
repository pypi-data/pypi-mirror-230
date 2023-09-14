
/* Chrysalide - Outil d'analyse de fichiers binaires
 * register.h - prototypes pour les aides auxiliaires relatives aux registres Dalvik
 *
 * Copyright (C) 2012-2018 Cyrille Bagard
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


#ifndef _ARCH_REGISTER_H
#define _ARCH_REGISTER_H


#include <glib-object.h>
#include <stdbool.h>


#include "../glibext/bufferline.h"



/* ---------------------------- PUR REGISTRE DU MATERIEL ---------------------------- */


#define G_TYPE_ARCH_REGISTER            g_arch_register_get_type()
#define G_ARCH_REGISTER(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_ARCH_REGISTER, GArchRegister))
#define G_IS_ARCH_REGISTER(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_ARCH_REGISTER))
#define G_ARCH_REGISTER_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ARCH_REGISTER, GArchRegisterClass))
#define G_IS_ARCH_REGISTER_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ARCH_REGISTER))
#define G_ARCH_REGISTER_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ARCH_REGISTER, GArchRegisterClass))


/* Représentation d'un registre (instance) */
typedef struct _GArchRegister GArchRegister;

/* Représentation d'un registre (classe) */
typedef struct _GArchRegisterClass GArchRegisterClass;


/* Indique le type défini pour une représentation d'un registre. */
GType g_arch_register_get_type(void);

/* Produit une empreinte à partir d'un registre. */
guint g_arch_register_hash(const GArchRegister *);

/* Compare un registre avec un autre. */
int g_arch_register_compare(const GArchRegister *, const GArchRegister *);

/* Traduit un registre en version humainement lisible. */
void g_arch_register_print(const GArchRegister *, GBufferLine *);

/* Indique si le registre correspond à ebp ou similaire. */
bool g_arch_register_is_base_pointer(const GArchRegister *);

/* Indique si le registre correspond à esp ou similaire. */
bool g_arch_register_is_stack_pointer(const GArchRegister *);



#endif  /* _ARCH_REGISTER_H */
