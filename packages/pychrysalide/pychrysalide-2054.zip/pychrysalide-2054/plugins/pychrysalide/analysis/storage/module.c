
/* Chrysalide - Outil d'analyse de fichiers binaires
 * module.c - intégration du répertoire storage en tant que module
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


#include "module.h"


#include <assert.h>


#include "cache.h"
#include "container.h"
#include "serialize.h"
#include "storage.h"
#include "tpmem.h"
#include "../../helpers.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : super = module dont la définition est à compléter.           *
*                                                                             *
*  Description : Ajoute le module 'analysis.storage' à un module Python.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool add_analysis_storage_module(PyObject *super)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Sous-module mis en place    */

#define PYCHRYSALIDE_ANALYSIS_STORAGE_MODULE_DOC                        \
    "This module gathers all the features relative to serialization.\n" \
    "\n"                                                                \
    "This serialization is used for object caching and disassembly"     \
    " results storage."

    static PyModuleDef py_chrysalide_analysis_db_module = {

        .m_base = PyModuleDef_HEAD_INIT,

        .m_name = "pychrysalide.analysis.storage",
        .m_doc = PYCHRYSALIDE_ANALYSIS_STORAGE_MODULE_DOC,

        .m_size = -1,

    };

    module = build_python_module(super, &py_chrysalide_analysis_db_module);

    result = (module != NULL);

    if (!result)
        Py_XDECREF(module);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Intègre les objets du module 'analysis.storage'.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool populate_analysis_storage_module(void)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    if (result) result = ensure_python_cache_container_is_registered();
    if (result) result = ensure_python_serializable_object_is_registered();

    if (result) result = ensure_python_object_cache_is_registered();
    if (result) result = ensure_python_object_storage_is_registered();
    if (result) result = ensure_python_type_memory_is_registered();

    assert(result);

    return result;

}
