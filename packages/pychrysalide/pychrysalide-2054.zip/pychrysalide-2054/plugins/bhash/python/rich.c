
/* Chrysalide - Outil d'analyse de fichiers binaires
 * rich.c - équivalent Python du fichier "plugins/bhash/rich.c"
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


#include "rich.h"


#include <pygobject.h>


#include <plugins/pe/python/format.h>
#include <plugins/pychrysalide/access.h>
#include <plugins/pychrysalide/helpers.h>


#include "../rich.h"



/* Calcule la valeur pour empreinte d'en-tête PE enrichi. */
static PyObject *py_bhash_compute_pe_rich_header_checksum(PyObject *, PyObject *);

/* Calcule l'empreinte des informations d'en-tête PE enrichi. */
static PyObject *py_bhash_compute_pe_rich_header_hash(PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = paramètre à récupérer pour le traitement.             *
*                                                                             *
*  Description : Calcule la valeur pour empreinte d'en-tête PE enrichi.       *
*                                                                             *
*  Retour      : None ou empreinte déterminée.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_bhash_compute_pe_rich_header_checksum(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Valeur à retourner          */
    GPeFormat *format;                      /* Format PE à manipuler       */
    int ret;                                /* Bilan de lecture des args.  */
    uint32_t csum;                          /* Empreinte réalisée          */
    bool status;                            /* Bilan de l'opération        */

#define BHASH_COMPUTE_PE_RICH_HEADER_CHECKSUM_METHOD PYTHON_METHOD_DEF  \
(                                                                       \
    compute_pe_rich_header_checksum, "format, /",                       \
    METH_VARARGS, py_bhash,                                             \
    "Compute the expected value for the Rich header checksum of a PE"   \
    " file.\n"                                                          \
    "\n"                                                                \
    "The *format* argument is a PE file format provided as a"           \
    " pychrysalide.format.pe.PeFormat instance.\n"                      \
    "\n"                                                                \
    "The returned value is a 32-bit integer value or *None* in case of" \
    " error."                                                           \
)

    result = NULL;

    ret = PyArg_ParseTuple(args, "O&", convert_to_pe_format, &format);
    if (!ret) goto exit;

    status = compute_pe_rich_header_checksum(format, &csum);

    if (status)
        result = PyLong_FromUnsignedLong(csum);

    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = paramètre à récupérer pour le traitement.             *
*                                                                             *
*  Description : Calcule l'empreinte des informations d'en-tête PE enrichi.   *
*                                                                             *
*  Retour      : Empreinte MD5 calculée ou None en cas d'échec.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_bhash_compute_pe_rich_header_hash(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Valeur à retourner          */
    int pv;                                 /* Sélection de l'empreinte    */
    GPeFormat *format;                      /* Format PE à manipuler       */
    int ret;                                /* Bilan de lecture des args.  */
    char *digest;                           /* Empreinte calculée          */

#define BHASH_COMPUTE_PE_RICH_HEADER_HASH_METHOD PYTHON_METHOD_DEF      \
(                                                                       \
    compute_pe_rich_header_hash, "format, /, pv=True",                  \
    METH_VARARGS, py_bhash,                                             \
    "Compute the Rich hash or the RichPV hash for a given PE format.\n" \
    "\n"                                                                \
    "The *format* argument is a PE file format provided as a"           \
    " pychrysalide.format.pe.PeFormat instance and *pv* defines the"    \
    " kind of hash to compute.\n"                                       \
    "\n"                                                                \
    "The returned value is a MD5 digest string or *None* in case of"    \
    " error."                                                           \
)

    result = NULL;

    pv = 1;

    ret = PyArg_ParseTuple(args, "O&|p", convert_to_pe_format, &format, &pv);
    if (!ret) goto exit;

    digest = compute_pe_rich_header_hash(format, pv);

    if (digest != NULL)
    {
        result = PyUnicode_FromString(digest);
        free(digest);
    }
    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : super = module dont la définition est à compléter.           *
*                                                                             *
*  Description : Définit une extension du module 'bhash' à compléter.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool populate_bhash_module_with_rich_header(PyObject *super)
{
    bool result;                            /* Bilan à retourner           */

    static PyMethodDef py_rich_header_methods[] = {
        BHASH_COMPUTE_PE_RICH_HEADER_CHECKSUM_METHOD,
        BHASH_COMPUTE_PE_RICH_HEADER_HASH_METHOD,
        { NULL }
    };

    result = register_python_module_methods(super, py_rich_header_methods);

    return result;

}
