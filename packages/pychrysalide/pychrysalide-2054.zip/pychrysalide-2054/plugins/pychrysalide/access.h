
/* Chrysalide - Outil d'analyse de fichiers binaires
 * access.h - prototypes pour l'accès aux modules Python en cours d'enregistrement
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


#ifndef _PLUGINS_PYCHRYSALIDE_ACCESS_H
#define _PLUGINS_PYCHRYSALIDE_ACCESS_H


#include <Python.h>



/* Enregistre une référence à un module Python en chargement. */
void register_access_to_python_module(const char *, PyObject *);

/* Fournit la référence à un module Python défini. */
PyObject *get_access_to_python_module(const char *path);

/* Supprime tous les accès rapide aux modules Python. */
void clear_all_accesses_to_python_modules(void);



#endif  /* _PLUGINS_PYCHRYSALIDE_ACCESS_H */
