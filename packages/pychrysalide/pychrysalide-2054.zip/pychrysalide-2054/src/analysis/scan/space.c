
/* Chrysalide - Outil d'analyse de fichiers binaires
 * space.c - définition d'un espace de noms pour les fonctions de scan
 *
 * Copyright (C) 2022 Cyrille Bagard
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


#include "space.h"


#include <assert.h>
#include <string.h>


#include "space-int.h"



/* ------------------------- SOCLE POUR LES ESPACES DE NOMS ------------------------- */


/* Initialise la classe des espaces de noms pour scan. */
static void g_scan_namespace_class_init(GScanNamespaceClass *);

/* Initialise une instance d'espace de noms pour scan. */
static void g_scan_namespace_init(GScanNamespace *);

/* Supprime toutes les références externes. */
static void g_scan_namespace_dispose(GScanNamespace *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_namespace_finalize(GScanNamespace *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Indique le nom associé à une expression d'évaluation. */
static char *g_scan_namespace_get_name(const GScanNamespace *);

/* Lance une résolution d'élément à solliciter. */
static bool g_scan_namespace_resolve(GScanNamespace *, const char *, GScanContext *, GScanScope *, GRegisteredItem **);



/* ---------------------------------------------------------------------------------- */
/*                           SOCLE POUR LES ESPACES DE NOMS                           */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une définition d'espace de noms. */
G_DEFINE_TYPE(GScanNamespace, g_scan_namespace, G_TYPE_REGISTERED_ITEM);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des espaces de noms pour scan.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_namespace_class_init(GScanNamespaceClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GRegisteredItemClass *registered;       /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_namespace_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_namespace_finalize;

    registered = G_REGISTERED_ITEM_CLASS(klass);

    registered->get_name = (get_registered_item_name_fc)g_scan_namespace_get_name;
    registered->resolve = (resolve_registered_item_fc)g_scan_namespace_resolve;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : space = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance d'espace de noms pour scan.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_namespace_init(GScanNamespace *space)
{
    space->name = NULL;

    space->children = NULL;
    space->names = NULL;
    space->count = 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : space = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_namespace_dispose(GScanNamespace *space)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < space->count; i++)
        g_clear_object(&space->children[i]);

    G_OBJECT_CLASS(g_scan_namespace_parent_class)->dispose(G_OBJECT(space));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : space = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_namespace_finalize(GScanNamespace *space)
{
    size_t i;                               /* Boucle de parcours          */

    if (space->name != NULL)
        free(space->name);

    if (space->children != NULL)
        free(space->children);

    for (i = 0; i < space->count; i++)
        free(space->names[i]);

    if (space->names != NULL)
        free(space->names);

    G_OBJECT_CLASS(g_scan_namespace_parent_class)->finalize(G_OBJECT(space));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : name = désignation du futur espace de noms.                  *
*                                                                             *
*  Description : Construit un nouvel espace de noms pour scan.                *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanNamespace *g_scan_namespace_new(const char *name)
{
    GScanNamespace *result;                 /* Instance à retourner        */

    result = g_object_new(G_TYPE_SCAN_NAMESPACE, NULL);

    if (!g_scan_namespace_create(result, name))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : space = instance d'espace de noms à initialiser.             *
*                name  = désignation du futur espace de noms.                 *
*                                                                             *
*  Description : Met en place un nouvel espace de noms pour scan.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_namespace_create(GScanNamespace *space, const char *name)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    if (name != NULL)
        space->name = strdup(name);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : space = espace de noms à compléter.                          *
*                child = élément d'évaluation à intégrer.                     *
*                                                                             *
*  Description : Intègre un nouvel élément dans l'esapce de noms.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_namespace_register_item(GScanNamespace *space, GRegisteredItem *child)
{
    bool result;                            /* Bilan à retourner           */
    char *name;                             /* Nom de l'élément à ajouter  */
    size_t i;                               /* Boucle de parcours          */

    name = g_registered_item_get_name(child);

    /* Validation de l'unicité du nom */

    for (i = 0; i < space->count; i++)
        if (strcmp(name, space->names[i]) == 0)
            break;

    result = (i == space->count);

    /* Inscription de l'élément ? */

    if (!result)
        free(name);

    else
    {
        space->count++;

        space->children = realloc(space->children, space->count * sizeof(GRegisteredItem *));
        space->children[space->count - 1] = child;
        g_object_ref(G_OBJECT(child));

        space->names = realloc(space->names, space->count * sizeof(char *));
        space->names[space->count - 1] = strdup(name);

    }

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : space = élément d'appel à consulter.                         *
*                                                                             *
*  Description : Indique le nom associé à une expression d'évaluation.        *
*                                                                             *
*  Retour      : Désignation humaine de l'expression d'évaluation.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_scan_namespace_get_name(const GScanNamespace *space)
{
    char *result;                           /* Désignation à retourner     */

    if (space->name != NULL)
        result = strdup(space->name);

    else
        result = NULL;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item   = élément d'appel à consulter.                        *
*                target = désignation de l'objet d'appel à identifier.        *
*                ctx    = contexte de suivi de l'analyse courante.            *
*                scope  = portée courante des variables locales.              *
*                out    = zone d'enregistrement de la résolution opérée. [OUT]*
*                                                                             *
*  Description : Lance une résolution d'élément à solliciter.                 *
*                                                                             *
*  Retour      : Bilan de l'opération : false en cas d'erreur irrécupérable.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_scan_namespace_resolve(GScanNamespace *item, const char *target, GScanContext *ctx, GScanScope *scope, GRegisteredItem **out)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours          */

    result = true;

    for (i = 0; i < item->count; i++)
        if (strcmp(target, item->names[i]) == 0)
        {
            *out = item->children[i];
            g_object_ref(G_OBJECT(*out));
            break;
        }

    return result;

}
