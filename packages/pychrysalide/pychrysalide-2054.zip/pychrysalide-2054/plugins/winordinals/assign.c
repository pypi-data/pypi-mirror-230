
/* Chrysalide - Outil d'analyse de fichiers binaires
 * assign.c - renseignement des importations sous forme d'ordinaux
 *
 * Copyright (C) 2021 Cyrille Bagard
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


#include "assign.h"


#include <i18n.h>
#include <core/global.h>
#include <core/nproc.h>
#include <glibext/delayed-int.h>
#include <plugins/pe/routine.h>


#include "ordinals.h"



#define G_TYPE_ORDINAL_RESOLVER            g_ordinal_resolver_get_type()
#define G_ORDINAL_RESOLVER(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_ORDINAL_RESOLVER, GOrdinalResolver))
#define G_IS_ORDINAL_RESOLVER(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_ORDINAL_RESOLVER))
#define G_ORDINAL_RESOLVER_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ORDINAL_RESOLVER, GOrdinalResolverClass))
#define G_IS_ORDINAL_RESOLVER_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ORDINAL_RESOLVER))
#define G_ORDINAL_RESOLVER_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ORDINAL_RESOLVER, GOrdinalResolverClass))


/* Tâche de résolution d'ordinaux (instance) */
typedef struct _GOrdinalResolver
{
    GDelayedWork parent;                    /* A laisser en premier        */

    GPeFormat *format;                      /* Format à faire évoluer      */

    size_t begin;                           /* Point de départ du parcours */
    size_t end;                             /* Point d'arrivée exclu       */

    activity_id_t id;                       /* Identifiant pour messages   */

} GOrdinalResolver;

/* Tâche de résolution d'ordinaux (classe) */
typedef struct _GOrdinalResolverClass
{
    GDelayedWorkClass parent;               /* A laisser en premier        */

} GOrdinalResolverClass;


/* Indique le type défini pour les tâches de résolution d'ordinaux. */
GType g_ordinal_resolver_get_type(void);

/* Initialise la classe des tâches des resolutions d'ordinaux. */
static void g_ordinal_resolver_class_init(GOrdinalResolverClass *);

/* Initialise une tâche de résolution d'ordinaux importés. */
static void g_ordinal_resolver_init(GOrdinalResolver *);

/* Supprime toutes les références externes. */
static void g_ordinal_resolver_dispose(GOrdinalResolver *);

/* Procède à la libération totale de la mémoire. */
static void g_ordinal_resolver_finalize(GOrdinalResolver *);

/* Crée une tâche de résolution des ordinaux importés. */
static GOrdinalResolver *g_ordinal_resolver_new(GPeFormat *, size_t, size_t, activity_id_t);

/* Effectue une résolution d'ordinaux importés. */
static void g_ordinal_resolver_process(GOrdinalResolver *, GtkStatusStack *);



/* Indique le type défini pour les tâches de résolution d'ordinaux. */
G_DEFINE_TYPE(GOrdinalResolver, g_ordinal_resolver, G_TYPE_DELAYED_WORK);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des tâches des resolutions d'ordinaux.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_ordinal_resolver_class_init(GOrdinalResolverClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDelayedWorkClass *work;                /* Version en classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_ordinal_resolver_dispose;
    object->finalize = (GObjectFinalizeFunc)g_ordinal_resolver_finalize;

    work = G_DELAYED_WORK_CLASS(klass);

    work->run = (run_task_fc)g_ordinal_resolver_process;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : resolver = instance à initialiser.                           *
*                                                                             *
*  Description : Initialise une tâche de résolution d'ordinaux importés.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_ordinal_resolver_init(GOrdinalResolver *resolver)
{
    resolver->format = NULL;

    resolver->begin = 0;
    resolver->end = 0;

    resolver->id = 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : resolver = instance d'objet GLib à traiter.                  *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_ordinal_resolver_dispose(GOrdinalResolver *resolver)
{
    g_clear_object(&resolver->format);

    G_OBJECT_CLASS(g_ordinal_resolver_parent_class)->dispose(G_OBJECT(resolver));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : resolver = instance d'objet GLib à traiter.                  *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_ordinal_resolver_finalize(GOrdinalResolver *resolver)
{
    G_OBJECT_CLASS(g_ordinal_resolver_parent_class)->finalize(G_OBJECT(resolver));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = ensemble d'instructions désassemblées.              *
*                begin  = point de départ du parcours de liste.               *
*                end    = point d'arrivée exclu du parcours.                  *
*                id     = identifiant du message affiché à l'utilisateur.     *
*                                                                             *
*  Description : Crée une tâche de résolution des ordinaux importés.          *
*                                                                             *
*  Retour      : Tâche créée.                                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GOrdinalResolver *g_ordinal_resolver_new(GPeFormat *format, size_t begin, size_t end, activity_id_t id)
{
    GOrdinalResolver *result;               /* Tâche à retourner           */

    result = g_object_new(G_TYPE_ORDINAL_RESOLVER, NULL);

    result->format = format;
    g_object_ref(G_OBJECT(format));

    result->begin = begin;
    result->end = end;

    result->id = id;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : resolver = étude de routines à mener.                        *
*                status   = barre de statut à tenir informée.                 *
*                                                                             *
*  Description : Effectue une résolution d'ordinaux importés.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_ordinal_resolver_process(GOrdinalResolver *resolver, GtkStatusStack *status)
{
    GBinFormat *base;                       /* Format basique du binaire   */
    size_t i;                               /* Boucle de parcours          */
    GBinSymbol *symbol;                     /* Commodité d'accès           */
    uint16_t ordinal;                       /* Ordinal défini              */
    const char *name;                       /* Désignation actuelle        */
    const char *library;                    /* Fichier DLL à charger       */

    base = G_BIN_FORMAT(resolver->format);

    for (i = resolver->begin; i < resolver->end; i++)
    {
        symbol = g_binary_format_get_symbol(base, i);

        if (!G_IS_PE_IMPORTED_ROUTINE(symbol))
            goto next;

        ordinal = g_pe_exported_routine_get_ordinal(G_PE_EXPORTED_ROUTINE(symbol));

        if (ordinal == UNDEF_PE_ORDINAL)
            goto next;

        name = g_binary_routine_get_name(G_BIN_ROUTINE(symbol));

        if (name != NULL)
            goto next;

        library = g_pe_imported_routine_get_library(G_PE_IMPORTED_ROUTINE(symbol));

        if (library == NULL)
            goto next;

        name = get_symbol_by_ordinal(library, ordinal);

        if (name != NULL)
            g_binary_routine_set_name(G_BIN_ROUTINE(symbol), strdup(name));

 next:

        gtk_status_stack_update_activity_value(status, resolver->id, 1);

        g_object_unref(G_OBJECT(symbol));

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format PE à traiter.                                *
*                status  = barre de statut à tenir informée.                  *
*                                                                             *
*  Description : Attribue un nom aux symboles PE importés par ordinal.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void assign_name_imported_ordinals(GPeFormat *format, GtkStatusStack *status)
{
    GBinFormat *base;                       /* Format basique du binaire   */
    size_t sym_count;                       /* Nombre de ces symboles      */
    guint runs_count;                       /* Qté d'exécutions parallèles */
    size_t run_size;                        /* Volume réparti par exécution*/
    activity_id_t id;                       /* Identifiant de progression  */
    GWorkQueue *queue;                      /* Gestionnaire de différés    */
    wgroup_id_t gid;                        /* Identifiant pour les tâches */
    guint i;                                /* Boucle de parcours          */
    size_t begin;                           /* Début de bloc de traitement */
    size_t end;                             /* Fin d'un bloc de traitement */
    GOrdinalResolver *resolver;             /* Tâche d'étude à programmer  */

    base = G_BIN_FORMAT(format);

    g_binary_format_lock_symbols_rd(base);

    sym_count = g_binary_format_count_symbols(base);

    run_size = compute_run_size(sym_count, &runs_count);

    id = gtk_status_stack_add_activity(status, _("Resolving names for imported ordinals..."), sym_count);

    queue = get_work_queue();

    gid = g_work_queue_define_work_group(queue);

    for (i = 0; i < runs_count; i++)
    {
        begin = i * run_size;

        if ((i + 1) == runs_count)
            end = sym_count;
        else
            end = begin + run_size;

        resolver = g_ordinal_resolver_new(format, begin, end, id);

        g_work_queue_schedule_work(queue, G_DELAYED_WORK(resolver), gid);

    }

    g_work_queue_wait_for_completion(queue, gid);

    g_work_queue_delete_work_group(queue, gid);

    gtk_status_stack_remove_activity(status, id);

    g_binary_format_unlock_symbols_rd(base);

}
