
/* Chrysalide - Outil d'analyse de fichiers binaires
 * core.c - équivalent Python du fichier "analysis/scan/core.c"
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


#include "core.h"


#include <pygobject.h>


#include <analysis/scan/core.h>


#include "patterns/modifier.h"
#include "../../access.h"
#include "../../helpers.h"



/* #include <malloc.h> */

/* #include <i18n.h> */
/* #include <arch/processor.h> */
/* #include <core/processors.h> */

/* #include "../core.h" */

/* #include "../arch/processor.h" */



/* Inscrit un modificateur dans la liste des disponibles. */
static PyObject *py_scan_register_token_modifier(PyObject *, PyObject *);

/* Fournit le modificateur correspondant à un nom. */
static PyObject *py_scan_find_token_modifiers_for_name(PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Inscrit un modificateur dans la liste des disponibles.       *
*                                                                             *
*  Retour      : Bilan des enregistrements effectués : True si nouveauté.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_scan_register_token_modifier(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    PyObject *instance;                     /* Instance Python fournie     */
    GScanTokenModifier *modifier;           /* Version native              */
    int ret;                                /* Bilan de lecture des args.  */
    bool status;                            /* Bilan d'un enregistrement   */

#define SCAN_REGISTER_TOKEN_MODIFIER_METHOD PYTHON_METHOD_DEF           \
(                                                                       \
    register_token_modifier, "inst, /",                                 \
    METH_VARARGS, py_scan,                                              \
    "Register a token modifier for byte patterns to scan.\n"            \
    "\n"                                                                \
    "This instance will be used as singleton and has to be a"           \
    " subclass of pychrysalide.analysis.scan.patterns.TokenModifier."   \
)

    ret = PyArg_ParseTuple(args, "O!", get_python_scan_token_modifier_type(), &instance);
    if (!ret) return NULL;

    modifier = G_SCAN_TOKEN_MODIFIER(pygobject_get(instance));

    status = register_scan_token_modifier(modifier);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Fournit le modificateur correspondant à un nom.              *
*                                                                             *
*  Retour      : Instance du modificateur identifié ou None.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_scan_find_token_modifiers_for_name(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    const char *name;                       /* Nom d'appel à rechercher    */
    int ret;                                /* Bilan de lecture des args.  */
    GScanTokenModifier *modifier;           /* Instance mise en place      */

#define SCAN_FIND_TOKEN_MODIFIERS_FOR_NAME_METHOD PYTHON_METHOD_DEF \
(                                                                   \
    find_token_modifiers_for_name, "name, /",                       \
    METH_VARARGS, py_scan,                                          \
    "Provide the registered instance of a pattern modifier linked"  \
    " to a given *name* provided as a key string.\n"                \
    "\n"                                                            \
    "The returned instance is an object inherited from"             \
    " pychrysalide.analysis.scan.patterns.TokenModifier or *None*"  \
    " if no instance was found for the provided name."              \
)

    ret = PyArg_ParseTuple(args, "s", &name);
    if (!ret) return NULL;

    modifier = find_scan_token_modifiers_for_name(name);

    if (modifier != NULL)
    {
        result = pygobject_new(G_OBJECT(modifier));
        g_object_unref(G_OBJECT(modifier));
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
*  Description : Définit une extension du module 'scan' à compléter.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool populate_scan_module_with_core_methods(void)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Module à recompléter        */

    static PyMethodDef py_core_methods[] = {
        SCAN_REGISTER_TOKEN_MODIFIER_METHOD,
        SCAN_FIND_TOKEN_MODIFIERS_FOR_NAME_METHOD,
        { NULL }
    };

    module = get_access_to_python_module("pychrysalide.analysis.scan");

    result = register_python_module_methods(module, py_core_methods);

    return result;

}
