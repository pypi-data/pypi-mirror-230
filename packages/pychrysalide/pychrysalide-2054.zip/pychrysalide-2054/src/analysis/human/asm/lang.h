
/* Chrysalide - Outil d'analyse de fichiers binaires
 * lang.h - prototypes pour la traduction en language d'assembleur classique
 *
 * Copyright (C) 2016-2018 Cyrille Bagard
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


#ifndef _ANALYSIS_HUMAN_ASM_LANG_H
#define _ANALYSIS_HUMAN_ASM_LANG_H


#include <glib-object.h>


#include "../lang.h"



#define G_TYPE_ASM_LANGUAGE             g_asm_language_get_type()
#define G_ASM_LANGUAGE(obj)             (G_TYPE_CHECK_INSTANCE_CAST((obj), g_asm_language_get_type(), GAsmLanguage))
#define G_IS_ASM_LANGUAGE(obj)          (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_asm_language_get_type()))
#define G_ASM_LANGUAGE_CLASS(klass)     (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ASM_LANGUAGE, GAsmLanguageClass))
#define G_IS_ASM_LANGUAGE_CLASS(klass)  (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ASM_LANGUAGE))
#define G_ASM_LANGUAGE_GET_CLASS(obj)   (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ASM_LANGUAGE, GAsmLanguageClass))


/* Traduction d'éléments en language d'assembleur (instance) */
typedef struct _GAsmLanguage GAsmLanguage;

/* Traduction d'éléments en language d'assembleur (classe) */
typedef struct _GAsmLanguageClass GAsmLanguageClass;


/* Indique le type défini pour une traduction en langage d'assembleur. */
GType g_asm_language_get_type(void);

/* Crée une instance de traduction en langage d'assembleur. */
GCodingLanguage *g_asm_language_new(void);



#endif  /* _ANALYSIS_HUMAN_ASM_LANG_H */
