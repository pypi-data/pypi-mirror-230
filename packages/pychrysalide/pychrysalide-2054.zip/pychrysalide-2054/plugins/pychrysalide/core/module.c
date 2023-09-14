
/* Chrysalide - Outil d'analyse de fichiers binaires
 * module.c - intégration du répertoire core en tant que module
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


#include "module.h"


#include <assert.h>


#include "demanglers.h"
#include "global.h"
#include "logs.h"
#include "params.h"
#include "processors.h"
#include "queue.h"
#include "../helpers.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : super = module dont la définition est à compléter.           *
*                                                                             *
*  Description : Ajoute le module 'core' à un module Python.                  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool add_core_module(PyObject *super)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Sous-module mis en place    */

#define PYCHRYSALIDE_CORE_DOC                                               \
    "This module provides access to the Chrysalide core properties through" \
    " the Python bindings.\n"                                               \
    "\n"                                                                    \
    "Some of these features are singleton objects.\n"                       \
    "\n"                                                                    \
    "As attributes are not allowed for Python modules, all these"           \
    " property accesses are handled with methods."

    static PyModuleDef py_chrysalide_core_module = {

        .m_base = PyModuleDef_HEAD_INIT,

        .m_name = "pychrysalide.core",
        .m_doc = PYCHRYSALIDE_CORE_DOC,

        .m_size = -1,

    };

    module = build_python_module(super, &py_chrysalide_core_module);

    result = (module != NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Intègre les objets du module 'core'.                         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool populate_core_module(void)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    if (result) result = populate_core_module_with_demanglers();
    if (result) result = populate_core_module_with_global();
    if (result) result = populate_core_module_with_logs();
    if (result) result = populate_core_module_with_params();
    if (result) result = populate_core_module_with_processors();
    if (result) result = populate_core_module_with_queue();

    assert(result);

    return result;

}
