
/* Chrysalide - Outil d'analyse de fichiers binaires
 * global.c - conservation et accès aux variables globales
 *
 * Copyright (C) 2017-2019 Cyrille Bagard
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


#include "global.h"


#include <assert.h>



/* Mode de fonctionnement */
static bool _batch_mode = false;

/* Gestionnaire de tâches parallèles */
static GWorkQueue *_queue = NULL;

/* Explorateur de contenus */
static GContentExplorer *_explorer = NULL;

/* Résolveur de contenus */
static GContentResolver *_resolver = NULL;

/* Espace de noms racine pour ROST */
static GScanNamespace *_rost_root_ns = NULL;

/* Projet global actif */
static GStudyProject *_project = NULL;

/* Avertisseur de changement de projet principal */
static current_project_change_cb _project_notify = NULL;



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Note un mode d'exécution sans interface.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void set_batch_mode(void)
{
    _batch_mode = true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Indique le mode d'exécution courant du programme.            *
*                                                                             *
*  Retour      : true si le fonctionnement est sans interface.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool is_batch_mode(void)
{
    return _batch_mode;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : queue = nouveau gestionnaire à mémoriser ou NULL.            *
*                                                                             *
*  Description : Définit le gestionnaire de traitements parallèles courant.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void set_work_queue(GWorkQueue *queue)
{
    assert(_queue == NULL);

    _queue = queue;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Fournit le gestionnaire de traitements parallèles courant.   *
*                                                                             *
*  Retour      : Gestionnaire de traitements parallèles courant.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GWorkQueue *get_work_queue(void)
{
    return _queue;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : explorer = éventuelle adresse du nouveau gestionnaire.       *
*                                                                             *
*  Description : Définit l'adresse de l'explorateur de contenus courant.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void set_current_content_explorer(GContentExplorer *explorer)
{
    if (_explorer != NULL)
        g_object_unref(G_OBJECT(_explorer));

    _explorer = explorer;

    if (explorer != NULL)
        g_object_ref_sink(G_OBJECT(explorer));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Fournit l'adresse de l'explorateur de contenus courant.      *
*                                                                             *
*  Retour      : Adresse de l'explorateur global ou NULL si aucun (!).        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GContentExplorer *get_current_content_explorer(void)
{
    assert(_explorer != NULL);

    g_object_ref(G_OBJECT(_explorer));

    return _explorer;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : resolver = éventuelle adresse du nouveau gestionnaire.       *
*                                                                             *
*  Description : Définit l'adresse du résolveur de contenus courant.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void set_current_content_resolver(GContentResolver *resolver)
{
    if (_resolver != NULL)
        g_object_unref(G_OBJECT(_resolver));

    _resolver = resolver;

    if (resolver != NULL)
        g_object_ref_sink(G_OBJECT(resolver));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Fournit l'adresse du résolveur de contenus courant.          *
*                                                                             *
*  Retour      : Adresse du résolveur global ou NULL si aucun (!).            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GContentResolver *get_current_content_resolver(void)
{
    assert(_resolver != NULL);

    g_object_ref(G_OBJECT(_resolver));

    return _resolver;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ns = espace de noms racine de ROST.                          *
*                                                                             *
*  Description : Définit l'adresse de l'espace de noms principal pour ROST.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void set_rost_root_namespace(GScanNamespace *ns)
{
    if (_rost_root_ns != NULL)
        g_object_unref(G_OBJECT(_rost_root_ns));

    _rost_root_ns = ns;

    if (ns != NULL)
        g_object_ref_sink(G_OBJECT(ns));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Fournit l'adresse de l'espace de noms principal pour ROST.   *
*                                                                             *
*  Retour      : Espace de noms racine de ROST ou NULL si aucun (!).          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanNamespace *get_rost_root_namespace(void)
{
    assert(_rost_root_ns != NULL);

    g_object_ref(G_OBJECT(_rost_root_ns));

    return _rost_root_ns;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : project = éventuelle adresse du nouveau projet principal.    *
*                                                                             *
*  Description : Définit l'adresse du projet courant.                         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void set_current_project(GStudyProject *project)
{
    if (_project != NULL)
    {
        if (_project_notify != NULL)
            _project_notify(_project, false);

        g_object_unref(G_OBJECT(_project));

    }

    _project = project;

    if (_project != NULL && _project_notify != NULL)
        _project_notify(_project, true);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Fournit l'adresse du projet courant.                         *
*                                                                             *
*  Retour      : Adresse du projet ouvert ou NULL si aucun (!).               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GStudyProject *get_current_project(void)
{
    if (_project != NULL)
        g_object_ref(G_OBJECT(_project));

    return _project;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : notify = procédure à appeler à chaque changement de project. *
*                                                                             *
*  Description : Enregistre une partie de code à avertir en cas de changement.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void register_project_change_notification(current_project_change_cb notify)
{
    _project_notify = notify;

}
