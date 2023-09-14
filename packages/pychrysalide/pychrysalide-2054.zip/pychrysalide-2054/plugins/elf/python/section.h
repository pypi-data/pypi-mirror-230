
/* Chrysalide - Outil d'analyse de fichiers binaires
 * section.h - prototypes pour l'équivalent Python du fichier "plugins/elf/section.h"
 *
 * Copyright (C) 2017 Cyrille Bagard
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


#ifndef _PLUGINS_ELF_PYTHON_SECTION_H
#define _PLUGINS_ELF_PYTHON_SECTION_H


#include <Python.h>



/* Retrouve une section par son indice. */
PyObject *py_elf_format_find_section_by_index(PyObject *, PyObject *);

/* Retrouve une section par son nom. */
PyObject *py_elf_format_find_section_by_name(PyObject *, PyObject *);

/* Retrouve une section par son adresse en mémoire. */
PyObject *py_elf_format_find_section_by_virtual_address(PyObject *, PyObject *);

/* Retrouve des sections par leur type. */
PyObject *py_elf_format_find_sections_by_type(PyObject *, PyObject *);



#endif  /* _PLUGINS_ELF_PYTHON_SECTION_H */
