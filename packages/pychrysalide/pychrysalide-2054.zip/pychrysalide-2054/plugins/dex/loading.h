
/* Chrysalide - Outil d'analyse de fichiers binaires
 * loading.h - prototypes pour les chargements parallèles des éléments de la table globale du format Dex
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


#ifndef _PLUGINS_DEX_LOADING_H
#define _PLUGINS_DEX_LOADING_H


#include <glib-object.h>
#include <stdbool.h>
#include <stdint.h>


#include <glibext/notifier.h>



#define G_TYPE_DEX_LOADING            g_dex_loading_get_type()
#define G_DEX_LOADING(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_DEX_LOADING, GDexLoading))
#define G_IS_DEX_LOADING(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_DEX_LOADING))
#define G_DEX_LOADING_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DEX_LOADING, GDexLoadingClass))
#define G_IS_DEX_LOADING_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DEX_LOADING))
#define G_DEX_LOADING_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DEX_LOADING, GDexLoadingClass))


/* Fraction de loading à limiter (instance) */
typedef struct _GDexLoading GDexLoading;

/* Fraction de loading à limiter (classe) */
typedef struct _GDexLoadingClass GDexLoadingClass;


/* Extrait une représentation générique d'une table Dex. */
typedef GObject * (* dex_loading_cb) (GObject *, uint32_t);


/* Indique le type défini pour les tâches de chargements pour format DEX. */
GType g_dex_loading_get_type(void);

/* Crée une tâche de chargement pour DEX différée. */
GDexLoading *g_dex_loading_new(GObject *, uint32_t, uint32_t, activity_id_t, dex_loading_cb, bool *);



#endif  /* _PLUGINS_DEX_LOADING_H */
