
/* Chrysalide - Outil d'analyse de fichiers binaires
 * strings.c - recherche des chaînes contenues dans un ELF
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


#include "strings.h"


#include <assert.h>
#include <ctype.h>
#include <malloc.h>
#include <sys/param.h>


#include <i18n.h>


#include <arch/instructions/raw.h>
#include <core/global.h>
#include <core/nproc.h>
#include <format/strsym.h>


#include "elf-int.h"
#include "loading.h"
#include "section.h"



/**
 * Petit complément, sur la base de :
 * http://www.cplusplus.com/reference/cctype/
 *
 * On veut identifier '\t', '\f','\v','\n','\r', mais sans les caractères
 * de contrôle, ni les espaces.
 */

#define isctrledspace(c) (isspace(c) && c != ' ')


/* Lance les vagues de chargement des chaînes de caractères. */
static bool parse_elf_string_data(GElfFormat *, phys_t, phys_t, virt_t, GWorkQueue *, wgroup_id_t, GtkStatusStack *, activity_id_t);

/* Enregistre toutes les chaînes de caractères trouvées. */
static bool do_elf_string_loading(GElfLoading *, GElfFormat *, phys_t *);



/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à analyser.             *
*                gid    = groupe de travail impliqué.                         *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Charge en mémoire toutes les chaînes trouvées.               *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool find_all_elf_strings(GElfFormat *format, wgroup_id_t gid, GtkStatusStack *status)
{
    activity_id_t msg;                      /* Message de progression      */
    GWorkQueue *queue;                      /* Gestionnaire de différés    */
    bool got_string;                        /* Indique un remplissage      */
    phys_t str_start;                       /* Début de section            */
    phys_t str_size;                        /* Taille de section           */
    virt_t str_addr;                        /* Adresse virtuelle associée  */
    elf_shdr *sections;                     /* Groupe de sections trouvées */
    size_t count;                           /* Quantité de données         */
    size_t i;                               /* Boucle de parcours #1       */
    phys_t max;                             /* Borne à ne pas dépasser     */
    phys_t iter;                            /* Boucle de parcours #2       */
    elf_phdr phdr;                          /* En-tête de programme ELF    */

    msg = gtk_status_stack_add_activity(status, _("Finding all existing strings..."), 0);

    queue = get_work_queue();

    got_string = false;

    /* Données en lecture seule */

    if (find_elf_section_content_by_name(format, ".rodata", &str_start, &str_size, &str_addr))
        got_string |= parse_elf_string_data(format, str_start, str_size, str_addr,
                                            queue, gid, status, msg);

    else
    {
        if (find_elf_sections_by_type(format, SHT_PROGBITS, &sections, &count))
        {
            for (i = 0; i < count; i++)
                if (ELF_SHDR(format, sections[i], sh_flags) == SHF_ALLOC
                    || (ELF_SHDR(format, sections[i], sh_flags) & SHF_STRINGS))
                {
                    get_elf_section_content(format, &sections[i], &str_start, &str_size, &str_addr);
                    got_string |= parse_elf_string_data(format, str_start, str_size, str_addr,
                                                        queue, gid, status, msg);
                }

            free(sections);

        }

    }

    /* Chaîne de caractères déclarées */

    if (find_elf_sections_by_type(format, SHT_STRTAB, &sections, &count))
    {
        for (i = 0; i < count; i++)
        {
            get_elf_section_content(format, &sections[i], &str_start, &str_size, &str_addr);
            got_string |= parse_elf_string_data(format, str_start, str_size, str_addr,
                                                queue, gid, status, msg);
        }

        free(sections);

    }

    /* En désespoir de cause, on se rabbat sur les parties de programme directement */

    if (!got_string)
    {
        max = ELF_HDR(format, format->header, e_phoff)
            + ELF_HDR(format, format->header, e_phnum) * ELF_SIZEOF_PHDR(format);

        for (iter = ELF_HDR(format, format->header, e_phoff); iter < max; iter += ELF_SIZEOF_PHDR(format))
        {
            if (!read_elf_program_header(format, iter, &phdr))
                continue;

            if (ELF_PHDR(format, phdr, p_flags) & PF_R
                && !(ELF_PHDR(format, phdr, p_flags) & PF_X))
                parse_elf_string_data(format,
                                      ELF_PHDR(format, phdr, p_offset),
                                      ELF_PHDR(format, phdr, p_filesz),
                                      ELF_PHDR(format, phdr, p_vaddr),
                                      queue, gid, status, msg);

        }

    }

    gtk_status_stack_remove_activity(status, msg);

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format  = description de l'exécutable à compléter.           *
*                start   = début de la zone à parcourir.                      *
*                size    = taille de l'espace à parcourir.                    *
*                address = adresse virtuelle du début de la section.          *
*                wq      = espace de travail dédié.                           *
*                gid     = groupe de travail impliqué.                        *
*                status  = barre de statut à tenir informée.                  *
*                msg     = identifiant du message de progression.             *
*                                                                             *
*  Description : Lance les vagues de chargement des chaînes de caractères.    *
*                                                                             *
*  Retour      : true si des chaînes ont été ajoutées, ou false.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool parse_elf_string_data(GElfFormat *format, phys_t start, phys_t size, virt_t address, GWorkQueue *wq, wgroup_id_t gid, GtkStatusStack *status, activity_id_t msg)
{
    bool result;                            /* Bilan à retourner           */
    phys_t final;                           /* Position finale à atteindre */
    guint runs_count;                       /* Qté d'exécutions parallèles */
    phys_t run_size;                        /* Volume réparti par exécution*/
    guint i;                                /* Boucle de parcours          */
    phys_t begin;                           /* Début de zone de traitement */
    phys_t end;                             /* Fin d'un zone de traitement */
    GElfLoading **loadings;                 /* Tâches de chargement lancées*/

    result = false;

    if (address > 0)
    {
        final = start + size;

        run_size = compute_run_size(size, &runs_count);

        gtk_status_stack_extend_activity(status, msg, size);

        loadings = (GElfLoading **)malloc(runs_count * sizeof(GElfLoading *));

        for (i = 0; i < runs_count; i++)
        {
            begin = start + i * run_size;

            if ((i + 1) == runs_count)
                end = final;
            else
                end = begin + run_size;

            loadings[i] = g_elf_loading_new_for_strings(format, begin, end, start, start + size, address,
                                                        msg, do_elf_string_loading);

            if (loadings[i] != NULL)
            {
                g_object_ref(G_OBJECT(loadings[i]));
                g_work_queue_schedule_work(wq, G_DELAYED_WORK(loadings[i]), gid);
            }

        }

        g_work_queue_wait_for_completion(wq, gid);

        for (i = 0; i < runs_count; i++)
        {
            if (loadings[i] == NULL)
                continue;

            result |= g_elf_loading_get_status(loadings[i]);

            g_object_unref(G_OBJECT(loadings[i]));

        }

        free(loadings);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : loading = chargement de chaînes de caractères en cours.      *
*                format  = format ELF à compléter.                            *
*                iter    = tête de lecture évoluant avec le temps. [OUT]      *
*                                                                             *
*  Description : Enregistre toutes les chaînes de caractères trouvées.        *
*                                                                             *
*  Retour      : true si au moins une chaîne a été insérée.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool do_elf_string_loading(GElfLoading *loading, GElfFormat *format, phys_t *iter)
{
    bool result;                            /* Bilan à retourner           */
    GBinFormat *base;                       /* Autre version du format     */
    GBinContent *content;                   /* Contenu binaire à lire      */
    phys_t first;                           /* Première position traitée   */
    phys_t offset;                          /* Décalage pour les données   */
    phys_t final;                           /* Point global de fin de zone */
    const bin_t *data;                      /* Contenu complet et original */
    phys_t end;                             /* Position de fin de chaîne   */
    vmpa2t pos;                             /* Tête de lecture             */
    GArchInstruction *instr;                /* Instruction décodée         */
    bool inserted;                          /* Bilan d'une insertion       */
    const mrange_t *range;                  /* Espace occupé par une chaîne*/
    GBinSymbol *symbol;                     /* Symbole à intégrer          */
    bool cut;                               /* Coupure par étiquette ?     */

    result = false;

    /* Préparation des accès */

    base = G_BIN_FORMAT(format);

    data = g_elf_loading_get_info_for_strings(loading, &content, &first, &offset, &final);

    /* Analyse des données */

    if (isprint(data[*iter - offset]) || isctrledspace(data[*iter - offset]))
    {
        for (end = *iter; end < final; end++)
            if (!isprint(data[end - offset])) break;

        for (; end < final; end++)
            if (!isctrledspace(data[end - offset])) break;

        if (end < final && data[end - offset] == '\0')
            end++;

        if ((first - offset) > 0 && *iter == first)
        {
            /**
             * Si une tâche précédente si termine par un caratère valable,
             * elle va étendre sa chaîne jusqu'à intégrer notre chaîne initiale.
             *
             * Rien ne sert donc de poursuivre, on saute ici cette première chaîne.
             */

            if (isprint(data[first - 1 - offset]))
            {
                /**
                 * Le seul truc, c'est que l'autre chaîne peut se terminer par isctrledspace(),
                 * et que la notre peut commencer par le même type de caractères.
                 *
                 * Donc la chaîne qui déborde peut ne pas couvrir entièrement notre chaîne.
                 *
                 * On repositionne donc notre fin à la fin de la chaîne précédente.
                 */

                for (end = *iter; end < final; end++)
                    if (!isprint(data[end - offset])) break;

                for (; end < final; end++)
                    if (!isctrledspace(data[end - offset])) break;

                goto skip_first;

            }

        }

        g_elf_loading_compute_string_address(loading, iter, &pos);

        instr = g_raw_instruction_new_array(content, MDS_8_BITS, end - *iter, &pos, format->endian);
        assert(instr != NULL);

        g_raw_instruction_mark_as_string(G_RAW_INSTRUCTION(instr), true);

        /**
         * Comme g_preload_info_add_instruction() peut consommer l'instruction
         * et qu'on réutilise cette dernière ensuite avec g_arch_instruction_get_range()...
         */
        g_object_ref(G_OBJECT(instr));

        inserted = g_preload_info_add_instruction(base->info, instr);

        result |= inserted;

        if (inserted)
        {
            range = g_arch_instruction_get_range(instr);

            symbol = g_string_symbol_new_read_only(SET_GUESS, G_KNOWN_FORMAT(base), range);

            g_object_ref(G_OBJECT(symbol));

            g_binary_format_add_symbol(base, symbol);

            /* Jointure avec la chaîne précédente ? */

            if ((first - offset) == 0)
                cut = true;
            else
                cut = (data[*iter - offset - 1] == '\0');

            if (cut)
                g_string_symbol_build_label(G_STR_SYMBOL(symbol), base);

            g_object_unref(G_OBJECT(symbol));

        }

        g_object_unref(G_OBJECT(instr));

        /* Conclusion */

 skip_first:

        *iter = end;

    }

    else
        (*iter)++;

    return result;

}
