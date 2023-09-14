
/* Chrysalide - Outil d'analyse de fichiers binaires
 * loading.c - chargements parallèles des symboles de format ELF
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


#include "loading.h"


#include <assert.h>
#include <string.h>


#include <i18n.h>
#include <common/extstr.h>
#include <common/sort.h>
#include <core/logs.h>
#include <core/params.h>
#include <glibext/delayed-int.h>


#include "elf-int.h"



/* Fraction de routines à limiter (instance) */
struct _GElfLoading
{
    GDelayedWork parent;                    /* A laisser en premier        */

    GElfFormat *format;                     /* Format à faire évoluer      */

    phys_t str_start;                       /* Chaînes à disposition       */

    /**
     * Gestion des informations de contexte.
     */

    union
    {
        struct
        {
            bool use_virt;                  /* Représentatio par défaut    */

        };

        struct
        {
            elf_rel *relocs_to_fill;        /* Tableau à remplir           */

        };

        struct
        {
            elf_rel *relocs;                /* Relocalisations présentes   */
            size_t rel_count;               /* Qté de ces relocalisations  */

            phys_t sym_start;               /* Début de zone des symboles  */
            uint32_t sym_count;             /* Nombre de symboles présents */

            GBinSymbol **imports_to_fill;   /* Liste de symboles constitués*/

        };

        struct
        {
            phys_t global_start;            /* Départ global dans la zone  */
            phys_t global_end;              /* Fin globale dans la zone    */
            virt_t global_addr;             /* Adresse virtuelle initiale  */

            GBinContent *content;           /* Contenu binaire à lire      */
            const bin_t *data;              /* Contenu complet et original */

        };

    };

    /**
     * Gestion du mode de parcours.
     */

    union
    {
        struct
        {
            phys_t begin;                   /* Point de départ du parcours */
            phys_t end;                     /* Point d'arrivée exclu       */

            elf_loading_cb callback_0;      /* Routine de traitement #0    */

        };

        struct
        {
            vmpa2t start;                   /* Point de départ du parcours */

            elf_importing_cb callback_1;    /* Routine de traitement #1    */

        };

    };

    unsigned int kind;                      /* Type de traitements         */
    bool status;                            /* Bilan des traitements       */

    activity_id_t id;                       /* Identifiant pour messages   */

};

/* Fraction de routines à limiter (classe) */
struct _GElfLoadingClass
{
    GDelayedWorkClass parent;               /* A laisser en premier        */

};


/* Initialise la classe des tâches des chargements pour ELF. */
static void g_elf_loading_class_init(GElfLoadingClass *);

/* Initialise une tâche de chargements pour ELF. */
static void g_elf_loading_init(GElfLoading *);

/* Supprime toutes les références externes. */
static void g_elf_loading_dispose(GElfLoading *);

/* Procède à la libération totale de la mémoire. */
static void g_elf_loading_finalize(GElfLoading *);

/* Assure le chargement pour un format ELF en différé. */
static void g_elf_loading_process(GElfLoading *, GtkStatusStack *);



/* Indique le type défini pour les tâches de chargements pour format ELF. */
G_DEFINE_TYPE(GElfLoading, g_elf_loading, G_TYPE_DELAYED_WORK);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des tâches des chargements pour ELF.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_elf_loading_class_init(GElfLoadingClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDelayedWorkClass *work;                /* Version en classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_elf_loading_dispose;
    object->finalize = (GObjectFinalizeFunc)g_elf_loading_finalize;

    work = G_DELAYED_WORK_CLASS(klass);

    work->run = (run_task_fc)g_elf_loading_process;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : loading = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une tâche de chargements pour ELF.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_elf_loading_init(GElfLoading *loading)
{
    loading->status = false;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : loading = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_elf_loading_dispose(GElfLoading *loading)
{
    size_t i;                               /* Boucle de parcours          */

    if (loading->kind == 1)
        for (i = 0; i < loading->rel_count; i++)
            g_clear_object(&loading->imports_to_fill[i]);

    else if (loading->kind == 2)
        g_clear_object(&loading->content);

    G_OBJECT_CLASS(g_elf_loading_parent_class)->dispose(G_OBJECT(loading));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : loading = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_elf_loading_finalize(GElfLoading *loading)
{
    G_OBJECT_CLASS(g_elf_loading_parent_class)->finalize(G_OBJECT(loading));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format    = ensemble d'instructions désassemblées.           *
*                str_start = début des chaînes de caractères à consulter.     *
*                first     = position du premier élément.                     *
*                begin     = point de départ du parcours de liste.            *
*                end       = point d'arrivée exclu du parcours.               *
*                id        = identifiant du message affiché à l'utilisateur.  *
*                callback  = routine de traitements particuliers.             *
*                                                                             *
*  Description : Crée une tâche de chargement pour ELF différée.              *
*                                                                             *
*  Retour      : Tâche créée.                                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GElfLoading *g_elf_loading_new_for_symbols(GElfFormat *format, phys_t str_start, phys_t first, phys_t begin, phys_t end, activity_id_t id, elf_loading_cb callback)
{
    GElfLoading *result;                    /* Tâche à retourner           */
#ifndef NDEBUG
    bool status;                            /* Etat d'une consultation     */
#endif

    result = g_object_new(G_TYPE_ELF_LOADING, NULL);

    result->format = format;

    result->str_start = str_start;

#ifndef NDEBUG
    status = g_generic_config_get_value(get_main_configuration(), MPK_FORMAT_NO_NAME, &result->use_virt);
    assert(status);
#else
    g_generic_config_get_value(get_main_configuration(), MPK_FORMAT_NO_NAME, &result->use_virt);
#endif

    result->begin = begin;
    result->end = end;
    result->callback_0 = callback;

    result->kind = 0;

    result->id = id;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format   = ensemble d'instructions désassemblées.            *
*                begin    = point de départ du parcours de liste.             *
*                end      = point d'arrivée exclu du parcours.                *
*                relocs   = table des relocalisations à remplir.              *
*                id       = identifiant du message affiché à l'utilisateur.   *
*                callback = routine de traitements particuliers.              *
*                                                                             *
*  Description : Crée une tâche de chargement pour ELF différée.              *
*                                                                             *
*  Retour      : Tâche créée.                                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GElfLoading *g_elf_loading_new_for_relocations(GElfFormat *format, phys_t begin, phys_t end, elf_rel *relocs, activity_id_t id, elf_loading_cb callback)
{
    GElfLoading *result;                    /* Tâche à retourner           */

    result = g_object_new(G_TYPE_ELF_LOADING, NULL);

    result->format = format;

    result->str_start = VMPA_NO_PHYSICAL;

    result->relocs_to_fill = relocs;

    result->begin = begin;
    result->end = end;
    result->callback_0 = callback;

    result->kind = 0;

    result->id = id;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format    = ensemble d'instructions désassemblées.           *
*                start     = point de départ du parcours de la PLT.           *
*                str_start = début de la zone contenant les descriptions.     *
*                relocs    = table des relocalisations chargées.              *
*                rel_count = nombre de ces éléments à interpréter.            *
*                sym_start = localisation du début de la zone de symboles.    *
*                sym_count = nombre de descriptions de symbole attendues.     *
*                id        = identifiant du message affiché à l'utilisateur.  *
*                callback  = routine de traitements particuliers.             *
*                                                                             *
*  Description : Crée une tâche de chargement pour ELF différée.              *
*                                                                             *
*  Retour      : Tâche créée.                                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GElfLoading *g_elf_loading_new_for_imported(GElfFormat *format, const vmpa2t *start, phys_t str_start, elf_rel *relocs, size_t rel_count, phys_t sym_start, uint32_t sym_count, activity_id_t id, elf_importing_cb callback)
{
    GElfLoading *result;                    /* Tâche à retourner           */

    result = g_object_new(G_TYPE_ELF_LOADING, NULL);

    result->format = format;

    result->str_start = str_start;

    result->relocs = relocs;
    result->rel_count = rel_count;
    result->sym_start = sym_start;
    result->sym_count = sym_count;

    result->imports_to_fill = calloc(rel_count, sizeof(GBinSymbol *));

    copy_vmpa(&result->start, start);
    result->callback_1 = callback;

    result->kind = 1;

    result->id = id;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format   = ensemble d'instructions désassemblées.            *
*                begin    = point de départ de la zone à traiter.             *
*                end      = point d'arrivée exclu du parcours.                *
*                gb_start = position de départ pour l'ensemble des données.   *
*                gb_end   = position finale dans l'ensemble des données.      *
*                addr     = adresse virtuelle de la position initiale.        *
*                id       = identifiant du message affiché à l'utilisateur.   *
*                callback = routine de traitements particuliers.              *
*                                                                             *
*  Description : Crée une tâche de chargement de chaînes pour ELF différée.   *
*                                                                             *
*  Retour      : Tâche créée.                                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GElfLoading *g_elf_loading_new_for_strings(GElfFormat *format, phys_t begin, phys_t end, phys_t gb_start, phys_t gb_end, virt_t addr, activity_id_t id, elf_loading_cb callback)
{
    GElfLoading *result;                    /* Tâche à retourner           */
    vmpa2t pos;                             /* Tête de lecture             */

    result = g_object_new(G_TYPE_ELF_LOADING, NULL);

    result->format = format;

    result->global_start = gb_start;
    result->global_end = gb_end;
    result->global_addr = addr;

    result->content = g_known_format_get_content(G_KNOWN_FORMAT(format));

    init_vmpa(&pos, gb_start, addr);

    result->data = g_binary_content_get_raw_access(result->content, &pos, gb_end - gb_start);
    if (result->data == NULL) goto no_data;

    result->begin = begin;
    result->end = end;
    result->callback_0 = callback;

    result->kind = 2;

    result->id = id;

    return result;

 no_data:

    g_object_unref(G_OBJECT(result));

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : loading = traitements différés à mener.                      *
*                status  = barre de statut à tenir informée.                  *
*                                                                             *
*  Description : Assure le chargement pour un format ELF en différé.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_elf_loading_process(GElfLoading *loading, GtkStatusStack *status)
{
    GElfFormat *format;                     /* Format plus accessible      */
    phys_t iter;                            /* Boucle de parcours #1       */
    phys_t old;                             /* Sauvegarde du point d'avant */
    bool ret;                               /* Bilan d'un appel            */
    size_t i;                               /* Boucle de parcours #2       */
    GBinSymbol *symbol;                     /* Symbole analysé             */

    format = loading->format;

    switch (loading->kind)
    {
        case 0:

            for (iter = loading->begin; iter < loading->end; )
            {
                old = iter;
                ret = loading->callback_0(loading, format, &iter);

                if (!ret)
                {
                    log_variadic_message(LMT_ERROR, _("Error while loading ELF data @ 0x%08x!"), old);
                    break;
                }

                gtk_status_stack_update_activity_value(status, loading->id, 1);

            }

            loading->status = (iter == loading->end);
            break;

        case 1:

            for (i = 0; i < loading->rel_count; i++)
            {
                symbol = loading->callback_1(loading, format, &loading->start);

                if (symbol == NULL)
                {
                    log_variadic_message(LMT_ERROR, _("Error while applying ELF relocation %zu!"), i);
                    break;
                }

                loading->imports_to_fill[i] = symbol;

                gtk_status_stack_update_activity_value(status, loading->id, 1);

            }

            loading->status = (i == loading->rel_count);
            break;

        case 2:

            for (iter = loading->begin; iter < loading->end; )
            {
                old = iter;

                loading->status |= loading->callback_0(loading, format, &iter);

                gtk_status_stack_update_activity_value(status, loading->id, iter - old);

            }

            break;

        default:
            assert(false);
            break;

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : loading = procédure de chargements écoulés à consulter.      *
*                                                                             *
*  Description : Fournit le bilan des traitements différés.                   *
*                                                                             *
*  Retour      : true si tout s'est bien déroulé.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_elf_loading_get_status(const GElfLoading *loading)
{
    return loading->status;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : loading = chargement pour ELF à mener.                       *
*                name    = indice de la désignation du symbole concerné.      *
*                virt    = adresse virtuelle du symbole en mémoire.           *
*                prefix  = préfixe d'une désignation par défaut.              *
*                alt     = zone de constitution d'un nom alternatif. [OUT]    *
*                addr    = localisation compléte à associer au symbole. [OUT] *
*                                                                             *
*  Description : Construit la désignation adaptée à un symbole.               *
*                                                                             *
*  Retour      : Pointeur vers une étiquette constituée.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_elf_loading_build_name(const GElfLoading *loading, uint32_t name, virt_t virt, const char *prefix, char *alt, vmpa2t *addr)
{
    const char *result;                     /* Désignation à retourner     */
    GElfFormat *format;                     /* Format plus accessible      */
    vmpa2t pos;                             /* Position de lecture         */
    const GBinContent *content;             /* Contenu binaire à lire      */
    size_t plen;                            /* Taille du préfixe           */

    result = NULL;

    format = loading->format;

    if (g_exe_format_translate_address_into_vmpa(G_EXE_FORMAT(format), virt, addr))
    {
        init_vmpa(&pos, loading->str_start + name, VMPA_NO_VIRTUAL);

        content = G_KNOWN_FORMAT(format)->content;

        result = (const char *)g_binary_content_get_raw_access(content, &pos, 1);

        if (result != NULL && result[0] == '\0')
            result = NULL;

        if (result == NULL)
        {
            /**
             * Charge à l'appelant de s'assurer que la zone tampon est assez grande !
             */

            strcpy(alt, prefix);
            plen = strlen(prefix);

            if (loading->use_virt)
                vmpa2_virt_to_string(addr, MDS_UNDEFINED, alt + plen, NULL);
            else
                vmpa2_phys_to_string(addr, MDS_UNDEFINED, alt + plen, NULL);

            result = alt;

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : loading = chargement pour ELF à compléter.                   *
*                iter    = tête de lecture courante.                          *
*                reloc   = relocalisation à conserver en mémoire.             *
*                                                                             *
*  Description : Intègre dans la liste adaptée une relocalisation chargée.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_elf_loading_store_relocation(const GElfLoading *loading, const phys_t *iter, const elf_rel *reloc)
{
    GElfFormat *format;                     /* Format plus accessible      */
    size_t index;                           /* Indice de l'élément         */

    format = loading->format;

    index = (*iter - loading->begin);

    assert(index % sizeof(ELF_SIZEOF_REL(format)) == 0);

    index /= sizeof(ELF_SIZEOF_REL(format));

    /* La tête de lecture a consommé un élément ! */
    index--;

    memcpy(&loading->relocs_to_fill[index], reloc, sizeof(elf_rel));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : loading = chargement pour ELF à consulter.                   *
*                offset = décalage à retrouver idéalement.                    *
*                reloc  = informations quant à la relocalisation. [OUT]       *
*                                                                             *
*  Description : Recherche une relocalisation par son décalage.               *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_elf_loading_search_for_relocation(const GElfLoading *loading, const uint64_t *offset, elf_rel **reloc)
{
    bool result;                            /* Validité à faire remonter   */
    void *found;                            /* Eventuel élément trouvé     */

    int compare_relocations(const uint64_t *off, const elf_rel *rel)
    {
        return sort_uint64_t(*off, ELF_REL(loading->format, *rel, r_offset));
    }

    found = bsearch(offset, loading->relocs, loading->rel_count,
                    sizeof(elf_rel), (__compar_fn_t)compare_relocations);

    result = (found != NULL);

    if (result)
        *reloc = (elf_rel *)found;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : loading = chargement pour ELF à poursuivre.                  *
*                index   = indice du symbole concerné.                        *
*                                                                             *
*  Description : Construit le symbole adapté à un symbole importé.            *
*                                                                             *
*  Retour      : Nouveau symbole constitué ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinSymbol *g_elf_loading_build_plt_symbol(const GElfLoading *loading, uint64_t index)
{
    GBinSymbol *result;                     /* Symbole à retourner         */
    GElfFormat *format;                     /* Format plus accessible      */
    phys_t offset;                          /* Tête de lecture brute       */
    elf_sym sym;                            /* Symbole aux infos visées    */
    bool status;                            /* Bilan de récupération       */
    uint32_t name;                          /* Indice du nom du symbole    */
    vmpa2t pos;                             /* Position de lecture         */
    GBinFormat *base;                       /* Autre version du format     */
    const GBinContent *content;             /* Contenu binaire à lire      */
    const char *raw_label;                  /* Première partie de nom      */
    GBinRoutine *routine;                   /* Routine à mettre en place   */

    format = loading->format;

    offset = loading->sym_start + index * ELF_SIZEOF_SYM(format);

    status = read_elf_symbol(format, &offset, &sym);

    if (!status)
        result = NULL;

    else
    {
        name = ELF_SYM(format, sym, st_name);

        offset = loading->str_start + name;

        init_vmpa(&pos, offset, VMPA_NO_VIRTUAL);

        base = G_BIN_FORMAT(format);
        content = G_KNOWN_FORMAT(base)->content;

        raw_label = (const char *)g_binary_content_get_raw_access(content, &pos, 1);

        if (raw_label != NULL && raw_label[0] == '\0')
            result = NULL;

        else
        {
            routine = g_binary_format_decode_routine(base, raw_label);

            /**
             * L'ajout d'un suffixe "@plt" artificiel est ici supprimé.
             *
             * Si un tel ajout est facile sur des fonctions C classiques
             * (via un appel à g_binary_routine_get_name(), une modification du résultat
             * obtenu puis une mise à jour avec g_binary_routine_set_name()) le traitement
             * des fonctions C++ s'avère plus laborieux.
             *
             * Par exemple, cerner le nom d'une fonction comportant des patrons requiert
             * des opérations pour la mise à jour de ce nom ; et charge à l'utilisateur
             * de procéder à un traitement tout aussi complexe s'il souhaite retrouver
             * le nom d'origine, sans facilité apportée par Chrysalide.
             *
             * On garde en référence à ce titre la fonction _ZN6google8protobuf8internal20RepeatedPtrFieldBase5ClearINS0_16RepeatedPtrFieldIN8pittpatt5proto14DetectedObjectEE11TypeHandlerEEEvv.
             */

            result = G_BIN_SYMBOL(routine);

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : loading = chargement pour ELF à poursuivre.                  *
*                count   = taille de la liste retournée. [OUT]                *
*                                                                             *
*  Description : Fournit la liste de symboles importés constituée.            *
*                                                                             *
*  Retour      : Liste des symboles importés ou NULL en cas d'échec.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinSymbol **g_elf_loading_get_imported_symbols(const GElfLoading *loading, size_t *count)
{
    GBinSymbol **result;                    /* Liste à retourner           */
    size_t i;                               /* Boucle de parcours          */

    *count = loading->rel_count;

    result = malloc(*count * sizeof(GBinSymbol *));

    for (i = 0; i < *count; i++)
    {
        result[i] = loading->imports_to_fill[i];
        assert(result[i] != NULL);

        g_object_ref(G_OBJECT(result[i]));

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : loading = chargement pour ELF à mener.                       *
*                content = gestionnaire de contenu utilisé. [OUT]             *
*                first   = première position traitée par la tâche. [OUT]      *
*                offset  = décalage pour les données. [OUT]                   *
*                final   = première position dans les données à exclure. [OUT]*
*                                                                             *
*  Description : Donne les informations utiles à la recherche de chaînes.     *
*                                                                             *
*  Retour      : Données brutes à analyser.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const bin_t *g_elf_loading_get_info_for_strings(const GElfLoading *loading, GBinContent **content, phys_t *first, phys_t *offset, phys_t *final)
{
    const bin_t *result;                    /* Données à communiquer       */

    result = loading->data;

    *content = loading->content;
    *first = loading->begin;
    *offset = loading->global_start;
    *final = loading->global_end;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : loading = chargement pour ELF à poursuivre.                  *
*                iter    = point de départ dans la zone de données traitée.   *
*                pos     = emplacement construit à la demande. [OUT]          *
*                                                                             *
*  Description : Détermine l'adresse de départ d'une chaîne avec une position.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_elf_loading_compute_string_address(const GElfLoading *loading, const phys_t *iter, vmpa2t *pos)
{
    init_vmpa(pos, *iter, loading->global_addr + (*iter - loading->global_start));

}
