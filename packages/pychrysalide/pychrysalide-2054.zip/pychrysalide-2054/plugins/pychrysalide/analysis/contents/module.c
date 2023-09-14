
/* Chrysalide - Outil d'analyse de fichiers binaires
 * module.c - intégration du répertoire contents en tant que module
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


#include "encapsulated.h"
#include "file.h"
#include "memory.h"
#include "restricted.h"
#include "../../helpers.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : super = module dont la définition est à compléter.           *
*                                                                             *
*  Description : Ajoute le module 'analysis.contents' à un module Python.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool add_analysis_contents_module(PyObject *super)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Sous-module mis en place    */

#define PYCHRYSALIDE_ANALYSIS_CONTENT_MODULE_DOC                            \
    "This module provides several ways to load and deal with raw binary"    \
    " contents.\n"                                                          \
    "\n"                                                                    \
    "The most used BinContent implementation is probably the"               \
    " pychrysalide.analysis.contents.FileContent class."

    static PyModuleDef py_chrysalide_analysis_contents_module = {

        .m_base = PyModuleDef_HEAD_INIT,

        .m_name = "pychrysalide.analysis.contents",
        .m_doc = PYCHRYSALIDE_ANALYSIS_CONTENT_MODULE_DOC,

        .m_size = -1,

    };

    module = build_python_module(super, &py_chrysalide_analysis_contents_module);

    result = (module != NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Intègre les objets du module 'analysis.contents'.            *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool populate_analysis_contents_module(void)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    if (result) result = ensure_python_encaps_content_is_registered();
    if (result) result = ensure_python_file_content_is_registered();
    if (result) result = ensure_python_memory_content_is_registered();
    if (result) result = ensure_python_restricted_content_is_registered();

    assert(result);

    return result;

}
