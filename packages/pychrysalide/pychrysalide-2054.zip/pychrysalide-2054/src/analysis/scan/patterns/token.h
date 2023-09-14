
/* Chrysalide - Outil d'analyse de fichiers binaires
 * token.h - prototypes pour les bribes de recherche textuelle
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


#ifndef _ANALYSIS_SCAN_PATTERNS_TOKEN_H
#define _ANALYSIS_SCAN_PATTERNS_TOKEN_H


#include <glib-object.h>


#include "backend.h"
#include "tokens/node.h"
#include "../matches/pending.h"



#define G_TYPE_STRING_TOKEN            g_string_token_get_type()
#define G_STRING_TOKEN(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_STRING_TOKEN, GStringToken))
#define G_IS_STRING_TOKEN(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_STRING_TOKEN))
#define G_STRING_TOKEN_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_STRING_TOKEN, GStringTokenClass))
#define G_IS_STRING_TOKEN_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_STRING_TOKEN))
#define G_STRING_TOKEN_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_STRING_TOKEN, GStringTokenClass))


/* Encadrement d'une bribe de recherche textuelle (instance) */
typedef struct _GStringToken GStringToken;

/* Encadrement d'une bribe de recherche textuelle (classe) */
typedef struct _GStringTokenClass GStringTokenClass;


/* Indique le type défini pour une bribe de recherche textuelle. */
GType g_string_token_get_type(void);

/* Indique si seuls des mots entiers sont retenus des analyses. */
bool g_string_token_target_fullword(const GStringToken *);

/* Détermine si le gestionnaire est à vocation privée. */
bool g_string_token_is_private(const GStringToken *);

/* Inscrit la définition d'un motif dans un moteur de recherche. */
bool g_string_token_enroll(GStringToken *, GScanContext *, GEngineBackend *, size_t);

/* Transforme les correspondances locales en trouvailles. */
void g_string_token_check(const GStringToken *, GScanContext *, GBinContent *, pending_matches_t *);



#endif  /* _ANALYSIS_SCAN_PATTERNS_TOKEN_H */
