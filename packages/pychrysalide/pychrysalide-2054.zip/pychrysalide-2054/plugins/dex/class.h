
/* Chrysalide - Outil d'analyse de fichiers binaires
 * class.h - prototypes pour la manipulation des classes du format DEX
 *
 * Copyright (C) 2017-2020 Cyrille Bagard
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


#ifndef _PLUGINS_DEX_CLASS_H
#define _PLUGINS_DEX_CLASS_H


#include <glib-object.h>


#include "field.h"
#include "format.h"
#include "method.h"



#define G_TYPE_DEX_CLASS            (g_dex_class_get_type())
#define G_DEX_CLASS(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_DEX_CLASS, GDexClass))
#define G_DEX_CLASS_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DEX_CLASS, GDexClassClass))
#define G_IS_DEX_CLASS(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_DEX_CLASS))
#define G_IS_DEX_CLASS_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DEX_CLASS))
#define G_DEX_CLASS_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DEX_CLASS, GDexClassClass))



/* Classe issue du code source (instance) */
typedef struct _GDexClass GDexClass;

/* Classe issue du code source (classe) */
typedef struct _GDexClassClass GDexClassClass;


/* Détermine le type d'une classe issue du code source. */
GType g_dex_class_get_type(void);

/* Crée une nouvelle représentation de classe issue de code. */
GDexClass *g_dex_class_new(GDexFormat *, const class_def_item *);

/* Fournit la définition brute d'une classe. */
const class_def_item *g_dex_class_get_definition(const GDexClass *);

/* Fournit la définition brute des données d'une classe. */
const class_data_item *g_dex_class_get_data(const GDexClass *);

/* Indique le type Android d'une classe. */
GDataType *g_dex_class_get_class_type(const GDexClass *);

/* Indique le type Android parent d'une classe. */
GDataType *g_dex_class_get_superclass_type(const GDexClass *);

/* Indique le type Android des interfaces d'une classe. */
GDataType **g_dex_class_get_interface_types(const GDexClass *, size_t *);

/* Dénombre les champs de classe chargés d'une classe donnée. */
size_t g_dex_class_count_fields(const GDexClass *, bool);

/* Fournit un champ chargé correspondant à une classe donnée. */
GDexField *g_dex_class_get_field(const GDexClass *, bool, size_t);

/* Dénombre les méthodes chargées d'un type donné. */
size_t g_dex_class_count_methods(const GDexClass *, bool);

/* Fournit une méthode chargée correspondant à un type donné. */
GDexMethod *g_dex_class_get_method(const GDexClass *, bool, size_t);

/* Etablit une liste de tous les symboles d'une classe. */
bool g_dex_class_get_collect_symbols(const GDexClass *, GBinSymbol ***, size_t *);

/* Intègre la méthode en tant que portion de code. */
void g_dex_class_include_as_portion(const GDexClass *, GExeFormat *);

/* Retrouve si possible la méthode associée à une adresse. */
GDexMethod *g_dex_class_find_method_by_address(const GDexClass *, vmpa_t);

/* Retrouve si possible le nom du fichier source d'une classe. */
const char *g_dex_class_get_source_file(const GDexClass *);



#endif  /* _PLUGINS_DEX_CLASS_H */
