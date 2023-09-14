
/* Chrysalide - Outil d'analyse de fichiers binaires
 * scope.h - prototypes pour l'équivalent Python du fichier "plugins/kaitai/scope.h"
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


#ifndef _PLUGINS_KAITAI_PYTHON_SCOPE_H
#define _PLUGINS_KAITAI_PYTHON_SCOPE_H


#include <Python.h>
#include <stdbool.h>


#include "../scope.h"



/* Fournit un accès à une définition de type à diffuser. */
PyTypeObject *get_python_kaitai_scope_type(void);

/* Prend en charge l'objet 'pychrysalide.common.PackedBuffer'. */
bool ensure_python_kaitai_scope_is_registered(void);

/* Convertit une structure 'kaitai_scope_t' en objet Python. */
PyObject *build_from_internal_kaitai_scope(const kaitai_scope_t *);

/* Tente de convertir en environnement local pour Kaitai. */
int convert_to_kaitai_scope(PyObject *, void *);



#endif  /* _PLUGINS_KAITAI_PYTHON_SCOPE_H */
