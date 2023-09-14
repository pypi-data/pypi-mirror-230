
/* Chrysalide - Outil d'analyse de fichiers binaires
 * info.c - lecture des informations principales du format DWARF
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


#include "info.h"


#include <i18n.h>
#include <analysis/contents/restricted.h>
#include <core/nproc.h>
#include <glibext/seq.h>
#include <core/global.h>


#include "die.h"
#include "format-int.h"
#include "utils.h"



#define RANGE_ALLOC_BLOCK 100


/* Rassemblement des informations utiles */
typedef struct _work_data
{
    GDwarfFormat *format;                   /* Format à manipuler          */
    mrange_t *ranges;                       /* Espace des DIE à charger    */

} work_data;

/* Procède au chargement d'un DIE de la section debug_info. */
static bool extract_dies_from_debug_info(const work_data *, size_t, GtkStatusStack *, activity_id_t);



/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations de débogage DWARF à compléter.         *
*                gid    = groupe de travail impliqué.                         *
                 status = barre de statut à tenir informée.                   *

*                                                                             *
*  Description : Charge les informations depuis une section ".debug_info".    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_dwarf_debug_information(GDwarfFormat *format, wgroup_id_t gid, GtkStatusStack *status)
{
    bool result;                            /* Bilan à renvoyer            */
    GExeFormat *exe;                        /* Exécutable associé          */
    mrange_t range;                         /* Couverture d'une section    */
    GBinContent *content;                   /* Contenu binaire à lire      */
    GBinContent *restricted;                /* Limitation des traitements  */
    vmpa2t stop;                            /* Point d'arrivée à atteindre */
    mrange_t *ranges;                       /* Séquences de zones à traiter*/
    size_t count;                           /* Nombre de ces séquences     */
    size_t allocated;                       /* Quantité d'allocations      */
    SourceEndian endian;                    /* Boutisme du format parent   */
    vmpa2t iter;                            /* Tête de lecture mouvante    */
    vmpa2t start;                           /* Sauvegarde de position      */
    dw_compil_unit_header header;           /* Unité à cerner puis traiter */
    vmpa2t next;                            /* Départ de l'unité suivante  */
    phys_t size;                            /* Taille complète d'une unité */
    work_data data;                         /* Données à communiquer       */
    guint runs_count;                       /* Qté d'exécutions parallèles */
    size_t run_size;                        /* Volume réparti par exécution*/
    GWorkQueue *queue;                      /* Gestionnaire de différés    */
    activity_id_t msg;                      /* Message de progression      */
    guint i;                                /* Boucle de parcours          */
    size_t begin;                           /* Début de bloc de traitement */
    size_t end;                             /* Fin d'un bloc de traitement */
    GSeqWork *work;                         /* Tâche de chargement à lancer*/

    exe = G_DBG_FORMAT(format)->executable;

    result = g_exe_format_get_section_range_by_name(exe, ".debug_info", &range);

    if (result)
    {
        content = G_KNOWN_FORMAT(format)->content;

        restricted = g_restricted_content_new(content, &range);

        compute_mrange_end_addr(&range, &stop);

        /* Constitution des zones de travail */

        ranges = NULL;
        count = 0;
        allocated = 0;

        endian = g_binary_format_get_endianness(G_BIN_FORMAT(exe));

        for (copy_vmpa(&iter, get_mrange_addr(&range));
             result && cmp_vmpa(&iter, &stop) < 0;
             copy_vmpa(&iter, &next))
        {
            copy_vmpa(&start, &iter);

            result = read_dwarf_compil_unit_header(restricted, &iter, endian, &header, &next);
            if (!result) break;

            if (count == allocated)
            {
                allocated += RANGE_ALLOC_BLOCK;
                ranges = realloc(ranges, allocated * sizeof(mrange_t));
            }

            size = compute_vmpa_diff(&start, &next);

            init_mrange(&ranges[count++], &start, size);

        }

        if (!result)
            goto exit;

        /* Préparation des réceptacles */

        format->info = calloc(count, sizeof(dw_die *));
        format->info_count = count;

        data.format = format;
        data.ranges = ranges;

        /* Lancement des travaux */

        run_size = compute_run_size(count, &runs_count);

        queue = get_work_queue();

        msg = gtk_status_stack_add_activity(status, _("Loading all information from the .debug_info section..."),
                                            get_mrange_length(&range));

        for (i = 0; i < runs_count; i++)
        {
            begin = i * run_size;

            if ((i + 1) == runs_count)
                end = count;
            else
                end = begin + run_size;

            work = g_seq_work_new_boolean(&data, begin, end, msg,
                                          (seq_work_bool_cb)extract_dies_from_debug_info, &result);

            g_work_queue_schedule_work(queue, G_DELAYED_WORK(work), gid);

        }

        g_work_queue_wait_for_completion(queue, gid);

        gtk_status_stack_remove_activity(status, msg);

 exit:

        if (ranges != NULL)
            free(ranges);

        g_object_unref(G_OBJECT(restricted));

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : data   = ensemble d'informations utiles à l'opération.       *
*                i      = indice des éléments à traiter.                      *
*                status = barre de statut à tenir informée.                   *
*                id     = identifiant du message affiché à l'utilisateur.     *
*                                                                             *
*  Description : Procède au chargement d'un DIE de la section debug_info.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool extract_dies_from_debug_info(const work_data *data, size_t i, GtkStatusStack *status, activity_id_t id)
{
    bool result;                            /* Bilan à retourner           */
    GDwarfFormat *format;                   /* Format en cours d'analyse   */
    GBinContent *content;                   /* Contenu binaire à lire      */
    GExeFormat *exe;                        /* Exécutable associé          */
    SourceEndian endian;                    /* Boutisme du format parent   */
    vmpa2t iter;                            /* Tête de lecture mouvante    */
    dw_compil_unit_header header;           /* Unité à cerner puis traiter */
    vmpa2t next;                            /* Départ de l'unité suivante  */
    dw_abbrev_brotherhood *abbrevs;         /* Série d'abréviations        */

    format = data->format;

    /**
     * Comme les informations peuvent aller taper ailleurs dans le binaire
     * (par exemple dans la section debug_str pour certaine valeur, on ne peut
     * pas restreinte le contenu au seul espace traité.
     *
     * L'en-tête lui même a déjà été valide, donc on ne s'embête pas à distinguer
     * différents cas ici.
     */

    content = G_KNOWN_FORMAT(format)->content;

    exe = G_DBG_FORMAT(format)->executable;

    endian = g_binary_format_get_endianness(G_BIN_FORMAT(exe));

    copy_vmpa(&iter, get_mrange_addr(&data->ranges[i]));

    result = read_dwarf_compil_unit_header(content, &iter, endian, &header, &next);
    if (!result) goto exit;

    abbrevs = load_all_dwarf_abbreviations(format, &header);
    if (abbrevs == NULL) goto exit;

    result = build_dwarf_die(format, content, &iter, &header, abbrevs, &format->info[i]);

    free_all_dwarf_abbreviations(abbrevs);

    gtk_status_stack_update_activity_value(status, id, get_mrange_length(&data->ranges[i]));

 exit:

    return result;

}
