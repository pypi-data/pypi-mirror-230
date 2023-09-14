
/* Chrysalide - Outil d'analyse de fichiers binaires
 * pool.h - prototypes pour l'extraction des informations issues des tables globales
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


#ifndef _PLUGINS_DEX_POOL_H
#define _PLUGINS_DEX_POOL_H


#include <analysis/routine.h>
#include <glibext/delayed.h>


#include "class.h"
#include "format.h"
#include "method.h"



#define G_TYPE_DEX_POOL            (g_dex_pool_get_type())
#define G_DEX_POOL(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_DEX_POOL, GDexPool))
#define G_DEX_POOL_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DEX_POOL, GDexPoolClass))
#define G_IS_DEX_POOL(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_DEX_POOL))
#define G_IS_DEX_POOL_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DEX_POOL))
#define G_DEX_POOL_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DEX_POOL, GDexPoolClass))


/* Table des ressources pour format Dex (instance) */
typedef struct _GDexPool GDexPool;

/* Table des ressources pour format Dex (classe) */
typedef struct _GDexPoolClass GDexPoolClass;


/* Détermine le type d'une table des ressources pour format Dex. */
GType g_dex_pool_get_type(void);

/* Crée une nouvelle table de ressources pour format Dex. */
GDexPool *g_dex_pool_new(GDexFormat *);

/* Charge en mémoire l'ensemble des chaînes du format DEX. */
bool g_dex_pool_load_all_string_symbols(GDexPool *, wgroup_id_t, GtkStatusStack *);

/* Compte le nombre de chaînes de caractères dans une table DEX. */
uint32_t g_dex_pool_count_strings(const GDexPool *);

/* Extrait une chaîne de caractères d'une table DEX. */
const char *g_dex_pool_get_string(const GDexPool *, uint32_t, bool *, mrange_t *);

/* Extrait un symbole de chaîne d'une table DEX. */
GBinSymbol *g_dex_pool_get_string_symbol(GDexPool *, uint32_t);

/* Charge en mémoire l'ensemble des types du format DEX. */
bool g_dex_pool_load_all_types(GDexPool *, wgroup_id_t, GtkStatusStack *);

/* Compte le nombre de types dans une table DEX. */
uint32_t g_dex_pool_count_types(const GDexPool *);

/* Reconstitue les éléments bruts d'un type Dex. */
bool g_dex_pool_get_raw_type(GDexPool *, uint32_t, type_id_item *);

/* Extrait une représentation de type d'une table DEX. */
GDataType *g_dex_pool_get_type_(GDexPool *, uint32_t);

/* Charge en mémoire l'ensemble des champs du format DEX. */
bool g_dex_pool_load_all_fields(GDexPool *, wgroup_id_t, GtkStatusStack *);

/* Compte le nombre de champs dans une table DEX. */
uint32_t g_dex_pool_count_fields(const GDexPool *);

/* Reconstitue les éléments bruts d'un champ Dex. */
bool g_dex_pool_get_raw_field(GDexPool *, uint32_t, field_id_item *);

/* Extrait une représentation de champ d'une table DEX. */
GBinVariable *g_dex_pool_get_field(GDexPool *, uint32_t);

/* Compte le nombre de prototypes dans une table DEX. */
uint32_t g_dex_pool_count_prototypes(const GDexPool *);

/* Reconstitue les éléments bruts d'une routine Dex. */
bool g_dex_pool_get_raw_prototype(GDexPool *, uint32_t, proto_id_item *);

/* Extrait une représentation de routine d'une table DEX. */
GBinRoutine *g_dex_pool_get_prototype(GDexPool *, uint32_t);

/* Charge toutes les classes listées dans le contenu binaire. */
bool g_dex_pool_load_all_methods(GDexPool *, wgroup_id_t, GtkStatusStack *);

/* Compte le nombre de méthodes dans une table DEX. */
uint32_t g_dex_pool_count_methods(const GDexPool *);

/* Reconstitue les éléments bruts d'une méthode Dex. */
bool g_dex_pool_get_raw_method(GDexPool *, uint32_t, method_id_item *);

/* Extrait une représentation de méthode d'une table DEX. */
GDexMethod *g_dex_pool_get_method(GDexPool *, uint32_t);

/* Charge toutes les classes listées dans le contenu binaire. */
bool g_dex_pool_load_all_classes(GDexPool *, wgroup_id_t, GtkStatusStack *);

/* Dénombre le nombre de classes trouvées. */
uint32_t g_dex_pool_count_classes(const GDexPool *);

/* Reconstitue les éléments bruts d'une classe Dex. */
bool g_dex_pool_get_raw_class(GDexPool *, uint32_t, class_def_item *);

/* Extrait une représentation de classe d'une table DEX. */
GDexClass *g_dex_pool_get_class(GDexPool *, uint32_t);



#endif  /* _PLUGINS_DEX_POOL_H */
