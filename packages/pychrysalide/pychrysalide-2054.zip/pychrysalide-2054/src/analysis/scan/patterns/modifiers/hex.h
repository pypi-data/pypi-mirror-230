
/* Chrysalide - Outil d'analyse de fichiers binaires
 * hex.h - prototypes pour la transformation en version hexadécimale d'une séquence d'octets
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


#ifndef _ANALYSIS_SCAN_PATTERNS_MODIFIERS_HEX_H
#define _ANALYSIS_SCAN_PATTERNS_MODIFIERS_HEX_H


#include <glib-object.h>


#include "../modifier.h"



#define G_TYPE_SCAN_HEX_MODIFIER            g_scan_hex_modifier_get_type()
#define G_SCAN_HEX_MODIFIER(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_HEX_MODIFIER, GScanHexModifier))
#define G_IS_SCAN_HEX_MODIFIER(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_HEX_MODIFIER))
#define G_SCAN_HEX_MODIFIER_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_HEX_MODIFIER, GScanHexModifierClass))
#define G_IS_SCAN_HEX_MODIFIER_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_HEX_MODIFIER))
#define G_SCAN_HEX_MODIFIER_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_HEX_MODIFIER, GScanHexModifierClass))


/* Transformation d'une séquence d'octets dans sa version hexadécimale (instance) */
typedef GScanTokenModifier GScanHexModifier;

/* Transformation d'une séquence d'octets dans sa version hexadécimale (classe) */
typedef GScanTokenModifierClass GScanHexModifierClass;


/* Indique le type défini pour une transformation d'une séquence d'octets dans sa version hexadécimale. */
GType g_scan_hex_modifier_get_type(void);

/* Construit un modificateur fournistant une vue hexadécimale. */
GScanTokenModifier *g_scan_hex_modifier_new(void);



#endif  /* _ANALYSIS_SCAN_PATTERNS_MODIFIERS_HEX_H */
