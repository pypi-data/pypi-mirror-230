
/* Chrysalide - Outil d'analyse de fichiers binaires
 * itoa.c - équivalent Python du fichier "common/itoa.c"
 *
 * Copyright (C) 2023 Cyrille Bagard
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


#include "itoa.h"


#include <common/itoa.h>


#include "../access.h"
#include "../helpers.h"



/* Détermine l'empreinte Itoa d'une chaîne de caractères. */
static PyObject *py_itoa(PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = NULL car méthode statique.                            *
*                args = arguments fournis lors de l'appel à la fonction.      *
*                                                                             *
*  Description : Convertit une valeur en une forme textuelle.                 *
*                                                                             *
*  Retour      : Chaîne de caractères mises en place.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_itoa(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    long long n;                            /* Valeur à transformer        */
    unsigned char base;                     /* Base de travail             */
    int ret;                                /* Bilan de lecture des args.  */
    char *strval;                           /* Valeur sous forme de chaîne */

#define ITOA_METHOD PYTHON_METHOD_DEF                               \
(                                                                   \
    itoa, "n, /, base=10",                                          \
    METH_VARARGS, py,                                               \
    "Construct a string representation of an integer *n* according" \
    " to a given *base*.\n"                                         \
    "\n"                                                            \
    "Both arguments are expected to be integer values; the result"  \
    " is a string or None in case of failure."                      \
)

    base = 10;

    ret = PyArg_ParseTuple(args, "L|b", &n, &base);
    if (!ret) return NULL;

    strval = itoa(n, base);

    if (strval != NULL)
    {
        result = PyUnicode_FromString(strval);
        free(strval);
    }
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

bool populate_common_module_with_itoa(void)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Module à recompléter        */

    static PyMethodDef py_itoa_methods[] = {
        ITOA_METHOD,
        { NULL }
    };

    module = get_access_to_python_module("pychrysalide.common");

    result = register_python_module_methods(module, py_itoa_methods);

    return result;

}
