
/* Chrysalide - Outil d'analyse de fichiers binaires
 * demanglers.c - équivalent Python du fichier "core/demanglers.c"
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


#include "demanglers.h"


#include <pygobject.h>


#include <core/demanglers.h>


#include "../access.h"
#include "../helpers.h"



/* Fournit le décodeur de désignations correspondant à un type. */
static PyObject *py_demanglers_get_demangler_for_key(PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = NULL car méthode statique.                            *
*                key = nom technique du décodeur recherché.                   *
*                                                                             *
*  Description : Fournit le décodeur de désignations correspondant à un type. *
*                                                                             *
*  Retour      : Décodeur trouvé et mis en place ou None.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_demanglers_get_demangler_for_key(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Désignation à retourner     */
    const char *key;                        /* Nom court du format         */
    int ret;                                /* Bilan de lecture des args.  */
    GCompDemangler *demangler;              /* Décodeur mis en place       */

#define DEMANGLERS_GET_DEMANGLER_FOR_KEY_METHOD PYTHON_METHOD_DEF           \
(                                                                           \
    get_demangler_for_key, "key, /",                                        \
    METH_VARARGS, py_demanglers,                                            \
    "Create a new demangler for a given type of encoding, provided as"      \
    " a key string.\n"                                                      \
    "\n"                                                                    \
    "The return instance is a pychrysalide.mangling.CompDemangler subclass."\
)

    ret = PyArg_ParseTuple(args, "s", &key);
    if (!ret) return NULL;

    demangler = get_compiler_demangler_for_key(key);

    if (demangler != NULL)
    {
        result = pygobject_new(G_OBJECT(demangler));
        Py_INCREF(result);

        g_object_unref(G_OBJECT(demangler));

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
*  Description : Définit une extension du module 'core' à compléter.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool populate_core_module_with_demanglers(void)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Module à recompléter        */

    static PyMethodDef py_demanglers_methods[] = {
        DEMANGLERS_GET_DEMANGLER_FOR_KEY_METHOD,
        { NULL }
    };

    module = get_access_to_python_module("pychrysalide.core");

    result = register_python_module_methods(module, py_demanglers_methods);

    return result;

}
