
/* Chrysalide - Outil d'analyse de fichiers binaires
 * routines.c - étude des flots d'exécution dans les routines
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


#include "routines.h"


#include <malloc.h>


#include "dragon.h"
#include "limit.h"
#include "loop.h"
#include "rank.h"
#include "../../core/logs.h"
#include "../../glibext/delayed-int.h"



/* Fraction de routines à limiter (instance) */
struct _GRoutinesStudy
{
    GDelayedWork parent;                    /* A laisser en premier        */

    GLoadedBinary *binary;                  /* Binaire en cours d'analyse  */

    GArchProcessor *proc;                   /* Processeur avec ses instr.  */
    GBinFormat *format;                     /* Format de fichier manipulé  */
    GBinPortion *portions;                  /* Couches de binaire bornées  */

    size_t count;                           /* Nombre de symboles à traiter*/

    rtn_fallback_cb fallback;               /* Routine de traitement finale*/
    size_t begin;                           /* Point de départ du parcours */
    size_t end;                             /* Point d'arrivée exclu       */

    activity_id_t id;                       /* Identifiant pour messages   */

};

/* Fraction de routines à limiter (classe) */
struct _GRoutinesStudyClass
{
    GDelayedWorkClass parent;               /* A laisser en premier        */

};


/* Initialise la classe des tâches d'étude de routines. */
static void g_routines_study_class_init(GRoutinesStudyClass *);

/* Initialise une tâche d'étude de routines. */
static void g_routines_study_init(GRoutinesStudy *);

/* Supprime toutes les références externes. */
static void g_routines_study_dispose(GRoutinesStudy *);

/* Procède à la libération totale de la mémoire. */
static void g_routines_study_finalize(GRoutinesStudy *);

/* Assure l'étude des routines en différé. */
static void g_routines_study_process(GRoutinesStudy *, GtkStatusStack *);



/* Indique le type défini pour les tâches d'étude de routines. */
G_DEFINE_TYPE(GRoutinesStudy, g_routines_study, G_TYPE_DELAYED_WORK);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des tâches d'étude de routines.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_routines_study_class_init(GRoutinesStudyClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDelayedWorkClass *work;                /* Version en classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_routines_study_dispose;
    object->finalize = (GObjectFinalizeFunc)g_routines_study_finalize;

    work = G_DELAYED_WORK_CLASS(klass);

    work->run = (run_task_fc)g_routines_study_process;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : study = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une tâche d'étude de routines.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_routines_study_init(GRoutinesStudy *study)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : study = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_routines_study_dispose(GRoutinesStudy *study)
{
    g_clear_object(&study->binary);

    g_clear_object(&study->proc);

    if (study->format != NULL)
        g_binary_format_unlock_symbols_rd(study->format);

    g_clear_object(&study->format);

    g_clear_object(&study->portions);

    G_OBJECT_CLASS(g_routines_study_parent_class)->dispose(G_OBJECT(study));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : study = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_routines_study_finalize(GRoutinesStudy *study)
{
    G_OBJECT_CLASS(g_routines_study_parent_class)->finalize(G_OBJECT(study));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary   = binaire chargé comprenant les routines à traiter. *
*                portions = ensemble de couches binaires bornées.             *
*                begin    = point de départ du parcours de liste.             *
*                end      = point d'arrivée exclu du parcours.                *
*                id       = identifiant du message affiché à l'utilisateur.   *
*                fallback = routine de traitements particuliers.              *
*                                                                             *
*  Description : Crée une tâche d'étude de routines différée.                 *
*                                                                             *
*  Retour      : Tâche créée.                                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GRoutinesStudy *g_routines_study_new(GLoadedBinary *binary, GBinPortion *portions, size_t begin, size_t end, activity_id_t id, rtn_fallback_cb fallback)
{
    GRoutinesStudy *result;                /* Tâche à retourner           */

    result = g_object_new(G_TYPE_ROUTINES_STUDY, NULL);

    result->binary = binary;
    g_object_ref(G_OBJECT(binary));

    result->proc = g_loaded_binary_get_processor(binary);
    result->format = G_BIN_FORMAT(g_loaded_binary_get_format(binary));

    result->portions = portions;
    g_object_ref(G_OBJECT(portions));

    g_binary_format_lock_symbols_rd(result->format);

    result->count = g_binary_format_count_symbols(result->format);

    result->fallback = fallback;
    result->begin = begin;
    result->end = end;

    result->id = id;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : study  = étude de routines à mener.                          *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Assure l'étude des routines en différé.                      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_routines_study_process(GRoutinesStudy *study, GtkStatusStack *status)
{
    size_t i;                               /* Boucle de parcours          */
    GBinSymbol *symbol;                     /* Commodité d'accès           */
    SymbolType type;                        /* Type de symbole rencontré   */

    for (i = study->begin; i < study->end; i++)
    {
        symbol = g_binary_format_get_symbol(study->format, i);

        type = g_binary_symbol_get_stype(symbol);

        if (type == STP_ROUTINE || type == STP_ENTRY_POINT)
            study->fallback(study, G_BIN_ROUTINE(symbol), i);

        gtk_status_stack_update_activity_value(status, study->id, 1);

        g_object_unref(G_OBJECT(symbol));

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : study   = étude de routines à mener.                         *
*                routine = routine à traiter.                                 *
*                index   = indice de l'insruction visée.                      *
*                                                                             *
*  Description : Détermine si besoin est les bornes des routines.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_routines_study_compute_limits(GRoutinesStudy *study, GBinRoutine *routine, size_t index)
{
    GBinSymbol *symbol;                     /* Version alternative         */
    const vmpa2t *next;                     /* Début de la zone suivante   */
    GBinSymbol *next_symbol;                /* Eventuel symbole suivant    */
    const mrange_t *range;                  /* Zone du symbole suivant     */
    vmpa2t _next;                           /* Emplacement de zone         */

    symbol = G_BIN_SYMBOL(routine);

    for (next = NULL, index++; next == NULL && index < study->count; index++)
    {
        next_symbol = g_binary_format_get_symbol(study->format, index);

        /**
         * Les étiquettes à l'intérieur de code ne doivent pas constituer
         * une profonde coupure à l'intérieur d'une routine.
         *
         * On recherche donc la fin de la routine courante via les
         * symboles suivants.
         */

        if (g_binary_symbol_get_stype(next_symbol) == STP_CODE_LABEL)
            goto skip_symbol;

        range = g_binary_symbol_get_range(next_symbol);

        copy_vmpa(&_next, get_mrange_addr(range));
        next = &_next;

 skip_symbol:

        g_object_unref(G_OBJECT(next_symbol));

    }

    compute_routine_limit(symbol, next, study->proc, study->portions);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : study   = étude de routines à mener.                         *
*                routine = routine à traiter.                                 *
*                index   = indice de l'insruction visée.                      *
*                                                                             *
*  Description : Procède au traitement des blocs de routines.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_routines_study_handle_blocks(GRoutinesStudy *study, GBinRoutine *routine, size_t index)
{
    GBinSymbol *symbol;                     /* Version alternative         */
    const mrange_t *range;                  /* Couverture d'une routine    */
    const vmpa2t *start;                    /* Adresse de départ           */
    const instr_coverage *coverage;         /* Instructions couvertes      */
    char *label;                            /* Etiquette du symbole        */
    VMPA_BUFFER(loc);                       /* Position de la routine      */
    dragon_knight *knight;                  /* Complexité de code posée    */
    GBlockList *blocks;                     /* Liste de blocs basiques     */

    /* Préparatifs communs */

    symbol = G_BIN_SYMBOL(routine);

    range = g_binary_symbol_get_range(symbol);
    start = get_mrange_addr(range);

    coverage = g_arch_processor_find_coverage_by_address(study->proc, start);

    /**
     * Si aucune couverture adaptée n'est trouvée, c'est que la routine ne se
     * trouve probablement pas dans le corps du binaire...
     *
     * Erreur d'interprétation ou adresse fixe ? En tout cas, sans instructions,
     * il n'y a aucun traitement possible ici !
     */
    if (coverage == NULL)
    {
        label = g_binary_symbol_get_label(symbol);

        vmpa2_to_string(start, MDS_UNDEFINED, loc, NULL);

        if (label == NULL)
            log_variadic_message(LMT_BAD_BINARY, _("Skipped out of bound routine @ %s"), loc);

        else
        {
            log_variadic_message(LMT_BAD_BINARY, _("Skipped out of bound routine '%s' @ %s"), label, loc);
            free(label);
        }

        return;

    }

    knight = begin_dragon_knight(study->proc, coverage, range, start);


    /**
     * FIXME
     * L'état 'knight == NULL' peut avoir deux origines :
     *  - soit le binaire est mal-formé.
     *  - soit le désassemblage s'est mal déroulé.
     * Dans les deux cas, on obtient un symbole qui n'a pas d'instruction de départ.
     * A traiter autrement qu'en filtrant sur knight...
     */
    if (knight == NULL) return;


    /* Traitement par blocs */

    blocks = translate_dragon_knight(knight, study->binary);

    g_binary_routine_set_basic_blocks(routine, blocks);

    detect_loops_in_basic_blocks(blocks);

    rank_routine_blocks(routine);

    g_object_unref(G_OBJECT(blocks));

    /* Nettoyage final */

    end_dragon_knight(knight);

}
