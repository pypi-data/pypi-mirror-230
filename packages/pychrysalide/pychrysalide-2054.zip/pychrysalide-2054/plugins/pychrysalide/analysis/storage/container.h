
/* Chrysalide - Outil d'analyse de fichiers binaires
 * container.h - prototypes pour l'équivalent Python du fichier "analysis/storage/container.h"
 *
 * Copyright (C) 2020 Cyrille Bagard
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
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#ifndef _PLUGINS_PYCHRYSALIDE_ANALYSIS_STORAGE_CONTAINER_H
#define _PLUGINS_PYCHRYSALIDE_ANALYSIS_STORAGE_CONTAINER_H


#include <Python.h>
#include <stdbool.h>



/* Fournit un accès à une définition de type à diffuser. */
PyTypeObject *get_python_cache_container_type(void);

/* Prend en charge l'objet 'pychrysalide.analysis.storage.CacheContainer'. */
bool ensure_python_cache_container_is_registered(void);

/* Tente de convertir en conteneur d'objets entreposables. */
int convert_to_cache_container(PyObject *, void *);



#endif  /* _PLUGINS_PYCHRYSALIDE_ANALYSIS_STORAGE_CONTAINER_H */
