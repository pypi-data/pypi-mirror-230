
/* Chrysalide - Outil d'analyse de fichiers binaires
 * program.c - équivalent Python du fichier "plugins/elf/program.c"
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


#include "program.h"


#include <pygobject.h>


#include "translate.h"
#include "../program.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : self = format Elf à manipuler.                               *
*                args = indice du segment visé.                               *
*                                                                             *
*  Description : Retrouve un segment par son indice.                          *
*                                                                             *
*  Retour      : Elément trouvé ou rien (None).                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *py_elf_format_find_program_by_index(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Trouvaille à retourner      */
    GElfFormat *format;                     /* Version GLib du format      */
    unsigned short int index;               /* Indice du segment visé      */
    int ret;                                /* Bilan de lecture des args.  */
    elf_phdr program;                       /* Informations remontées      */
    bool found;                             /* Recherches concluantes ?    */

    format = G_ELF_FORMAT(pygobject_get(self));

    ret = PyArg_ParseTuple(args, "H", &index);
    if (!ret) return NULL;

    found = find_elf_program_by_index(format, index, &program);

    if (found)
        result = translate_elf_program_to_python(format, &program);

    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = format Elf à manipuler.                               *
*                args = type du segment visé.                                 *
*                                                                             *
*  Description : Retrouve un segment par son type.                            *
*                                                                             *
*  Retour      : Elément trouvé ou rien (None).                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *py_elf_format_find_program_by_type(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Trouvaille à retourner      */
    GElfFormat *format;                     /* Version GLib du format      */
    unsigned int type;                      /* Type de segment visé        */
    int ret;                                /* Bilan de lecture des args.  */
    elf_phdr program;                       /* Informations remontées      */
    bool found;                             /* Recherches concluantes ?    */

    format = G_ELF_FORMAT(pygobject_get(self));

    ret = PyArg_ParseTuple(args, "I", &type);
    if (!ret) return NULL;

    found = find_elf_program_by_type(format, type, &program);

    if (found)
        result = translate_elf_program_to_python(format, &program);

    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

    return result;

}
