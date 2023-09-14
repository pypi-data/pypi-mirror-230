
/* Chrysalide - Outil d'analyse de fichiers binaires
 * dynamic.h - prototypes pour l'équivalent Python du fichier "plugins/elf/dynamic.h"
 *
 * Copyright (C) 2017-2018 Cyrille Bagard
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


#ifndef _PLUGINS_ELF_PYTHON_DYNAMIC_H
#define _PLUGINS_ELF_PYTHON_DYNAMIC_H


#include <Python.h>



/* Retrouve un élément dans la section dynamique par son indice. */
PyObject *py_elf_format_find_dynamic_item_by_index(PyObject *, PyObject *);

#define ELF_FORMAT_FIND_DYNAMIC_ITEM_BY_INDEX_METHOD PYTHON_METHOD_DEF      \
(                                                                           \
    find_dynamic_item_by_index, "$self, index, /",                          \
    METH_VARARGS, py_elf_format,                                            \
    "Find an item from the dynamic item using a given index."               \
    "\n"                                                                    \
    "The result is an instance of type pychrysalide.StructObject"           \
    " on success, None otherwise."                                          \
    "\n"                                                                    \
    "The provided information about a found dynamic item is composed of"    \
    " the following properties :\n"                                         \
    "* d_tag;\n"                                                            \
    "* d_un.d_val;\n"                                                       \
    "* d_un.d_ptr."                                                         \
)

/* Retrouve un élément dans la section dynamique par son type. */
PyObject *py_elf_format_find_dynamic_item_by_type(PyObject *, PyObject *);

#define ELF_FORMAT_FIND_DYNAMIC_ITEM_BY_TYPE_METHOD PYTHON_METHOD_DEF       \
(                                                                           \
    find_dynamic_item_by_type, "$self, type, /",                            \
    METH_VARARGS, py_elf_format,                                            \
    "Find an item from the dynamic item using a given type."                \
    "\n"                                                                    \
    "The result is an instance of type pychrysalide.StructObject"           \
    " on success, None otherwise."                                          \
    "\n"                                                                    \
    "The provided information about a found dynamic item is composed of"    \
    " the following properties :\n"                                         \
    "* d_tag;\n"                                                            \
    "* d_un.d_val;\n"                                                       \
    "* d_un.d_ptr."                                                         \
)

/* Fournit la liste des objets partagés requis. */
PyObject *py_elf_format_get_needed(PyObject *, void *);

#define ELF_FORMAT_NEEDED_ATTRIB PYTHON_GET_DEF_FULL            \
(                                                               \
    needed, py_elf_format,                                      \
    "Provide the list of requiered shared objects."             \
    "\n"                                                        \
    "The result is a tuple of strings or an empty tuple if"     \
    " no external library is required by the binary."           \
)



#endif  /* _PLUGINS_ELF_PYTHON_DYNAMIC_H */
