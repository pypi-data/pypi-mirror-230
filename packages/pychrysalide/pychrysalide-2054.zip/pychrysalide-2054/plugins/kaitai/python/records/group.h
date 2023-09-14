
/* Chrysalide - Outil d'analyse de fichiers binaires
 * group.h - prototypes pour l'équivalent Python du fichier "plugins/kaitai/records/group.h"
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


#ifndef _PLUGINS_KAITAI_PYTHON_RECORDS_GROUP_H
#define _PLUGINS_KAITAI_PYTHON_RECORDS_GROUP_H


#include <Python.h>
#include <stdbool.h>



/* Fournit un accès à une définition de type à diffuser. */
PyTypeObject *get_python_record_group_type(void);

/* Prend en charge l'objet 'pychrysalide.plugins.kaitai.records.RecordGroup'. */
bool ensure_python_record_group_is_registered(void);

/* Tente de convertir en correspondances attribut/binaire. */
int convert_to_record_group(PyObject *, void *);



#endif  /* _PLUGINS_KAITAI_PYTHON_RECORDS_GROUP_H */
