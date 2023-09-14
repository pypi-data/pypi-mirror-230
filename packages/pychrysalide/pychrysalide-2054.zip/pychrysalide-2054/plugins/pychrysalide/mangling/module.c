
/* Chrysalide - Outil d'analyse de fichiers binaires
 * module.c - intégration du répertoire mangling en tant que module
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


#include "demangler.h"
#include "../helpers.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : super = module dont la définition est à compléter.           *
*                                                                             *
*  Description : Ajoute le module 'mangling' à un module Python.              *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool add_mangling_module(PyObject *super)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Sous-module mis en place    */

#define PYCHRYSALIDE_MANGLING_DOC                                           \
    "This module provides facilities to decode function or type names"      \
    " mangled by a compiler.\n"                                             \
    "\n"                                                                    \
    "The benefit of using these facilities instead of external tools such"  \
    " as *c++filt* resides in the quantity of recovered information: not"   \
    " only the mangled name is restored in a human readable form, but all"  \
    " the involved inner types get available for further processing."

    static PyModuleDef py_chrysalide_mangling_module = {

        .m_base = PyModuleDef_HEAD_INIT,

        .m_name = "pychrysalide.mangling",
        .m_doc = PYCHRYSALIDE_MANGLING_DOC,

        .m_size = -1,

    };

    module = build_python_module(super, &py_chrysalide_mangling_module);

    result = (module != NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Intègre les objets du module 'mangling'.                     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool populate_mangling_module(void)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    if (result) result = ensure_python_compiler_demangler_is_registered();

    assert(result);

    return result;

}
