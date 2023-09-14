
/* Chrysalide - Outil d'analyse de fichiers binaires
 * cache.c - conservation hors mémoire d'objets choisis
 *
 * Copyright (C) 2020 Cyrille Bagard
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#include "cache.h"


#include <assert.h>
#include <fcntl.h>
#include <malloc.h>
#include <unistd.h>


#include "cache-int.h"
#include "../../core/logs.h"



/* Initialise la classe des caches d'objets entreposables. */
static void g_object_cache_class_init(GObjectCacheClass *);

/* Initialise une instance de cache d'objets entreposables. */
static void g_object_cache_init(GObjectCache *);

/* Supprime toutes les références externes. */
static void g_object_cache_dispose(GObjectCache *);

/* Procède à la libération totale de la mémoire. */
static void g_object_cache_finalize(GObjectCache *);



/* Indique le type défini pour un cache d'objets entreposables. */
G_DEFINE_TYPE(GObjectCache, g_object_cache, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des caches d'objets entreposables.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_object_cache_class_init(GObjectCacheClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_object_cache_dispose;
    object->finalize = (GObjectFinalizeFunc)g_object_cache_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cache = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance de cache d'objets entreposables.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_object_cache_init(GObjectCache *cache)
{
    cache->loaded = NULL;

    cache->filename = NULL;
    cache->fd = -1;

    cache->containers = NULL;
    cache->count = 0;
    cache->free_ptr = 0;
    g_mutex_init(&cache->mutex);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cache = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_object_cache_dispose(GObjectCache *cache)
{
    size_t i;                               /* Boucle de parcours          */

    g_clear_object(&cache->loaded);

    g_mutex_lock(&cache->mutex);

    for (i = 0; i < cache->count; i++)
        g_clear_object(&cache->containers[i]);

    g_mutex_unlock(&cache->mutex);

    g_mutex_clear(&cache->mutex);

    G_OBJECT_CLASS(g_object_cache_parent_class)->dispose(G_OBJECT(cache));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cache = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_object_cache_finalize(GObjectCache *cache)
{
    int ret;                                /* Bilan d'un appel            */

    ret = access(cache->filename, W_OK);
    if (ret == 0)
    {
        ret = unlink(cache->filename);
        if (ret != 0) LOG_ERROR_N("unlink");
    }

    free(cache->filename);

    if (cache->containers != NULL)
        free(cache->containers);

    G_OBJECT_CLASS(g_object_cache_parent_class)->finalize(G_OBJECT(cache));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : loaded = contenu binaire à associer.                         *
*                                                                             *
*  Description : Crée le support d'un cache d'objets entreposables.           *
*                                                                             *
*  Retour      : Mécanismes mis en place.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GObjectCache *g_object_cache_new(GLoadedContent *loaded)
{
    GObjectCache *result;                    /* Structure à retourner       */

    result = g_object_new(G_TYPE_OBJECT_CACHE, NULL);

    if (!g_object_cache_open_for(result, loaded))
    {
        g_object_unref(G_OBJECT(result));
        result = NULL;
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cache  = cache d'objets à manipuler.                         *
*                loaded = contenu binaire à associer.                         *
*                                                                             *
*  Description : Associe un contenu à un cache d'objets.                      *
*                                                                             *
*  Retour      : Bilan de l'opéation.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_object_cache_open_for(GObjectCache *cache, GLoadedContent *loaded)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu binaire traité      */
    const gchar *checksum;                  /* Empreinte de ce contenu     */

    result = (cache->loaded == NULL);
    assert(result);

    if (result) goto done;

    cache->loaded = loaded;
    g_object_ref(G_OBJECT(loaded));

    /* Constitution du fichier de cache */

    content = g_loaded_content_get_content(loaded);

    checksum = g_binary_content_get_checksum(content);

    asprintf(&cache->filename, "/dev/shm/%s.cache", checksum);

    g_object_unref(G_OBJECT(content));

    /* Ouverture dudit fichier */

    cache->fd = open(cache->filename, O_CREAT | O_TRUNC | O_LARGEFILE, 0600);
    if (cache->fd == -1)
    {
        LOG_ERROR_N("open");
        result = false;
        goto done;
    }

    /* Préparation du cache */

    cache->count = 1000;

    cache->containers = calloc(cache->count, sizeof(GCacheContainer *));

    result = true;

 done:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cache     = cache d'objets à manipuler.                      *
*                container = objet à placer dans le cache.                    *
*                                                                             *
*  Description : Introduit un contenu dans un cache d'objets.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_object_cache_add(GObjectCache *cache, GCacheContainer *container)
{
    bool loop;                              /* Détection de trop-plein     */
    size_t i;                               /* Boucle de parcours          */

    /* Recherche d'un emplacement libre */

    loop = false;

    i = cache->free_ptr;

    do
    {
        if (cache->containers[i] != NULL)
        {
            g_cache_container_lock_unlock(cache->containers[i], true);

            if (g_cache_container_can_store(cache->containers[i]))
            {
                if (true)   // TODO     
                    g_clear_object(&cache->containers[i]);
            }

            g_cache_container_lock_unlock(cache->containers[i], false);

        }

        if (cache->containers[i] == NULL)
            break;

        i++;

        if (i == cache->count)
            i = 0;

        loop = (i == cache->free_ptr);

    } while (!loop);

    if (loop)
    {
        log_simple_message(LMT_WARNING, _("Instruction cache is full!"));
        goto exit;
    }

    /* Inscription à la liste des sursis */

    cache->containers[i] = container;

    cache->free_ptr = (i + 1);

    if (cache->free_ptr == cache->count)
        cache->free_ptr = 0;

 exit:

    ;

}
