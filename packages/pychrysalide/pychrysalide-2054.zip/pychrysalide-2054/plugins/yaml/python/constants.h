
/* Chrysalide - Outil d'analyse de fichiers binaires
 * constants.h - prototypes pour la prise en charge des constantes liées à YAML
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
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#ifndef _PLUGINS_YAML_PYTHON_CONSTANTS_H
#define _PLUGINS_YAML_PYTHON_CONSTANTS_H


#include <Python.h>
#include <stdbool.h>



/* Définit les constantes relatives au noeuds principaux. */
bool define_yaml_pair_constants(PyTypeObject *);

/* Tente de convertir en constante YamlOriginalStyle. */
int convert_to_yaml_pair_original_style(PyObject *, void *);



#endif  /* _PLUGINS_YAML_PYTHON_CONSTANTS_H */
