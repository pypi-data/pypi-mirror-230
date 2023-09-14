
/* Chrysalide - Outil d'analyse de fichiers binaires
 * options.c - rassemblement des options d'analyse communiquées par le donneur d'ordre
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


#include "options.h"


#include "options-int.h"



/* Initialise la classe des ensembles d'options d'analyses. */
static void g_scan_options_class_init(GScanOptionsClass *);

/* Initialise une instance de groupe d'options d'analyse. */
static void g_scan_options_init(GScanOptions *);

/* Supprime toutes les références externes. */
static void g_scan_options_dispose(GScanOptions *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_options_finalize(GScanOptions *);



/* Indique le type défini pour un ensemble d'options d'analyses. */
G_DEFINE_TYPE(GScanOptions, g_scan_options, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des ensembles d'options d'analyses.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_options_class_init(GScanOptionsClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_options_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_options_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : options = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance de groupe d'options d'analyse.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_options_init(GScanOptions *options)
{
    options->data_backend = G_TYPE_INVALID;

    options->print_json = false;
    options->print_strings = false;
    options->print_stats = false;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : options = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_options_dispose(GScanOptions *options)
{
    G_OBJECT_CLASS(g_scan_options_parent_class)->dispose(G_OBJECT(options));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : options = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_options_finalize(GScanOptions *options)
{
    G_OBJECT_CLASS(g_scan_options_parent_class)->finalize(G_OBJECT(options));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un réceptacle pour diverses options d'analyse.          *
*                                                                             *
*  Retour      : Point de collecte mise en place.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanOptions *g_scan_options_new(void)
{
    GScanOptions *result;                   /* Instance à retourner        */

    result = g_object_new(G_TYPE_SCAN_OPTIONS, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : options = ensemble d'options d'analyses à consulter.         *
*                                                                             *
*  Description : Indique le type d'un moteur d'analyse de données sélectionné.*
*                                                                             *
*  Retour      : Type d'objet, idéalement valide.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GType g_scan_options_get_backend_for_data(const GScanOptions *options)
{
    GType result;                           /* Type à retourner            */

    result = options->data_backend;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : options = ensemble d'options d'analyses à modifier.          *
*                backend = type du moteur sélectionné.                        *
*                                                                             *
*  Description : Sélectionne un type de moteur d'analyse pour données brutes. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_scan_options_set_backend_for_data(GScanOptions *options, GType backend)
{
    options->data_backend = backend;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : options = ensemble d'options d'analyses à consulter.         *
*                                                                             *
*  Description : Impose le format JSON comme type de sortie.                  *
*                                                                             *
*  Retour      : Etat de l'option visée à conservé.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_options_get_print_json(const GScanOptions *options)
{
    bool result;                            /* Statut à retourner          */

    result = options->print_json;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : options = ensemble d'options d'analyses à modifier.          *
*                state   = état de l'option visée à conserver.                *
*                                                                             *
*  Description : Mémorise le format JSON comme type de sortie.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_scan_options_set_print_json(GScanOptions *options, bool state)
{
    options->print_json = state;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : options = ensemble d'options d'analyses à consulter.         *
*                                                                             *
*  Description : Indique un besoin d'affichage des correspondances finales.   *
*                                                                             *
*  Retour      : Etat de l'option visée à conservé.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_options_get_print_strings(const GScanOptions *options)
{
    bool result;                            /* Statut à retourner          */

    result = options->print_strings;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : options = ensemble d'options d'analyses à modifier.          *
*                state   = état de l'option visée à conserver.                *
*                                                                             *
*  Description : Mémorise un besoin d'affichage des correspondances finales.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_scan_options_set_print_strings(GScanOptions *options, bool state)
{
    options->print_strings = state;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : options = ensemble d'options d'analyses à consulter.         *
*                                                                             *
*  Description : Indique un besoin de statistiques en fin de compilation.     *
*                                                                             *
*  Retour      : Etat de l'option visée à conservé.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_options_get_print_stats(const GScanOptions *options)
{
    bool result;                            /* Statut à retourner          */

    result = options->print_stats;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : options = ensemble d'options d'analyses à modifier.          *
*                state   = état de l'option visée à conserver.                *
*                                                                             *
*  Description : Mémorise un besoin de statistiques en fin de compilation.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_scan_options_set_print_stats(GScanOptions *options, bool state)
{
    options->print_stats = state;

}
