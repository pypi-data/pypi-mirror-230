
/* Chrysalide - Outil d'analyse de fichiers binaires
 * rev.h - prototypes pour la transormation via inversement d'une séquence d'octets
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


#ifndef _ANALYSIS_SCAN_PATTERNS_MODIFIERS_REV_H
#define _ANALYSIS_SCAN_PATTERNS_MODIFIERS_REV_H


#include <glib-object.h>


#include "../modifier.h"



#define G_TYPE_SCAN_REVERSE_MODIFIER            g_scan_reverse_modifier_get_type()
#define G_SCAN_REVERSE_MODIFIER(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_REVERSE_MODIFIER, GScanReverseModifier))
#define G_IS_SCAN_REVERSE_MODIFIER(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_REVERSE_MODIFIER))
#define G_SCAN_REVERSE_MODIFIER_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_REVERSE_MODIFIER, GScanReverseModifierClass))
#define G_IS_SCAN_REVERSE_MODIFIER_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_REVERSE_MODIFIER))
#define G_SCAN_REVERSE_MODIFIER_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_REVERSE_MODIFIER, GScanReverseModifierClass))


/* Transormation via inversement d'une séquence d'octets (instance) */
typedef GScanTokenModifier GScanReverseModifier;

/* Transormation via inversement d'une séquence d'octets (classe) */
typedef GScanTokenModifierClass GScanReverseModifierClass;


/* Indique le type défini pour une transormation via inversement d'une séquence d'octets. */
GType g_scan_reverse_modifier_get_type(void);

/* Construit un modificateur livrant des octets inversés. */
GScanTokenModifier *g_scan_reverse_modifier_new(void);



#endif  /* _ANALYSIS_SCAN_PATTERNS_MODIFIERS_REV_H */
