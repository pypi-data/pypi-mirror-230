
/* Chrysalide - Outil d'analyse de fichiers binaires
 * fetch.c - récupération d'instructions à partir de binaire brut
 *
 * Copyright (C) 2010-2018 Cyrille Bagard
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


#include "fetch.h"


#include <assert.h>


#include <i18n.h>


#include "area.h"
#include "../../core/global.h"
#include "../../format/known.h"
#include "../../format/format.h"
#include "../../glibext/delayed-int.h"



/* ------------------------- RECUPERATIONS EN TOILE DE FOND ------------------------- */


#define G_TYPE_DELAYED_FETCHING               g_delayed_fetching_get_type()
#define G_DELAYED_FETCHING(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), g_delayed_fetching_get_type(), GDelayedFetching))
#define G_IS_DELAYED_FETCHING(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_delayed_fetching_get_type()))
#define G_DELAYED_FETCHING_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DELAYED_FETCHING, GDelayedFetchingClass))
#define G_IS_DELAYED_FETCHING_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DELAYED_FETCHING))
#define G_DELAYED_FETCHING_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DELAYED_FETCHING, GDelayedFetchingClass))


/* Ensembles binaires à désassembler (instance) */
typedef struct _GDelayedFetching
{
    GDelayedWork parent;                    /* A laisser en premier        */

    wgroup_id_t gid;                        /* Groupe de travail parallèle */

    GExeFormat *format;                     /* Format du fichier binaire   */

    GProcContext *ctx;                      /* Contexte de désassemblage   */
    mem_area *areas;                        /* Zone de productions         */
    size_t count;                           /* Nombre de ces zones         */

    GtkStatusStack *status;                 /* Barre de statut             */
    activity_id_t id;                       /* Groupe de progression       */

    DisassPriorityLevel level;              /* Niveau d'importance du point*/
    virt_t virt;                            /* Adresse de départ dépilée   */

} GDelayedFetching;

/* Ensembles binaires à désassembler (classe) */
typedef struct _GDelayedFetchingClass
{
    GDelayedWorkClass parent;               /* A laisser en premier        */

} GDelayedFetchingClass;


/* Indique le type défini pour les tâches de récupération différée. */
GType g_delayed_fetching_get_type(void);

/* Initialise la classe des tâches de désassemblage différé. */
static void g_delayed_fetching_class_init(GDelayedFetchingClass *);

/* Initialise une tâche de désassemblage différé. */
static void g_delayed_fetching_init(GDelayedFetching *);

/* Supprime toutes les références externes. */
static void g_delayed_fetching_dispose(GDelayedFetching *);

/* Procède à la libération totale de la mémoire. */
static void g_delayed_fetching_finalize(GDelayedFetching *);

/* Crée une tâche de récupération d'instructions différée. */
static GDelayedFetching *g_delayed_fetching_new(const GDelayedFetching *, DisassPriorityLevel, virt_t);

/* Assure la récupération d'instructions en différé. */
static void g_delayed_fetching_process(GDelayedFetching *, GtkStatusStack *);



/* ------------------------ DESASSEMBLAGE DE BINAIRE DIFFERE ------------------------ */


/* Poursuit l'analyse à partir des points d'entrée découverts. */
static void follow_execution_flow(GProcContext *, const GDelayedFetching *);

/* Etudie le besoin d'attendre d'avantage de prochaines tâches. */
static bool check_if_extra_wait_is_needed(GWorkQueue *, wgroup_id_t, GProcContext *);



/* ---------------------------------------------------------------------------------- */
/*                           RECUPERATIONS EN TOILE DE FOND                           */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour les tâches de récupération différée. */
G_DEFINE_TYPE(GDelayedFetching, g_delayed_fetching, G_TYPE_DELAYED_WORK);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des tâches de récupération différée.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_delayed_fetching_class_init(GDelayedFetchingClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDelayedWorkClass *work;                /* Version en classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_delayed_fetching_dispose;
    object->finalize = (GObjectFinalizeFunc)g_delayed_fetching_finalize;

    work = G_DELAYED_WORK_CLASS(klass);

    work->run = (run_task_fc)g_delayed_fetching_process;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : fetching = instance à initialiser.                           *
*                                                                             *
*  Description : Initialise une tâche de récupération différée.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_delayed_fetching_init(GDelayedFetching *fetching)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : fetching = instance d'objet GLib à traiter.                  *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_delayed_fetching_dispose(GDelayedFetching *fetching)
{
    g_clear_object(&fetching->format);

    g_clear_object(&fetching->ctx);

    g_clear_object(&fetching->status);

    G_OBJECT_CLASS(g_delayed_fetching_parent_class)->dispose(G_OBJECT(fetching));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : fetching = instance d'objet GLib à traiter.                  *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_delayed_fetching_finalize(GDelayedFetching *fetching)
{
    G_OBJECT_CLASS(g_delayed_fetching_parent_class)->finalize(G_OBJECT(fetching));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : template = modèle dont les informations sont à copier.       *
*                level    = indication de priorité et d'origine de l'adresse. *
*                virt     = point départ dépilé et personnalisant l'instance. *
*                                                                             *
*  Description : Crée une tâche de récupération d'instructions différée.      *
*                                                                             *
*  Retour      : Tâche créée.                                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GDelayedFetching *g_delayed_fetching_new(const GDelayedFetching *template, DisassPriorityLevel level, virt_t virt)
{
    GDelayedFetching *result;            /* Tâche à retourner           */

    result = g_object_new(G_TYPE_DELAYED_FETCHING, NULL);

    result->gid = template->gid;

    result->format = template->format;
    g_object_ref(G_OBJECT(result->format));

    result->ctx = template->ctx;
    g_object_ref(G_OBJECT(result->ctx));

    result->areas = template->areas;
    result->count = template->count;

    result->status = template->status;
    if (result->status != NULL)
        g_object_ref(G_OBJECT(result->status));

    result->id = template->id;

    result->level = level;
    result->virt = virt;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : fetching = récupération à mener.                             *
*                status   = barre de statut à tenir informée.                 *
*                                                                             *
*  Description : Assure la récupération d'instructions en différé.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_delayed_fetching_process(GDelayedFetching *fetching, GtkStatusStack *status)
{
    vmpa2t addr;                            /* Conversion en pleine adresse*/
    mem_area *area;                         /* Zone trouvée à traiter      */

    if (!g_exe_format_translate_address_into_vmpa(fetching->format, fetching->virt, &addr))
        return;

    area = find_memory_area_by_addr(fetching->areas, fetching->count, &addr);

    if (area != NULL)
        load_code_from_mem_area(area, fetching->areas, fetching->count,
                                   fetching->ctx, &addr, fetching->level < 2,
                                   fetching->status, fetching->id);

}



/* ---------------------------------------------------------------------------------- */
/*                          DESASSEMBLAGE DE BINAIRE DIFFERE                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : ctx      = contexte de désass. avec une nouvelle entrée.     *
*                template = modèle dont les informations sont à copier.       *
*                                                                             *
*  Description : Poursuit l'analyse à partir des points d'entrée découverts.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void follow_execution_flow(GProcContext *ctx, const GDelayedFetching *template)
{
    GWorkQueue *queue;                      /* Gestionnaire de différés    */
    gint *remaining_counter;                /* Compteur à considérer       */
    DisassPriorityLevel level;              /* Niveau d'importance du point*/
    virt_t virt;                            /* Adresse de départ dépilée   */
    GDelayedFetching *fetching;             /* Récupération à mener        */

    queue = get_work_queue();

    remaining_counter = (gint *)g_object_get_data(G_OBJECT(ctx), "remaining_counter");

    while (g_proc_context_pop_drop_point(ctx, &level, &virt))
    {
        fetching = g_delayed_fetching_new(template, level, virt);

        /**
         * Pas très élégant : l'identifiant du groupe de travail ne sert qu'ici ;
         * il n'est donc aucune utilité dans la tâche elle-même.
         *
         * Cependant, les paramètres d'appel étant limités, il faudrait créer
         * une structure intermediare pour communiquer l'identifiant, ce qui
         * est tout aussi moche.
         */

        g_work_queue_schedule_work(queue, G_DELAYED_WORK(fetching), template->gid);

        /**
         * Le décompte n'est réalisé qu'après la programmation de la tâche.
         * Ainsi, lors de l'attente de la fin des traitements, on a la garantie
         * de ne pas avoir de trou entre le dépilement des points et la programmation
         * des tâches de traitement associées.
         */

        if (g_atomic_int_dec_and_test(remaining_counter))
            g_work_queue_wake_up_waiters(queue, template->gid);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : queue = gestionnaire de l'ensemble des groupes de travail.   *
*                id    = identifiant d'un groupe de travail.                  *
*                ctx   = contexte de désass. avec une nouvelle entrée.        *
*                                                                             *
*  Description : Etudie le besoin d'attendre d'avantage de prochaines tâches. *
*                                                                             *
*  Retour      : true pour attendre d'avantage, false sinon.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool check_if_extra_wait_is_needed(GWorkQueue *queue, wgroup_id_t id, GProcContext *ctx)
{
    bool result;                            /* Bilan à retourner           */
    gint *remaining_counter;                /* Compteur à considérer       */

    remaining_counter = (gint *)g_object_get_data(G_OBJECT(ctx), "remaining_counter");

    result = (g_atomic_int_get(remaining_counter) > 0);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary = représentation de binaire chargé.                   *
*                ctx    = contexte fourni pour suivre le désassemblage.       *
*                gid    = identifiant du groupe de travail à utiliser.        *
*                status = barre de statut avec progression à mettre à jour.   *
*                count  = nombre d'instructions récupérées.                   *
*                                                                             *
*  Description : Procède au désassemblage basique d'un contenu binaire.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction **disassemble_binary_content(GLoadedBinary *binary, GProcContext *ctx, wgroup_id_t gid, GtkStatusStack *status, size_t *count)
{
    GArchInstruction **result;              /* Instruction désassemblées   */
    GDelayedFetching template;              /* Patron des tâches à venir   */
    GBinFormat *format;                     /* Format du fichier binaire   */
    GBinContent *content;                   /* Contenu binaire à manipuler */
    phys_t length;                          /* Taille des données à lire   */
    GWorkQueue *queue;                      /* Gestionnaire de différés    */
    gint remaining_counter;                 /* Quantité de points restants */

    /* Constitution du modèle de référence */

    template.gid = gid;

    template.format = g_loaded_binary_get_format(binary);
    format = G_BIN_FORMAT(template.format);

    template.ctx = ctx;

    content = g_known_format_get_content(G_KNOWN_FORMAT(format));
    length = g_binary_content_compute_size(content);
    g_object_unref(G_OBJECT(content));

    template.areas = collect_memory_areas(gid, status, binary, length, &template.count);

    template.status = status;

    /* Amorce des traitements */

    queue = get_work_queue();

    g_atomic_int_set(&remaining_counter, 0);

    g_object_set_data(G_OBJECT(template.ctx), "remaining_counter", &remaining_counter);

    g_proc_context_attach_counter(template.ctx, &remaining_counter);

    /**
     * Première phase de désassemblage : intégration des infos du format,
     * récupérées dans le contexte via un appel à g_binary_format_preload_disassembling_context().
     */

    populate_fresh_memory_areas(gid, status, template.areas, template.count, G_PRELOAD_INFO(ctx));

    g_work_queue_wait_for_completion(queue, gid);

    /**
     * Seconde phase : suivi des chemins tracés.
     */

    g_work_queue_set_extra_wait_callback(queue, gid,
                                         (wait_for_incoming_works_cb)check_if_extra_wait_is_needed,
                                         template.ctx);

    g_signal_connect(template.ctx, "drop-point-pushed", G_CALLBACK(follow_execution_flow), &template);

    template.id = gtk_status_stack_add_activity(status,
                                                _("Disassembling following the execution flow..."),
                                                length);

    g_binary_format_activate_disassembling_context(format, template.ctx, status);

    g_work_queue_wait_for_completion(queue, gid);

    /**
     * Troisième phase : on comble les trous laissés.
     */

    ensure_all_mem_areas_are_filled(gid, status, template.id, template.areas, template.count, template.ctx);

    g_work_queue_set_extra_wait_callback(queue, gid, NULL, NULL);

    g_object_set_data(G_OBJECT(template.ctx), "remaining_counter", NULL);

    ensure_all_mem_areas_are_filled(gid, status, template.id, template.areas, template.count, NULL);

    gtk_status_stack_remove_activity(status, template.id);

    /**
     * Quatrième et dernière phase : récolte des fruits.
     */

    result = collect_disassembled_instructions(gid, status, template.areas, template.count, count);

    /* Libération finale */

    g_object_unref(G_OBJECT(template.format));

    return result;

}
