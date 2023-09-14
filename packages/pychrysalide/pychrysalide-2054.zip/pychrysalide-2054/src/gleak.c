
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gleak.c - aide à la détection de fuites d'instances de GTypes
 *
 * Copyright (C) 2019 Cyrille Bagard
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


#include "gleak.h"


#include <assert.h>
#include <glib-object.h>
#include <malloc.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


#include "common/environment.h"



#define DUMP_OPEN_MSG  "\n---------- GType instance leak dump ----------\n\n"
#define DUMP_CLOSE_MSG "\n----------------------------------------------\n\n"


/* Description de type utilisé */
typedef struct _tracked_gtype_t
{
    GType type;                             /* Type GLib représenté        */
    char *name;                             /* Désignation humaine         */

} tracked_gtype_t;

/* Conservation des types même sans les greffons associés */
static tracked_gtype_t *__tracking = NULL;
static size_t __count = 0;


/* Effectue une comparaison entre deux mémorisations de GTypes. */
static int compare_gtypes_for_leaks(const tracked_gtype_t *, const tracked_gtype_t *);

/* Constitue une base de données de nom de tous les GTypes. */
static void _remember_gtypes_for_leaks(GType);

/*  Parcourt l'arborescence des types à la recherche de fuites. */
static void track_gtype_for_leak(GType, bool *);




/******************************************************************************
*                                                                             *
*  Paramètres  : a = première description à comparer.                         *
*                b = seconde description à comparer.                          *
*                                                                             *
*  Description : Effectue une comparaison entre deux mémorisations de GTypes. *
*                                                                             *
*  Retour      : Bilan de l'opération (-1, 0 ou 1).                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int compare_gtypes_for_leaks(const tracked_gtype_t *a, const tracked_gtype_t *b)
{
    int result;                             /* Bilan à retourner           */

    if (a->type < b->type)
        result = -1;

    else if (a->type > b->type)
        result = 1;

    else
        result = 0;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : root  = racine des types d'instance à parcourir.             *
*                                                                             *
*  Description : Constitue une base de données de nom de tous les GTypes.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void _remember_gtypes_for_leaks(GType root)
{
    GType *children;                        /* Liste de tous les sous-types*/
    guint count;                            /* Taille de cette liste       */
    tracked_gtype_t *new;                   /* Nouvelle feuille à mémoriser*/
    GType *iter;                            /* Boucle de parcours          */

    children = g_type_children(root, &count);

    if (count == 0)
    {
        __tracking = realloc(__tracking, ++__count * sizeof(tracked_gtype_t));

        new = &__tracking[__count - 1];

        new->type = root;
        new->name = strdup(g_type_name(root));

    }

    else
        for (iter = children; *iter != 0; iter++)
            _remember_gtypes_for_leaks(*iter);

    g_free(children);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : root  = racine des types d'instance à parcourir.             *
*                                                                             *
*  Description : Constitue une base de données de nom de tous les GTypes.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void remember_gtypes_for_leaks(void)
{
    _remember_gtypes_for_leaks(G_TYPE_OBJECT);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : root  = racine des types d'instance à retrouver.             *
*                first = suivi des premières impressions. [OUT]               *
*                                                                             *
*  Description : Parcourt l'arborescence des types à la recherche de fuites.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void track_gtype_for_leak(GType root, bool *first)
{
    GType *children;                        /* Liste de tous les sous-types*/
    guint count;                            /* Taille de cette liste       */
    int remaining;                          /* Nombre d'instances restantes*/
    const tracked_gtype_t *tracked;         /* Infos de type mémorisées    */
    GType *iter;                            /* Boucle de parcours          */

    children = g_type_children(root, &count);

    if (count == 0)
    {
        remaining = g_type_get_instance_count(root);

        if (remaining > 0)
        {
            if (*first)
            {
                fprintf(stderr, DUMP_OPEN_MSG);
                *first = false;
            }

            tracked = bsearch((tracked_gtype_t []) { { .type = root } }, __tracking,
                              __count, sizeof(tracked_gtype_t), (__compar_fn_t)compare_gtypes_for_leaks);

            assert(tracked != NULL);

            fprintf(stderr, "%s: %d\n", tracked->name, remaining);

        }

    }

    else
        for (iter = children; *iter != 0; iter++)
            track_gtype_for_leak(*iter, first);

    g_free(children);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Affiche la liste des instances courantes restantes par type. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void dump_remaining_gtypes(void)
{
    char *debug;                            /* Conditions d'environnement  */
    bool first;                             /* Première fois ?             */
    size_t i;                               /* Boucle de parcours          */

    debug = get_env_var("GOBJECT_DEBUG");

    if (strstr(debug, "instance-count") == NULL)
    {
        fprintf(stderr, DUMP_OPEN_MSG);
        fprintf(stderr, "The GOBJECT_DEBUG variable does not include instance-count.\n");
        fprintf(stderr, "Exiting the dumping process...\n");
        fprintf(stderr, DUMP_CLOSE_MSG);
    }

    else
    {
        first = true;

        qsort(__tracking, __count, sizeof(tracked_gtype_t), (__compar_fn_t)compare_gtypes_for_leaks);

        track_gtype_for_leak(G_TYPE_OBJECT, &first);

        if (!first)
            fprintf(stderr, DUMP_CLOSE_MSG);

    }

    free(debug);

    for (i = 0; i < __count; i++)
        free(__tracking[i].name);

    if (__tracking != NULL)
    {
        free(__tracking);

        __tracking = NULL;
        __count = 0;

    }

}
