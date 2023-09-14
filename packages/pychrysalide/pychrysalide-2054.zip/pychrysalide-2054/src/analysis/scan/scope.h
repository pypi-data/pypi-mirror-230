
/* Chrysalide - Outil d'analyse de fichiers binaires
 * scope.h - prototypes pour la définition d'une portée locale de variables
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
 *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _ANALYSIS_SCAN_SCOPE_H
#define _ANALYSIS_SCAN_SCOPE_H


#include <glib-object.h>
#include <stdbool.h>



#define G_TYPE_SCAN_SCOPE            g_scan_scope_get_type()
#define G_SCAN_SCOPE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_SCOPE, GScanScope))
#define G_IS_SCAN_SCOPE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_SCOPE))
#define G_SCAN_SCOPE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_SCOPE, GScanScopeClass))
#define G_IS_SCAN_SCOPE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_SCOPE))
#define G_SCAN_SCOPE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_SCOPE, GScanScopeClass))


/* Portée locale de variables et règle d'appartenance (instance) */
typedef struct _GScanScope GScanScope;

/* Portée locale de variables et règle d'appartenance (classe) */
typedef struct _GScanScopeClass GScanScopeClass;


/* Indique le type défini pour la définition de portée de variables. */
GType g_scan_scope_get_type(void);

/* Prépare une définition de portée pour variables. */
GScanScope *g_scan_scope_new(const char *);

/* Fournit le nom de la règle d'appartenance. */
const char *g_scan_scope_get_rule_name(const GScanScope *);



#endif  /* _ANALYSIS_SCAN_SCOPE_H */
