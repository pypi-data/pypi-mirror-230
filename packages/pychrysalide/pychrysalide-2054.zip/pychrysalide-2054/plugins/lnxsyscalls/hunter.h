
/* Chrysalide - Outil d'analyse de fichiers binaires
 * hunter.h - prototypes pour la recherche de portes vers le noyau
 *
 * Copyright (C) 2018-2019 Cyrille Bagard
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


#ifndef _PLUGINS_LNXSYSCALLS_HUNTER_H
#define _PLUGINS_LNXSYSCALLS_HUNTER_H


#include <analysis/binary.h>
#include <glibext/notifier.h>


#include "hops.h"



#define G_TYPE_GATE_HUNTER               g_gate_hunter_get_type()
#define G_GATE_HUNTER(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), g_gate_hunter_get_type(), GGateHunter))
#define G_IS_GATE_HUNTER(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_gate_hunter_get_type()))
#define G_GATE_HUNTER_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_GATE_HUNTER, GGateHunterClass))
#define G_IS_GATE_HUNTER_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_GATE_HUNTER))
#define G_GATE_HUNTER_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_GATE_HUNTER, GGateHunterClass))


/* Chasse à l'appel système (instance) */
typedef struct _GGateHunter GGateHunter;

/* Chasse à l'appel système (classe) */
typedef struct _GGateHunterClass GGateHunterClass;


/* Indique le type défini pour les tâches d'étude de routines. */
GType g_gate_hunter_get_type(void);

/* Crée une tâche d'étude de routines différée. */
GGateHunter *g_gate_hunter_new(GLoadedBinary *, GProcContext *, size_t, size_t, activity_id_t, const hunting_ops *);



#endif  /* _PLUGINS_LNXSYSCALLS_HUNTER_H */
