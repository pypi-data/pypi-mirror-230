
/* Chrysalide - Outil d'analyse de fichiers binaires
 * module.h - prototypes pour l'intégration du répertoire yaml en tant que module
 *
 * Copyright (C) 2019 Cyrille Bagard
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


#ifndef _PLUGINS_YAML_PYTHON_MODULE_H
#define _PLUGINS_YAML_PYTHON_MODULE_H


#include <stdbool.h>



/* Ajoute le module 'plugins.yaml' au module Python. */
bool add_yaml_module_to_python_module(void);

/* Intègre les objets du module 'plugins.yaml'. */
bool populate_yaml_module(void);



#endif  /* _PLUGINS_YAML_PYTHON_MODULE_H */
