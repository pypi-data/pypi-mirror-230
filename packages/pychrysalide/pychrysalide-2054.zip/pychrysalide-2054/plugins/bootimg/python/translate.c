
/* Chrysalide - Outil d'analyse de fichiers binaires
 * translate.c - conversion de structures ELF en objets Python
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


#include "translate.h"


#include <assert.h>


#include <plugins/pychrysalide/struct.h>



/******************************************************************************
*                                                                             *
*  Paramètres  : header = entête BOOT.img à décrire en Python.                *
*                                                                             *
*  Description : Traduit un entête BOOT.img en Python.                        *
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'erreur.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *translate_bootimg_header_to_python(const boot_img_hdr *header)
{
    PyObject *result;                       /* Construction à retourner    */
    PyTypeObject *base;                     /* Modèle d'objet à créer      */
    PyObject *attrib;                       /* Attribut à constituer       */
    int ret;                                /* Bilan d'une mise en place   */

    base = get_python_py_struct_type();

    result = PyObject_CallFunction((PyObject *)base, NULL);
    assert(result != NULL);


#define TRANSLATE_HEADER_BYTE_VALUE(_f, _sz)                            \
    do                                                                  \
    {                                                                   \
        attrib = PyBytes_FromStringAndSize((char *)header->_f, _sz);    \
        ret = PyDict_SetItemString(result, #_f, attrib);                \
        if (ret != 0) goto failed;                                      \
    }                                                                   \
    while (0);

#define TRANSLATE_HEADER_NUMERIC_VALUE(_f)                              \
    do                                                                  \
    {                                                                   \
        attrib = PyLong_FromUnsignedLongLong(header->_f);               \
        ret = PyDict_SetItemString(result, #_f, attrib);                \
        if (ret != 0) goto failed;                                      \
    }                                                                   \
    while (0);


    TRANSLATE_HEADER_BYTE_VALUE(magic, BOOT_MAGIC_SIZE);
    TRANSLATE_HEADER_NUMERIC_VALUE(kernel_size);
    TRANSLATE_HEADER_NUMERIC_VALUE(kernel_addr);

    TRANSLATE_HEADER_NUMERIC_VALUE(ramdisk_size);
    TRANSLATE_HEADER_NUMERIC_VALUE(ramdisk_addr);

    TRANSLATE_HEADER_NUMERIC_VALUE(second_size);
    TRANSLATE_HEADER_NUMERIC_VALUE(second_addr);

    TRANSLATE_HEADER_NUMERIC_VALUE(tags_addr);
    TRANSLATE_HEADER_NUMERIC_VALUE(page_size);
    TRANSLATE_HEADER_NUMERIC_VALUE(header_version);
    TRANSLATE_HEADER_NUMERIC_VALUE(os_version);
    TRANSLATE_HEADER_BYTE_VALUE(name, BOOT_NAME_SIZE);
    TRANSLATE_HEADER_BYTE_VALUE(cmdline, BOOT_ARGS_SIZE);
    TRANSLATE_HEADER_BYTE_VALUE(id, 8 * sizeof(uint32_t));
    TRANSLATE_HEADER_BYTE_VALUE(extra_cmdline, BOOT_EXTRA_ARGS_SIZE);

    TRANSLATE_HEADER_NUMERIC_VALUE(recovery_dtbo_size);
    TRANSLATE_HEADER_NUMERIC_VALUE(recovery_dtbo_offset);
    TRANSLATE_HEADER_NUMERIC_VALUE(header_size);

    return result;

 failed:

    Py_DECREF(result);

    return NULL;

}
