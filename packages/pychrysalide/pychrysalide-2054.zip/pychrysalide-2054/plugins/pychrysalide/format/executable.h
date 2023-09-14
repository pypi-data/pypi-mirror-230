
/* Chrysalide - Outil d'analyse de fichiers binaires
 * executable.h - prototypes pour l'équivalent Python du fichier "format/executable.h"
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


#ifndef _PLUGINS_PYCHRYSALIDE_FORMAT_EXECUTABLE_H
#define _PLUGINS_PYCHRYSALIDE_FORMAT_EXECUTABLE_H


#include <Python.h>
#include <stdbool.h>


#include <format/executable.h>



/* ------------------------ DECLARATION DE FORMAT EXECUTABLE ------------------------ */


/* Fournit un accès à une définition de type à diffuser. */
PyTypeObject *get_python_executable_format_type(void);

/* Prend en charge l'objet 'pychrysalide.format.ExeFormat'. */
bool ensure_python_executable_format_is_registered(void);

/* Tente de convertir en format exécutable. */
int convert_to_executable_format(PyObject *, void *);



/* ---------------------------- TRADUCTION D'EMPLACEMENT ---------------------------- */


/* Informations utiles à une traduction */
typedef struct _exe_cv_info_t
{
    GExeFormat *format;                     /* Eventuel format indiqué     */
    vmpa2t *vmpa;                           /* Emplacement à définir       */

    vmpa2t tmp;                             /* Eventuel stockage temporaire*/

} exe_cv_info_t;


/* Réalise une conversion d'un objet Python en localisation. */
int convert_to_vmpa_using_executable(PyObject *, exe_cv_info_t *);



#endif  /* _PLUGINS_PYCHRYSALIDE_FORMAT_EXECUTABLE_H */
