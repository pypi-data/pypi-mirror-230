
/* Chrysalide - Outil d'analyse de fichiers binaires
 * module.c - intégration du répertoire analysis en tant que module
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


#include "module.h"


#include <assert.h>


#include "binary.h"
#include "block.h"
#include "cattribs.h"
#include "content.h"
#include "loaded.h"
#include "loading.h"
#include "project.h"
#include "routine.h"
#include "type.h"
#include "variable.h"
#include "contents/module.h"
#include "db/module.h"
#include "disass/module.h"
#include "scan/module.h"
#include "storage/module.h"
#include "types/module.h"
#include "../helpers.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : super = module dont la définition est à compléter.           *
*                                                                             *
*  Description : Ajoute le module 'analysis' à un module Python.              *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool add_analysis_module(PyObject *super)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Sous-module mis en place    */

#define PYCHRYSALIDE_ANALYSIS_MODULE_DOC                                    \
    "This module provides bindings for all Chrysalide analysis-relative"    \
    " features."

    static PyModuleDef py_chrysalide_analysis_module = {

        .m_base = PyModuleDef_HEAD_INIT,

        .m_name = "pychrysalide.analysis",
        .m_doc = PYCHRYSALIDE_ANALYSIS_MODULE_DOC,

        .m_size = -1,

    };

    module = build_python_module(super, &py_chrysalide_analysis_module);

    result = (module != NULL);

    if (result) result = add_analysis_contents_module(module);
    if (result) result = add_analysis_db_module(module);
    if (result) result = add_analysis_disass_module(module);
    if (result) result = add_analysis_scan_module(module);
    if (result) result = add_analysis_storage_module(module);
    if (result) result = add_analysis_types_module(module);

    if (!result)
        Py_XDECREF(module);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Intègre les objets du module 'analysis'.                     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool populate_analysis_module(void)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    if (result) result = ensure_python_loaded_binary_is_registered();
    if (result) result = ensure_python_code_block_is_registered();
    if (result) result = ensure_python_block_list_is_registered();
    if (result) result = ensure_python_content_attributes_is_registered();
    if (result) result = ensure_python_binary_content_is_registered();
    if (result) result = ensure_python_loaded_content_is_registered();
    if (result) result = ensure_python_content_explorer_is_registered();
    if (result) result = ensure_python_content_resolver_is_registered();
    if (result) result = ensure_python_study_project_is_registered();
    if (result) result = ensure_python_binary_routine_is_registered();
    if (result) result = ensure_python_data_type_is_registered();
    if (result) result = ensure_python_binary_variable_is_registered();

    if (result) result = populate_analysis_contents_module();
    if (result) result = populate_analysis_db_module();
    if (result) result = populate_analysis_disass_module();
    if (result) result = populate_analysis_scan_module();
    if (result) result = populate_analysis_storage_module();
    if (result) result = populate_analysis_types_module();

    assert(result);

    return result;

}
