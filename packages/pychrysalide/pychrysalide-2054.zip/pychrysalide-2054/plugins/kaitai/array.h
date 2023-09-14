
/* Chrysalide - Outil d'analyse de fichiers binaires
 * array.h - prototypes pour les données associées à un flux de données Kaitai
 *
 * Copyright (C) 2023 Cyrille Bagard
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


#ifndef PLUGINS_KAITAI_ARRAY_H
#define PLUGINS_KAITAI_ARRAY_H


#include <glib-object.h>
#include <stdbool.h>


#include <common/szstr.h>



/* expression.h : informations transportées par une expression */
typedef struct _resolved_value_t resolved_value_t;



#define G_TYPE_KAITAI_ARRAY            g_kaitai_array_get_type()
#define G_KAITAI_ARRAY(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_KAITAI_ARRAY, GKaitaiArray))
#define G_IS_KAITAI_ARRAY(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_KAITAI_ARRAY))
#define G_KAITAI_ARRAY_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_KAITAI_ARRAY, GKaitaiArrayClass))
#define G_IS_KAITAI_ARRAY_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_KAITAI_ARRAY))
#define G_KAITAI_ARRAY_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_KAITAI_ARRAY, GKaitaiArrayClass))


/* Tableau rassemblant des éléments divers (instance) */
typedef struct _GKaitaiArray GKaitaiArray;

/* Tableau rassemblant des éléments divers (classe) */
typedef struct _GKaitaiArrayClass GKaitaiArrayClass;


/* Indique le type défini pour un tableau rassemblant des éléments Kaitai. */
GType g_kaitai_array_get_type(void);

/* Constitue une amorce de tableau pour rassembler des éléments. */
GKaitaiArray *g_kaitai_array_new(void);

/* Dénombre le nombre d'éléments enregistrés. */
size_t g_kaitai_array_count_items(const GKaitaiArray *);

/* Intègre un élément supplémentaire dans un tableau Kaitai. */
void g_kaitai_array_append_item(GKaitaiArray *, const resolved_value_t *);

/* Fournit un élément ciblé dans un tableau Kaitai. */
bool g_kaitai_array_get_item(const GKaitaiArray *, size_t, resolved_value_t *);

/* Convertit un tableau d'éléments en séquence d'octets. */
bool g_kaitai_array_convert_to_bytes(const GKaitaiArray *, sized_string_t *);



#endif  /* PLUGINS_KAITAI_ARRAY_H */
