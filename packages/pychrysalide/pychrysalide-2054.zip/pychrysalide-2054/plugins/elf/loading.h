
/* Chrysalide - Outil d'analyse de fichiers binaires
 * loading.h - prototypes pour les chargements parallèles des symboles de format ELF
 *
 * Copyright (C) 2017-2018 Cyrille Bagard
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


#ifndef _PLUGINS_ELF_LOADING_H
#define _PLUGINS_ELF_LOADING_H


#include <format/symiter.h>
#include <glibext/notifier.h>


#include "format.h"



#define G_TYPE_ELF_LOADING            g_elf_loading_get_type()
#define G_ELF_LOADING(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_ELF_LOADING, GElfLoading))
#define G_IS_ELF_LOADING(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_ELF_LOADING))
#define G_ELF_LOADING_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ELF_LOADING, GElfLoadingClass))
#define G_IS_ELF_LOADING_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ELF_LOADING))
#define G_ELF_LOADING_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ELF_LOADING, GElfLoadingClass))


/* Fraction de loading à limiter (instance) */
typedef struct _GElfLoading GElfLoading;

/* Fraction de loading à limiter (classe) */
typedef struct _GElfLoadingClass GElfLoadingClass;


/* Assure un chargement pour ELF en différé. */
typedef bool (* elf_loading_cb) (GElfLoading *, GElfFormat *, phys_t *);

/* Assure l'intégration d'un symbole issu des relocalisations. */
typedef GBinSymbol * (* elf_importing_cb) (GElfLoading *, GElfFormat *, vmpa2t *);


/* Indique le type défini pour les tâches de chargements pour format ELF. */
GType g_elf_loading_get_type(void);

/* Crée une tâche de chargement pour ELF différée. */
GElfLoading *g_elf_loading_new_for_symbols(GElfFormat *, phys_t, phys_t, phys_t, phys_t, activity_id_t, elf_loading_cb);

/* Crée une tâche de chargement pour ELF différée. */
GElfLoading *g_elf_loading_new_for_relocations(GElfFormat *, phys_t, phys_t, elf_rel *, activity_id_t, elf_loading_cb);

/* Crée une tâche de chargement pour ELF différée. */
GElfLoading *g_elf_loading_new_for_imported(GElfFormat *, const vmpa2t *, phys_t, elf_rel *, size_t, phys_t, uint32_t, activity_id_t, elf_importing_cb);

/* Crée une tâche de chargement de chaînes pour ELF différée. */
GElfLoading *g_elf_loading_new_for_strings(GElfFormat *, phys_t, phys_t, phys_t, phys_t, virt_t, activity_id_t, elf_loading_cb);

/* Fournit le bilan des traitements différés. */
bool g_elf_loading_get_status(const GElfLoading *);

/* Construit la désignation adaptée à un symbole. */
const char *g_elf_loading_build_name(const GElfLoading *, uint32_t, virt_t, const char *, char *, vmpa2t *);

/* Intègre dans la liste adaptée une relocalisation chargée. */
void g_elf_loading_store_relocation(const GElfLoading *, const phys_t *, const elf_rel *);

/* Recherche une relocalisation par son décalage. */
bool g_elf_loading_search_for_relocation(const GElfLoading *, const uint64_t *, elf_rel **);

/* Construit le symbole adapté à un symbole importé. */
GBinSymbol *g_elf_loading_build_plt_symbol(const GElfLoading *, uint64_t);

/* Fournit la liste de symboles importés constituée. */
GBinSymbol **g_elf_loading_get_imported_symbols(const GElfLoading *, size_t *);

/* Donne les informations utiles à la recherche de chaînes. */
const bin_t *g_elf_loading_get_info_for_strings(const GElfLoading *, GBinContent **, phys_t *, phys_t *, phys_t *);

/* Détermine l'adresse de départ d'une chaîne avec une position. */
void g_elf_loading_compute_string_address(const GElfLoading *, const phys_t *, vmpa2t *);



#endif  /* _PLUGINS_ELF_LOADING_H */
