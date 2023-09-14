
/* Chrysalide - Outil d'analyse de fichiers binaires
 * pathname.c - équivalent Python du fichier "common/pathname.c"
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


#include "pathname.h"


#include <malloc.h>
#include <pygobject.h>


#include <i18n.h>


#include <common/pathname.h>


#include "../access.h"
#include "../helpers.h"



/* Calcule le chemin relatif entre deux fichiers donnés. */
static PyObject *py_pathname_build_relative_filename(PyObject *, PyObject *);

/* Calcule le chemin absolu d'un fichier par rapport à un autre. */
static PyObject *py_pathname_build_absolute_filename(PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = NULL car méthode statique.                            *
*                args = arguments fournis lors de l'appel à la fonction.      *
*                                                                             *
*  Description : Calcule le chemin relatif entre deux fichiers donnés.        *
*                                                                             *
*  Retour      : Chemin relatif obtenu.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_pathname_build_relative_filename(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    const char *ref;                        /* Fichier de référence        */
    const char *target;                     /* Fichier à cibler            */
    int ret;                                /* Bilan de lecture des args.  */
    char *relative;                         /* Chemin d'accès construit    */

#define BUILD_RELATIVE_FILENAME_METHOD PYTHON_METHOD_DEF            \
(                                                                   \
    build_relative_filename, "reference, target",                   \
    METH_VARARGS, py_pathname,                                      \
    "Compute the relative path between two files: a *reference*"    \
    " location as point of view and a *target* file.\n"             \
    "\n"                                                            \
    "Both arguments must be strings.\n"                             \
    "\n"                                                            \
    "The result is also a string."                                  \
)

    ret = PyArg_ParseTuple(args, "ss", &ref, &target);
    if (!ret) return NULL;

    relative = build_relative_filename(ref, target);

    result = PyUnicode_FromString(relative);

    free(relative);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = NULL car méthode statique.                            *
*                args = arguments fournis lors de l'appel à la fonction.      *
*                                                                             *
*  Description : Calcule le chemin absolu d'un fichier par rapport à un autre.*
*                                                                             *
*  Retour      : Chemin absolu obtenu.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_pathname_build_absolute_filename(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    const char *ref;                        /* Fichier de référence        */
    const char *target;                     /* Fichier à cibler            */
    int ret;                                /* Bilan de lecture des args.  */
    char *relative;                         /* Chemin d'accès construit    */

#define BUILD_ABSOLUTE_FILENAME_METHOD PYTHON_METHOD_DEF            \
(                                                                   \
    build_absolute_filename, "reference, target",                   \
    METH_VARARGS, py_pathname,                                      \
    "Compute the absolute path for a *target* file from a"          \
    " *reference* location.\n"                                      \
    "\n"                                                            \
    "Both arguments must be strings.\n"                             \
    "\n"                                                            \
    "The result is a string on success. A *ValueError*  exception"  \
    " is raised on failure."                                        \
)

    ret = PyArg_ParseTuple(args, "ss", &ref, &target);
    if (!ret) return NULL;

    relative = build_absolute_filename(ref, target);

    if (relative == NULL)
    {
        PyErr_SetString(PyExc_ValueError, _("Relative path is too deep."));
        result = NULL;
    }
    else
    {
        result = PyUnicode_FromString(relative);
        free(relative);
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

bool populate_common_module_with_pathname(void)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Module à recompléter        */

    static PyMethodDef py_pathname_methods[] = {
        BUILD_RELATIVE_FILENAME_METHOD,
        BUILD_ABSOLUTE_FILENAME_METHOD,
        { NULL }
    };

    module = get_access_to_python_module("pychrysalide.common");

    result = register_python_module_methods(module, py_pathname_methods);

    return result;

}
