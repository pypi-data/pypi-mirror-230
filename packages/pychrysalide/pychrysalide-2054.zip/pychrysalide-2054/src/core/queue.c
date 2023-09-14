
/* Chrysalide - Outil d'analyse de fichiers binaires
 * queue.c - mise en place des mécanismes de traitements parallèles
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#include "queue.h"


#include <assert.h>
#include <malloc.h>


#include "global.h"



/* Mémorisation des groupes de travail */
static wgroup_id_t *_global_group_ids = NULL;
static size_t _global_group_count = 0;
G_LOCK_DEFINE_STATIC(_gg_mutex);


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Met en place les mécanismes de traitements parallèles.       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool init_global_works(void)
{
    GWorkQueue *queue;                      /* Singleton pour tâches       */
#ifndef NDEBUG
    wgroup_id_t expected;                   /* Identifiant gloabl attendu  */
#endif

    queue = g_work_queue_new();
    set_work_queue(queue);

#ifndef NDEBUG
    expected = setup_global_work_group();
    assert(expected == DEFAULT_WORK_GROUP);
#else
    setup_global_work_group();
#endif

#ifndef NDEBUG
    expected = setup_global_work_group();
    assert(expected == LOADING_WORK_GROUP);
#else
    setup_global_work_group();
#endif

#ifndef NDEBUG
    expected = setup_global_work_group();
    assert(expected == STORAGE_WORK_GROUP);
#else
    setup_global_work_group();
#endif

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Constitue un nouveau groupe de travail global.               *
*                                                                             *
*  Retour      : Nouvel identifiant unique d'un nouveau groupe de travail.    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

wgroup_id_t setup_global_work_group(void)
{
    wgroup_id_t result;                     /* Valeur à retourner          */
    GWorkQueue *queue;                      /* Singleton pour tâches       */

    queue = get_work_queue();

    result = g_work_queue_define_work_group(queue);

    G_LOCK(_gg_mutex);

    _global_group_ids = realloc(_global_group_ids, ++_global_group_count * sizeof(wgroup_id_t));

    _global_group_ids[_global_group_count - 1] = result;

    G_UNLOCK(_gg_mutex);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : count = quantité de threads à allouer.                       *
*                                                                             *
*  Description : Constitue un nouveau petit groupe de travail global.         *
*                                                                             *
*  Retour      : Nouvel identifiant unique d'un nouveau groupe de travail.    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

wgroup_id_t setup_tiny_global_work_group(guint count)
{
    wgroup_id_t result;                     /* Valeur à retourner          */
    GWorkQueue *queue;                      /* Singleton pour tâches       */

    queue = get_work_queue();

    result = g_work_queue_define_tiny_work_group(queue, count);

    G_LOCK(_gg_mutex);

    _global_group_ids = realloc(_global_group_ids, ++_global_group_count * sizeof(wgroup_id_t));

    _global_group_ids[_global_group_count - 1] = result;

    G_UNLOCK(_gg_mutex);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Supprime les mécanismes de traitements parallèles.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void exit_global_works(void)
{
    GWorkQueue *queue;                      /* Singleton pour tâches       */

    G_LOCK(_gg_mutex);

    if (_global_group_ids != NULL)
        free(_global_group_ids);

    _global_group_ids = NULL;
    _global_group_count = 0;

    G_UNLOCK(_gg_mutex);

    queue = get_work_queue();

    g_object_unref(G_OBJECT(queue));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Attend que toutes les tâches de tout groupe soient traitées. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void wait_for_all_global_works(void)
{
    GWorkQueue *queue;                      /* Singleton pour tâches       */

    queue = get_work_queue();

    g_work_queue_wait_for_all_completions(queue, _global_group_ids, _global_group_count);

}
