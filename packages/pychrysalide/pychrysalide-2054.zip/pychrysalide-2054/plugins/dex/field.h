
/* Chrysalide - Outil d'analyse de fichiers binaires
 * field.h - prototypes pour la manipulation des champs de classe du format DEX
 *
 * Copyright (C) 2018-2019 Cyrille Bagard
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


#ifndef _PLUGINS_DEX_FIELD_H
#define _PLUGINS_DEX_FIELD_H


#include <glib-object.h>


#include <analysis/routine.h>


#include "dex_def.h"
#include "format.h"



#define G_TYPE_DEX_FIELD            (g_dex_field_get_type())
#define G_DEX_FIELD(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_DEX_FIELD, GDexField))
#define G_DEX_FIELD_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DEX_FIELD, GDexFieldClass))
#define G_IS_DEX_FIELD(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_DEX_FIELD))
#define G_IS_DEX_FIELD_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DEX_FIELD))
#define G_DEX_FIELD_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DEX_FIELD, GDexFieldClass))


/* Champ d'une classe Dex (instance) */
typedef struct _GDexField GDexField;

/* Champ d'une classe Dex (classe) */
typedef struct _GDexFieldClass GDexFieldClass;


/* Détermine le type d'une fielde issue du code source. */
GType g_dex_field_get_type(void);

/* Crée une nouvelle représentation de champ de classe. */
GDexField *g_dex_field_new(GDexFormat *, const encoded_field *, uleb128_t *);

/* Fournit les indications Dex concernant le champ de classe. */
const encoded_field *g_dex_field_get_dex_info(const GDexField *);

/* Fournit la variable Chrysalide correspondant au champ. */
GBinVariable *g_dex_field_get_variable(const GDexField *);



#endif  /* _PLUGINS_DEX_FIELD_H */
