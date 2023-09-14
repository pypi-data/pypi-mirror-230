
/* Chrysalide - Outil d'analyse de fichiers binaires
 * section.c - équivalent Python du fichier "plugins/elf/section.c"
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


#include "section.h"


#include <malloc.h>
#include <pygobject.h>


#include "translate.h"
#include "../section.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : self = format Elf à manipuler.                               *
*                args = indice de la section visée.                           *
*                                                                             *
*  Description : Retrouve une section par son indice.                         *
*                                                                             *
*  Retour      : Elément trouvé ou rien (None).                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *py_elf_format_find_section_by_index(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Trouvaille à retourner      */
    GElfFormat *format;                     /* Version GLib du format      */
    unsigned short int index;               /* Indice de section visée     */
    int ret;                                /* Bilan de lecture des args.  */
    elf_shdr section;                       /* Informations remontées      */
    bool found;                             /* Recherches concluantes ?    */

    format = G_ELF_FORMAT(pygobject_get(self));

    ret = PyArg_ParseTuple(args, "H", &index);
    if (!ret) return NULL;

    found = find_elf_section_by_index(format, index, &section);

    if (found)
        result = translate_elf_section_to_python(format, &section);

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
*                args = désignation de la section visée.                      *
*                                                                             *
*  Description : Retrouve une section par son nom.                            *
*                                                                             *
*  Retour      : Elément trouvé ou rien (None).                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *py_elf_format_find_section_by_name(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Trouvaille à retourner      */
    GElfFormat *format;                     /* Version GLib du format      */
    PyObject *name;                         /* Etiquette à retrouver       */
    int ret;                                /* Bilan de lecture des args.  */
    elf_shdr section;                       /* Informations remontées      */
    bool found;                             /* Recherches concluantes ?    */

    format = G_ELF_FORMAT(pygobject_get(self));

    ret = PyArg_ParseTuple(args, "O!", &PyUnicode_Type, &name);
    if (!ret) return NULL;

    found = find_elf_section_by_name(format, PyUnicode_DATA(name), &section);

    if (found)
        result = translate_elf_section_to_python(format, &section);

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
*                args = adresse en mémoire de la section visée.               *
*                                                                             *
*  Description : Retrouve une section par son adresse en mémoire.             *
*                                                                             *
*  Retour      : Elément trouvé ou rien (None).                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *py_elf_format_find_section_by_virtual_address(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Trouvaille à retourner      */
    GElfFormat *format;                     /* Version GLib du format      */
    unsigned long long addr;                /* Adresse en mémoire virtuelle*/
    int ret;                                /* Bilan de lecture des args.  */
    elf_shdr section;                       /* Informations remontées      */
    bool found;                             /* Recherches concluantes ?    */

    format = G_ELF_FORMAT(pygobject_get(self));

    ret = PyArg_ParseTuple(args, "K", &addr);
    if (!ret) return NULL;

    found = find_elf_section_by_virtual_address(format, addr, &section);

    if (found)
        result = translate_elf_section_to_python(format, &section);

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
*                args = type des sections visées.                             *
*                                                                             *
*  Description : Retrouve des sections par leur type.                         *
*                                                                             *
*  Retour      : Liste d'éléments trouvés, éventuellement vide.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *py_elf_format_find_sections_by_type(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Trouvaille à retourner      */
    GElfFormat *format;                     /* Version GLib du format      */
    unsigned int type;                      /* Type de section visée       */
    int ret;                                /* Bilan de lecture des args.  */
    elf_shdr *sections;                     /* Liste des sections trouvées */
    size_t count;                           /* Taille de cette liste       */
    size_t i;                               /* Boucle de parcours          */
    PyObject *section;                      /* Traduction d'une section    */

    format = G_ELF_FORMAT(pygobject_get(self));

    ret = PyArg_ParseTuple(args, "I", &type);
    if (!ret) return NULL;

    find_elf_sections_by_type(format, type, &sections, &count);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
        section = translate_elf_section_to_python(format, &sections[i]);
        PyTuple_SetItem(result, i, section);
    }

    if (sections != NULL)
        free(sections);

    return result;

}
