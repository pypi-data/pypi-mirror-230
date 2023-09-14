
/* Chrysalide - Outil d'analyse de fichiers binaires
 * global.h - prototypes pour la conservation et l'accès aux variables globales
 *
 * Copyright (C) 2017-2018 Cyrille Bagard
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


#ifndef _CORE_GLOBAL_H
#define _CORE_GLOBAL_H


#include <stdbool.h>


#include "../analysis/loading.h"
#include "../analysis/project.h"
#include "../analysis/scan/space.h"
#include "../glibext/delayed.h"



/* Note un mode d'exécution sans interface. */
void set_batch_mode(void);

/* Indique le mode d'exécution courant du programme. */
bool is_batch_mode(void);

/* Définit le gestionnaire de traitements parallèles courant. */
void set_work_queue(GWorkQueue *);

/* Fournit le gestionnaire de traitements parallèles courant. */
GWorkQueue *get_work_queue(void);

/* Définit l'adresse de l'explorateur de contenus courant. */
void set_current_content_explorer(GContentExplorer *);

/* Fournit l'adresse de l'explorateur de contenus courant. */
GContentExplorer *get_current_content_explorer(void);

/* Définit l'adresse du résolveur de contenus courant. */
void set_current_content_resolver(GContentResolver *);

/* Fournit l'adresse du résolveur de contenus courant. */
GContentResolver *get_current_content_resolver(void);

/* Définit l'adresse de l'espace de noms principal pour ROST. */
void set_rost_root_namespace(GScanNamespace *);

/* Fournit l'adresse de l'espace de noms principal pour ROST. */
GScanNamespace *get_rost_root_namespace(void);

/* Définit l'adresse du projet courant. */
void set_current_project(GStudyProject *);

/* Fournit l'adresse du projet courant. */
GStudyProject *get_current_project(void);

/* Réagit à un changement du projet principal. */
typedef void (* current_project_change_cb) (GStudyProject *, bool);

/* Enregistre une partie de code à avertir en cas de changement. */
void register_project_change_notification(current_project_change_cb);



#endif  /* _CORE_GLOBAL_H */
