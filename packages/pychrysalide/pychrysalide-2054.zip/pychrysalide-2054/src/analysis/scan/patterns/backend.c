
/* Chrysalide - Outil d'analyse de fichiers binaires
 * backend.c - méthode de recherches au sein d'un contenu binaire
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


#include "backend.h"


#include "backend-int.h"



/* Initialise la classe des méthodes de recherche pour binaire. */
static void g_engine_backend_class_init(GEngineBackendClass *);

/* Initialise une instance de méthode de recherche pour binaire. */
static void g_engine_backend_init(GEngineBackend *);

/* Supprime toutes les références externes. */
static void g_engine_backend_dispose(GEngineBackend *);

/* Procède à la libération totale de la mémoire. */
static void g_engine_backend_finalize(GEngineBackend *);



/* Indique le type défini pour une méthode de recherche dans du binaire. */
G_DEFINE_TYPE(GEngineBackend, g_engine_backend, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des méthodes de recherche pour binaire. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_engine_backend_class_init(GEngineBackendClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_engine_backend_dispose;
    object->finalize = (GObjectFinalizeFunc)g_engine_backend_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance de méthode de recherche pour binaire.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_engine_backend_init(GEngineBackend *backend)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_engine_backend_dispose(GEngineBackend *backend)
{
    G_OBJECT_CLASS(g_engine_backend_parent_class)->dispose(G_OBJECT(backend));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_engine_backend_finalize(GEngineBackend *backend)
{
    G_OBJECT_CLASS(g_engine_backend_parent_class)->finalize(G_OBJECT(backend));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = moteur de recherche à consulter.                   *
*                                                                             *
*  Description : Indique la taille maximale des suites d'octets recherchées.  *
*                                                                             *
*  Retour      : Valeur strictement positive.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_engine_backend_get_atom_max_size(const GEngineBackend *backend)
{
    size_t result;                          /* Taille à faire connaître    */
    GEngineBackendClass *class;             /* Classe à activer            */

    class = G_ENGINE_BACKEND_GET_CLASS(backend);

    result = class->get_max_size(backend);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = moteur de recherche à manipuler.                   *
*                context = contexte de l'analyse à mener.                     *
*                plain   = chaîne de caractères classique à intégrer.         *
*                len     = taille de cette chaîne.                            *
*                                                                             *
*  Description : Inscrit dans le moteur une chaîne de caractères à rechercher.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

patid_t g_engine_backend_enroll_plain_pattern(GEngineBackend *backend, GScanContext *context, const uint8_t *plain, size_t len)
{
    patid_t result;                         /* Identifiant à retourner     */
    GEngineBackendClass *class;             /* Classe à activer            */

    class = G_ENGINE_BACKEND_GET_CLASS(backend);

    result = class->enroll_plain(backend, context, plain, len);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = moteur de recherche à préparer.                    *
*                                                                             *
*  Description : Met en ordre les derniers détails avant un premier scan.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_engine_backend_warm_up(GEngineBackend *backend)
{
    GEngineBackendClass *class;             /* Classe à activer            */

    class = G_ENGINE_BACKEND_GET_CLASS(backend);

    if (class->warm_up != NULL)
        class->warm_up(backend);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = moteur de recherche à manipuler.                   *
*                context = lieu d'enregistrement des résultats.               *
*                                                                             *
*  Description : Parcours un contenu binaire à la recherche de motifs.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_engine_backend_run_scan(const GEngineBackend *backend, GScanContext *context)
{
    GEngineBackendClass *class;             /* Classe à activer            */

    class = G_ENGINE_BACKEND_GET_CLASS(backend);

    class->run_scan(backend, context);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = moteur de recherche à consulter.                   *
*                                                                             *
*  Description : Imprime quelques faits quant aux éléments mis en place.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_engine_backend_output_stats(const GEngineBackend *backend)
{
    GEngineBackendClass *class;             /* Classe à activer            */

    class = G_ENGINE_BACKEND_GET_CLASS(backend);

    if (class->output != NULL)
        class->output(backend);

}
