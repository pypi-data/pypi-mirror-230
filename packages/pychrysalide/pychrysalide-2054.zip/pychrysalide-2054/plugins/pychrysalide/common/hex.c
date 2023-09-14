
/* Chrysalide - Outil d'analyse de fichiers binaires
 * hex.c - équivalent Python du fichier "common/hex.c"
 *
 * Copyright (C) 2021 Cyrille Bagard
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


#include "hex.h"


#include <assert.h>
#include <malloc.h>
#include <pygobject.h>


#include <common/hex.h>


#include "../access.h"
#include "../helpers.h"



/* Encode des données en chaîne hexadécimale. */
static PyObject *py_hex_encode_hex(PyObject *, PyObject *);

/* Décode un caractère hexadécimal. */
static PyObject *py_hex_decode_hex_digit(PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = arguments à utiliser pour l'opération.                *
*                                                                             *
*  Description : Encode des données en chaîne hexadécimale.                   *
*                                                                             *
*  Retour      : Chaîne hexadécimale.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_hex_encode_hex(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Valeur à retourner          */
    int lower;                              /* Taille des caractères finaux*/
    const char *data;                       /* Données à traiter           */
    Py_ssize_t len;                         /* Quantité de ces données     */
    int ret;                                /* Bilan de lecture des args.  */
    char *buffer;                           /* Tampon de travail           */

#define HEX_ENCODE_HEX_METHOD PYTHON_METHOD_DEF                         \
(                                                                       \
    encode_hex, "data, /, lower = True",                                \
    METH_VARARGS, py_hex,                                               \
    "Convert data to a hex string.\n"                                   \
    "\n"                                                                \
    "The *data* has to be a string or a read-only bytes-like object."   \
    " The *lower* argument defines the case of the result string.\n"    \
    "\n"                                                                \
    "This method may be only usefull for the internal test suite as"    \
    " there is a native Python alternative:\n"                          \
    "\n"                                                                \
    "    b'ABC'.hex()\n"                                                \
    "    '414243'"                                                      \
)

    lower = 1;

    ret = PyArg_ParseTuple(args, "s#|p", &data, &len, &lower);
    if (!ret) return NULL;

    buffer = malloc((len * 2 + 1) * sizeof(char));

    encode_hex(data, len, lower, buffer);

    result = PyUnicode_FromString(buffer);

    free(buffer);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = arguments à utiliser pour l'opération.                *
*                                                                             *
*  Description : Décode un caractère hexadécimal.                             *
*                                                                             *
*  Retour      : Bilan de l'opération : valeur en cas de succès, None sinon.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_hex_decode_hex_digit(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Valeur à retourner          */
    char byte;                              /* Valeur hexadécimale         */
    int ret;                                /* Bilan de lecture des args.  */
    uint8_t value;                          /* Valeur brute transcrite     */
    bool status;                            /* Bilan de l'opération        */

#define HEX_DECODE_HEX_DIGIT_METHOD PYTHON_METHOD_DEF       \
(                                                           \
    decode_hex_digit, "chr",                                \
    METH_VARARGS, py_hex,                                   \
    "Convert a string character to an integer value."       \
    "\n"                                                    \
    "The *chr* can be a string character of length 1.\n"    \
    "\n"                                                    \
    "The result is an integer value on success or *None*"   \
    " in case of failure."                                  \
)

    ret = PyArg_ParseTuple(args, "C", &byte);
    if (!ret) return NULL;

    status = decode_hex_digit((const char *)&byte, &value);

    if (status)
        result = PyLong_FromUnsignedLong(value);

    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Définit une extension du module 'common' à compléter.        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool populate_common_module_with_hex(void)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Module à recompléter        */

    static PyMethodDef py_hex_methods[] = {
        HEX_ENCODE_HEX_METHOD,
        HEX_DECODE_HEX_DIGIT_METHOD,
        { NULL }
    };

    module = get_access_to_python_module("pychrysalide.common");

    result = register_python_module_methods(module, py_hex_methods);

    return result;

}
