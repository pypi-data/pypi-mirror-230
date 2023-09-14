
/* Chrysalide - Outil d'analyse de fichiers binaires
 * routine.h - prototypes pour l'équivalent Python du fichier "plugins/pe/routine.h"
 *
 * Copyright (C) 2019 Cyrille Bagard
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


#ifndef _PLUGINS_PE_PYTHON_ROUTINE_H
#define _PLUGINS_PE_PYTHON_ROUTINE_H


#include <Python.h>
#include <stdbool.h>



/* ------------------------ SYMBOLES D'UN FORMAT PE EXPORTES ------------------------ */


/* Fournit un accès à une définition de type à diffuser. */
PyTypeObject *get_python_pe_exported_routine_type(void);

/* Prend en charge l'objet 'pychrysalide.format.pe.PeExportedRoutine'. */
bool register_python_pe_exported_routine(PyObject *);

/* Tente de convertir en routine de fichier PE. */
int convert_to_pe_exported_routine(PyObject *, void *);



/* ------------------------ SYMBOLES D'UN FORMAT PE IMPORTES ------------------------ */


/* Fournit un accès à une définition de type à diffuser. */
PyTypeObject *get_python_pe_imported_routine_type(void);

/* Prend en charge l'objet 'pychrysalide.format.pe.PeImportedRoutine'. */
bool register_python_pe_imported_routine(PyObject *);

/* Tente de convertir en routine de fichier PE. */
int convert_to_pe_imported_routine(PyObject *, void *);



#endif  /* _PLUGINS_PE_PYTHON_ROUTINE_H */
