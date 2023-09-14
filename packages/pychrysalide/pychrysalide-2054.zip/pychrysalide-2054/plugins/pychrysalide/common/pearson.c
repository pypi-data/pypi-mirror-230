
/* Chrysalide - Outil d'analyse de fichiers binaires
 * pearson.c - équivalent Python du fichier "common/pearson.c"
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


#include "pearson.h"


#include <pygobject.h>


#include <i18n.h>
#include <common/pearson.h>


#include "../access.h"
#include "../helpers.h"



/* Fournit les permutations par défaut par Pearson. */
static PyObject *py_pearson_permutations(PyObject *, PyObject *);

/* Détermine l'empreinte Pearson d'une chaîne de caractères. */
static PyObject *py_pearson(PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = NULL car méthode statique.                            *
*                args = adresse non utilisée ici, en l'absence d'argument.    *
*                                                                             *
*  Description : Fournit les permutations par défaut par Pearson.             *
*                                                                             *
*  Retour      : Table de valeurs utilisées par défaut.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_pearson_permutations(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    const char *table;                      /* Eventuelle table à utiliser */

#define PEARSON_PERMUTATIONS_METHOD PYTHON_METHOD_DEF   \
(                                                       \
    pearson_permutations, "",                           \
    METH_NOARGS, py,                                    \
    "Provide the default pseudorandom permutations"     \
    " for the Pearson hash computation.\n"              \
    "\n"                                                \
    "The result is 256-byte value."                     \
)

    table = get_pearson_permutations();

    result = PyBytes_FromStringAndSize(table, 256);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = NULL car méthode statique.                            *
*                args = arguments fournis lors de l'appel à la fonction.      *
*                                                                             *
*  Description : Détermine l'empreinte Pearson d'une chaîne de caractères.    *
*                                                                             *
*  Retour      : Numéro de révision.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_pearson(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    const char *str;                        /* Chaîne à traiter.           */
    PyObject *bytes;                        /* Tableau d'octets            */
    int ret;                                /* Bilan de lecture des args.  */
    const char *table;                      /* Eventuelle table à utiliser */
    uint8_t value;                          /* Empreinte calculée          */

#define PEARSON_METHOD PYTHON_METHOD_DEF                        \
(                                                               \
    pearson, "str, /, table",                                   \
    METH_VARARGS, py,                                           \
    "Compute the Pearson hash of a given string.\n"             \
    "\n"                                                        \
    "The default pseudorandom permutations are used if"         \
    " no *table* of 256 bytes is provided.\n"                   \
    "\n"                                                        \
    "A table of permutations can be created with this call:\n"  \
    "  bytes(sample(list(range(0, 256)), k=256))\n"             \
    "\n"                                                        \
    "The result is 8-bit integer value."                        \
)

    bytes = NULL;

    ret = PyArg_ParseTuple(args, "s|O!", &str, &PyBytes_Type, &bytes);
    if (!ret) return NULL;

    if (bytes != NULL)
    {
        if (PyBytes_Size(bytes) != 256)
        {
            PyErr_SetString(PyExc_ValueError, _("256 bytes are required for the custom table."));
            return NULL;
        }

        table = PyBytes_AsString(bytes);

        value = pearson_hash(str, table);

    }
    else
        value = pearson_hash(str, NULL);

    result = Py_BuildValue("B", (unsigned char)value);

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

bool populate_common_module_with_pearson(void)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Module à recompléter        */

    static PyMethodDef py_pearson_methods[] = {
        PEARSON_PERMUTATIONS_METHOD,
        PEARSON_METHOD,
        { NULL }
    };

    module = get_access_to_python_module("pychrysalide.common");

    result = register_python_module_methods(module, py_pearson_methods);

    return result;

}
