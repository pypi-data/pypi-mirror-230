
/* Chrysalide - Outil d'analyse de fichiers binaires
 * module.c - intégration du répertoire format en tant que module
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


#include "executable.h"
#include "flat.h"
#include "format.h"
#include "known.h"
#include "preload.h"
#include "strsym.h"
#include "symbol.h"
#include "symiter.h"
#include "../helpers.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : super = module dont la définition est à compléter.           *
*                                                                             *
*  Description : Ajoute le module 'format' à un module Python.                *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool add_format_module(PyObject *super)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Sous-module mis en place    */

#define PYCHRYSALIDE_FORMAT_DOC                                         \
    "This module contains the basic definitions requiered for dealing"  \
    " with file formats.\n"                                             \
    "\n"                                                                \
    "Support for specific formats (such as ELF files for instance)"     \
    " needs extra definitions in a specific module."

    static PyModuleDef py_chrysalide_format_module = {

        .m_base = PyModuleDef_HEAD_INIT,

        .m_name = "pychrysalide.format",
        .m_doc = PYCHRYSALIDE_FORMAT_DOC,

        .m_size = -1,

    };

    module = build_python_module(super, &py_chrysalide_format_module);

    result = (module != NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Intègre les objets du module 'format'.                       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool populate_format_module(void)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    if (result) result = ensure_python_executable_format_is_registered();
    if (result) result = ensure_python_flat_format_is_registered();
    if (result) result = ensure_python_known_format_is_registered();
    if (result) result = ensure_python_binary_format_is_registered();
    if (result) result = ensure_python_preload_info_is_registered();
    if (result) result = ensure_python_string_symbol_is_registered();
    if (result) result = ensure_python_binary_symbol_is_registered();
    if (result) result = ensure_python_sym_iterator_is_registered();

    assert(result);

    return result;

}
