
/* Chrysalide - Outil d'analyse de fichiers binaires
 * symbol.h - prototypes pour la gestion des symboles dans un binaire
 *
 * Copyright (C) 2009-2019 Cyrille Bagard
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


#ifndef _FORMAT_SYMBOL_H
#define _FORMAT_SYMBOL_H


#include <glib-object.h>


#include "../glibext/linegen.h"



/* --------------------- FONCTIONNALITES BASIQUES POUR SYMBOLES --------------------- */


/* Types de symbole */
typedef enum _SymbolType
{
    STP_DATA,                               /* Données brutes              */
    STP_ROUTINE,                            /* Simple morceau de code      */
    STP_CODE_LABEL,                         /* Renvoi au sein de code      */
    STP_OBJECT,                             /* Objet quelconque            */
    STP_ENTRY_POINT,                        /* Morceau de code en entrée   */
    STP_RO_STRING,                          /* Chaîne d'origine            */
    STP_DYN_STRING,                         /* Chaîne créée ex-nihilo      */

    STP_COUNT

} SymbolType;

/* Visibilité du symbole */
typedef enum _SymbolStatus
{
    SSS_INTERNAL,                           /* Visibilité nulle            */
    SSS_EXPORTED,                           /* Disponibilité extérieure    */
    SSS_IMPORTED,                           /* Besoin interne              */
    SSS_DYNAMIC,                            /* Création durant l'analyse   */

    SSS_COUNT

} SymbolStatus;

/* Indications supplémentaires liées aux symboles */

#define SFL_USER_BIT 1

typedef enum _SymbolFlag
{
    SFL_NONE          = (0 << 0),           /* Aucune propriété            */
    SFL_HAS_NM_PREFIX = (1 << 0),           /* Indication de nature        */

    SFL_LOW_USER      = (1 << SFL_USER_BIT),/* Premier bit disponible      */
    SFL_HIGH_USER     = (1 << 7),           /* Dernier bit disponible      */

} SymbolFlag;


#define G_TYPE_BIN_SYMBOL            g_binary_symbol_get_type()
#define G_BIN_SYMBOL(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_BIN_SYMBOL, GBinSymbol))
#define G_IS_BIN_SYMBOL(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_BIN_SYMBOL))
#define G_BIN_SYMBOL_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_BIN_SYMBOL, GBinSymbolClass))
#define G_IS_BIN_SYMBOL_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_BIN_SYMBOL))
#define G_BIN_SYMBOL_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_BIN_SYMBOL, GBinSymbolClass))


/* Symbole d'exécutable (instance) */
typedef struct _GBinSymbol GBinSymbol;

/* Symbole d'exécutable (classe) */
typedef struct _GBinSymbolClass GBinSymbolClass;


/* Indique le type défini pour un symbole d'exécutable. */
GType g_binary_symbol_get_type(void);

/* Crée un nouveau symbole d'exécutable. */
GBinSymbol *g_binary_symbol_new(const mrange_t *, SymbolType);

/* Compare deux symboles d'exécutable selon leurs propriétés. */
int g_binary_symbol_cmp(const GBinSymbol * const *, const GBinSymbol * const *);

/* Compare un symbole et une localisation. */
int g_binary_symbol_cmp_with_vmpa(const GBinSymbol *, const vmpa2t *);

/* Définit la couverture physique / en mémoire d'un symbole. */
void g_binary_symbol_set_range(GBinSymbol *, const mrange_t *);

/* Fournit l'emplacement où se situe un symbole. */
const mrange_t *g_binary_symbol_get_range(const GBinSymbol *);

/* Définit le type du symbole. */
void g_binary_symbol_set_stype(GBinSymbol *, SymbolType);

/* Fournit le type du symbole. */
SymbolType g_binary_symbol_get_stype(const GBinSymbol *);

/* Définit la visibilité du symbole. */
void g_binary_symbol_set_status(GBinSymbol *, SymbolStatus);

/* Fournit la visibilité du symbole. */
SymbolStatus g_binary_symbol_get_status(const GBinSymbol *);

/* Ajoute une information complémentaire à un symbole. */
bool g_binary_symbol_set_flag(GBinSymbol *, SymbolFlag);

/* Retire une information complémentaire à un symbole. */
bool g_binary_symbol_unset_flag(GBinSymbol *, SymbolFlag);

/* Détermine si un symbole possède un fanion particulier. */
bool g_binary_symbol_has_flag(const GBinSymbol *, SymbolFlag);

/* Fournit les particularités du symbole. */
SymbolFlag g_binary_symbol_get_flags(const GBinSymbol *);

/* Fournit le préfixe compatible avec une sortie "nm". */
bool g_binary_symbol_get_nm_prefix(const GBinSymbol *, char *);

/* Définit le préfixe compatible avec une sortie "nm". */
void g_binary_symbol_set_nm_prefix(const GBinSymbol *, char);

/* Fournit une étiquette pour viser un symbole. */
char *g_binary_symbol_get_label(const GBinSymbol *);

/* Définit un autre nom pour le symbole. */
void g_binary_symbol_set_alt_label(GBinSymbol *, const char *);



/* ------------------------ OFFRE DE CAPACITES DE GENERATION ------------------------ */


/* Détermine si un symbole pour faire office de générateur. */
GLineGenerator *g_binary_symbol_produce_label(GBinSymbol *);



#endif  /* _FORMAT_SYMBOL_H */
