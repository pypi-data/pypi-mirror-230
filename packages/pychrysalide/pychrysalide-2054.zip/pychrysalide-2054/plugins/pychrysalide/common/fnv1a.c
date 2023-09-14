
/* Chrysalide - Outil d'analyse de fichiers binaires
 * fnv1a.c - équivalent Python du fichier "common/fnv1a.c"
 *
 * Copyright (C) 2018-2019 Cyrille Bagard
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


#include "fnv1a.h"


#include <pygobject.h>


#include <common/fnv1a.h>


#include "../access.h"
#include "../helpers.h"



/* Détermine l'empreinte FNV1a d'une chaîne de caractères. */
static PyObject *py_fnv1a(PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = NULL car méthode statique.                            *
*                args = arguments fournis lors de l'appel à la fonction.      *
*                                                                             *
*  Description : Détermine l'empreinte FNV1a d'une chaîne de caractères.      *
*                                                                             *
*  Retour      : Numéro de révision.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_fnv1a(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    const char *str;                        /* Chaîne à traiter.           */
    int ret;                                /* Bilan de lecture des args.  */
    fnv64_t value;                          /* Empreinte calculée          */

#define FNV1A_METHOD PYTHON_METHOD_DEF                  \
(                                                       \
    fnv1a, "str, /",                                    \
    METH_VARARGS, py,                                   \
    "Compute the Fowler-Noll-Vo hash (version 1a) of a" \
    " given string."                                    \
    "\n"                                                \
    "The result is 64-bit integer value."               \
)

    ret = PyArg_ParseTuple(args, "s", &str);
    if (!ret) return NULL;

    value = fnv_64a_hash(str);

    result = Py_BuildValue("K", (unsigned long long)value);

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

bool populate_common_module_with_fnv1a(void)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Module à recompléter        */

    static PyMethodDef py_fnv1a_methods[] = {
        FNV1A_METHOD,
        { NULL }
    };

    module = get_access_to_python_module("pychrysalide.common");

    result = register_python_module_methods(module, py_fnv1a_methods);

    return result;

}
