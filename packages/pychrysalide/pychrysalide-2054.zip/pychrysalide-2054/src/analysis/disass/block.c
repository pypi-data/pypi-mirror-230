
/* Chrysalide - Outil d'analyse de fichiers binaires
 * block.c - encadrement des instructions par blocs
 *
 * Copyright (C) 2016-2019 Cyrille Bagard
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


#include "block.h"


#include <assert.h>
#include <malloc.h>


#include <i18n.h>


#include "../block-int.h"
#include "../../arch/instructions/raw.h"
#include "../../common/extstr.h"
#include "../../core/columns.h"
#include "../../core/params.h"
#include "../../glibext/gbinarycursor.h"



/* ------------------------ MISE EN PLACE DES BLOCS BASIQUES ------------------------ */


/* Description d'un bloc basique d'instructions (instance) */
struct _GBasicBlock
{
    GCodeBlock parent;                      /* A laisser en premier        */

    /* Référence circulaire */
    GLoadedBinary *binary;                  /* Binaire chargé et associé   */

    GArchInstruction *first;                /* Première instruction        */
    GArchInstruction *last;                 /* Dernière instruction        */

};

/* Description d'un bloc basique d'instructions (classe) */
struct _GBasicBlockClass
{
    GCodeBlockClass parent;                 /* A laisser en premier        */

};


/* Initialise la classe des blocs d'instructions basique. */
static void g_basic_block_class_init(GBasicBlockClass *);

/* Initialise un bloc d'instructions basique. */
static void g_basic_block_init(GBasicBlock *);

/* Supprime toutes les références externes. */
static void g_basic_block_dispose(GBasicBlock *);

/* Procède à la libération totale de la mémoire. */
static void g_basic_block_finalize(GBasicBlock *);

/* Détermine si un bloc de code contient une adresse donnée. */
static bool g_basic_block_contains_addr(const GBasicBlock *, const vmpa2t *);

/* Compare deux liens entre blocs de code. */
static int g_basic_block_compare_links(const block_link_t *, const block_link_t *);

/* Fournit les détails des origines d'un bloc de code donné. */
static block_link_t *g_basic_block_get_sources(const GBasicBlock *, const GBlockList *, size_t *);

/* Fournit les détails des destinations de bloc de code. */
static block_link_t *g_basic_block_get_destinations(const GBasicBlock *, const GBlockList *, size_t *);

#ifdef INCLUDE_GTK_SUPPORT

/* Fournit la représentation graphique d'un bloc de code. */
static GBufferView *g_basic_block_build_view(const GBasicBlock *, segcnt_list *);

/* Construit un ensemble d'indications pour bloc. */
static char *g_basic_block_build_tooltip(const GBasicBlock *);

#endif



/* ---------------------------------------------------------------------------------- */
/*                          MISE EN PLACE DES BLOCS BASIQUES                          */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un bloc d'instructions basique. */
G_DEFINE_TYPE(GBasicBlock, g_basic_block, G_TYPE_CODE_BLOCK);


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des blocs d'instructions basique.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_basic_block_class_init(GBasicBlockClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GCodeBlockClass *block;                 /* Version parente de la classe*/

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_basic_block_dispose;
    object->finalize = (GObjectFinalizeFunc)g_basic_block_finalize;

    block = G_CODE_BLOCK_CLASS(class);

    block->contains = (block_contains_fc)g_basic_block_contains_addr;
    block->cmp_links = (block_compare_links_fc)g_basic_block_compare_links;
    block->get_src = (block_get_links_fc)g_basic_block_get_sources;
    block->get_dest = (block_get_links_fc)g_basic_block_get_destinations;
#ifdef INCLUDE_GTK_SUPPORT
    block->build = (block_build_view_fc)g_basic_block_build_view;
    block->build_tooltip = (block_build_tooltip_fc)g_basic_block_build_tooltip;
#endif

}


/******************************************************************************
*                                                                             *
*  Paramètres  : block = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise un bloc d'instructions basique.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_basic_block_init(GBasicBlock *block)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : block = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_basic_block_dispose(GBasicBlock *block)
{
    //g_clear_object(&block->first);
    //g_clear_object(&block->last);

    G_OBJECT_CLASS(g_basic_block_parent_class)->dispose(G_OBJECT(block));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : block = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_basic_block_finalize(GBasicBlock *block)
{
    G_OBJECT_CLASS(g_basic_block_parent_class)->finalize(G_OBJECT(block));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = binaire chargé contenant les instructions.          *
*                first  = première instruction du bloc.                       *
*                last   = dernière instruction du bloc.                       *
*                bits   = liste des blocs dominés.                            *
*                                                                             *
*  Description : Crée un bloc basique d'exécution d'instructions.             *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GCodeBlock *g_basic_block_new(GLoadedBinary *binary, GArchInstruction *first, GArchInstruction *last, const bitfield_t *bits)
{
    GBasicBlock *result;                    /* Structure à retourner       */
    GCodeBlock *parent;                     /* Version parente d'instance  */

    result = g_object_new(G_TYPE_BASIC_BLOCK, NULL);

    result->binary = binary;

    result->first = first;
    result->last = last;

    //g_object_ref(G_OBJECT(first));
    //g_object_ref(G_OBJECT(last));

    parent = G_CODE_BLOCK(result);

    parent->domination = dup_bit_field(bits);

    return parent;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : block = bloc de code à consulter.                            *
*                addr  = localisation à comparer.                             *
*                                                                             *
*  Description : Détermine si un bloc de code contient une adresse donnée.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_basic_block_contains_addr(const GBasicBlock *block, const vmpa2t *addr)
{
    bool result;                            /* Bilan à retourner           */
    const mrange_t *frange;                 /* Couverture d'instruction #1 */
    const mrange_t *lrange;                 /* Couverture d'instruction #2 */
    phys_t diff;                            /* Ecart entre les positions   */
    mrange_t coverage;                      /* Couverture du bloc          */

    frange = g_arch_instruction_get_range(block->first);

    result = (cmp_vmpa(addr, get_mrange_addr(frange)) == 0);

    if (!result)
    {
        lrange = g_arch_instruction_get_range(block->last);

        result = (cmp_vmpa(addr, get_mrange_addr(lrange)) == 0);

        if (!result)
        {
            diff = compute_vmpa_diff(get_mrange_addr(frange), get_mrange_addr(lrange));
            diff += get_mrange_length(lrange);

            init_mrange(&coverage, get_mrange_addr(frange), diff);

            result = mrange_contains_addr(&coverage, addr);

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : link_a = premier lien à traiter.                             *
*                link_b = second lien à traiter.                              *
*                                                                             *
*  Description : Compare deux liens entre blocs de code.                      *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int g_basic_block_compare_links(const block_link_t *link_a, const block_link_t *link_b)
{
    int result;                             /* Bilan à retourner           */
    const mrange_t *range_a;                /* Couverture d'instruction #1 */
    const mrange_t *range_b;                /* Couverture d'instruction #2 */

    range_a = g_arch_instruction_get_range(G_BASIC_BLOCK(link_a->linked)->first);
    range_b = g_arch_instruction_get_range(G_BASIC_BLOCK(link_b->linked)->first);

    result = cmp_mrange(range_a, range_b);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : block = bloc dont les informations sont à consulter.         *
*                list  = ensemble des blocs de code à disposition.            *
*                count = nombre de ces origines. [OUT]                        *
*                                                                             *
*  Description : Fournit les détails des origines d'un bloc de code donné.    *
*                                                                             *
*  Retour      : Liens déterminés vers des blocs de code d'origine.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static block_link_t *g_basic_block_get_sources(const GBasicBlock *block, const GBlockList *list, size_t *count)
{
    block_link_t *result;                   /* Détails présents à renvoyer */
    size_t scount;                          /* Nombre de liens d'origine   */
    size_t i;                               /* Boucle de parcours          */
    const instr_link_t *src;                /* Instr. visée par une autre  */
    const mrange_t *range;                  /* Couverture d'instruction    */
    GCodeBlock *target;                     /* Bloc ciblé par un lien      */
    block_link_t *new;                      /* Nouvelle entrée à définir   */

    result = NULL;
    *count = 0;

    g_arch_instruction_lock_src(block->first);
    scount = g_arch_instruction_count_sources(block->first);

    for (i = 0; i < scount; i++)
    {
        src = g_arch_instruction_get_source(block->first, i);

        range = g_arch_instruction_get_range(src->linked);

        target = g_block_list_find_by_addr(list, get_mrange_addr(range));

        /**
         * Les liens ne sont pas toujours internes !
         */

        if (target != NULL)
        {
            result = realloc(result, ++(*count) * sizeof(block_link_t));

            new = &result[*count - 1];

            new->linked = target;
            new->type = src->type;

            /**
             * On pourrait par optimisation retirer les deux lignes suivantes...
             */

            ref_block_link(new);

            g_object_unref(G_OBJECT(target));

        }

        unref_instr_link(src);

    }

    g_arch_instruction_unlock_src(block->first);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : block = bloc dont les informations sont à consulter.         *
*                list  = ensemble des blocs de code à disposition.            *
*                count = nombre de ces destinations. [OUT]                    *
*                                                                             *
*  Description : Fournit les détails des destinations de bloc de code.        *
*                                                                             *
*  Retour      : Liens déterminés vers des blocs de code de destination.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static block_link_t *g_basic_block_get_destinations(const GBasicBlock *block, const GBlockList *list, size_t *count)
{
    block_link_t *result;                   /* Détails présents à renvoyer */
    size_t dcount;                          /* Nombre de liens de dest.    */
    size_t i;                               /* Boucle de parcours          */
    const instr_link_t *dest;               /* Instr. visée par une autre  */
    const mrange_t *range;                  /* Couverture d'instruction    */
    GCodeBlock *target;                     /* Bloc ciblé par un lien      */
    block_link_t *new;                      /* Nouvelle entrée à définir   */

    result = NULL;
    *count = 0;

    g_arch_instruction_lock_dest(block->last);
    dcount = g_arch_instruction_count_destinations(block->last);

    for (i = 0; i < dcount; i++)
    {
        dest = g_arch_instruction_get_destination(block->last, i);

        range = g_arch_instruction_get_range(dest->linked);

        target = g_block_list_find_by_addr(list, get_mrange_addr(range));

        /**
         * Les sauts ne se font pas toujours à l'intérieur d'une même fonction.
         * Par exemple sous ARM :
         *
         *    00008358 <call_gmon_start>:
         *        ....
         *        8362:       f7ff bfcf       b.w     8304 <_init+0x38>
         *        ....
         *
         */

        if (target != NULL)
        {
            result = realloc(result, ++(*count) * sizeof(block_link_t));

            new = &result[*count - 1];

            new->linked = target;
            new->type = dest->type;

            /**
             * On pourrait par optimisation retirer les deux lignes suivantes...
             */

            ref_block_link(new);

            g_object_unref(G_OBJECT(target));

        }

        unref_instr_link(dest);

    }

    g_arch_instruction_unlock_dest(block->last);

    return result;

}


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : block       = bloc de code à manipuler.                      *
*                highlighted = gestionnaire de surbrillance pour segments.    *
*                                                                             *
*  Description : Fournit la représentation graphique d'un bloc de code.       *
*                                                                             *
*  Retour      : Vue d'un cache de lignes.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GBufferView *g_basic_block_build_view(const GBasicBlock *block, segcnt_list *highlighted)
{
    GBufferView *result;                    /* Instance à retourner        */
    const mrange_t *first_range;            /* Couverture d'instruction #1 */
    const mrange_t *last_range;             /* Couverture d'instruction #2 */
    GLineCursor *start;                     /* Départ de zone couverture   */
    GLineCursor *end;                       /* Fin de zone couverture      */
    GBufferCache *cache;                    /* Tampon brut à découper      */

    first_range = g_arch_instruction_get_range(block->first);
    last_range = g_arch_instruction_get_range(block->last);

    start = g_binary_cursor_new();
    g_binary_cursor_update(G_BINARY_CURSOR(start), get_mrange_addr(first_range));

    end = g_binary_cursor_new();
    g_binary_cursor_update(G_BINARY_CURSOR(end), get_mrange_addr(last_range));

    cache = g_loaded_binary_get_disassembly_cache(block->binary);

    result = g_buffer_view_new(cache, highlighted);

    g_buffer_view_restrict(result, start, end);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : block = bloc de code à consulter.                            *
*                                                                             *
*  Description : Construit un ensemble d'indications pour bloc.               *
*                                                                             *
*  Retour      : Informations à présenter sous forme de bulle d'aide.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_basic_block_build_tooltip(const GBasicBlock *block)
{
    char *result;                           /* Description à retourner     */
    const mrange_t *brange[2];              /* Emplacements d'instruction  */
    phys_t diff;                            /* Espacement entre adresses   */
    mrange_t range;                         /* Couverture du bloc          */
    char *name;                             /* Désignation de l'entête     */
    GBinFormat *format;                     /* Format associé au binaire   */
    GBinSymbol *symbol;                     /* Symbole lié au bloc         */
    char *label;                            /* Etiquette à insérer         */
    GBufferCache *cache;                    /* Tampon d'impression colorée */
    GBufferLine *line;                      /* Ligne au contenu coloré     */
    VMPA_BUFFER(loc);                       /* Indication de position      */
    GGenConfig *config;                     /* Configuration à consulter   */
    unsigned int max_calls;                 /* Quantité d'appels à afficher*/
    unsigned int max_strings;               /* Nbre de chaînes à afficher  */
    unsigned int ins_count;                 /* Quantité d'instructions     */
    unsigned int call_count;                /* Quantité d'appels           */
    char *call_info;                        /* Détails des appels          */
    unsigned int string_count;              /* Quantité de chaînes         */
    char *string_info;                      /* Détails des chaînes         */
    GArchProcessor *proc;                   /* Architecture utilisée       */
    instr_iter_t *iter;                     /* Parcours local d'adresses   */
    GArchInstruction *instr;                /* Instruction correspondante  */
    size_t dcount;                          /* Nombre de liens de dest.    */
    size_t i;                               /* Boucle de parcours          */
    const instr_link_t *dest;               /* Instr. visée par une autre  */
    const mrange_t *irange;                 /* Emplacement d'instruction   */
    GLineCursor *cursor;                    /* Emplacement dans un tampon  */
    size_t index;                           /* Indice de ligne à traiter   */
    char *info;                             /* Ligne d'information créée   */

    /* Définition de la couverture du bloc */

    brange[0] = g_arch_instruction_get_range(block->first);
    brange[1] = g_arch_instruction_get_range(block->last);

    diff = compute_vmpa_diff(get_mrange_addr(brange[0]), get_mrange_addr(brange[1]));

    init_mrange(&range, get_mrange_addr(brange[0]), diff + get_mrange_length(brange[1]));

    /* Recherche d'un symbole de départ */

    name = NULL;

    format = G_BIN_FORMAT(g_loaded_binary_get_format(block->binary));

    if (g_binary_format_find_symbol_at(format, get_mrange_addr(brange[0]), &symbol))
    {
        label = g_binary_symbol_get_label(symbol);

        if (label != NULL)
        {
            cache = g_buffer_cache_new(NULL, DLC_COUNT, DLC_ASSEMBLY_LABEL);

            g_buffer_cache_wlock(cache);

            g_buffer_cache_append(cache, G_LINE_GENERATOR(symbol), BLF_NONE);

            line = g_buffer_cache_find_line_by_index(cache, 0);
            name = g_buffer_line_get_text(line, DLC_ASSEMBLY_LABEL, DLC_COUNT, true);
            g_object_unref(G_OBJECT(line));

            g_buffer_cache_wunlock(cache);

            g_object_unref(G_OBJECT(cache));

            /* Suppression de la fin de l'étiquette... */
            name = strrpl(name, ":", "");

        }

        else
            name = NULL;

        free(label);

        g_object_unref(G_OBJECT(symbol));

    }

    if (name == NULL)
    {
        proc = g_loaded_binary_get_processor(block->binary);

        if (g_arch_processor_has_virtual_space(proc) && has_virt_addr(get_mrange_addr(&range)))
            vmpa2_virt_to_string(get_mrange_addr(&range), MDS_UNDEFINED, loc, NULL);
        else
            vmpa2_phys_to_string(get_mrange_addr(&range), MDS_UNDEFINED, loc, NULL);

        name = strdup(loc);

        g_object_unref(G_OBJECT(proc));

    }

    result = name;

    /* Lecture des paramètres de configuration */

    config = get_main_configuration();

    if (!g_generic_config_get_value(config, MPK_TOOLTIP_MAX_CALLS, &max_calls))
        max_calls = 0;

    max_calls++;

    if (!g_generic_config_get_value(config, MPK_TOOLTIP_MAX_STRINGS, &max_strings))
        max_strings = 0;

    max_strings++;

    /* Parcours des instructions */

    ins_count = 0;

    call_count = 0;
    call_info = NULL;

    string_count = 0;
    string_info = NULL;

    proc = g_loaded_binary_get_processor(block->binary);
    cache = g_loaded_binary_get_disassembly_cache(block->binary);

    g_buffer_cache_rlock(cache);

    iter = g_arch_processor_get_iter_from_address(proc, get_mrange_addr(&range));
    if (iter == NULL) goto no_iter;

    restrict_instruction_iterator(iter, &range);

    for (instr = get_instruction_iterator_current(iter);
         instr != NULL;
         instr = get_instruction_iterator_next(iter))
    {
        ins_count ++;

        /* Appels ou références ? */

        g_arch_instruction_lock_dest(instr);
        dcount = g_arch_instruction_count_destinations(instr);

        for (i = 0; i < dcount; i++)
        {
            dest = g_arch_instruction_get_destination(instr, i);

            switch (dest->type)
            {
                case ILT_CALL:

                    call_count++;

                    if (call_count > max_calls)
                        goto next_dest;

                    if (call_count == max_calls)
                    {
                        call_info = stradd(call_info, "\n    ...");
                        goto next_dest;
                    }

                    irange = g_arch_instruction_get_range(instr);

                    cursor = g_binary_cursor_new();
                    g_binary_cursor_update(G_BINARY_CURSOR(cursor), get_mrange_addr(irange));

                    index = g_buffer_cache_find_index_by_cursor(cache, cursor, true);

                    g_object_unref(G_OBJECT(cursor));

                    index = g_buffer_cache_look_for_flag(cache, index, BLF_HAS_CODE);

                    line = g_buffer_cache_find_line_by_index(cache, index);

                    if (line != NULL)
                    {
                        info = g_buffer_line_get_text(line, DLC_ASSEMBLY_HEAD, DLC_COUNT, true);
                        g_object_unref(G_OBJECT(line));
                    }

                    else
                        info = NULL;

                    if (call_info != NULL)
                        call_info = stradd(call_info, "\n");

                    if (info != NULL)
                    {
                        call_info = stradd(call_info, "    - ");
                        call_info = stradd(call_info, info);
                        free(info);
                    }

                    else
                        call_info = stradd(call_info, "    - ???");

                    break;

                case ILT_REF:

                    if (!G_IS_RAW_INSTRUCTION(dest->linked))
                        goto next_dest;

                    if (!g_raw_instruction_is_string(G_RAW_INSTRUCTION(dest->linked)))
                        goto next_dest;

                    string_count++;

                    if (string_count > max_strings)
                        goto next_dest;

                    if (string_count == max_strings)
                    {
                        string_info = stradd(string_info, "\n    ...");
                        goto next_dest;
                    }

                    irange = g_arch_instruction_get_range(dest->linked);

                    cursor = g_binary_cursor_new();
                    g_binary_cursor_update(G_BINARY_CURSOR(cursor), get_mrange_addr(irange));

                    index = g_buffer_cache_find_index_by_cursor(cache, cursor, true);

                    g_object_unref(G_OBJECT(cursor));

                    index = g_buffer_cache_look_for_flag(cache, index, BLF_HAS_CODE);

                    line = g_buffer_cache_find_line_by_index(cache, index);

                    if (line != NULL)
                    {
                        info = g_buffer_line_get_text(line, DLC_ASSEMBLY, DLC_COUNT, true);
                        g_object_unref(G_OBJECT(line));
                    }

                    else
                        info = NULL;

                    if (string_info != NULL)
                        string_info = stradd(string_info, "\n");

                    if (info != NULL)
                    {
                        string_info = stradd(string_info, "    - ");
                        string_info = stradd(string_info, info);
                        free(info);
                    }

                    else
                        string_info = stradd(string_info, "    - ???");

                    break;

                default:
                    break;

            }

 next_dest:

            unref_instr_link(dest);

        }

        g_arch_instruction_unlock_dest(instr);

        g_object_unref(G_OBJECT(instr));

    }

    delete_instruction_iterator(iter);

 no_iter:

    g_buffer_cache_runlock(cache);

    g_object_unref(G_OBJECT(cache));
    g_object_unref(G_OBJECT(proc));

    /* Construction du résumé */

    result = stradd(result, "\n");

    if (ins_count > 1)
        asprintf(&info, " - %u %s", ins_count, _("instructions"));
    else
        asprintf(&info, " - %u %s", ins_count, _("instruction"));

    result = stradd(result, info);
    free(info);

    result = stradd(result, "\n");

    if (call_count > 1)
        asprintf(&info, " - %u %s", call_count, _("calls:"));
    else if (call_count == 1)
        asprintf(&info, " - 1 %s", _("call:"));
    else
        asprintf(&info, " - 0 %s", _("call"));

    if (call_count > 0)
    {
        info = stradd(info, "\n");
        info = stradd(info, call_info);
        free(call_info);
    }

    info = stradd(info, "\n");

    result = stradd(result, info);
    free(info);

    if (string_count > 1)
        asprintf(&info, " - %u %s", string_count, _("strings:"));
    else if (string_count == 1)
        asprintf(&info, " - 1 %s", _("string:"));
    else
        asprintf(&info, " - 0 %s", _("string"));

    if (string_count > 0)
    {
        info = stradd(info, "\n");
        info = stradd(info, string_info);
        free(string_info);
    }

    result = stradd(result, info);
    free(info);

    return result;

}


#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : block = bloc d'instructions à consulter.                     *
*                first = instruction de départ du bloc. [OUT]                 *
*                last  = dernière instruction du bloc. [OUT]                  *
*                                                                             *
*  Description : Fournit les instructions limites d'un bloc basique.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_basic_block_get_boundaries(const GBasicBlock *block, GArchInstruction **first, GArchInstruction **last)
{
    if (first != NULL)
    {
        *first = block->first;
        g_object_ref(G_OBJECT(*first));
    }

    if (last != NULL)
    {
        *last = block->last;
        g_object_ref(G_OBJECT(*last));
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : block = bloc d'instructions à consulter.                     *
*                proc  = processeur contenant l'ensemble des instructions.    *
*                                                                             *
*  Description : Fournit un itérateur d'instructions limité au bloc basique.  *
*                                                                             *
*  Retour      : Itérateur mis en place ou NULL en cas d'échec.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

instr_iter_t *g_basic_block_get_iterator(const GBasicBlock *block, GArchProcessor *proc)
{
    instr_iter_t *result;                   /* Itérateur à renvoyer        */
    const mrange_t *first_range;            /* Emplacement d'instruction #1*/
    const vmpa2t *first_addr;               /* Point de départ associé     */
    const mrange_t *last_range;             /* Emplacement d'instruction #2*/
    phys_t length;                          /* Taille de la couverture     */
    mrange_t range;                         /* Couverture du bloc          */

    first_range = g_arch_instruction_get_range(block->first);

    first_addr = get_mrange_addr(first_range);

    result = g_arch_processor_get_iter_from_address(proc, first_addr);

    if (result != NULL)
    {
        last_range = g_arch_instruction_get_range(block->last);

        length = compute_vmpa_diff(first_addr, get_mrange_addr(last_range));
        length += get_mrange_length(last_range);

        init_mrange(&range, first_addr, length);

        restrict_instruction_iterator(result, &range);

    }

    return result;

}
