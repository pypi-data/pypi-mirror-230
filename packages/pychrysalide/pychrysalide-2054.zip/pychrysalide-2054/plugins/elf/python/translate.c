
/* Chrysalide - Outil d'analyse de fichiers binaires
 * translate.c - conversion de structures ELF en objets Python
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


#include "translate.h"


#include <assert.h>


#include <plugins/pychrysalide/struct.h>


#include "../elf-int.h"
#include "../section.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : format = format Elf chargé sur lequel s'appuyer.             *
*                header = en-tête Elf à décrire en Python.                    *
*                                                                             *
*  Description : Traduit un en-tête Elf en Python.                            *
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'erreur.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *translate_elf_header_to_python(GElfFormat *format, const elf_header *header)
{
    PyObject *result;                       /* Construction à retourner    */
    PyTypeObject *base;                     /* Modèle d'objet à créer      */
    PyObject *attrib;                       /* Attribut à constituer       */
    int ret;                                /* Bilan d'une mise en place   */

    base = get_python_py_struct_type();

    result = PyObject_CallFunction((PyObject *)base, NULL);
    assert(result != NULL);

    /* Signature et propriétés générales */

    attrib = PyByteArray_FromStringAndSize((char *)ELF_HDR(format, *header, e_ident), EI_NIDENT);

    ret = PyDict_SetItemString(result, "e_ident", attrib);
    if (ret != 0) goto tehtp_failed;

    /* Champs réguliers */

#define TRANSLATE_HEADER_FIELD(_f)                                                  \
    do                                                                              \
    {                                                                               \
        attrib = PyLong_FromUnsignedLongLong(ELF_HDR(format, *header, e_ ## _f));   \
        ret = PyDict_SetItemString(result, "e_" #_f, attrib);                       \
        if (ret != 0) goto tehtp_failed;                                            \
    }                                                                               \
    while (0);

    TRANSLATE_HEADER_FIELD(type);
    TRANSLATE_HEADER_FIELD(machine);
    TRANSLATE_HEADER_FIELD(version);
    TRANSLATE_HEADER_FIELD(entry);
    TRANSLATE_HEADER_FIELD(phoff);
    TRANSLATE_HEADER_FIELD(shoff);
    TRANSLATE_HEADER_FIELD(flags);
    TRANSLATE_HEADER_FIELD(ehsize);
    TRANSLATE_HEADER_FIELD(phentsize);
    TRANSLATE_HEADER_FIELD(phnum);
    TRANSLATE_HEADER_FIELD(shentsize);
    TRANSLATE_HEADER_FIELD(shnum);
    TRANSLATE_HEADER_FIELD(shstrndx);

    return result;

 tehtp_failed:

    Py_DECREF(result);

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format  = format Elf chargé sur lequel s'appuyer.            *
*                program = segment Elf à décrire en Python.                   *
*                                                                             *
*  Description : Traduit un segment Elf en Python.                            *
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'erreur.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *translate_elf_program_to_python(GElfFormat *format, const elf_phdr *program)
{
    PyObject *result;                       /* Construction à retourner    */
    PyTypeObject *base;                     /* Modèle d'objet à créer      */
    PyObject *attrib;                       /* Attribut à constituer       */
    int ret;                                /* Bilan d'une mise en place   */

    base = get_python_py_struct_type();

    result = PyObject_CallFunction((PyObject *)base, NULL);
    assert(result != NULL);

#define TRANSLATE_PROGRAM_FIELD(_f)                                                     \
    do                                                                                  \
    {                                                                                   \
        attrib = PyLong_FromUnsignedLongLong(ELF_PHDR(format, *program, p_ ## _f));     \
        ret = PyDict_SetItemString(result, "p_" #_f, attrib);                           \
        if (ret != 0) goto teptp_failed;                                                \
    }                                                                                   \
    while (0);

    TRANSLATE_PROGRAM_FIELD(type);
    TRANSLATE_PROGRAM_FIELD(offset);
    TRANSLATE_PROGRAM_FIELD(vaddr);
    TRANSLATE_PROGRAM_FIELD(paddr);
    TRANSLATE_PROGRAM_FIELD(filesz);
    TRANSLATE_PROGRAM_FIELD(memsz);
    TRANSLATE_PROGRAM_FIELD(flags);
    TRANSLATE_PROGRAM_FIELD(align);

    return result;

 teptp_failed:

    Py_DECREF(result);

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format  = format Elf chargé sur lequel s'appuyer.            *
*                section = section Elf à décrire en Python.                   *
*                                                                             *
*  Description : Traduit une section Elf en Python.                           *
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'erreur.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *translate_elf_section_to_python(GElfFormat *format, const elf_shdr *section)
{
    PyObject *result;                       /* Construction à retourner    */
    PyTypeObject *base;                     /* Modèle d'objet à créer      */
    PyObject *attrib;                       /* Attribut à constituer       */
    int ret;                                /* Bilan d'une mise en place   */
    elf_shdr strings;                       /* Section des descriptions    */
    const char *name;                       /* Nom d'une section analysée  */

    base = get_python_py_struct_type();

    result = PyObject_CallFunction((PyObject *)base, NULL);
    assert(result != NULL);

    /* Champs réguliers */

#define TRANSLATE_SECTION_FIELD(_f)                                                     \
    do                                                                                  \
    {                                                                                   \
        attrib = PyLong_FromUnsignedLongLong(ELF_SHDR(format, *section, sh_ ## _f));    \
        ret = PyDict_SetItemString(result, "sh_" #_f, attrib);                          \
        if (ret != 0) goto testp_failed;                                                \
    }                                                                                   \
    while (0);

    TRANSLATE_SECTION_FIELD(name);
    TRANSLATE_SECTION_FIELD(type);
    TRANSLATE_SECTION_FIELD(flags);
    TRANSLATE_SECTION_FIELD(addr);
    TRANSLATE_SECTION_FIELD(offset);
    TRANSLATE_SECTION_FIELD(size);
    TRANSLATE_SECTION_FIELD(link);
    TRANSLATE_SECTION_FIELD(info);
    TRANSLATE_SECTION_FIELD(addralign);
    TRANSLATE_SECTION_FIELD(entsize);

    /* Liberté supplémentaire */

    if (find_elf_section_by_index(format, ELF_HDR(format, format->header, e_shstrndx), &strings))
    {
        name = extract_name_from_elf_string_section(format, &strings,
                                                    ELF_SHDR(format, *section, sh_name));

        if (name == NULL)
        {
            attrib = Py_None;
            Py_INCREF(attrib);
        }

        else
            attrib = PyUnicode_FromString(name);

        ret = PyDict_SetItemString(result, "name", attrib);
        if (ret != 0) goto testp_failed;

    }

    return result;

 testp_failed:

    Py_DECREF(result);

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format Elf chargé sur lequel s'appuyer.             *
*                dyn    = information du dynamisme Elf à décrire en Python.   *
*                                                                             *
*  Description : Traduit une information du dynamisme Elf en Python.          *
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'erreur.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *translate_elf_dyn_to_python(GElfFormat *format, const elf_dyn *dyn)
{
    PyObject *result;                       /* Construction à retourner    */
    PyTypeObject *base;                     /* Modèle d'objet à créer      */
    PyObject *attrib;                       /* Attribut à constituer       */
    int ret;                                /* Bilan d'une mise en place   */

    base = get_python_py_struct_type();

    result = PyObject_CallFunction((PyObject *)base, NULL);
    assert(result != NULL);

#define TRANSLATE_DYN_FIELD(_f)                                                 \
    do                                                                          \
    {                                                                           \
        attrib = PyLong_FromUnsignedLongLong(ELF_DYN(format, *dyn, d_ ## _f));  \
        ret = PyDict_SetItemString(result, "d_" #_f, attrib);                   \
        if (ret != 0) goto tedtp_failed;                                        \
    }                                                                           \
    while (0);

    TRANSLATE_DYN_FIELD(tag);
    TRANSLATE_DYN_FIELD(un.d_val);
    TRANSLATE_DYN_FIELD(un.d_ptr);

    return result;

 tedtp_failed:

    Py_DECREF(result);

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format Elf chargé sur lequel s'appuyer.             *
*                symbol = symbole Elf à décrire en Python.                    *
*                                                                             *
*  Description : Traduit un symbole Elf en Python.                            *
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'erreur.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *translate_elf_symbol_to_python(GElfFormat *format, const elf_sym *symbol)
{
    PyObject *result;                       /* Construction à retourner    */
    PyTypeObject *base;                     /* Modèle d'objet à créer      */
    PyObject *attrib;                       /* Attribut à constituer       */
    int ret;                                /* Bilan d'une mise en place   */
    elf_shdr strings;                       /* Section des descriptions    */
    const char *name;                       /* Nom d'une section analysée  */

    base = get_python_py_struct_type();

    result = PyObject_CallFunction((PyObject *)base, NULL);
    assert(result != NULL);

    /* Champs réguliers */

#define TRANSLATE_SYMBOL_FIELD(_f)                                                  \
    do                                                                              \
    {                                                                               \
        attrib = PyLong_FromUnsignedLongLong(ELF_SYM(format, *symbol, st_ ## _f));  \
        ret = PyDict_SetItemString(result, "st_" #_f, attrib);                      \
        if (ret != 0) goto testp_failed;                                            \
    }                                                                               \
    while (0);

    TRANSLATE_SYMBOL_FIELD(name);
    TRANSLATE_SYMBOL_FIELD(value);
    TRANSLATE_SYMBOL_FIELD(size);
    TRANSLATE_SYMBOL_FIELD(info);
    TRANSLATE_SYMBOL_FIELD(other);
    TRANSLATE_SYMBOL_FIELD(shndx);

    /* Liberté supplémentaire */

    if (find_elf_section_by_index(format, ELF_HDR(format, format->header, e_shstrndx), &strings))
    {
        name = extract_name_from_elf_string_section(format, &strings,
                                                    ELF_SYM(format, *symbol, st_name));

        if (name == NULL)
        {
            attrib = Py_None;
            Py_INCREF(attrib);
        }

        else
            attrib = PyUnicode_FromString(name);

        ret = PyDict_SetItemString(result, "name", attrib);
        if (ret != 0) goto testp_failed;

    }

    return result;

 testp_failed:

    Py_DECREF(result);

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format Elf chargé sur lequel s'appuyer.             *
*                rel    = relocalisation Elf à décrire en Python.             *
*                                                                             *
*  Description : Traduit une information de relocalisation Elf en Python.     *
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'erreur.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *translate_elf_rel_to_python(GElfFormat *format, const elf_rel *rel)
{
    PyObject *result;                       /* Construction à retourner    */
    PyTypeObject *base;                     /* Modèle d'objet à créer      */
    PyObject *attrib;                       /* Attribut à constituer       */
    int ret;                                /* Bilan d'une mise en place   */

    base = get_python_py_struct_type();

    result = PyObject_CallFunction((PyObject *)base, NULL);
    assert(result != NULL);

#define TRANSLATE_REL_FIELD(_f)                                                 \
    do                                                                          \
    {                                                                           \
        attrib = PyLong_FromUnsignedLongLong(ELF_REL(format, *rel, r_ ## _f));  \
        ret = PyDict_SetItemString(result, "r_" #_f, attrib);                   \
        if (ret != 0) goto tertp_failed;                                        \
    }                                                                           \
    while (0);

    TRANSLATE_REL_FIELD(offset);
    TRANSLATE_REL_FIELD(info);

    return result;

 tertp_failed:

    Py_DECREF(result);

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format Elf chargé sur lequel s'appuyer.             *
*                note   = note Elf à décrire en Python.                       *
*                                                                             *
*  Description : Traduit une note Elf en Python.                              *
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'erreur.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *translate_elf_note_to_python(GElfFormat *format, const elf_note *note)
{
    PyObject *result;                       /* Construction à retourner    */
    PyTypeObject *base;                     /* Modèle d'objet à créer      */
    PyObject *attrib;                       /* Attribut à constituer       */
    int ret;                                /* Bilan d'une mise en place   */

    base = get_python_py_struct_type();

    result = PyObject_CallFunction((PyObject *)base, NULL);
    assert(result != NULL);

    attrib = PyLong_FromUnsignedLongLong(note->type);

    ret = PyDict_SetItemString(result, "type", attrib);
    if (ret != 0) goto tentp_failed;

    if (note->name == NULL)
    {
        attrib = Py_None;
        Py_INCREF(attrib);
    }

    else
        attrib = PyUnicode_FromString(note->name);

    ret = PyDict_SetItemString(result, "name", attrib);
    if (ret != 0) goto tentp_failed;

    if (note->desc == NULL)
    {
        attrib = Py_None;
        Py_INCREF(attrib);
    }

    else
        attrib = PyUnicode_FromString(note->desc);

    ret = PyDict_SetItemString(result, "desc", attrib);
    if (ret != 0) goto tentp_failed;

    return result;

 tentp_failed:

    Py_DECREF(result);

    return NULL;

}
