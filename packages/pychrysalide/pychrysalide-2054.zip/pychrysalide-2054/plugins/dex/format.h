
/* Chrysalide - Outil d'analyse de fichiers binaires
 * format.h - prototypes pour le support du format DEX
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


#ifndef _PLUGINS_DEX_FORMAT_H
#define _PLUGINS_DEX_FORMAT_H


#include <glib-object.h>
#include <stdbool.h>
#include <sys/types.h>


#include <analysis/content.h>
#include <format/executable.h>


#include "dex_def.h"



#define G_TYPE_DEX_FORMAT            g_dex_format_get_type()
#define G_DEX_FORMAT(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_DEX_FORMAT, GDexFormat))
#define G_IS_DEX_FORMAT(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_DEX_FORMAT))
#define G_DEX_FORMAT_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DEX_FORMAT, GDexFormatClass))
#define G_IS_DEX_FORMAT_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DEX_FORMAT))
#define G_DEX_FORMAT_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DEX_FORMAT, GDexFormatClass))


/* Format d'exécutable DEX (instance) */
typedef struct _GDexFormat GDexFormat;

/* Format d'exécutable DEX (classe) */
typedef struct _GDexFormatClass GDexFormatClass;


/* Valide un contenu comme étant un format Dex. */
bool check_dex_format(const GBinContent *);

/* Indique le type défini pour un format d'exécutable DEX. */
GType g_dex_format_get_type(void);

/* Prend en charge un nouveau format DEX. */
GExeFormat *g_dex_format_new(GBinContent *);

/* Présente l'en-tête DEX du format chargé. */
const dex_header *g_dex_format_get_header(const GDexFormat *);

/* Redéfinition : table des ressources pour format Dex (instance) */
typedef struct _GDexPool GDexPool;

/* Fournit la table des ressources associée au format Dex. */
GDexPool *g_dex_format_get_pool(const GDexFormat *);



#endif  /* _PLUGINS_DEX_FORMAT_H */
