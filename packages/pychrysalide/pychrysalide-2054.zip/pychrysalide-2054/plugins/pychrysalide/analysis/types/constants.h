
/* Chrysalide - Outil d'analyse de fichiers binaires
 * constants.h - prototypes pour l'ajout des constantes de base pour les types
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


#ifndef _PLUGINS_PYCHRYSALIDE_ANALYSIS_TYPES_CONSTANTS_H
#define _PLUGINS_PYCHRYSALIDE_ANALYSIS_TYPES_CONSTANTS_H


#include <Python.h>
#include <stdbool.h>



/* Définit les constantes relatives aux types de base. */
bool define_basic_type_constants(PyTypeObject *);

/* Tente de convertir en constante BaseType. */
int convert_to_basic_type_base_type(PyObject *, void *);

/* Définit les constantes relatives aux classes et énumérations. */
bool define_class_enum_type_constants(PyTypeObject *);

/* Tente de convertir en constante ClassEnumKind. */
int convert_to_class_enum_type_class_enum_kind(PyObject *, void *);

/* Définit les constantes relatives aux types encapsulés. */
bool define_encapsulated_type_constants(PyTypeObject *);

/* Tente de convertir en constante EncapsulationType. */
int convert_to_encapsulation_type(PyObject *, void *);



#endif  /* _PLUGINS_PYCHRYSALIDE_ANALYSIS_TYPES_CONSTANTS_H */
