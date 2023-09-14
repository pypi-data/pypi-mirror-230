
/* Chrysalide - Outil d'analyse de fichiers binaires
 * lang.h - prototypes pour les traductions en langages de haut niveau
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


#ifndef _ANALYSIS_HUMAN_LANG_H
#define _ANALYSIS_HUMAN_LANG_H


#include <glib-object.h>



#define G_TYPE_CODING_LANGUAGE              g_coding_language_get_type()
#define G_CODING_LANGUAGE(obj)              (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_CODING_LANGUAGE, GCodingLanguage))
#define G_IS_CODING_LANGUAGE(obj)           (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_CODING_LANGUAGE))
#define G_CODING_LANGUAGE_CLASS(klass)      (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_CODING_LANGUAGE, GCodingLanguageClass))
#define G_IS_CODING_LANGUAGE_CLASS(klass)   (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_CODING_LANGUAGE))
#define G_CODING_LANGUAGE_GET_CLASS(obj)    (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_CODING_LANGUAGE, GCodingLanguageClass))


/* Traduction générique en langage humain (instance) */
typedef struct _GCodingLanguage GCodingLanguage;

/* Traduction générique en langage humain (classe) */
typedef struct _GCodingLanguageClass GCodingLanguageClass;


/* Indique le type défini pour une traduction en langage humain. */
GType g_coding_language_get_type(void);

/* Complète du texte pour en faire un vrai commentaire. */
void g_coding_language_encapsulate_comment(const GCodingLanguage *, char **);

/* Complète du texte pour en faire de vrais commentaires. */
void g_coding_language_encapsulate_comments(const GCodingLanguage *, char ***, size_t *);



#endif  /* _ANALYSIS_HUMAN_LANG_H */
