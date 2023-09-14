
/* Chrysalide - Outil d'analyse de fichiers binaires
 * translate.h - prototypes pour la conversion de structures ELF en objets Python
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


#ifndef _PLUGINS_ELF_PYTHON_TRANSLATE_H
#define _PLUGINS_ELF_PYTHON_TRANSLATE_H


#include <Python.h>


#include "../format.h"



/* Traduit un en-tête Elf en Python. */
PyObject *translate_elf_header_to_python(GElfFormat *, const elf_header *);

/* Traduit un segment Elf en Python. */
PyObject *translate_elf_program_to_python(GElfFormat *, const elf_phdr *);

/* Traduit une section Elf en Python. */
PyObject *translate_elf_section_to_python(GElfFormat *, const elf_shdr *);

/* Traduit une information du dynamisme Elf en Python. */
PyObject *translate_elf_dyn_to_python(GElfFormat *, const elf_dyn *);

/* Traduit un symbole Elf en Python. */
PyObject *translate_elf_symbol_to_python(GElfFormat *, const elf_sym *);

/* Traduit une information de relocalisation Elf en Python. */
PyObject *translate_elf_rel_to_python(GElfFormat *, const elf_rel *);

/* Traduit une note Elf en Python. */
PyObject *translate_elf_note_to_python(GElfFormat *, const elf_note *);



#endif  /* _PLUGINS_ELF_PYTHON_TRANSLATE_H */
