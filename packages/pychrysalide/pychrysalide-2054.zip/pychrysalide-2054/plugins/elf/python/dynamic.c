
/* Chrysalide - Outil d'analyse de fichiers binaires
 * dynamic.c - équivalent Python du fichier "plugins/elf/dynamic.c"
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


#include "dynamic.h"


#include <malloc.h>
#include <pygobject.h>


#include "translate.h"
#include "../dynamic.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : self = format Elf à manipuler.                               *
*                args = indice de l'élément recherché.                        *
*                                                                             *
*  Description : Retrouve un élément dans la section dynamique par son indice.*
*                                                                             *
*  Retour      : Elément trouvé ou rien (None).                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *py_elf_format_find_dynamic_item_by_index(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Trouvaille à retourner      */
    GElfFormat *format;                     /* Version GLib du format      */
    unsigned long index;                    /* Indice de l'élément visé    */
    int ret;                                /* Bilan de lecture des args.  */
    elf_dyn item;                           /* Informations remontées      */
    bool found;                             /* Recherches concluantes ?    */

    format = G_ELF_FORMAT(pygobject_get(self));

    ret = PyArg_ParseTuple(args, "k", &index);
    if (!ret) return NULL;

    found = find_elf_dynamic_item_by_index(format, index, &item);

    if (found)
        result = translate_elf_dyn_to_python(format, &item);

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
*                args = sorte d'élément recherché.                            *
*                                                                             *
*  Description : Retrouve un élément dans la section dynamique par son type.  *
*                                                                             *
*  Retour      : Elément trouvé ou rien (None).                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *py_elf_format_find_dynamic_item_by_type(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Trouvaille à retourner      */
    GElfFormat *format;                     /* Version GLib du format      */
    unsigned long type;                     /* Type de l'élément visé      */
    int ret;                                /* Bilan de lecture des args.  */
    elf_dyn item;                           /* Informations remontées      */
    bool found;                             /* Recherches concluantes ?    */

    format = G_ELF_FORMAT(pygobject_get(self));

    ret = PyArg_ParseTuple(args, "k", &type);
    if (!ret) return NULL;

    found = find_elf_dynamic_item_by_type(format, type, &item);

    if (found)
        result = translate_elf_dyn_to_python(format, &item);

    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = classe représentant un format ELF.                 *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Fournit la liste des objets partagés requis.                 *
*                                                                             *
*  Retour      : Liste de noms d'objets ou None en cas d'échec.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *py_elf_format_get_needed(PyObject *self, void *closure)
{
    PyObject *result;                       /* Liste éventuelle à renvoyer */
    GElfFormat *format;                     /* Version native              */
    size_t count;                           /* Taille de la liste obtenue  */
    const char **needed;                    /* Objets nécessaires          */
    size_t i;                               /* Boucle de parcours          */

    format = G_ELF_FORMAT(pygobject_get(self));

    needed = list_elf_needed_objects(format, &count);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
        PyTuple_SetItem(result, i, PyUnicode_FromString(needed[i]));

    if (needed != NULL)
        free(needed);

    return result;

}
