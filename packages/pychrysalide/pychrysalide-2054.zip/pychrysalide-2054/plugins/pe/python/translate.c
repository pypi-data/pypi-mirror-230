
/* Chrysalide - Outil d'analyse de fichiers binaires
 * translate.c - conversion de structures PE en objets Python
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


#include "translate.h"


#include <assert.h>


#include <plugins/pychrysalide/struct.h>



/******************************************************************************
*                                                                             *
*  Paramètres  : format = format PE chargé sur lequel s'appuyer.              *
*                header = en-tête MS-DOS à décrire en Python.                 *
*                                                                             *
*  Description : Traduit un en-tête MS-DOS en Python.                         *
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'erreur.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *translate_pe_dos_header_to_python(GPeFormat *format, const image_dos_header *header)
{
    PyObject *result;                       /* Construction à retourner    */
    PyTypeObject *base;                     /* Modèle d'objet à créer      */
    PyObject *attrib;                       /* Attribut à constituer       */
    int ret;                                /* Bilan d'une mise en place   */
    size_t i;                               /* Boucle de parcours          */
    PyObject *item;                         /* Elément de tableau          */

    base = get_python_py_struct_type();

    result = PyObject_CallFunction((PyObject *)base, NULL);
    assert(result != NULL);

#define TRANSLATE_DOS_HEADER_FIELD(_f)                                  \
    do                                                                  \
    {                                                                   \
        attrib = PyLong_FromUnsignedLongLong(header->e_ ## _f);         \
        ret = PyDict_SetItemString(result, "e_" #_f, attrib);           \
        if (ret != 0) goto failed;                                      \
    }                                                                   \
    while (0);

#define TRANSLATE_DOS_HEADER_FIELD_ARRAY(_f, _n)                        \
    do                                                                  \
    {                                                                   \
        attrib = PyTuple_New(_n);                                       \
        ret = 0;                                                        \
        for (i = 0; i < _n; i++)                                        \
        {                                                               \
            item = PyLong_FromUnsignedLongLong(header->e_ ## _f [i]);   \
            ret = PyTuple_SetItem(attrib, i, item);                     \
            if (ret != 0) break;                                        \
        }                                                               \
        if (ret != 0) goto failed;                                      \
        ret = PyDict_SetItemString(result, "e_" #_f, attrib);           \
        if (ret != 0) goto failed;                                      \
    }                                                                   \
    while (0);

    TRANSLATE_DOS_HEADER_FIELD(magic);
    TRANSLATE_DOS_HEADER_FIELD(cblp);
    TRANSLATE_DOS_HEADER_FIELD(cp);
    TRANSLATE_DOS_HEADER_FIELD(crlc);
    TRANSLATE_DOS_HEADER_FIELD(cparhdr);
    TRANSLATE_DOS_HEADER_FIELD(minalloc);
    TRANSLATE_DOS_HEADER_FIELD(maxalloc);
    TRANSLATE_DOS_HEADER_FIELD(ss);
    TRANSLATE_DOS_HEADER_FIELD(sp);
    TRANSLATE_DOS_HEADER_FIELD(csum);
    TRANSLATE_DOS_HEADER_FIELD(ip);
    TRANSLATE_DOS_HEADER_FIELD(cs);
    TRANSLATE_DOS_HEADER_FIELD(lfarlc);
    TRANSLATE_DOS_HEADER_FIELD(ovno);
    TRANSLATE_DOS_HEADER_FIELD_ARRAY(res, 4);
    TRANSLATE_DOS_HEADER_FIELD(oemid);
    TRANSLATE_DOS_HEADER_FIELD(oeminfo);
    TRANSLATE_DOS_HEADER_FIELD_ARRAY(res2, 10);
    TRANSLATE_DOS_HEADER_FIELD(lfanew);

    return result;

 failed:

    Py_DECREF(result);

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format PE chargé sur lequel s'appuyer.              *
*                dir    = répertoire PE à décrire en Python.                  *
*                                                                             *
*  Description : Traduit un répertoire PE en Python.                          *
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'erreur.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *translate_pe_image_data_directory_to_python(GPeFormat *format, const image_data_directory *dir)
{
    PyObject *result;                       /* Construction à retourner    */
    PyTypeObject *base;                     /* Modèle d'objet à créer      */
    PyObject *attrib;                       /* Attribut à constituer       */
    int ret;                                /* Bilan d'une mise en place   */

    base = get_python_py_struct_type();

    result = PyObject_CallFunction((PyObject *)base, NULL);
    assert(result != NULL);

#define TRANSLATE_IMAGE_DATA_DIRECTORY_FIELD(_f)            \
    do                                                      \
    {                                                       \
        attrib = PyLong_FromUnsignedLongLong(dir->_f);      \
        ret = PyDict_SetItemString(result, #_f, attrib);    \
        if (ret != 0) goto failed;                          \
    }                                                       \
    while (0);

    TRANSLATE_IMAGE_DATA_DIRECTORY_FIELD(virtual_address);
    TRANSLATE_IMAGE_DATA_DIRECTORY_FIELD(size);

    return result;

 failed:

    Py_DECREF(result);

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format PE chargé sur lequel s'appuyer.              *
*                id     = ensemble d'informations à décrire en Python.        *
*                                                                             *
*  Description : Traduit une série d'informations enrichies en Python.        *
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'erreur.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *translate_pe_comp_id_to_python(GPeFormat *format, const comp_id_t *id)
{
    PyObject *result;                       /* Construction à retourner    */
    PyTypeObject *base;                     /* Modèle d'objet à créer      */
    PyObject *attrib;                       /* Attribut à constituer       */
    int ret;                                /* Bilan d'une mise en place   */

    base = get_python_py_struct_type();

    result = PyObject_CallFunction((PyObject *)base, NULL);
    assert(result != NULL);

#define TRANSLATE_COMP_ID_VALUE(_f)                         \
    do                                                      \
    {                                                       \
        attrib = PyLong_FromUnsignedLongLong(id->_f);       \
        ret = PyDict_SetItemString(result, #_f, attrib);    \
        if (ret != 0) goto failed;                          \
    }                                                       \
    while (0);

    TRANSLATE_COMP_ID_VALUE(minor_cv);
    TRANSLATE_COMP_ID_VALUE(prod_id);
    TRANSLATE_COMP_ID_VALUE(count);

    return result;

 failed:

    Py_DECREF(result);

    return NULL;

}
