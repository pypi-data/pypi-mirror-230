
/* Chrysalide - Outil d'analyse de fichiers binaires
 * translate.h - prototypes pour la conversion de structures Dex en objets Python
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
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#ifndef _PLUGINS_DEX_PYTHON_TRANSLATE_H
#define _PLUGINS_DEX_PYTHON_TRANSLATE_H


#include <Python.h>


#include "../format.h"



/* Traduit des informations de type Dex en Python. */
PyObject *translate_dex_type_id_to_python(const type_id_item *);

/* Traduit des informations de type Dex en Python. */
PyObject *translate_dex_type_item_to_python(const type_item *);

/* Traduit des informations de champ Dex en Python. */
PyObject *translate_dex_field_id_to_python(const field_id_item *);

/* Traduit des informations de champ de classe Dex en Python. */
PyObject *translate_dex_field_info_to_python(const encoded_field *);

/* Traduit des identifiants de prototype Dex en Python. */
PyObject *translate_dex_proto_id_to_python(const proto_id_item *);

/* Traduit des identifiants de méthode Dex en Python. */
PyObject *translate_dex_method_id_to_python(const method_id_item *);

/* Traduit des informations de méthode Dex en Python. */
PyObject *translate_dex_method_info_to_python(const encoded_method *);

/* Traduit des informations de corps de méthode Dex en Python. */
PyObject *translate_dex_method_body_to_python(const code_item *);

/* Traduit une définition de classe Dex en Python. */
PyObject *translate_dex_class_definition_to_python(const class_def_item *);

/* Traduit des données de classe Dex en Python. */
PyObject *translate_dex_class_data_to_python(const class_data_item *);



#endif  /* _PLUGINS_DEX_PYTHON_TRANSLATE_H */
