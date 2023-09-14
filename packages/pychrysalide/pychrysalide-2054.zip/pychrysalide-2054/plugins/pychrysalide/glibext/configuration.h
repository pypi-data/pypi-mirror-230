
/* Chrysalide - Outil d'analyse de fichiers binaires
 * configuration.h - prototypes pour l'équivalent Python du fichier "glibext/configuration.h"
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


#ifndef _PLUGINS_PYCHRYSALIDE_GLIBEXT_CONFIGURATION_H
#define _PLUGINS_PYCHRYSALIDE_GLIBEXT_CONFIGURATION_H


#include <Python.h>
#include <stdbool.h>



/* ---------------------------- ELEMENT DE CONFIGURATION ---------------------------- */


/* Fournit un accès à une définition de type à diffuser. */
PyTypeObject *get_python_config_param_type(void);

/* Prend en charge l'objet 'pychrysalide.glibext.ConfigParam'. */
bool ensure_python_config_param_is_registered(void);

/* Tente de convertir en paramètre de configuration. */
int convert_to_config_param(PyObject *, void *);



/* ----------------------------- PARCOURS DE PARAMETRES ----------------------------- */


/* Fournit un accès à une définition de type à diffuser. */
PyTypeObject *get_python_config_param_iterator_type(void);

/* Prend en charge l'objet 'pychrysalide.glibext.ConfigParamIterator'. */
bool ensure_python_config_param_iterator_is_registered(void);


/* ----------------------- GESTION GENERIQUE DE CONFIGURATION ----------------------- */


/* Fournit un accès à une définition de type à diffuser. */
PyTypeObject *get_python_generic_config_type(void);

/* Prend en charge l'objet 'pychrysalide.glibext.GenConfig'. */
bool ensure_python_generic_config_is_registered(void);

/* Tente de convertir en configuration générique. */
int convert_to_generic_config(PyObject *, void *);



#endif  /* _PLUGINS_PYCHRYSALIDE_GLIBEXT_CONFIGURATION_H */
