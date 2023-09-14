
/* Chrysalide - Outil d'analyse de fichiers binaires
 * core.h - prototypes pour le plugin permettant des extensions en Python
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


#ifndef _PLUGINS_PYCHRYSALIDE_CORE_H
#define _PLUGINS_PYCHRYSALIDE_CORE_H


/**
 * Note:
 * Since Python may define some pre-processor definitions which affect the standard headers
 * on some systems, you must include Python.h before any standard headers are included.
 *
 * cf. https://docs.python.org/3.4/c-api/intro.html
 */
#include <Python.h>


#include <plugins/plugin.h>
#include <plugins/plugin-int.h>



/* Point d'entrée pour l'initialisation de Python. */
PyMODINIT_FUNC PyInit_pychrysalide(void);

/* Prend acte du chargement du greffon. */
G_MODULE_EXPORT bool chrysalide_plugin_init(GPluginModule *);

/* Prend acte du déchargement du greffon. */
G_MODULE_EXPORT void chrysalide_plugin_exit(GPluginModule *);

/* Accompagne la fin du chargement des modules natifs. */
G_MODULE_EXPORT void chrysalide_plugin_on_plugins_loaded(GPluginModule *, PluginAction);

/* Crée une instance à partir d'un type dynamique externe. */
G_MODULE_EXPORT gpointer chrysalide_plugin_build_type_instance(GPluginModule *, PluginAction, GType);

/* Présente dans le journal une exception survenue. */
void log_pychrysalide_exception(const char *, ...);



#endif  /* _PLUGINS_PYCHRYSALIDE_CORE_H */
