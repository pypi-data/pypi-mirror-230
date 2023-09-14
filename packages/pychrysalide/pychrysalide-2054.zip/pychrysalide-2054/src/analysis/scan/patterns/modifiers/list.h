
/* Chrysalide - Outil d'analyse de fichiers binaires
 * list.h - prototypes pour la gestion d'une liste de transformateurs
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


#ifndef _ANALYSIS_SCAN_MODIFIERS_LIST_H
#define _ANALYSIS_SCAN_MODIFIERS_LIST_H


#include <glib-object.h>
#include <stdbool.h>


#include "../modifier.h"



#define G_TYPE_SCAN_MODIFIER_LIST            g_scan_modifier_list_get_type()
#define G_SCAN_MODIFIER_LIST(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_MODIFIER_LIST, GScanModifierList))
#define G_IS_SCAN_MODIFIER_LIST(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_MODIFIER_LIST))
#define G_SCAN_MODIFIER_LIST_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_MODIFIER_LIST, GScanModifierListClass))
#define G_IS_SCAN_MODIFIER_LIST_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_MODIFIER_LIST))
#define G_SCAN_MODIFIER_LIST_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_MODIFIER_LIST, GScanModifierListClass))


/* Liste de transformations d'une séquence d'octets (instance) */
typedef struct _GScanModifierList GScanModifierList;

/* Liste de transformations d'une séquence d'octets (classe) */
typedef struct _GScanModifierListClass GScanModifierListClass;


/* Indique le type défini pour une série de transformations d'octets. */
GType g_scan_modifier_list_get_type(void);

/* Construit une liste de modificateurs d'octets. */
GScanTokenModifier *g_scan_modifier_list_new(void);

/* Intègre un nouveau transformateur dans une liste. */
bool g_scan_modifier_list_add(GScanModifierList *, GScanTokenModifier *);

/* Indique le nombre de transformateurs intégrés dans la liste. */
size_t g_scan_modifier_list_count(const GScanModifierList *);

/* Fournit un transformateur donné de la liste. */
GScanTokenModifier *g_scan_modifier_list_get(const GScanModifierList *, size_t);



#endif  /* _ANALYSIS_SCAN_MODIFIERS_LIST_H */
