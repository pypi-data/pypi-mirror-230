
/* Chrysalide - Outil d'analyse de fichiers binaires
 * buffercache.c - affichage à la demande d'un ensemble de lignes
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


#include "buffercache.h"


#include <assert.h>
#include <malloc.h>
#include <stdlib.h>


#include "buffercache-int.h"
#include "chrysamarshal.h"



/* --------------------- FONCTIONS AUXILIAIRES DE MANIPULATIONS --------------------- */


/* Gros verrou global pour alléger les structures... */
G_LOCK_DEFINE_STATIC(_line_update);


/* Met en place un nouvel ensemble d'information sur une ligne. */
static void init_cache_info(cache_info *, GLineGenerator *, size_t, BufferLineFlags);

/* Libère la mémoire occupée par des informations sur une ligne. */
static void release_cache_info(cache_info *);

/* Ajoute un générateur aux informations sur une ligne. */
static void extend_cache_info(cache_info *, GLineGenerator *, BufferLineFlags);

/* Retire un générateur aux informations d'une ligne. */
static void remove_from_cache_info(cache_info *, GLineGenerator *);

/* Retrouve l'emplacement correspondant à une position de ligne. */
static void get_cache_info_cursor(const cache_info *, size_t, gint, GLineCursor **);

/* Suivit les variations du compteur de références d'une ligne. */
static void on_line_ref_toggle(cache_info *, GBufferLine *, gboolean);

#ifdef INCLUDE_GTK_SUPPORT

/* Fournit la ligne de tampon correspondant aux générateurs. */
static GBufferLine *get_cache_info_line(cache_info *, const GWidthTracker *, size_t, const GBinContent *);

#endif

/* Force la réinitialisation d'une éventuelle ligne cachée. */
static void _reset_cache_info_line_unlocked(cache_info *);

/* Force la réinitialisation d'une éventuelle ligne cachée. */
static void reset_cache_info_line(cache_info *);



/* -------------------------- TAMPON POUR CODE DESASSEMBLE -------------------------- */


/* Taille des allocations de masse */
#define LINE_ALLOC_BULK 1000


/* Procède à l'initialisation d'une classe de tampon de lignes. */
static void g_buffer_cache_class_init(GBufferCacheClass *);

/* Procède à l'initialisation d'un tampon de gestion de lignes. */
static void g_buffer_cache_init(GBufferCache *);

/* Supprime toutes les références externes. */
static void g_buffer_cache_dispose(GBufferCache *);

/* Procède à la libération totale de la mémoire. */
static void g_buffer_cache_finalize(GBufferCache *);

/* Calcule l'indice d'apparition d'un générateur dans le tampon. */
static size_t g_buffer_cache_compute_repetition(GBufferCache *, size_t, GLineGenerator *);



/* ---------------------------------------------------------------------------------- */
/*                       FONCTIONS AUXILIAIRES DE MANIPULATIONS                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : info      = informations concernant une ligne à constituer.  *
*                generator = générateur à associer à toutes les lignes.       *
*                repeat    = compteur de répétition entre les lignes.         *
*                flags     = propriétés supplémentaires à associer à la ligne.*
*                                                                             *
*  Description : Met en place un nouvel ensemble d'information sur une ligne. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void init_cache_info(cache_info *info, GLineGenerator *generator, size_t repeat, BufferLineFlags flags)
{
    info->generator.instance = generator;
    info->generator.repeat = repeat;

    g_object_ref(G_OBJECT(generator));

    info->count = 1;

    info->line = NULL;

    info->extra_flags = flags;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = informations concernant une ligne à constituer.       *
*                                                                             *
*  Description : Libère la mémoire occupée par des informations sur une ligne.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void release_cache_info(cache_info *info)
{
    size_t i;                               /* Boucle de parcours          */

    if (info->count == 1)
        g_object_unref(G_OBJECT(info->generator.instance));

    else
        for (i = 0; i < info->count; i++)
            g_object_unref(G_OBJECT(info->generators[i].instance));

    reset_cache_info_line(info);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info      = informations concernant une ligne à actualiser.  *
*                generator = générateur à associer à toutes les lignes.       *
*                flags     = propriétés supplémentaires à associer à la ligne.*
*                                                                             *
*  Description : Ajoute un générateur aux informations sur une ligne.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void extend_cache_info(cache_info *info, GLineGenerator *generator, BufferLineFlags flags)
{
    generator_link first;                   /* Générateur déjà en place    */
    generator_link *new;                    /* Nouveau générateur placé    */

    if (info->count == 1)
    {
        first = info->generator;

        info->generators = calloc(2, sizeof(generator_link));

        info->generators[0] = first;
        info->count = 2;

        new = &info->generators[1];

    }
    else
    {
        info->generators = realloc(info->generators, ++info->count * sizeof(generator_link));

        new = &info->generators[info->count - 1];

    }

    new->instance = generator;
    new->repeat = 0;

    g_object_ref(G_OBJECT(generator));

    reset_cache_info_line(info);

    /**
     * On peut rajouter des indications, mais, en cas de retrait d'un générateur,
     * on ne saura pas forcément lesquelles retirer puisque qu'on ne trace pas
     * leur origine.
     *
     * On considère donc que seul le premier générateur (le principal) a le
     * droit de poser des fanions.
     */

    assert(flags == BLF_NONE);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info      = informations concernant une ligne à actualiser.  *
*                generator = générateur à dissocier de toutes les lignes.     *
*                                                                             *
*  Description : Retire un générateur aux informations d'une ligne.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void remove_from_cache_info(cache_info *info, GLineGenerator *generator)
{
    generator_link *link;                   /* Accès simplifié             */
    size_t i;                               /* Boucle de parcours          */
    generator_link *old;                    /* Mémorisation avant opérat°  */

    if (info->count == 1)
    {
        link = &info->generator;

        assert(link->instance == generator);

        g_object_unref(G_OBJECT(generator));

        info->count = 0;

    }

    else
    {
        for (i = 0; i < info->count; i++)
        {
            link = &info->generators[i];

            if (link->instance == generator)
            {
                if ((i + 1) < info->count)
                    memmove(&info->generators[i], &info->generators[i + 1],
                            (info->count - i - 1) * sizeof(generator_link));

                if (info->count == 2)
                {
                    old = info->generators;

                    info->count = 1;
                    info->generator = info->generators[0];

                    free(old);

                }
                else
                    info->generators = realloc(info->generators, --info->count * sizeof(generator_link));

                g_object_unref(G_OBJECT(generator));

                break;

            }

        }

#ifndef NDEBUG

        /**
         * Attention : si l'élément était en dernière position,
         * l'indice de parcours est désormais égal au nombre de générateurs présents !
         */
        assert(i <= info->count);

        for ( ; i < info->count; i++)
        {
            link = &info->generators[i];

            assert(link->instance != generator);

        }

#endif

    }

    reset_cache_info_line(info);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info   = informations sur une ligne à venir consulter.       *
*                index  = indice de la ligne visée par la consultation.       *
*                x      = position géographique sur la ligne concernée.       *
*                cursor = emplacement à constituer. [OUT]                     *
*                                                                             *
*  Description : Retrouve l'emplacement correspondant à une position de ligne.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void get_cache_info_cursor(const cache_info *info, size_t index, gint x, GLineCursor **cursor)
{
    const generator_link *generator;        /* Générateur retenu           */

    if (info->count == 1)
        generator = &info->generator;
    else
        generator = &info->generators[0];

    *cursor = g_line_generator_compute_cursor(generator->instance, x, index, generator->repeat);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = informations sur une ligne à venir manipuler.         *
*                line = tampon de lignes à venir supprimer au besoin.         *
*                last = indication sur la valeur du compteur de références.   *
*                                                                             *
*  Description : Suivit les variations du compteur de références d'une ligne. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_line_ref_toggle(cache_info *info, GBufferLine *line, gboolean last)
{
    if (last)
    {
        G_LOCK(_line_update);

        assert(info->line != NULL);

        _reset_cache_info_line_unlocked(info);

        G_UNLOCK(_line_update);

    }

}


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : info    = informations sur une ligne à venir manipuler.      *
*                tracker = gestionnaire de largeurs à consulter si besoin est.*
*                index   = indice de la ligne à constituer.                   *
*                content = éventuel contenu binaire brut à imprimer.          *
*                                                                             *
*  Description : Fournit la ligne de tampon correspondant aux générateurs.    *
*                                                                             *
*  Retour      : Ligne déjà en place ou créée pour le besoin.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GBufferLine *get_cache_info_line(cache_info *info, const GWidthTracker *tracker, size_t index, const GBinContent *content)
{
    GBufferLine *result;                    /* Construction à retourner    */
    size_t i;                               /* Boucle de parcours          */

    G_LOCK(_line_update);

    result = info->line;

    if (result == NULL)
    {
        result = g_buffer_line_new(g_width_tracker_count_columns(tracker));

        g_buffer_line_add_flag(result, info->extra_flags);

        g_object_add_toggle_ref(G_OBJECT(result), (GToggleNotify)on_line_ref_toggle, info);

        if (info->count == 1)
            g_line_generator_print(info->generator.instance, result, index,
                                   info->generator.repeat, content);

        else
            for (i = 0; i < info->count; i++)
                g_line_generator_print(info->generators[i].instance, result, index,
                                       info->generators[i].repeat, content);

        info->line = result;

    }

    else
        g_object_ref(G_OBJECT(result));

    G_UNLOCK(_line_update);

    return result;

}


#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : info = informations sur une ligne à venir manipuler.         *
*                                                                             *
*  Description : Force la réinitialisation d'une éventuelle ligne cachée.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void _reset_cache_info_line_unlocked(cache_info *info)
{
    if (info->line != NULL)
    {
        g_object_remove_toggle_ref(G_OBJECT(info->line), (GToggleNotify)on_line_ref_toggle, info);

        info->line = NULL;

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = informations sur une ligne à venir manipuler.         *
*                                                                             *
*  Description : Force la réinitialisation d'une éventuelle ligne cachée.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void reset_cache_info_line(cache_info *info)
{
    G_LOCK(_line_update);

    _reset_cache_info_line_unlocked(info);

    G_UNLOCK(_line_update);

}



/* ---------------------------------------------------------------------------------- */
/*                            TAMPON POUR CODE DESASSEMBLE                            */
/* ---------------------------------------------------------------------------------- */


/* Détermine le type du composant de tampon pour gestion de lignes optimisée. */
G_DEFINE_TYPE(GBufferCache, g_buffer_cache, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe de composant GLib à initialiser.              *
*                                                                             *
*  Description : Procède à l'initialisation d'une classe de tampon de lignes. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_buffer_cache_class_init(GBufferCacheClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_buffer_cache_dispose;
    object->finalize = (GObjectFinalizeFunc)g_buffer_cache_finalize;

    class->line_height = 17;
    class->left_margin = 2 * class->line_height;
    class->text_pos = 2.5 * class->line_height;

    /* Signaux */

    g_signal_new("size-changed",
                 G_TYPE_BUFFER_CACHE,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GBufferCacheClass, size_changed),
                 NULL, NULL,
                 g_cclosure_user_marshal_VOID__BOOLEAN_ULONG_ULONG,
                 G_TYPE_NONE, 3, G_TYPE_BOOLEAN, G_TYPE_ULONG, G_TYPE_ULONG);

    g_signal_new("line-updated",
                 G_TYPE_BUFFER_CACHE,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GBufferCacheClass, line_updated),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__ULONG,
                 G_TYPE_NONE, 1, G_TYPE_ULONG);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cache = composant GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation d'un tampon de gestion de lignes. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_buffer_cache_init(GBufferCache *cache)
{
    cache->content = NULL;

    cache->lines = NULL;
    cache->count = 0;
    cache->used = 0;
    g_rw_lock_init(&cache->access);

#ifdef INCLUDE_GTK_SUPPORT
    cache->tracker = NULL;
#endif

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

static void g_buffer_cache_dispose(GBufferCache *cache)
{
    size_t i;                               /* Boucle de parcours #1       */
    cache_info *info;                       /* Accès direct à une ligne    */
    size_t j;                               /* Boucle de parcours #2       */

    g_clear_object(&cache->content);

    for (i = 0; i < cache->used; i++)
    {
        info = &cache->lines[i];

        if (info->count == 1)
            g_clear_object(&info->generator.instance);

        else
            for (j = 0; j < info->count; j++)
                g_clear_object(&info->generators[j].instance);

        g_clear_object(&info->line);

    }

#ifdef INCLUDE_GTK_SUPPORT
    g_clear_object(&cache->tracker);
#endif

    G_OBJECT_CLASS(g_buffer_cache_parent_class)->dispose(G_OBJECT(cache));

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

static void g_buffer_cache_finalize(GBufferCache *cache)
{
    size_t i;                               /* Boucle de parcours          */
    cache_info *info;                       /* Accès direct à une ligne    */

    for (i = 0; i < cache->used; i++)
    {
        info = &cache->lines[i];

        if (info->count > 1)
            free(info->generators);

    }

    if (cache->lines != NULL)
        free(cache->lines);

    g_rw_lock_clear(&cache->access);

    G_OBJECT_CLASS(g_buffer_cache_parent_class)->finalize(G_OBJECT(cache));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content   = éventuel contenu binaire brut à référencer.      *
*                col_count = quantité maximale de colonnes à considérer.      *
*                opt_count = quantité de colonnes optionnelles.               *
*                                                                             *
*  Description : Crée un nouveau composant de tampon pour code désassemblé.   *
*                                                                             *
*  Retour      : Composant GLib créé.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBufferCache *g_buffer_cache_new(GBinContent *content, size_t col_count, size_t opt_count)
{
    GBufferCache *result;                   /* Composant à retourner       */

    result = g_object_new(G_TYPE_BUFFER_CACHE, NULL);

    if (content != NULL)
    {
        result->content = content;
        g_object_ref(G_OBJECT(content));
    }

#ifdef INCLUDE_GTK_SUPPORT
    result->tracker = g_width_tracker_new(result, col_count, opt_count);
#endif

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cache = tampon de lignes à consulter.                        *
*                                                                             *
*  Description : Indique l'éventuel contenu binaire associé au cache.         *
*                                                                             *
*  Retour      : Eventuel contenu renseigné ou NULL.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinContent *g_buffer_cache_get_content(const GBufferCache *cache)
{
    GBinContent *result;                    /* Contenu à retourner         */

    result = cache->content;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cache = tampon de lignes à consulter.                        *
*                                                                             *
*  Description : Fournit la hauteur d'impression d'une ligne visualisée.      *
*                                                                             *
*  Retour      : Hauteur de ligne en pixels.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

gint g_buffer_cache_get_line_height(const GBufferCache *cache)
{
    GBufferCacheClass *class;               /* Classe des tampons          */

    class = G_BUFFER_CACHE_GET_CLASS(cache);

    return class->line_height;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cache = tampon de lignes à consulter.                        *
*                                                                             *
*  Description : Fournit la taille réservée pour la marge gauche.             *
*                                                                             *
*  Retour      : Largeur en pixels.                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

gint g_buffer_cache_get_left_margin(const GBufferCache *cache)
{
    GBufferCacheClass *class;               /* Classe des tampons          */

    class = G_BUFFER_CACHE_GET_CLASS(cache);

    return class->left_margin;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cache = tampon de lignes à consulter.                        *
*                                                                             *
*  Description : Fournit la position de départ pour l'impression de texte.    *
*                                                                             *
*  Retour      : Position en pixels.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

gint g_buffer_cache_get_text_position(const GBufferCache *cache)
{
    GBufferCacheClass *class;               /* Classe des tampons          */

    class = G_BUFFER_CACHE_GET_CLASS(cache);

    return class->text_pos;

}


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : cache = composant GLib à consulter.                          *
*                                                                             *
*  Description : Fournit un lien vers la structure de suivi de largeurs.      *
*                                                                             *
*  Retour      : Gestionnaire de largeurs de lignes.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GWidthTracker *g_buffer_cache_get_width_tracker(const GBufferCache *cache)
{
    GWidthTracker *result;                  /* Instance à retourner    *   */

    result = cache->tracker;

    g_object_ref(G_OBJECT(result));

    return result;

}


#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : cache = cache de lignes à mettre à jour.                     *
*                write = précise le type d'accès prévu (lecture/écriture).    *
*                lock  = indique le sens du verrouillage à mener.             *
*                                                                             *
*  Description : Met à disposition un encadrement des accès aux lignes.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_buffer_cache_lock_unlock(GBufferCache *cache, bool write, bool lock)
{
    if (write)
    {
        if (lock) g_rw_lock_writer_lock(&cache->access);
        else g_rw_lock_writer_unlock(&cache->access);
    }
    else
    {
        if (lock) g_rw_lock_reader_lock(&cache->access);
        else g_rw_lock_reader_unlock(&cache->access);
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cache = instance GLib à consulter.                           *
*                                                                             *
*  Description : Compte le nombre de lignes rassemblées dans un tampon.       *
*                                                                             *
*  Retour      : Nombre de lignes constituant le tampon.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_buffer_cache_count_lines(GBufferCache *cache)
{
    size_t result;                          /* Quantité à retourner        */

    assert(!g_rw_lock_writer_trylock(&cache->access));

    result = cache->used;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cache     = instance GLib à consulter.                       *
*                index     = indice de la ligne où se trouve le générateur.   *
*                generator = générateur associé à au moins une ligne.         *
*                                                                             *
*  Description : Calcule l'indice d'apparition d'un générateur dans le tampon.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static size_t g_buffer_cache_compute_repetition(GBufferCache *cache, size_t index, GLineGenerator *generator)
{
    size_t result;                          /* Compteur à retourner        */
    cache_info *info;                       /* Accès direct à une ligne    */
    size_t i;                               /* Boucle de parcours          */

    result = 0;

    if (index > 0)
    {
        info = &cache->lines[index - 1];

        if (info->count == 1)
        {
            if (info->generator.instance == generator)
                result = info->generator.repeat + 1;

        }

        else
            for (i = 0; i < info->count; i++)
                if (info->generators[i].instance == generator)
                {
                    result = info->generators[i].repeat + 1;
                    break;
                }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cache     = instance GLib à modifier.                        *
*                index     = point d'insertion, puis de sauvegarde.           *
*                generator = générateur à insérer dans les lignes.            *
*                flags     = propriétés supplémentaires à associer à la ligne.*
*                before    = précise l'emplacement final des nouvelles lignes.*
*                after     = précise l'emplacement final des nouvelles lignes.*
*                                                                             *
*  Description : Insère un générateur dans des lignes à une position donnée.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_buffer_cache_insert_at(GBufferCache *cache, size_t index, GLineGenerator *generator, BufferLineFlags flags, bool before, bool after)
{
#if !defined(NDEBUG) && defined(INCLUDE_GTK_SUPPORT)
    GLineCursor *gen_cursor;                /* Position du générateur      */
    GLineCursor *line_cursor;               /* Position de la ligne        */
    int ret;                                /* Bilan de comparaison        */
#endif
    size_t needed;                          /* Emplacements nécessaires    */
    size_t i;                               /* Boucle de parcours          */

    assert(!g_rw_lock_writer_trylock(&cache->access));

    assert(index < cache->used);

    assert(!(before && after));

#if !defined(NDEBUG) && defined(INCLUDE_GTK_SUPPORT)

    if (!before && !after)
    {
        gen_cursor = g_line_generator_compute_cursor(generator, 0, index, 0);

        get_cache_info_cursor(&cache->lines[index], index, 0, &line_cursor);

        ret = g_line_cursor_compare(gen_cursor, line_cursor);

        g_object_unref(G_OBJECT(line_cursor));
        g_object_unref(G_OBJECT(gen_cursor));

        assert(ret == 0);

    }

#endif

    /* Cas particulier d'ajout en fin de cache... */
    if (after && (index + 1) == cache->used)
    {
        g_buffer_cache_append(cache, generator, flags);
        goto gbcia_done;
    }

    /* Adaptation de l'espace */

    needed = g_line_generator_count_lines(generator);

    if (before || after)
    {
        if ((cache->used + needed) >= cache->count)
        {
            cache->count += needed + LINE_ALLOC_BULK;
            cache->lines = realloc(cache->lines, cache->count * sizeof(cache_info));
        }
    }

    else if (needed > 1)
    {
        if ((cache->used + needed - 1) >= cache->count)
        {
            cache->count += needed - 1 + LINE_ALLOC_BULK;
            cache->lines = realloc(cache->lines, cache->count * sizeof(cache_info));
        }
    }

    /* Insertion du générateur */

    if (after)
        index++;

    if (before || after)
    {
        memmove(&cache->lines[index + needed], &cache->lines[index], (cache->used - index) * sizeof(cache_info));

        for (i = 0; i < needed; i++)
            init_cache_info(&cache->lines[index + i], generator, i, flags);

        cache->used += needed;

#ifdef INCLUDE_GTK_SUPPORT
        g_width_tracker_update_added(cache->tracker, index, needed);
#endif

        g_signal_emit_by_name(cache, "size-changed", true, index, needed);

    }

    else
    {
        extend_cache_info(&cache->lines[index], generator, flags);

#ifdef INCLUDE_GTK_SUPPORT
        g_width_tracker_update(cache->tracker, index);
#endif

        if (needed > 1)
        {
            /* On déborde sur les lignes suivantes, donc on crée de l'espace ! */

            memmove(&cache->lines[index + 1],
                    &cache->lines[index + 1 + needed - 1], (cache->used - index - 1) * sizeof(cache_info));

            for (i = 1; i < needed; i++)
                init_cache_info(&cache->lines[index + i], generator, i, BLF_NONE);

            cache->used += needed - 1;

#ifdef INCLUDE_GTK_SUPPORT
            g_width_tracker_update_added(cache->tracker, index + 1, needed - 1);
#endif

        }

        g_signal_emit_by_name(cache, "size-changed", true, index, needed - 1);

    }

 gbcia_done:

    ;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cache = instance GLib à modifier.                            *
*                index = point de suppression.                                *
*                                                                             *
*  Description : Retire une ligne du tampon.                                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_buffer_cache_delete_at(GBufferCache *cache, size_t index)
{
    cache_info *info;                       /* Accès direct à une ligne    */

    assert(!g_rw_lock_writer_trylock(&cache->access));

    assert(index < cache->used);

    info = &cache->lines[index];

    release_cache_info(info);

    if ((index + 1) < cache->used)
        memmove(&cache->lines[index], &cache->lines[index + 1],
                (cache->used - index - 1) * sizeof(cache_info));

    cache->used--;

#ifdef INCLUDE_GTK_SUPPORT
    g_width_tracker_update_deleted(cache->tracker, index, index);
#endif

    g_signal_emit_by_name(cache, "size-changed", false, index, 1);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cache  = instance GLib à modifier.                           *
*                index  = point d'insertion, puis de sauvegarde.              *
*                type   = type de générateurs à retirer des lignes visées.    *
*                before = précise l'emplacement final de l'élément visé.      *
*                after  = précise l'emplacement final de l'élément visé.      *
*                                                                             *
*  Description : Retire un type de générateur de lignes.                      *
*                                                                             *
*  Retour      : Générateur éventuellement trouvé ou NULL si aucun.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GLineGenerator *g_buffer_cache_delete_type_at(GBufferCache *cache, size_t index, GType type, bool before, bool after)
{
    GLineGenerator *result;                 /* Prédécesseur à retourner    */
    cache_info *info;                       /* Accès direct à une ligne    */
    generator_link *link;                   /* Accès simplifié             */
    size_t i;                               /* Boucle de parcours          */
    size_t count;                           /* Emplacements occupés        */
    size_t delete;                          /* Indice de suppression       */

    assert(!g_rw_lock_writer_trylock(&cache->access));

    assert(index < cache->used);

    assert(!(before && after));

    result = NULL;

    /* Recherche d'un générateur correspondant */

    if (before)
        info = &cache->lines[index - 1];
    else if (after)
        info = &cache->lines[index + 1];
    else
        info = &cache->lines[index];

    if (info->count == 1)
    {
        link = &info->generator;

        if (G_OBJECT_TYPE(link->instance) == type)
            result = link->instance;

    }

    else
        for (i = 0; i < info->count && result == NULL; i++)
        {
            link = &info->generators[i];

            if (G_OBJECT_TYPE(link->instance) == type)
                result = link->instance;

        }

    /* Retrait de l'instance trouvée */

    if (result != NULL)
    {
        count = g_line_generator_count_lines(result);

#ifndef NDEBUG
        if (!before && !after)
            assert(count == 1);
#endif

        g_object_ref(G_OBJECT(result));

        /* Suppression de l'élément */

        for (i = 0; i < count; i++)
        {
            if (before)
                info = &cache->lines[index - 1 - i];
            else if (after)
                info = &cache->lines[index + 1 + i];
            else
                info = &cache->lines[index];

            remove_from_cache_info(info, result);

        }

        /* Suppression des lignes associées */

        for (i = 0; i < count; i++)
        {
            if (before)
                delete = index - 1;
            else if (after)
                delete = index + 1;
            else
                delete = index;

            info = &cache->lines[delete];

            if (info->count == 0)
            {
                release_cache_info(info);

                if ((delete + 1) < cache->used)
                    memmove(&cache->lines[delete], &cache->lines[delete + 1],
                            (cache->used - delete - 1) * sizeof(cache_info));

                cache->used--;

#ifdef INCLUDE_GTK_SUPPORT
                g_width_tracker_update_deleted(cache->tracker, delete, delete);
#endif

                g_signal_emit_by_name(cache, "size-changed", false, delete, 1);

            }

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cache     = instance GLib à modifier.                        *
*                generator = générateur à associer à toutes les lignes.       *
*                flags     = propriétés supplémentaires à associer à la ligne.*
*                                                                             *
*  Description : Ajoute en fin de tampon un générateur de lignes.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_buffer_cache_append(GBufferCache *cache, GLineGenerator *generator, BufferLineFlags flags)
{
    size_t count;                           /* Nombre de lignes générées   */
    size_t index;                           /* Point d'insertion           */
    size_t i;                               /* Boucle de parcours          */
    cache_info *info;                       /* Accès direct à une ligne    */
    size_t repeat;                          /* Compteur de répétition      */

    assert(!g_rw_lock_writer_trylock(&cache->access));

    count = g_line_generator_count_lines(generator);

    assert(count > 0);

    assert((flags != BLF_NONE && count == 1) || flags == BLF_NONE);

    if ((cache->used + count) > cache->count)
    {
        cache->count += count + LINE_ALLOC_BULK;
        cache->lines = realloc(cache->lines, cache->count * sizeof(cache_info));
    }

    index = cache->used;

    for (i = 0; i < count; i++)
    {
        info = &cache->lines[index + i];

        repeat = g_buffer_cache_compute_repetition(cache, index + i, generator);

        init_cache_info(info, generator, repeat, flags);

    }

    cache->used += count;

#ifdef INCLUDE_GTK_SUPPORT
    g_width_tracker_update_added(cache->tracker, index, count);
#endif

    g_signal_emit_by_name(cache, "size-changed", true, index, count);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cache     = instance GLib à modifier.                        *
*                count     = quantité totale de lignes à avoir à disposition. *
*                generator = générateur à associer à toutes les lignes.       *
*                                                                             *
*  Description : Etend un tampon avec un générateur de lignes unique.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_buffer_cache_extend_with(GBufferCache *cache, size_t count, GLineGenerator *generator)
{
    size_t index;                           /* Point d'insertion           */
    size_t i;                               /* Boucle de parcours          */
    cache_info *info;                       /* Accès direct à une ligne    */
    size_t repeat;                          /* Compteur de répétition      */
    size_t added;                           /* Nombre d'ajouts effectués   */

    assert(!g_rw_lock_writer_trylock(&cache->access));

    assert(count >= cache->used);

    if (count > cache->count)
    {
        cache->lines = realloc(cache->lines, count * sizeof(cache_info));
        cache->count = count;
    }

    index = cache->used;

    for (i = index; i < count; i++)
    {
        info = &cache->lines[i];

        repeat = g_buffer_cache_compute_repetition(cache, i, generator);

        init_cache_info(info, generator, repeat, BLF_NONE);

    }

    added = count - cache->used;

    cache->used = count;

    if (added > 0)
    {
#ifdef INCLUDE_GTK_SUPPORT
        g_width_tracker_update_added(cache->tracker, index, added);
#endif

        g_signal_emit_by_name(cache, "size-changed", true, index, added);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cache = instance GLib à modifier.                            *
*                max   = nombre maximal de lignes à conserver.                *
*                                                                             *
*  Description : Réduit le tampon à une quantité de lignes précise.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_buffer_cache_truncate(GBufferCache *cache, size_t max)
{
    size_t i;                               /* Boucle de parcours #1       */
    cache_info *info;                       /* Accès direct à une ligne    */
    size_t j;                               /* Boucle de parcours #2       */
    size_t removed;                         /* Nombre de retraits effectués*/

    assert(!g_rw_lock_writer_trylock(&cache->access));

    for (i = max; i < cache->used; i++)
    {
        info = &cache->lines[i];

        if (info->count == 1)
            g_object_unref(G_OBJECT(info->generator.instance));

        else
        {
            for (j = 0; j < info->count; j++)
                g_object_unref(G_OBJECT(info->generators[j].instance));

            free(info->generators);

        }

        reset_cache_info_line(info);

    }

    if (max < cache->used)
    {
        removed = cache->used - max;

        cache->used = max;

#ifdef INCLUDE_GTK_SUPPORT
        g_width_tracker_update_deleted(cache->tracker, max, max + removed - 1);
#endif

        g_signal_emit_by_name(cache, "size-changed", false, max, removed);

    }

}


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : cache  = tampon de lignes à venir consulter.                 *
*                index  = indice de la ligne visée par la consultation.       *
*                x      = position géographique sur la ligne concernée.       *
*                cursor = emplacement à constituer. [OUT]                     *
*                                                                             *
*  Description : Retrouve l'emplacement correspondant à une position de ligne.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_buffer_cache_get_line_cursor(GBufferCache *cache, size_t index, gint x, GLineCursor **cursor)
{
    assert(!g_rw_lock_writer_trylock(&cache->access));

    assert(index < cache->used);

    get_cache_info_cursor(&cache->lines[index], index, x, cursor);

}


#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : cache = tampon de lignes à venir consulter.                  *
*                index = indice de la ligne visée par la consultation.        *
*                flag  = propriété à intégrer.                                *
*                                                                             *
*  Description : Ajoute une propriété particulière à une ligne.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_buffer_cache_add_line_flag(GBufferCache *cache, size_t index, BufferLineFlags flag)
{
    cache_info *info;                       /* Accès direct à une ligne    */

    assert(!g_rw_lock_writer_trylock(&cache->access));

    assert(index < cache->used);

    info = &cache->lines[index];

    if ((info->extra_flags & flag) == 0)
    {
        info->extra_flags |= flag;

        if (info->line != NULL)
            g_buffer_line_add_flag(info->line, flag);

        g_signal_emit_by_name(cache, "line-updated", index);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cache = tampon de lignes à venir consulter.                  *
*                index = indice de la ligne visée par la consultation.        *
*                                                                             *
*  Description : Détermine l'ensemble des propriétés attachées à une ligne.   *
*                                                                             *
*  Retour      : Somme de toutes les propriétés enregistrées.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

BufferLineFlags g_buffer_cache_get_line_flags(GBufferCache *cache, size_t index)
{
    BufferLineFlags result;                 /* Somme à renvoyer            */
    cache_info *info;                       /* Accès direct à une ligne    */
    const generator_link *generator;        /* Générateur retenu           */
    size_t i;                               /* Boucle de parcours          */

    assert(!g_rw_lock_writer_trylock(&cache->access));

    assert(index < cache->used);

    info = &cache->lines[index];

    result = info->extra_flags;

    if (info->count == 1)
    {
        generator = &info->generator;
        result |= g_line_generator_get_flags(generator->instance, index, generator->repeat);
    }

    else
        for (i = 0; i < info->count; i++)
        {
            generator = &info->generators[i];
            result |= g_line_generator_get_flags(generator->instance, index, generator->repeat);
        }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cache = tampon de lignes à venir consulter.                  *
*                index = indice de la ligne visée par la consultation.        *
*                flag  = propriété à supprimer.                               *
*                                                                             *
*  Description : Retire une propriété particulière attachée à une ligne.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_buffer_cache_remove_line_flag(GBufferCache *cache, size_t index, BufferLineFlags flag)
{
    cache_info *info;                       /* Accès direct à une ligne    */

    assert(!g_rw_lock_writer_trylock(&cache->access));

    assert(index < cache->used);

    info = &cache->lines[index];

    if ((info->extra_flags & flag) != 0)
    {
        info->extra_flags &= ~flag;

        if (info->line != NULL)
            g_buffer_line_remove_flag(info->line, flag);

        g_signal_emit_by_name(cache, "line-updated", index);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cache = tampon de lignes à consulter.                        *
*                start = point de départ du parcours.                         *
*                flag  = propriétés à retrouver si possible.                  *
*                                                                             *
*  Description : Avance autant que possible vers une ligne idéale.            *
*                                                                             *
*  Retour      : Indice de la ligne recherchée, si elle existe.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_buffer_cache_look_for_flag(GBufferCache *cache, size_t start, BufferLineFlags flag)
{
    size_t result;                          /* Indice de ligne à retourner */
    GLineCursor *init;                      /* Localisation de départ      */
    size_t i;                               /* Boucle de parcours          */
    GLineCursor *next;                      /* Localisation suivante       */
    int ret;                                /* Bilan de comparaison        */

    assert(!g_rw_lock_writer_trylock(&cache->access));

    assert(start < cache->used);

    result = start;

    get_cache_info_cursor(&cache->lines[start], start, 0, &init);

    for (i = start + 1; i < cache->used; i++)
    {
        get_cache_info_cursor(&cache->lines[i], i, 0, &next);

        ret = g_line_cursor_compare(init, next);

        g_object_unref(G_OBJECT(next));

        if (ret != 0)
            break;

        if ((g_buffer_cache_get_line_flags(cache, i) & flag) != 0)
        {
            result = i;
            break;
        }

    }

    g_object_unref(G_OBJECT(init));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cache = tampon de lignes à venir consulter.                  *
*                index = indice de la ligne visée par l'opération.            *
*                                                                             *
*  Description : Force la mise à jour du contenu d'une ligne donnée.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_buffer_cache_refresh_line(GBufferCache *cache, size_t index)
{
    cache_info *info;                       /* Accès direct à une ligne    */

    assert(!g_rw_lock_writer_trylock(&cache->access));

    assert(index < cache->used);

    info = &cache->lines[index];

    reset_cache_info_line(info);

    g_signal_emit_by_name(cache, "line-updated", index);

}


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : cache = tampon de lignes à consulter.                        *
*                index = indice de la ligne recherchée.                       *
*                                                                             *
*  Description : Retrouve une ligne au sein d'un tampon avec un indice.       *
*                                                                             *
*  Retour      : Line retrouvée ou NULL en cas d'échec.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBufferLine *g_buffer_cache_find_line_by_index(GBufferCache *cache, size_t index)
{
    GBufferLine *result;                    /* Ligne trouvée à retourner   */

    assert(!g_rw_lock_writer_trylock(&cache->access));

    if (index < cache->used)
        result = get_cache_info_line(&cache->lines[index], cache->tracker, index, cache->content);
    else
        result = NULL;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cache     = tampon de lignes à venir consulter.              *
*                index     = indice de la ligne à mesurer.                    *
*                col_count = quantité de colonnes à considérer.               *
*                opt_count = quantité de colonnes optionnelles.               *
*                widths    = largeur mesurée pour chacune des colonnes. [OUT] *
*                merged    = largeur cumulée en cas de fusion. [OUT]          *
*                                                                             *
*  Description : Fait remonter les largeurs requises par une ligne donnée.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_buffer_cache_collect_widths(GBufferCache *cache, size_t index, size_t col_count, size_t opt_count, gint *widths, gint *merged)
{
    GBufferLine *line;                      /* Ligne éphémère à mesurer    */

    line = get_cache_info_line(&cache->lines[index], cache->tracker, index, cache->content);

    g_buffer_line_collect_widths(line, col_count, opt_count, widths, merged);

    g_object_unref(G_OBJECT(line));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cache    = visualisation à représenter.                      *
*                cr       = contexte graphique dédié à la procédure.          *
*                first    = première ligne à dessiner.                        *
*                last     = dernière ligne à dessiner.                        *
*                area     = position et surface à traiter.                    *
*                options  = règles d'affichage des colonnes modulables.       *
*                selected = ordonnée d'une ligne sélectionnée ou NULL.        *
*                list     = liste de contenus à mettre en évidence.           *
*                                                                             *
*  Description : Imprime une partie choisie du tampon contenant des lignes.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_buffer_cache_draw(const GBufferCache *cache, cairo_t *cr, size_t first, size_t last, const cairo_rectangle_int_t *area, const GDisplayOptions *options, const gint *selected, const segcnt_list *list)
{
    GBufferCacheClass *class;               /* Classe des tampons          */
    gint y;                                 /* Point de départ en ordonnée */
    bool wait_selection;                    /* Sélection déjà passée ?     */
    size_t i;                               /* Boucle de parcours          */
    cache_info *info;                       /* Accès direct à une ligne    */
    GBufferLine *line;                      /* Ligne à venir dessiner      */

    class = G_BUFFER_CACHE_GET_CLASS(cache);

    y = 0;

    wait_selection = true;

    if (cache->used > 0)
        for (i = first; i <= last; i++)
        {
            /* Si sélection, on sousligne la ligne concernée */
            if (wait_selection && selected != NULL && *selected == y)
            {
                cairo_set_source_rgba(cr, 1.0, 1.0, 1.0, 0.05);

                cairo_rectangle(cr, area->x, y, area->width, class->line_height);
                cairo_fill(cr);

                wait_selection = false;

            }

            info = &cache->lines[i];

            line = get_cache_info_line(info, cache->tracker, i, cache->content);

            g_buffer_line_draw(line, i, cr, class->text_pos, y, cache->tracker, options, list);

            g_object_unref(G_OBJECT(line));

            y += class->line_height;

        }

}


#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : cache  = tampon de lignes à consulter.                       *
*                cursor = emplacement à retrouver dans le tampon.             *
*                first  = indique si on l'arrête à la première ou la dernière.*
*                start  = borne inférieure des recherches (incluse).          *
*                end    = borne supérieure des recherches (incluse).          *
*                                                                             *
*  Description : Indique l'indice correspondant à une adresse donnée.         *
*                                                                             *
*  Retour      : Indice des infos à l'adresse demandée, ou nombre de lignes.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t _g_buffer_cache_find_index_by_cursor(GBufferCache *cache, const GLineCursor *cursor, bool first, size_t start, size_t end)
{
    size_t result;                          /* Indice à retourner          */
    cache_info *found;                      /* Eventuel élément trouvé     */

    assert(!g_rw_lock_writer_trylock(&cache->access));

    int find_containing_generator(const GLineCursor *c, const cache_info *i)
    {
        const generator_link *generator;    /* Générateur retenu           */

        if (i->count == 1)
            generator = &i->generator;
        else
            generator = &i->generators[0];

        return g_line_generator_contain_cursor(generator->instance,
                                                i - cache->lines, generator->repeat, c);

    }

    found = (cache_info *)bsearch(cursor, &cache->lines[start], end - start + 1,
                                  sizeof(cache_info), (__compar_fn_t)find_containing_generator);

    if (found == NULL)
        result = cache->used;

    else
    {
        result = (found - cache->lines);
        assert(start <= result && result <= end);

        /* On s'assure d'un arrêt sur la bonne ligne */

        if (first)
            for (; result > start; result--)
            {
                found = &cache->lines[result - 1];

                if (find_containing_generator(cursor, found) != 0)
                    break;

            }

        else
            for (; result < end; result++)
            {
                found = &cache->lines[result + 1];

                if (find_containing_generator(cursor, found) != 0)
                    break;

            }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cache  = tampon de lignes à consulter.                       *
*                cursor = emplacement à retrouver dans le tampon.             *
*                first  = indique si on l'arrête à la première ou la dernière.*
*                                                                             *
*  Description : Indique l'indice correspondant à une adresse donnée.         *
*                                                                             *
*  Retour      : Indice des infos à l'adresse demandée, ou nombre de lignes.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_buffer_cache_find_index_by_cursor(GBufferCache *cache, const GLineCursor *cursor, bool first)
{
    size_t result;                          /* Indice à retourner          */

    assert(!g_rw_lock_writer_trylock(&cache->access));

    if (cache->used == 0)
        result = 0;
    else
        result = _g_buffer_cache_find_index_by_cursor(cache, cursor, first, 0, cache->used - 1);

    return result;

}


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : cache  = tampon de lignes à consulter.                       *
*                cursor = emplacement à présenter à l'écran.                  *
*                first  = borne inférieure des recherches (incluse).          *
*                last   = borne supérieure des recherches (incluse).          *
*                code   = s'arrête si possible à une ligne avec code.         *
*                x      = position horizontale au sein du composant. [OUT]    *
*                y      = position verticale au sein du composant. [OUT]      *
*                                                                             *
*  Description : Indique la position d'affichage d'une adresse donnée.        *
*                                                                             *
*  Retour      : true si l'adresse fait partie du composant, false sinon.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_buffer_cache_get_cursor_coordinates(GBufferCache *cache, const GLineCursor *cursor, size_t first, size_t last, bool code, gint *x, gint *y)
{
    bool result;                            /* Bilan à retourner           */
    size_t index;                           /* Indice de correspondance    */
    gint lheight;                           /* Hauteur d'une ligne         */
    const cache_info *info;                 /* Infos sur une ligne donnée  */
    const generator_link *generator;        /* Générateur retenu           */

    assert(!g_rw_lock_writer_trylock(&cache->access));

    index = _g_buffer_cache_find_index_by_cursor(cache, cursor, true, first, last);

    result = (index < cache->used);

    if (result)
    {
        lheight = G_BUFFER_CACHE_GET_CLASS(cache)->line_height;

        *x = 0;
        *y = (index - first) * G_BUFFER_CACHE_GET_CLASS(cache)->line_height;

        for (; code && index <= last; index++)
        {
            if (g_buffer_cache_get_line_flags(cache, index) & BLF_HAS_CODE)
                break;

            if (index == last)
                break;

            info = &cache->lines[index + 1];

            if (info->count == 1)
                generator = &info->generator;
            else
                generator = &info->generators[0];

            if (!g_line_generator_contain_cursor(generator->instance, index + 1, generator->repeat, cursor))
                break;

            *y += lheight;

        }

    }

    return result;

}


#endif
