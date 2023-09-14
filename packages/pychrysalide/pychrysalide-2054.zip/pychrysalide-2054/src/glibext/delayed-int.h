
/* Chrysalide - Outil d'analyse de fichiers binaires
 * delayed-int.h - définitions internes pour la gestion des travaux différés
 *
 * Copyright (C) 2009-2018 Cyrille Bagard
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


#ifndef _GLIBEXT_DELAYED_INT_H
#define _GLIBEXT_DELAYED_INT_H


#include "delayed.h"


#include "notifier.h"
#include "../common/dllist.h"



/* -------------------------- TACHE DIFFEREE DANS LE TEMPS -------------------------- */


/* Traite un travail programmé. */
typedef void (* run_task_fc) (GDelayedWork *, GtkStatusStack *);


/* Travail différé (instance) */
struct _GDelayedWork
{
    GObject parent;                         /* A laisser en premier        */

    DL_LIST_ITEM(link);                     /* Lien vers les maillons      */

    bool completed;                         /* Fin de la tâche ?           */
    GMutex mutex;                           /* Accès à la variable         */
    GCond cond;                             /* Attente de changement       */

};

/* Travail différé (classe) */
struct _GDelayedWorkClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    run_task_fc run;                        /* Traitement externalisé      */

    /* Signaux */

    void (* work_completed) (GDelayedWork *);

};


#define delayed_work_list_add_tail(new, head) dl_list_add_tail(new, head, GDelayedWork, link)
#define delayed_work_list_del(item, head) dl_list_del(item, head, GDelayedWork, link)



#endif  /* _GLIBEXT_DELAYED_INT_H */
