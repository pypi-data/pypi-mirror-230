
/* Chrysalide - Outil d'analyse de fichiers binaires
 * translate.h - prototypes pour la conversion de structures PE en objets Python
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


#ifndef _PLUGINS_PE_PYTHON_TRANSLATE_H
#define _PLUGINS_PE_PYTHON_TRANSLATE_H


#include <Python.h>


#include "../format.h"
#include "../rich.h"



/* Traduit un en-tête MS-DOS en Python. */
PyObject *translate_pe_dos_header_to_python(GPeFormat *, const image_dos_header *);

/* Traduit un répertoire PE en Python. */
PyObject *translate_pe_image_data_directory_to_python(GPeFormat *, const image_data_directory *);

/* Traduit une série d'informations enrichies en Python. */
PyObject *translate_pe_comp_id_to_python(GPeFormat *, const comp_id_t *);



#endif  /* _PLUGINS_PE_PYTHON_TRANSLATE_H */
