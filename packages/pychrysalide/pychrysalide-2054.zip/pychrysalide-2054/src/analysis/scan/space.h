
/* Chrysalide - Outil d'analyse de fichiers binaires
 * space.h - prototypes pour la définition d'un espace de noms pour les fonctions de scan
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


#ifndef _ANALYSIS_SCAN_SPACE_H
#define _ANALYSIS_SCAN_SPACE_H


#include <glib-object.h>
#include <stdbool.h>


#include "item.h"



#define G_TYPE_SCAN_NAMESPACE            g_scan_namespace_get_type()
#define G_SCAN_NAMESPACE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_NAMESPACE, GScanNamespace))
#define G_IS_SCAN_NAMESPACE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_NAMESPACE))
#define G_SCAN_NAMESPACE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_NAMESPACE, GScanNamespaceClass))
#define G_IS_SCAN_NAMESPACE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_NAMESPACE))
#define G_SCAN_NAMESPACE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_NAMESPACE, GScanNamespaceClass))


/* Espace de noms pour un groupe de fonctions (instance) */
typedef struct _GScanNamespace GScanNamespace;

/* Espace de noms pour un groupe de fonctions (classe) */
typedef struct _GScanNamespaceClass GScanNamespaceClass;


/* Indique le type défini pour une définition d'espace de noms. */
GType g_scan_namespace_get_type(void);

/* Construit un nouvel espace de noms pour scan. */
GScanNamespace *g_scan_namespace_new(const char *);

/* Intègre un nouvel élément dans l'esapce de noms. */
bool g_scan_namespace_register_item(GScanNamespace *, GRegisteredItem *);



#endif  /* _ANALYSIS_SCAN_SPACE_H */
