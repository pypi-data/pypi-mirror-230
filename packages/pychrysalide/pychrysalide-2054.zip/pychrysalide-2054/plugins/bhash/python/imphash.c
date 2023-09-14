
/* Chrysalide - Outil d'analyse de fichiers binaires
 * imphash.c - équivalent Python du fichier "plugins/bhash/imphash.c"
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


#include "imphash.h"


#include <pygobject.h>


#include <plugins/pe/python/format.h>
#include <plugins/pychrysalide/access.h>
#include <plugins/pychrysalide/helpers.h>


#include "../imphash.h"



/* Calcule l'empreinte des importations d'un format PE. */
static PyObject *py_bhash_compute_pe_import_hash(PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = paramètre à récupérer pour le traitement.             *
*                                                                             *
*  Description : Calcule l'empreinte des importations d'un format PE.         *
*                                                                             *
*  Retour      : Empreinte MD5 calculée ou None en cas d'échec.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_bhash_compute_pe_import_hash(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Valeur à retourner          */
    int std;                                /* Méthode de calcul           */
    GPeFormat *format;                      /* Format PE à manipuler       */
    int ret;                                /* Bilan de lecture des args.  */
    char *digest;                           /* Empreinte calculée          */

#define BHASH_COMPUTE_PE_IMPORT_HASH_METHOD PYTHON_METHOD_DEF           \
(                                                                       \
    compute_pe_import_hash, "format, /, std=True",                      \
    METH_VARARGS, py_bhash,                                             \
    "Compute the import hash for a given PE format.\n"                  \
    "\n"                                                                \
    "The *format* argument is a PE file format provided as a"           \
    " pychrysalide.format.pe.PeFormat instance and *std* defines the"   \
    " kind of hash to compute.\n"                                       \
    "\n"                                                                \
    "The standard version has been created by Mandiant/FireEye; the"    \
    " other one is used by the popular pefile Python module.\n"         \
    "\n"                                                                \
    "The returned value is a MD5 digest string or *None* in case of"    \
    " error."                                                           \
)

    result = NULL;

    std = 1;

    ret = PyArg_ParseTuple(args, "O&|p", convert_to_pe_format, &format, &std);
    if (!ret) goto exit;

    digest = compute_pe_import_hash(format, std);

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

bool populate_bhash_module_with_imphash(PyObject *super)
{
    bool result;                            /* Bilan à retourner           */

    static PyMethodDef py_imphash_methods[] = {
        BHASH_COMPUTE_PE_IMPORT_HASH_METHOD,
        { NULL }
    };

    result = register_python_module_methods(super, py_imphash_methods);

    return result;

}
