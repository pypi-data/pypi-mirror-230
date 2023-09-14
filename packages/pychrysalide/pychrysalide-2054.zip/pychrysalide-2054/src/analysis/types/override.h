
/* Chrysalide - Outil d'analyse de fichiers binaires
 * override.h - prototypes pour la manipulation des types pointant sur une fonction virtuelle
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


#ifndef _ANALYSIS_TYPES_OVERRIDE_H
#define _ANALYSIS_TYPES_OVERRIDE_H


#include <glib-object.h>
#include <stdbool.h>
#include <sys/types.h>


#include "../type.h"



#define G_TYPE_OVERRIDE_TYPE            g_override_type_get_type()
#define G_OVERRIDE_TYPE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_OVERRIDE_TYPE, GOverrideType))
#define G_IS_OVERRIDE_TYPE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_OVERRIDE_TYPE))
#define G_OVERRIDE_TYPE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_OVERRIDE_TYPE, GOverrideTypeClass))
#define G_IS_OVERRIDE_TYPE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_OVERRIDE_TYPE))
#define G_OVERRIDE_TYPE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_OVERRIDE_TYPE, GOverrideTypeClass))


/* Description de fonction virtuelle (instance) */
typedef struct _GOverrideType GOverrideType;

/* Description de fonction virtuelle (classe) */
typedef struct _GOverrideTypeClass GOverrideTypeClass;


/* Indications de sauts */
typedef struct _call_offset_t
{
    ssize_t values[2];                      /* Décalages à appliquer       */
    bool virtual;                           /* Appel virtuel ?             */

} call_offset_t;


/* Indique le type défini pour une fonction virtuelle. */
GType g_override_type_get_type(void);

/* Crée une représentation de fonction virtuelle. */
GDataType *g_override_type_new(GDataType *, const call_offset_t *);

/* Crée une représentation de fonction virtuelle avec covariant. */
GDataType *g_override_type_new_with_covariant(GDataType *, const call_offset_t *, const call_offset_t *);

/* Fournit le type de base comportant la fonction virtuelle. */
GDataType *g_override_type_get_base(const GOverrideType *);

/* Fournit les décalages appliquée pour une fonction virtuelle. */
bool g_override_type_get_offsets(const GOverrideType *, call_offset_t *, call_offset_t *);



#endif  /* _ANALYSIS_TYPES_OVERRIDE_H */
