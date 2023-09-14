
/* Chrysalide - Outil d'analyse de fichiers binaires
 * plugin.h - prototypes pour les interactions avec un greffon Python
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
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#ifndef _PLUGINS_PYCHRYSALIDE_PLUGINS_PLUGIN_H
#define _PLUGINS_PYCHRYSALIDE_PLUGINS_PLUGIN_H


#include <Python.h>
#include <glib-object.h>
#include <stdbool.h>


#include <plugins/plugin.h>



/* Fournit un accès à une définition de type à diffuser. */
PyTypeObject *get_python_plugin_module_type(void);

/* Prend en charge l'objet 'pychrysalide.plugins.PluginModule'. */
bool ensure_python_plugin_module_is_registered(void);

/* Crée un greffon à partir de code Python. */
GPluginModule *create_python_plugin(const char *, const char *);



#endif  /* _PLUGINS_PYCHRYSALIDE_PLUGINS_PLUGIN_H */
