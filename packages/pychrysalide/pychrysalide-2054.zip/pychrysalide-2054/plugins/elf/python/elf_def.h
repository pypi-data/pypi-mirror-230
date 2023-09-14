
/* Chrysalide - Outil d'analyse de fichiers binaires
 * elf_def.h - prototypes pour l'équivalent Python du fichier "plugins/elf/elf_def.h"
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


#ifndef _PLUGINS_ELF_PYTHON_ELF_DEF_H
#define _PLUGINS_ELF_PYTHON_ELF_DEF_H


#include <Python.h>



/* Indique la taille d'un entête ELF. */
PyObject *py_elf_format_get_sizeof_hdr(PyObject *, void *);

/* Indique la taille d'un entête de programme ELF. */
PyObject *py_elf_format_get_sizeof_phdr(PyObject *, void *);

/* Indique la taille d'un entête de section ELF. */
PyObject *py_elf_format_get_sizeof_shdr(PyObject *, void *);

/* Indique la taille d'une entité dynamique de format ELF. */
PyObject *py_elf_format_get_sizeof_dyn(PyObject *, void *);

/* Indique la taille d'une information sur un symbole ELF. */
PyObject *py_elf_format_get_sizeof_sym(PyObject *, void *);

/* Indique la taille d'une information de relocalisation ELF. */
PyObject *py_elf_format_get_sizeof_rel(PyObject *, void *);



#endif  /* _PLUGINS_ELF_PYTHON_ELF_DEF_H */
