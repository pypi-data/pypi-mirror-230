
/* Chrysalide - Outil d'analyse de fichiers binaires
 * symbols.c - gestion des symboles d'un ELF
 *
 * Copyright (C) 2017-2019 Cyrille Bagard
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


#include "symbols.h"


#include <assert.h>
#include <malloc.h>
#include <stdlib.h>
#include <string.h>


#include <i18n.h>
#include <arch/instructions/raw.h>
#include <common/extstr.h>
#include <common/sort.h>
#include <core/global.h>
#include <core/logs.h>
#include <core/nproc.h>
#include <format/symiter.h>
#include <mangling/demangler.h>


#include "dynamic.h"
#include "elf-int.h"
#include "loading.h"
#include "program.h"
#include "section.h"



/* ------------------------- CHARGEMENT GLOBAL DES SYMBOLES ------------------------- */


/* Assure le chargement des symboles internes ELF en différé. */
static bool do_elf_symbol_loading(GElfLoading *, GElfFormat *, bool, phys_t *, GBinSymbol **);

/* Charge tous les symboles possibles. */
static void add_all_elf_symbols(GElfFormat *, phys_t, size_t, phys_t, GWorkQueue *, wgroup_id_t, elf_loading_cb, GtkStatusStack *, activity_id_t);



/* --------------------------- DETAIL DES SYMBOLES LOCAUX --------------------------- */


/* Assure le chargement des symboles locaux ELF en différé. */
static bool do_elf_local_symbol_loading(GElfLoading *, GElfFormat *, phys_t *);

/* Charge tous les symboles internes possibles. */
static bool load_elf_local_symbols(GElfFormat *, wgroup_id_t, GtkStatusStack *);



/* --------------------------- DETAIL DE SYMBOLES GLOBAUX --------------------------- */


/* Assure le chargement des symboles globaux ELF en différé. */
static bool do_elf_global_symbol_loading(GElfLoading *, GElfFormat *, phys_t *);

/* Dénombre le nombre de symboles en lien avec l'extérieur. */
static bool count_elf_global_symbols(GElfFormat *, GExeFormat *, uint32_t *);

/* Charge tous les éléments dynamiques externes possibles. */
static bool load_elf_global_symbols(GElfFormat *, wgroup_id_t, GtkStatusStack *);



/* ------------------------ INSCRIPTION DE SYMBOLES IMPORTES ------------------------ */


/* Assure le chargement des relocalisations ELF en différé. */
static bool do_elf_relocation_loading(GElfLoading *, GElfFormat *, phys_t *);

/* Charge en mémoire toutes les relocalisations présentes. */
static bool load_elf_relocations(GElfFormat *, const elf_phdr *, elf_rel **, size_t *, wgroup_id_t, GtkStatusStack *);

/* Assure la construction d'un symbole issu des relocalisations. */
static GBinSymbol *do_elf_relocation_convert(GElfLoading *, GElfFormat *, vmpa2t *);

/* Construit une liste de symboles issus des relocalisations. */
static GBinSymbol **convert_elf_relocations_to_symbols(GElfFormat *, elf_rel *, size_t, vmpa2t *, wgroup_id_t, GtkStatusStack *, size_t *);

/* Ajoute l'ensemble des symboles importés. */
static bool load_imported_elf_symbols(GElfFormat *, wgroup_id_t, GtkStatusStack *);



/* ------------------------- INSCRIPTION DE POINTS D'ENTREE ------------------------- */


/* Enregistre un point d'entrée au sein d'un binaire ELF. */
static bool register_elf_entry_point(GElfFormat *, virt_t, GBinRoutine *, DisassPriorityLevel);

/* Désigne tous les points d'entrée par une étiquette dédiée. */
static bool load_elf_entry_points_from_array(GElfFormat *, const elf_dyn *, const elf_dyn *, const char *, DisassPriorityLevel);

/* Enumère tous les points d'entrée principaux d'un binaire ELF. */
static bool load_all_elf_basic_entry_points(GElfFormat *, GtkStatusStack *);



/* ---------------------------------------------------------------------------------- */
/*                           CHARGEMENT GLOBAL DES SYMBOLES                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                gid    = groupe de travail impliqué.                         *
                 status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Charge en mémoire la liste humaine des symboles.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_elf_symbols(GElfFormat *format, wgroup_id_t gid, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    /* Symboles internes */

    result &= load_elf_local_symbols(format, gid, status);

    /* Symboles importés et/ou exportés */

    if (find_elf_dynamic_program_header(format, (elf_phdr []) { { { 0 } } }))
    {
        log_variadic_message(LMT_INFO, _("Binary is dynamically linked"));

        result &= load_elf_global_symbols(format, gid, status);

        result &= load_imported_elf_symbols(format, gid, status);

    }
    else log_variadic_message(LMT_INFO, _("Binary is statically linked"));

    /* Symboles d'entrée, si encore besoin */

    if (result)
        result = load_all_elf_basic_entry_points(format, status);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : loading = chargement de symboles en cours.                   *
*                format  = format ELF à compléter.                            *
*                local   = s'apprête-t-on à constuire un symbole interne ?    *
*                iter    = tête de lecture évoluant avec le temps. [OUT]      *
*                new     = éventuel renseignement du nouveau symbole. [OUT]   *
*                                                                             *
*  Description : Assure le chargement des symboles internes ELF en différé.   *
*                                                                             *
*  Retour      : Bilan de l'exécution, utile pour la poursuite du traitement. *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool do_elf_symbol_loading(GElfLoading *loading, GElfFormat *format, bool local, phys_t *iter, GBinSymbol **new)
{
    bool result;                            /* Bilan à retourner           */
    elf_sym sym;                            /* Symbole aux infos visées    */
    virt_t virt;                            /* Adresse virtuelle           */
    SymbolStatus status;                    /* Visibilité du symbole       */
    GBinFormat *base;                       /* Version basique du format   */
    uint32_t index;                         /* Indice du nom du symbole    */
    const char *name;                       /* Nom du symbole trouvé       */
    GBinSymbol *symbol;                     /* Nouveau symbole construit   */
    char alt_name[6 + VMPA_MAX_LEN];        /* Nom abstrait de substitution*/
    virt_t original_virt;                   /* Adresse virtuelle retenue   */
    vmpa2t addr;                            /* Localisation d'un symbole   */
    mrange_t range;                         /* Couverture mémoire associée */
    GBinRoutine *routine;                   /* Nouvelle routine trouvée    */

    if (new != NULL)
        *new = NULL;

    result = read_elf_symbol(format, iter, &sym);
    if (!result) goto desl_done;

    /**
     * Si l'adresse virtuelle est nulle, on ne peut ratacher le symbole à aucune position...
     *
     * On ne réalise donc aucune opération ici, quitte à laisser une seconde passe
     * s'occuper des symboles importés par exemple.
     */

    virt = ELF_SYM(format, sym, st_value);
    if (virt == 0) goto desl_done;

    /**
     * En ce qui concerne la nature de la visibilité, on distingue les deux situations suivantes :
     *  - zone DYNSYM : uniquement les importations / exportations.
     *  - zone SYMTAB : tous les symboles.
     *
     * La première zone doit donc être traitée en amont, et la seconde complète les traitements
     * avec à priori uniquement des symboles locaux.
     */

    if (local)
        status = SSS_INTERNAL;

    else
    {
        status = ELF_SYM(format, sym, st_shndx) == 0 ? SSS_IMPORTED : SSS_EXPORTED;

        /**
         * Si le symbol doit être traité ailleurs...
         */

        if (status == SSS_IMPORTED)
            goto desl_done;

    }

    /* Traitements particuliers */

    base = G_BIN_FORMAT(format);

    index = ELF_SYM(format, sym, st_name);

    switch (ELF_ST_TYPE(format, sym))
    {
        case STT_OBJECT:

            name = g_elf_loading_build_name(loading, index, virt, "obj_", alt_name, &addr);
            if (name == NULL)
            {
                symbol = NULL;
                break;
            }

            init_mrange(&range, &addr, ELF_SYM(format, sym, st_size));

            symbol = g_binary_symbol_new(&range, STP_OBJECT);

            g_binary_symbol_set_alt_label(symbol, name);

            break;

        case STT_FUNC:

            original_virt = virt;

            /* Ajustement de la position */

            virt = format->ops.fix_virt(virt);

            /* Constitution d'une routine */

            name = g_elf_loading_build_name(loading, index, virt, "func_", alt_name, &addr);
            if (name == NULL)
            {
                symbol = NULL;
                break;
            }

            routine = g_binary_format_decode_routine(base, name);
            symbol = G_BIN_SYMBOL(routine);

            init_mrange(&range, &addr, ELF_SYM(format, sym, st_size));

            g_binary_symbol_set_range(symbol, &range);

            /* Comptabilisation pour le désassemblage brut */

            g_binary_format_register_code_point(base, original_virt, DPL_SYMBOL);

            break;

        default:
            symbol = NULL;
            break;

    }

    if (symbol != NULL)
    {
        g_binary_symbol_set_status(symbol, status);

        /*
        if (new != NULL)
        {
            g_object_ref(G_OBJECT(symbol));
            *new = symbol;
        }
        */

        g_binary_format_add_symbol(base, symbol);

    }

 desl_done:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format    = description de l'exécutable à compléter.         *
*                sym_start = localisation du début de la zone de symboles.    *
*                count     = nombre de descriptions de symbole attendues.     *
*                str_start = début de la zone contenant les descriptions.     *
*                wq        = espace de travail dédié.                         *
*                gid       = groupe de travail impliqué.                      *
*                callback  = routine de traitements particuliers.             *
*                status    = barre de statut à tenir informée.                *
*                msg       = identifiant du message de progression.           *
*                                                                             *
*  Description : Charge tous les symboles possibles.                          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void add_all_elf_symbols(GElfFormat *format, phys_t sym_start, size_t count, phys_t str_start, GWorkQueue *wq, wgroup_id_t gid, elf_loading_cb callback, GtkStatusStack *status, activity_id_t msg)
{
    phys_t sym_size;                        /* Taille de chaque symbole lu */
    guint runs_count;                       /* Qté d'exécutions parallèles */
    phys_t run_size;                        /* Volume réparti par exécution*/
    guint i;                                /* Boucle de parcours          */
    phys_t begin;                           /* Début de zone de traitement */
    phys_t end;                             /* Fin d'un zone de traitement */
    GElfLoading *loading;                   /* Tâche de chargement à lancer*/

    sym_size = ELF_SIZEOF_SYM(format);

    run_size = compute_run_size(count, &runs_count);

    gtk_status_stack_extend_activity(status, msg, count);

    for (i = 0; i < runs_count; i++)
    {
        begin = sym_start + i * run_size * sym_size;

        if ((i + 1) == runs_count)
            end = sym_start + count * sym_size;
        else
            end = begin + run_size * sym_size;

        loading = g_elf_loading_new_for_symbols(format, str_start, sym_start, begin, end, msg, callback);

        g_work_queue_schedule_work(wq, G_DELAYED_WORK(loading), gid);

    }

}



/* ---------------------------------------------------------------------------------- */
/*                             DETAIL DES SYMBOLES LOCAUX                             */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : loading = chargement de symboles externes en cours.          *
*                format  = format ELF à compléter.                            *
*                iter    = tête de lecture évoluant avec le temps. [OUT]      *
*                                                                             *
*  Description : Assure le chargement des symboles locaux ELF en différé.     *
*                                                                             *
*  Retour      : Bilan de l'exécution, utile pour la poursuite du traitement. *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool do_elf_local_symbol_loading(GElfLoading *loading, GElfFormat *format, phys_t *iter)
{
    bool result;                            /* Bilan à retourner           */

    result = do_elf_symbol_loading(loading, format, true, iter, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                gid    = groupe de travail impliqué.                         *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Charge tous les symboles internes possibles.                 *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool load_elf_local_symbols(GElfFormat *format, wgroup_id_t gid, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    activity_id_t msg;                      /* Message de progression      */
    GWorkQueue *queue;                      /* Gestionnaire de différés    */
    size_t size;                            /* Taille de chaque symbole lu */
    elf_shdr *symtabs;                      /* Groupe de sections trouvées */
    size_t count;                           /* Quantité de données         */
    size_t i;                               /* Boucle de parcours          */
    phys_t sym_start;                       /* Début de la zone à traiter  */
    phys_t sym_size;                        /* Taille de cette même zone   */
    size_t sym_count;                       /* Nombre de symboles déduits  */
    elf_shdr strtab;                        /* Section dédiées aux chaînes */
    phys_t str_start;                       /* Début de cette section      */

    result = true;

    msg = gtk_status_stack_add_activity(status, _("Loading local symbols..."), 0);

    queue = get_work_queue();

    size = ELF_SIZEOF_SYM(format);

    if (find_elf_sections_by_type(format, SHT_SYMTAB, &symtabs, &count))
        for (i = 0; i < count; i++)
        {
            get_elf_section_content(format, &symtabs[i], &sym_start, &sym_size, NULL);

            if (sym_size % size != 0)
                continue;

            sym_count = sym_size / size;

            if (!find_elf_section_by_index(format, ELF_SHDR(format, symtabs[i], sh_link), &strtab))
                continue;

            get_elf_section_content(format, &strtab, &str_start, NULL, NULL);

            add_all_elf_symbols(format, sym_start, sym_count, str_start,
                                queue, gid, do_elf_local_symbol_loading, status, msg);

        }

    g_work_queue_wait_for_completion(queue, gid);

    gtk_status_stack_remove_activity(status, msg);

    if (symtabs != NULL) free(symtabs);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                             DETAIL DE SYMBOLES GLOBAUX                             */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : loading = chargement de symboles externes en cours.          *
*                format  = format ELF à compléter.                            *
*                iter    = tête de lecture évoluant avec le temps. [OUT]      *
*                                                                             *
*  Description : Assure le chargement des symboles globaux ELF en différé.    *
*                                                                             *
*  Retour      : Bilan de l'exécution, utile pour la poursuite du traitement. *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool do_elf_global_symbol_loading(GElfLoading *loading, GElfFormat *format, phys_t *iter)
{
    bool result;                            /* Bilan à retourner           */
    GBinSymbol *symbol;                     /* Nouveau symbole en place    */

    result = do_elf_symbol_loading(loading, format, false, iter, &symbol);

    //g_clear_object(&symbol);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                exec   = autre vision de ce format.                          *
*                count  = nombre de symboles présents. [OUT]                  *
*                                                                             *
*  Description : Dénombre le nombre de symboles en lien avec l'extérieur.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool count_elf_global_symbols(GElfFormat *format, GExeFormat *exec, uint32_t *count)
{
    bool result;                            /* Bilan à retourner           */
    elf_dyn hash;                           /* Table de type DT_HASH       */
    bool found;                             /* Détection validée           */
    vmpa2t addr;                            /* Position de départ brute    */
    uint32_t n_buckets;                     /* Quantité de bacs en place   */
    uint32_t sym_offset;                    /* Indice du premier symbole   */
    uint32_t bloom_size;                    /* Taille du filtre Bloom      */
    uint32_t last_symbol;                   /* Indice de dernier symbole   */
    uint32_t i;                             /* Boucle de parcours          */
    uint32_t start;                         /* Indice de départ d'un bac   */
    uint32_t value;                         /* Valeur d'un maillon         */

    result = false;

    /**
     * Cf. l'astuce indiquée par :
     *
     *    - http://www.gabriel.urdhr.fr/2015/09/28/elf-file-format/#symbol-tables
     *    - http://www.sco.com/developers/gabi/latest/ch5.dynamic.html#hash
     *
     * Le fonctionnement global des chaînes est décrit ici :
     *
     *    - https://flapenguin.me/2017/04/24/elf-lookup-dt-hash/
     *
     * Celui des chaînes GNU fait l'objet de l'article suivant :
     *
     *    - https://flapenguin.me/2017/05/10/elf-lookup-dt-gnu-hash/
     *
     */

    /* Méthode DT_HASH */

    found = find_elf_dynamic_item_by_type(format, DT_HASH, &hash);

    if (found)
    {
        result = g_exe_format_translate_address_into_vmpa(exec, ELF_DYN(format, hash, d_un.d_ptr), &addr);
        if (!result) goto exit;

        advance_vmpa(&addr, sizeof(uint32_t));

        result = g_binary_content_read_u32(G_KNOWN_FORMAT(format)->content, &addr, format->endian, count);
        if (!result) goto exit;

        goto exit;

    }

    /* Méthode DT_GNU_HASH */

    found = find_elf_dynamic_item_by_type(format, DT_GNU_HASH, &hash);

    if (found)
    {
        result = g_exe_format_translate_address_into_vmpa(exec, ELF_DYN(format, hash, d_un.d_ptr), &addr);
        if (!result) goto exit;

        result = g_binary_content_read_u32(G_KNOWN_FORMAT(format)->content, &addr, format->endian, &n_buckets);
        if (!result) goto exit;

        result = g_binary_content_read_u32(G_KNOWN_FORMAT(format)->content, &addr, format->endian, &sym_offset);
        if (!result) goto exit;

        result = g_binary_content_read_u32(G_KNOWN_FORMAT(format)->content, &addr, format->endian, &bloom_size);
        if (!result) goto exit;

        /* Saut de bloom_shift */
        advance_vmpa(&addr, sizeof(uint32_t));

        /* Saut de bloom[bloom_size] */
        if (format->is_32b)
            advance_vmpa(&addr, bloom_size * sizeof(uint32_t));
        else
            advance_vmpa(&addr, bloom_size * sizeof(uint64_t));

        /* Localisation de la chaîne comportant le plus grand index */

        last_symbol = 0;

        for (i = 0; i < n_buckets; i++)
        {
            result = g_binary_content_read_u32(G_KNOWN_FORMAT(format)->content, &addr, format->endian, &start);
            if (!result) goto exit;

            if (last_symbol < start)
                last_symbol = start;

        }

        if (last_symbol < sym_offset)
        {
            *count = sym_offset;
            result = true;
        }

        else
        {
            /* Parcours de la chaîne au plus haut potentiel */

            advance_vmpa(&addr, (last_symbol - sym_offset) * sizeof(uint32_t));

            while (true)
            {
                result = g_binary_content_read_u32(G_KNOWN_FORMAT(format)->content, &addr, format->endian, &value);
                if (!result) goto exit;

                last_symbol++;

                if (value & 0x1)
                    break;

            }

            *count = last_symbol;
            result = true;

        }

    }

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                gid    = groupe de travail impliqué.                         *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Charge tous les éléments dynamiques externes possibles.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool load_elf_global_symbols(GElfFormat *format, wgroup_id_t gid, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    GExeFormat *exec;                       /* Autre vision du format      */
    elf_dyn strtab;                         /* Table de type DT_STRTAB     */
    phys_t str_start;                       /* Début de zone des chaînes   */
    elf_dyn symtab;                         /* Table de type DT_SYMTAB     */
    phys_t sym_start;                       /* Début de zone des symboles  */
    uint32_t count;                         /* Nombre de symboles présents */
    activity_id_t msg;                      /* Message de progression      */
    GWorkQueue *queue;                      /* Gestionnaire de différés    */

    result = true;

    /**
     * Les spécifications ne sont pas très claires sur le nombre de tables
     * possible... On y parle de LA table des symboles, ce qui laisse penser
     * qu'il ne peut y en avoir qu'une.
     */

    exec = G_EXE_FORMAT(format);

    /* Récupération du début des chaînes de description */

    result = find_elf_dynamic_item_by_type(format, DT_STRTAB, &strtab);
    if (!result) goto exit;

    result = g_exe_format_translate_address_into_offset(exec, ELF_DYN(format, strtab, d_un.d_ptr), &str_start);
    if (!result) goto exit;

    /* Récupération du début des définitions de symboles */

    result = find_elf_dynamic_item_by_type(format, DT_SYMTAB, &symtab);
    if (!result) goto exit;

    result = g_exe_format_translate_address_into_offset(exec, ELF_DYN(format, symtab, d_un.d_ptr), &sym_start);
    if (!result) goto exit;

    /* Détermination du nombre d'éléments */

    result = count_elf_global_symbols(format, exec, &count);
    if (!result) goto exit;

    /* Chargement des symboles */

    msg = gtk_status_stack_add_activity(status, _("Loading global symbols..."), 0);

    queue = get_work_queue();

    add_all_elf_symbols(format, sym_start, count, str_start,
                        queue, gid, do_elf_global_symbol_loading, status, msg);

    g_work_queue_wait_for_completion(queue, gid);

    gtk_status_stack_remove_activity(status, msg);

 exit:

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                          INSCRIPTION DE SYMBOLES IMPORTES                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : loading = chargement de relocalisations en cours.            *
*                format  = format ELF à compléter.                            *
*                iter    = tête de lecture évoluant avec le temps. [OUT]      *
*                                                                             *
*  Description : Assure le chargement des relocalisations ELF en différé.     *
*                                                                             *
*  Retour      : Bilan de l'exécution, utile pour la poursuite du traitement. *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool do_elf_relocation_loading(GElfLoading *loading, GElfFormat *format, phys_t *iter)
{
    bool result;                            /* Bilan à retourner           */
    elf_rel reloc;                          /* Relocalisation constituée   */

    result = read_elf_relocation(format, iter, &reloc);

    if (result)
        g_elf_loading_store_relocation(loading, iter, &reloc);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format  = informations chargées à consulter.                 *
*                dynamic = en-tête de programme de type DYNAMIC.              *
*                relocs  = liste des relocalisations triées à charger. [OUT]  *
*                count   = taille de cette liste. [OUT]                       *
*                gid     = groupe de travail dédié.                           *
*                status  = barre de statut à tenir informée.                  *
*                                                                             *
*  Description : Charge en mémoire toutes les relocalisations présentes.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool load_elf_relocations(GElfFormat *format, const elf_phdr *dynamic, elf_rel **relocs, size_t *count, wgroup_id_t gid, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    GExeFormat *exec;                       /* Autre vision du format      */
    elf_dyn jmprel;                         /* Table des relocalisations   */
    vmpa2t start;                           /* Position de départ brute    */
    elf_dyn pltrelsz;                       /* Taille de table en octets   */
    uint64_t length;                        /* Nombre total des éléments   */
    mrange_t shr_range;                     /* Emplacement des relocs. #1  */
    mrange_t phr_range;                     /* Emplacement des relocs. #2  */
    phys_t rel_size;                        /* Taille de chaque élément lu */
    bool ret;                               /* Bilan d'un appel            */
    activity_id_t msg;                      /* Message de progression      */
    GWorkQueue *queue;                      /* Gestionnaire de différés    */
    guint runs_count;                       /* Qté d'exécutions parallèles */
    phys_t run_size;                        /* Volume réparti par exécution*/
    GElfLoading **loadings;                 /* Tâches de chargement        */
    guint i;                                /* Boucle de parcours          */
    phys_t begin;                           /* Début de zone de traitement */
    phys_t end;                             /* Fin d'un zone de traitement */

    result = true;

    *relocs = NULL;
    *count = 0;

    exec = G_EXE_FORMAT(format);

    /* Collecte des informations */

    if (!_find_elf_dynamic_item_by_type(format, dynamic, DT_JMPREL, &jmprel))
        goto exit;

    result = g_exe_format_translate_address_into_vmpa(exec, ELF_DYN(format, jmprel, d_un.d_ptr), &start);

    if (!result)
        goto exit;

    if (!_find_elf_dynamic_item_by_type(format, dynamic, DT_PLTRELSZ, &pltrelsz))
        goto exit;

    length = ELF_DYN(format, pltrelsz, d_un.d_val);

    /* Corrélation des informations */

    ret = find_elf_section_range_by_name(format, ".rel.plt", &shr_range);

    if (ret)
    {
        init_mrange(&phr_range, &start, length);

        if (cmp_mrange(&phr_range, &shr_range) != 0)
            log_simple_message(LMT_BAD_BINARY,
                               _("The linker PLT and the PLT section differ by their area definition."));

    }

    /* Détermination du nombre d'éléments */

    rel_size = ELF_SIZEOF_REL(format);

    if (length % rel_size != 0)
    {
        result = false;
        goto exit;
    }

    length /= rel_size;

    /* Chargement en mémoire des relocalisations */

    if (length == 0)
        goto exit;

    *relocs = malloc(length * sizeof(elf_rel));
    *count = length;

    msg = gtk_status_stack_add_activity(status, _("Loading relocations..."), length);

    queue = get_work_queue();

    run_size = compute_run_size(length, &runs_count);

    loadings = malloc(runs_count * sizeof(GElfLoading *));

    for (i = 0; i < runs_count; i++)
    {
        begin = get_phy_addr(&start) + i * run_size * rel_size;

        if ((i + 1) == runs_count)
            end = get_phy_addr(&start) + length * rel_size;
        else
            end = begin + run_size * rel_size;

        loadings[i] = g_elf_loading_new_for_relocations(format, begin, end,
                                                        (*relocs) + i * run_size,
                                                        msg, do_elf_relocation_loading);

        g_object_ref(G_OBJECT(loadings[i]));

        g_work_queue_schedule_work(queue, G_DELAYED_WORK(loadings[i]), gid);

    }

    g_work_queue_wait_for_completion(queue, gid);

    gtk_status_stack_remove_activity(status, msg);

    /* Vérifications du bon déroulement */

    for (i = 0; i < runs_count; i++)
    {
        result &= g_elf_loading_get_status(loadings[i]);

        g_object_unref(G_OBJECT(loadings[i]));

    }

    free(loadings);

    if (!result)
    {
        free(*relocs);
        goto exit;
    }

    /* Tri de la liste obtenue */

    int compare_relocations(const elf_rel *a, const elf_rel *b)
    {
        return sort_uint64_t(ELF_REL(format, *a, r_offset), ELF_REL(format, *b, r_offset));
    }

    qsort(*relocs, *count, sizeof(elf_rel), (__compar_fn_t)compare_relocations);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : loading = chargement de relocalisations en cours.            *
*                format  = format ELF à compléter.                            *
*                addr    = emplacement de code à traiter. [OUT]               *
*                                                                             *
*  Description : Assure la construction d'un symbole issu des relocalisations.*
*                                                                             *
*  Retour      : Nouveau symbole constitué ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GBinSymbol *do_elf_relocation_convert(GElfLoading *loading, GElfFormat *format, vmpa2t *addr)
{
    GBinSymbol *result;                     /* Symbole à retourner         */
    vmpa2t start;                           /* Sauvegarde du départ        */
    uint64_t offset;                        /* Décalage à retrouver        */
    bool status;                            /* Bilan d'une opération       */
    elf_rel *reloc;                         /* Infos de relocalisation     */
    uint64_t index;                         /* Indice du symbole concerné  */
    phys_t length;                          /* Taille du nouveau symbole   */
    mrange_t range;                         /* Couverture mémoire associée */

    result = NULL;

    /* Détermination de la relocalisation associée */

    copy_vmpa(&start, addr);

    status = format->ops.get_linkage_offset(format, addr, &offset);
    if (!status) goto exit;

    status = g_elf_loading_search_for_relocation(loading, &offset, &reloc);
    if (!status) goto exit;

    /* Récupération des données du symbole visé */

    index = ELF_REL_SYM(format, *reloc);

    result = g_elf_loading_build_plt_symbol(loading, index);
    if (result == NULL) goto exit;

    /* Inscription des propriétés associées */

    length = compute_vmpa_diff(&start, addr);

    init_mrange(&range, &start, length);
    g_binary_symbol_set_range(result, &range);

    g_binary_symbol_set_status(result, SSS_IMPORTED);

    /* Comptabilisation pour le désassemblage brut */

    g_binary_format_register_code_point(G_BIN_FORMAT(format), start.virtual, DPL_FORMAT_POINT);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format    = format ELF à compléter.                          *
*                relocs    = table des relocalisations chargées.              *
*                rel_count = nombre de ces éléments à interpréter.            *
*                start     = emplacement du premier symbole.                  *
*                gid       = groupe de travail dédié.                         *
*                status    = barre de statut à tenir informée.                *
*                count     = nombre de symboles mis en place. [OUT]           *
*                                                                             *
*  Description : Construit une liste de symboles issus des relocalisations.   *
*                                                                             *
*  Retour      : Liste de symboles triée ou NULL en cas d'erreur.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GBinSymbol **convert_elf_relocations_to_symbols(GElfFormat *format, elf_rel *relocs, size_t rel_count, vmpa2t *start, wgroup_id_t gid, GtkStatusStack *status, size_t *count)
{
    GBinSymbol **result;                    /* Liste à retourner           */
    GExeFormat *exec;                       /* Autre vision du format      */
    elf_dyn strtab;                         /* Table de type DT_STRTAB     */
    bool ret;                               /* Bilan d'une opération       */
    phys_t str_start;                       /* Début de zone des chaînes   */
    elf_dyn symtab;                         /* Table de type DT_SYMTAB     */
    phys_t sym_start;                       /* Début de zone des symboles  */
    uint32_t sym_count;                     /* Nombre de symboles présents */
    activity_id_t msg;                      /* Message de progression      */
    GWorkQueue *queue;                      /* Gestionnaire de différés    */
    GElfLoading *loading;                   /* Tâche de chargement         */

    result = NULL;

    exec = G_EXE_FORMAT(format);

    /* Récupération du début des chaînes de description */

    ret = find_elf_dynamic_item_by_type(format, DT_STRTAB, &strtab);
    if (!ret) goto aer_exit;

    ret = g_exe_format_translate_address_into_offset(exec, ELF_DYN(format, strtab, d_un.d_ptr), &str_start);
    if (!ret) goto aer_exit;

    /* Récupération du début des définitions de symboles */

    ret = find_elf_dynamic_item_by_type(format, DT_SYMTAB, &symtab);
    if (!ret) goto aer_exit;

    ret = g_exe_format_translate_address_into_offset(exec, ELF_DYN(format, symtab, d_un.d_ptr), &sym_start);
    if (!ret) goto aer_exit;

    /* Détermination du nombre d'éléments */

    ret = count_elf_global_symbols(format, exec, &sym_count);
    if (!ret) goto aer_exit;

    /* Mise en application des références externes */

    msg = gtk_status_stack_add_activity(status, _("Applying relocations..."), rel_count);

    queue = get_work_queue();

    loading = g_elf_loading_new_for_imported(format, start, str_start, relocs, rel_count,
                                             sym_start, sym_count, msg, do_elf_relocation_convert);

    g_object_ref(G_OBJECT(loading));

    g_work_queue_schedule_work(queue, G_DELAYED_WORK(loading), gid);

    g_work_queue_wait_for_completion(queue, gid);

    gtk_status_stack_remove_activity(status, msg);

    /* Vérification du bon déroulement */

    ret = g_elf_loading_get_status(loading);

    if (ret)
        result = g_elf_loading_get_imported_symbols(loading, count);

    g_object_unref(G_OBJECT(loading));

 aer_exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                gid    = groupe de travail dédié.                            *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Ajoute l'ensemble des symboles importés.                     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool load_imported_elf_symbols(GElfFormat *format, wgroup_id_t gid, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    elf_phdr dynamic;                       /* En-tête de programme DYNAMIC*/
    elf_rel *relocs;                        /* Relocalisations présentes   */
    size_t rel_count;                       /* Qté de ces relocalisations  */
    virt_t plt_virt;                        /* Adresse de la PLT           */
    GExeFormat *exec;                       /* Autre vision du format      */
    vmpa2t plt_addr;                        /* Localisation complète       */
    size_t count;                           /* Quantité de symboles chargés*/
    GBinSymbol **symbols;                   /* Liste de ces symboles       */
    size_t i;                               /* Boucle de parcours          */

    result = false;

    if (!find_elf_dynamic_program_header(format, &dynamic))
        goto quick_exit;

    /* Chargement des relocalisations */

    if (!load_elf_relocations(format, &dynamic, &relocs, &rel_count, gid, status))
        goto quick_exit;

    /* Localisation du code de la PLT */

    if (!resolve_plt_using_got(format, &plt_virt))
        goto exit;

    exec = G_EXE_FORMAT(format);

    if (!g_exe_format_translate_address_into_vmpa(exec, plt_virt, &plt_addr))
        goto exit;

    /* Inscription des symboles */

    result = format->ops.find_first_plt(format, &plt_addr);
    if (!result) goto exit;

    symbols = convert_elf_relocations_to_symbols(format, relocs, rel_count, &plt_addr, gid, status, &count);
    if (symbols == NULL) goto exit;

    result = g_binary_format_add_symbols(G_BIN_FORMAT(format), symbols, count);

    for (i = 0; i < count; i++)
        g_object_unref(symbols[i]);

    if (symbols != NULL)
        free(symbols);

 exit:

    if (relocs != NULL)
        free(relocs);

 quick_exit:

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                           INSCRIPTION DE POINTS D'ENTREE                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : format  = description de l'exécutable à compléter.           *
*                vaddr   = adresse virtuelle du symbole à insérer.            *
*                routine = représentation de la fonction repérée.             *
*                level   = indication de priorité et d'origine de l'adresse.  *
*                                                                             *
*  Description : Enregistre un point d'entrée au sein d'un binaire ELF.       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool register_elf_entry_point(GElfFormat *format, virt_t vaddr, GBinRoutine *routine, DisassPriorityLevel level)
{
    bool result;                            /* Bilan à renvoyer            */
    virt_t final_vaddr;                     /* Adresse virtuelle retenue   */
    vmpa2t addr;                            /* Localisation d'une routine  */
    GBinFormat *base;                       /* Version basique du format   */
    GBinSymbol *symbol;                     /* Nouveau symbole construit   */
    mrange_t range;                         /* Couverture mémoire associée */

    /* Localisation complète du symbole */

    final_vaddr = format->ops.fix_virt(vaddr);

    result = g_exe_format_translate_address_into_vmpa(G_EXE_FORMAT(format), final_vaddr, &addr);
    if (!result) goto exit;

    /* Comptabilisation en tant que symbole */

    base = G_BIN_FORMAT(format);

    if (g_binary_format_find_symbol_at(base, &addr, &symbol))
    {
        /**
         * On ne relâche pas tout de suite le symbole trouvé, afin de le traiter
         * en fin de fonction.
         *
         * Par contre, la routine proposée est détruite ici.
         */

        g_object_unref(G_OBJECT(routine));

    }

    else
    {
        symbol = G_BIN_SYMBOL(routine);
        g_object_ref(G_OBJECT(symbol));

        init_mrange(&range, &addr, 0);
        g_binary_symbol_set_range(symbol, &range);

        g_binary_format_add_symbol(base, symbol);

    }

    /* Marquage */

    g_binary_symbol_set_stype(symbol, STP_ENTRY_POINT);

    g_object_unref(G_OBJECT(symbol));

    /* Comptabilisation pour le désassemblage brut */
    g_binary_format_register_code_point(base, vaddr, level);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                array  = indications quant au tableau à charger.             *
*                size   = indications quant à la taille de ce tableau.        *
*                prefix = désignation de base des éléments du tableau.        *
*                level  = indication de priorité et d'origine de l'adresse.   *
*                                                                             *
*  Description : Désigne tous les points d'entrée par une étiquette dédiée.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool load_elf_entry_points_from_array(GElfFormat *format, const elf_dyn *array, const elf_dyn *size, const char *prefix, DisassPriorityLevel level)
{
    bool result;                            /* Bilan à renvoyer            */
    GBinFormat *base;                       /* Autre version du format     */
    GBinContent *content;                   /* Contenu binaire à lire      */
    vmpa2t pos;                             /* Tête de lecture courante    */
    phys_t length;                          /* Taille totale du contenu    */
    uint32_t virt_32;                       /* Adresse virtuelle sur 32b   */
    uint64_t virt_64;                       /* Adresse virtuelle sur 64b   */
    unsigned int i;                         /* Boucle de parcours          */
    bool status;                            /* Bilan d'une opération       */
    virt_t ep;                              /* Point d'entrée détecté      */
    char fullname[64];                      /* Désignation humaine         */
    GBinRoutine *routine;                   /* Routine à associer à un pt. */

    assert(sizeof(fullname) >= (strlen(prefix) + sizeof(XSTR(UINT64_MAX) + 1)));

    base = G_BIN_FORMAT(format);
    content = G_KNOWN_FORMAT(base)->content;

    result = g_exe_format_translate_address_into_vmpa(G_EXE_FORMAT(format),
                                                      ELF_DYN(format, *array, d_un.d_val),
                                                      &pos);
    if (!result) goto exit;

    length = get_phy_addr(&pos) + ELF_DYN(format, *size, d_un.d_val);

    for (i = 0; get_phy_addr(&pos) < length && result; i++)
    {
        /**
         * Selon la libc d'Android (https://www.codeaurora.org/.../android/bionic/linker/README.TXT) :
         *
         *      DT_INIT_ARRAY
         *          Points to an array of function addresses that must be
         *          called, in-order, to perform initialization. Some of
         *          the entries in the array can be 0 or -1, and should
         *          be ignored.
         *
         * On étend le principe aux sections DT_FINI_ARRAY et DT_PREINIT_ARRAY.
         */

        if (format->is_32b)
        {
            result = g_binary_content_read_u32(content, &pos, format->endian, &virt_32);

            status = (virt_32 != 0x0 && virt_32 != 0xffffffff);
            ep = virt_32;

        }
        else
        {
            result = g_binary_content_read_u64(content, &pos, format->endian, &virt_64);

            status = (virt_64 != 0x0 && virt_64 != 0xffffffffffffffff);
            ep = virt_64;

        }

        if (result && status)
        {
            snprintf(fullname, sizeof(fullname), "%s%u", prefix, i);

            routine = g_binary_format_decode_routine(base, fullname);
            result = register_elf_entry_point(format, ep, routine, level);

        }

    }

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à consulter.            *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Enumère tous les points d'entrée principaux d'un binaire ELF.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool load_all_elf_basic_entry_points(GElfFormat *format, GtkStatusStack *status)
{
    bool result;                            /* Bilan à renvoyer            */
    activity_id_t msg;                      /* Message de progression      */
    GBinFormat *base;                       /* Autre version du format     */
    virt_t ep;                              /* Point d'entrée détecté      */
    GBinRoutine *routine;                   /* Routine à associer à un pt. */
    elf_phdr dynamic;                       /* En-tête de programme DYNAMIC*/
    elf_dyn item_a;                         /* Premier élément DYNAMIC     */
    elf_dyn item_b;                         /* Second élément DYNAMIC      */

    result = true;

    msg = gtk_status_stack_add_activity(status, _("Registering entry points..."), 0);

    base = G_BIN_FORMAT(format);

    /* Point d'entrée principal éventuel */

    ep = ELF_HDR(format, format->header, e_entry);

    if (ep != 0x0)
    {
        routine = g_binary_format_decode_routine(base, "entry_point");
        result = register_elf_entry_point(format, ep, routine, DPL_ENTRY_POINT);
        if (!result) goto exit;
    }

    /* Chargemet de l'en-tête de programme DYNAMIC */

    if (!find_elf_dynamic_program_header(format, &dynamic))
        goto exit;

    /* Détection des constructeurs & destructeurs */

    if (_find_elf_dynamic_item_by_type(format, &dynamic, DT_INIT, &item_a))
    {
        ep = ELF_DYN(format, item_a, d_un.d_ptr);

        if (ep != 0x0)
        {
            routine = g_binary_format_decode_routine(base, "init_function");
            result = register_elf_entry_point(format, ep, routine, DPL_ENTRY_POINT);
            if (!result) goto exit;
        }

    }

    if (_find_elf_dynamic_item_by_type(format, &dynamic, DT_FINI, &item_a))
    {
        ep = ELF_DYN(format, item_a, d_un.d_ptr);

        if (ep != 0x0)
        {
            routine = g_binary_format_decode_routine(base, "termination_function");
            result = register_elf_entry_point(format, ep, routine, DPL_FORMAT_POINT);
            if (!result) goto exit;
        }

    }

    if (_find_elf_dynamic_item_by_type(format, &dynamic, DT_INIT_ARRAY, &item_a))
    {
        if (_find_elf_dynamic_item_by_type(format, &dynamic, DT_INIT_ARRAYSZ, &item_b))
        {
            result = load_elf_entry_points_from_array(format, &item_a, &item_b,
                                                      "init_array_function_", DPL_ENTRY_POINT);
            if (!result) goto exit;
        }

    }

    if (_find_elf_dynamic_item_by_type(format, &dynamic, DT_FINI_ARRAY, &item_a))
    {
        if (_find_elf_dynamic_item_by_type(format, &dynamic, DT_FINI_ARRAYSZ, &item_b))
        {
            result = load_elf_entry_points_from_array(format, &item_a, &item_b,
                                                      "fini_array_function_", DPL_FORMAT_POINT);
            if (!result) goto exit;
        }

    }

    if (_find_elf_dynamic_item_by_type(format, &dynamic, DT_PREINIT_ARRAY, &item_a))
    {
        if (_find_elf_dynamic_item_by_type(format, &dynamic, DT_PREINIT_ARRAYSZ, &item_b))
        {
            result = load_elf_entry_points_from_array(format, &item_a, &item_b,
                                                      "preinit_array_function_", DPL_ENTRY_POINT);
            if (!result) goto exit;
        }

    }

    /* Identification de l'entrée de la PLT */

    if (resolve_plt_using_got(format, &ep))
    {
        if (ep != 0x0)
        {
            routine = g_binary_format_decode_routine(base, "plt_entry");
            result = register_elf_entry_point(format, ep, routine, DPL_FORMAT_POINT);
        }

    }

 exit:

    gtk_status_stack_remove_activity(status, msg);

    return result;

}
