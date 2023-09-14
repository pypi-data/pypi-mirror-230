
/* Chrysalide - Outil d'analyse de fichiers binaires
 * params.c - équivalent Python du fichier "core/params.c"
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


#include "params.h"


#include <pygobject.h>


#include <core/params.h>


#include "constants.h"
#include "../access.h"
#include "../helpers.h"



/* Fournit la version du programme global. */
static PyObject *py_params_get_main_configuration(PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = NULL car méthode statique.                            *
*                args = non utilisé ici.                                      *
*                                                                             *
*  Description : Fournit la version du programme global.                      *
*                                                                             *
*  Retour      : Configuration prête à emploi ou None si aucune définie.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_params_get_main_configuration(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance GLib à retourner   */
    GGenConfig *config;                     /* Configuration à convertir   */

#define PARAMS_GET_MAIN_CONFIGURATION_METHOD PYTHON_METHOD_DEF  \
(                                                               \
    get_main_configuration, "",                                 \
    METH_NOARGS, py_params,                                     \
    "Give access to the main configuration of Chrysalide."      \
    "\n"                                                        \
    "The returned object is an instance of type"                \
    " pychrysalide.glibext.GenConfig."                          \
)

    config = get_main_configuration();

    result = pygobject_new(G_OBJECT(config));
    Py_XINCREF(result);

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

bool populate_core_module_with_params(void)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Module à recompléter        */

    static PyMethodDef py_params_methods[] = {
        PARAMS_GET_MAIN_CONFIGURATION_METHOD,
        { NULL }
    };

    module = get_access_to_python_module("pychrysalide.core");

    result = register_python_module_methods(module, py_params_methods);

    if (result)
        define_core_params_constants(module);

    return result;

}
