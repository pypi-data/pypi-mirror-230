
/* Chrysalide - Outil d'analyse de fichiers binaires
 * method.h - prototypes pour la manipulation des methodes du format DEX
 *
 * Copyright (C) 2017-2019 Cyrille Bagard
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


#ifndef _PLUGINS_DEX_METHOD_H
#define _PLUGINS_DEX_METHOD_H


#include <glib-object.h>


#include <analysis/routine.h>


#include "dex_def.h"
#include "format.h"



#define G_TYPE_DEX_METHOD            (g_dex_method_get_type())
#define G_DEX_METHOD(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_DEX_METHOD, GDexMethod))
#define G_DEX_METHOD_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DEX_METHOD, GDexMethodClass))
#define G_IS_DEX_METHOD(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_DEX_METHOD))
#define G_IS_DEX_METHOD_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DEX_METHOD))
#define G_DEX_METHOD_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DEX_METHOD, GDexMethodClass))



/* Methode issue du code source (instance) */
typedef struct _GDexMethod GDexMethod;

/* Methode issue du code source (classe) */
typedef struct _GDexMethodClass GDexMethodClass;


/* Détermination des variables */
typedef enum _DexVariableIndex
{
    /* Indices... */

    DVI_LOCAL       = (1 << 29),
    DVI_THIS        = (1 << 30),
    DVI_ARGUMENT    = (1 << 31)

} DexVariableIndex;

#define DVI_INDEX(v) (v & ~(7 << 29))


/* Détermine le type d'une methode issue du code source. */
GType g_dex_method_get_type(void);

/* Crée une nouvelle représentation de methode issue de code. */
GDexMethod *g_dex_method_new_defined(GDexFormat *, const encoded_method *, uleb128_t *);

/* Crée une nouvelle représentation de methode vide. */
GDexMethod *g_dex_method_new_callable(GDexFormat *, const method_id_item *);

/* Fournit les identifiants Dex concernant la méthode. */
const method_id_item *g_dex_method_get_dex_id_item(const GDexMethod *);

/* Fournit les indications Dex concernant la méthode. */
const encoded_method *g_dex_method_get_dex_info(const GDexMethod *);

/* Indique si du code est rattaché à une méthode Dex. */
bool g_dex_method_has_dex_body(const GDexMethod *);

/* Fournit les indications Dex relatives au corps de la méthode. */
const code_item *g_dex_method_get_dex_body(const GDexMethod *);

/* Fournit la routine Chrysalide correspondant à la méthode. */
GBinRoutine *g_dex_method_get_routine(const GDexMethod *);

/* Intègre la méthode en tant que portion de code. */
void g_dex_method_include_as_portion(const GDexMethod *, GExeFormat *);

/* Indique la position de la méthode au sein du binaire. */
bool g_dex_method_get_offset(const GDexMethod *method, phys_t *);

/* Fournit des indications sur la nature d'une variable donnée. */
DexVariableIndex g_dex_method_get_variable(const GDexMethod *, uint32_t);



#endif  /* _PLUGINS_DEX_METHOD_H */
