
/* Chrysalide - Outil d'analyse de fichiers binaires
 * format.c - équivalent Python du fichier "plugins/elf/format.c"
 *
 * Copyright (C) 2017-2019 Cyrille Bagard
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


#include "format.h"


#include <pygobject.h>


#include <i18n.h>
#include <format/executable.h>
#include <analysis/content.h>
#include <plugins/pychrysalide/helpers.h>
#include <plugins/pychrysalide/analysis/content.h>
#include <plugins/pychrysalide/format/executable.h>


#include "constants.h"
#include "dynamic.h"
#include "elf_def.h"
#include "program.h"
#include "section.h"
#include "translate.h"
#include "../format.h"



/* Crée un nouvel objet Python de type 'ElfFormat'. */
static PyObject *py_elf_format_new(PyTypeObject *, PyObject *, PyObject *);

/* Fournit l'en-tête Elf correspondant au format. */
static PyObject *py_elf_format_get_header(PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de l'objet à instancier.                         *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Crée un nouvel objet Python de type 'ElfFormat'.             *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_elf_format_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinContent *content;                   /* Instance GLib du contenu    */
    int ret;                                /* Bilan de lecture des args.  */
    GExeFormat *format;                     /* Création GLib à transmettre */

    ret = PyArg_ParseTuple(args, "O&", convert_to_binary_content, &content);
    if (!ret) return NULL;

    format = g_elf_format_new(content);

    if (format == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }

    else
    {
        result = pygobject_new(G_OBJECT(format));
        g_object_unref(format);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = argument non utilisé ici.                             *
*                                                                             *
*  Description : Fournit l'en-tête Elf correspondant au format.               *
*                                                                             *
*  Retour      : Structure Python créée pour l'occasion.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_elf_format_get_header(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Trouvaille à retourner      */
    GElfFormat *format;                     /* Version GLib du format      */

    format = G_ELF_FORMAT(pygobject_get(self));

    result = translate_elf_header_to_python(format, g_elf_format_get_header(format));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Fournit un accès à une définition de type à diffuser.        *
*                                                                             *
*  Retour      : Définition d'objet pour Python.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyTypeObject *get_python_elf_format_type(void)
{
    static PyMethodDef py_elf_format_methods[] = {
        {
            "get_header", py_elf_format_get_header,
            METH_NOARGS,
            "get_header($self, /)\n--\n\nGet the Elf header."
        },
        {
            "find_program_by_index", py_elf_format_find_program_by_index,
            METH_VARARGS,
            "find_program_by_index($self, index, /)\n--\n\nFind a segment using a given index."
        },
        {
            "find_program_by_type", py_elf_format_find_program_by_type,
            METH_VARARGS,
            "find_program_by_type($self, type, /)\n--\n\nFind a segment using a given type."
        },
        {
            "find_section_by_index", py_elf_format_find_section_by_index,
            METH_VARARGS,
            "find_section_by_index($self, index, /)\n--\n\nFind a section using a given index."
        },
        {
            "find_section_by_name", py_elf_format_find_section_by_name,
            METH_VARARGS,
            "find_section_by_name($self, name, /)\n--\n\nFind a section using a given name."
        },
        {
            "find_section_by_virtual_address", py_elf_format_find_section_by_virtual_address,
            METH_VARARGS,
            "find_section_by_virtual_address($self, addr, /)\n--\n\nFind a section using a given virtual address."
        },
        {
            "find_sections_by_type", py_elf_format_find_sections_by_type,
            METH_VARARGS,
            "find_sections_by_type($self, type, /)\n--\n\nFind sections using a given type."
        },
        ELF_FORMAT_FIND_DYNAMIC_ITEM_BY_INDEX_METHOD,
        ELF_FORMAT_FIND_DYNAMIC_ITEM_BY_TYPE_METHOD,
        { NULL }
    };

    static PyGetSetDef py_elf_format_getseters[] = {
        {
            "sizeof_hdr", py_elf_format_get_sizeof_hdr, NULL,
            "Provide the size of Elf_Ehdr structures for the loaded format.", NULL
        },
        {
            "sizeof_phdr", py_elf_format_get_sizeof_phdr, NULL,
            "Provide the size of Elf_Phdr structures for the loaded format.", NULL
        },
        {
            "sizeof_shdr", py_elf_format_get_sizeof_shdr, NULL,
            "Provide the size of Elf_Shdr structures for the loaded format.", NULL
        },
        {
            "sizeof_dyn", py_elf_format_get_sizeof_dyn, NULL,
            "Provide the size of Elf_Dyn structures for the loaded format.", NULL
        },
        {
            "sizeof_sym", py_elf_format_get_sizeof_sym, NULL,
            "Provide the size of Elf_Sym structures for the loaded format.", NULL
        },
        {
            "sizeof_rel", py_elf_format_get_sizeof_rel, NULL,
            "Provide the size of Elf_Rel structures for the loaded format.", NULL
        },
        ELF_FORMAT_NEEDED_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_elf_format_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.format.elf.ElfFormat",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = "PyChrysalide Elf format",

        .tp_methods     = py_elf_format_methods,
        .tp_getset      = py_elf_format_getseters,
        .tp_new         = py_elf_format_new

    };

    return &py_elf_format_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.format.elf.ElfFormat'. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool register_python_elf_format(PyObject *module)
{
    PyTypeObject *type;                     /* Type Python 'ElfFormat'     */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_elf_format_type();

    dict = PyModule_GetDict(module);

    if (!ensure_python_executable_format_is_registered())
        return false;

    if (!register_class_for_pygobject(dict, G_TYPE_ELF_FORMAT, type))
        return false;

    if (!define_python_elf_format_constants(type))
        return false;

    return true;

}
