
/* Chrysalide - Outil d'analyse de fichiers binaires
 * scope-int.h - prototypes internes pour la définition d'une portée locale de variables
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


#ifndef _ANALYSIS_SCAN_SCOPE_INT_H
#define _ANALYSIS_SCAN_SCOPE_INT_H


#include "scope.h"



/* Portée locale de variables et règle d'appartenance (instance) */
struct _GScanScope
{
    GObject parent;                         /* A laisser en premier        */

    char *rule;                             /* Règle d'appartenance        */

};

/* Portée locale de variables et règle d'appartenance (classe) */
struct _GScanScopeClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};


/* Met en place une définition de portée pour variables. */
bool g_scan_scope_create(GScanScope *, const char *);



#endif  /* _ANALYSIS_SCAN_SCOPE_INT_H */
