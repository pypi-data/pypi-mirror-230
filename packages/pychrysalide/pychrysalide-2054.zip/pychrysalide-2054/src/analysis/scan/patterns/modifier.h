
/* Chrysalide - Outil d'analyse de fichiers binaires
 * modifier.h - prototypes pour la modification d'une séquence d'octets pour un motif recherché
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _ANALYSIS_SCAN_MODIFIER_H
#define _ANALYSIS_SCAN_MODIFIER_H


#include <glib-object.h>
#include <stdbool.h>


#include "../../../common/szstr.h"



#define G_TYPE_SCAN_TOKEN_MODIFIER            g_scan_token_modifier_get_type()
#define G_SCAN_TOKEN_MODIFIER(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_TOKEN_MODIFIER, GScanTokenModifier))
#define G_IS_SCAN_TOKEN_MODIFIER(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_TOKEN_MODIFIER))
#define G_SCAN_TOKEN_MODIFIER_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_TOKEN_MODIFIER, GScanTokenModifierClass))
#define G_IS_SCAN_TOKEN_MODIFIER_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_TOKEN_MODIFIER))
#define G_SCAN_TOKEN_MODIFIER_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_TOKEN_MODIFIER, GScanTokenModifierClass))


/* Transformation d'une séquence d'octets en une ou plusieurs autres formes (instance) */
typedef struct _GScanTokenModifier GScanTokenModifier;

/* Transformation d'une séquence d'octets en une ou plusieurs autres formes (classe) */
typedef struct _GScanTokenModifierClass GScanTokenModifierClass;


/* Indique le type défini pour une transformation d'une séquence d'octets. */
GType g_scan_token_modifier_get_type(void);

/* Fournit le nom d'appel d'un modificateur pour motif. */
char *g_scan_token_modifier_get_name(const GScanTokenModifier *);

/* Transforme une séquence d'octets pour motif de recherche. */
bool g_scan_token_modifier_transform(const GScanTokenModifier *, const sized_binary_t *, sized_binary_t **, size_t *);



#endif  /* _ANALYSIS_SCAN_MODIFIER_H */
