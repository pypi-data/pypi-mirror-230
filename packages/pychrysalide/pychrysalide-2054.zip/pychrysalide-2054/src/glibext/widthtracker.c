
/* Chrysalide - Outil d'analyse de fichiers binaires
 * widthtracker.c - suivi des largeurs associées à un ensemble de lignes
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


#include "widthtracker.h"


#include <assert.h>
#include <malloc.h>
#include <stdlib.h>
#include <string.h>


#include <i18n.h>


#include "buffercache.h"
#include "delayed-int.h"
#include "../core/global.h"
#include "../core/nproc.h"



/* --------------------------- PRISE DE MESURES INITIALES --------------------------- */


/* Procédure de mise à jour des mesures de largeurs (instance) */
typedef struct _GWidthUpdate
{
    GDelayedWork parent;                    /* A laisser en premier        */

    activity_id_t id;                       /* Groupe de progression       */

    GWidthTracker *tracker;                 /* Gestionnaire à manipuler    */

    size_t start;                           /* Premier indice à traiter    */
    size_t end;                             /* Premier indice à écarter    */

    line_width_summary summary;             /* Largeurs requises suivies   */

} GWidthUpdate;

/* Procédure de mise à jour des mesures de largeurs (classe) */
typedef struct _GWidthUpdateClass
{
    GDelayedWorkClass parent;               /* A laisser en premier        */

} GWidthUpdateClass;


#define G_TYPE_WIDTH_UPDATE            g_width_update_get_type()
#define G_WIDTH_UPDATE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_WIDTH_UPDATE, GWidthUpdate))
#define G_IS_WIDTH_UPDATE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_WIDTH_UPDATE))
#define G_WIDTH_UPDATE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_WIDTH_UPDATE, GWidthUpdateClass))
#define G_IS_WIDTH_UPDATE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_WIDTH_UPDATE))
#define G_WIDTH_UPDATE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_WIDTH_UPDATE, GWidthUpdateClass))


/* Initialise la classe des tâches de mesures de largeurs. */
static void g_width_update_class_init(GWidthUpdateClass *);

/* Initialise une tâche de mesures de largeurs. */
static void g_width_update_init(GWidthUpdate *);

/* Supprime toutes les références externes. */
static void g_width_update_dispose(GWidthUpdate *);

/* Procède à la libération totale de la mémoire. */
static void g_width_update_finalize(GWidthUpdate *);

/* Indique le type défini pour les tâches de mesures de largeurs. */
GType g_width_update_get_type(void);

/* Crée une tâche de mesures de largeurs. */
static GWidthUpdate *g_width_update_new(activity_id_t, GWidthTracker *, size_t, size_t);

/* Assure les mesures initiales d'un ensemble de lignes. */
static void g_width_update_process(GWidthUpdate *, GtkStatusStack *);

/* Récupère les données obtenues lors d'une mesure globale. */
static void g_width_update_collect(GWidthUpdate *, line_width_summary *);



/* ---------------------------- RASSEMBLEMENT DE MESURES ---------------------------- */


/* Portions de largeurs communes */
typedef struct _common_metrics
{
    size_t first;                           /* Premier indice de portion   */
    size_t last;                            /* Dernier indice de portion   */

    line_width_summary summary;             /* Compilation de largeurs     */
    bool cached;                            /* Mise en cache des calculs   */

} common_metrics;


/* Gestionnaire de largeurs associées aux lignes (instance) */
struct _GWidthTracker
{
    GObject parent;                         /* A laisser en premier        */

    GBufferCache *cache;                    /* Ensemble complet de lignes  */
    size_t col_count;                       /* Nombre maximum de colonnes  */
    size_t opt_count;                       /* Qté de colonnes en option   */

    common_metrics *portions;               /* Portions représentées       */
    size_t count;                           /* Quantité de ces portions    */

    gint *min_widths;                       /* Largeurs min. à respecter   */

    line_width_summary summary;             /* Largeurs requises suivies   */
    bool cached;                            /* Mise en cache des calculs   */

};

/* Gestionnaire de largeurs associées aux lignes (classe) */
struct _GWidthTrackerClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};


/* Procède à l'initialisation d'une classe de suivi de largeurs. */
static void g_width_tracker_class_init(GWidthTrackerClass *);

/* Procède à l'initialisation d'un suivi de largeurs de lignes. */
static void g_width_tracker_init(GWidthTracker *);

/* Supprime toutes les références externes. */
static void g_width_tracker_dispose(GWidthTracker *);

/* Procède à la libération totale de la mémoire. */
static void g_width_tracker_finalize(GWidthTracker *);

/* Recherche la portion contenant un indice de ligne donné. */
static size_t g_width_tracker_find_metrics(const GWidthTracker *, size_t);

/* Prend en compte une évolution du volume de lignes. */
static void g_width_tracker_update_ranges(GWidthTracker *, size_t, size_t);

/* Réinitialise les largeurs requises par une portion de lignes.* */
static void g_width_tracker_reset_widths(GWidthTracker *, size_t);

/* Recalcule les largeurs requises par une portion de lignes. */
static const line_width_summary *g_width_tracker_get_up_to_date_widths(GWidthTracker *, size_t);

/* Calcule les largeurs requises par un ensemble de lignes. */
static void g_width_tracker_ensure_valid_required_widths(GWidthTracker *);



/* ---------------------------------------------------------------------------------- */
/*                             PRISE DE MESURES INITIALES                             */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour les tâches de mesures de largeurs. */
G_DEFINE_TYPE(GWidthUpdate, g_width_update, G_TYPE_DELAYED_WORK);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des tâches de mesures de largeurs.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_width_update_class_init(GWidthUpdateClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDelayedWorkClass *work;                /* Version en classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_width_update_dispose;
    object->finalize = (GObjectFinalizeFunc)g_width_update_finalize;

    work = G_DELAYED_WORK_CLASS(klass);

    work->run = (run_task_fc)g_width_update_process;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : update = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une tâche de mesures de largeurs.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_width_update_init(GWidthUpdate *update)
{
    memset(&update->summary, 0, sizeof(line_width_summary));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : update = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_width_update_dispose(GWidthUpdate *update)
{
    g_clear_object(&update->tracker);

    G_OBJECT_CLASS(g_width_update_parent_class)->dispose(G_OBJECT(update));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : update = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_width_update_finalize(GWidthUpdate *update)
{
    G_OBJECT_CLASS(g_width_update_parent_class)->finalize(G_OBJECT(update));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : id      = identifiant pour signaler la progression courante. *
*                tracker = gestionnaire de largeurs à consulter.              *
*                start   = indice de la première ligne à traiter.             *
*                end     = indice de la première ligne à éviter.              *
*                                                                             *
*  Description : Crée une tâche de mesures de largeurs.                       *
*                                                                             *
*  Retour      : Tâche créée.                                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GWidthUpdate *g_width_update_new(activity_id_t id, GWidthTracker *tracker, size_t start, size_t end)
{
    GWidthUpdate *result;                   /* Tâche à retourner           */

    result = g_object_new(G_TYPE_WIDTH_UPDATE, NULL);

    result->id = id;

    g_object_ref(G_OBJECT(tracker));
    result->tracker = tracker;

    result->start = start;
    result->end = end;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : update = opération de mesures à mener.                       *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Assure les mesures initiales d'un ensemble de lignes.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_width_update_process(GWidthUpdate *update, GtkStatusStack *status)
{
    line_width_summary *local;              /* Valeurs collectées          */
    size_t i;                               /* Boucle de parcours #1       */
    const line_width_summary *summary;      /* Valeurs à intégrer          */
    size_t k;                               /* Boucle de parcours #2       */

    local = &update->summary;

    for (i = update->start; i < update->end; i++)
    {
        summary = g_width_tracker_get_up_to_date_widths(update->tracker, i);

        for (k = 0; k < update->tracker->col_count; k++)
            local->max_widths[k] = MAX(local->max_widths[k], summary->max_widths[k]);

        local->merged_width = MAX(local->merged_width, summary->merged_width);

        gtk_status_stack_update_activity_value(status, update->id, 1);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : update = opération de mesures menée à bien.                  *
*                global = lieu de centralisation des données globales.        *
*                                                                             *
*  Description : Récupère les données obtenues lors d'une mesure globale.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_width_update_collect(GWidthUpdate *update, line_width_summary *global)
{
    line_width_summary *local;              /* Valeurs collectées          */
    size_t i;                               /* Boucle de parcours          */

    local = &update->summary;

    for (i = 0; i < update->tracker->col_count; i++)
        global->max_widths[i] = MAX(global->max_widths[i], local->max_widths[i]);

    global->merged_width = MAX(global->merged_width, local->merged_width);

}



/* ---------------------------------------------------------------------------------- */
/*                              RASSEMBLEMENT DE MESURES                              */
/* ---------------------------------------------------------------------------------- */


/* Détermine le type du gestionnaire de largeurs associées aux lignes. */
G_DEFINE_TYPE(GWidthTracker, g_width_tracker, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe de composant GTK à initialiser.               *
*                                                                             *
*  Description : Procède à l'initialisation d'une classe de suivi de largeurs.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_width_tracker_class_init(GWidthTrackerClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_width_tracker_dispose;
    object->finalize = (GObjectFinalizeFunc)g_width_tracker_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tracker = composant GLib à initialiser.                      *
*                                                                             *
*  Description : Procède à l'initialisation d'un suivi de largeurs de lignes. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_width_tracker_init(GWidthTracker *tracker)
{
    tracker->portions = NULL;
    tracker->count = 0;

    memset(&tracker->summary, 0, sizeof(line_width_summary));
    tracker->cached = false;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tracker = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_width_tracker_dispose(GWidthTracker *tracker)
{
    g_object_unref(G_OBJECT(tracker->cache));

    G_OBJECT_CLASS(g_width_tracker_parent_class)->dispose(G_OBJECT(tracker));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tracker = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_width_tracker_finalize(GWidthTracker *tracker)
{
    if (tracker->min_widths != NULL)
        free(tracker->min_widths);

    G_OBJECT_CLASS(g_width_tracker_parent_class)->finalize(G_OBJECT(tracker));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cache     = tampon de lignes à lier au futur élément.        *
*                col_count = quantité maximale de colonnes à considérer.      *
*                opt_count = quantité de colonnes optionnelles.               *
*                                                                             *
*  Description : Crée un nouveau suivi de largeurs au sein de lignes.         *
*                                                                             *
*  Retour      : Composant GLib créé.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GWidthTracker *g_width_tracker_new(GBufferCache *cache, size_t col_count, size_t opt_count)
{
    GWidthTracker *result;                  /* Composant à retourner       */

    result = g_object_new(G_TYPE_WIDTH_TRACKER, NULL);

    g_object_ref(G_OBJECT(cache));
    result->cache = cache;

    result->col_count = col_count;
    result->opt_count = opt_count;

    result->min_widths = calloc(col_count, sizeof(gint));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : buffer = tampon contenant les lignes à surveiller.           *
*                first  = indice de la première ligne d'une zone réduite.     *
*                last   = indice de la dernière ligne d'une zone réduite.     *
*                                                                             *
*  Description : Crée un nouveau suivi de largeurs au sein de lignes.         *
*                                                                             *
*  Retour      : Composant GLib créé.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GWidthTracker *g_width_tracker_new_restricted(const GWidthTracker *template, size_t first, size_t last)
{
    GWidthTracker *result;                  /* Composant à retourner       */
    size_t start;                           /* Début de la zone à copier   */
    size_t end;                             /* Fin de cette même zone      */
    size_t i;                               /* Boucle de parcours          */

    result = g_object_new(G_TYPE_WIDTH_TRACKER, NULL);

    g_object_ref(G_OBJECT(template->cache));
    result->cache = template->cache;

    result->col_count = template->col_count;
    result->opt_count = template->opt_count;

    start = g_width_tracker_find_metrics(template, first);
    assert(start < template->count);

    end = g_width_tracker_find_metrics(template, last);
    assert(end < template->count);

    result->count = end - start + 1;
    result->portions = calloc(result->count, sizeof(common_metrics));

    for (i = 0; i < result->count; i++)
        memcpy(&result->portions[i], &template->portions[start + i], sizeof(common_metrics));

    if (result->portions[0].first != first)
    {
        result->portions[0].first = first;
        g_width_tracker_reset_widths(result, 0);
    }

    if (result->portions[result->count - 1].last != last)
    {
        result->portions[result->count - 1].last = last;
        g_width_tracker_reset_widths(result, result->count - 1);
    }

    result->min_widths = calloc(template->col_count, sizeof(gint));

    for (i = 0; i < template->col_count; i++)
        result->min_widths[i] = template->min_widths[i];

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tracker = gestionnaire de largeurs de lignes à consulter.    *
*                                                                             *
*  Description : Indique le nombre de colonnes prises en compte.              *
*                                                                             *
*  Retour      : Quantité normalement strictement positive.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_width_tracker_count_columns(const GWidthTracker *tracker)
{
    size_t result;                          /* Quantité à retourner        */

    result = tracker->col_count;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tracker = gestionnaire de largeurs de lignes à mettre jour.  *
*                col     = indice de colonne visée.                           *
*                                                                             *
*  Description : Indique la largeur minimale pour une colonne donnée.         *
*                                                                             *
*  Retour      : Largeur minimale à imposée, nulle ou positive.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

gint g_width_tracker_get_column_min_width(GWidthTracker *tracker, size_t col)
{
    gint result;                            /* Largeur à renvoyer          */

    assert(col < tracker->col_count);

    result = tracker->min_widths[col];

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tracker = gestionnaire de largeurs de lignes à mettre jour.  *
*                col     = indice de colonne visée.                           *
*                width   = largeur minimale à imposer.                        *
*                                                                             *
*  Description : Impose une largeur minimale pour une colonne donnée.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_width_tracker_set_column_min_width(GWidthTracker *tracker, size_t col, gint width)
{
    assert(col < tracker->col_count);

    if (width < 0)
        width = 0;

    tracker->min_widths[col] = width;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tracker = gestionnaire de suivi à consulter.                 *
*                index   = indice d'une ligne dont la portion est inconnue.   *
*                                                                             *
*  Description : Recherche la portion contenant un indice de ligne donné.     *
*                                                                             *
*  Retour      : Indice de portion trouvée ou le nombre de portions sinon.    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static size_t g_width_tracker_find_metrics(const GWidthTracker *tracker, size_t index)
{
    size_t result;                          /* Indice trouvé à retourner   */
    common_metrics *found;                  /* Portion trouvée ou NULL     */

    int look_for_metrics(const size_t *idx, const common_metrics *m)
    {
        int status;

        if (*idx < m->first)
            status = -1;

        else if (*idx > m->last)
            status = 1;

        else
            status = 0;

        return status;

    }

    found = bsearch(&index, tracker->portions, tracker->count,
                    sizeof(common_metrics), (__compar_fn_t)look_for_metrics);

    if (found == NULL)
        result = tracker->count;
    else
        result = found - tracker->portions;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tracker = gestionnaire de largeurs de lignes à mettre jour.  *
*                start   = première ligne à traiter.                          *
*                diff    = nombre de lignes ajoutées ou supprimées.           *
*                                                                             *
*  Description : Prend en compte une évolution du volume de lignes.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_width_tracker_update_ranges(GWidthTracker *tracker, size_t start, size_t diff)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = start; i < tracker->count; i++)
    {
#ifndef NDEBUG
        if ((i + 1) < tracker->count)
            assert((tracker->portions[i].last + 1) == tracker->portions[i + 1].first);
#endif

        tracker->portions[i].first += diff;
        tracker->portions[i].last += diff;

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tracker = gestionnaire de largeurs de lignes à mettre jour.  *
*                index   = indice de portion à marquer pour réinitialisation. *
*                                                                             *
*  Description : Réinitialise les largeurs requises par une portion de lignes.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_width_tracker_reset_widths(GWidthTracker *tracker, size_t index)
{
    common_metrics *portion;                /* Portion à actualiser        */
    size_t k;                               /* Boucle de parcours          */

    assert(index < tracker->count);

    portion = &tracker->portions[index];

    /* Réinitialisation globale ? */

    if (portion->cached)
    {
        for (k = 0; k < tracker->col_count && tracker->cached; k++)
            tracker->cached &= (tracker->summary.max_widths[k] != portion->summary.max_widths[k]);

        tracker->cached &= (tracker->summary.merged_width != portion->summary.merged_width);

    }

    /* Réinitialisation locale */

    portion->cached = false;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tracker = gestionnaire de largeurs de lignes à mettre jour.  *
*                index   = indice de la portion à rafraîchir.                 *
*                                                                             *
*  Description : Recalcule les largeurs requises par une portion de lignes.   *
*                                                                             *
*  Retour      : Accès en lecture seule au résumé à jour.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static const line_width_summary *g_width_tracker_get_up_to_date_widths(GWidthTracker *tracker, size_t index)
{
    common_metrics *portion;                /* Portion à actualiser        */
    gint *widths;                           /* Collecte de largeurs        */
    gint merged;                            /* Collecte de fusion          */
    size_t i;                               /* Boucle de parcours #1       */
    size_t k;                               /* Boucle de parcours #2       */

    assert(index < tracker->count);

    portion = &tracker->portions[index];

    if (!portion->cached)
    {
        /* Réinitialisation locale */

        memset(&portion->summary, 0, sizeof(line_width_summary));

        /* Collecte */

        widths = malloc(tracker->col_count * sizeof(gint));

        for (i = portion->first; i <= portion->last; i++)
        {
            g_buffer_cache_collect_widths(tracker->cache, i, tracker->col_count, tracker->opt_count,
                                          widths, &merged);

            for (k = 0; k < tracker->col_count; k++)
                portion->summary.max_widths[k] = MAX(portion->summary.max_widths[k], widths[k]);

            portion->summary.merged_width = MAX(portion->summary.merged_width, merged);

        }

        free(widths);

        /* Marquage pour mémoire */

        portion->cached = true;

    }

    return &portion->summary;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tracker = gestionnaire de largeurs de lignes à mettre jour.  *
*                index   = position de la première des lignes à ajouter.      *
*                                                                             *
*  Description : Prend acte d'un changement sur une ligne pour les largeurs.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_width_tracker_update(GWidthTracker *tracker, size_t index)
{
    size_t current;                         /* Indice de portion visée     */

    current = g_width_tracker_find_metrics(tracker, index);

    g_width_tracker_reset_widths(tracker, current);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tracker = gestionnaire de largeurs de lignes à mettre jour.  *
*                index   = position de la première des lignes à ajouter.      *
*                count   = quantité de lignes devant être ajoutées.           *
*                                                                             *
*  Description : Prend acte de l'ajout de lignes pour les largeurs.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_width_tracker_update_added(GWidthTracker *tracker, size_t index, size_t count)
{
    size_t current;                         /* Indice de portion visée     */
    common_metrics *portion;                /* Portion sélectionnée        */
    size_t i;                               /* Boucle de parcours          */
    size_t dest;                            /* Destination d'une recopie   */
    size_t src;                             /* Source d'une recopie        */

    /* Cas particulier du premier ajout */
    if (tracker->count == 0)
    {
        assert(index == 0);

        tracker->portions = calloc(1, sizeof(common_metrics));
        tracker->count = 1;

        tracker->portions[0].first = 0;
        tracker->portions[0].last = count - 1;

        g_width_tracker_reset_widths(tracker, 0);

        return;

    }

    current = g_width_tracker_find_metrics(tracker, index);

    /* Si la ligne est rajoutée en fin d'ensemble */
    if (current == tracker->count)
    {
        current = tracker->count - 1;
        portion = &tracker->portions[current];

        assert(index == (portion->last + 1));

    }
    else
        portion = &tracker->portions[current];

    portion->last += count;

    g_width_tracker_reset_widths(tracker, current);

    /* Suite impérative : accroître les indices ! */

    g_width_tracker_update_ranges(tracker, current + 1, count);

    /* Un découpage s'impose-t-il quelque part ? */

    for (i = index + count - 1; i >= index; i--)
    {
        if (g_buffer_cache_get_line_flags(tracker->cache, i) & BLF_WIDTH_MANAGER)
        {
            /* Insertion d'une nouvelle place */

            tracker->count++;

            tracker->portions = realloc(tracker->portions, tracker->count * sizeof(common_metrics));

            portion = &tracker->portions[current];

            dest = current + 2;
            src = current + 1;

            if ((tracker->count - src) > 0)
                memmove(&tracker->portions[dest], &tracker->portions[src],
                        (tracker->count - src - 1) * sizeof(common_metrics));

            /* Insertion au début */
            if (i == portion->first)
            {
                assert(i == index);

                tracker->portions[current + 1].first = i + 1;
                tracker->portions[current + 1].last = portion->last;

                tracker->portions[current + 1].cached = false;

                portion->first = i;
                portion->last = i;

            }

            /* Insertion au sein de la portion ou à la fin */
            else
            {
                tracker->portions[current + 1].first = i;
                tracker->portions[current + 1].last = portion->last;

                tracker->portions[current + 1].cached = false;

                portion->last = i - 1;

            }

            assert((tracker->portions[current].last + 1) == tracker->portions[current + 1].first);

            /* Mise à jour des largeurs */

            g_width_tracker_reset_widths(tracker, current);

            g_width_tracker_reset_widths(tracker, current + 1);

        }

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tracker = gestionnaire de largeurs de lignes à mettre jour.  *
*                start   = première ligne devant être supprimée.              *
*                end     = dernière ligne devant être supprimée.              *
*                                                                             *
*  Description : Prend acte de la suppression de lignes pour les largeurs.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_width_tracker_update_deleted(GWidthTracker *tracker, size_t start, size_t end)
{
    size_t first;                           /* Première portion concernée  */
    size_t last;                            /* Dernière portion concernée  */
    size_t diff;                            /* Nombre de lignes supprimées */
    bool keep_first;                        /* Conservation de portion #1  */
    size_t dest;                            /* Destination du transfert    */
    bool keep_last;                         /* Conservation de portion #2  */
    size_t src;                             /* Source du transfert         */
    size_t update;                          /* Début de la série en rafale */

    first = g_width_tracker_find_metrics(tracker, start);
    assert(first < tracker->count);

    last = g_width_tracker_find_metrics(tracker, end);
    assert(last < tracker->count);

    diff = end - start + 1;

    /* Suppression de portions inutiles ? */

    keep_first = (tracker->portions[first].first < start);

    dest = (keep_first ? first + 1 : first);

    keep_last = (end < tracker->portions[last].last);

    src = (keep_last ? last : last + 1);

    if (src > dest)
    {
        if (src < tracker->count)
            memmove(&tracker->portions[dest], &tracker->portions[src],
                    (tracker->count - src) * sizeof(common_metrics));

        tracker->count -= (src - dest);

        tracker->portions = realloc(tracker->portions, tracker->count * sizeof(common_metrics));

    }

    /* Si une fusion s'impose */

    if (keep_first && keep_last && last != first)
    {
        tracker->portions[first].last = tracker->portions[first + 1].last;

        if ((first - 2) < tracker->count)
            memmove(&tracker->portions[first + 1], &tracker->portions[first + 2],
                    (tracker->count - first - 2) * sizeof(common_metrics));

        tracker->count--;

        tracker->portions = realloc(tracker->portions, tracker->count * sizeof(common_metrics));

        keep_last = false;

    }

    /* Avant toute chose : faire décroître les indices ! */

    if (keep_first && keep_last)
    {
        tracker->portions[first].last -= diff;
        update = first + 1;
    }

    else
    {
        if (keep_first)
        {
            tracker->portions[first].last = start - 1;
            update = first + 1;
        }
        else
            update = first;

        if (keep_last)
            tracker->portions[update].first = end + 1;

    }

    g_width_tracker_update_ranges(tracker, update, -diff);

    /* Mise à jour des largeurs aux extrémités */

    if (keep_first)
        g_width_tracker_reset_widths(tracker, first);

    if (keep_last && !keep_first)
        g_width_tracker_reset_widths(tracker, update);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tracker = suivi de largeurs dont le cache est à construire.  *
*                gid     = groupe de travail impliqué.                        *
*                status  = barre de statut à tenir informée.                  *
*                                                                             *
*  Description : Calcule les largeurs requises par un ensemble de lignes.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_width_tracker_build_initial_cache(GWidthTracker *tracker, wgroup_id_t gid, GtkStatusStack *status)
{
    guint runs_count;                       /* Qté d'exécutions parallèles */
    GWidthUpdate **updates;                 /* Mesures à suivre            */
    size_t run_size;                        /* Volume réparti par exécution*/
    GWorkQueue *queue;                      /* Gestionnaire de différés    */
    activity_id_t id;                       /* Identifiant de progression  */
    guint i;                                /* Boucle de parcours          */
    size_t start;                           /* Début de zone de traitement */
    bool closing;                           /* Détection de fin en amont   */
    size_t end;                             /* Fin de zone de traitement   */

    assert(!tracker->cached);

    /* Lancement des traitements */

    run_size = compute_run_size(tracker->count, &runs_count);

    updates = calloc(runs_count, sizeof(GWidthUpdate *));

    queue = get_work_queue();

    id = gtk_status_stack_add_activity(status, _("Computing width of all lines for rendering"), tracker->count);

    for (i = 0; i < runs_count; i++)
    {
        start = i * run_size;

        closing = ((i + 1) == runs_count);

        if (closing)
            end = tracker->count;
        else
            end = start + run_size;

        updates[i] = g_width_update_new(id, tracker, start, end);

        g_object_ref(G_OBJECT(updates[i]));
        g_work_queue_schedule_work(queue, G_DELAYED_WORK(updates[i]), gid);

    }

    g_work_queue_wait_for_completion(queue, gid);

    /* Récupération des aires */

    memset(&tracker->summary, 0, sizeof(line_width_summary));

    for (i = 0; i < runs_count; i++)
    {
        g_width_update_collect(updates[i], &tracker->summary);

        g_object_unref(G_OBJECT(updates[i]));

    }

    /* Fin */

    free(updates);

    gtk_status_stack_remove_activity(status, id);

    tracker->cached = true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tracker = suivi de largeurs à mettre à jour si besoin est.   *
*                                                                             *
*  Description : Calcule les largeurs requises par un ensemble de lignes.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_width_tracker_ensure_valid_required_widths(GWidthTracker *tracker)
{
    line_width_summary *global;             /* Valeurs collectées          */
    size_t i;                               /* Boucle de parcours #1       */
    const line_width_summary *summary;      /* Valeurs à intégrer          */
    size_t k;                               /* Boucle de parcours #2       */

    if (!tracker->cached)
    {
        global = &tracker->summary;

        /* Réinitialisation */

        memset(global, 0, sizeof(line_width_summary));

        /* Collecte */

        for (i = 0; i < tracker->count; i++)
        {
            summary = g_width_tracker_get_up_to_date_widths(tracker, i);

            for (k = 0; k < tracker->col_count; k++)
                global->max_widths[k] = MAX(global->max_widths[k], summary->max_widths[k]);

            global->merged_width = MAX(global->merged_width, summary->merged_width);

        }

        tracker->cached = true;

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tracker = suivi de largeurs à consulter.                     *
*                options = règles d'affichage des colonnes modulables.        *
*                                                                             *
*  Description : Fournit la largeur requise par une visualisation.            *
*                                                                             *
*  Retour      : Dimension calculée.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

gint g_width_tracker_get_width(GWidthTracker *tracker, const GDisplayOptions *options)
{
    gint result;                            /* Taille à retourner          */
    const line_width_summary *summary;      /* Accès rapide aux mesures    */
    gint col_width;                         /* Calcul selon les colonnes   */
    gint full_width;                        /* Calcul selon les fusions    */
    size_t count;                           /* Qté de colonnes en option   */
    size_t i;                               /* Boucle de parcours          */

    g_width_tracker_ensure_valid_required_widths(tracker);

    result = 0;

    summary = &tracker->summary;

    col_width = 0;
    full_width = 0;

    count = g_display_options_count(options);

    /* Première méthode */

    for (i = 0; i < tracker->col_count; i++)
    {
        if (i < count)
        {
            if (!g_display_options_get(options, i))
                continue;
        }

        col_width += summary->max_widths[i];

        if ((i + 1) < tracker->col_count)
            col_width += COL_MARGIN;

    }

    /* Seconde méthode */

    for (i = 0; i < count; i++)
    {
        if (!g_display_options_get(options, i))
            continue;

        full_width += summary->max_widths[i] + COL_MARGIN;

    }

    full_width += summary->merged_width;

    /* Mise en concurrence et poursuite... */

    result += + MAX(col_width, full_width);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tracker = suivi de largeurs à consulter.                     *
*                display = règles d'affichage des colonnes modulables.        *
*                                                                             *
*  Description : Fournit la largeur requise pour dépasser les marges gauches. *
*                                                                             *
*  Retour      : Dimension calculée.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

gint g_width_tracker_get_margin(GWidthTracker *tracker, const GDisplayOptions *options)
{
    gint result;                            /* Taille à retourner          */
    const line_width_summary *summary;      /* Accès rapide aux mesures    */
    size_t count;                           /* Qté de colonnes en option   */
    size_t i;                               /* Boucle de parcours          */

    g_width_tracker_ensure_valid_required_widths(tracker);

    result = 0;

    summary = &tracker->summary;

    count = g_display_options_count(options);

    for (i = 0; i < count; i++)
    {
        if (!g_display_options_get(options, i))
            continue;

        result += summary->max_widths[i] + COL_MARGIN;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tracker   = suivi de largeurs à consulter.                   *
*                index     = indice de la ligne dont la portion est visée.    *
*                col       = indice de la colonne visée par l'opération.      *
*                opt_count = quantité de colonnes initiales en options.       *
*                                                                             *
*  Description : Indique la largeur locale d'une colonne donnée.              *
*                                                                             *
*  Retour      : Taille positive ou nulle.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

gint g_width_tracker_get_local_column_width(GWidthTracker *tracker, size_t index, size_t col, size_t opt_count)
{
    gint result;                            /* Largeur à retourner         */
    size_t current;                         /* Indice de portion visée     */
    const line_width_summary *local;        /* Valeurs à intégrer          */

    g_width_tracker_ensure_valid_required_widths(tracker);

    assert(col < tracker->col_count);

    if (col < opt_count)
    {
        assert(opt_count < tracker->col_count);
        result = tracker->summary.max_widths[col];
    }

    else
    {
        current = g_width_tracker_find_metrics(tracker, index);
        assert(current < tracker->count);

        local = g_width_tracker_get_up_to_date_widths(tracker, current);

        result = local->max_widths[col];

    }

    result = MAX(result, tracker->min_widths[col]);

    return result;

}
