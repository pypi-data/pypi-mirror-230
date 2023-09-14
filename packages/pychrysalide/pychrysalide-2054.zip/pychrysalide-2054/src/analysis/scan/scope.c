
/* Chrysalide - Outil d'analyse de fichiers binaires
 * scope.c - définition d'une portée locale de variables
 *
 * Copyright (C) 2023 Cyrille Bagard
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


#include "scope.h"


#include <malloc.h>
#include <string.h>


#include "scope-int.h"



/* Initialise la classe des définitions de portée locale. */
static void g_scan_scope_class_init(GScanScopeClass *);

/* Initialise une instance de définition de portée locale. */
static void g_scan_scope_init(GScanScope *);

/* Supprime toutes les références externes. */
static void g_scan_scope_dispose(GScanScope *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_scope_finalize(GScanScope *);



/* Indique le type défini pour la définition de portée de variables. */
G_DEFINE_TYPE(GScanScope, g_scan_scope, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des définitions de portée locale.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_scope_class_init(GScanScopeClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_scope_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_scope_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : scope = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance de définition de portée locale.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_scope_init(GScanScope *scope)
{
    scope->rule = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : scope = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_scope_dispose(GScanScope *scope)
{
    G_OBJECT_CLASS(g_scan_scope_parent_class)->dispose(G_OBJECT(scope));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : scope = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_scope_finalize(GScanScope *scope)
{
    if (scope->rule != NULL)
        free(scope->rule);

    G_OBJECT_CLASS(g_scan_scope_parent_class)->finalize(G_OBJECT(scope));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : rule = désignation de la règle courante dans l'analyse.      *
*                                                                             *
*  Description : Prépare une définition de portée pour variables.             *
*                                                                             *
*  Retour      : Définition mise en place.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanScope *g_scan_scope_new(const char *rule)
{
    GScanScope *result;                /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_SCOPE, NULL);

    if (!g_scan_scope_create(result, rule))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : scope = définition de portée à à initialiser pleinement.     *
*                rule  = désignation de la règle courante dans l'analyse.     *
*                                                                             *
*  Description : Met en place une définition de portée pour variables.        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_scope_create(GScanScope *scope, const char *rule)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    scope->rule = strdup(rule);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : scope = définition de portée à consulter.                    *
*                                                                             *
*  Description : Fournit le nom de la règle d'appartenance.                   *
*                                                                             *
*  Retour      : Nom de la règle courante pour une analyse.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_scan_scope_get_rule_name(const GScanScope *scope)
{
    const char *result;                     /* Chemin à retourner          */

    result = scope->rule;

    return result;

}
