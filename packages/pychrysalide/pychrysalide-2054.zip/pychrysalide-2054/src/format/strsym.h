
/* Chrysalide - Outil d'analyse de fichiers binaires
 * strsym.h - prototypes pour la gestion des chaînes dans un binaire
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


#ifndef _FORMAT_STRSYM_H
#define _FORMAT_STRSYM_H


#include <glib-object.h>


#include "known.h"
#include "format.h"
#include "symbol.h"



/* ----------------------- VITRINE POUR CHAINES DE CARACTERES ----------------------- */


/* Types de chaînes */
typedef enum _StringEncodingType
{
    SET_NONE,                               /* Valeur d'initialisation     */

    SET_ASCII,                              /* Format brut                 */
    SET_UTF_8,                              /* Format UTF-8                */
    SET_MUTF_8,                             /* Format UTF-8 modifié        */

    SET_GUESS,                              /* Détection automatique       */

} StringEncodingType;


#define G_TYPE_STR_SYMBOL            g_string_symbol_get_type()
#define G_STR_SYMBOL(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_STR_SYMBOL, GStrSymbol))
#define G_IS_STR_SYMBOL(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_STR_SYMBOL))
#define G_STR_SYMBOL_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_STR_SYMBOL, GStrSymbolClass))
#define G_IS_STR_SYMBOL_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_STR_SYMBOL))
#define G_STR_SYMBOL_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_STR_SYMBOL, GStrSymbolClass))


/*/* Symbole pour chaîne de caractères (instance) */
typedef struct _GStrSymbol GStrSymbol;

/* Symbole pour chaîne de caractères (classe) */
typedef struct _GStrSymbolClass GStrSymbolClass;


/* Indique le type défini pour un symbole d'exécutable. */
GType g_string_symbol_get_type(void);

/* Crée un nouveau symbole pour chaîne de caractères. */
GBinSymbol *g_string_symbol_new_read_only(StringEncodingType, GKnownFormat *, const mrange_t *);

/* Réalise la complète initialisation d'unsymbole pour chaîne. */
void g_string_symbol_init_read_only(GStrSymbol *, StringEncodingType, GKnownFormat *, const mrange_t *);

/* Crée un nouveau symbole pour chaîne de caractères. */
GBinSymbol *g_string_symbol_new_dynamic(StringEncodingType, const char *, const vmpa2t *);

/* Réalise la complète initialisation d'unsymbole pour chaîne. */
void g_string_symbol_init_dynamic(GStrSymbol *, StringEncodingType, const char *, const vmpa2t *);

/* Définit si une chaîne de caractères est liée au format. */
void g_string_symbol_set_structural(GStrSymbol *, bool);

/* Indique si une chaîne de caractères est liée au format. */
bool g_string_symbol_is_structural(const GStrSymbol *);

/* Fournit l'encodage d'une chaîne de caractères. */
StringEncodingType g_string_symbol_get_encoding(const GStrSymbol *);

/* Fournit la chaîne brute de caractères du symbole. */
const char *g_string_symbol_get_raw(const GStrSymbol *, size_t *);

/* Fournit la chaîne de caractères du symbole. */
const char *g_string_symbol_get_utf8(const GStrSymbol *, size_t *);

/* Construit une désignation pour chaîne de caractères. */
bool g_string_symbol_build_label(GStrSymbol *, GBinFormat *);



#endif  /* _FORMAT_STRSYM_H */
