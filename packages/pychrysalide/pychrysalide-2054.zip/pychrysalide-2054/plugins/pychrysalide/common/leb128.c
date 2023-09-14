
/* Chrysalide - Outil d'analyse de fichiers binaires
 * leb128.c - équivalent Python du fichier "common/leb128.c"
 *
 * Copyright (C) 2018-2020 Cyrille Bagard
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


#include "leb128.h"


#include <assert.h>
#include <pygobject.h>


#include <common/leb128.h>


#include "packed.h"
#include "../access.h"
#include "../helpers.h"



/* Encode un nombre non signé encodé au format LEB128. */
static PyObject *py_leb128_pack_uleb128(PyObject *, PyObject *);

/* Encode un nombre signé encodé au format LEB128. */
static PyObject *py_leb128_pack_leb128(PyObject *, PyObject *);

/* Décode un nombre non signé encodé au format LEB128. */
static PyObject *py_leb128_unpack_uleb128(PyObject *, PyObject *);

/* Décode un nombre signé encodé au format LEB128. */
static PyObject *py_leb128_unpack_leb128(PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = tampon de données à constituer.                       *
*                                                                             *
*  Description : Encode un nombre non signé encodé au format LEB128.          *
*                                                                             *
*  Retour      : Bilan de l'opération : True en cas de succès, False sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_leb128_pack_uleb128(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Valeur à retourner          */
    uleb128_t value;                        /* Valeur à manipuler          */
    packed_buffer_t *pbuf;                  /* Tampon de données à employer*/
    int ret;                                /* Bilan de lecture des args.  */
    bool status;                            /* Bilan de l'opération        */

#define LEB128_PACK_ULEB128_METHOD PYTHON_METHOD_DEF                \
(                                                                   \
    pack_uleb128, "value, pbuf",                                    \
    METH_VARARGS, py_leb128,                                        \
    "Pack an unsigned LEB128 value into a data buffer.\n"           \
    "\n"                                                            \
    "The *value* is an integer value. The *pbuf* argument has to"   \
    " be a pychrysalide.common.PackedBuffer instance where data"    \
    " will be appended.\n"                                          \
    "\n"                                                            \
    "The returned value is the operation status: *True* for"        \
    " success, *False* for failure."                                \
)

    ret = PyArg_ParseTuple(args, "O&O&", convert_to_uleb128_value, &value, convert_to_packed_buffer, &pbuf);
    if (!ret) return NULL;

    status = pack_uleb128(&value, pbuf);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = tampon de données à constituer.                       *
*                                                                             *
*  Description : Encode un nombre signé encodé au format LEB128.              *
*                                                                             *
*  Retour      : Bilan de l'opération : True en cas de succès, False sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_leb128_pack_leb128(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Valeur à retourner          */
    leb128_t value;                         /* Valeur à manipuler          */
    packed_buffer_t *pbuf;                  /* Tampon de données à employer*/
    int ret;                                /* Bilan de lecture des args.  */
    bool status;                            /* Bilan de l'opération        */

#define LEB128_PACK_LEB128_METHOD PYTHON_METHOD_DEF                 \
(                                                                   \
    pack_leb128, "value, pbuf",                                     \
    METH_VARARGS, py_leb128,                                        \
    "Pack a signed LEB128 value into a data buffer.\n"              \
    "\n"                                                            \
    "The *value* is an integer value. The *pbuf* argument has to"   \
    " be a pychrysalide.common.PackedBuffer instance where data"    \
    " will be appended.\n"                                          \
    "\n"                                                            \
    "The returned value is the operation status: *True* for"        \
    " success, *False* for failure."                                \
)

    ret = PyArg_ParseTuple(args, "O&O&", convert_to_leb128_value, &value, convert_to_packed_buffer, &pbuf);
    if (!ret) return NULL;

    status = pack_leb128(&value, pbuf);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = tampon de données à consulter.                        *
*                                                                             *
*  Description : Décode un nombre non signé encodé au format LEB128.          *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_leb128_unpack_uleb128(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Valeur à retourner          */
    packed_buffer_t *pbuf;                  /* Tampon de données à employer*/
    int ret;                                /* Bilan de lecture des args.  */
    uleb128_t value;                        /* Valeur à manipuler          */
    bool status;                            /* Bilan de l'opération        */

#define LEB128_UNPACK_ULEB128_METHOD PYTHON_METHOD_DEF              \
(                                                                   \
    unpack_uleb128, "pbuf",                                         \
    METH_VARARGS, py_leb128,                                        \
    "Unpack an unsigned LEB128 value into a data buffer.\n"         \
    "\n"                                                            \
    "The *pbuf* argument has to be a"                               \
    " pychrysalide.common.PackedBuffer instance from where data"    \
    " will be read.\n"                                              \
    "\n"                                                            \
    "The returned value depends on the operation status: *None*"    \
    " for failure or a integer value for success."                  \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_packed_buffer, &pbuf);
    if (!ret) return NULL;

    status = unpack_uleb128(&value, pbuf);

    if (status)
        result = PyLong_FromUnsignedLongLong(value);

    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = tampon de données à consulter.                        *
*                                                                             *
*  Description : Décode un nombre signé encodé au format LEB128.              *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_leb128_unpack_leb128(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Valeur à retourner          */
    packed_buffer_t *pbuf;                  /* Tampon de données à employer*/
    int ret;                                /* Bilan de lecture des args.  */
    leb128_t value;                         /* Valeur à manipuler          */
    bool status;                            /* Bilan de l'opération        */

#define LEB128_UNPACK_LEB128_METHOD PYTHON_METHOD_DEF               \
(                                                                   \
    unpack_leb128, "pbuf",                                          \
    METH_VARARGS, py_leb128,                                        \
    "Unpack a signed LEB128 value into a data buffer.\n"            \
    "\n"                                                            \
    "The *pbuf* argument has to be a"                               \
    " pychrysalide.common.PackedBuffer instance from where data"    \
    " will be read.\n"                                              \
    "\n"                                                            \
    "The returned value depends on the operation status: *None*"    \
    " for failure or a integer value for success."                  \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_packed_buffer, &pbuf);
    if (!ret) return NULL;

    status = unpack_leb128(&value, pbuf);

    if (status)
        result = PyLong_FromLongLong(value);

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

bool populate_common_module_with_leb128(void)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Module à recompléter        */

    static PyMethodDef py_leb128_methods[] = {
        LEB128_PACK_ULEB128_METHOD,
        LEB128_PACK_LEB128_METHOD,
        LEB128_UNPACK_ULEB128_METHOD,
        LEB128_UNPACK_LEB128_METHOD,
        { NULL }
    };

    module = get_access_to_python_module("pychrysalide.common");

    result = register_python_module_methods(module, py_leb128_methods);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en valeur LEB128 non signée.              *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_uleb128_value(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */
    unsigned long long value;               /* Valeur récupérée            */

    result = PyObject_IsInstance(arg, (PyObject *)&PyLong_Type);

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to ULEB128 value");
            break;

        case 1:
            value = PyLong_AsUnsignedLongLong(arg);
            *((uleb128_t *)dst) = value;
            break;

        default:
            assert(false);
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en valeur LEB128 signée.                  *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_leb128_value(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */
    long long value;                        /* Valeur récupérée            */

    result = PyObject_IsInstance(arg, (PyObject *)&PyLong_Type);

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to LEB128 value");
            break;

        case 1:
            value = PyLong_AsLongLong(arg);
            *((leb128_t *)dst) = value;
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
