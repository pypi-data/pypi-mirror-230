
/* Chrysalide - Outil d'analyse de fichiers binaires
 * queue.h - prototypes pour la mise en place des mécanismes de traitements parallèles
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


#ifndef _CORE_QUEUE_H
#define _CORE_QUEUE_H


#include <stdbool.h>


#include "../glibext/delayed.h"



/**
 * Groupes d'exécution principaux.
 */

#define DEFAULT_WORK_GROUP 0
#define LOADING_WORK_GROUP 1
#define STORAGE_WORK_GROUP 2


/* Met en place les mécanismes de traitements parallèles. */
bool init_global_works(void);

/* Constitue un nouveau groupe de travail global. */
wgroup_id_t setup_global_work_group(void);

/* Constitue un nouveau petit groupe de travail global. */
wgroup_id_t setup_tiny_global_work_group(guint);

/* Supprime les mécanismes de traitements parallèles. */
void exit_global_works(void);

/* Attend que toutes les tâches de tout groupe soient traitées. */
void wait_for_all_global_works(void);



#endif  /* _CORE_QUEUE_H */
