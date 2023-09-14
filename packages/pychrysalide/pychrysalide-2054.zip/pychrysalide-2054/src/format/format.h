
/* Chrysalide - Outil d'analyse de fichiers binaires
 * format.h - prototypes pour le support des différents formats binaires
 *
 * Copyright (C) 2009-2020 Cyrille Bagard
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


#ifndef _FORMAT_FORMAT_H
#define _FORMAT_FORMAT_H


#include <glib-object.h>
#include <stdbool.h>
#include <sys/types.h>


#include "symbol.h"
#include "../analysis/content.h"
#include "../arch/context.h"
#include "../glibext/delayed.h"
#include "../glibext/notifier.h"



/* Depuis ../mangling/demangler.h : Décodeur de désignations générique (instance) */
typedef struct _GCompDemangler GCompDemangler;

/* Indications supplémentaires liées aux formats */
typedef enum _FormatFlag
{
    FFL_NONE                = (0 << 0),     /* Aucune propriété            */
    FFL_RUN_IN_KERNEL_SPACE = (1 << 0),     /* Exécution en espace noyau   */

    FFL_MASK                = (1 << 1) - 1, /* Indication de nature        */

} FormatFlag;


#define G_TYPE_BIN_FORMAT            g_binary_format_get_type()
#define G_BIN_FORMAT(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_BIN_FORMAT, GBinFormat))
#define G_IS_BIN_FORMAT(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_BIN_FORMAT))
#define G_BIN_FORMAT_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_BIN_FORMAT, GBinFormatClass))
#define G_IS_BIN_FORMAT_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_BIN_FORMAT))
#define G_BIN_FORMAT_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_BIN_FORMAT, GBinFormatClass))


/* Format binaire générique (instance) */
typedef struct _GBinFormat GBinFormat;

/* Format binaire générique (classe) */
typedef struct _GBinFormatClass GBinFormatClass;


/* Indique le type défini pour un format binaire générique. */
GType g_binary_format_get_type(void);

/* Ajoute une information complémentaire à un format. */
bool g_binary_format_set_flag(GBinFormat *, FormatFlag);

/* Retire une information complémentaire à un format. */
bool g_binary_format_unset_flag(GBinFormat *, FormatFlag);

/* Détermine si un format possède un fanion particulier. */
bool g_binary_format_has_flag(const GBinFormat *, FormatFlag);

/* Fournit les particularités du format. */
FormatFlag g_binary_format_get_flags(const GBinFormat *);

/* Indique le boutisme employé par le format binaire analysé. */
SourceEndian g_binary_format_get_endianness(const GBinFormat *);

/* Enregistre une adresse comme début d'une zone de code. */
void g_binary_format_register_code_point(GBinFormat *, virt_t, DisassPriorityLevel);

/* Intègre dans un contexte les informations tirées d'un format. */
void g_binary_format_preload_disassembling_context(GBinFormat *, GProcContext *, GtkStatusStack *);

/* Définit les points de départ d'un contexte de désassemblage. */
void g_binary_format_activate_disassembling_context(GBinFormat *, GProcContext *, GtkStatusStack *);



/* ------------------------------ DECODAGE DE SYMBOLES ------------------------------ */


/* Fournit le décodeur de symboles privilégié pour un format. */
GCompDemangler *g_binary_format_get_demangler(const GBinFormat *);



/* ---------------------- RASSEMBLEMENT ET GESTION DE SYMBOLES ---------------------- */


/* Protège ou lève la protection de l'accès aux symboles. */
void g_binary_format_lock_unlock_symbols_rd(GBinFormat *, bool);

#define g_binary_format_lock_symbols_rd(f) g_binary_format_lock_unlock_symbols_rd(f, true)
#define g_binary_format_unlock_symbols_rd(f) g_binary_format_lock_unlock_symbols_rd(f, false)

/* Protège ou lève la protection de l'accès aux symboles. */
void g_binary_format_lock_unlock_symbols_wr(GBinFormat *, bool);

#define g_binary_format_lock_symbols_wr(f) g_binary_format_lock_unlock_symbols_wr(f, true)
#define g_binary_format_unlock_symbols_wr(f) g_binary_format_lock_unlock_symbols_wr(f, false)

/* Assure qu'un verrou est bien posé pour l'accès aux symboles. */
#ifndef NDEBUG
void g_binary_format_check_for_symbols_lock(const GBinFormat *);
#endif

/* Fournit la marque de dernière modification des symboles. */
unsigned int g_binary_format_get_symbols_stamp(const GBinFormat *);

/* Compte le nombre de symboles représentés. */
size_t g_binary_format_count_symbols(const GBinFormat *);

/* Fournit un symbole lié à un format. */
GBinSymbol *g_binary_format_get_symbol(const GBinFormat *, size_t);

/* Ajoute un symbole à la collection du format binaire. */
bool g_binary_format_add_symbol(GBinFormat *, GBinSymbol *);

/* Ajoute plusieurs symboles à la collection du format binaire. */
bool g_binary_format_add_symbols(GBinFormat *, GBinSymbol **, size_t);

/* Retire un symbole de la collection du format binaire. */
void g_binary_format_remove_symbol(GBinFormat *, GBinSymbol *);

/* Recherche le symbole correspondant à une étiquette. */
bool g_binary_format_find_symbol_by_label(GBinFormat *, const char *, GBinSymbol **);

/* Recherche l'indice du symbole correspondant à une adresse. */
bool g_binary_format_find_symbol_index_at(GBinFormat *, const vmpa2t *, size_t *);

/* Recherche le symbole correspondant à une adresse. */
bool g_binary_format_find_symbol_at(GBinFormat *, const vmpa2t *, GBinSymbol **);

/* Recherche le symbole contenant une adresse. */
bool g_binary_format_find_symbol_for(GBinFormat *, const vmpa2t *, GBinSymbol **);

/* Recherche le symbole suivant celui lié à une adresse. */
bool g_binary_format_find_next_symbol_at(GBinFormat *, const vmpa2t *, GBinSymbol **);

/* Recherche le premier symbole inclus dans une zone mémoire. */
bool g_binary_format_find_first_symbol_inside(GBinFormat *, const mrange_t *, size_t *);

/* Recherche le symbole correspondant à une adresse. */
bool g_binary_format_resolve_symbol(GBinFormat *, const vmpa2t *, bool, GBinSymbol **, phys_t *);



/* ------------------ CONSERVATION DES SOUCIS DURANT LE CHARGEMENT ------------------ */


/* Types d'erreurs détectées */

#define FMT_ERROR(idx) ((idx << 2) | (0 << 0))

typedef enum _BinaryFormatError
{
    BFE_SPECIFICATION = FMT_ERROR(0),       /* Non respect des specs       */
    BFE_STRUCTURE     = FMT_ERROR(1)        /* Code non reconnu            */

} BinaryFormatError;


/* Protège ou lève la protection de l'accès aux erreurs. */
void g_binary_format_lock_unlock_errors(GBinFormat *, bool);

#define g_binary_format_lock_errors(f) g_binary_format_lock_unlock_errors(f, true)
#define g_binary_format_unlock_errors(f) g_binary_format_lock_unlock_errors(f, false)

/* Etend la liste des soucis détectés avec de nouvelles infos. */
void g_binary_format_add_error(GBinFormat *, BinaryFormatError, const vmpa2t *, const char *);

/* Indique le nombre d'erreurs relevées au niveau assembleur. */
size_t g_binary_format_count_errors(GBinFormat *);

/* Fournit les éléments concernant un soucis détecté. */
bool g_binary_format_get_error(GBinFormat *, size_t, BinaryFormatError *, vmpa2t *, char **);



#endif  /* _FORMAT_FORMAT_H */
