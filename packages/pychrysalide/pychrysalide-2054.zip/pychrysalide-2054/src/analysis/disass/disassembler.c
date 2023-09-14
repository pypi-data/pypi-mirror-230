
/* Chrysalide - Outil d'analyse de fichiers binaires
 * disassembler.c - encadrement des phases de désassemblage
 *
 * Copyright (C) 2010-2019 Cyrille Bagard
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


#include "disassembler.h"


#include <malloc.h>
#include <stdio.h>
#include <string.h>


#include <i18n.h>


#include "fetch.h"
#include "instructions.h"
#include "output.h"
#include "routines.h"
#include "../human/asm/lang.h"
#include "../../arch/storage.h"
#include "../../core/columns.h"
#include "../../core/global.h"
#include "../../core/params.h"
#include "../../core/nproc.h"
#include "../../glibext/generators/prologue.h"
#include "../../plugins/pglist.h"



/* Opère sur toutes les instructions. */
static void process_all_instructions(wgroup_id_t, GtkStatusStack *, const char *, ins_fallback_cb, GArchProcessor *, GProcContext *, GExeFormat *);

/* Opère sur toutes les routines. */
static void process_all_routines(GLoadedBinary *, wgroup_id_t, GtkStatusStack *, const char *, rtn_fallback_cb);

/* Réalise un désassemblage effectif. */
static void compute_disassembly(GLoadedBinary *, GProcContext *, wgroup_id_t, GtkStatusStack *);



/******************************************************************************
*                                                                             *
*  Paramètres  : gid      = groupe de travail impliqué.                       *
*                status   = barre de statut à tenir informée.                 *
*                msg      = message à faire paraître pour la patience.        *
*                fallback = routine de traitements particuliers.              *
*                proc     = ensemble d'instructions désassemblées.            *
*                ctx      = contexte fourni pour suivre le désassemblage.     *
*                format   = accès aux données du binaire d'origine.           *
*                                                                             *
*  Description : Opère sur toutes les instructions.                           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void process_all_instructions(wgroup_id_t gid, GtkStatusStack *status, const char *msg, ins_fallback_cb fallback, GArchProcessor *proc, GProcContext *ctx, GExeFormat *format)
{
    size_t ins_count;                       /* Quantité d'instructions     */
    guint runs_count;                       /* Qté d'exécutions parallèles */
    size_t run_size;                        /* Volume réparti par exécution*/
    GWorkQueue *queue;                      /* Gestionnaire de différés    */
    activity_id_t id;                       /* Identifiant de progression  */
    guint i;                                /* Boucle de parcours          */
    size_t begin;                           /* Début de bloc de traitement */
    size_t end;                             /* Fin d'un bloc de traitement */
    GInstructionsStudy *study;              /* Tâche d'étude à programmer  */

    g_arch_processor_lock(proc);

    ins_count = g_arch_processor_count_instructions(proc);

    g_arch_processor_unlock(proc);

    run_size = compute_run_size(ins_count, &runs_count);

    queue = get_work_queue();

    id = gtk_status_stack_add_activity(status, msg, ins_count);

    for (i = 0; i < runs_count; i++)
    {
        begin = i * run_size;

        if ((i + 1) == runs_count)
            end = ins_count;
        else
            end = begin + run_size;

        study = g_instructions_study_new(proc, ctx, format, begin, end, id, fallback);

        g_work_queue_schedule_work(queue, G_DELAYED_WORK(study), gid);

    }

    g_work_queue_wait_for_completion(queue, gid);

    gtk_status_stack_remove_activity(status, id);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary   = binaire chargé comprenant les routines à traiter. *
*                gid      = groupe de travail impliqué.                       *
                 status   = barre de statut à tenir informée.                 *
*                msg      = message à faire paraître pour la patience.        *
*                fallback = routine de traitements particuliers.              *
*                                                                             *
*  Description : Opère sur toutes les routines.                               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void process_all_routines(GLoadedBinary *binary, wgroup_id_t gid, GtkStatusStack *status, const char *msg, rtn_fallback_cb fallback)
{
    GBinFormat *format;                     /* Format associé au binaire   */
    GBinPortion *portions;                  /* Couche première de portions */
    size_t sym_count;                       /* Nombre de ces symboles      */
    guint runs_count;                       /* Qté d'exécutions parallèles */
    size_t run_size;                        /* Volume réparti par exécution*/
    GWorkQueue *queue;                      /* Gestionnaire de différés    */
    activity_id_t id;                       /* Identifiant de progression  */
    guint i;                                /* Boucle de parcours          */
    size_t begin;                           /* Début de bloc de traitement */
    size_t end;                             /* Fin d'un bloc de traitement */
    GRoutinesStudy *study;                  /* Tâche d'étude à programmer  */

    format = G_BIN_FORMAT(g_loaded_binary_get_format(binary));

    portions = g_exe_format_get_portions(G_EXE_FORMAT(format));

    g_binary_format_lock_symbols_rd(format);

    sym_count = g_binary_format_count_symbols(format);

    run_size = compute_run_size(sym_count, &runs_count);

    queue = get_work_queue();

    id = gtk_status_stack_add_activity(status, msg, sym_count);

    for (i = 0; i < runs_count; i++)
    {
        begin = i * run_size;

        if ((i + 1) == runs_count)
            end = sym_count;
        else
            end = begin + run_size;

        study = g_routines_study_new(binary, portions, begin, end, id, fallback);

        g_work_queue_schedule_work(queue, G_DELAYED_WORK(study), gid);

    }

    g_work_queue_wait_for_completion(queue, gid);

    gtk_status_stack_remove_activity(status, id);

    g_binary_format_unlock_symbols_rd(format);

    g_object_unref(G_OBJECT(portions));

    g_object_unref(G_OBJECT(format));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary  = représentation de binaire chargé.                  *
*                context = contexte de désassemblage utilisé.                 *
*                gid     = groupe de travail dédié.                           *
*                status  = barre de statut à tenir informée.                  *
*                                                                             *
*  Description : Réalise un désassemblage effectif.                           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void compute_disassembly(GLoadedBinary *binary, GProcContext *context, wgroup_id_t gid, GtkStatusStack *status)
{
    GArchProcessor *proc;                   /* Architecture du binaire     */
    GExeFormat *format;                     /* Format du binaire représenté*/
    GBinContent *content;                   /* Contenu brut représenté     */
    const gchar *id;                        /* Identifiant court et unique */
    GAsmStorage *storage;                   /* Cache propre à constituer   */
    bool cached;                            /* Instructions en cache       */
    GArchInstruction **instrs;              /* Instructions résultantes    */
    size_t count;                           /* Quantité de ces instructions*/

    /**
     * Récupération des objets utiles.
     */

    proc = g_loaded_binary_get_processor(binary);

    format = g_loaded_binary_get_format(binary);

    g_binary_format_preload_disassembling_context(G_BIN_FORMAT(format), context, status);

    /**
     * Etape zéro : récupération des instructions depuis un cache, si ce dernier exitste.
     */

    content = g_loaded_content_get_content(G_LOADED_CONTENT(binary));

    id = g_binary_content_get_checksum(content);

    storage = g_asm_storage_new_compressed(proc, id);

    g_object_unref(G_OBJECT(content));

    cached = g_asm_storage_has_cache(storage);

    if (cached)
        cached = g_asm_storage_open(storage, G_BIN_FORMAT(format), gid);

    g_object_unref(G_OBJECT(storage));

    /**
     * Première étape : collecte des instructions.
     */

    if (!cached)
    {
        instrs = disassemble_binary_content(binary, context, gid, status, &count);

        g_arch_processor_set_instructions(proc, instrs, count);

        process_disassembly_event(PGA_DISASSEMBLY_RAW, binary, status, context);

    }

    /**
     * Seconde étape : liaisons des instructions.
     */

    if (!cached)
    {
        process_all_instructions(gid, status, _("Calling 'link' hook on all instructions..."),
                                 g_instructions_study_do_link_operation,
                                 proc, context, format);

        process_disassembly_event(PGA_DISASSEMBLY_HOOKED_LINK, binary, status, context);

    }

    /**
     * Troisième étape : exécution d'éventuels post-traitements.
     */

    process_all_instructions(gid, status, _("Calling 'post' hook on all instructions..."),
                             g_instructions_study_do_post_operation,
                             proc, context, format);

    process_disassembly_event(PGA_DISASSEMBLY_HOOKED_POST, binary, status, context);

    /**
     * Quatrième étape : établissement des couvertures de routines restantes.
     */

    process_all_routines(binary, gid, status,
                         _("Finding remaining limits..."),
                         g_routines_study_compute_limits);

    process_disassembly_event(PGA_DISASSEMBLY_LIMITED, binary, status, context);

    /**
     * Cinquième étape : liaisons entre instructions.
     */

    if (!cached)
    {
        process_all_instructions(gid, status, _("Establishing links betweek all instructions..."),
                                 g_instructions_study_establish_links,
                                 proc, context, format);

        process_disassembly_event(PGA_DISASSEMBLY_LINKED, binary, status, context);

    }

    /**
     * Sixième étape : regroupement en blocs basiques.
     */

    process_all_routines(binary, gid, status,
                         _("Control-flow analysis for routines..."),
                         g_routines_study_handle_blocks);

    process_disassembly_event(PGA_DISASSEMBLY_GROUPED, binary, status, context);

    /**
     * Nettoyage final et sortie !
     */

    g_object_unref(G_OBJECT(format));

    g_object_unref(G_OBJECT(proc));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary  = représentation de binaire chargé.                  *
*                gid     = groupe de travail dédié.                           *
*                status  = barre de statut à tenir informée.                  *
*                context = contexte de désassemblage. [OUT]                   *
*                                                                             *
*  Description : Procède au désassemblage d'un contenu binaire donné.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void disassemble_binary(GLoadedBinary *binary, wgroup_id_t gid, GtkStatusStack *status, GProcContext **context)
{
    GArchProcessor *proc;                   /* Architecture du binaire     */

    /* Préparatifs */

    process_disassembly_event(PGA_DISASSEMBLY_STARTED, binary, status, NULL);

    proc = g_loaded_binary_get_processor(binary);

    *context = g_arch_processor_get_context(proc);

    g_object_unref(G_OBJECT(proc));

    /* Lancement des opérations ! */

    compute_disassembly(binary, *context, gid, status);

    process_disassembly_event(PGA_DISASSEMBLY_ENDED, binary, status, *context);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary  = représentation de binaire chargé.                  *
*                context = contexte de désassemblage utilisé.                 *
*                status  = barre de statut à tenir informée.                  *
*                cache   = tampon de code mis en place. [OUT]                 *
*                                                                             *
*  Description : Imprime le résultat d'un désassemblage.                      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void output_disassembly(GLoadedBinary *binary, GProcContext *context, GtkStatusStack *status, GBufferCache **cache)
{
    GBinFormat *format;                     /* Format associé au binaire   */
    GBinContent *content;                   /* Contenu bianire manipulé    */
    GCodingLanguage *lang;                  /* Langage de sortie préféré   */
    int offset;                             /* Décalage des étiquettes     */
#ifdef INCLUDE_GTK_SUPPORT
    GWidthTracker *tracker;                 /* Gestionnaire de largeurs    */
#endif
    char **text;                            /* Contenu brute à imprimer    */
    char *desc;                             /* Désignation du binaire      */
    const gchar *checksum;                  /* Identifiant de binaire      */
    GIntroGenerator *generator;             /* Générateur constitué        */

    /**
     * Initialisation des biens communs.
     */

    format = G_BIN_FORMAT(g_loaded_binary_get_format(binary));
    content = g_known_format_get_content(G_KNOWN_FORMAT(format));
    lang = g_asm_language_new();

    *cache = g_buffer_cache_new(content, DLC_COUNT, DLC_ASSEMBLY_LABEL);

    g_generic_config_get_value(get_main_configuration(), MPK_LABEL_OFFSET, &offset);

#ifdef INCLUDE_GTK_SUPPORT
    tracker = g_buffer_cache_get_width_tracker(*cache);
    g_width_tracker_set_column_min_width(tracker, DLC_ASSEMBLY_LABEL, offset);
    g_object_unref(G_OBJECT(tracker));
#endif

    g_buffer_cache_wlock(*cache);

    /**
     * Impression du prologue.
     */

    text = calloc(4, sizeof(char *));

    /* Introduction */

    text[0] = strdup(_("Disassembly generated by Chrysalide"));
    text[1] = strdup(_("Chrysalide is free software - © 2008-2018 Cyrille Bagard"));

    /* Fichier */

    desc = g_binary_content_describe(content, true);

    asprintf(&text[2], "%s%s", _("Source: "), desc);

    free(desc);

    /* Checksum SHA256 */

    checksum = g_binary_content_get_checksum(content);

    asprintf(&text[3], "%s%s", _("Sha256: "), checksum);

    /* Intégration finale */

    generator = g_intro_generator_new(format, lang, text, 4);

    g_buffer_cache_append(*cache, G_LINE_GENERATOR(generator), BLF_NONE);

    /**
     * Impression des instructions désassemblées.
     */

    print_disassembled_instructions(*cache, lang, binary, G_PRELOAD_INFO(context), status);

    /**
     * Rajout de tous les éléments mis en place automatiquement.
     */

    void add_to_collection(GDbItem *item, gpointer unused)
    {
        g_object_ref(G_OBJECT(item));

        g_loaded_binary_add_to_collection(binary, item);

    }

    g_proc_context_foreach_db_item(context, (GFunc)add_to_collection, NULL);

    /**
     * Nettoyage avant sortie.
     */

    g_buffer_cache_wunlock(*cache);

    g_object_unref(G_OBJECT(lang));
    g_object_unref(G_OBJECT(content));
    g_object_unref(G_OBJECT(format));

}
