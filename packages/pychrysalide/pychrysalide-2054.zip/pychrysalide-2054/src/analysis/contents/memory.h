
/* Chrysalide - Outil d'analyse de fichiers binaires
 * memory.h - prototypes pour le chargement de données binaires à partir de la mémoire
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


#ifndef _ANALYSIS_CONTENTS_MEMORY_H
#define _ANALYSIS_CONTENTS_MEMORY_H


#include <glib-object.h>


#include "../content.h"



#define G_TYPE_MEMORY_CONTENT            (g_memory_content_get_type())
#define G_MEMORY_CONTENT(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_MEMORY_CONTENT, GMemoryContent))
#define G_IS_MEMORY_CONTENT(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_MEMORY_CONTENT))
#define G_MEMORY_CONTENT_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_MEMORY_CONTENT, GMemoryContentClass))
#define G_IS_MEMORY_CONTENT_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_MEMORY_CONTENT))
#define G_MEMORY_CONTENT_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_MEMORY_CONTENT, GMemoryContentClass))


/* Contenu de données binaires résidant en mémoire (instance) */
typedef struct _GMemoryContent GMemoryContent;

/* Contenu de données binaires résidant en mémoire (classe) */
typedef struct _GMemoryContentClass GMemoryContentClass;


/* Indique le type défini par la GLib pour les contenus de données en mémoire. */
GType g_memory_content_get_type(void);

/* Charge en mémoire le contenu de données brutes. */
GBinContent *g_memory_content_new(const bin_t *, phys_t);



#endif  /* _ANALYSIS_CONTENTS_MEMORY_H */
